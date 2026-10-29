/* Os sorteios da arena (docs/TAREFA_V2_UP_ARENA.md, secao 10.4). O jogo usa um fluxo por uso: cada um e um mulberry32 (o criarRng do
   motor) semeado pelos 32 bits baixos de derivarSemente("arena", semente, fluxo); trocar a IA nao muda o dano nem as erupcoes.
   A sequencia unica existe SO para teste e medicao (P1, Matheus, 2026-10-29): os quatro usos tiram do mesmo gerador, na ordem do
   prototipo arena.html, o que reproduz as lutas medidas no arena_equilibrio.md. A tela nunca a usa. */
import { criarRng, type Rng } from "../motor/rng.ts";
import { derivarSemente } from "../motor/mundo.ts";
import type { Sorteios } from "./tipos.ts";

export const FLUXOS = ["ia", "combate", "cena", "visual"] as const;
export type Fluxo = typeof FLUXOS[number];

/** semente de 32 bits de um fluxo: os 32 bits baixos de derivarSemente("arena", semente, ...rotulos) */
export function sementeArena(semente: number, ...rotulos: (string | number)[]): number {
  return Number(derivarSemente("arena", semente, ...rotulos) & 0xffffffffn);
}

/** o jogo: um gerador por fluxo */
export function sorteiosPorFluxo(semente: number): Sorteios {
  const g = Object.fromEntries(FLUXOS.map(f => [f, criarRng(sementeArena(semente, f))])) as Record<Fluxo, Rng>;
  return { ia: () => g.ia.random(), combate: () => g.combate.random(), cena: () => g.cena.random(), visual: () => g.visual.random() };
}

/** so teste e medicao: um gerador para tudo, como o Math.random trocado do harness do prototipo */
export function sorteioUnico(rng: Rng): Sorteios {
  const r = () => rng.random();
  return { ia: r, combate: r, cena: r, visual: r };
}
