/* O decodificador de conceitos `dec-v1` (docs/research/ESPEC_DECODIFICADOR_FALA.md, DC1): o espelho de digilab/digibrain/decodificador.py.
   Do `motivo` de uma decisao do modular aos 12 conceitos nomeados (valor e confianca em [0, S]) e a intencao (regra I-a). Funcao pura em inteiros,
   sem rng, sem DOM; so le. Nao le o `consequencia` do motivo (so aparece na decisao seguinte) nem o `estadoInterno()`. Falha alto em receptor,
   comportamento ou sonda desconhecidos. Conferido bit a bit contra test/gabaritos/decodificador_python.json. */
import { divArred, clamp, mul } from "./_comum.ts";
import { CONFIG_DECODIFICADOR, type ConfigDecodificador } from "./constantes.ts";

type Dict = Record<string, any>;

export const VERSAO_DECODIFICADOR = "dec-v1";
export const CATALOGO_CONCEITOS = ["fome", "sono", "bem_estar", "mal_estar", "agitacao", "aversao", "frustracao", "determinacao", "indecisao",
  "lembranca", "solidao", "curiosidade"] as const;
export type NomeConceito = (typeof CATALOGO_CONCEITOS)[number];
const RECEPTORES = ["fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto"];
const COMPORTAMENTOS = ["ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar"];
const SONDAS_DECIDIU = ["afeto_decidiu", "aprendido_decidiu", "habito_decidiu", "incentivo_decidiu", "lembranca_decidiu", "memoria_decidiu",
  "persistencia_decidiu"];

export interface Conceito { nome: NomeConceito; valor: number; confianca: number; alvo?: string }
/** o formato fixo da espec (secao 2) */
export interface ConceitosDec { versao: string; k: number; intencao: NomeConceito; conceitos: Conceito[] }

function media(pares: [number, number][]): number {
  let soma = 0, tot = 0;
  for (const [p, s] of pares) { soma += p; tot += p * s; }
  return soma === 0 ? 0 : divArred(tot, soma);
}
function fracao(m: Dict, comportamentos: string[], S: number): number {
  const un: Dict[] = m["unidades"];
  const total = un.reduce((s, u) => s + u["w"], 0);
  if (total <= 0) return 0;
  return divArred(un.filter(u => comportamentos.includes(u["chave"][0])).reduce((s, u) => s + u["w"], 0) * S, total);
}
function escolhida(m: Dict): Dict {
  const chave = JSON.stringify(m["escolha"]);
  const esc = (m["unidades"] as Dict[]).filter(u => JSON.stringify(u["chave"]) === chave);
  if (esc.length !== 1) throw new Error("o motivo nao tem a unidade escolhida: " + chave);
  return esc[0]!;
}
function validar(m: Dict): void {
  for (const r of Object.keys(m["afeto"]["urgencias"])) if (!RECEPTORES.includes(r)) throw new Error("receptor desconhecido no motivo: " + r);
  for (const u of m["unidades"] as Dict[]) if (!COMPORTAMENTOS.includes(u["chave"][0])) throw new Error("comportamento desconhecido no motivo: " + u["chave"][0]);
  for (const s of Object.keys(m["sondas"])) if (s.endsWith("_decidiu") && !SONDAS_DECIDIU.includes(s)) throw new Error("sonda desconhecida no motivo: " + s);
  for (const s of SONDAS_DECIDIU) if (!(s in m["sondas"])) throw new Error("o motivo nao tem a sonda " + s);
}

