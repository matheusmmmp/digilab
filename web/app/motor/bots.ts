/* Os rivais da campanha (espelho de ConfigCampanha / campanha.py): os lugares, os NPCs e os nomes. As listas de gambits dos bots, das formas,
   dos lideres e as candidatas das rodadas de equilibrio eram do combate por turnos e sairam com ele (LUTA_POC, LP4): na luta da POC o rival
   e um Digimon com os numeros do perfil (motor/luta_poc.ts). O `estilo` de cada NPC fica so como dado (o perfilNPC le o estagio). */
import { FORMAS_AD, LINHA_DA_FORMA } from "./constantes.ts";
import { NOME_ARQ } from "./nomes.ts";
import type { Especie, Estagio, Forma, FormaAdultaNormal, TracoCombate } from "./tipos.ts";

/* lugares do mapa; vencer QUALQUER rival de um lugar abre o proximo (a Torre tem 3 rivais para nenhuma
   linha ficar travada; experiments/calibrar_progressao.py) */
export interface Lugar { nome: string; x: number; y: number; sugerido: string; est: Estagio; rivais: string[] }
export const LUGARES: Lugar[] = [
  { nome: "Campina", x: 74, y: 176, sugerido: "Rookie", est: "crianca", rivais: [] },
  { nome: "Torre de pedra", x: 196, y: 118, sugerido: "Champion", est: "adolescente", rivais: [] },
  { nome: "Cidadela", x: 300, y: 58, sugerido: "Ultimate", est: "adulto", rivais: [] },
];
/* todo pet treinado vence cada NPC (decisao do Matheus: NPC fixo e imprevisivel, eps alto) */
export interface DesafioCampanha {
  k: string; nome: string; total: number; estilo: string; estagio?: Estagio; eps: number; lug: number; grade?: string; cor: TracoCombate; licao: string;
  /** so na campanha v5: E = vida do nivel x fator (os de sempre ficam em CESC.fatorNpc) e sprite de outro NPC */
  fator?: number; sprite?: string;
}
export const CAMPANHA: DesafioCampanha[] = [
  { k: "npc_tier1_brutamontes", nome: "Gazimon", total: 96, estilo: "crianca:arisco", estagio: "crianca", eps: .5, lug: 0, grade: "crianca", cor: "golpe",
    licao: "Um valentão do tamanho de um Rookie, forte mas desastrado: às vezes ataca sem pensar. Treinando no Rookie você vence com folga." },
  { k: "npc_tier2_sentinela", nome: "Tortomon", total: 72, estilo: "v2c:tartaruga", eps: .4, lug: 1, cor: "bloqueio",
    licao: "Se fecha na defesa e espera o seu erro. Treinado, seu pet quebra a guarda dele." },
  { k: "npc_tier2_carcereiro", nome: "Guardromon", total: 90, estilo: "v21:espelho", eps: .5, lug: 1, cor: "agarrao",
    licao: "Devolve o que recebe, mas se distrai. Treinado, seu pet aguenta a troca." },
  { k: "npc_tier2_porteiro", nome: "Devidramon", total: 90, estilo: "v2c:agressivo", eps: .5, lug: 1, cor: "golpe",
    licao: "Agressivo e esperto, porém imprevisível. O mais difícil da Torre para um pet sem treino." },
  { k: "npc_tier3_soberano", nome: "Piedmon", total: 110, estilo: "v2c:agressivo", eps: .5, lug: 2, cor: "carga",
    licao: "O chefe: forte em tudo, mas imprevisível. Todo pet bem treinado consegue vencê-lo." },
];
LUGARES.forEach((L, i) => { L.rivais = CAMPANHA.filter(c => c.lug === i).map(c => c.k); });
/* campanha dos pets v5 (evolucao canonica, so no jogo; docs/DESIGN_EVOLUCAO_CANONICA.md, secao 5). No canone o Piedmon
   e Mega (um dos Mestres das Trevas da Montanha Espiral): ele vai para a Montanha Espiral, nova, com o Puppetmon e o
   Machinedramon; a Cidadela fica com o Myotismon (Ultimate, com o estilo e o fator do Piedmon de sempre). Os pets
   v1-v4 seguem em LUGARES/CAMPANHA (Piedmon na Cidadela): o replay deles nao muda. Campina e Torre sao as mesmas
   (mesmas chaves). Fatores da Espiral: PROPOSTOS, calibrados como os de sempre (test/calibrar_mega.mjs,
   artifacts_campanha/mega/): sem treino <= 0,30 e com o treino tipico >= 0,80. */
