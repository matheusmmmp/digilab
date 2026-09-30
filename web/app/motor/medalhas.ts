/* Medalhas do Tamer (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 3 e 4; so no jogo, a pesquisa em Python nao tem Tamer).
   TABELA UNICA de onde cada medalha vem: uma por arena (decisao do Matheus: 6 arenas), dada pelo lider dela (as regras de
   cada arena ficam em arenas.ts). Desde a parte 2 (arenas com lideres) as seis tem fonte definitiva: a 3a vem do lider da
   Floresta (Youkomon) e a 5a do lider do Lago (MarinBullmon), no lugar das provisorias da parte 1 (Devidramon e Tortomon, na
   Torre de pedra). Os ids nao mudaram. Uma medalha e ganha uma vez so por Tamer, na primeira vitoria contra o lider (na
   Cidadela, a primeira serie de tres vitorias), com qualquer pet v6 (os v1-v5 nao tem Tamer). */
import { CMD } from "./constantes.ts";
import type { Estagio } from "./tipos.ts";

export interface Medalha {
  /** id interno (fica no registro do Tamer): o da arena */
  id: string;
  /** nome na tela */
  nome: string;
  /** o lider: chave do NPC da campanha v6 (motor/bots.ts, CAMPANHA_V6) */
  lider: string;
  /** indice do lugar da campanha v6 onde fica a arena (LUGARES_V6) */
  lugar: number;
  /** fonte provisoria (parte 1): nenhuma desde a parte 2; o campo sai junto com as telas */
  provisoria?: string;
}
export const MEDALHAS: readonly Medalha[] = [
  { id: "campina", nome: "Medalha da Campina", lider: "npc_tier1_brutamontes", lugar: 0 },
  { id: "torre", nome: "Medalha da Torre de pedra", lider: "npc_tier2_carcereiro", lugar: 1 },
  { id: "floresta", nome: "Medalha da Floresta", lider: "npc_v6_youkomon", lugar: 2 },
  { id: "cidadela", nome: "Medalha da Cidadela", lider: "npc_v5_myotismon", lugar: 3 },
  { id: "lago", nome: "Medalha do Lago", lider: "npc_v6_marinbullmon", lugar: 4 },
  { id: "espiral", nome: "Medalha da Montanha Espiral", lider: "npc_v5_piedmon", lugar: 5 },
];
export const MEDALHA_POR_ID: Readonly<Record<string, Medalha>> = Object.fromEntries(MEDALHAS.map(x => [x.id, x]));
/** a medalha que o lider da (null: o NPC nao e lider) */
export const medalhaDoLider = (k: string): Medalha | null => MEDALHAS.find(x => x.lider === k) ?? null;
/** medalhas que a evolucao para o estagio pede (pets v6); 0 = nenhuma */
export const medalhasPara = (alvo: Estagio): number => (CMD as Partial<Record<Estagio, number>>)[alvo] ?? 0;
/** o que cada medalha libera na evolucao: a n-esima medalha completa a conta de qual estagio (null: nenhum) */
export function estagioLiberadoPor(n: number): Estagio | null {
  const e = (Object.entries(CMD) as [Estagio, number][]).find(([, v]) => v === n);
  return e ? e[0] : null;
}
