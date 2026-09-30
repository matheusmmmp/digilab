/* Bots (espelho de combate_v2/bots.py e combate_v2/v21/bots.py), sementes de gambits por estagio e
   campanha contra os NPCs (espelho de ConfigCampanha / campanha.py). */
import { CV, FORMAS_AD, LINHA_DA_FORMA, TECNICAS, type Tecnica } from "./constantes.ts";
import { Cd, Rg, validarLista, type Estilo, type ListaGambits, type RegrasLuta } from "./combate.ts";
import { NOME_ARQ } from "./nomes.ts";
import type { Especie, Estagio, Forma, FormaAdultaNormal, Linha, Ramo, TracoCombate } from "./tipos.ts";

const FQ_ = (a: string) => Cd("oponente_frequente", a);
export const BOTS_V2: Record<string, ListaGambits> = {
  aleatorio: { regras: [], final: "defender" },
  /* V2C: bots redesenhados (bots.GAMBITS_V2C); a V2 original fica so no Python */
  agressivo: { regras: [Rg([Cd("executando_pesado"), FQ_("esquivar")], "fintar"),
    Rg([Cd("hp_proprio_abaixo", .5), FQ_("golpe_rapido")], "defender"), Rg(Cd("distancia_eh", 2), "avancar"), Rg(Cd("distancia_eh", 1), "avancar"),
    Rg(Cd("oponente_preparando"), "golpe_rapido"), Rg([FQ_("defender"), Cd("guts_proprio_acima", 40)], "preparar_pesado"),
    Rg(Cd("guts_proprio_acima", 20), "golpe_rapido")], final: "carregar" },
  tartaruga: { regras: [Rg([Cd("oponente_preparando"), FQ_("fintar")], "defender"), Rg(Cd("oponente_preparando"), "esquivar"),
    Rg([FQ_("preparar_pesado"), Cd("distancia_eh", 0)], "golpe_rapido"), Rg(Cd("oponente_guts_abaixo", 20), "preparar_pesado"),
    Rg([FQ_("defender"), Cd("distancia_eh", 0)], "preparar_pesado"), Rg(FQ_("defender"), "avancar"),
    Rg([FQ_("carregar"), Cd("distancia_eh", 0)], "golpe_rapido"), Rg([Cd("guts_proprio_abaixo", 40), FQ_("defender")], "carregar")], final: "defender" },
  atirador: { regras: [Rg([Cd("oponente_preparando"), Cd("distancia_eh", 0)], "esquivar"), Rg([Cd("distancia_eh", 0), Cd("guts_proprio_acima", 40)], "golpe_rapido"),
    Rg(Cd("distancia_eh", 0), "recuar"), Rg([Cd("hp_proprio_abaixo", .5), FQ_("disparo")], "avancar"),
    Rg([FQ_("disparo"), Cd("guts_proprio_acima", 40)], "esquivar"), Rg(Cd("sempre"), "disparo")], final: "carregar" },
  contragolpe: { regras: [Rg(Cd("oponente_preparando"), "esquivar"), Rg(Cd("oponente_guts_abaixo", 20), "preparar_pesado"),
    Rg(Cd("oponente_guts_abaixo", 20), "golpe_rapido"), Rg([FQ_("defender"), Cd("distancia_eh", 0)], "preparar_pesado"),
    Rg(Cd("distancia_eh", 2), "avancar"), Rg(Cd("guts_proprio_abaixo", 40), "carregar"), Rg(Cd("distancia_eh", 1), "avancar")], final: "defender" },
  adaptativo: { regras: [Rg(Cd("oponente_preparando"), "esquivar"), Rg(Cd("oponente_repete", "defender", 2), "preparar_pesado"),
    Rg(Cd("oponente_frequente", "preparar_pesado"), "golpe_rapido"), Rg(Cd("oponente_frequente", "carregar"), "golpe_rapido"),
    Rg(Cd("oponente_frequente", "disparo"), "avancar"), Rg(Cd("oponente_frequente", "golpe_rapido"), "defender"),
    Rg([Cd("distancia_eh", 0), Cd("guts_proprio_acima", 40)], "golpe_rapido"), Rg(Cd("guts_proprio_acima", 20), "avancar")], final: "carregar" },
};
/* bots canonicos da bateria V2.1: um por forma adulta (8 regras), um adolescente por linha (5) e, so na
   web, uma semente de 3 regras para cada ramo da crianca */