export const LUGARES_V5: Lugar[] = [
  ...LUGARES.map(L => ({ ...L, rivais: [] as string[] })),
  { nome: "Montanha Espiral", x: 330, y: 20, sugerido: "Mega", est: "mega", rivais: [] },
];
export const CAMPANHA_V5: DesafioCampanha[] = [
  ...CAMPANHA.filter(c => c.lug < 2),
  { k: "npc_v5_myotismon", nome: "Myotismon", total: 110, estilo: "v2c:agressivo", eps: .5, lug: 2, cor: "carga", fator: 1.2,
    licao: "O senhor da Cidadela: forte em tudo, mas imprevisível. Treinado, seu Ultimate vence." },
  { k: "npc_v5_puppetmon", nome: "Puppetmon", total: 90, estilo: "v21:espelho", estagio: "mega", eps: .5, lug: 3, cor: "agarrao", fator: 2.1,
    licao: "Um Mestre das Trevas que brinca com o rival e devolve o que recebe. Só um Mega treinado aguenta a troca." },
  { k: "npc_v5_machinedramon", nome: "Machinedramon", total: 72, estilo: "v2c:tartaruga", estagio: "mega", eps: .4, lug: 3, cor: "bloqueio", fator: 2,
    licao: "Uma fortaleza de metal que espera o seu erro. Um Mega treinado quebra a guarda dele." },
  { k: "npc_v5_piedmon", nome: "Piedmon", total: 110, estilo: "v2c:agressivo", estagio: "mega", eps: .5, lug: 3, cor: "carga", fator: 1.2, sprite: "npc_tier3_soberano",
    licao: "O chefe final, o último Mestre das Trevas: forte em tudo, mas imprevisível. Todo Mega bem treinado consegue vencê-lo." },
];
LUGARES_V5.forEach((L, i) => { L.rivais = CAMPANHA_V5.filter(c => c.lug === i).map(c => c.k); });
/* campanha dos pets v6 (medalhas, parte 2; docs/DESIGN_MEDALHAS_ARENAS.md, secao 3): seis arenas, uma por lugar, cada uma com
   um lider (motor/arenas.ts: a regra da arena e o fator calibrado do lider). A ordem do mapa segue o nivel: Campina (Rookie),
   Torre de pedra (Champion), Floresta (Champion, nova), Cidadela (Ultimate), Lago (Ultimate, novo), Montanha Espiral (Mega).
   Os NPCs de antes seguem como desafiantes, com as mesmas chaves (o replay dos pets v6 ja salvos acha todos); os dois lideres
   novos so existem aqui. Vencer qualquer rival de um lugar abre o proximo, como sempre. Pets v1-v5: campanhas de antes. */
