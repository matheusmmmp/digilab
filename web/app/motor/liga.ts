/* A Liga dos Lideres na Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 2 e 4; medalhas parte 4a; so no jogo). O final do jogo:
   com as 6 medalhas, o pet enfrenta os 6 lideres das arenas em sequencia, na ordem das arenas (Campina -> Espiral), cada um lutando com um
   Mega do jogo, de um arquetipo diferente. Na luta da POC (LUTA_POC, LP2b; LP4): sem cura entre as lutas (a vida do pet passa de uma luta
   para a outra; o lider de cada luta comeca inteiro), cada lider no mapa do lugar dele (LP-4), com o perfil canonico do Mega pelo mapeamento
   da LP2-2 (Motor._rivalPoc); perder uma luta encerra a tentativa. Os fatores, a cura dos v9 e as listas eram do combate por turnos e sairam.

   Registro e replay: a tentativa inteira e UM evento de luta "l" do registro do pet, com o rival RIVAL_LIGA e a semente (as lutas 2 a 6
   usam sementes derivadas, arenas.sementeDaSerie), como a serie da Cidadela. O titulo (vencer as 6) vai para o registro do Tamer
   (src/tamer.ts, evento "campeao"); o motor do pet nao le o Tamer: a entrada confere as medalhas que o pet conhece (evento "u"). */
import { ARENA_POR_ID } from "./arenas.ts";
import { LINHA_DA_FORMA } from "./constantes.ts";
import { MEDALHAS } from "./medalhas.ts";
import { nomeForma } from "./nomes.ts";
import type { Especie, Forma, FormaAdultaNormal } from "./tipos.ts";
/** versao de pet em que a Liga existe (a das medalhas e das arenas) */
export const VERSAO_LIGA = 6;
/** a chave do rival no evento de luta "l" da Liga (a tentativa inteira) */
export const RIVAL_LIGA = "liga";
/** medalhas que a entrada na Fronteira pede: todas */
export const MEDALHAS_LIGA = MEDALHAS.length;

export interface LiderLiga {
  /** a arena (e a medalha) do lider: arenas.ts, medalhas.ts */
  arena: string;
  /** o lider: chave do NPC da campanha v6 (bots.ts) */
  lider: string;
  /** o Mega com que ele luta: a especie e o arquetipo (a forma adulta; o Mega da cadeia e o mesmo Digimon para as duas formas
      adultas da linha, o arquetipo e que muda) */
  esp: Especie;
  adulta: FormaAdultaNormal;
}
/* a tabela do desenho (secao 2): 6 arquetipos distintos entre os 8, as 4 especies. Nomes na tela: WarGreymon, Seraphimon,
   MegaGargomon, Vikemon, Rosemon e Imperialdramon Dragon Mode (nomes.nomeForma). Todos os sprites ja estao no atlas */
export const LIGA: readonly LiderLiga[] = [
  { arena: "campina", lider: "npc_tier1_brutamontes", esp: "brasa", adulta: "furioso" },
  { arena: "torre", lider: "npc_tier2_carcereiro", esp: "cirro", adulta: "espelho" },
  { arena: "floresta", lider: "npc_v6_youkomon", esp: "ferrugem", adulta: "sentinela" },
  { arena: "cidadela", lider: "npc_v5_myotismon", esp: "limo", adulta: "tita" },
  { arena: "lago", lider: "npc_v6_marinbullmon", esp: "limo", adulta: "muralha" },
  { arena: "espiral", lider: "npc_v5_piedmon", esp: "ferrugem", adulta: "duelista" },
];
/* a tabela confere na carga: um lider por arena, na ordem delas, e cada lider e o da arena */
LIGA.forEach((x, i) => {
  const ar = ARENA_POR_ID[x.arena];
  if (!ar || ar.lider !== x.lider || MEDALHAS[i].id !== x.arena) throw new Error(`Liga: o lider ${i + 1} não é o da arena ${x.arena}`);
});
if (new Set(LIGA.map(x => x.adulta)).size !== LIGA.length) throw new Error("Liga: arquétipos repetidos");

/** a forma do Mega do lider i (ramo sereno, como os bots canonicos da bateria) */
export function formaLiga(i: number): Forma {
  const x = LIGA[i];
  if (!x) throw new Error("lider da Liga desconhecido: " + i);
  return { esp: x.esp, est: "mega", ramo: "sereno", linha: LINHA_DA_FORMA[x.adulta], adulta: x.adulta };
}
/** o nome do Mega do lider i na tela (o Digimon da cadeia) */
export const nomeMegaLiga = (i: number): string => nomeForma(formaLiga(i));
