/* Medalhas do Tamer (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 3 e 4; so no jogo, a pesquisa em Python nao tem Tamer).
   TABELA UNICA de onde cada medalha vem: a parte 2 (arenas com lideres) troca so esta tabela. Decisao do Matheus: 6
   arenas. Nesta parte so existem os 4 lugares da campanha v5, entao duas medalhas tem FONTE PROVISORIA (marcada em
   `provisoria`): a 3 (a arena da Floresta ainda nao existe: vencer o Devidramon na Torre de pedra) e a 5 (o Lago ainda
   nao existe: vencer o Machinedramon na Montanha Espiral). Uma medalha e ganha uma vez so por Tamer, na primeira
   vitoria contra o lider, com qualquer pet v6 (os v1-v5 nao tem Tamer). */
import { CMD } from "./constantes.ts";
import type { Estagio } from "./tipos.ts";

export interface Medalha {
  /** id interno (fica no registro do Tamer): o da arena do desenho, mesmo quando a fonte e provisoria */
  id: string;
  /** nome na tela */
  nome: string;
  /** o lider: chave do NPC da campanha v5 (motor/bots.ts, CAMPANHA_V5) */
  lider: string;
  /** indice do lugar da campanha v5 onde o lider fica hoje (LUGARES_V5) */
  lugar: number;
  /** fonte provisoria: o texto diz ate quando */
  provisoria?: string;
}
export const MEDALHAS: readonly Medalha[] = [
  { id: "campina", nome: "Medalha da Campina", lider: "npc_tier1_brutamontes", lugar: 0 },
  { id: "torre", nome: "Medalha da Torre de pedra", lider: "npc_tier2_carcereiro", lugar: 1 },
  { id: "floresta", nome: "Medalha do Devidramon", lider: "npc_tier2_porteiro", lugar: 1, provisoria: "até a arena da Floresta existir" },
  { id: "cidadela", nome: "Medalha da Cidadela", lider: "npc_v5_myotismon", lugar: 2 },
  { id: "lago", nome: "Medalha do Machinedramon", lider: "npc_v5_machinedramon", lugar: 3, provisoria: "até a arena do Lago existir" },
  { id: "espiral", nome: "Medalha da Montanha Espiral", lider: "npc_v5_piedmon", lugar: 3 },
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
