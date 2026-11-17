/* O login por provedor (CN2; CN-2: Google e GitHub, sem senha). Cada provedor cumpre a interface Provedor: monta o endereço de
   autorização (com o state e o desafio do PKCE, S256) e troca o código pelo perfil. O servidor nunca vê senha.

   O perfil devolvido tem o id do provedor e, quando houver, o login (GitHub) e o e-mail verificado (Google). O login e o e-mail servem
   só para conferir a lista de convidados (CN-10), na memória: NÃO se guardam (seção 9 do plano). O banco guarda o provedor e o id.

   Sem as chaves no ambiente (GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET; GITHUB_CLIENT_ID e GITHUB_CLIENT_SECRET), o provedor real fica
   desligado e diz por quê. O ProvedorFalso é para os testes e para o `npm run dev` local: ele mesmo faz a página de autorização e confere
   o PKCE como um provedor de verdade; fora do local, ele não liga (config.ts). */
import { createHash, randomBytes } from "node:crypto";

export type NomeProvedor = "google" | "github" | "falso";
export const NOMES_PROVEDOR: readonly NomeProvedor[] = ["google", "github", "falso"];

export interface Perfil {
  /** o id estável do usuário no provedor (o `sub` do Google, o `id` numérico do GitHub) */
  id: string;
  /** o login público (GitHub), só para a lista de convidados */
  login?: string;
  /** o e-mail verificado (Google), só para a lista de convidados; nunca se guarda */
  emailVerificado?: string;
}

export interface PedidoAutorizacao { state: string; desafio: string; redirectUri: string }
export interface PedidoTroca { codigo: string; verificador: string; redirectUri: string }

export interface Provedor {
  readonly nome: NomeProvedor;
  /** [ligado, motivo]: o motivo diz por que está desligado ("" se ligado) */
  estado(): [boolean, string];
  urlAutorizacao(p: PedidoAutorizacao): string;
  trocarCodigo(p: PedidoTroca): Promise<Perfil>;
}

/** erro do provedor (código recusado, resposta sem id): o callback responde "não deu" sem guardar nada */
export class ErroProvedor extends Error {}

export type Buscar = (url: string, init?: RequestInit) => Promise<Response>;

/* --- o PKCE (RFC 7636, método S256) --- */
export const aleatorio = (bytes = 32): string => randomBytes(bytes).toString("base64url");
export const desafioPkce = (verificador: string): string => createHash("sha256").update(verificador).digest("base64url");

interface Credenciais { clientId: string; clientSecret: string }

function credenciaisDe(ambiente: Record<string, string | undefined>, prefixo: string): Credenciais | null {
  const clientId = ambiente[`${prefixo}_CLIENT_ID`]?.trim(), clientSecret = ambiente[`${prefixo}_CLIENT_SECRET`]?.trim();
  return clientId && clientSecret ? { clientId, clientSecret } : null;
}

async function lerJson(r: Response, oQue: string): Promise<Record<string, unknown>> {
  if (!r.ok) throw new ErroProvedor(`${oQue}: HTTP ${r.status}`);
  const d = await r.json() as unknown;
  if (typeof d !== "object" || d === null || Array.isArray(d)) throw new ErroProvedor(`${oQue}: resposta não é um objeto`);
  return d as Record<string, unknown>;
}

abstract class ProvedorOAuth implements Provedor {
  abstract readonly nome: NomeProvedor;
  protected abstract readonly variavel: string;
  protected readonly cred: Credenciais | null;
  protected readonly buscar: Buscar;
  constructor(cred: Credenciais | null, buscar: Buscar) { this.cred = cred; this.buscar = buscar; }
  estado(): [boolean, string] {
    return this.cred ? [true, ""] : [false, `sem ${this.variavel}_CLIENT_ID e ${this.variavel}_CLIENT_SECRET no ambiente`];
  }
  protected exigir(): Credenciais {
    if (!this.cred) throw new ErroProvedor(this.estado()[1]);
    return this.cred;
  }
  abstract urlAutorizacao(p: PedidoAutorizacao): string;
  abstract trocarCodigo(p: PedidoTroca): Promise<Perfil>;
}

/** o Google (OpenID Connect): o escopo `openid email`; o e-mail vem só para a lista de convidados e não se guarda */
export class ProvedorGoogle extends ProvedorOAuth {
  readonly nome = "google" as const;
  protected readonly variavel = "GOOGLE";
  static readonly AUTORIZAR = "https://accounts.google.com/o/oauth2/v2/auth";
  static readonly TOKEN = "https://oauth2.googleapis.com/token";
  static readonly PERFIL = "https://openidconnect.googleapis.com/v1/userinfo";
  urlAutorizacao({ state, desafio, redirectUri }: PedidoAutorizacao): string {
    const u = new URL(ProvedorGoogle.AUTORIZAR);
    u.search = new URLSearchParams({ client_id: this.exigir().clientId, redirect_uri: redirectUri, response_type: "code",
      scope: "openid email", state, code_challenge: desafio, code_challenge_method: "S256", prompt: "select_account" }).toString();
    return u.toString();
  }
  async trocarCodigo({ codigo, verificador, redirectUri }: PedidoTroca): Promise<Perfil> {
    const c = this.exigir();
    const token = await lerJson(await this.buscar(ProvedorGoogle.TOKEN, { method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
      body: new URLSearchParams({ grant_type: "authorization_code", code: codigo, redirect_uri: redirectUri, client_id: c.clientId,
        client_secret: c.clientSecret, code_verifier: verificador }).toString() }), "token do Google");
    if (typeof token.access_token !== "string") throw new ErroProvedor("token do Google sem access_token");
    const p = await lerJson(await this.buscar(ProvedorGoogle.PERFIL, { headers: { Authorization: `Bearer ${token.access_token}` } }), "perfil do Google");
    if (typeof p.sub !== "string" || !p.sub) throw new ErroProvedor("perfil do Google sem sub");
    const email = p.email_verified === true && typeof p.email === "string" ? p.email : undefined;
    return email ? { id: p.sub, emailVerificado: email } : { id: p.sub };
  }
}

