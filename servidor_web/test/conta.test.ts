/* A conta (CN2) com o provedor falso e o banco na memória: o fluxo inteiro, o CSRF, o cookie, o CORS, o convidado fora da lista, o
   menor, apagar e baixar. O Google e o GitHub entram com um fetch falso: nenhuma chamada sai da máquina. */
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { criarApp } from "../src/app.ts";
import { ROOKIES, sortearApelido } from "../src/conta/apelido.ts";
import { abrirBanco, migrar, versaoDe, VERSAO_BANCO, type Banco } from "../src/conta/banco.ts";
import { configDoAmbiente, VERSAO_PRIVACIDADE, VERSAO_TERMOS, type ConfigConta } from "../src/conta/config.ts";
import { chavesDoPerfil, normalizarChave } from "../src/conta/convidados.ts";
import { desafioPkce, ProvedorGitHub, ProvedorGoogle, type Buscar } from "../src/conta/provedores.ts";
import { COOKIE_PENDENTE, COOKIE_SESSAO, DURACAO_SESSAO_MS, destinoSeguro, nomeDoAparelho } from "../src/conta/rotas.ts";
import { GeradorFala } from "../src/fala.ts";

const API = "http://127.0.0.1:8766";
const JOGO = "http://127.0.0.1:5173/jogo/";
const ORIGEM_JOGO = "http://127.0.0.1:5173";
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36";
const ACEITE = { termos: VERSAO_TERMOS, privacidade: VERSAO_PRIVACIDADE };

type App = ReturnType<typeof criarApp>;

/** um navegador: guarda os cookies entre os pedidos */
class Navegador {
  readonly cookies = new Map<string, string>();
  readonly brutos: string[] = [];
  readonly app: App;
  readonly ua: string;
  constructor(app: App, ua = UA) { this.app = app; this.ua = ua; }
  async pedir(caminho: string, init: Omit<RequestInit, "headers"> & { headers?: Record<string, string> } = {}): Promise<Response> {
    const headers: Record<string, string> = { "User-Agent": this.ua, ...(init.headers ?? {}) };
    if (this.cookies.size) headers.Cookie = [...this.cookies].map(([k, v]) => `${k}=${v}`).join("; ");
    const r = await this.app.request(caminho, { ...init, headers });
    for (const sc of r.headers.getSetCookie()) {
      this.brutos.push(sc);
      const [par] = sc.split(";"), i = par!.indexOf("=");
      const nome = par!.slice(0, i), valor = par!.slice(i + 1);
      if (/Max-Age=0/i.test(sc) || valor === "") this.cookies.delete(nome); else this.cookies.set(nome, valor);
    }
    return r;
  }
  json(metodo: string, caminho: string, corpo?: unknown, csrf?: string, extra: Record<string, string> = {}): Promise<Response> {
    const headers: Record<string, string> = { ...extra };
    if (csrf !== undefined) headers["X-CSRF-Token"] = csrf;
    if (corpo !== undefined) headers["Content-Type"] = "application/json";
    return this.pedir(caminho, { method: metodo, headers, body: corpo === undefined ? undefined : JSON.stringify(corpo) });
  }
}

const caminho = (url: string): string => { const u = new URL(url); return u.pathname + u.search; };

interface Montado { app: App; cfg: ConfigConta; banco: Banco; relogio: { t: number } }

function montar(ambiente: Record<string, string> = {}, buscar?: Buscar): Montado {
  const relogio = { t: Date.UTC(2026, 10, 16, 12) };
  const banco = abrirBanco(":memory:");
  const cfg = configDoAmbiente({ porta: 8766, banco, buscar, agora: () => relogio.t,
    ambiente: { DIGILAB_URL_API: API, DIGILAB_URL_JOGO: JOGO, DIGILAB_CONVIDADOS: "falso:ana falso:caio", ...ambiente } });
  return { app: criarApp({ gerador: new GeradorFala(null, null), motivoInicial: "", conta: cfg }), cfg, banco, relogio };
}

