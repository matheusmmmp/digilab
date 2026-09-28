/* Bots (espelho de combate_v2/bots.py e combate_v2/v21/bots.py), sementes de gambits por estagio e
   campanha contra os NPCs (espelho de ConfigCampanha / campanha.py). */
import { CV, FORMAS_AD, LINHA_DA_FORMA, TECNICAS } from "./constantes.ts";
import { Cd, Rg, validarLista, type Estilo, type ListaGambits } from "./combate.ts";
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
[...Object.values(BOTS_V2), ...Object.values(BOTS_V21), ...Object.values(ADOL_V21), ...Object.values(CRIANCA_V21)].forEach(validarLista);
/* sombrias redesenhadas para o S2 (bots.SOMBRIOS): a sombra tira a leitura do oponente */
export const GAMBITS_SOMBRIA: Record<string, ListaGambits> = {
  devastador: { regras: [Rg(D2, "avancar"), Rg(D1, "avancar"), Rg([D0, GA_(60)], "preparar_pesado"), Rg(D0, "golpe_rapido")], final: "carregar" },
  predador: { regras: [Rg(D2, "avancar"), Rg(D1, "avancar"), Rg(D0, "golpe_rapido")], final: "carregar" },
  get bastiao_rachado(): ListaGambits { return { regras: BOTS_V21.espelho.regras.filter(r => !r.se.some(c => c.n.startsWith("oponente_"))), final: BOTS_V21.espelho.final }; },
};

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
/** v21: gambits canonicos da forma sem as regras de tecnica e da passiva do vigia (o NPC nao tem);
    v2c: bots redesenhados da V2C (os BOTS_V2 da web) */
export function gambitNPC(estilo: string): ListaGambits {
  const [fam, nome] = estilo.split(":");
  if (fam === "v21") {
    const g = BOTS_V21[nome as FormaAdultaNormal];
    return { regras: g.regras.filter(r => !(TECNICAS as readonly string[]).includes(r.entao) && !r.se.some(c => c.n === "oponente_vai_preparar")), final: g.final };
  }
  if (fam === "v2c") return BOTS_V2[nome];
  if (fam === "crianca") return CRIANCA_V21[nome as Ramo];
  throw new Error("familia de estilo desconhecida: " + estilo);
}
export type Npc = DesafioCampanha & { tier: number; lugar: string; sugerido: string; est: Estagio };
export const NPC: Partial<Record<string, Npc>> = Object.fromEntries(CAMPANHA.map(c => [c.k, { ...c, tier: c.lug + 1, lugar: LUGARES[c.lug].nome, sugerido: LUGARES[c.lug].sugerido, est: LUGARES[c.lug].est }]));
export const NOME_BOT: Record<string, string> = {
  aleatorio: "aleatório", agressivo: "agressivo", tartaruga: "tartaruga", atirador: "atirador",
  contragolpe: "contragolpe", adaptativo: "adaptativo", oraculo: "oráculo", ...Object.fromEntries(FORMAS_AD.map(f => [f, NOME_ARQ[f]])),
  ...Object.fromEntries(CAMPANHA.map(c => [c.k, c.nome])),
};
export const nomeEstiloNPC = (e: string): string => { const [fam, nome] = e.split(":"); return fam === "v21" ? `${NOME_ARQ[nome].toLowerCase()} sem técnica` : fam === "crianca" ? `Rookie ${nome}` : NOME_BOT[nome]; };
/* rivais V2.1: cada forma adulta com uma especie fixa (para variar os sprites) e o carater canonico */
export const RIVAL_ESPECIE: Record<FormaAdultaNormal, Especie> = { duelista: "brasa", furioso: "ferrugem", espelho: "limo", muralha: "ferrugem", sentinela: "cirro", emboscador: "cirro", vigia: "limo", tita: "brasa" };
export const formaRival = (nome: FormaAdultaNormal): Forma => ({ esp: RIVAL_ESPECIE[nome], est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[nome], adulta: nome });
export const BOT_TRACO: Record<string, TracoCombate> = { aleatorio: "golpe", agressivo: "golpe", tartaruga: "bloqueio", atirador: "finta", contragolpe: "agarrao", adaptativo: "carga", oraculo: "carga" };
export const copiarGambits = (g: ListaGambits): ListaGambits => JSON.parse(JSON.stringify(g));
export const estiloBot = (nome: string): Estilo => nome === "oraculo" ? { nome, oraculo: true, eps: CV.eps }
  : NPC[nome] ? { nome, gambits: copiarGambits(gambitNPC(NPC[nome]!.estilo)), eps: NPC[nome]!.eps ?? CV.eps }
  : { nome, gambits: copiarGambits(BOTS_V2[nome] || BOTS_V21[nome as FormaAdultaNormal]), eps: nome === "aleatorio" ? 1 : CV.eps };
