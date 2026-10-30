/* Combate V2.1 (espelho de digilab/combate_v2/ e combate_v2/v21/, regras corrigidas V2C/V21C): os tipos, o catalogo de gambits e o
   perfil de cada lutador. O combate por turnos (jogarV2, resolverV2) saiu na COMBATE-TR R3: toda luta do v13 e em tempo real
   (combate_tr/). Cada lutador tem um PERFIL (catalogo.ts) e, conforme o estagio, a tecnica da linha (adolescente) e a passiva da
   forma (adulto). */
import { CV, CV21, CV21E_TR, TECNICAS } from "./constantes.ts";
import type { ResultadoLutaTR } from "./combate_tr/luta.ts";
import type { Perfil } from "./catalogo.ts";
import type { Estagio } from "./tipos.ts";

export const ACOES_V2: readonly string[] = ["avancar", "recuar", "golpe_rapido", "preparar_pesado", "disparo", "defender", "esquivar", "carregar", ...TECNICAS];
/* V2C: fintar so existe no turno de execucao do pesado (alternativa a executar) */
export const ACOES_V2_OBS: readonly string[] = [...ACOES_V2, "pesado", "fintar"];
export const DIST = ["perto", "medio", "longe"];
export const custoV2 = (a: string): number => CV.custo[a] ?? CV21.custo[a] ?? 0;
/** regras de uma luta (CV21E_TR, as dos pets v13): as chaves da V21D e da V21E que mudam as listas das formas (bots.gambitsAdulto) e o
    oponente_preparando (preparo sob pele oculto). Vale para a luta inteira, os dois lados, como as Regras do Python */
export interface RegrasV21 {
  readonly versaoPet: number;
  readonly preparoSobPeleOculto: boolean; readonly muralhaListaEspelho: boolean;
  readonly vigiaBateEmQuemRecua: boolean; readonly vigiaRecuaDoPreparoSobPele: boolean;
  /* V21E */
  readonly duelistaDefendeDoGolpe?: boolean; readonly titaDefendeDoGolpe?: boolean; readonly espelhoSemCarregar?: boolean;
  readonly muralhaSemCarregar?: boolean; readonly muralhaContraGolpeNaPele?: boolean;
  /** pets v13 (CV21E_TR): a luta e jogada em tempo real (combate_tr/adaptador.ts, jogarLuta) */
  readonly tempoReal?: boolean;
}
export type RegrasLuta = RegrasV21;
/** as regras das lutas de uma versao de pet: so a v13 (CV21E_TR); as outras falham alto */
export const regrasDaVersao = (versao: number): RegrasLuta => {
  if (versao !== CV21E_TR.versaoPet) throw new Error(`regras de luta da versão ${versao} não existem mais (só a ${CV21E_TR.versaoPet})`);
  return CV21E_TR;
};

export interface Lado {
  p: Perfil; hp: number; hpMax: number; guts: number; gutsMax: number; regen: number; prep: boolean; hist: string[];
  marca: number; pele: number; recarga: number; disparou: boolean;
  /** o preparo do pesado em curso foi feito com pele_dura ativa (so e lido com preparoSobPeleOculto) */
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
/** quem foi desafiado na luta (0 = lado A, 1 = lado B) ou null (ninguem: o limite decide pela fracao de vida, como sempre). Regra do
    limite (decisao do Matheus, 2026-09-30, so no jogo): a luta que chega ao limite sem KO e do desafiado. O pet (lado A) sempre
    desafia (desafiadoDaVersao), tambem na Liga dos Lideres da Fronteira (o desafiado e o lider; liga.ts) */
export type Desafiado = 0 | 1 | null;
/** versao de pet a partir da qual o limite e do desafiado */
export const VERSAO_LIMITE_DESAFIADO = 6;
/** o desafiado nas lutas do motor (o pet e o lado A): o rival (lado B); so a v13 existe, as outras falham alto */
export const desafiadoDaVersao = (versao: number): Desafiado => {
  if (versao !== CV21E_TR.versaoPet) throw new Error(`desafiado da versão ${versao} não existe mais (só a ${CV21E_TR.versaoPet})`);
  return 1;
};

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
export const Cd = (n: string, ...p: (number | string)[]): Cond => ({ n, p });
export const Rg = (se: Cond | Cond[], entao: string): Regra => ({ se: Array.isArray(se) ? se : [se], entao });

export interface Lutador { nome: string; estilo: Estilo; cond: Perfil; sombra?: boolean }
/** o resultado de uma luta (combate_tr/adaptador.ts, jogarLuta): E0 e E trazem so a vida e o guts do comeco e do fim; o resto (as acoes,
    o saldo de cada uma, a duracao) esta em `tr`, a luta em tempo real (pets v13) */
export interface ResultadoLuta { E0: EstadoLuta; pontosA: number; fim: "ko" | "limite"; E: EstadoLuta; tr: ResultadoLutaTR }

/** efeito de uma carta na luta (itens.ts; pets v6): `guts` a mais no comeco, `foco` = sem exploracao (epsilon 0), e a `cura`: na
    primeira vez que a vida cai abaixo de `abaixo` da maxima (e o lado nao caiu), cura `fracao` da vida maxima, uma vez */
export interface CuraLuta { abaixo: number; fracao: number }
export interface EfeitoCarta { guts?: number; foco?: boolean; cura?: CuraLuta }
/** a carta no lutador: o guts a mais entra no guts do comeco (ate o maximo) e o foco zera a exploracao. A cura e da luta (combate_tr/luta.ts, jogarTR) */
export function comCarta(L: Lutador, ef: EfeitoCarta | null): Lutador {
  if (!ef) return L;
  const cond = ef.guts ? { ...L.cond, guts0: Math.min(L.cond.gutsMax, L.cond.guts0 + ef.guts) } : L.cond;
  return { ...L, cond, estilo: ef.foco ? { ...L.estilo, eps: 0 } : L.estilo };
}
