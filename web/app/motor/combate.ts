/* Combate V2.1 (espelho de digilab/combate_v2/ e combate_v2/v21/, regras corrigidas V2C/V21C). Resolucao
   deterministica, sem rng; so as decisoes (epsilon) usam rng. Cada lutador tem um PERFIL (catalogo.ts) e,
   conforme o estagio, a tecnica da linha (adolescente) e a passiva da forma (adulto). */
import { CSO, CV, CV21, CV21D, TECNICAS } from "./constantes.ts";
import type { Perfil } from "./catalogo.ts";
import { criarRng, hashSemente, type Rng } from "./rng.ts";
import type { Estagio } from "./tipos.ts";

export const ACOES_V2: readonly string[] = ["avancar", "recuar", "golpe_rapido", "preparar_pesado", "disparo", "defender", "esquivar", "carregar", ...TECNICAS];
/* V2C: fintar so existe no turno de execucao do pesado (alternativa a executar) */
export const ACOES_V2_OBS: readonly string[] = [...ACOES_V2, "pesado", "fintar"];
export const DIST = ["perto", "medio", "longe"];
export const custoV2 = (a: string): number => CV.custo[a] ?? CV21.custo[a] ?? 0;
/** regras de uma luta: null = V21C (pets v1-v5, cenarios); CV21D = a variante a_c_e2v_v do reequilibrio (docs/VALIDACAO_V21D.md),
    so nas lutas de pets v6: o preparo sob pele nao aparece em oponente_preparando, e a muralha e o vigia (do pet e dos bots)
    usam as listas variantes (bots.gambitsAdulto). Vale para a luta inteira, os dois lados, como as Regras do Python */
export type RegrasLuta = typeof CV21D | null;
export const regrasDaVersao = (versao: number): RegrasLuta => versao >= CV21D.versaoPet ? CV21D : null;

export interface Lado {
  p: Perfil; hp: number; hpMax: number; guts: number; gutsMax: number; regen: number; prep: boolean; hist: string[];
  marca: number; pele: number; recarga: number; disparou: boolean;
  /** o preparo do pesado em curso foi feito com pele_dura ativa (so e lido com CV21D.preparoSobPeleOculto) */
  prepPele: boolean;
}
export interface EstadoLuta { turno: number; dist: number; L: Lado[] }

export function estadoV2(pa: Perfil, pb: Perfil): EstadoLuta {
  const L = (p: Perfil): Lado => ({
    p, hp: p.hpMax, hpMax: p.hpMax, guts: p.guts0, gutsMax: p.gutsMax, regen: p.regen, prep: false, hist: [],
    marca: 0, pele: 0, recarga: 0, disparou: false, prepPele: false,
  });
  return { turno: 0, dist: 1, L: [L(pa), L(pb)] };
}
export function legalV2(E: EstadoLuta, lado: number, a: string): boolean {
  const eu = E.L[lado], p = eu.p, d = E.dist;
  if (a === "fintar") return eu.prep;              /* V2C: so no turno de execucao do pesado */
  if (eu.prep || a === "pesado" || !ACOES_V2.includes(a)) return false;
  /* V2C fuga condicionada: avancar ilegal em perto, recuar ilegal em longe */
  if (a === "avancar" && d === 0) return false;
  if (a === "recuar" && d === 2) return false;
  if ((TECNICAS as readonly string[]).includes(a) && p.tecnica !== a) return false;
  if (eu.guts < custoV2(a)) return false;
  if (a === "golpe_rapido" || a === "preparar_pesado") return d === 0;
  if (a === "disparo") return d !== 0;
  if (a === "investida") return d === 1;
  if (a === "contra_golpe") return p.passiva === "espelho" || d === 0;
  if (a === "marcar") return d !== 0 && eu.marca === 0;
  if (a === "pele_dura") return eu.pele === 0;
  if (a === "defender") return p.passiva !== "furioso" && p.passiva !== "devastador";
  if (a === "esquivar") return p.passiva !== "devastador";
  if (a === "recuar") return p.passiva !== "predador";
  return true;
}
export const legaisV2 = (E: EstadoLuta, lado: number): string[] => ACOES_V2.filter(a => legalV2(E, lado, a));
const CORPO_A_CORPO = ["golpe_rapido", "pesado", "investida", "fintar"];

export interface ResultadoTurno { E: EstadoLuta; dano: number[]; dev: number[]; interr: boolean[]; errou: boolean[] }

