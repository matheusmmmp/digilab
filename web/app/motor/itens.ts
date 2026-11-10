/* Itens do Tamer (docs/DESIGN_MEDALHAS_ARENAS.md, secao 13; medalhas parte 3; so no jogo). TABELA UNICA do catalogo: o que cada item faz
   e de onde vem (o item da medalha de cada arena e a carta da revanche).

   Desde a LP4 da LUTA_POC (docs/TAREFA_V3_LUTA_POC.md, LP-5 e LP2-6) so o chip de stat faz efeito: pontos de treino a mais na luta, dentro dos
   tetos (bonusChipsStat), que entram nos 6 stats do pet (Motor.pontosDeLuta). Os chips de regra e as cartas mudavam as regras e as escolhas
   do combate por turnos, que saiu; eles ficam no catalogo so como itens de antes, sem efeito, porque o registro do Tamer os guarda (o Tamer
   fica inteiro: LP-6). Nenhum pet os equipa ou usa, e o Tamer nao os ganha mais (src/tamer.ts).
   O inventario e do Tamer (src/tamer.ts); no registro do pet entra o evento "i" (equipar/desequipar um chip de stat). O motor do pet nunca
   le o Tamer. Numeros PROPOSTOS (CIT em constantes.ts); o equilibrio e o da LP5.

   Os itens nos pets v9 (rodada de equilibrio geral, fase 3; docs/EQUILIBRIO_GERAL.md, CIT_V9 em constantes.ts), que seguem valendo: com o
   treino do pet abaixo de CIT_V9.treinoMinimo do treino tipico do nivel dele, os chips nao fazem efeito (itensValem), e os pontos do chip de
   stat valem CIT_V9.fatorChipStat dos de antes. */
import { CIT, CIT_V9, CMG, CTR, STATS } from "./constantes.ts";
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
/** um chip de regra do combate por turnos: so no registro do Tamer, sem efeito na luta da POC (LP4) */
export interface ChipRegra extends ItemBase { tipo: "chip_regra" }
/** uma carta do combate por turnos: so no registro do Tamer, sem efeito na luta da POC (LP4) */
export interface Carta extends ItemBase { tipo: "carta" }
export type Item = ChipStat | ChipRegra | Carta;
export type Chip = ChipStat | ChipRegra;

/** o efeito dos itens de antes na tela */
export const SEM_EFEITO_NA_LUTA_NOVA = "Item da luta de antes: sem efeito na luta em tempo real.";
const antigo = (id: string, nome: string, tipo: "chip_regra" | "carta"): Item => ({ id, nome, tipo, efeito: SEM_EFEITO_NA_LUTA_NOVA });
export const ITENS: readonly Item[] = [
  { id: "chip_forca", nome: "Chip de Força", tipo: "chip_stat", pontos: { forca: 1, vigor: 1 },
    efeito: "+1 de força e +1 de vigor, como treino: só ocupa o espaço de treino que ainda falta no estágio." },
  { id: "chip_guarda", nome: "Chip de Guarda", tipo: "chip_stat", pontos: { guarda: 1, recuperacao: 1 },
    efeito: "+1 de guarda e +1 de recuperação, como treino: só ocupa o espaço de treino que ainda falta no estágio." },
  antigo("chip_recuo", "Chip Recuo", "chip_regra"),
  antigo("chip_oportunista", "Chip Oportunista", "chip_regra"),
  antigo("chip_perseguidor", "Chip Perseguidor", "chip_regra"),
  antigo("chip_aparo", "Chip Aparo", "chip_regra"),
  antigo("carta_folego", "Carta de Fôlego", "carta"),
  antigo("carta_cura", "Carta de Cura", "carta"),
  antigo("carta_foco", "Carta de Foco", "carta"),
];
export const ITEM_POR_ID: Readonly<Record<string, Item>> = Object.fromEntries(ITENS.map(x => [x.id, x]));
/** o item que a medalha da (a primeira vitoria contra o lider da arena), pelo id da medalha (medalhas.ts). Desde a LP4 o Tamer so ganha os
    chips de stat (temEfeito); os outros ficam na tabela para conferir os itens que o registro do Tamer ja tem */
export const ITEM_DA_MEDALHA: Readonly<Record<string, string>> = {
  campina: "chip_forca", torre: "chip_recuo", floresta: "chip_oportunista", cidadela: "chip_guarda", lago: "chip_perseguidor", espiral: "chip_aparo",
};
/** a carta que a revanche contra o lider dava; desde a LP4 nenhuma revanche da carta: a tabela so confere as que o registro do Tamer ja tem */
export const CARTA_DA_REVANCHE: Readonly<Record<string, string>> = {
  campina: "carta_folego", torre: "carta_foco", floresta: "carta_folego", cidadela: "carta_cura", lago: "carta_foco", espiral: "carta_cura",
};

