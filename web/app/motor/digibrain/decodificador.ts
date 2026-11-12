/* O decodificador de conceitos `dec-v1` (docs/research/ESPEC_DECODIFICADOR_FALA.md, DC1): o espelho de digilab/digibrain/decodificador.py.
   Do `motivo` de uma decisao do modular aos 12 conceitos nomeados (valor e confianca em [0, S]) e a intencao (regra I-a). Funcao pura em inteiros,
   sem rng, sem DOM; so le. Nao le o `consequencia` do motivo (so aparece na decisao seguinte) nem o `estadoInterno()`. Falha alto em receptor,
   comportamento ou sonda desconhecidos. Conferido bit a bit contra test/gabaritos/decodificador_python.json. */
import { divArred, clamp, mul } from "./_comum.ts";
import { CONFIG_DECODIFICADOR, CONFIG_FALA_ASSISTIR, type ConfigDecodificador, type ConfigFalaAssistir } from "./constantes.ts";

type Dict = Record<string, any>;

export const VERSAO_DECODIFICADOR = "dec-v1";
export const VERSAO_DECODIFICADOR_V2 = "dec-v2";
/** dec-v2 (DC2b): o episodio lembrado, de catalogo fechado (o espelho de CLASSES_EPISODIO e DESFECHOS do decodificador.py) */
export const CLASSES_EPISODIO_DEC = ["racao", "a", "b", "c", "podre", "nao_havia", "bola", "sem_alvo"] as const;
export const DESFECHOS = ["bom", "ruim", "neutro"] as const;
export const CATALOGO_CONCEITOS = ["fome", "sono", "bem_estar", "mal_estar", "agitacao", "aversao", "frustracao", "determinacao", "indecisao",
  "lembranca", "solidao", "curiosidade"] as const;
export type NomeConceito = (typeof CATALOGO_CONCEITOS)[number];
const RECEPTORES = ["fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto"];
const COMPORTAMENTOS = ["ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar"];
const SONDAS_DECIDIU = ["afeto_decidiu", "aprendido_decidiu", "habito_decidiu", "incentivo_decidiu", "lembranca_decidiu", "memoria_decidiu",
  "persistencia_decidiu"];

export interface EpisodioDec { acao: string; classe: (typeof CLASSES_EPISODIO_DEC)[number]; desfecho: (typeof DESFECHOS)[number] }
export interface Conceito { nome: NomeConceito; valor: number; confianca: number; alvo?: string; episodio?: EpisodioDec }
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
function validar(m: Dict, comportamentos: readonly string[] = COMPORTAMENTOS): void {
  for (const r of Object.keys(m["afeto"]["urgencias"])) if (!RECEPTORES.includes(r)) throw new Error("receptor desconhecido no motivo: " + r);
  for (const u of m["unidades"] as Dict[]) if (!comportamentos.includes(u["chave"][0])) throw new Error("comportamento desconhecido no motivo: " + u["chave"][0]);
  for (const s of Object.keys(m["sondas"])) if (s.endsWith("_decidiu") && !SONDAS_DECIDIU.includes(s)) throw new Error("sonda desconhecida no motivo: " + s);
  for (const s of SONDAS_DECIDIU) if (!(s in m["sondas"])) throw new Error("o motivo nao tem a sonda " + s);
}

