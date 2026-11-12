/* A fala por LLM (porte de servidor/fala_llm.py, so o provedor Claude). Troca so o TEXTO da fala do adolescente e do adulto: a LLM gera a
   moldura (abertura e fecho, no tom do humor) e o miolo e sempre o template. A moldura e validada; qualquer falha (sem credencial, rede,
   recusa, validacao, teto, limite por minuto) cai no template. Nada daqui entra no registro do pet. */
import Anthropic from "@anthropic-ai/sdk";
import { CATALOGO, FalaReprovada, PedidoInvalido, compor, montarPedido, template, validarMoldura, type Motivo } from "./catalogo.ts";
import { custoUsd, type ControleGasto } from "./gasto.ts";

export interface RespostaProvedor {
  texto: string;              // o JSON devolvido pelo modelo
  completa: boolean;          // false se cortou (limite de tokens) ou recusou
  motivoParada: string;
  modelo: string;
  tokensEntrada: number | null;
  tokensSaida: number | null;
}

/** o pedaco do cliente do SDK que a fala usa (os testes passam um falso: nenhuma chamada paga) */
export interface ClienteClaude {
  messages: { create(p: Record<string, unknown>): Promise<unknown> };
  beta: { messages: { create(p: Record<string, unknown>): Promise<unknown> } };
}

interface MensagemSdk {
  content: { type: string; text?: string }[];
  stop_reason: string | null;
  model?: string;
  usage?: { input_tokens?: number; output_tokens?: number };
}

export class ProvedorClaude {
  readonly nome = "claude";
  readonly temCusto = true;
  readonly cliente: ClienteClaude | null;
  readonly modelo: string;
  readonly maxTokens: number;

  constructor(cliente: ClienteClaude | null, modelo: string = CATALOGO.modelo_padrao, maxTokens: number = CATALOGO.max_tokens_saida) {
    /* modelo sem preco na tabela nao liga: sem preco nao da para garantir o teto de gasto */
    if (!(modelo in CATALOGO.precos_usd_por_mtok))
      throw new Error(`modelo sem preco conhecido: ${JSON.stringify(modelo)}; sem preco nao da para garantir o teto de gasto`);
    this.cliente = cliente;
    this.modelo = modelo;
    this.maxTokens = maxTokens;
  }

  disponivel(): [boolean, string] {
    return this.cliente !== null ? [true, ""] : [false, "sem credencial da API (ANTHROPIC_API_KEY)"];
  }

  /** entrada estimada por cima: 1 token a cada 2 caracteres */
  custoMaximo(sistema: string, pedido: string): number {
    return custoUsd(this.modelo, Math.ceil(([...sistema].length + [...pedido].length + 400) / 2), this.maxTokens);
  }

  custoReal(r: RespostaProvedor): number | null {
    if (r.tokensEntrada === null || r.tokensSaida === null) return null;
    /* o fallback de recusa pode cobrar outro modelo; sem preco dele, usa o mais caro da tabela */
    const precos = CATALOGO.precos_usd_por_mtok;
    const m = r.modelo in precos ? r.modelo : Object.keys(precos).reduce((a, b) => (precos[b][1] > precos[a][1] ? b : a));
    return custoUsd(m, r.tokensEntrada, r.tokensSaida);
  }