export function itemDe(id: string): Item {
  const it = ITEM_POR_ID[id];
  if (!it) throw new Error("item desconhecido: " + JSON.stringify(id));
  return it;
}
/** o item faz efeito na luta de hoje (so o chip de stat) */
export const temEfeito = (it: Item): it is ChipStat => it.tipo === "chip_stat";
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
/** os itens valem como nos pets v9 (CIT_V9) nesta versao de pet? */
export const itensDosV9 = (versao: number): boolean => versao >= CIT_V9.versaoPet;
/** os itens fazem efeito num pet desta versao, neste nivel, com este treino (pontos no total)? Nos pets v9 pedem o treino minimo
    (CIT_V9.treinoMinimo do treino tipico do nivel); nos v6-v8, sempre (o bebe nao tem item) */
export function itensValem(versao: number, est: Estagio, treinoTotal: number): boolean {
  if (!itensDosV9(versao)) return true;
  const tip = CIT.tipico[est];
  return tip !== undefined && treinoTotal >= CIT_V9.treinoMinimo * tip - 1e-9;
}
/** por que os itens nao fazem efeito agora (null: fazem) — a frase da tela */
export function porqueItensNaoValem(versao: number, est: Estagio, treinoTotal: number): string | null {
  if (itensValem(versao, est, treinoTotal)) return null;
  const tip = CIT.tipico[est];
  if (tip === undefined) return "o In-Training não usa itens";
  return `os itens pedem treino: pelo menos ${Math.ceil(CIT_V9.treinoMinimo * tip)} pontos neste nível (o seu pet tem ${Math.floor(treinoTotal)})`;
}

/** chips que o pet pode ter equipados pelas medalhas que conhece (0 sem medalha) */
export const vagasDeChip = (medalhas: number): number => CIT.vagas.find(([m]) => medalhas >= m)?.[1] ?? 0;

/** o chip serve no estagio? So o chip de stat, do Rookie em diante (o bebe nao treina); o chip de regra nao serve em nenhum (LP4) */
export function chipServe(c: Chip, est: Estagio): boolean {
  return est !== "bebe" && c.tipo === "chip_stat";
}

/* ---------------------------------------------------------------- chips de stat: dentro dos tetos */
const tetoEstagio = (est: Estagio): number => est === "mega" ? CMG.tetoEstagio : CTR.tetoEstagio[est as EstagioTreino];
const tetoVida = (est: Estagio): number => est === "mega" ? CMG.tetoVida : CTR.tetoVida;
/** os pontos que os chips de stat somam na luta (null: nenhum). A soma pedida pelos chips (ChipStat.pontos) e cortada, nesta ordem:
    25% do treino tipico do estagio (CIT.tetoChipStat), o espaco que falta no teto do estagio (`pontosEst` = pontos treinados nele) e
    no teto da vida (`pontos` = o treino do pet); depois cada stat fica abaixo do teto dele. Adianta treino: com o estagio no teto, nada.
    Nos pets v9 (`versao`) cada ponto do chip vale CIT_V9.fatorChipStat */
export function bonusChipsStat(ids: readonly string[], est: Estagio, pontos: Readonly<Stats>, pontosEst: number, versao = CIT.versaoPet): Stats | null {
  const chips = ids.map(chipDe).filter((c): c is ChipStat => c.tipo === "chip_stat");
  if (!chips.length || est === "bebe") return null;
  const mult = itensDosV9(versao) ? CIT_V9.fatorChipStat : 1;
  const pedido = Object.fromEntries(STATS.map(k => [k, chips.reduce((s, c) => s + (c.pontos[k] ?? 0) * mult, 0)])) as Stats;
  const soma = STATS.reduce((s, k) => s + pedido[k], 0), total = STATS.reduce((s, k) => s + pontos[k], 0);
  const cabe = Math.max(0, Math.min(soma, CIT.tetoChipStat * CIT.tipico[est]!, tetoEstagio(est) - pontosEst, tetoVida(est) - total));
  const f = soma > 0 ? cabe / soma : 0;
  return Object.fromEntries(STATS.map(k => [k, Math.max(0, Math.min(f * pedido[k], CTR.tetoStat - pontos[k]))])) as Stats;
}
/** o treino com que o pet luta: o do pet mais o dos chips de stat (null: sem treino e sem chip, o perfil de sempre). A trava do treino
    minimo dos pets v9 (itensValem) fica com quem chama (o motor: Motor.pontosDeLuta) */
export function pontosComChips(ids: readonly string[], est: Estagio, pontos: Readonly<Stats>, pontosEst: number, treinou: boolean,
  versao = CIT.versaoPet): Stats | null {
  const b = bonusChipsStat(ids, est, pontos, pontosEst, versao);
  if (!b) return treinou ? { ...pontos } : null;
  return Object.fromEntries(STATS.map((k: Stat) => [k, pontos[k] + b[k]])) as Stats;
}
