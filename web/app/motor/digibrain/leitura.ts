/* A leitura do painel do DigiBrain modular (docs/TAREFA_V3_LAB_MODULAR.md, LM5b; pranchas em docs/pranchas/lab/): o ultimo motivo do M-ADAPT
   (`motivos[k]`, de `adapt.py`) virado nos numeros que a tela mostra. A tela so escolhe o texto e formata; toda conta mora aqui, em inteiros
   (as partes e as chances em permil, ate a ultima casa o mesmo para o mesmo registro). So le: nao muda nenhum modulo nem a rng. */
import { divArred, type ChaveUnidade } from "./_comum.ts";
import type { DigiBrain } from "./adapt.ts";

type Dict = Record<string, any>;

/** os termos do motivo na ordem da prancha; `prox` e `nov` juntas em "objeto" (LM5-2). A faceta nao existe no laboratorio (LAB-1) */
export type TermoLab = "memoria" | "inato" | "lembranca" | "objeto" | "incentivo" | "persistencia" | "habito";
export const ORDEM_TERMOS: readonly TermoLab[] = ["memoria", "inato", "lembranca", "objeto", "incentivo", "persistencia", "habito"];

/** a parte de um termo na unidade escolhida: `permil` = termo / soma dos modulos dos termos, em milesimos, com o sinal (negativa = o modulo
    puxou contra); fica sempre entre -1000 e 1000 */
export interface BarraLab { termo: TermoLab; valor: number; permil: number }
export interface ChanceLab { chave: ChaveUnidade; acao: string; permil: number | null; escolhida: boolean }
/** uma sonda de "o que mudaria a escolha": a unidade que o motivo daria sem aquele termo e se a escolha mudaria */
export interface SondaLab { nome: string; chave: ChaveUnidade | null; mudaria: boolean }
/** o resultado da decisao anterior (CADEIA, etapa 3, PR-C da auditoria; o `consequencia` que o M-ADAPT grava no motivo dela ao fechar):
    o que ele escolheu, se comeu (o tipo e a situacao), se chegou ao alvo, o efeito no corpo (o sinal do r normalizado), o que ficou na memoria
    (o episodio de consumo ou o da visita vazia) e se o habito recebeu credito. So le o motivo */
export interface ResultadoLab {
  k: number; escolha: ChaveUnidade;
  comeu: { tipo: string; situacao: string } | null; chegou: boolean | null;
  efeito: "melhorou" | "piorou" | "igual";
  memoria: "consumo" | "visita" | null;
  aprendeu: boolean;
}
export interface LeituraLab {
  /** o numero da decisao (`motivo.k`) */
  k: number;
  acao: string;
  /** a chave da unidade escolhida: [acao, tipo, id] */
  escolha: ChaveUnidade;
  tipo_escolha: string | null;
  /** o reflexo do sono: nao ha sorteio e nenhuma sonda decide */
  reflexo: boolean;
  nada_a_fazer: boolean;
  /** o alvo entregue ao motor (so nas acoes com alvo) */
  alvo: { tipo: string; x: number; y: number; do_mem: boolean } | null;
  /** as barras nao nulas, da maior parte (em modulo) para a menor, e os termos que nao contribuem agora */
  barras: BarraLab[];
  zeradas: TermoLab[];
  /** a lembranca da vez (`motivo.lembranca`): `sim_permil` e a semelhanca; null sem episodio lembrado */
  lembranca: { recuperado: number; memoria: string; sim_permil: number; sigma: number; L: number } | null;
  /** o que a unidade seria sem o lugar lembrado (`sondas.sem_memoria`), so quando a escolha e o lugar lembrado e ele decidiu (a sonda tira tambem a lembranca) */
  sem_lugar: ChaveUnidade | null;
  /** a intencao em curso quando a decisao comecou (`motivo.estado`); `inicio` e a decisao em que ela comecou, lida do estado do M-ESTADO,
      e `C` e `F` ficam em permil da escala S */
  intencao: { chave: ChaveUnidade; C_permil: number; F_permil: number; n_sp: number; inicio: number | null } | null;
  /** as opcoes com chance maior que zero (so a escolhida no reflexo ou sem sorteio) */
  chances: ChanceLab[];
  sondas: SondaLab[];
}

/** os termos de um grupo na unidade: prox e nov somam em "objeto" */
function valorTermo(termos: Dict, t: TermoLab): number {
  if (t === "objeto") return (termos["prox"] ?? 0) + (termos["nov"] ?? 0);
  return termos[t] ?? 0;
}
const mesmaChave = (a: ChaveUnidade | null, b: ChaveUnidade | null): boolean => JSON.stringify(a) === JSON.stringify(b);