  async gerar(sistema: string, pedido: string, esquema: Record<string, unknown>): Promise<RespostaProvedor> {
    if (this.cliente === null) throw new Error("sem cliente");
    const base = { model: this.modelo, max_tokens: this.maxTokens, system: sistema, messages: [{ role: "user", content: pedido }] };
    const formato = { type: "json_schema", schema: esquema };
    const resp = (CATALOGO.modelos_com_fallback.includes(this.modelo)
      /* Opus 5 / Fable 5.1: esforco baixo e fallback de recusa do servidor da API */
      ? await this.cliente.beta.messages.create({ ...base, output_config: { effort: "low", format: formato },
          betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" })
      /* Haiku 4.5: sem `effort` (o modelo rejeita); recusa cai no template */
      : await this.cliente.messages.create({ ...base, output_config: { format: formato } })) as MensagemSdk;
    const texto = resp.content.find(b => b.type === "text")?.text ?? "";
    return { texto, completa: resp.stop_reason === "end_turn", motivoParada: String(resp.stop_reason), modelo: resp.model ?? this.modelo,
      tokensEntrada: resp.usage?.input_tokens ?? null, tokensSaida: resp.usage?.output_tokens ?? null };
  }
}

export interface Resultado { texto: string; fonte: "llm" | "template"; detalhe: string }

/** troca o surrogate solto por "?" (o encode("utf-8", "replace") do Python) */
const limpo = (s: string): string => s.replace(/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/g, "?");

/** a fala com cache, limite por minuto, teto de gasto e queda para o template; sem provedor, so template */
export class GeradorFala {
  readonly provedor: ProvedorClaude | null;
  readonly gasto: ControleGasto | null;
  readonly limite: number;
  readonly estatisticas = { llm: 0, template: 0, reprovadas: 0, erros: 0, cache: 0 };
  private readonly cache = new Map<string, Resultado>();
  private chamadas: number[] = [];
  private readonly agora: () => number;

  constructor(provedor: ProvedorClaude | null, gasto: ControleGasto | null, limitePorMinuto: number = CATALOGO.limite_por_minuto,
    agora: () => number = () => performance.now()) {
    if (provedor !== null && provedor.temCusto && gasto === null) throw new Error("provedor com custo exige um ControleGasto");
    this.provedor = provedor;
    this.gasto = gasto;
    this.limite = limitePorMinuto;
    this.agora = agora;
  }

  get modelo(): string | null { return this.provedor?.modelo ?? null; }

  private chave(m: Motivo, estagio: string, humor: number | null): string {
    const faixa = humor === null ? null : humor >= 0.66 ? 2 : humor >= 0.33 ? 1 : 0;
    return JSON.stringify([m, estagio, faixa, this.provedor?.nome ?? null, this.modelo, CATALOGO.versao_prompt]);
  }

  private podeChamar(): boolean {
    const t = this.agora();
    this.chamadas = this.chamadas.filter(x => t - x < 60_000);
    if (this.chamadas.length >= this.limite) return false;
    this.chamadas.push(t);
    return true;
  }

  private doTemplate(m: Motivo, estagio: string, humor: number | null, detalhe: string): Resultado {
    const texto = template(m, estagio, humor);
    this.estatisticas.template += 1;
    return { texto, fonte: "template", detalhe };
  }

  async gerar(m: Motivo, estagio: string, humor: number | null): Promise<Resultado> {
    if (!CATALOGO.estagios.includes(estagio)) throw new PedidoInvalido(`estagio desconhecido: ${JSON.stringify(estagio)}`);
    if (!CATALOGO.estagios_llm.includes(estagio)) return this.doTemplate(m, estagio, humor, `estagio ${estagio} nao usa LLM`);
    const p = this.provedor;
    if (p === null) return this.doTemplate(m, estagio, humor, "servidor sem provedor de LLM");
    const chave = this.chave(m, estagio, humor);
    const pronta = this.cache.get(chave);
    if (pronta) { this.estatisticas.cache += 1; return pronta; }
    if (!this.podeChamar()) return this.doTemplate(m, estagio, humor, "limite de chamadas por minuto");
    const pedido = montarPedido(m, estagio, humor);
    const g = this.gasto!;
    const custoMax = p.custoMaximo(CATALOGO.sistema, pedido);
    if (!g.reservar(custoMax))
      return this.doTemplate(m, estagio, humor, `limite de gasto atingido (US$ ${g.gasto.toFixed(4)} de US$ ${g.limite.toFixed(2)})`);
    let r: RespostaProvedor;
    try {
      r = await p.gerar(CATALOGO.sistema, pedido, CATALOGO.esquema);
    } catch (err) {
      /* rede, credencial, timeout: a fala e so exibicao; sem uso informado, conta o pior caso */
      g.acertar(custoMax, custoMax);
      this.estatisticas.erros += 1;
      return this.doTemplate(m, estagio, humor, `erro no provedor ${p.nome}: ${(err as Error)?.constructor?.name ?? "Error"}`);
    }
    g.acertar(custoMax, p.custoReal(r) ?? custoMax);
    if (!r.completa) {
      this.estatisticas.erros += 1;
      return this.doTemplate(m, estagio, humor, `resposta interrompida: ${r.motivoParada}`);
    }
    let abertura: string, fecho: string;
    try {
      const dados: unknown = JSON.parse(limpo(r.texto));
      if (typeof dados !== "object" || dados === null || Array.isArray(dados)) throw new FalaReprovada("resposta nao e objeto");
      const o = dados as Record<string, unknown>;
      if (!("abertura" in o) || !("fecho" in o)) throw new FalaReprovada("resposta sem abertura ou fecho");
      [abertura, fecho] = validarMolduraLimpa(o.abertura, o.fecho);
    } catch (err) {
      if (!(err instanceof FalaReprovada || err instanceof SyntaxError)) throw err;
      this.estatisticas.reprovadas += 1;
      return this.doTemplate(m, estagio, humor, `reprovada: ${err.message}`);
    }
    const res: Resultado = { texto: compor(abertura, template(m, estagio, humor), fecho), fonte: "llm", detalhe: `${p.nome}: ${r.modelo}` };
    this.estatisticas.llm += 1;
    this.cache.set(chave, res);
    return res;
  }
}

const validarMolduraLimpa = (a: unknown, f: unknown): [string, string] =>
  validarMoldura(typeof a === "string" ? limpo(a) : a, typeof f === "string" ? limpo(f) : f);

/** cliente do Claude se houver credencial no ambiente; senao null. A chave fica so no ambiente do servidor, nunca na pagina */
export function criarClienteClaude(env: NodeJS.ProcessEnv = process.env): ClienteClaude | null {
  if (!(env.ANTHROPIC_API_KEY || env.ANTHROPIC_AUTH_TOKEN || env.ANTHROPIC_PROFILE)) return null;
  return new Anthropic({ timeout: CATALOGO.timeout_s * 1000, maxRetries: 0 }) as unknown as ClienteClaude;
}