const PREP = Cd("oponente_preparando"), D0 = Cd("distancia_eh", 0), D1 = Cd("distancia_eh", 1), D2 = Cd("distancia_eh", 2);
const GA_ = (g: number) => Cd("guts_proprio_acima", g), GB_ = (g: number) => Cd("guts_proprio_abaixo", g), FQ = (a: string) => Cd("oponente_frequente", a);
export const BOTS_V21: Record<FormaAdultaNormal, ListaGambits> = {
  duelista: { regras: [Rg(PREP, "esquivar"), Rg(D1, "investida"), Rg(D2, "avancar"), Rg([D0, Cd("oponente_repete", "defender", 2)], "preparar_pesado"),
    Rg([D0, FQ("esquivar")], "preparar_pesado"), Rg([D0, GA_(40)], "preparar_pesado"), Rg(D0, "golpe_rapido"), Rg(GB_(20), "carregar")], final: "defender" },
  furioso: { regras: [Rg(PREP, "esquivar"), Rg(D1, "investida"), Rg(D2, "avancar"), Rg([D0, Cd("hp_proprio_abaixo", .5)], "golpe_rapido"),
    Rg([D0, GA_(40)], "preparar_pesado"), Rg(D0, "golpe_rapido"), Rg(D1, "avancar"), Rg(GB_(20), "carregar")], final: "carregar" },
  espelho: { regras: [Rg(PREP, "contra_golpe"), Rg(FQ("disparo"), "contra_golpe"), Rg(FQ("golpe_rapido"), "contra_golpe"), Rg(FQ("investida"), "contra_golpe"),
    Rg([D0, Cd("oponente_repete", "defender", 2)], "preparar_pesado"), Rg([D0, GA_(60)], "golpe_rapido"), Rg(GB_(40), "carregar"), Rg(D2, "avancar")], final: "defender" },
  muralha: { regras: [Rg(PREP, "contra_golpe"), Rg(FQ("golpe_rapido"), "contra_golpe"), Rg([D1, FQ("investida")], "defender"),
    Rg([D0, Cd("oponente_repete", "defender", 2)], "preparar_pesado"), Rg([D0, Cd("oponente_guts_abaixo", 20)], "preparar_pesado"),
    Rg(FQ("disparo"), "avancar"), Rg([D1, GA_(60)], "disparo"), Rg(D2, "avancar")], final: "defender" },
  sentinela: { regras: [Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(Cd("oponente_repete", "avancar", 2), "recuar"), Rg(FQ("investida"), "recuar"),
    Rg(GA_(40), "marcar"), Rg(GA_(20), "disparo"), Rg(D1, "recuar"), Rg(GB_(20), "carregar")], final: "carregar" },
  emboscador: { regras: [Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(Cd("turno_execucao", 5), "marcar"), Rg(Cd("turno_execucao", 5), "disparo"),
    Rg([D1, FQ("avancar")], "recuar"), Rg(D1, "recuar"), Rg(GB_(60), "carregar"), Rg(GA_(60), "marcar")], final: "carregar" },
  vigia: { regras: [Rg([Cd("oponente_vai_preparar"), D0], "golpe_rapido"), Rg(PREP, "esquivar"), Rg([D0, GA_(40)], "pele_dura"),
    Rg([D0, FQ("esquivar")], "golpe_rapido"), Rg([D0, GA_(20)], "preparar_pesado"), Rg(D1, "avancar"), Rg(D2, "avancar"), Rg(GB_(20), "carregar")], final: "defender" },
  tita: { regras: [Rg(PREP, "pele_dura"), Rg(PREP, "esquivar"), Rg([D0, GA_(40)], "pele_dura"), Rg([D0, FQ("esquivar")], "golpe_rapido"),
    Rg([D0, GA_(20)], "preparar_pesado"), Rg(D1, "avancar"), Rg(D2, "avancar"), Rg(GB_(20), "carregar")], final: "defender" },
};
/* V21D (pets v6; espelho de bots.GAMBITS_MURALHA_V21D e bots.GAMBITS_VIGIA_V21D[(True, True)], chaves muralha_lista_espelho,
   vigia_bate_em_quem_recua e vigia_recua_do_preparo_sob_pele). BOTS_V21 (as listas canonicas) nao muda:
   - muralha: a lista do espelho (as regras de contra-golpe fora de perto nunca disparam na muralha);
   - vigia, E2: "de perto, contra quem recua com frequencia, golpe rapido" logo antes do preparar; sai "oponente preparando
     -> esquivar"; V: "o oponente vai preparar e usa pele com frequencia -> recuar" no topo; sai "guts < 20 -> carregar" */
