/* Catalogo (docs/catalogo_pets.json, docs/arvore_evolucao.json): stats da forma, renormalizacao e perfil de
   combate (vida, guts, multiplicadores). Espelho de combate_v2/v21/catalogo.py e campanha.perfil_de_stats. */
import { CAT, CCOND, CESC, CESC_V6, CMG, CTR, CV21, LINHA_DA_FORMA, SOMBRIA, STATS, type Tecnica } from "./constantes.ts";
import type { Carater, Estagio, Forma, FormaAdultaNormal, Stats } from "./tipos.ts";

export interface Perfil {
  est: Estagio; tecnica: Tecnica | null; passiva: string | null; stats: Stats;
  hpMax: number; guts0: number; gutsMax: number; regen: number; mPerto: number; mDisparo: number; mGuarda: number;
  /** escala E (so no combate da campanha com a escala ligada); ausente = combate de sempre */
  escala?: number;
}
/** multiplicador de estagio (vida e guts); o Mega (pets v5) e o do adulto x CMG.multEstagio */
export const multEstagio = (est: Estagio): number => est === "mega" ? CAT.estagio.adulto * CMG.multEstagio : CAT.estagio[est];

/* chave da escala (ConfigEscala.ligada). Desligada por padrao: os gabaritos de paridade rodam sem ela; o app liga. */
export const ESCALA = { ligada: false };
export function ligarEscala(v: boolean): void { ESCALA.ligada = v; }
/** versao de pet da escala propria (CESC_V6) */
export const VERSAO_ESCALA_V6 = CESC_V6.versaoPet;
/** E do pet: vida do estagio x (1 + beta x pontos treinados); `versao` = a do pet (>= 6: a escala dos pets v6) */
export const escalaDe = (est: Estagio, pontos: number, versao = 0): number => versao >= VERSAO_ESCALA_V6
  ? CESC_V6.vida[est] * (1 + CESC_V6.beta * pontos)
  : (est === "mega" ? CMG.vida : CESC.vida[est]) * (1 + CESC.beta * pontos);
/** quanto 1 ponto de vida de combate deste lutador vale na tela (dano e vida exibidos); 1 sem a escala */
export function fatorExibicao(p: Perfil, versao = 0): number {
  if (!ESCALA.ligada) return 1;
  return p.escala !== undefined ? p.escala / CESC.vidaNeutra : escalaDe(p.est, 0, versao) / (CESC.vidaNeutra * multEstagio(p.est));
}
/** vida mostrada ao jogador: E x vida propria / vida neutra (com a escala), ou a vida de combate (sem) */
export function vidaExibida(p: Perfil, estagio: Estagio = p.est, pontos = 0, versao = 0): number {
  if (!ESCALA.ligada) return p.hpMax;
  const propria = p.escala !== undefined ? p.hpMax : p.hpMax / multEstagio(p.est);
  return (p.escala ?? escalaDe(estagio, pontos, versao)) * propria / CESC.vidaNeutra;
}

export function tecnicaDe(f: Forma): Tecnica | null { return f.linha ? CAT.adolescente[f.linha].tecnica : null; }

/** renormalizacao (no lugar do corte): prende no limite quem saiu da faixa e devolve a diferenca, em
    partes iguais, aos stats livres; o total volta ao orcamento da especie */
export function renormalizar(v0: Stats, total: number): Stats {
  const presos: Partial<Stats> = {}; const v = { ...v0 };
  for (;;) {
    const livres = STATS.filter(k => !(k in presos)), fora = livres.filter(k => v[k] < CAT.min || v[k] > CAT.max);
    if (!fora.length) return Object.fromEntries(STATS.map(k => [k, k in presos ? presos[k] : v[k]])) as Stats;
    for (const k of fora) presos[k] = v[k] < CAT.min ? CAT.min : CAT.max;
    const l2 = livres.filter(k => !(k in presos));
    if (!l2.length) throw new Error("renormalização sem stats livres");
    const sobra = total - Object.values(presos).reduce((s, x) => s + x, 0) - l2.reduce((s, k) => s + v[k], 0);
    for (const k of l2) v[k] += sobra / l2.length;
  }
}
export function statsDe(f: Forma, car: Partial<Carater> | null | undefined): Stats {
  const b = { ...CAT.especies[f.esp] }, soma = (m: Partial<Stats>, w = 1): void => { for (const [k, x] of Object.entries(m)) b[k as keyof Stats] += w * x; };
  for (const [eixo, x] of Object.entries(car || {})) { if (!CAT.carater[eixo as keyof Carater]) throw new Error("eixo de caráter desconhecido: " + eixo); soma(CAT.carater[eixo as keyof Carater], x); }
  if (f.ramo) soma(CAT.crianca[f.ramo]);
  if (f.linha) soma(CAT.adolescente[f.linha].stats);
  if (SOMBRIA[f.adulta!]) soma(SOMBRIA[f.adulta!]!.stats);
  else if (f.adulta) soma(CAT.adulto[f.linha!].formas[f.adulta as FormaAdultaNormal]!.stats);
  return renormalizar(b, Object.values(CAT.especies[f.esp]).reduce((s, x) => s + x, 0));
}
/** stats -> numeros de combate; estagio multiplica vida e guts; condicao (do cuidado) multiplica vida e
    guts iniciais; treino: arena normaliza ao orcamento mantendo as proporcoes, campanha usa o ganho absoluto; `versao`: a do
    pet, que escolhe a escala da campanha (>= 6: CESC_V6). `comEscala`: a escala vale mesmo com a chave desligada (a Fabrica da Fronteira,
    fabrica.ts: as lutas dela estao so no registro do Tamer e nao podem depender da chave do app); sem ele, a chave decide, como sempre */
