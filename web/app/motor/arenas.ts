/* Arenas com lideres (docs/DESIGN_MEDALHAS_ARENAS.md, secao 3; parte 2; so no jogo). Cada lugar da campanha (bots.LUGARES_V6) tem uma
   arena, com um lider; vencer o lider da a medalha da arena (medalhas.ts). Na luta da POC (LUTA_POC, LP2, decisao 5; LP4) das regras das
   arenas fica so a serie da Cidadela (tres lutas seguidas sem cura para o pet; o lider volta inteiro), e cada lugar luta no mapa dele (LP-4,
   luta_poc.mapaDoLugar). A regra depende so do rival, que o registro ja tem (o evento de luta "l" grava rival, semente e mapa).
   Os fatores, as tecnicas e as listas dos lideres eram do combate por turnos e sairam com ele (LP4). */
import { hashSemente } from "./rng.ts";

export type RegraArena = "nenhuma" | "paciencia" | "leitura" | "resistencia" | "vinculo" | "chefe";
export interface Arena {
  /** o id da medalha da arena (medalhas.ts) */
  id: string;
  /** indice do lugar em LUGARES_V6 */
  lugar: number;
  /** o lider: chave do NPC (bots.ts) */
  lider: string;
  regra: RegraArena;
  /** o nome curto da regra, na tela */
  titulo: string;
  /** a regra em uma frase, na tela */
  frase: string;
  /** lutas seguidas, sem cura (Cidadela: 3); sem ele, 1 */
  lutas?: number;
}
export const ARENAS: readonly Arena[] = [
  { id: "campina", lugar: 0, lider: "npc_tier1_brutamontes", regra: "nenhuma", titulo: "O básico",
    frase: "Sem regra especial: vence o pet bem cuidado e treinado." },
  { id: "torre", lugar: 1, lider: "npc_tier2_carcereiro", regra: "paciencia", titulo: "A arena que fecha",
    frase: "Luta no Coliseu: aos 30 segundos a área segura começa a encolher, e fora dela a vida cai." },
  { id: "floresta", lugar: 2, lider: "npc_v6_youkomon", regra: "leitura", titulo: "A mata",
    frase: "Luta na Floresta: as árvores bloqueiam corpos e tiros, e quem entra na moita fica escondido." },
  { id: "cidadela", lugar: 3, lider: "npc_v5_myotismon", regra: "resistencia", titulo: "Resistência", lutas: 3,
    frase: "Três lutas seguidas, sem cura: a vida passa de uma para a outra. A medalha só vem com as três." },
  { id: "lago", lugar: 4, lider: "npc_v6_marinbullmon", regra: "vinculo", titulo: "A maré",
    frase: "Luta na Praia: a maré sobe e desce, e na água o pet anda mais devagar." },
  { id: "espiral", lugar: 5, lider: "npc_v5_piedmon", regra: "chefe", titulo: "O chefe",
    frase: "O chefe da campanha, na Caverna: a lava queima e o chão entra em erupção." },
];
export const ARENA_POR_ID: Readonly<Record<string, Arena>> = Object.fromEntries(ARENAS.map(a => [a.id, a]));
/** a arena de que o NPC e lider (null: ele e desafiante) */
export const arenaDoLider = (k: string): Arena | null => ARENAS.find(a => a.lider === k) ?? null;
/** a arena cuja regra vale nesta luta: contra o lider dela. `versao` fica na assinatura por quem chama (a v21 e o unico pet que luta) */
export const arenaDaLuta = (rival: string, _versao?: number): Arena | null => arenaDoLider(rival);
/** semente da luta k (0 = a primeira) de uma serie: a primeira e a semente do evento; as outras saem dela */
export const sementeDaSerie = (semente: number, k: number): number => k ? hashSemente("serie-arena", semente, k) : semente;
