/* Itens do Tamer: chips e cartas (docs/DESIGN_MEDALHAS_ARENAS.md, secao 13; medalhas parte 3; so no jogo e so nos pets v6).
   TABELA UNICA do catalogo: o que cada item faz, de onde vem (o item da medalha de cada arena e a carta da revanche) e os efeitos
   na luta. Principio (secao 6 e docs/DIAGNOSTICO_ARQUETIPOS.md): os stats da forma pesam pouco e a lista de regras decide, entao o
   item complementa a criatura em vez de substitui-la: mais chips de regra (mudam comportamento) que de stat, e o chip de stat preso
   aos tetos do treino (adianta treino, nao passa do teto).

   Tres tipos:
   - chip de stat: pontos de treino a mais na luta, dentro dos tetos (bonusChipsStat);
   - chip de regra: uma regra de catalogo fechado na lista de gambits do pet (GambitsPet.equiparRegra); nunca tecnica, nunca a
     leitura da intencao (passiva do vigia), nunca as regras do vigia V21D; so com as condicoes do estagio;
   - carta: efeito de uma luta so (combate.EfeitoCarta), consumida; uma por luta.
   O inventario e do Tamer (src/tamer.ts); no registro do pet entram os eventos "i" (equipar/desequipar) e "k" (carta da proxima
   luta). O motor do pet nunca le o Tamer. Numeros PROPOSTOS e sem equilibrio (CIT em constantes.ts): o equilibrio dos itens entra na
   rodada de equilibrio geral do combate (decisao do Matheus, 2026-09-30); test/medir_itens.mjs tem os gates da secao 13.7 para ela. */
import { CIT, CMG, CTR, CV21, STATS, TECNICAS, baseDe } from "./constantes.ts";
import { CONDICOES_ESTAGIO, Cd, Rg, validarLista, type EfeitoCarta, type ListaGambits, type Regra } from "./combate.ts";
import { REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE } from "./bots.ts";
import type { Estagio, EstagioTreino, Stat, Stats } from "./tipos.ts";

export type TipoItem = "chip_stat" | "chip_regra" | "carta";
interface ItemBase {
  id: string;
  /** nome na tela */
  nome: string;
  tipo: TipoItem;
  /** o efeito em uma frase, na tela */
  efeito: string;
}
export interface ChipStat extends ItemBase { tipo: "chip_stat"; pontos: Readonly<Partial<Stats>> }
export interface ChipRegra extends ItemBase { tipo: "chip_regra"; regra: Regra; /** a fraqueza medida que ele ataca (tela e docs) */ alvo: string }
export interface Carta extends ItemBase { tipo: "carta"; carta: Readonly<EfeitoCarta> }
export type Item = ChipStat | ChipRegra | Carta;
export type Chip = ChipStat | ChipRegra;

