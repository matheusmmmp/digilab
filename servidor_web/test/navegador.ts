/* O navegador de mentira e o login pelo provedor falso, para os testes que precisam de uma conta (o envio dos logs, MMO3). O mesmo fluxo do
   test/conta.test.ts (CN2): banco na memória, relógio parado, nenhuma chamada sai da máquina. */
import { expect } from "vitest";
import { criarApp } from "../src/app.ts";
import { abrirBanco, type Banco } from "../src/conta/banco.ts";
import { configDoAmbiente, VERSAO_PRIVACIDADE, VERSAO_TERMOS, type ConfigConta } from "../src/conta/config.ts";
import { GeradorFala } from "../src/fala.ts";

export const API = "http://127.0.0.1:8766";
export const JOGO = "http://127.0.0.1:5173/jogo/";
export const ORIGEM_JOGO = "http://127.0.0.1:5173";
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36";

export type App = ReturnType<typeof criarApp>;

/** um navegador: guarda os cookies entre os pedidos */
export class Navegador {
  readonly cookies = new Map<string, string>();
  readonly app: App;
  constructor(app: App) { this.app = app; }
  async pedir(caminho: string, init: Omit<RequestInit, "headers"> & { headers?: Record<string, string> } = {}): Promise<Response> {
    const headers: Record<string, string> = { "User-Agent": UA, ...(init.headers ?? {}) };
    if (this.cookies.size) headers.Cookie = [...this.cookies].map(([k, v]) => `${k}=${v}`).join("; ");
    const r = await this.app.request(caminho, { ...init, headers });
    for (const sc of r.headers.getSetCookie()) {
      const [par] = sc.split(";"), i = par!.indexOf("=");
      const nome = par!.slice(0, i), valor = par!.slice(i + 1);
      if (/Max-Age=0/i.test(sc) || valor === "") this.cookies.delete(nome); else this.cookies.set(nome, valor);
    }
    return r;
  }
  /** um pedido com corpo JSON; `corpo` em texto vai como está */
  json(metodo: string, caminho: string, corpo?: unknown, csrf?: string, extra: Record<string, string> = {}): Promise<Response> {
    const headers: Record<string, string> = { ...extra };
    if (csrf !== undefined) headers["X-CSRF-Token"] = csrf;
    if (corpo !== undefined) headers["Content-Type"] = "application/json";
    const body = corpo === undefined ? undefined : typeof corpo === "string" ? corpo : JSON.stringify(corpo);
    return this.pedir(caminho, { method: metodo, headers, body });
  }
}

const caminho = (url: string): string => { const u = new URL(url); return u.pathname + u.search; };

export interface Montado { app: App; cfg: ConfigConta; banco: Banco; relogio: { t: number } }

export function montar(): Montado {
  const relogio = { t: Date.UTC(2026, 10, 16, 12) };
  const banco = abrirBanco(":memory:");
  const cfg = configDoAmbiente({ porta: 8766, banco, agora: () => relogio.t,
    ambiente: { DIGILAB_URL_API: API, DIGILAB_URL_JOGO: JOGO, DIGILAB_CONVIDADOS: "falso:ana falso:caio" } });
  return { app: criarApp({ gerador: new GeradorFala(null, null), motivoInicial: "", conta: cfg }), cfg, banco, relogio };
}

/** o fluxo inteiro pelo provedor falso até a conta criada; devolve o csrf da sessão */
export async function criarConta(nav: Navegador, usuario = "ana"): Promise<string> {
  const ida = await nav.pedir("/auth/falso?volta=%23%2Fconfig%2Fconta");
  const autorizar = new URL(ida.headers.get("location")!);
  const form = new URLSearchParams({ state: autorizar.searchParams.get("state")!, code_challenge: autorizar.searchParams.get("code_challenge")!,
    redirect_uri: autorizar.searchParams.get("redirect_uri")!, usuario });
  const dado = await nav.pedir("/auth/falso/autorizar", { method: "POST", body: form.toString(),
    headers: { "Content-Type": "application/x-www-form-urlencoded" } });
  const cb = await nav.pedir(caminho(dado.headers.get("location")!));
  expect(new URL(cb.headers.get("location")!).searchParams.get("conta")).toBe("primeiro_acesso");
  const p = await (await nav.pedir("/conta/primeiro-acesso")).json() as { csrf: string };
  const r = await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais", aceite: { termos: VERSAO_TERMOS, privacidade: VERSAO_PRIVACIDADE } }, p.csrf);
  expect(r.status).toBe(201);
  return ((await (await nav.pedir("/conta")).json()) as { csrf: string }).csrf;
}

export const contar = (banco: Banco, tabela: string): number => (banco.prepare(`SELECT count(*) AS n FROM ${tabela}`).get() as { n: number }).n;
