/* A porta das lutas do motor (COMBATE-TR, etapa R2): jogarLuta joga em tempo real quando as regras da luta pedem (CV21E_TR, pets v13) e
   por turnos nas outras (jogarV2), e devolve sempre o ResultadoLuta de hoje. Na luta em tempo real, o resultado traz em `tr` as acoes, o
   saldo de cada uma e a duracao; `turnos` vem vazio, e E0 e E so tem a vida e o guts do comeco e do fim (o que as series, a Liga, as
   instalacoes e a Fabrica passam de uma luta para a outra). As series, a Liga, o Salao, as instalacoes, a Fabrica e as telas jogam por
   aqui, entao a versao do pet decide sozinha qual combate vale. */
import { estadoV2, jogarV2, type CuraLuta, type Desafiado, type EstadoLuta, type Lutador, type RegrasLuta, type ResultadoLuta } from "../combate.ts";
import { PASSO_TR_MS } from "./constantes_tr.ts";
import { faixaTR } from "./controlador.ts";
import { jogarTR, type ResultadoLutaTR } from "./luta.ts";

/** o ResultadoLuta de uma luta em tempo real: E0 e E com a vida e o guts do comeco e do fim; a distancia de E e a faixa do fim */
export function comoResultadoLuta(A: Lutador, B: Lutador, r: ResultadoLutaTR): ResultadoLuta {
  const base = estadoV2(A.cond, B.cond);
  const E0: EstadoLuta = { ...base, L: base.L.map((l, i) => ({ ...l, hp: r.E0.hp[i], guts: r.E0.guts[i] })) };
  const E: EstadoLuta = {
    turno: 0, dist: faixaTR(r.E),
    L: base.L.map((l, i) => ({ ...l, hp: r.E.L[i].hp, guts: r.E.L[i].guts, hist: r.E.L[i].hist.slice() })),
  };
  return { E0, turnos: [], pontosA: r.pontosA, fim: r.fim, E, tr: r };
}

/** uma luta pelas regras dela: em tempo real com R.tempoReal (pets v13), por turnos nas outras. Os parametros sao os do jogarV2 */
export function jogarLuta(A: Lutador, B: Lutador, semente: number, R: RegrasLuta = null, ini: { hp: number; guts: number } | null = null,
  desafiado: Desafiado = null, curas: readonly (CuraLuta | null)[] | null = null): ResultadoLuta {
  if (!R?.tempoReal) return jogarV2(A, B, semente, R, ini, desafiado, curas);
  return comoResultadoLuta(A, B, jogarTR(A, B, semente, { R, ini, desafiado, curas }));
}

/** a carta de Cura do lado A ja curou nesta luta (as series gastam a cura uma vez so) */
export const curouA = (res: ResultadoLuta): boolean => res.tr ? res.tr.curou[0] : res.turnos.some(t => t.cura);

/** quanto a luta durou, para a tela: "48 s" no tempo real, "24 turnos" por turnos */
export function duracaoLuta(res: ResultadoLuta): string {
  if (res.tr) return `${Math.floor(res.tr.passos * PASSO_TR_MS / 1000)} s`;
  return `${res.turnos.length} turno${res.turnos.length === 1 ? "" : "s"}`;
}
/** a luta durou isto em "unidades" de comparacao (o recorde do mais rapido na Campanha e na Fronteira): segundos no tempo real, turnos
    por turnos */
export const tamanhoLuta = (res: ResultadoLuta): number => res.tr ? Math.floor(res.tr.passos * PASSO_TR_MS / 1000) : res.turnos.length;