export const REGRA_BATE_EM_QUEM_RECUA = Rg([D0, FQ("recuar")], "golpe_rapido");
export const REGRA_RECUA_DO_PREPARO_SOB_PELE = Rg([Cd("oponente_vai_preparar"), FQ("pele_dura")], "recuar");
const chaveRg = (r: { se: { n: string; p: unknown[] }[]; entao: string }): string => JSON.stringify([r.se.map(c => [c.n, c.p]), r.entao]);
function vigiaV21D(): ListaGambits {
  const regras = [...BOTS_V21.vigia.regras], pos = (r: typeof regras[number]) => {
    const i = regras.findIndex(x => chaveRg(x) === chaveRg(r));
    if (i < 0) throw new Error("regra do vigia canonico nao encontrada: " + chaveRg(r));
    return i;
  };
  regras.splice(pos(Rg(PREP, "esquivar")), 1);
  regras.splice(pos(Rg([D0, GA_(20)], "preparar_pesado")), 0, REGRA_BATE_EM_QUEM_RECUA);
  regras.splice(pos(Rg(GB_(20), "carregar")), 1);
  regras.unshift(REGRA_RECUA_DO_PREPARO_SOB_PELE);
  return { regras, final: BOTS_V21.vigia.final };
}
export const BOTS_V21D: Partial<Record<FormaAdultaNormal, ListaGambits>> = {
  muralha: { regras: BOTS_V21.espelho.regras, final: BOTS_V21.espelho.final },
  vigia: vigiaV21D(),
};
/** lista canonica da forma adulta sob as regras da luta: nas lutas V21D (pets v6), a muralha e o vigia usam a variante */
export const gambitsAdulto = (forma: FormaAdultaNormal, R: RegrasLuta): ListaGambits =>
  (R && ((forma === "muralha" && R.muralhaListaEspelho) || (forma === "vigia" && R.vigiaBateEmQuemRecua && R.vigiaRecuaDoPreparoSobPele))
    ? BOTS_V21D[forma] : undefined) ?? BOTS_V21[forma];