export function resolverV2(E: EstadoLuta, aa: string, ab: string): ResultadoTurno {
  const ac = [aa, ab];
  for (const l of [0, 1]) {
    if (E.L[l].prep) { if (ac[l] !== "pesado" && ac[l] !== "fintar") throw new Error(`lado ${l} está preparando e escolheu ${ac[l]}`); }
    else if (!legalV2(E, l, ac[l])) throw new Error(`ação ilegal do lado ${l}: ${ac[l]}`);
  }
  const guts = [0, 1].map(l => E.L[l].guts - custoV2(ac[l]));
  const pele = [0, 1].map(l => ac[l] === "pele_dura" || E.L[l].pele > 0);
  const d0 = E.dist, dano = [0, 0], dev = [0, 0], interr = [false, false], errou = [false, false];
  const marcaUsada = [false, false], parry = [false, false], recebeuCac = [false, false];
  for (const atk of [0, 1]) {
    const alvo = 1 - atk, eu = E.L[atk], pa = eu.p, pal = E.L[alvo].p, a = ac[atk], r = ac[alvo];
    let bruto = 0;
    if (a === "golpe_rapido") bruto = CV.dano.golpe_rapido * pa.mPerto;
    else if (a === "fintar") { if (d0 === 0) bruto = CV.dano.golpe_rapido * pa.mPerto; }   /* acerta quem esquiva, nao quebra guarda */
    else if (a === "investida") bruto = CV21.danoInvestida * pa.mPerto;
    else if (a === "pesado") { if (d0 === 0) { bruto = CV.dano.pesado * pa.mPerto; if (pa.passiva === "tita") bruto *= CV21.multTita; } else errou[atk] = true; }
    else if (a === "disparo") {
      bruto = CV.dano.disparo * pa.mDisparo;
      if (eu.marca > 0) { bruto *= CV21.multMarca; marcaUsada[atk] = true; }
      if (pa.passiva === "emboscador" && !eu.disparou) bruto *= CV21.multEmb;
      if (pa.passiva === "predador") bruto *= CSO.multPred;
    }
    if (CORPO_A_CORPO.includes(a) && pa.passiva === "furioso" && eu.hp / eu.hpMax < CV21.limFurioso) bruto *= CV21.multFurioso;
    if (CORPO_A_CORPO.includes(a) && pa.passiva === "devastador") bruto *= CSO.multDev;
    if (!bruto) continue;
    let rec = bruto;
    const marcado = a === "disparo" && marcaUsada[atk];
    if (r === "esquivar") {
      if (a === "pesado" || a === "disparo") {
        rec = 0;
        if (a === "pesado" && pa.passiva === "duelista") { rec = CV21.duelista; guts[atk] += CV.custo.preparar_pesado; }
      }
    } else if (r === "defender" || r === "contra_golpe") {
      /* disparo marcado ignora a REDUCAO da postura; o contra-golpe ainda devolve */
      if (marcado) { /* sem reducao */ }
      else if (a === "investida") { rec = bruto * CV21.parry; if (r === "defender") parry[atk] = true; }
      else if (a === "pesado") rec = bruto * CV.multDefPesado * pal.mGuarda;
      else rec = bruto * CV.multDef * pal.mGuarda;
      if (r === "contra_golpe") {
        if (CORPO_A_CORPO.includes(a)) dev[alvo] += (pal.passiva === "bastiao_rachado" ? CSO.fracBastiao : CV21.fracCG) * bruto;
        else if (a === "disparo" && pal.passiva === "espelho") dev[alvo] += CV21.espelho * bruto;
      }
    } else if (r === "carregar") rec = bruto * CV.multCarregar;
    if (pele[alvo]) rec *= CV21.multPele;
    dano[alvo] += rec;
    if (CORPO_A_CORPO.includes(a) && rec > 0) recebeuCac[alvo] = true;
    /* V2C parry: defender contra golpe rapido (ou finta) que acertou devolve dano ao atacante */
    if ((a === "golpe_rapido" || a === "fintar") && r === "defender") { dano[atk] += CV.parry; recebeuCac[atk] = true; }
    if ((a === "golpe_rapido" || a === "investida" || a === "fintar") && r === "preparar_pesado" && !pele[alvo]) interr[alvo] = true;
  }
  for (const i of [0, 1]) if (dev[i]) { dano[1 - i] += dev[i] * (pele[1 - i] ? CV21.multPele : 1); recebeuCac[1 - i] = true; }
  /* escala (campanha): o dano recebido por i veio do oponente e passa para as unidades de i por E_oponente / E_i */
  const ea = E.L[0].p.escala, eb = E.L[1].p.escala;
  if (ea !== undefined || eb !== undefined) {
    if (ea === undefined || eb === undefined) throw new Error("escala ligada em um lado só");
    dano[0] *= eb / ea; dano[1] *= ea / eb;
  }
  /* V2C morte subita: a partir do turno 25 todo dano x1,5 */
  if (E.turno + 1 >= CV.turnoMS) for (const i of [0, 1]) dano[i] *= CV.multMS;
  const passo = (x: string): number => x === "avancar" || x === "investida" ? -1 : x === "recuar" ? 1 : 0;
  const passos = [0, 1].map(i => parry[i] ? 0 : passo(ac[i]));
  /* V2C fuga condicionada: recuar nao afasta se o oponente se aproxima (a sentinela com a passiva pronta recua) */
  for (const i of [0, 1]) if (ac[i] === "recuar" && passos[1 - i] < 0 && !(E.L[i].p.passiva === "sentinela" && E.L[i].recarga === 0)) passos[i] = 0;
  const recarga = [0, 1].map(i => Math.max(0, E.L[i].recarga - 1));
  for (const i of [0, 1])
    if (E.L[i].p.passiva === "sentinela" && ac[i] === "recuar" && passos[1 - i] < 0 && E.L[i].recarga === 0) { passos[1 - i] = 0; recarga[i] = CV21.recargaSent; }
  const dist = Math.min(2, Math.max(0, d0 + passos[0] + passos[1]));
  const L = [0, 1].map(l => {
    const s = E.L[l], p = s.p; let g = guts[l] + s.regen * (p.passiva === "colosso_partido" ? CSO.multRegenColosso : 1);
    if (ac[l] === "defender" && p.passiva !== "bastiao_rachado") g += CV.gutsDef + (p.passiva === "muralha" ? CV21.muralha : 0);
    if (ac[l] === "carregar") g += CV.gutsCarregar;
    let marca = ac[l] === "marcar" ? CV21.turnosMarca : marcaUsada[l] ? 0 : Math.max(0, s.marca - 1);
    /* V21C marca fragil: perde com dano corpo a corpo recebido ou terminando o turno em perto */
    if (recebeuCac[l] || dist === 0) marca = 0;
    const pl = ac[l] === "pele_dura" ? (p.passiva === "colosso_partido" ? CSO.turnosPeleColosso : CV21.turnosPele) - 1 : Math.max(0, s.pele - 1);
    return {
      ...s, hp: s.hp - dano[l], guts: Math.max(0, Math.min(s.gutsMax, g)), prep: ac[l] === "preparar_pesado" && !interr[l],
      prepPele: ac[l] === "preparar_pesado" && !interr[l] && pele[l],
      hist: [...s.hist, ac[l]], marca, pele: pl, recarga: recarga[l], disparou: s.disparou || ac[l] === "disparo",
    };
  });
  return { E: { turno: E.turno + 1, dist, L }, dano, dev, interr, errou };
}
/** quem foi desafiado na luta (0 = lado A, 1 = lado B) ou null (ninguem: o limite de turnos decide pela fracao de vida, como
    sempre). Regra do limite (decisao do Matheus, 2026-09-30, so no jogo): a luta que chega ao limite de turnos sem KO e do
    desafiado. Nas lutas dos pets v6 o pet (lado A) sempre desafia (desafiadoDaVersao), tambem na Liga dos Lideres da Fronteira (o desafiado e o lider; liga.ts) */
