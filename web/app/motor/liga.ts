/* A Liga dos Lideres na Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 2 e 4; medalhas parte 4a; so no jogo e so nos pets v6).
   O final do jogo: com as 6 medalhas, o pet enfrenta os 6 lideres das arenas em sequencia, na ordem das arenas (Campina -> Espiral),
   cada um lutando com um Mega do jogo, de um arquetipo diferente, com a lista canonica dele (V21D). Regras da Liga:
   - sem cura entre as lutas: a vida e o guts do pet passam de uma luta para a outra (como na serie da Cidadela, arenas.jogarSerie);
     o lider de cada luta comeca inteiro;
   - os chips equipados valem (estao no pet: treino e lista); as cartas NAO valem (o motor recusa carta antes da luta da Liga);
   - o limite de turnos e do desafiado, o lider (combate.desafiadoDaVersao: nos pets v6 o rival);
   - perder uma luta encerra a tentativa; tentar de novo nao custa nada.
   A forca dos rivais: estagio Mega na escala dos pets v6 (CESC_V6), sem treino, vezes FATOR_LIGA. SEM calibracao (decisao do Matheus:
   sem rodada de equilibrio nesta parte). O desenho pedia o fator do Piedmon na arena da Espiral (1,6); com ele cada luta sozinha e
   vencivel pela forma certa, mas a Liga inteira (sem cura) nao: nenhuma forma, em nenhuma especie, venceu as 6 na conferencia
   (test/conferir_liga.mjs, artifacts_campanha/liga/conferencia.json). O jogo tem de ser completavel, entao a Liga ficou SEM fator
   (1: o Mega na escala, como ele e; o Piedmon da Espiral precisava do fator porque e um NPC de perfil neutro, sem tecnica nem
   passiva, e os Megas da Liga lutam com a tecnica, a passiva e a lista canonica). Desvio registrado em docs/REGISTRO_DESVIOS.md.

   Registro e replay: a tentativa inteira e UM evento de luta "l" do registro do pet, com o rival RIVAL_LIGA e a semente (as lutas 2 a 6
   usam sementes derivadas, arenas.sementeDaSerie), como a serie da Cidadela. Nada novo no formato do registro: a regra sai do rival.
   O titulo (vencer as 6) vai para o registro do Tamer (src/tamer.ts, evento "campeao"); o motor do pet nao le o Tamer: a entrada
   confere as medalhas que o pet conhece (evento "u"). */
import { ARENA_POR_ID } from "./arenas.ts";
import { copiarGambits, gambitsAdulto } from "./bots.ts";
import { ESCALA, caraterCanonico, perfilDe } from "./catalogo.ts";
import { CV, LINHA_DA_FORMA } from "./constantes.ts";
import type { Lutador, RegrasLuta } from "./combate.ts";
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
/** o fator de rival dos Megas da Liga: 1 (sem fator; ver o cabecalho). O do desenho, o do Piedmon na arena da Espiral, fica em
    FATOR_LIGA_DESENHO para a conferencia */
export const FATOR_LIGA = 1;
export const FATOR_LIGA_DESENHO: number = (() => {
  const f = ARENA_POR_ID.espiral?.fator;
  if (f === undefined) throw new Error("a arena da Montanha Espiral sem fator");
  return f;
})();
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
/** o lutador do lider i: o Mega com a tecnica da linha, a passiva da forma, o carater canonico e a lista canonica dele sob as regras
    da luta (V21D nos pets v6: a muralha com a lista do espelho); epsilon dos bots canonicos. Com a escala ligada (o app): E = vida do
    Mega na escala dos pets v6 x fator (FATOR_LIGA; outro so na conferencia), sem treino */
export function lutadorLiga(i: number, R: RegrasLuta, fator: number = FATOR_LIGA): Lutador {
  const f = formaLiga(i), x = LIGA[i];
  const p = perfilDe(f, caraterCanonico(x.adulta), 1, null, true, VERSAO_LIGA);
  const cond = ESCALA.ligada ? { ...p, escala: p.escala! * fator } : p;
  return { nome: "Rival " + nomeForma(f), estilo: { nome: `liga:${x.arena}`, gambits: copiarGambits(gambitsAdulto(x.adulta, R)), eps: CV.eps }, cond };
}
/** os 6 lutadores da Liga, na ordem */
export const lutadoresLiga = (R: RegrasLuta, fator: number = FATOR_LIGA): Lutador[] => LIGA.map((_, i) => lutadorLiga(i, R, fator));
