/* A Liga dos Lideres na Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 2 e 4; medalhas parte 4a; so no jogo e so nos pets v6).
   O final do jogo: com as 6 medalhas, o pet enfrenta os 6 lideres das arenas em sequencia, na ordem das arenas (Campina -> Espiral),
   cada um lutando com um Mega do jogo, de um arquetipo diferente, com a lista canonica dele sob as regras da luta. Regras da Liga:
   - sem cura entre as lutas: a vida e o guts do pet passam de uma luta para a outra (como na serie da Cidadela, arenas.jogarSerie);
     o lider de cada luta comeca inteiro;
   - os chips equipados valem (estao no pet: treino e lista); as cartas NAO valem (o motor recusa carta antes da luta da Liga);
   - o limite de turnos e do desafiado, o lider (combate.desafiadoDaVersao: nos pets v6 o rival);
   - perder uma luta encerra a tentativa; tentar de novo nao custa nada.
   A forca dos rivais: estagio Mega na escala dos pets (CESC_V9: a vida e o beta que eram os da escala dos v6), sem treino, vezes FATOR_LIGA. SEM calibracao (decisao do Matheus:
   sem rodada de equilibrio nesta parte). O desenho pedia o fator do Piedmon na arena da Espiral (1,6); com ele cada luta sozinha e
   vencivel pela forma certa, mas a Liga inteira (sem cura) nao: nenhuma forma, em nenhuma especie, venceu as 6 na conferencia
   (test/conferir_liga.mjs, artifacts_campanha/liga/conferencia.json). O jogo tem de ser completavel, entao a Liga ficou SEM fator
   (1: o Mega na escala, como ele e; o Piedmon da Espiral precisava do fator porque e um NPC de perfil neutro, sem tecnica nem
   passiva, e os Megas da Liga lutam com a tecnica, a passiva e a lista canonica). Desvio registrado em docs/REGISTRO_DESVIOS.md.

   Registro e replay: a tentativa inteira e UM evento de luta "l" do registro do pet, com o rival RIVAL_LIGA e a semente (as lutas 2 a 6
   usam sementes derivadas, arenas.sementeDaSerie), como a serie da Cidadela. Nada novo no formato do registro: a regra sai do rival.
   O titulo (vencer as 6) vai para o registro do Tamer (src/tamer.ts, evento "campeao"); o motor do pet nao le o Tamer: a entrada
   confere as medalhas que o pet conhece (evento "u"). */
import { ARENA_POR_ID, jogarSerie } from "./arenas.ts";
import { copiarGambits, gambitsAdulto } from "./bots.ts";
import { ESCALA, caraterCanonico, perfilDe } from "./catalogo.ts";
import { CV, LINHA_DA_FORMA, VERSAO_PET } from "./constantes.ts";
import type { Desafiado, Lutador, RegrasLuta, ResultadoLuta } from "./combate.ts";
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

/* A Liga dos pets v9 (rodada de equilibrio geral, fase 3; docs/EQUILIBRIO_GERAL.md, meta M-C1): as mesmas 6 lutas, os mesmos Megas e as
   mesmas regras, com o fator de cada lider calibrado (FATOR_LIGA_V9, por arena) e uma cura parcial entre as lutas (CURA_LIGA_V9: depois
   de cada vitoria o pet recupera esta fracao da vida maxima; o guts passa como esta). Vale pela versao das regras da luta (R.versaoPet >= 9,
   as lutas dos pets v9); os pets v6-v8 seguem com FATOR_LIGA e sem cura. test/conferir_liga.mjs --calibrar (sementes de calibracao),
   artifacts_equilibrio_geral/fase3/liga_calibracao.json: a cura foi medida (0 a 0,5) e a escolhida e 0 (sem cura, como antes: com cura
   nenhuma busca passou de 6 formas na faixa, e o furioso sobe: o dreno e o que o segura); os fatores sao os da busca (7 das 8 formas na
   faixa; a muralha nao chega a 0,25 com nenhum, presa ao MegaGargomon e aos empates no limite contra Seraphimon e Rosemon). PROPOSTOS */