const PREP = Cd("oponente_preparando"), D0 = Cd("distancia_eh", 0), FQ = (a: string) => Cd("oponente_frequente", a);
export const ITENS: readonly Item[] = [
  { id: "chip_forca", nome: "Chip de Força", tipo: "chip_stat", pontos: { forca: 1, vigor: 1 },
    efeito: "+1 de força e +1 de vigor, como treino: só ocupa o espaço de treino que ainda falta no estágio." },
  { id: "chip_guarda", nome: "Chip de Guarda", tipo: "chip_stat", pontos: { guarda: 1, recuperacao: 1 },
    efeito: "+1 de guarda e +1 de recuperação, como treino: só ocupa o espaço de treino que ainda falta no estágio." },
  { id: "chip_recuo", nome: "Chip Recuo", tipo: "chip_regra", regra: Rg(PREP, "recuar"),
    efeito: "Regra nova: quando o rival prepara o golpe pesado, recuar (o pesado erra de longe, sem gastar guts).",
    alvo: "quem responde ao pesado anunciado gastando guts na esquiva ou com a pele" },
  { id: "chip_oportunista", nome: "Chip Oportunista", tipo: "chip_regra", regra: Rg([D0, Cd("oponente_guts_abaixo", 20)], "preparar_pesado"),
    efeito: "Regra nova: de perto, com o rival sem fôlego (guts < 20), preparar o golpe pesado.",
    alvo: "as linhas lentas (guardião e colosso), as que mais perdem dos líderes do nível delas" },
  { id: "chip_perseguidor", nome: "Chip Perseguidor", tipo: "chip_regra", regra: Rg(FQ("disparo"), "avancar"),
    efeito: "Regra nova: contra quem insiste em atirar de longe, avançar.",
    alvo: "colossos e guardiãs contra os caçadores, que atiram de longe e fogem do pesado" },
  { id: "chip_aparo", nome: "Chip Aparo", tipo: "chip_regra", regra: Rg(FQ("golpe_rapido"), "defender"),
    efeito: "Regra nova: contra quem insiste no golpe rápido, defender (o aparo devolve dano).",
    alvo: "caçadores e colossos contra o furioso e os líderes agressivos (o aparo é o único freio medido do furioso)" },
  { id: "carta_folego", nome: "Carta de Fôlego", tipo: "carta", carta: { guts: CIT.gutsFolego },
    efeito: `+${CIT.gutsFolego} de guts no começo da luta (até o máximo).` },
  { id: "carta_cura", nome: "Carta de Cura", tipo: "carta", carta: { cura: { abaixo: CIT.curaAbaixo, fracao: CIT.curaFracao } },
    efeito: `Na primeira vez que a vida cai abaixo de ${CIT.curaAbaixo * 100}%, cura ${CIT.curaFracao * 100}% da vida máxima.` },
  { id: "carta_foco", nome: "Carta de Foco", tipo: "carta", carta: { foco: true },
    efeito: "O pet não se distrai: segue as próprias regras em todos os turnos." },
];
export const ITEM_POR_ID: Readonly<Record<string, Item>> = Object.fromEntries(ITENS.map(x => [x.id, x]));
/** o item que a medalha da (a primeira vitoria contra o lider da arena), pelo id da medalha (medalhas.ts) */
export const ITEM_DA_MEDALHA: Readonly<Record<string, string>> = {
  campina: "chip_forca", torre: "chip_recuo", floresta: "chip_oportunista", cidadela: "chip_guarda", lago: "chip_perseguidor", espiral: "chip_aparo",
};
/** a carta que a revanche contra o lider da (vitoria com a medalha ja ganha, pet do nivel da arena, uma a cada CIT.espera min) */
export const CARTA_DA_REVANCHE: Readonly<Record<string, string>> = {
  campina: "carta_folego", torre: "carta_foco", floresta: "carta_folego", cidadela: "carta_cura", lago: "carta_foco", espiral: "carta_cura",
};

export function itemDe(id: string): Item {
  const it = ITEM_POR_ID[id];
  if (!it) throw new Error("item desconhecido: " + JSON.stringify(id));
  return it;
}
export const ehChip = (it: Item): it is Chip => it.tipo !== "carta";
export function chipDe(id: string): Chip {
  const it = itemDe(id);
  if (!ehChip(it)) throw new Error(`${it.nome} não é chip`);
  return it;
}
export function cartaDe(id: string): Carta {
  const it = itemDe(id);
  if (it.tipo !== "carta") throw new Error(`${it.nome} não é carta`);
  return it;
}
/** chips que o pet pode ter equipados pelas medalhas que conhece (0 sem medalha) */
export const vagasDeChip = (medalhas: number): number => CIT.vagas.find(([m]) => medalhas >= m)?.[1] ?? 0;

const ORDEM: readonly Estagio[] = ["bebe", "crianca", "adolescente", "adulto", "mega"];
/** o chip serve no estagio? chip de stat: do Rookie em diante (o bebe nao treina); chip de regra: todas as condicoes do estagio */
export function chipServe(c: Chip, est: Estagio): boolean {
  if (est === "bebe") return false;
  return c.tipo === "chip_stat" || c.regra.se.every(x => CONDICOES_ESTAGIO[est].includes(x.n));
}
/** o primeiro estagio em que o chip serve (tela: "pede um Champion") */
export const estagioMinimo = (c: Chip): Estagio => ORDEM.find(e => chipServe(c, e))!;

/* o catalogo respeita a secao 13: nenhuma regra de chip usa tecnica, a leitura da intencao ou as regras do vigia V21D, e toda
   regra e valida na linguagem de gambits (falha alto na carga) */
