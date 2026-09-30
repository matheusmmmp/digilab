/* Arenas com lideres (docs/DESIGN_MEDALHAS_ARENAS.md, secao 3; parte 2; so no jogo, pets v6). Cada lugar da campanha v6
   (bots.LUGARES_V6) tem uma arena, com um lider e uma regra propria; vencer o lider da a medalha da arena (medalhas.ts).
   A regra so vale na luta de um pet v6 contra o lider, e depende so do rival e da versao do pet, que o registro ja tem (o
   evento de luta "l" grava rival e semente): o replay refaz a mesma luta sem campo novo no evento.

   As regras (o que cada arena testa):
   - Campina (Rookie), Gazimon: nenhuma (o basico: cuidado e treino);
   - Torre de pedra (Champion), Guardromon: PACIENCIA. O lider tem o contra-golpe (a tecnica do guardiao) e a lista do espelho
     com as regras dele: quem prepara o pesado de perto ou insiste no golpe rapido leva o golpe de volta; contra quem atira com
     frequencia ele vai buscar (bots.GAMBITS_ARENA.torre, desde a escala dos pets v6);
   - Floresta (Champion, nova), Youkomon: LEITURA. O lider muda de padrao no turno 10 (bots.GAMBITS_ARENA.floresta, pela
     condicao de turno da linguagem de gambits): de atirador vira brigao;
   - Cidadela (Ultimate), Myotismon: RESISTENCIA. Tres lutas seguidas, sem cura: a vida e o guts do pet passam de uma para a
     outra (o lider volta inteiro); a vitoria (e a medalha) so vem com as tres;
   - Lago (Ultimate, novo), MarinBullmon: VINCULO. As travas e os vetos do dono nao valem: o pet luta com a lista que ele
     mesmo faria (GambitsPet.listaSozinho);
   - Montanha Espiral (Mega), Piedmon: o chefe da campanha, sem regra a mais.

   Fatores dos lideres: calibrados no motor web com as regras e a escala dos pets v6 (CESC_V6; test/calibrar_arenas.mjs,
   artifacts_campanha/arenas/). Metas (decisao do Matheus, 2026-09-30: o treino tem que decidir): sem treino <= 0,05 e com o
   treino tipico >= 0,80, sem forma travada. PROPOSTOS. O fator fica aqui quando o lider e um NPC que ja existia (Gazimon 1,3,
   Guardromon 1,6, Myotismon 0,9 na serie, Piedmon 1,6; fora da arena e nos pets v1-v5, os de sempre); os lideres novos tem o
   fator no proprio NPC (bots.CAMPANHA_V6: Youkomon 1,5, MarinBullmon 1,5). */