export const LUGARES_V6: Lugar[] = [
  ...LUGARES.slice(0, 2).map(L => ({ ...L, rivais: [] as string[] })),
  { nome: "Floresta", x: 250, y: 140, sugerido: "Champion", est: "adolescente", rivais: [] },
  { ...LUGARES[2], rivais: [] },
  { nome: "Lago", x: 240, y: 60, sugerido: "Ultimate", est: "adulto", rivais: [] },
  { ...LUGARES_V5[3], rivais: [] },
];
const doV5 = (k: string, lug: number): DesafioCampanha => ({ ...CAMPANHA_V5.find(c => c.k === k)!, lug });
export const CAMPANHA_V6: DesafioCampanha[] = [
  ...CAMPANHA.filter(c => c.lug < 2),
  { k: "npc_v6_youkomon", nome: "Youkomon", total: 90, estilo: "arena:floresta", eps: .5, lug: 2, cor: "finta", fator: 1.5,
    licao: "A raposa da Floresta: começa de longe, disparando, e no meio da luta muda de jeito e parte para cima. Regras que leem o rival acompanham a troca." },
  doV5("npc_v5_myotismon", 3),
  { k: "npc_v6_marinbullmon", nome: "MarinBullmon", total: 110, estilo: "v2c:adaptativo", eps: .5, lug: 4, cor: "agarrao", fator: 1.5,
    licao: "O guardião do Lago lê o que o rival repete e responde. Aqui o dono não trava nem veta: o pet luta com o que aprendeu." },
  ...CAMPANHA_V5.filter(c => c.lug === 3).map(c => ({ ...c, lug: 5 })),
];
LUGARES_V6.forEach((L, i) => { L.rivais = CAMPANHA_V6.filter(c => c.lug === i).map(c => c.k); });
/** campanha e lugares da versao do pet */
export const campanhaDe = (versao: number): DesafioCampanha[] => versao >= 6 ? CAMPANHA_V6 : versao >= 5 ? CAMPANHA_V5 : CAMPANHA;
export const lugaresDe = (versao: number): Lugar[] => versao >= 6 ? LUGARES_V6 : versao >= 5 ? LUGARES_V5 : LUGARES;
export type Npc = DesafioCampanha & { tier: number; lugar: string; sugerido: string; est: Estagio };
/* todos os NPCs (das duas campanhas); os que as duas tem sao os mesmos, no mesmo lugar */
const npcDe = (c: DesafioCampanha, Ls: Lugar[]): Npc =>
  ({ ...c, tier: c.lug + 1, lugar: Ls[c.lug].nome, sugerido: Ls[c.lug].sugerido, est: Ls[c.lug].est });
/* o `lug` (e o tier) de um NPC e o da primeira campanha em que ele aparece; o lugar dele na campanha de um pet sai de
   Motor.lugarDe (na v6 o Myotismon e a Espiral mudam de indice). O resto (nome, estilo, estagio do lugar, fator) e o mesmo */
export const NPC: Partial<Record<string, Npc>> = Object.fromEntries([...CAMPANHA.map(c => [c.k, npcDe(c, LUGARES)]),
  ...CAMPANHA_V5.filter(c => !CAMPANHA.includes(c)).map(c => [c.k, npcDe(c, LUGARES_V5)]),
  ...CAMPANHA_V6.filter(c => !CAMPANHA.some(x => x.k === c.k) && !CAMPANHA_V5.some(x => x.k === c.k)).map(c => [c.k, npcDe(c, LUGARES_V6)])]);
export const NOME_BOT: Record<string, string> = {
  aleatorio: "aleatório", agressivo: "agressivo", tartaruga: "tartaruga", atirador: "atirador",
  contragolpe: "contragolpe", adaptativo: "adaptativo", oraculo: "oráculo", ...Object.fromEntries(FORMAS_AD.map(f => [f, NOME_ARQ[f]])),
  ...Object.fromEntries([...CAMPANHA, ...CAMPANHA_V5, ...CAMPANHA_V6].map(c => [c.k, c.nome])),
};
/* rivais V2.1: cada forma adulta com uma especie fixa (para variar os sprites) e o carater canonico */
export const RIVAL_ESPECIE: Record<FormaAdultaNormal, Especie> = { duelista: "brasa", furioso: "ferrugem", espelho: "limo", muralha: "ferrugem", sentinela: "cirro", emboscador: "cirro", vigia: "limo", tita: "brasa" };
export const formaRival = (nome: FormaAdultaNormal): Forma => ({ esp: RIVAL_ESPECIE[nome], est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[nome], adulta: nome });
export const BOT_TRACO: Record<string, TracoCombate> = { aleatorio: "golpe", agressivo: "golpe", tartaruga: "bloqueio", atirador: "finta", contragolpe: "agarrao", adaptativo: "carga", oraculo: "carga" };