for (const it of ITENS) if (it.tipo === "chip_regra") {
  const r = it.regra, k = JSON.stringify([r.se.map(c => [c.n, c.p]), r.entao]);
  validarLista({ regras: [r], final: "defender" });
  if ((TECNICAS as readonly string[]).includes(r.entao)) throw new Error(`${it.nome}: regra de chip com técnica`);
  if (r.se.some(c => c.n === "oponente_vai_preparar")) throw new Error(`${it.nome}: regra de chip com a leitura da intenção (vigia)`);
  for (const v of [REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE])
    if (JSON.stringify([v.se.map(c => [c.n, c.p]), v.entao]) === k) throw new Error(`${it.nome}: regra que define o vigia V21D`);
}

/* ---------------------------------------------------------------- chips de stat: dentro dos tetos */
const tetoEstagio = (est: Estagio): number => est === "mega" ? CMG.tetoEstagio : CTR.tetoEstagio[est as EstagioTreino];
const tetoVida = (est: Estagio): number => est === "mega" ? CMG.tetoVida : CTR.tetoVida;
/** os pontos que os chips de stat somam na luta (null: nenhum). A soma pedida pelos chips (ChipStat.pontos) e cortada, nesta ordem:
    25% do treino tipico do estagio (CIT.tetoChipStat), o espaco que falta no teto do estagio (`pontosEst` = pontos treinados nele) e
    no teto da vida (`pontos` = o treino do pet); depois cada stat fica abaixo do teto dele. Adianta treino: com o estagio no teto, nada */
export function bonusChipsStat(ids: readonly string[], est: Estagio, pontos: Readonly<Stats>, pontosEst: number): Stats | null {
  const chips = ids.map(chipDe).filter((c): c is ChipStat => c.tipo === "chip_stat");
  if (!chips.length || est === "bebe") return null;
  const pedido = Object.fromEntries(STATS.map(k => [k, chips.reduce((s, c) => s + (c.pontos[k] ?? 0), 0)])) as Stats;
  const soma = STATS.reduce((s, k) => s + pedido[k], 0), total = STATS.reduce((s, k) => s + pontos[k], 0);
  const cabe = Math.max(0, Math.min(soma, CIT.tetoChipStat * CIT.tipico[est]!, tetoEstagio(est) - pontosEst, tetoVida(est) - total));
  const f = soma > 0 ? cabe / soma : 0;
  return Object.fromEntries(STATS.map(k => [k, Math.max(0, Math.min(f * pedido[k], CTR.tetoStat - pontos[k]))])) as Stats;
}
/** o treino com que o pet luta: o do pet mais o dos chips de stat (null: sem treino e sem chip, o perfil de sempre) */
export function pontosComChips(ids: readonly string[], est: Estagio, pontos: Readonly<Stats>, pontosEst: number, treinou: boolean): Stats | null {
  const b = bonusChipsStat(ids, est, pontos, pontosEst);
  if (!b) return treinou ? { ...pontos } : null;
  return Object.fromEntries(STATS.map((k: Stat) => [k, pontos[k] + b[k]])) as Stats;
}

/* ---------------------------------------------------------------- chips de regra: a lista como no pet recem-equipado */
/** capacidade da lista no estagio */
export const capacidadeLista = (est: Estagio): number => CV21.maxRegras[baseDe(est)];
/** a lista com os chips de regra como no pet recem-equipado (GambitsPet.equiparRegra): cada chip, na ordem dos ids, vai para o topo
    (o ultimo equipado fica na frente; se a regra ja estava na lista, ela sobe); passando da capacidade, sai a ultima regra. Para a
    medicao com os bots de referencia (test/medir_itens.mjs) */
export function listaComChips(g: ListaGambits, ids: readonly string[], cap: number): ListaGambits {
  let regras = [...g.regras];
  const chave = (r: Regra) => JSON.stringify([r.se.map(c => [c.n, c.p]), r.entao]);
  for (const id of ids) {
    const c = chipDe(id);
    if (c.tipo !== "chip_regra") continue;
    regras = [c.regra, ...regras.filter(r => chave(r) !== chave(c.regra))].slice(0, cap);
  }
  return { regras, final: g.final };
}