/** o GitHub (OAuth app, com PKCE): sem escopo, só o perfil público (o id e o login) */
export class ProvedorGitHub extends ProvedorOAuth {
  readonly nome = "github" as const;
  protected readonly variavel = "GITHUB";
  static readonly AUTORIZAR = "https://github.com/login/oauth/authorize";
  static readonly TOKEN = "https://github.com/login/oauth/access_token";
  static readonly PERFIL = "https://api.github.com/user";
  urlAutorizacao({ state, desafio, redirectUri }: PedidoAutorizacao): string {
    const u = new URL(ProvedorGitHub.AUTORIZAR);
    u.search = new URLSearchParams({ client_id: this.exigir().clientId, redirect_uri: redirectUri, scope: "", state,
      code_challenge: desafio, code_challenge_method: "S256", allow_signup: "true" }).toString();
    return u.toString();
  }
  async trocarCodigo({ codigo, verificador, redirectUri }: PedidoTroca): Promise<Perfil> {
    const c = this.exigir();
    const token = await lerJson(await this.buscar(ProvedorGitHub.TOKEN, { method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
      body: new URLSearchParams({ client_id: c.clientId, client_secret: c.clientSecret, code: codigo, redirect_uri: redirectUri,
        code_verifier: verificador }).toString() }), "token do GitHub");
    if (typeof token.access_token !== "string") throw new ErroProvedor(`token do GitHub sem access_token${typeof token.error === "string" ? ` (${token.error})` : ""}`);
    const p = await lerJson(await this.buscar(ProvedorGitHub.PERFIL, { headers: { Authorization: `Bearer ${token.access_token}`,
      Accept: "application/vnd.github+json", "User-Agent": "digilab-servidor-web" } }), "perfil do GitHub");
    if (typeof p.id !== "number" && typeof p.id !== "string") throw new ErroProvedor("perfil do GitHub sem id");
    return typeof p.login === "string" ? { id: String(p.id), login: p.login } : { id: String(p.id) };
  }
}

/** o provedor falso: a "autorização" é uma página do próprio servidor (GET /auth/falso/autorizar), onde se escolhe o usuário de
    teste; o código vale uma vez, por 5 minutos, e só com o verificador certo (o PKCE de verdade). Nunca liga fora do local. */
export class ProvedorFalso implements Provedor {
  readonly nome = "falso" as const;
  private readonly codigos = new Map<string, { perfil: Perfil; desafio: string; redirectUri: string; expira: number }>();
  private readonly urlApi: string;
  private readonly agora: () => number;
  constructor(urlApi: string, agora: () => number = Date.now) { this.urlApi = urlApi; this.agora = agora; }
  estado(): [boolean, string] { return [true, ""]; }
  urlAutorizacao({ state, desafio, redirectUri }: PedidoAutorizacao): string {
    const u = new URL("/auth/falso/autorizar", this.urlApi);
    u.search = new URLSearchParams({ state, code_challenge: desafio, redirect_uri: redirectUri }).toString();
    return u.toString();
  }
  /** a página de autorização chama isto com o usuário escolhido; devolve o código que volta ao /auth/callback */
  emitirCodigo(perfil: Perfil, desafio: string, redirectUri: string): string {
    const codigo = aleatorio(16);
    this.codigos.set(codigo, { perfil, desafio, redirectUri, expira: this.agora() + 5 * 60_000 });
    return codigo;
  }
  async trocarCodigo({ codigo, verificador, redirectUri }: PedidoTroca): Promise<Perfil> {
    const c = this.codigos.get(codigo);
    this.codigos.delete(codigo);
    if (!c || c.expira < this.agora()) throw new ErroProvedor("código desconhecido ou expirado");
    if (c.redirectUri !== redirectUri) throw new ErroProvedor("redirect_uri diferente");
    if (desafioPkce(verificador) !== c.desafio) throw new ErroProvedor("PKCE: o verificador não confere");
    return c.perfil;
  }
}

/** os provedores reais pelo ambiente (desligados sem as chaves) */
export function provedoresReais(ambiente: Record<string, string | undefined>, buscar: Buscar = fetch): Provedor[] {
  return [new ProvedorGoogle(credenciaisDe(ambiente, "GOOGLE"), buscar), new ProvedorGitHub(credenciaisDe(ambiente, "GITHUB"), buscar)];
}