/** a leitura do ultimo motivo do DigiBrain modular; null antes da primeira decisao */
/** o resultado da decisao anterior a ultima (a ultima ainda nao fechou); null sem ela ou antes de ela fechar */
export function resultadoAnterior(lab: DigiBrain): ResultadoLab | null {
  const n = lab.motivos.length;
  if (n < 2) return null;
  const m: Dict = lab.motivos[n - 2]!, c: Dict | null = m["consequencia"] ?? null;
  if (c === null) return null;
  for (const k of ["r_n", "chegou", "comeu", "episodio", "creditos", "p1"]) if (!(k in c)) throw new Error(`o consequencia do motivo ${m["k"]} sem ${k}`);
  const comeu: Dict | null = c["comeu"];
  return {
    k: m["k"], escolha: m["escolha"] as ChaveUnidade,
    comeu: comeu === null ? null : { tipo: comeu["tipo"], situacao: comeu["situacao"] },
    chegou: c["chegou"],
    efeito: c["r_n"] > 0 ? "melhorou" : c["r_n"] < 0 ? "piorou" : "igual",
    memoria: c["episodio"] === null ? null : comeu !== null ? "consumo" : "visita",
    aprendeu: (c["creditos"] as unknown[]).length > 0 || c["p1"] !== null,
  };
}

export function leituraLab(lab: DigiBrain): LeituraLab | null {
  const m: Dict | null = lab.ultimoMotivo;
  if (m === null) return null;
  const S = lab.S, un: Dict[] = m["unidades"], escolha = m["escolha"] as ChaveUnidade;
  const esc = un.find(x => mesmaChave(x["chave"], escolha));
  if (esc === undefined) throw new Error("o motivo nao tem a unidade escolhida: " + JSON.stringify(escolha));
  const termos: Dict = esc["termos"];
  /* o divisor e a soma dos modulos dos termos (nao a soma com sinal): com termos de sinais mistos a soma e pequena e a parte passaria de 100 % */
  let soma = 0;
  for (const v of Object.values<number>(termos)) soma += Math.abs(v);
  const barras: BarraLab[] = [], zeradas: TermoLab[] = [];
  for (const t of ORDEM_TERMOS) {
    const v = valorTermo(termos, t);
    if (v === 0 || soma === 0) zeradas.push(t);
    else barras.push({ termo: t, valor: v, permil: divArred(v * 1000, soma) });
  }
  barras.sort((a, b) => Math.abs(b.permil) - Math.abs(a.permil));
  const lem: Dict | null = m["lembranca"] ?? null;
  const lembranca = lem === null || lem["recuperado"] === null ? null
    : { recuperado: lem["recuperado"] as number, memoria: lem["memoria"] as string, sim_permil: divArred(lem["sim"] * 1000, S), sigma: lem["sigma"] as number, L: lem["L"] as number };
  const sondas: Dict = m["sondas"], decidiu = lab.arb.decidiu;
  const alvo: Dict | null = m["alvo"] ?? null;
  const e: Dict = m["estado"], interno = (lab.estado.estadoInterno() as Dict)["I"] as Dict | null;
  let intencao: LeituraLab["intencao"] = null;
  if (e["I"] !== null) {
    intencao = {
      chave: e["I"], C_permil: divArred(e["C"] * 1000, S), F_permil: divArred(e["F"] * 1000, S), n_sp: e["n_sp"],
      inicio: interno !== null && mesmaChave(interno["chave"], e["I"]) ? interno["inicio"] : null,
    };
  }
  const total = un.reduce((s, x) => s + x["w"], 0), unica = m["reflexo"] || un.filter(x => x["w"] > 0).length < 2;
  const chances: ChanceLab[] = un.filter(x => mesmaChave(x["chave"], escolha) || (!unica && x["w"] > 0))
    .map(x => ({ chave: x["chave"], acao: (x["chave"] as ChaveUnidade)[0], permil: unica || total <= 0 ? null : divArred(x["w"] * 1000, total), escolhida: mesmaChave(x["chave"], escolha) }))
    .sort((a, b) => Number(b.escolhida) - Number(a.escolhida) || (b.permil ?? 0) - (a.permil ?? 0));
  return {
    k: m["k"], acao: m["acao"], escolha, tipo_escolha: m["tipo_escolha"], reflexo: m["reflexo"], nada_a_fazer: m["nada_a_fazer"],
    alvo: alvo === null ? null : { tipo: alvo["tipo"], x: alvo["x"], y: alvo["y"], do_mem: alvo["do_mem"] },
    barras, zeradas, lembranca,
    sem_lugar: alvo !== null && alvo["do_mem"] === true && sondas["memoria_decidiu"] === true ? sondas["sem_memoria"] : null,
    intencao, chances,
    sondas: Object.keys(sondas).filter(n => n in decidiu).map(n => ({ nome: n, chave: sondas[n] ?? null, mudaria: sondas[decidiu[n]!] === true })),
  };
}