export const ADOL_V21: Record<Linha, ListaGambits> = {
  brigao: { regras: [Rg(PREP, "esquivar"), Rg(D1, "investida"), Rg(D2, "avancar"), Rg([D0, GA_(40)], "preparar_pesado"), Rg(D0, "golpe_rapido")], final: "defender" },
  guardiao: { regras: [Rg(PREP, "contra_golpe"), Rg([D0, Cd("oponente_guts_abaixo", 20)], "preparar_pesado"), Rg([D0, GA_(60)], "golpe_rapido"),
    Rg(GB_(40), "carregar"), Rg(D2, "avancar")], final: "defender" },
  cacador: { regras: [Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(GA_(40), "marcar"), Rg(GA_(20), "disparo"), Rg(D1, "recuar")], final: "carregar" },
  colosso: { regras: [Rg(PREP, "esquivar"), Rg([D0, GA_(40)], "pele_dura"), Rg([D0, GA_(20)], "preparar_pesado"), Rg(D1, "avancar"), Rg(D2, "avancar")], final: "defender" },
};
export const CRIANCA_V21: Record<Ramo, ListaGambits> = {
  sereno: { regras: [Rg(GB_(40), "carregar"), Rg(D2, "avancar"), Rg([D0, GA_(40)], "golpe_rapido")], final: "defender" },
  arisco: { regras: [Rg(D2, "avancar"), Rg(D1, "avancar"), Rg([D0, GA_(20)], "golpe_rapido")], final: "carregar" },
};
[...Object.values(BOTS_V2), ...Object.values(BOTS_V21), ...Object.values(BOTS_V21D) as ListaGambits[], ...Object.values(ADOL_V21), ...Object.values(CRIANCA_V21)].forEach(validarLista);
/* sombrias redesenhadas para o S2 (bots.SOMBRIOS): a sombra tira a leitura do oponente */
export const GAMBITS_SOMBRIA: Record<string, ListaGambits> = {
  devastador: { regras: [Rg(D2, "avancar"), Rg(D1, "avancar"), Rg([D0, GA_(60)], "preparar_pesado"), Rg(D0, "golpe_rapido")], final: "carregar" },
  predador: { regras: [Rg(D2, "avancar"), Rg(D1, "avancar"), Rg(D0, "golpe_rapido")], final: "carregar" },
  get bastiao_rachado(): ListaGambits { return { regras: BOTS_V21.espelho.regras.filter(r => !r.se.some(c => c.n.startsWith("oponente_"))), final: BOTS_V21.espelho.final }; },
};

/* lideres das arenas (pets v6, docs/DESIGN_MEDALHAS_ARENAS.md secao 3; motor/arenas.ts): listas proprias, familia "arena".
   Floresta (leitura): o lider MUDA DE PADRAO no meio da luta, pela condicao de turno que a linguagem ja tem (turno_execucao).
   Ate o turno 10 ele e um atirador (foge de perto e dispara); do turno 10 em diante, um brigao (encurta e golpeia rapido).
   Quem tem regras condicionais (o que o oponente faz, a distancia) acompanha a troca. Sem tecnica e sem passiva, como os NPCs.
   A lista saiu de 30 variantes medidas so nas sementes de calibracao (test/explorar_floresta.mjs,
   artifacts_campanha/arenas/floresta_variantes.json): a primeira, com o pesado na fase 2, nao fechava as metas. */
const T10 = Cd("turno_execucao", 10);
/* Torre de pedra (paciencia), escala dos pets v6: a lista do espelho com o contra-golpe (contra quem prepara o pesado, insiste no
   golpe rapido ou na investida), mas contra quem atira com frequencia ele vai buscar (a resposta da muralha canonica) no lugar
   do contra-golpe, que nao devolve disparo sem a passiva do espelho: com a lista de antes o cacador sem treino vencia o lider
   atirando de longe com qualquer fator (test/explorar_torre.mjs, artifacts_campanha/arenas/torre_variantes.json, so nas
   sementes de calibracao) */