export function perfilDe(f: Forma, car: Partial<Carater> | null | undefined, condicao = 1, treino: Stats | null = null, absoluto = false,
  versao = 0, comEscala = false): Perfil {
  if (!(condicao >= CCOND.min && condicao <= CCOND.max)) throw new Error("condição fora da faixa: " + condicao);
  let s = statsDe(f, car);
  /* campanha com a escala: o treino vai para a escala E; o perfil fica normalizado ao orcamento (como na arena) */
  const esc = absoluto && (ESCALA.ligada || comEscala);
  if (treino) {
    const b = Object.fromEntries(STATS.map(k => [k, s[k] + CTR.pesoPontoCombate * (treino[k] || 0)])) as Stats;
    if (absoluto && !esc) s = b;
    else {
      const tot = STATS.reduce((a, k) => a + s[k], 0), soma = STATS.reduce((a, k) => a + b[k], 0);
      s = renormalizar(Object.fromEntries(STATS.map(k => [k, b[k] * tot / soma])) as Stats, tot);
    }
  }
  const mult = multEstagio(f.est), est = mult * condicao, gMax = (CV21.gMaxBase + CV21.gMaxFolego * s.folego) * mult;
  const pontos = treino ? STATS.reduce((a, k) => a + (treino[k] || 0), 0) : 0;
  return {
    est: f.est, tecnica: tecnicaDe(f), passiva: f.adulta || null, stats: s,
    ...(esc ? { escala: escalaDe(f.est, pontos, versao) } : {}),
    hpMax: (CV21.hpBase + CV21.hpVigor * s.vigor) * (esc ? condicao : est), guts0: Math.min(gMax, (CV21.g0Base + CV21.g0Folego * s.folego) * est),
    gutsMax: gMax, regen: CV21.regenBase + CV21.regenRec * s.recuperacao,
    mPerto: CV21.multBase + CV21.multPonto * s.forca, mDisparo: CV21.multBase + CV21.multPonto * s.mira,
    mGuarda: CV21.guardaBase - CV21.guardaPonto * s.guarda,
  };
}
/** bots classicos: todos os stats neutros (10), adulto, sem tecnica nem passiva */
export function perfilNeutro(): Perfil {
  return {
    est: "adulto", tecnica: null, passiva: null, stats: Object.fromEntries(STATS.map(k => [k, 10])) as Stats,
    hpMax: CV21.hpBase + 10 * CV21.hpVigor, guts0: CV21.g0Base + 10 * CV21.g0Folego, gutsMax: CV21.gMaxBase + 10 * CV21.gMaxFolego,
    regen: CV21.regenBase + 10 * CV21.regenRec, mPerto: 1, mDisparo: 1, mGuarda: 1,
  };
}
/** NPC da campanha: mesma conversao de perfilDe com stats uniformes (campanha.perfil_de_stats). Com a escala: perfil
    neutro (10 em cada stat) e `escala` = E do NPC (vida do estagio sugerido x fator; campanha.npc). `tecnica`: so o lider de
    arena que tem uma (arenas.ts; os NPCs de sempre nao tem tecnica nem passiva) */
export function perfilNPC(total: number, estagio: Estagio = "adulto", escala?: number, tecnica: Tecnica | null = null): Perfil {
  const v = escala !== undefined ? 10 : total / STATS.length, s = Object.fromEntries(STATS.map(k => [k, v])) as Stats, est = multEstagio(estagio),
    gMax = (CV21.gMaxBase + CV21.gMaxFolego * v) * est;
  return {
    est: estagio, tecnica, passiva: null, stats: s, ...(escala !== undefined ? { escala } : {}),
    hpMax: (CV21.hpBase + CV21.hpVigor * v) * (escala !== undefined ? 1 : est), guts0: Math.min(gMax, (CV21.g0Base + CV21.g0Folego * v) * est),
    gutsMax: gMax, regen: CV21.regenBase + CV21.regenRec * v,
    mPerto: CV21.multBase + CV21.multPonto * v, mDisparo: CV21.multBase + CV21.multPonto * v,
    mGuarda: CV21.guardaBase - CV21.guardaPonto * v,
  };
}
/** carater dos bots da bateria: eixo da linha +0,5 e complementar +-0,25 com o sinal da forma */
export function caraterCanonico(forma: FormaAdultaNormal): Partial<Carater> {
  const l = LINHA_DA_FORMA[forma], a = CAT.adulto[l];
  return { [CAT.adolescente[l].eixo]: .5, [a.comp]: .25 * a.formas[forma]!.sinal };
}
