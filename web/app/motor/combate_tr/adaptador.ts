/* A porta das lutas do motor (COMBATE-TR, etapas R2 e R3): jogarLuta joga sempre em tempo real (CV21E_TR, pets v13) e devolve o
   ResultadoLuta; o resultado traz em `tr` as acoes, o saldo de cada uma e a duracao, e E0 e E so tem a vida e o guts do comeco e do
   fim (o que as series, a Liga, as instalacoes e a Fabrica passam de uma luta para a outra). O combate por turnos saiu na R3. As
   series, a Liga, o Salao, as instalacoes, a Fabrica e as telas jogam por aqui. */
import { estadoV2, type CuraLuta, type Desafiado, type EstadoLuta, type Lutador, type RegrasLuta, type ResultadoLuta } from "../combate.ts";
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
  return { E0, pontosA: r.pontosA, fim: r.fim, E, tr: r };
}

/** uma luta pelas regras dela: sempre em tempo real; regras que nao pedem o tempo real (R.tempoReal) falham alto. `ini`: o lado A
    comeca com esta vida e este guts; `desafiado`: quem fica com a luta no limite de tempo; `curas`: a carta de Cura de cada lado */
export function jogarLuta(A: Lutador, B: Lutador, semente: number, R: RegrasLuta, ini: { hp: number; guts: number } | null = null,
  desafiado: Desafiado = null, curas: readonly (CuraLuta | null)[] | null = null): ResultadoLuta {
  if (!R?.tempoReal) throw new Error("só há luta em tempo real: as regras da luta têm de ser as dos pets v13 (tempoReal)");
  return comoResultadoLuta(A, B, jogarTR(A, B, semente, { R, ini, desafiado, curas }));
}

/** a carta de Cura do lado A ja curou nesta luta (as series gastam a cura uma vez so) */
export const curouA = (res: ResultadoLuta): boolean => res.tr.curou[0];

/** quanto a luta durou, para a tela: "48 s" */
export function duracaoLuta(res: ResultadoLuta): string {
  return `${Math.floor(res.tr.passos * PASSO_TR_MS / 1000)} s`;
}
/** a luta durou isto em "unidades" de comparacao (o recorde do mais rapido na Campanha e na Fronteira): segundos */
export const tamanhoLuta = (res: ResultadoLuta): number => Math.floor(res.tr.passos * PASSO_TR_MS / 1000);