/** o login pelo provedor falso até a volta ao jogo; devolve o endereço de volta */
async function entrarFalso(nav: Navegador, usuario: string, volta = "#/config/conta"): Promise<URL> {
  const ida = await nav.pedir(`/auth/falso?volta=${encodeURIComponent(volta)}`);
  expect(ida.status).toBe(302);
  const autorizar = new URL(ida.headers.get("location")!);
  expect(autorizar.pathname).toBe("/auth/falso/autorizar");
  expect(autorizar.searchParams.get("code_challenge")).toMatch(/^[A-Za-z0-9_-]{43}$/);
  const pagina = await nav.pedir(caminho(autorizar.toString()));
  expect(pagina.status).toBe(200);
  const form = new URLSearchParams({ state: autorizar.searchParams.get("state")!, code_challenge: autorizar.searchParams.get("code_challenge")!,
    redirect_uri: autorizar.searchParams.get("redirect_uri")!, usuario });
  const dado = await nav.pedir("/auth/falso/autorizar", { method: "POST", body: form.toString(),
    headers: { "Content-Type": "application/x-www-form-urlencoded" } });
  expect(dado.status).toBe(302);
  const cb = await nav.pedir(caminho(dado.headers.get("location")!));
  expect(cb.status).toBe(302);
  return new URL(cb.headers.get("location")!);
}

/** o fluxo inteiro até a conta criada; devolve o csrf da sessão */
async function criarConta(nav: Navegador, usuario = "ana"): Promise<string> {
  const volta = await entrarFalso(nav, usuario);
  expect(volta.searchParams.get("conta")).toBe("primeiro_acesso");
  const p = await (await nav.pedir("/conta/primeiro-acesso")).json() as any;
  const r = await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais", aceite: ACEITE }, p.csrf);
  expect(r.status).toBe(201);
  const conta = await (await nav.pedir("/conta")).json() as any;
  return conta.csrf;
}

const contar = (banco: Banco, tabela: string): number => (banco.prepare(`SELECT count(*) AS n FROM ${tabela}`).get() as { n: number }).n;
const TABELAS = ["contas", "identidades", "consentimentos", "aparelhos", "sessoes"];

describe("o banco", () => {
  it("migra até a versão do código, com as tabelas da seção 4, e migrar de novo não faz nada", () => {
    const b = abrirBanco(":memory:");
    expect(versaoDe(b)).toBe(VERSAO_BANCO);
    const tabelas = (b.prepare("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").all() as { name: string }[]).map(r => r.name);
    expect(tabelas).toEqual(expect.arrayContaining([...TABELAS, "estados_oauth", "acessos_pendentes", "convidados"]));
    expect(migrar(b)).toBe(0);
  });
  it("um banco mais novo que o código não abre", () => {
    const b = abrirBanco(":memory:");
    b.exec(`PRAGMA user_version = ${VERSAO_BANCO + 1}`);
    expect(() => migrar(b)).toThrow(/versão/);
  });
  it("a idade só aceita adulto (o menor nunca vira conta)", () => {
    const b = abrirBanco(":memory:");
    expect(() => b.prepare("INSERT INTO contas VALUES ('x', 'Agumon#1000', 0, 'menos_de_18')").run()).toThrow();
  });
});

describe("os provedores reais sem as chaves", () => {
  it("ficam desligados e dizem por quê", async () => {
    const { app } = montar();
    const lista = await (await app.request("/auth/provedores")).json() as any[];
    expect(lista.find(p => p.nome === "google")).toEqual({ nome: "google", ligado: false, motivo: "sem GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no ambiente" });
    expect(lista.find(p => p.nome === "github").ligado).toBe(false);
    expect(lista.find(p => p.nome === "falso").ligado).toBe(true);
    const r = await app.request("/auth/github");
    expect(r.status).toBe(503);
    expect((await r.json() as any).motivo).toMatch(/GITHUB_CLIENT_ID/);
    expect((await app.request("/auth/orkut")).status).toBe(404);
  });
  it("o provedor falso não liga fora do local, e o local sem lista deixa só a ana", () => {
    expect(() => configDoAmbiente({ porta: 1, banco: abrirBanco(":memory:"), ambiente: { DIGILAB_URL_API: "https://api.exemplo.test",
      DIGILAB_URL_JOGO: "https://exemplo.test/jogo/", DIGILAB_PROVEDOR_FALSO: "1", DIGILAB_TURNSTILE: "0" } })).toThrow(/falso só liga no local/);
    const fora = configDoAmbiente({ porta: 1, banco: abrirBanco(":memory:"), ambiente: { DIGILAB_URL_API: "https://api.exemplo.test",
      DIGILAB_URL_JOGO: "https://exemplo.test/jogo/", DIGILAB_TURNSTILE: "0" } });
    expect(fora.provedores.has("falso")).toBe(false);
    expect(fora.cookieSeguro).toBe(true);
    expect(() => configDoAmbiente({ porta: 1, banco: abrirBanco(":memory:"), ambiente: { DIGILAB_URL_API: "http://api.exemplo.test" } })).toThrow(/https/);
    const local = configDoAmbiente({ porta: 9, banco: abrirBanco(":memory:"), ambiente: {} });
    expect(local.urlJogo).toBe("http://127.0.0.1:9/dev/conta");
    expect(local.convidados.contem("falso", { id: "id-ana", login: "ana" })).toBe(true);
    expect(local.convidados.contem("falso", { id: "id-bia", login: "bia" })).toBe(false);
  });
});

