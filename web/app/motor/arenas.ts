/* Arenas com lideres (docs/DESIGN_MEDALHAS_ARENAS.md, secao 3; parte 2; so no jogo, pets v6). Cada lugar da campanha v6
   (bots.LUGARES_V6) tem uma arena, com um lider e uma regra propria; vencer o lider da a medalha da arena (medalhas.ts).
   A regra so vale na luta de um pet v6 contra o lider, e depende so do rival e da versao do pet, que o registro ja tem (o
   evento de luta "l" grava rival e semente): o replay refaz a mesma luta sem campo novo no evento.

   As regras (o que cada arena testa):
   - Campina (Rookie), Gazimon: nenhuma (o basico: cuidado e treino);
   - Torre de pedra (Champion), Guardromon: PACIENCIA. O lider tem o contra-golpe (a tecnica do guardiao) e a lista do espelho
     com as regras dele: quem prepara o pesado de perto ou insiste no golpe rapido leva o golpe de volta;
   - Floresta (Champion, nova), Youkomon: LEITURA. O lider muda de padrao no turno 10 (bots.GAMBITS_ARENA.floresta, pela
     condicao de turno da linguagem de gambits): de atirador vira brigao;
   - Cidadela (Ultimate), Myotismon: RESISTENCIA. Tres lutas seguidas, sem cura: a vida e o guts do pet passam de uma para a
     outra (o lider volta inteiro); a vitoria (e a medalha) so vem com as tres;
   - Lago (Ultimate, novo), MarinBullmon: VINCULO. As travas e os vetos do dono nao valem: o pet luta com a lista que ele
     mesmo faria (GambitsPet.listaSozinho);
   - Montanha Espiral (Mega), Piedmon: o chefe da campanha, sem regra a mais.

   Fatores dos lideres: calibrados no motor web com as regras dos pets v6 (test/calibrar_arenas.mjs,
   artifacts_campanha/arenas/): sem treino <= 0,30 e com o treino tipico >= 0,80, sem forma travada. PROPOSTOS. O fator fica
   aqui quando a luta de arena muda um NPC que ja existia (Guardromon 1,4 no lugar de 1,5; Myotismon 0,7 na serie, no lugar de
   1,2); os lideres novos tem o fator no proprio NPC (bots.CAMPANHA_V6: Youkomon 1,2, MarinBullmon 1,2). Campina e Montanha
   Espiral ficam com os fatores de sempre (1,1 e 1,2), medidos de novo com as regras dos pets v6. */
import { jogarV2, type Lutador, type RegrasLuta, type ResultadoLuta } from "./combate.ts";
import type { Tecnica } from "./constantes.ts";
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
  /** fator de escala do lider na luta de arena; sem ele, o do NPC (fator ou CESC.fatorNpc) */
  fator?: number;
  /** tecnica do lider (Torre de pedra: contra-golpe); as regras dela ficam na lista dele */
  tecnica?: Tecnica;
  /** lutas seguidas, sem cura (Cidadela: 3); sem ele, 1 */
  lutas?: number;
}
/** versao de pet em que as arenas valem (a das medalhas) */
export const VERSAO_ARENAS = 6;
export const ARENAS: readonly Arena[] = [
  { id: "campina", lugar: 0, lider: "npc_tier1_brutamontes", regra: "nenhuma", titulo: "O básico",
    frase: "Sem regra especial: vence o pet bem cuidado e treinado." },
  { id: "torre", lugar: 1, lider: "npc_tier2_carcereiro", regra: "paciencia", titulo: "Paciência", tecnica: "contra_golpe", fator: 1.4,
    frase: "O líder devolve golpe forte: preparar o pesado de perto ou insistir no golpe rápido volta contra você." },
  { id: "floresta", lugar: 2, lider: "npc_v6_youkomon", regra: "leitura", titulo: "Leitura",
    frase: "O líder muda de padrão no turno 10: de longe e disparando, depois colado e golpeando. Vence quem lê o rival." },
  { id: "cidadela", lugar: 3, lider: "npc_v5_myotismon", regra: "resistencia", titulo: "Resistência", lutas: 3, fator: .7,
    frase: "Três lutas seguidas, sem cura: a vida e o guts passam de uma para a outra. A medalha só vem com as três." },
  { id: "lago", lugar: 4, lider: "npc_v6_marinbullmon", regra: "vinculo", titulo: "Vínculo",
    frase: "Aqui as travas e os vetos do dono não valem: o pet decide sozinho, com as regras que ele mesmo aprendeu." },
  { id: "espiral", lugar: 5, lider: "npc_v5_piedmon", regra: "chefe", titulo: "O chefe",
    frase: "O chefe da campanha: forte em tudo. Pede tudo o que o pet aprendeu." },
];
export const ARENA_POR_ID: Readonly<Record<string, Arena>> = Object.fromEntries(ARENAS.map(a => [a.id, a]));
/** a arena de que o NPC e lider (null: ele e desafiante) */
export const arenaDoLider = (k: string): Arena | null => ARENAS.find(a => a.lider === k) ?? null;
/** a arena cuja regra vale nesta luta: so pets v6 contra o lider */
export const arenaDaLuta = (rival: string, versao: number): Arena | null => versao >= VERSAO_ARENAS ? arenaDoLider(rival) : null;
/** semente da luta k (0 = a primeira) de uma serie: a primeira e a semente do evento; as outras saem dela */
export const sementeDaSerie = (semente: number, k: number): number => k ? hashSemente("serie-arena", semente, k) : semente;
/** a luta (ou as lutas seguidas) de arena: `lutas` lutas, parando na primeira que nao for vitoria; da segunda em diante o
    pet (lado A) comeca com a vida e o guts do fim da anterior, e o lider (B) volta inteiro. Deterministico */
export function jogarArena(A: Lutador, B: Lutador, semente: number, R: RegrasLuta, lutas = 1): ResultadoLuta[] {
  if (!Number.isInteger(lutas) || lutas < 1) throw new Error("lutas da arena inválidas: " + lutas);
  const serie: ResultadoLuta[] = [];
  let ini: { hp: number; guts: number } | null = null;
  for (let k = 0; k < lutas; k++) {
    const res = jogarV2(A, B, sementeDaSerie(semente, k), R, ini);
    serie.push(res);
    if (res.pontosA !== 1) break;
    ini = { hp: res.E.L[0].hp, guts: res.E.L[0].guts };
  }
  return serie;
}
