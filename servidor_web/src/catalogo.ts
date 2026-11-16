/* O catalogo fechado da fala (porte de servidor/fala_llm.py e de digilab/expressao.py). As tabelas vem de catalogo_fala.json, gerado do Python
   por tools/gerar_catalogo_fala_web.py: a fonte continua uma so. Aqui fica so a logica, conferida contra o gabarito do Python
   (test/gabarito_fala.json). A entrada da pagina nao e confiavel: so acao, fator e parametro do catalogo chegam ao prompt. */
import { readFileSync } from "node:fs";

type TextoFator = { marcador: string; bebe: string; crianca: string; adolescente: string; adulto: string };
export interface Catalogo {
  versao_prompt: string;
  estagios: string[];
  estagios_llm: string[];
  humor_alegre: number;
  humor_neutro: number;
  fatores: Record<string, TextoFator>;
  dominios: Record<string, string[][]>;
  acoes_vida: Record<string, [string, string, string]>;
  acoes_combate: Record<string, [string, string, string]>;
  reacao_bebe: Record<string, string>;
  emote_humor: [string, string, string];
  generico_adulto: string;
  generico_instinto: string;
  max_refs: number;
  max_inteiro: number;
  sistema: string;
  esquema: Record<string, unknown>;
  moldura: { max_palavras: number; max_chars: number; causais: string[]; temas: string[]; extra: string };
  modelo_padrao: string;
  modelos_com_fallback: string[];
  precos_usd_por_mtok: Record<string, [number, number]>;
  max_tokens_saida: number;
  limite_usd_padrao: number;
  limite_por_minuto: number;
  timeout_s: number;
}

export const CATALOGO: Catalogo = JSON.parse(readFileSync(new URL("../catalogo_fala.json", import.meta.url), "utf8"));

/** pedido invalido (o servidor responde 400), como o ValueError/KeyError/TypeError do Python */
export class PedidoInvalido extends Error {}
/** a moldura proposta pela LLM quebra uma regra (cai no template) */
export class FalaReprovada extends Error {}

export type Motivo =
  | { origem: "vida"; acao: string; fatores: string[]; evento_ref: number[]; intensidade: number; exploracao: boolean; tick: number }
  | { origem: "combate"; acao: string; fatores: string[]; evento_ref: number[]; exploracao: boolean; turno: number };

const has = (o: object, k: string): boolean => Object.prototype.hasOwnProperty.call(o, k);
const repr = (x: unknown): string => JSON.stringify(x) ?? String(x);

function fatorValido(f: unknown): string {
  if (typeof f !== "string" || [...f].length > 64) throw new PedidoInvalido(`fator invalido: ${repr(f)}`);
  const base = f.split("(")[0];
  if (!has(CATALOGO.fatores, base)) throw new PedidoInvalido(`fator desconhecido: ${repr(base)}`);
  if (f.includes("(") && !f.endsWith(")")) throw new PedidoInvalido(`fator malformado: ${repr(f)}`);
  const params = f.includes("(") ? f.slice(f.indexOf("(") + 1, -1).split(",") : [];
  const dom = CATALOGO.dominios[base] ?? [];
  if (params.length !== dom.length || params.some((p, i) => !dom[i].includes(p))) throw new PedidoInvalido(`parametros invalidos em ${repr(f)}`);
  return f;
}

function inteiro(x: unknown, rotulo: string): number {
  if (typeof x !== "number" || !Number.isInteger(x) || x < 0 || x > CATALOGO.max_inteiro) throw new PedidoInvalido(`${rotulo} invalido: ${repr(x)}`);
  return x;
}

const CHAVES = {
  vida: ["origem", "acao", "fatores", "evento_ref", "intensidade", "exploracao", "tick"],
  combate: ["origem", "acao", "fatores", "evento_ref", "exploracao", "turno"],
} as const;