/** versao de pet da Liga da fase 3 (a do combate V21E) */
export const VERSAO_LIGA_V9 = 9;
export const FATOR_LIGA_V9: Readonly<Record<string, number>> = { campina: .4, torre: .3, floresta: .1, cidadela: 1, lago: 1.7, espiral: .9 };
export const CURA_LIGA_V9 = 0;
if (LIGA.some(x => FATOR_LIGA_V9[x.arena] === undefined) || Object.keys(FATOR_LIGA_V9).length !== LIGA.length) throw new Error("FATOR_LIGA_V9 sem um lider por arena");
const ehV9 = (R: RegrasLuta): boolean => R.versaoPet >= VERSAO_LIGA_V9;
/** o fator do lider i nas lutas destas regras: o da Liga dos v9 (R dos pets v9) ou FATOR_LIGA */
export const fatorLiga = (i: number, R: RegrasLuta): number => {
  const x = LIGA[i];
  if (!x) throw new Error("lider da Liga desconhecido: " + i);
  return ehV9(R) ? FATOR_LIGA_V9[x.arena] : FATOR_LIGA;
};
/** a cura entre as lutas da Liga nestas regras: CURA_LIGA_V9 nos pets v9; 0 (sem cura) nos v6-v8 */
export const curaLiga = (R: RegrasLuta): number => ehV9(R) ? CURA_LIGA_V9 : 0;

/** a forma do Mega do lider i (ramo sereno, como os bots canonicos da bateria) */
export function formaLiga(i: number): Forma {
  const x = LIGA[i];
  if (!x) throw new Error("lider da Liga desconhecido: " + i);
  return { esp: x.esp, est: "mega", ramo: "sereno", linha: LINHA_DA_FORMA[x.adulta], adulta: x.adulta };
}
/** o nome do Mega do lider i na tela (o Digimon da cadeia) */
export const nomeMegaLiga = (i: number): string => nomeForma(formaLiga(i));
/** o lutador do lider i: o Mega com a tecnica da linha, a passiva da forma, o carater canonico e a lista canonica dele sob as regras
    da luta (a muralha com a lista do espelho); epsilon dos bots canonicos. Com a escala ligada (o app): E = vida do
    Mega na escala dos pets x fator (fatorLiga: FATOR_LIGA nos v6-v8, FATOR_LIGA_V9 nos v9; outro so na conferencia), sem treino */
export function lutadorLiga(i: number, R: RegrasLuta, fator: number = fatorLiga(i, R)): Lutador {
  const f = formaLiga(i), x = LIGA[i];
  const p = perfilDe(f, caraterCanonico(x.adulta), 1, null, true, VERSAO_PET);
  const cond = ESCALA.ligada ? { ...p, escala: p.escala! * fator } : p;
  return { nome: "Rival " + nomeForma(f), estilo: { nome: `liga:${x.arena}`, gambits: copiarGambits(gambitsAdulto(x.adulta, R)), eps: CV.eps }, cond };
}
/** os 6 lutadores da Liga, na ordem. `fator`: um so para os 6 (a conferencia) ou um por lider; sem ele, o das regras (fatorLiga) */
export const lutadoresLiga = (R: RegrasLuta, fator?: number | readonly number[]): Lutador[] =>
  LIGA.map((_, i) => lutadorLiga(i, R, fator === undefined ? fatorLiga(i, R) : typeof fator === "number" ? fator : fator[i]));
/** a tentativa da Liga como o motor a joga: as 6 lutas seguidas contra `lideres` (os das regras), parando na primeira que nao for vitoria,
    sem carta, com a cura entre as lutas das regras (curaLiga; `cura` so na calibracao) */
export const jogarLiga = (A: Lutador, semente: number, R: RegrasLuta, desafiado: Desafiado, lideres: readonly Lutador[] = lutadoresLiga(R),
  cura: number = curaLiga(R)): ResultadoLuta[] => jogarSerie(A, lideres, semente, R, desafiado, null, cura);