export type Desafiado = 0 | 1 | null;
/** versao de pet a partir da qual o limite de turnos e do desafiado */
export const VERSAO_LIMITE_DESAFIADO = 6;
/** o desafiado nas lutas do motor (o pet e o lado A): o rival (lado B) nos pets v6; ninguem nos v1-v5 */
export const desafiadoDaVersao = (versao: number): Desafiado => versao >= VERSAO_LIMITE_DESAFIADO ? 1 : null;
export function fimV2(E: EstadoLuta, desafiado: Desafiado = null): [number, "ko" | "limite"] | null {
  const [a, b] = E.L, koA = a.hp <= 0, koB = b.hp <= 0;
  if (koA || koB) return [koA && koB ? .5 : koA ? 0 : 1, "ko"];
  if (E.turno >= CV.tMax) {
    if (desafiado !== null) return [desafiado === 0 ? 1 : 0, "limite"];
    const fa = a.hp / a.hpMax, fb = b.hp / b.hpMax; return [fa === fb ? .5 : fa > fb ? 1 : 0, "limite"];
  }
  return null;
}

/* ------------------------------------------------ gambits */
export interface Cond { n: string; p: (number | string)[] }
export interface Regra { se: Cond[]; entao: string }
export interface ListaGambits { regras: Regra[]; final: string }
export interface Estilo { nome: string; gambits?: ListaGambits; oraculo?: boolean; eps: number; base?: string }