/** os conceitos do `motivo` de uma decisao (a espec, secao 2), os 12 na ordem do catalogo; `S` e a escala do cerebro (`DigiBrain.S`) */
export function decodificar(motivo: Dict, S: number, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR): ConceitosDec {
  return decodificarCom(motivo, S, cfg, COMPORTAMENTOS);
}
/** o dec-v1 sobre o catalogo de comportamentos dado (o do dec-v1, ou o do dec-v4 com o `olhar`); as contas nao mudam */
function decodificarCom(motivo: Dict, S: number, cfg: ConfigDecodificador, comportamentos: readonly string[]): ConceitosDec {
  const m = motivo;
  validar(m, comportamentos);
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

/** PROPOSTA (DC2b, SEM FONTE): o desfecho e o sinal da significancia `sigma` do episodio, com a margem `limiar_desfecho` */
export function desfechoDoEpisodio(ep: Dict, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR): (typeof DESFECHOS)[number] {
  if (ep["sigma"] >= cfg.limiar_desfecho) return "bom";
  return ep["sigma"] <= -cfg.limiar_desfecho ? "ruim" : "neutro";
}
/** {acao, classe, desfecho} do episodio autobiografico (mem.ts), de catalogo fechado, ou null para o de luta; falha alto fora do catalogo */
export function episodioDec(ep: Dict, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR): EpisodioDec | null {
  if (ep["origem"] === "luta") return null;
  const acao = (ep["acao"] as unknown[])[0] as string;
  if (!COMPORTAMENTOS.includes(acao)) throw new Error("episodio com comportamento desconhecido: " + acao);
  if (!(CLASSES_EPISODIO_DEC as readonly string[]).includes(ep["classe"])) throw new Error("episodio com classe desconhecida: " + ep["classe"]);
  return { acao, classe: ep["classe"], desfecho: desfechoDoEpisodio(ep, cfg) };
}
/** o `dec-v2`: o `dec-v1` com a versao trocada e, no conceito `lembranca`, o `episodio`; `episodio` e o autobiografico recuperado na decisao
    (ou null: sem lembranca, saiu da memoria ou de luta) */
export function decodificarV2(motivo: Dict, S: number, episodio: Dict | null, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR): ConceitosDec {
  const r = decodificar(motivo, S, cfg);
  r.versao = VERSAO_DECODIFICADOR_V2;
  if (episodio === null) return r;
  const rec = (motivo["lembranca"] as Dict)["recuperado"];
  if (rec === null || episodio["id"] !== rec) throw new Error(`o episodio ${String(episodio["id"])} nao e o recuperado na decisao (${String(rec)})`);
  const dec = episodioDec(episodio, cfg);
  if (dec !== null) for (const c of r.conceitos) if (c.nome === "lembranca") c.episodio = dec;
  return r;
}

/* ====================================================================== o dec-v4: a fala do assistir (FA-2 a FA-4; o espelho do decodificador.py) */
export const VERSAO_DECODIFICADOR_V4 = "dec-v4";
const COMPORTAMENTOS_V4 = [...COMPORTAMENTOS, "olhar"];
/** os conceitos do assistir da primeira versao (FA-3, sem o `de_novo`), na ordem do catalogo (o desempate da intencao) */
export const CATALOGO_ASSISTIR = ["gostei", "susto", "chato", "o_que_e"] as const;
export type NomeAssistir = (typeof CATALOGO_ASSISTIR)[number];
const CAMPOS_OLHAR_V4 = ["telas", "olhava", "agrado", "agrado_inato", "gosto", "enjoo", "agrado_efetivo", "olha"];
export interface ConceitoAssistir { nome: NomeAssistir; valor: number; confianca: number }
export interface Assistir { olhava: number; intencao: NomeAssistir | null; conceitos: ConceitoAssistir[] }
export interface ConceitosDecV4 extends ConceitosDec { assistir: Assistir | null }

/** o sinal x em [0, S] em duas retas: 0 -> 0, `limiar` -> h, S -> S */
function escala(x: number, limiar: number, h: number, S: number): number {
  x = clamp(x, 0, S);
  return x < limiar ? divArred(x * h, limiar) : h + divArred((x - limiar) * (S - h), S - limiar);
}
function confiancaAssistir(valor: number, h: number, S: number): number {
  return valor >= h ? divArred((valor - h) * S, S - h) : divArred((h - valor) * S, h);
}
/** os conceitos do assistir (decodificador.py, `conceitos_assistir`), ou null se o pet nao olhava; `anterior` e o motivo da decisao k - 1 */
export function conceitosAssistir(motivo: Dict, anterior: Dict | null, S: number, cfg: ConfigFalaAssistir = CONFIG_FALA_ASSISTIR): Assistir | null {
  const o: Dict = motivo["olhar"];
  const falta = CAMPOS_OLHAR_V4.filter(c => !(c in o));
  if (falta.length) throw new Error("o dec-v4 pede o olhar com o enjoo no motivo; faltam " + falta.join(", "));
  if (o["olhava"] !== null && ["agrado", "agrado_efetivo", "enjoo"].some(c => o[c] === null)) throw new Error("o dec-v4: o pet olhava e o motivo nao tem o agrado, o agrado efetivo ou o enjoo");
  let sustoAntes = 0;
  if (anterior === null) { if (motivo["k"] !== 0) throw new Error(`o dec-v4 pede o motivo anterior a decisao ${motivo["k"]}`); }
  else {
    if (anterior["k"] !== motivo["k"] - 1) throw new Error(`o motivo anterior e o da decisao ${anterior["k"]}, nao o da ${motivo["k"] - 1}`);
    sustoAntes = anterior["afeto"]["urgencias"]["susto"];
  }
  if (o["olhava"] === null) return null;
  const h = cfg.limiar_ativo, urg: Dict = motivo["afeto"]["urgencias"];
  const tapa = (motivo["gestos"] as unknown[][]).some(g => g[0] === "tapa");
  const subida = tapa ? 0 : Math.max(0, urg["susto"] - sustoAntes);
  const ae = o["agrado_efetivo"] as number, enjoo = o["enjoo"] as number;
  const valores: Record<NomeAssistir, number> = {
    gostei: escala(ae, cfg.gostei_agrado, h, S),
    susto: escala(subida, cfg.susto_subida, h, S),
    chato: Math.min(escala(enjoo, cfg.chato_enjoo, h, S), escala(urg["tedio"], cfg.chato_tedio, h, S)),
    o_que_e: Math.min(escala(S - (o["agrado"] as number), S - cfg.o_que_e_agrado, h, S), escala(S - enjoo, S - cfg.o_que_e_enjoo, h, S)),
  };
  const cs: ConceitoAssistir[] = CATALOGO_ASSISTIR.map(nome => ({ nome, valor: valores[nome], confianca: confiancaAssistir(valores[nome], h, S) }));
  const ativos = cs.filter(c => c.valor >= h);
  let intencao: NomeAssistir | null = null;
  if (ativos.some(c => c.nome === "susto")) intencao = "susto";
  else for (const c of ativos) if (intencao === null || c.valor > valores[intencao]) intencao = c.nome;
  return { olhava: o["olhava"], intencao, conceitos: cs };
}
/** o `dec-v4`: os 12 conceitos do dec-v1 com o `olhar` no catalogo e o bloco `assistir`; falha alto sem o olhar com o enjoo */
export function decodificarV4(motivo: Dict, anterior: Dict | null, S: number, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR,
                              cfgAssistir: ConfigFalaAssistir = CONFIG_FALA_ASSISTIR): ConceitosDecV4 {
  if (!("olhar" in motivo)) throw new Error("o dec-v4 pede o motivo com o olhar (a subchave `olhar` do modular)");
  const r = decodificarCom(motivo, S, cfg, COMPORTAMENTOS_V4);
  return { ...r, versao: VERSAO_DECODIFICADOR_V4, assistir: conceitosAssistir(motivo, anterior, S, cfgAssistir) };
}