/** o motivo a partir do JSON da pagina (motivo_de_dict): campos desconhecidos, faltando ou fora do catalogo levantam erro */
export function motivoDeDict(d: unknown): Motivo {
  if (typeof d !== "object" || d === null || Array.isArray(d)) throw new PedidoInvalido("motivo precisa ser um objeto");
  const o = d as Record<string, unknown>;
  const origem = o.origem;
  if (origem !== "vida" && origem !== "combate") throw new PedidoInvalido(`origem desconhecida: ${repr(origem)}`);
  const chaves: readonly string[] = CHAVES[origem];
  const extras = Object.keys(o).filter(k => !chaves.includes(k) && !["intensidade", "tick", "turno"].includes(k));
  const faltam = chaves.filter(k => !has(o, k));
  if (extras.length || faltam.length) throw new PedidoInvalido(`campos errados no motivo: sobram ${repr(extras.sort())}, faltam ${repr(faltam)}`);
  const acoes = origem === "vida" ? CATALOGO.acoes_vida : CATALOGO.acoes_combate;
  if (typeof o.acao !== "string" || !has(acoes, o.acao)) throw new PedidoInvalido(`acao desconhecida: ${repr(o.acao)}`);
  if (!Array.isArray(o.fatores) || o.fatores.length > 4) throw new PedidoInvalido("fatores precisa ser lista de ate 4");
  if (!Array.isArray(o.evento_ref) || o.evento_ref.length > CATALOGO.max_refs) throw new PedidoInvalido(`evento_ref precisa ser lista de ate ${CATALOGO.max_refs}`);
  if (typeof o.exploracao !== "boolean") throw new PedidoInvalido("exploracao precisa ser booleano");
  const fatores = o.fatores.map(fatorValido);
  const refs = o.evento_ref.map(r => inteiro(r, "evento_ref"));
  /* as regras do proprio Motivo (digilab/motivo.py, __post_init__) */
  if (fatores.length > 2) throw new PedidoInvalido(`no maximo 2 fatores, veio ${repr(fatores)}`);
  if (o.exploracao && fatores.length) throw new PedidoInvalido("exploracao nao tem fator");
  if (origem === "vida") {
    const inten = o.intensidade;
    if (typeof inten !== "number" || !Number.isFinite(inten)) throw new PedidoInvalido("intensidade invalida");
    if (!(inten >= 0 && inten <= 1)) throw new PedidoInvalido(`motivo de vida precisa de intensidade em [0,1]: ${inten}`);
    return { origem, acao: o.acao, fatores, evento_ref: refs, intensidade: inten, exploracao: o.exploracao, tick: inteiro(o.tick, "tick") };
  }
  return { origem, acao: o.acao, fatores, evento_ref: refs, exploracao: o.exploracao, turno: inteiro(o.turno, "turno") };
}

/* ------------------------------------------------ template (digilab/expressao.py: expressar) */

function paramsFator(f: string): string[] {
  if (!f.includes("(")) return [];
  return f.slice(f.indexOf("(") + 1, -1).split(",").map(p => {
    const n = Number(p);
    if (p.trim() === "" || Number.isNaN(n)) return p.replace(/_/g, " ");
    return n > 0 && n < 1 ? `${Math.round(n * 100)}%` : p;
  });
}

function textoFator(f: string, est: "crianca" | "adolescente" | "adulto"): string {
  const t = CATALOGO.fatores[f.split("(")[0]][est];
  if (!t.includes("{")) return t;
  const ps = paramsFator(f);
  return t.replace(/\{p(\d+)\}/g, (_, i: string) => {
    if (Number(i) >= ps.length) throw new PedidoInvalido(`parametro p${i} ausente em ${repr(f)}`);
    return ps[Number(i)];
  });
}

function refsTxt(m: Motivo): string {
  if (!m.evento_ref.length) return "";
  return m.origem === "vida" ? " (lembro do evento #" + m.evento_ref.join(", #") + ")" : " (turno " + m.evento_ref.join(", ") + ")";
}

export function template(m: Motivo, estagio: string, humor: number | null): string {
  if (!CATALOGO.estagios.includes(estagio)) throw new PedidoInvalido(`estagio desconhecido: ${repr(estagio)}`);
  const [icone, palavra, frase] = (m.origem === "vida" ? CATALOGO.acoes_vida : CATALOGO.acoes_combate)[m.acao];
  const fatores = m.exploracao ? [] : m.fatores;
  if (estagio === "bebe") {
    if (m.origem === "vida") {
      if (humor === null) throw new PedidoInvalido("bebe na vida precisa do humor");
      return CATALOGO.emote_humor[humor >= CATALOGO.humor_alegre ? 2 : humor >= CATALOGO.humor_neutro ? 1 : 0];
    }
    return CATALOGO.reacao_bebe[m.acao];
  }
  if (estagio === "crianca") return [icone, ...(fatores.length ? [textoFator(fatores[0], "crianca")] : [])].join(" ");
  if (estagio === "adolescente") return `${palavra}... ` + (fatores.length ? textoFator(fatores[0], "adolescente") : "");
  if (!fatores.length) {
    const geral = m.origem === "vida" && !m.exploracao ? CATALOGO.generico_instinto : CATALOGO.generico_adulto;
    return `${frase}. ${geral}`;
  }
  const causas = fatores.slice(0, 2).map(f => textoFator(f, "adulto")).join(" e ");
  return `${frase} ${causas}${refsTxt(m)}.`;
}