export const CATALOGO_V2: Record<string, string[]> = {
  sempre: [], distancia_eh: ["d"], hp_proprio_abaixo: ["f"], guts_proprio_abaixo: ["g"], guts_proprio_acima: ["g"],
  oponente_preparando: [], oponente_hp_abaixo: ["f"], oponente_guts_abaixo: ["g"], oponente_repete: ["a", "k"], oponente_frequente: ["a"],
  turno_execucao: ["t"], oponente_vai_preparar: [], executando_pesado: [],
};
const DOMINIO_V2: Record<string, readonly (number | string)[]> = { d: [0, 1, 2], f: CV.fracoes, g: CV.guts, a: ACOES_V2_OBS, k: CV.ks, t: CV21.turnos };
/* a evolucao muda a cabeca: condicoes por estagio (o vigia tambem ve oponente_vai_preparar) */
export const CONDICOES_ESTAGIO: Record<Estagio, string[]> = (() => {
  const cri = ["sempre", "distancia_eh", "hp_proprio_abaixo", "guts_proprio_abaixo", "guts_proprio_acima"];
  const ado = [...cri, "oponente_preparando", "oponente_hp_abaixo", "oponente_guts_abaixo"];
  const adu = [...ado, "oponente_repete", "oponente_frequente", "turno_execucao", "executando_pesado"];
  return { bebe: [], crianca: cri, adolescente: ado, adulto: adu, mega: adu };   /* o Mega (pets v5) pensa como o adulto */
})();
export function validarCond(c: Cond): void {
  const tipos = CATALOGO_V2[c.n];
  if (!tipos) throw new Error("condição fora do catálogo: " + c.n);
  if (c.p.length !== tipos.length) throw new Error(`${c.n}: parâmetros errados`);
  tipos.forEach((t, i) => { if (!DOMINIO_V2[t].includes(c.p[i])) throw new Error(`${c.n}: parâmetro ${c.p[i]} fora do domínio`); });
}
export function validarLista(g: ListaGambits): ListaGambits {
  if (g.regras.length > CV.maxRegras) throw new Error(`no máximo ${CV.maxRegras} regras além da final`);
  for (const r of g.regras) {
    if (r.se.length < 1 || r.se.length > CV.maxCond) throw new Error("cada regra tem 1 ou 2 condições");
    if (r.entao === "fintar") { if (!r.se.some(c => c.n === "executando_pesado")) throw new Error("regra de fintar precisa de 'executando pesado'"); }
    else if (!ACOES_V2.includes(r.entao)) throw new Error("ação não escolhível: " + r.entao);
    r.se.forEach(validarCond);
  }
  if (!["defender", "carregar"].includes(g.final)) throw new Error("a regra final precisa ser 'sempre → defender' ou 'sempre → carregar'");
  return g;
}
export interface Contexto { intencao: string | null }
export function valeCond(c: Cond, E: EstadoLuta, lado: number, ctx: Contexto | null, R: RegrasLuta = null): boolean {
  const eu = E.L[lado], op = E.L[1 - lado], p = c.p;
  switch (c.n) {
    case "sempre": return true;
    case "distancia_eh": return E.dist === p[0];
    case "hp_proprio_abaixo": return eu.hp / eu.hpMax < (p[0] as number);
    case "guts_proprio_abaixo": return eu.guts < (p[0] as number);
    case "guts_proprio_acima": return eu.guts >= (p[0] as number);
    /* V21D (candidato A): o preparo feito sob pele_dura nao aparece */
    case "oponente_preparando": return op.prep && !(R?.preparoSobPeleOculto && op.prepPele);
    case "oponente_hp_abaixo": return op.hp / op.hpMax < (p[0] as number);
    case "oponente_guts_abaixo": return op.guts < (p[0] as number);
    case "oponente_repete": { const u = op.hist.slice(-(p[1] as number)); return u.length === p[1] && u.every(x => x === p[0]); }
    case "oponente_frequente": { const u = op.hist.slice(-CV.janelaFreq); return u.filter(x => x === p[0]).length / CV.janelaFreq >= CV.limiarFreq; }
    case "turno_execucao": return E.turno >= (p[0] as number);
    case "oponente_vai_preparar": return !!ctx && ctx.intencao === "preparar_pesado";
    case "executando_pesado": return eu.prep;
  }
  throw new Error("condição sem avaliador: " + c.n);
}
function valorOr(E: EstadoLuta, lado: number): number {
  const eu = E.L[lado], op = E.L[1 - lado];
  let v = (eu.hp / eu.hpMax - op.hp / op.hpMax) + CV.pesoGutsOr * (eu.guts - op.guts);
  if (E.dist === 0) { const pend = CV.pesoPendOr * CV.dano.pesado; if (eu.prep) v += pend / op.hpMax; if (op.prep) v -= pend / eu.hpMax; }
  return v;
}
/** REFERENCIA FORA DA LINGUAGEM: melhor resposta de 1 passo contra a frequencia do oponente na partida */
export function oraculoV2(E: EstadoLuta, lado: number): string {
  const minhas = legaisV2(E, lado), op = 1 - lado;
  let dist: Record<string, number>;
  if (E.L[op].prep) dist = { pesado: 1 };
  else {
    const leg = legaisV2(E, op), cont: Record<string, number> = {};
    for (const x of leg) cont[x] = 0;
    for (const x of E.L[op].hist) if (x in cont) cont[x]++;
    const tot = Object.values(cont).reduce((s, c) => s + c, 0);
    dist = {};
    if (tot) { for (const x of leg) if (cont[x]) dist[x] = cont[x] / tot; } else for (const x of leg) dist[x] = 1 / leg.length;
  }
  let melhor: string | null = null, mv: number | null = null;
  for (const a of minhas) {
    let v = 0;
    for (const [b, p] of Object.entries(dist)) { const par = lado === 0 ? [a, b] : [b, a]; v += p * valorOr(resolverV2(E, par[0], par[1]).E, lado); }
    if (mv === null || v > mv) { mv = v; melhor = a; }
  }
  return melhor as string;
}
/** o que a lista do lado escolheria agora, sem exploracao e sem rng (o que o vigia ve) */
export function intencaoV2(estilo: Estilo, E: EstadoLuta, lado: number, R: RegrasLuta = null): string | null {
  if (E.L[lado].prep) return null;
  if (estilo.oraculo) return oraculoV2(E, lado);
  const g = estilo.gambits!;
  for (const r of g.regras) if (r.se.every(c => valeCond(c, E, lado, null, R)) && legalV2(E, lado, r.entao)) return r.entao;
  return legalV2(E, lado, g.final) ? g.final : "carregar";
}
/** decisao do lado: [acao, motivo] (indice da regra, "exploracao", "oraculo" ou "pesado_automatico") */
export function decidirV2(estilo: Estilo, E: EstadoLuta, lado: number, rng: Rng, ctx: Contexto | null, R: RegrasLuta = null): [string, number | string] {
  if (E.L[lado].prep) {
    /* V2C finta: a primeira regra de fintar que vale troca o pesado (sem exploracao) */
    const g = estilo.gambits;
    if (g) for (let i = 0; i < g.regras.length; i++) {
      const r = g.regras[i];
      if (r.entao === "fintar" && r.se.every(c => valeCond(c, E, lado, ctx, R))) return ["fintar", i];
    }
    return ["pesado", "pesado_automatico"];
  }
  const leg = legaisV2(E, lado);
  if (estilo.eps > 0 && rng.random() < estilo.eps) return [leg[rng.int(leg.length)], "exploracao"];
  if (estilo.oraculo) return [oraculoV2(E, lado), "oraculo"];
  const g = estilo.gambits!;
  for (let i = 0; i < g.regras.length; i++) {
    const r = g.regras[i];
    if (r.se.every(c => valeCond(c, E, lado, ctx, R)) && legalV2(E, lado, r.entao)) return [r.entao, i];
  }
  /* furioso nao defende: a final 'defender' cai para carregar */
  return [legalV2(E, lado, g.final) ? g.final : "carregar", g.regras.length];
}