const CG_ = "contra_golpe";
export const GAMBITS_ARENA: Record<string, ListaGambits> = {
  floresta: { regras: [Rg([T10, D2], "avancar"), Rg([T10, D1], "avancar"), Rg([T10, GA_(20)], "golpe_rapido"),
    Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(GA_(20), "disparo")], final: "carregar" },
  torre: { regras: [Rg(PREP, CG_), Rg(FQ("disparo"), "avancar"), Rg(FQ("golpe_rapido"), CG_), Rg(FQ("investida"), CG_),
    Rg([D0, Cd("oponente_repete", "defender", 2)], "preparar_pesado"), Rg([D0, GA_(60)], "golpe_rapido"), Rg(GB_(40), "carregar"), Rg(D2, "avancar")],
    final: "defender" },
};
Object.values(GAMBITS_ARENA).forEach(validarLista);

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
/** v21: gambits canonicos da forma sem as regras de tecnica e da passiva do vigia (o NPC nao tem); nas lutas V21D (pets
    v6) a lista da forma e a variante (gambitsAdulto); v2c: bots redesenhados da V2C (os BOTS_V2 da web); arena: as listas
    proprias dos lideres (GAMBITS_ARENA). `tecnica`: o lider de arena que tem tecnica (Torre de pedra: contra-golpe) fica com
    as regras dela */
export function gambitNPC(estilo: string, R: RegrasLuta = null, tecnica: Tecnica | null = null): ListaGambits {
  const [fam, nome] = estilo.split(":");
  if (fam === "v21") {
    const g = gambitsAdulto(nome as FormaAdultaNormal, R);
    return { regras: g.regras.filter(r => (r.entao === tecnica || !(TECNICAS as readonly string[]).includes(r.entao)) && !r.se.some(c => c.n === "oponente_vai_preparar")), final: g.final };
  }
  if (fam === "v2c") return BOTS_V2[nome];
  if (fam === "crianca") return CRIANCA_V21[nome as Ramo];
  if (fam === "arena") { if (!GAMBITS_ARENA[nome]) throw new Error("lista de arena desconhecida: " + estilo); return GAMBITS_ARENA[nome]; }
  throw new Error("familia de estilo desconhecida: " + estilo);
}
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
const NOME_LISTA_ARENA: Record<string, string> = { floresta: "atirador que vira brigão no turno 10", torre: "espelho com contra-golpe que vai buscar quem atira" };
export const nomeEstiloNPC = (e: string): string => {
  const [fam, nome] = e.split(":");
  return fam === "v21" ? `${NOME_ARQ[nome].toLowerCase()} sem técnica` : fam === "crianca" ? `Rookie ${nome}` : fam === "arena" ? NOME_LISTA_ARENA[nome] : NOME_BOT[nome];
};
/* rivais V2.1: cada forma adulta com uma especie fixa (para variar os sprites) e o carater canonico */
export const RIVAL_ESPECIE: Record<FormaAdultaNormal, Especie> = { duelista: "brasa", furioso: "ferrugem", espelho: "limo", muralha: "ferrugem", sentinela: "cirro", emboscador: "cirro", vigia: "limo", tita: "brasa" };
export const formaRival = (nome: FormaAdultaNormal): Forma => ({ esp: RIVAL_ESPECIE[nome], est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[nome], adulta: nome });
export const BOT_TRACO: Record<string, TracoCombate> = { aleatorio: "golpe", agressivo: "golpe", tartaruga: "bloqueio", atirador: "finta", contragolpe: "agarrao", adaptativo: "carga", oraculo: "carga" };
export const copiarGambits = (g: ListaGambits): ListaGambits => JSON.parse(JSON.stringify(g));
/** estilo do bot sob as regras da luta (R = CV21D nas lutas de pets v6: a muralha e o vigia com as listas variantes) */
export const estiloBot = (nome: string, R: RegrasLuta = null): Estilo => nome === "oraculo" ? { nome, oraculo: true, eps: CV.eps }
  : NPC[nome] ? { nome, gambits: copiarGambits(gambitNPC(NPC[nome]!.estilo, R)), eps: NPC[nome]!.eps ?? CV.eps }
  : { nome, gambits: copiarGambits(BOTS_V2[nome] || gambitsAdulto(nome as FormaAdultaNormal, R)), eps: nome === "aleatorio" ? 1 : CV.eps };