/* ------------------------------------------------ pedido a LLM (montar_pedido, fala-v4 em diante) */

/** faixas iguais as do cache e do emote do bebe (0,33 / 0,66); sem humor, neutro */
export function tomDoHumor(humor: number | null): string {
  if (humor === null) return "neutro";
  return humor >= 0.66 ? "animado" : humor >= 0.33 ? "neutro" : "rabugento";
}

/** json.dumps(..., ensure_ascii=False, sort_keys=True) do Python, para um objeto plano de textos: o mesmo pedido byte a byte */
function dumpsPy(o: Record<string, string>): string {
  return "{" + Object.keys(o).sort().map(k => `${JSON.stringify(k)}: ${JSON.stringify(o[k])}`).join(", ") + "}";
}

/** a LLM so ve a acao, o estagio, o tom e a frase pronta (a verdade); nao ve fatores: nao tem o que inventar */
export function montarPedido(m: Motivo, estagio: string, humor: number | null): string {
  const acoes = m.origem === "vida" ? CATALOGO.acoes_vida : CATALOGO.acoes_combate;
  return dumpsPy({
    contexto: m.origem === "vida" ? "vida do pet" : "luta na arena",
    estagio,
    acao: acoes[m.acao][2],
    tom: tomDoHumor(humor),
    frase: template(m, estagio, humor),
  });
}

/* ------------------------------------------------ validacao da moldura (validar_moldura) */

const EXTRA_MOLDURA = new Set([...CATALOGO.moldura.extra]);
const caractereOk = (c: string): boolean =>
  (c >= " " && c <= "~") || (c >= "À" && c <= "ÿ" && c !== "×" && c !== "÷") || EXTRA_MOLDURA.has(c);
const MARCADORES = Object.values(CATALOGO.fatores).map(e => e.marcador.toLowerCase());

function semRepeticao(parte: string): string {
  const out: string[] = [];
  for (const w of parte.split(" ").filter(Boolean)) if (!out.length || w !== out[out.length - 1]) out.push(w);
  return out.join(" ");
}

/** a moldura so pode enfeitar: curta, sem numero, sem conectivo de causa, sem marcador de fator e sem tema de causa */
export function validarMoldura(abertura: unknown, fecho: unknown): [string, string] {
  const saida: string[] = [];
  for (const [rotulo, bruta] of [["abertura", abertura], ["fecho", fecho]] as const) {
    if (typeof bruta !== "string") throw new FalaReprovada(`${rotulo} nao e texto`);
    const parte = bruta.split(/\s+/u).filter(Boolean).join(" ");
    const baixo = ` ${parte.toLowerCase()} `;
    const fora = [...new Set([...parte].filter(c => !caractereOk(c)))].sort();
    if (fora.length) throw new FalaReprovada(`${rotulo} com caractere fora do alfabeto (${repr(fora.join(""))}): ${repr(parte)}`);
    if ([...parte].length > CATALOGO.moldura.max_chars || parte.split(" ").filter(Boolean).length > CATALOGO.moldura.max_palavras)
      throw new FalaReprovada(`${rotulo} longa demais: ${repr(parte)}`);
    if (/\d/.test(parte.replaceAll(":3", ""))) throw new FalaReprovada(`${rotulo} com numero: ${repr(parte)}`);
    for (const c of CATALOGO.moldura.causais) if (baixo.includes(c)) throw new FalaReprovada(`${rotulo} com conectivo de causa (${repr(c.trim())}): ${repr(parte)}`);
    for (const m of MARCADORES) if (baixo.includes(m)) throw new FalaReprovada(`${rotulo} usa o marcador de um fator: ${repr(parte)}`);
    for (const t of CATALOGO.moldura.temas) if (baixo.includes(t)) throw new FalaReprovada(`${rotulo} fala de um tema de causa (${repr(t)}): ${repr(parte)}`);
    saida.push(semRepeticao(parte));
  }
  return [saida[0], saida[1]];
}

export const compor = (abertura: string, frase: string, fecho: string): string => [abertura, frase.trim(), fecho].filter(Boolean).join(" ");