export const Cd = (n: string, ...p: (number | string)[]): Cond => ({ n, p });
export const Rg = (se: Cond | Cond[], entao: string): Regra => ({ se: Array.isArray(se) ? se : [se], entao });

export interface Lutador { nome: string; estilo: Estilo; cond: Perfil; sombra?: boolean }
export interface Turno {
  t: number; a: string; ma: number | string; b: string; mb: number | string; antes: EstadoLuta; depois: EstadoLuta;
  dano: number[]; interr: boolean[]; errou: boolean[];
  /** carta de Cura (itens.ts): a vida que o lado curou no fim deste turno (so aparece no turno da cura) */
  cura?: number[];
}
export interface ResultadoLuta { E0: EstadoLuta; turnos: Turno[]; pontosA: number; fim: "ko" | "limite"; E: EstadoLuta }

/** efeito de uma carta na luta (itens.ts; pets v6): `guts` a mais no comeco, `foco` = sem exploracao (epsilon 0), e a `cura`: na
    primeira vez que a vida cai abaixo de `abaixo` da maxima (e o lado nao caiu), cura `fracao` da vida maxima, uma vez */
export interface CuraLuta { abaixo: number; fracao: number }
export interface EfeitoCarta { guts?: number; foco?: boolean; cura?: CuraLuta }
/** a carta no lutador: o guts a mais entra no guts do comeco (ate o maximo) e o foco zera a exploracao. A cura e da luta (jogarV2) */
export function comCarta(L: Lutador, ef: EfeitoCarta | null): Lutador {
  if (!ef) return L;
  const cond = ef.guts ? { ...L.cond, guts0: Math.min(L.cond.gutsMax, L.cond.guts0 + ef.guts) } : L.cond;
  return { ...L, cond, estilo: ef.foco ? { ...L.estilo, eps: 0 } : L.estilo };
}

