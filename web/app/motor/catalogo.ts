/* Catalogo (docs/catalogo_pets.json, docs/arvore_evolucao.json): stats da forma, renormalizacao e perfil de
   combate (vida, guts, multiplicadores). Espelho de combate_v2/v21/catalogo.py e campanha.perfil_de_stats. */
import { CAT, CCOND, CTR, CV21, LINHA_DA_FORMA, SOMBRIA, STATS, type Tecnica } from "./constantes.ts";
import type { Carater, Estagio, Forma, FormaAdultaNormal, Stats } from "./tipos.ts";

export interface Perfil {
  est: Estagio; tecnica: Tecnica | null; passiva: string | null; stats: Stats;
  hpMax: number; guts0: number; gutsMax: number; regen: number; mPerto: number; mDisparo: number; mGuarda: number;
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
    guts iniciais; treino: arena normaliza ao orcamento mantendo as proporcoes, campanha usa o ganho absoluto */
export function perfilDe(f: Forma, car: Partial<Carater> | null | undefined, condicao = 1, treino: Stats | null = null, absoluto = false): Perfil {
  if (!(condicao >= CCOND.min && condicao <= CCOND.max)) throw new Error("condição fora da faixa: " + condicao);
  let s = statsDe(f, car);
  if (treino) {
    const b = Object.fromEntries(STATS.map(k => [k, s[k] + CTR.pesoPontoCombate * (treino[k] || 0)])) as Stats;
    if (absoluto) s = b;
    else {
      const tot = STATS.reduce((a, k) => a + s[k], 0), soma = STATS.reduce((a, k) => a + b[k], 0);
      s = renormalizar(Object.fromEntries(STATS.map(k => [k, b[k] * tot / soma])) as Stats, tot);
    }
  }
  const est = CAT.estagio[f.est] * condicao, gMax = (CV21.gMaxBase + CV21.gMaxFolego * s.folego) * CAT.estagio[f.est];
  return {
    est: f.est, tecnica: tecnicaDe(f), passiva: f.adulta || null, stats: s,
    hpMax: (CV21.hpBase + CV21.hpVigor * s.vigor) * est, guts0: Math.min(gMax, (CV21.g0Base + CV21.g0Folego * s.folego) * est),
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
/** NPC da campanha: mesma conversao de perfilDe com stats uniformes (campanha.perfil_de_stats) */
export function perfilNPC(total: number, estagio: Estagio = "adulto"): Perfil {
  const v = total / STATS.length, s = Object.fromEntries(STATS.map(k => [k, v])) as Stats, est = CAT.estagio[estagio],
    gMax = (CV21.gMaxBase + CV21.gMaxFolego * v) * est;
  return {
    est: estagio, tecnica: null, passiva: null, stats: s,
    hpMax: (CV21.hpBase + CV21.hpVigor * v) * est, guts0: Math.min(gMax, (CV21.g0Base + CV21.g0Folego * v) * est),
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