/** os conceitos do `motivo` de uma decisao (a espec, secao 2), os 12 na ordem do catalogo; `S` e a escala do cerebro (`DigiBrain.S`) */
export function decodificar(motivo: Dict, S: number, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR): ConceitosDec {
  const m = motivo;
  validar(m);
  const urg: Dict = m["afeto"]["urgencias"], est: Dict = m["estado"], escolha = m["escolha"] as unknown[], sondas: Dict = m["sondas"];
  const I = est["I"] as unknown[] | null;
  const esc = escolhida(m);
  const total = (m["unidades"] as Dict[]).reduce((s, u) => s + u["w"], 0);
  const escConf = m["reflexo"] ? S : (total <= 0 ? 0 : divArred(esc["w"] * S, total));
  const cs: Partial<Record<NomeConceito, Conceito>> = {};
  const conceito = (nome: NomeConceito, valor: number, confianca: number, alvo?: string): void => {
    const c: Conceito = { nome, valor: clamp(valor, 0, S), confianca: clamp(confianca, 0, S) };
    if (alvo !== undefined) c.alvo = alvo;
    cs[nome] = c;
  };
  const alvoComida = escolha[0] === "comer" && escolha[1] !== null ? (escolha[1] as string) : undefined;
  conceito("fome", media([[cfg.p_fome_urgencia, urg["fome"]], [cfg.p_fome_fracao, fracao(m, ["comer"], S)],
    [cfg.p_fome_intencao, I !== null && I[0] === "comer" ? S : 0], [cfg.p_fome_pista, m["memoria"]["pista"] ? S : 0]]), escConf, alvoComida);
  conceito("sono", media([[cfg.p_sono_urgencia, urg["energia"]], [cfg.p_sono_fracao, fracao(m, ["dormir"], S)],
    [cfg.p_sono_reflexo, m["reflexo"] ? S : 0], [cfg.p_sono_noite, m["contexto"]["noite"] ? S : 0]]), escConf);
  const V = m["afeto"]["V"] as number;
  conceito("bem_estar", cfg.ganho_v * Math.max(0, V), Math.min(S, Math.abs(V)));
  conceito("mal_estar", cfg.ganho_v * Math.max(0, -V), Math.min(S, Math.abs(V)));
  const E = m["afeto"]["E"] as number;
  conceito("agitacao", media([[cfg.p_agitacao_e, E], [cfg.p_agitacao_urgencia, Math.max(urg["dor"], urg["susto"], urg["estresse"])]]), E);
  const lem: Dict = m["lembranca"];
  const ep = lem["recuperado"] === null ? undefined : `ep${lem["recuperado"]}`;
  if (lem["recuperado"] !== null && lem["sigma"] < 0) conceito("aversao", mul(lem["sim"], clamp(cfg.ganho_sigma * -lem["sigma"], 0, S), S), lem["sim"], ep);
  else conceito("aversao", 0, 0);
  const frustrado = (m["fins"] as Dict[]).some(f => (cfg.fins_frustrantes as readonly string[]).includes(f["motivo"]));
  conceito("frustracao", media([[cfg.p_frustracao_f, est["F"]], [cfg.p_frustracao_fim, frustrado ? S : 0],
    [cfg.p_frustracao_n_sp, Math.min(S, divArred(est["n_sp"] * S, cfg.n_sp_teto))]]), est["F"]);
  let det = 0;
  if (I !== null) det = media([[cfg.p_determinacao_c, est["C"]], [cfg.p_determinacao_persistencia, clamp(esc["termos"]["persistencia"], 0, S)]]);
  if (sondas["persistencia_decidiu"]) det = Math.max(det, cfg.piso_sonda);
  conceito("determinacao", det, I !== null ? est["C"] : 0);
  const ws = (m["unidades"] as Dict[]).map(u => u["w"] as number).filter(w => w > 0).sort((a, b) => b - a);
  const margem = m["reflexo"] || ws.length < 2 ? S : divArred((ws[0]! - ws[1]!) * S, ws.reduce((s, w) => s + w, 0));
  const nDec = SONDAS_DECIDIU.filter(s => sondas[s]).length;
  conceito("indecisao", media([[cfg.p_indecisao_margem, S - margem], [cfg.p_indecisao_sondas, divArred(nDec * S, SONDAS_DECIDIU.length)]]), S - margem);
  let valLem = lem["recuperado"] === null ? 0 : (lem["sim"] as number);
  if (sondas["lembranca_decidiu"]) valLem = Math.max(valLem, cfg.piso_sonda);
  conceito("lembranca", valLem, lem["recuperado"] === null ? 0 : lem["sim"], ep);
  conceito("solidao", media([[cfg.p_solidao_urgencia, urg["solidao"]], [cfg.p_solidao_fracao, fracao(m, ["chamar_atencao", "emburrar"], S)]]), urg["solidao"]);
  const gx = m["afeto"]["g_exp"] as number;
  conceito("curiosidade", media([[cfg.p_curiosidade_urgencia, urg["curiosidade"]], [cfg.p_curiosidade_tedio, urg["tedio"]],
    [cfg.p_curiosidade_g_exp, gx], [cfg.p_curiosidade_fracao, fracao(m, ["explorar"], S)]]), gx);
  let intencao: NomeConceito = "lembranca";
  if (!sondas["lembranca_decidiu"]) {
    let melhor: NomeConceito | null = null;
    for (const n of CATALOGO_CONCEITOS) if (n !== "lembranca" && (melhor === null || cs[n]!.valor > cs[melhor]!.valor)) melhor = n;
    intencao = melhor!;
  }
  return { versao: VERSAO_DECODIFICADOR, k: m["k"], intencao, conceitos: CATALOGO_CONCEITOS.map(n => cs[n]!) };
}