describe("o fluxo inteiro com o provedor falso", () => {
  it("entrar, o primeiro acesso, trocar o apelido, criar, ler a conta, sair e entrar de novo", async () => {
    const { app, banco } = montar();
    const nav = new Navegador(app);
    const volta = await entrarFalso(nav, "ana", "#/config/conta");
    expect(volta.origin + volta.pathname).toBe(JOGO);
    expect(volta.searchParams.get("conta")).toBe("primeiro_acesso");
    expect(volta.hash).toBe("#/config/conta");
    expect(nav.cookies.has(COOKIE_PENDENTE)).toBe(true);
    expect(TABELAS.map(t => contar(banco, t))).toEqual([0, 0, 0, 0, 0]);

    const p = await (await nav.pedir("/conta/primeiro-acesso")).json() as any;
    expect(p.apelido).toMatch(/^[A-Za-z]+#\d{4}$/);
    expect(ROOKIES).toContain(p.apelido.split("#")[0]);
    expect(p.digimons).toEqual(ROOKIES);
    expect(p.idades).toEqual(["18_ou_mais", "menos_de_18"]);
    expect(p.provedor).toBe("falso");

    const troca = await nav.json("POST", "/conta/primeiro-acesso/apelido", { digimon: "Gomamon" }, p.csrf);
    expect(troca.status).toBe(200);
    const { apelido } = await troca.json() as any;
    expect(apelido).toMatch(/^Gomamon#\d{4}$/);
    expect((await nav.json("POST", "/conta/primeiro-acesso/apelido", { digimon: "WarGreymon" }, p.csrf)).status).toBe(400);

    const criar = await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais", aceite: ACEITE }, p.csrf);
    expect(criar.status).toBe(201);
    const criada = await criar.json() as any;
    expect(criada.conta.apelido).toBe(apelido);
    expect(criada.destino).toBe("#/config/conta");
    expect(nav.cookies.has(COOKIE_PENDENTE)).toBe(false);
    expect(nav.cookies.has(COOKIE_SESSAO)).toBe(true);
    expect(TABELAS.map(t => contar(banco, t))).toEqual([1, 1, 1, 1, 1]);
    expect(contar(banco, "acessos_pendentes")).toBe(0);

    const conta = await (await nav.pedir("/conta")).json() as any;
    expect(conta.conta).toMatchObject({ apelido, idade: "18_ou_mais" });
    expect(conta.provedores).toEqual(["falso"]);
    expect(conta.consentimentos).toEqual([{ versao_termos: VERSAO_TERMOS, versao_privacidade: VERSAO_PRIVACIDADE, aceito_em: expect.any(String) }]);
    const aparelhos = await (await nav.pedir("/conta/aparelhos")).json() as any[];
    expect(aparelhos).toEqual([expect.objectContaining({ nome: "Chrome no Windows", atual: true })]);

    expect((await nav.json("POST", "/auth/sair", undefined, conta.csrf)).status).toBe(200);
    expect(nav.cookies.has(COOKIE_SESSAO)).toBe(false);
    expect((await nav.pedir("/conta")).status).toBe(401);
    expect(contar(banco, "aparelhos")).toBe(0);

    const de_novo = await entrarFalso(nav, "ana");
    expect(de_novo.searchParams.get("conta")).toBe("entrou");
    expect((await (await nav.pedir("/conta")).json() as any).conta.apelido).toBe(apelido);
    expect(contar(banco, "contas")).toBe(1);
  });

  it("entrar de novo no mesmo navegador mantém o aparelho; outro navegador é outro aparelho, e desconectá-lo derruba a sessão dele", async () => {
    const { app, banco } = montar();
    const a = new Navegador(app), b = new Navegador(app, "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/140.0 Mobile Safari/537.36");
    const csrfA = await criarConta(a);
    await entrarFalso(a, "ana");
    expect(contar(banco, "aparelhos")).toBe(1);
    expect(contar(banco, "sessoes")).toBe(1);
    expect((await entrarFalso(b, "ana")).searchParams.get("conta")).toBe("entrou");
    const aparelhos = await (await a.pedir("/conta/aparelhos")).json() as any[];
    expect(aparelhos.map(x => x.nome).sort()).toEqual(["Chrome no Android", "Chrome no Windows"]);
    const outro = aparelhos.find(x => !x.atual);
    const csrf = (await (await a.pedir("/conta")).json() as any).csrf;
    expect(csrf).not.toBe(csrfA); /* a sessão nova tem csrf novo */
    expect((await a.json("DELETE", `/conta/aparelhos/${outro.id}`, undefined, csrf)).status).toBe(200);
    expect((await b.pedir("/conta")).status).toBe(401);
    expect((await a.pedir("/conta")).status).toBe(200);
    expect((await a.json("DELETE", "/conta/aparelhos/nao-existe", undefined, csrf)).status).toBe(404);
  });

  it("cancelar o primeiro acesso não guarda nada", async () => {
    const { app, banco } = montar();
    const nav = new Navegador(app);
    await entrarFalso(nav, "ana");
    const p = await (await nav.pedir("/conta/primeiro-acesso")).json() as any;
    expect((await nav.json("POST", "/conta/primeiro-acesso/cancelar", undefined, p.csrf)).status).toBe(200);
    expect((await nav.pedir("/conta/primeiro-acesso")).status).toBe(401);
    expect(TABELAS.concat("acessos_pendentes").map(t => contar(banco, t))).toEqual([0, 0, 0, 0, 0, 0]);
  });

  it("o aceite precisa da versão atual, e a idade é uma das duas", async () => {
    const { app } = montar();
    const nav = new Navegador(app);
    await entrarFalso(nav, "ana");
    const p = await (await nav.pedir("/conta/primeiro-acesso")).json() as any;
    expect((await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais", aceite: { termos: "velha", privacidade: VERSAO_PRIVACIDADE } }, p.csrf)).status).toBe(409);
    expect((await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais" }, p.csrf)).status).toBe(409);
    expect((await nav.json("POST", "/conta/primeiro-acesso", { idade: 30, aceite: ACEITE }, p.csrf)).status).toBe(400);
  });
});

describe("os estados de Entrar (CN-10)", () => {
  it("fora da lista: volta com fora_da_lista e nada fica guardado", async () => {
    const { app, banco } = montar();
    const nav = new Navegador(app);
    const volta = await entrarFalso(nav, "bia");
    expect(volta.searchParams.get("conta")).toBe("fora_da_lista");
    expect(nav.cookies.has(COOKIE_PENDENTE)).toBe(false);
    expect(TABELAS.concat("acessos_pendentes").map(t => contar(banco, t))).toEqual([0, 0, 0, 0, 0, 0]);
  });
  it("a lista também vem da tabela", async () => {
    const { app, cfg } = montar();
    cfg.convidados.adicionar("falso:bia");
    expect((await entrarFalso(new Navegador(app), "bia")).searchParams.get("conta")).toBe("primeiro_acesso");
  });
  it("menos de 18: 403 menos_de_18, e nada fica guardado", async () => {
    const { app, banco } = montar();
    const nav = new Navegador(app);
    await entrarFalso(nav, "ana");
    const p = await (await nav.pedir("/conta/primeiro-acesso")).json() as any;
    const r = await nav.json("POST", "/conta/primeiro-acesso", { idade: "menos_de_18", aceite: ACEITE }, p.csrf);
    expect(r.status).toBe(403);
    expect((await r.json() as any).estado).toBe("menos_de_18");
    expect(nav.cookies.has(COOKIE_PENDENTE)).toBe(false);
    expect(nav.cookies.has(COOKIE_SESSAO)).toBe(false);
    expect(TABELAS.concat("acessos_pendentes").map(t => contar(banco, t))).toEqual([0, 0, 0, 0, 0, 0]);
  });
  it("não deu: state sem o cookie, state trocado, state reusado ou o PKCE errado", async () => {
    const { app, cfg } = montar();
    const nav = new Navegador(app);
    expect(new URL((await nav.pedir("/auth/callback?code=x&state=y")).headers.get("location")!).searchParams.get("conta")).toBe("nao_deu");

    /* o state certo no banco, mas o navegador da vítima não tem o cookie dele (o login forjado) */
    const ida = await nav.pedir("/auth/falso");
    const st = new URL(ida.headers.get("location")!).searchParams.get("state")!;
    const vitima = new Navegador(app);
    expect(new URL((await vitima.pedir(`/auth/callback?code=x&state=${st}`)).headers.get("location")!).searchParams.get("conta")).toBe("nao_deu");

    /* o código emitido para outro desafio: o verificador do banco não confere */
    const ida2 = await nav.pedir("/auth/falso");
    const st2 = new URL(ida2.headers.get("location")!).searchParams.get("state")!;
    const falso = cfg.provedores.get("falso") as any;
    const codigo = falso.emitirCodigo({ id: "id-ana", login: "ana" }, desafioPkce("outro-verificador"), `${API}/auth/callback`);
    expect(new URL((await nav.pedir(`/auth/callback?code=${codigo}&state=${st2}`)).headers.get("location")!).searchParams.get("conta")).toBe("nao_deu");
    /* o mesmo state outra vez: já foi usado */
    expect(new URL((await nav.pedir(`/auth/callback?code=${codigo}&state=${st2}`)).headers.get("location")!).searchParams.get("conta")).toBe("nao_deu");
  });
  it("o hash de volta só aceita rota do app", () => {
    expect(destinoSeguro("#/config/conta")).toBe("#/config/conta");
    expect(destinoSeguro("https://mal.example")).toBe("");
    expect(destinoSeguro("#/a?b=<script>")).toBe("");
    expect(destinoSeguro(undefined)).toBe("");
  });
});

describe("o cookie da sessão", () => {
  it("httpOnly, SameSite=Lax, Path=/; sem Secure no local", async () => {
    const { app } = montar();
    const nav = new Navegador(app);
    await criarConta(nav);
    const sc = nav.brutos.find(s => s.startsWith(`${COOKIE_SESSAO}=`))!;
    expect(sc).toMatch(/HttpOnly/);
    expect(sc).toMatch(/SameSite=Lax/);
    expect(sc).toMatch(/Path=\//);
    expect(sc).toMatch(new RegExp(`Max-Age=${DURACAO_SESSAO_MS / 1000}`));
    expect(sc).not.toMatch(/Secure/);
    const oauth = nav.brutos.find(s => s.startsWith("dl_oauth="))!;
    expect(oauth).toMatch(/HttpOnly/);
    expect(oauth).toMatch(/Path=\/auth/);
  });
  it("Secure fora do local", async () => {
    const m = montar();
    const app = criarApp({ gerador: new GeradorFala(null, null), motivoInicial: "", conta: { ...m.cfg, cookieSeguro: true } });
    const nav = new Navegador(app);
    await criarConta(nav);
    for (const nome of [COOKIE_SESSAO, COOKIE_PENDENTE, "dl_oauth"]) expect(nav.brutos.find(s => s.startsWith(`${nome}=`))).toMatch(/Secure/);
  });
  it("o banco guarda só o hash do token, e a sessão expira", async () => {
    const { app, banco, relogio } = montar();
    const nav = new Navegador(app);
    await criarConta(nav);
    const token = nav.cookies.get(COOKIE_SESSAO)!;
    expect(banco.prepare("SELECT 1 FROM sessoes WHERE token_hash = ?").get(token)).toBeUndefined();
    relogio.t += DURACAO_SESSAO_MS + 1;
    expect((await nav.pedir("/conta")).status).toBe(401);
    expect(contar(banco, "sessoes")).toBe(0);
  });
});

describe("o CSRF", () => {
  it("sair, desconectar e apagar pedem o X-CSRF-Token da sessão e a origem certa", async () => {
    const { app, banco } = montar();
    const nav = new Navegador(app);
    const csrf = await criarConta(nav);
    expect((await nav.json("POST", "/auth/sair")).status).toBe(403);
    expect((await nav.json("POST", "/auth/sair", undefined, "errado")).status).toBe(403);
    expect((await nav.json("POST", "/auth/sair", undefined, csrf, { Origin: "https://mal.example" })).status).toBe(403);
    expect((await nav.json("DELETE", "/conta", { confirmar: "apagar" })).status).toBe(403);
    expect((await nav.json("DELETE", "/conta", { confirmar: "apagar" }, csrf, { Origin: "https://mal.example" })).status).toBe(403);
    const ap = (await (await nav.pedir("/conta/aparelhos")).json() as any[])[0].id;
    expect((await nav.json("DELETE", `/conta/aparelhos/${ap}`)).status).toBe(403);
    expect(contar(banco, "contas")).toBe(1);
    expect(contar(banco, "aparelhos")).toBe(1);
    expect((await nav.json("POST", "/auth/sair", undefined, csrf, { Origin: ORIGEM_JOGO })).status).toBe(200);
  });
  it("o primeiro acesso pede o csrf do acesso pendente", async () => {
    const { app, banco } = montar();
    const nav = new Navegador(app);
    await entrarFalso(nav, "ana");
    expect((await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais", aceite: ACEITE })).status).toBe(403);
    expect((await nav.json("POST", "/conta/primeiro-acesso/apelido", { digimon: "Agumon" }, "errado")).status).toBe(403);
    expect(contar(banco, "contas")).toBe(0);
  });
  it("sem sessão é 401, e o corpo que não é JSON leva 415", async () => {
    const { app } = montar();
    const nav = new Navegador(app);
    expect((await nav.json("DELETE", "/conta", { confirmar: "apagar" }, "x")).status).toBe(401);
    expect((await nav.pedir("/conta/dados")).status).toBe(401);
    const csrf = await criarConta(nav);
    const r = await nav.pedir("/conta", { method: "DELETE", body: "confirmar=apagar",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRF-Token": csrf } });
    expect(r.status).toBe(415);
  });
});

describe("o CORS (RC-6: a API em api., o jogo no domínio)", () => {
  it("abre só para a origem do jogo, com credenciais", async () => {
    const { app } = montar();
    const pre = (origem: string) => app.request("/conta", { method: "OPTIONS",
      headers: { Origin: origem, "Access-Control-Request-Method": "DELETE", "Access-Control-Request-Headers": "content-type,x-csrf-token" } });
    const ok = await pre(ORIGEM_JOGO);
    expect(ok.headers.get("access-control-allow-origin")).toBe(ORIGEM_JOGO);
    expect(ok.headers.get("access-control-allow-credentials")).toBe("true");
    expect(ok.headers.get("access-control-allow-headers")?.toLowerCase()).toContain("x-csrf-token");
    const mal = await pre("https://mal.example");
    expect(mal.headers.get("access-control-allow-origin")).toBeNull();
    const get = await app.request("/conta", { headers: { Origin: "https://mal.example" } });
    expect(get.headers.get("access-control-allow-origin")).toBeNull();
  });
});

describe("baixar os meus dados", () => {
  it("o JSON da conta, como anexo, sem e-mail nem token", async () => {
    const { app } = montar();
    const nav = new Navegador(app);
    await criarConta(nav);
    const r = await nav.pedir("/conta/dados");
    expect(r.status).toBe(200);
    expect(r.headers.get("content-disposition")).toMatch(/^attachment; filename="digilab-conta-[A-Za-z]+-\d{4}\.json"$/);
    const texto = await r.text();
    const d = JSON.parse(texto);
    expect(d.formato).toBe("digilab-conta-dados-v1");
    expect(Object.keys(d)).toEqual(["formato", "gerado_em", "conta", "identidades", "consentimentos", "aparelhos", "sessoes", "envios", "sementes", "desafio", "premios", "pontuacoes", "nuvem", "cota_fala", "nao_guardamos"]);
    expect(d.identidades).toEqual([{ provedor: "falso", id_provedor: "id-ana", criada_em: expect.any(String) }]);
    expect(d.aparelhos).toHaveLength(1);
    expect(d.sessoes).toEqual([{ aparelho_id: d.aparelhos[0].id, criada_em: expect.any(String), expira_em: expect.any(String) }]);
    expect(texto).not.toContain(nav.cookies.get(COOKIE_SESSAO)!);
    expect(texto).not.toMatch(/token|csrf/);
  });
});

describe("apagar a conta (CN-5)", () => {
  it("some com tudo, tira o cookie, e entrar de novo é primeiro acesso", async () => {
    const { app, banco } = montar();
    const a = new Navegador(app), b = new Navegador(app);
    const csrf = await criarConta(a);
    await entrarFalso(b, "ana");
    await criarConta(new Navegador(app), "caio");
    expect(TABELAS.map(t => contar(banco, t))).toEqual([2, 2, 2, 3, 3]);
    expect((await a.json("DELETE", "/conta", { confirmar: "talvez" }, csrf)).status).toBe(400);
    const r = await a.json("DELETE", "/conta", { confirmar: "apagar" }, csrf);
    expect(r.status).toBe(200);
    expect(a.cookies.has(COOKIE_SESSAO)).toBe(false);
    /* só a conta do caio fica */
    expect(TABELAS.map(t => contar(banco, t))).toEqual([1, 1, 1, 1, 1]);
    expect(banco.prepare("SELECT 1 FROM identidades WHERE id_provedor = 'id-ana'").get()).toBeUndefined();
    expect((await b.pedir("/conta")).status).toBe(401);
    expect((await entrarFalso(a, "ana")).searchParams.get("conta")).toBe("primeiro_acesso");
  });
});

describe("o Google e o GitHub com um fetch falso", () => {
  const AMBIENTE = { GOOGLE_CLIENT_ID: "g-id", GOOGLE_CLIENT_SECRET: "g-segredo", GITHUB_CLIENT_ID: "h-id", GITHUB_CLIENT_SECRET: "h-segredo" };
  function buscarFalso(perfis: Record<string, unknown>) {
    const pedidos: { url: string; init?: RequestInit }[] = [];
    const buscar: Buscar = async (url, init) => {
      pedidos.push({ url, init });
      const resp = (d: unknown) => new Response(JSON.stringify(d), { status: 200, headers: { "Content-Type": "application/json" } });
      if (url === ProvedorGoogle.TOKEN || url === ProvedorGitHub.TOKEN) return resp({ access_token: "tok", token_type: "bearer" });
      if (url in perfis) return resp(perfis[url]);
      return new Response("{}", { status: 404 });
    };
    return { buscar, pedidos };
  }
  async function loginReal(app: App, nome: "google" | "github") {
    const nav = new Navegador(app);
    const ida = await nav.pedir(`/auth/${nome}?volta=%23/config/conta`);
    expect(ida.status).toBe(302);
    const u = new URL(ida.headers.get("location")!);
    const cb = await nav.pedir(`/auth/callback?code=codigo-do-provedor&state=${u.searchParams.get("state")}`);
    return { nav, autorizar: u, volta: new URL(cb.headers.get("location")!) };
  }

  it("o Google: o endereço com o state e o PKCE S256, a troca com o verificador; o e-mail entra na lista e não se guarda", async () => {
    const email = "Convidada@Exemplo.test";
    const { buscar, pedidos } = buscarFalso({ [ProvedorGoogle.PERFIL]: { sub: "1234567890", email, email_verified: true } });
    const { app, banco } = montar({ ...AMBIENTE, DIGILAB_CONVIDADOS: `email:${email.toLowerCase()}` }, buscar);
    const { nav, autorizar, volta } = await loginReal(app, "google");
    expect(autorizar.origin + autorizar.pathname).toBe(ProvedorGoogle.AUTORIZAR);
    expect(autorizar.searchParams.get("client_id")).toBe("g-id");
    expect(autorizar.searchParams.get("redirect_uri")).toBe(`${API}/auth/callback`);
    expect(autorizar.searchParams.get("code_challenge_method")).toBe("S256");
    expect(autorizar.searchParams.get("scope")).toBe("openid email");
    const corpoToken = new URLSearchParams(String(pedidos[0]!.init!.body));
    expect(corpoToken.get("code")).toBe("codigo-do-provedor");
    expect(desafioPkce(corpoToken.get("code_verifier")!)).toBe(autorizar.searchParams.get("code_challenge"));
    expect(corpoToken.get("client_secret")).toBe("g-segredo");
    expect(volta.searchParams.get("conta")).toBe("primeiro_acesso");

    const p = await (await nav.pedir("/conta/primeiro-acesso")).json() as any;
    expect((await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais", aceite: ACEITE }, p.csrf)).status).toBe(201);
    /* nenhuma tabela guarda o e-mail */
    for (const t of [...TABELAS, "acessos_pendentes", "estados_oauth", "convidados"]) {
      const linhas = JSON.stringify(banco.prepare(`SELECT * FROM ${t}`).all()).toLowerCase();
      expect(linhas).not.toContain("exemplo.test");
    }
    expect(JSON.stringify(await (await nav.pedir("/conta/dados")).json())).not.toContain("xemplo");
  });

  it("o Google sem e-mail verificado não entra pela lista de e-mail", async () => {
    const { buscar } = buscarFalso({ [ProvedorGoogle.PERFIL]: { sub: "1", email: "a@b.test", email_verified: false } });
    const { app } = montar({ ...AMBIENTE, DIGILAB_CONVIDADOS: "email:a@b.test" }, buscar);
    expect((await loginReal(app, "google")).volta.searchParams.get("conta")).toBe("fora_da_lista");
  });

  it("o GitHub: sem escopo, o login entra na lista, e a recusa do provedor volta como nao_deu", async () => {
    const { buscar, pedidos } = buscarFalso({ [ProvedorGitHub.PERFIL]: { id: 42, login: "Convidado" } });
    const { app } = montar({ ...AMBIENTE, DIGILAB_CONVIDADOS: "github:convidado" }, buscar);
    const { autorizar, volta } = await loginReal(app, "github");
    expect(autorizar.origin + autorizar.pathname).toBe(ProvedorGitHub.AUTORIZAR);
    expect(autorizar.searchParams.get("scope")).toBe("");
    expect(autorizar.searchParams.get("code_challenge_method")).toBe("S256");
    expect(new URLSearchParams(String(pedidos[0]!.init!.body)).get("code_verifier")).toBeTruthy();
    expect(volta.searchParams.get("conta")).toBe("primeiro_acesso");

    const recusa: Buscar = async () => new Response(JSON.stringify({ error: "bad_verification_code" }), { status: 200 });
    const { app: app2, banco } = montar({ ...AMBIENTE, DIGILAB_CONVIDADOS: "github:convidado" }, recusa);
    expect((await loginReal(app2, "github")).volta.searchParams.get("conta")).toBe("nao_deu");
    expect(contar(banco, "acessos_pendentes")).toBe(0);
  });
});

describe("as peças", () => {
  it("os Rookies do apelido são os do jogo (web/app/motor/nomes.ts)", () => {
    const texto = readFileSync(new URL("../../web/app/motor/nomes.ts", import.meta.url), "utf8");
    const m = /export const DIGIMON_DA_FORMA: Record<string, \[string, string\]> = (\{.*?\});/.exec(texto);
    const mapa = JSON.parse(m![1]!) as Record<string, [string, string]>;
    const rookies = Object.values(mapa).filter(([, nivel]) => nivel === "Rookie").map(([nome]) => nome);
    expect([...ROOKIES].sort()).toEqual([...new Set(rookies)].sort());
  });
  it("o apelido sorteia de novo se o número já está ocupado", () => {
    const seq = [0, 1000, 0, 1000, 0, 1001];
    const sortear = () => seq.shift()!;
    expect(sortearApelido(a => a === "Agumon#1000", undefined, sortear)).toBe("Agumon#1001");
    expect(() => sortearApelido(() => false, "Greymon")).toThrow(/fora da lista/);
  });
  it("as chaves da lista de convidados", () => {
    expect(normalizarChave("GitHub:Matheus")).toBe("github:matheus");
    expect(normalizarChave("github:id:42")).toBe("github:id:42");
    expect(normalizarChave("email:A@B.test")).toMatch(/^email:[0-9a-f]{64}$/);
    expect(() => normalizarChave("google:pessoa")).toThrow(/Google/);
    expect(() => normalizarChave("orkut:x")).toThrow(/formato/);
    expect(chavesDoPerfil("github", { id: "42", login: "Ana" })).toEqual(["github:id:42", "github:ana"]);
  });
  it("o nome do aparelho sai do User-Agent, curto", () => {
    expect(nomeDoAparelho(UA)).toBe("Chrome no Windows");
    expect(nomeDoAparelho("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605 Version/18.0 Mobile/15E148 Safari/604.1")).toBe("Safari no iOS");
    expect(nomeDoAparelho(undefined)).toBe("aparelho");
  });
  it("a página de teste só existe no local", async () => {
    const { app } = montar();
    expect((await app.request("/dev/conta")).status).toBe(200);
  });
});