/** `ini`: o lado A comeca com esta vida e este guts (as lutas seguidas da arena da Cidadela, sem cura; arenas.jogarArena);
    null = a luta de sempre, os dois inteiros. `desafiado`: quem fica com a luta no limite de turnos (fimV2). `curas`: a carta de
    Cura de cada lado ([A, B]; null = nenhuma), que vale uma vez nesta luta; sem ela, a luta de sempre */
export function jogarV2(A: Lutador, B: Lutador, semente: number, R: RegrasLuta = null, ini: { hp: number; guts: number } | null = null,
  desafiado: Desafiado = null, curas: readonly (CuraLuta | null)[] | null = null): ResultadoLuta {
  const ra = criarRng(hashSemente("v2", semente, 0)), rb = criarRng(hashSemente("v2", semente, 1));
  let E = estadoV2(A.cond, B.cond), fim: ReturnType<typeof fimV2>;
  if (ini) {
    if (!(ini.hp > 0 && ini.hp <= E.L[0].hpMax) || !(ini.guts >= 0)) throw new Error(`começo da luta inválido: vida ${ini.hp}, guts ${ini.guts}`);
    E = { ...E, L: [{ ...E.L[0], hp: ini.hp, guts: Math.min(ini.guts, E.L[0].gutsMax) }, E.L[1]] };
  }
  const E0 = E, turnos: Turno[] = [], pendentes = curas ? [curas[0] ?? null, curas[1] ?? null] : null;
  while (!(fim = fimV2(E, desafiado))) {
    /* o vigia ve a intencao do oponente (sem exploracao, sem rng) antes de decidir */
    const ctxA = A.cond.passiva === "vigia" ? { intencao: intencaoV2(B.estilo, E, 1, R) } : null;
    const ctxB = B.cond.passiva === "vigia" ? { intencao: intencaoV2(A.estilo, E, 0, R) } : null;
    const [aa, ma] = decidirV2(A.estilo, E, 0, ra, ctxA, R), [ab, mb] = decidirV2(B.estilo, E, 1, rb, ctxB, R);
    const antes = E, r = resolverV2(E, aa, ab); E = r.E;
    let cura: number[] | undefined;
    if (pendentes) for (const l of [0, 1]) {
      const c = pendentes[l], s = E.L[l];
      if (!c || s.hp <= 0 || s.hp >= c.abaixo * s.hpMax) continue;
      const ganho = Math.min(s.hpMax - s.hp, c.fracao * s.hpMax);
      E = { ...E, L: E.L.map((x, i) => i === l ? { ...x, hp: x.hp + ganho } : x) };
      (cura ??= [0, 0])[l] = ganho; pendentes[l] = null;
    }
    turnos.push({ t: E.turno, a: aa, ma, b: ab, mb, antes, depois: E, dano: r.dano, interr: r.interr, errou: r.errou, ...(cura ? { cura } : {}) });
  }
  return { E0, turnos, pontosA: fim[0], fim: fim[1], E };
}