import { comCarta, jogarV2, type Desafiado, type EfeitoCarta, type Lutador, type RegrasLuta, type ResultadoLuta } from "./combate.ts";
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
  /** lista propria do lider na luta de arena (bots.GAMBITS_ARENA); sem ela, a do NPC (com as regras da tecnica) */
  lista?: string;
  /** lutas seguidas, sem cura (Cidadela: 3); sem ele, 1 */
  lutas?: number;
}
/** versao de pet em que as arenas valem (a das medalhas) */
export const VERSAO_ARENAS = 6;
export const ARENAS: readonly Arena[] = [
  { id: "campina", lugar: 0, lider: "npc_tier1_brutamontes", regra: "nenhuma", titulo: "O básico", fator: 1.3,
    frase: "Sem regra especial: vence o pet bem cuidado e treinado." },
  { id: "torre", lugar: 1, lider: "npc_tier2_carcereiro", regra: "paciencia", titulo: "Paciência", tecnica: "contra_golpe", lista: "torre", fator: 1.6,
    frase: "O líder devolve golpe forte: preparar o pesado de perto ou insistir no golpe rápido volta contra você. Quem só atira de longe, ele vai buscar." },
  { id: "floresta", lugar: 2, lider: "npc_v6_youkomon", regra: "leitura", titulo: "Leitura",
    frase: "O líder muda de padrão no turno 10: de longe e disparando, depois colado e golpeando. Vence quem lê o rival." },
  { id: "cidadela", lugar: 3, lider: "npc_v5_myotismon", regra: "resistencia", titulo: "Resistência", lutas: 3, fator: .9,
    frase: "Três lutas seguidas, sem cura: a vida e o guts passam de uma para a outra. A medalha só vem com as três." },
  { id: "lago", lugar: 4, lider: "npc_v6_marinbullmon", regra: "vinculo", titulo: "Vínculo",
    frase: "Aqui as travas e os vetos do dono não valem: o pet decide sozinho, com as regras que ele mesmo aprendeu." },
  { id: "espiral", lugar: 5, lider: "npc_v5_piedmon", regra: "chefe", titulo: "O chefe", fator: 1.6,
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
    pet (lado A) comeca com a vida e o guts do fim da anterior, e o lider (B) volta inteiro. Deterministico. `desafiado`: o do
    limite de turnos (combate.fimV2); nos pets v6 o rival, e uma luta da serie que chega ao limite e derrota e quebra a serie */
export function jogarArena(A: Lutador, B: Lutador, semente: number, R: RegrasLuta, lutas = 1, desafiado: Desafiado = null,
  carta: EfeitoCarta | null = null): ResultadoLuta[] {
  if (!Number.isInteger(lutas) || lutas < 1) throw new Error("lutas da arena inválidas: " + lutas);
  return jogarSerie(A, Array.from({ length: lutas }, () => B), semente, R, desafiado, carta);
}
/** lutas seguidas sem cura, uma contra cada rival de `Bs`, na ordem (a Cidadela: o mesmo lider tres vezes; a Liga dos Lideres,
    liga.ts: os 6 lideres). Para na primeira que nao for vitoria; da segunda em diante o pet (lado A) comeca com a vida e o guts do
    fim da anterior, e cada rival comeca inteiro. A luta k usa a semente sementeDaSerie(semente, k). Deterministico */
export function jogarSerie(A: Lutador, Bs: readonly Lutador[], semente: number, R: RegrasLuta, desafiado: Desafiado = null,
  carta: EfeitoCarta | null = null): ResultadoLuta[] {
  if (!Bs.length) throw new Error("série de lutas sem rival");
  return jogarSequencia(A, k => Bs[k], Bs.length, semente, R, desafiado, carta);
}
/** a mesma conta de jogarSerie, com o rival de cada luta dado na hora (rivalDe(k), so para as lutas que acontecem) e no maximo `max`
    lutas: as instalacoes da Fronteira (instalacoes.ts), em que os rivais sao sorteados e a sequencia vai ate a primeira luta que nao for
    vitoria. jogarSerie e esta funcao com os rivais de uma lista: as lutas sao as mesmas */
export function jogarSequencia(A: Lutador, rivalDe: (k: number) => Lutador, max: number, semente: number, R: RegrasLuta, desafiado: Desafiado = null,
  carta: EfeitoCarta | null = null): ResultadoLuta[] {
  if (!Number.isInteger(max) || max < 1) throw new Error("sequência de lutas sem luta: " + max);
  /* a carta do pet (itens.ts; pets v6) vale para o evento inteiro: o guts a mais no comeco da primeira luta (nas seguintes, o que
     sobrou), o foco em todas e a cura uma vez so na serie */
  const Ac = comCarta(A, carta), serie: ResultadoLuta[] = [];
  let ini: { hp: number; guts: number } | null = null, cura = carta?.cura ?? null;
  for (let k = 0; k < max; k++) {
    const res = jogarV2(Ac, rivalDe(k), sementeDaSerie(semente, k), R, ini, desafiado, cura ? [cura, null] : null);
    serie.push(res);
    if (cura && res.turnos.some(t => t.cura)) cura = null;
    if (res.pontosA !== 1) break;
    ini = { hp: res.E.L[0].hp, guts: res.E.L[0].guts };
  }
  return serie;
}
