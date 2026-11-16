/* As rotas da conta (CN2, docs/PLANO_V3_CONTA.md seções 2, 4 e 9; as telas 1, 2, 4 e 6 a 7 do docs/PLANO_UX_CONTA.md são do app, depois).

   O login (o navegador vai e volta por navegação, não por fetch):
     GET  /auth/provedores                 [{nome, ligado, motivo}]: o que a tela Entrar mostra
     GET  /auth/:provedor?volta=#/...      302 para o provedor, com o state e o PKCE; o state fica no banco e num cookie (dl_oauth)
     GET  /auth/callback?code&state        confere o state, troca o código e devolve o jogador a DIGILAB_URL_JOGO com ?conta=<estado>:
                                           entrou | primeiro_acesso | fora_da_lista | nao_deu (e o hash de volta)
   O primeiro acesso (o cookie dl_pendente, 15 min; nada fica guardado até "Criar a conta"):
     GET  /conta/primeiro-acesso           {apelido, digimons, idades, versao_termos, versao_privacidade, provedor, csrf}
     POST /conta/primeiro-acesso/apelido   {digimon}: troca o Digimon, o número sai por sorteio
     POST /conta/primeiro-acesso           {idade, aceite: {termos, privacidade}, aparelho?}: cria a conta, ou 403 menos_de_18 (e esquece)
     POST /conta/primeiro-acesso/cancelar  esquece o acesso pendente
   A conta (o cookie dl_sessao):
     GET    /conta                         {conta, provedores, consentimentos, aparelho, csrf}
     GET    /conta/aparelhos               [{id, nome, criado_em, visto_em, atual}]
     DELETE /conta/aparelhos/:id           desconecta o aparelho (as sessões dele saem)
     GET    /conta/dados                   baixar os meus dados (JSON, anexo)
     DELETE /conta                         {confirmar: "apagar"}: apaga a conta e tudo dela, agora (CN-5: em até 30 dias)
     POST   /auth/sair                     sai deste aparelho

   O que muda algo (POST e DELETE em /conta e /auth/sair) pede o cabeçalho X-CSRF-Token (o csrf da sessão ou do acesso pendente) e, se o
   navegador manda Origin, a origem do jogo ou a da API. O CORS abre só para a origem do jogo, com credenciais. */
import { createHash, randomUUID, timingSafeEqual } from "node:crypto";
import type { Context, Hono } from "hono";
import { deleteCookie, getCookie, setCookie } from "hono/cookie";
import { cors } from "hono/cors";
import { ROOKIES, sortearApelido } from "./apelido.ts";
import { transacao } from "./banco.ts";
import type { ConfigConta } from "./config.ts";
import { paginaAutorizarFalso, paginaDevConta } from "./paginas.ts";
import { aleatorio, desafioPkce, ErroProvedor, NOMES_PROVEDOR, ProvedorFalso, type NomeProvedor, type Perfil } from "./provedores.ts";

/* os tempos (PROPOSTO, SEM FONTE) */
export const DURACAO_SESSAO_MS = 30 * 24 * 3600_000;
export const DURACAO_PENDENTE_MS = 15 * 60_000;
export const DURACAO_ESTADO_OAUTH_MS = 10 * 60_000;
export const COOKIE_SESSAO = "dl_sessao", COOKIE_PENDENTE = "dl_pendente", COOKIE_OAUTH = "dl_oauth";
export const IDADES = ["18_ou_mais", "menos_de_18"] as const;
const DESTINO_PADRAO = "";
const LIMITE_CORPO_CONTA = 4 * 1024;

export type EstadoVolta = "entrou" | "primeiro_acesso" | "fora_da_lista" | "nao_deu";

const hash = (s: string): string => createHash("sha256").update(s).digest("hex");
function iguais(a: string, b: string): boolean {
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}
const iso = (ms: number): string => new Date(ms).toISOString();

/** o hash de volta ao jogo: só rota de hash do app (#/...), sem nada que saia da página */
export function destinoSeguro(v: string | undefined): string {
  return v !== undefined && /^#\/[A-Za-z0-9/_-]{0,80}$/.test(v) ? v : DESTINO_PADRAO;
}

/** um nome curto do aparelho pelo User-Agent ("Chrome no Windows"); o User-Agent inteiro não se guarda */
export function nomeDoAparelho(ua: string | undefined): string {
  const s = ua ?? "";
  const nav = /Edg\//.test(s) ? "Edge" : /Firefox\//.test(s) ? "Firefox" : /Chrome\//.test(s) ? "Chrome" : /Safari\//.test(s) ? "Safari" : "";
  const so = /Android/.test(s) ? "Android" : /iPhone|iPad/.test(s) ? "iOS" : /Windows/.test(s) ? "Windows" : /Mac OS X/.test(s) ? "macOS" : /Linux/.test(s) ? "Linux" : "";
  return nav && so ? `${nav} no ${so}` : nav || so || "aparelho";
}

interface Sessao { token_hash: string; conta_id: string; aparelho_id: string; csrf: string; expira_em: number }
interface Pendente { token_hash: string; provedor: NomeProvedor; id_provedor: string; apelido: string; csrf: string; destino: string; expira_em: number }

export function montarRotasConta(app: Hono, cfg: ConfigConta): void {
  const { banco, agora } = cfg;
  const origemApi = new URL(cfg.urlApi).origin;
  const redirectUri = `${cfg.urlApi}/auth/callback`;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store" });
  const opcoesCookie = (maxAgeMs: number, path = "/") =>
    ({ httpOnly: true, secure: cfg.cookieSeguro, sameSite: "Lax" as const, path, maxAge: Math.floor(maxAgeMs / 1000) });

  /* --- o CORS: só a origem do jogo, com o cookie --- */
  const corsConta = cors({ origin: o => (o === cfg.origemJogo ? o : null), credentials: true,
    allowMethods: ["GET", "POST", "DELETE"], allowHeaders: ["Content-Type", "X-CSRF-Token"], maxAge: 600 });
  app.use("/conta", corsConta);
  app.use("/conta/*", corsConta);
  app.use("/auth/*", corsConta);

  /* --- as sessões --- */
  const limparVencidos = () => {
    const t = agora();
    banco.prepare("DELETE FROM sessoes WHERE expira_em <= ?").run(t);
    banco.prepare("DELETE FROM acessos_pendentes WHERE expira_em <= ?").run(t);
    banco.prepare("DELETE FROM estados_oauth WHERE expira_em <= ?").run(t);
  };
  const sessaoDe = (c: Context): Sessao | null => {
    const token = getCookie(c, COOKIE_SESSAO);
    if (!token) return null;
    const s = banco.prepare("SELECT token_hash, conta_id, aparelho_id, csrf, expira_em FROM sessoes WHERE token_hash = ?").get(hash(token)) as Sessao | undefined;
    if (!s) return null;
    if (s.expira_em <= agora()) { banco.prepare("DELETE FROM sessoes WHERE token_hash = ?").run(s.token_hash); return null; }
    banco.prepare("UPDATE aparelhos SET visto_em = ? WHERE id = ?").run(agora(), s.aparelho_id);
    return s;
  };
  const pendenteDe = (c: Context): Pendente | null => {
    const token = getCookie(c, COOKIE_PENDENTE);
    if (!token) return null;
    const p = banco.prepare("SELECT * FROM acessos_pendentes WHERE token_hash = ?").get(hash(token)) as Pendente | undefined;
    return p && p.expira_em > agora() ? p : null;
  };
  /** cria a sessão (e o aparelho, se não vier um da sessão anterior da mesma conta) e põe o cookie */
  const abrirSessao = (c: Context, contaId: string, nomeAparelho: string, aparelhoId?: string): void => {
    const t = agora();
    if (aparelhoId === undefined) {
      aparelhoId = randomUUID();
      banco.prepare("INSERT INTO aparelhos (id, conta_id, nome, criado_em, visto_em) VALUES (?, ?, ?, ?, ?)").run(aparelhoId, contaId, nomeAparelho, t, t);
    } else {
      banco.prepare("UPDATE aparelhos SET visto_em = ? WHERE id = ?").run(t, aparelhoId);
    }
    const token = aleatorio(32);
    banco.prepare("INSERT INTO sessoes (token_hash, conta_id, aparelho_id, csrf, criada_em, expira_em) VALUES (?, ?, ?, ?, ?, ?)")
      .run(hash(token), contaId, aparelhoId, aleatorio(24), t, t + DURACAO_SESSAO_MS);
    setCookie(c, COOKIE_SESSAO, token, opcoesCookie(DURACAO_SESSAO_MS));
  };
  const voltarAoJogo = (c: Context, estado: EstadoVolta, destino: string) => {
    const u = new URL(cfg.urlJogo);
    u.searchParams.set("conta", estado);
    u.hash = destino;
    c.header("Cache-Control", "no-store");
    return c.redirect(u.toString(), 302);
  };

  /* --- o CSRF: nas rotas que mudam algo --- */
  const origemValida = (c: Context): boolean => {
    const o = c.req.header("origin");
    return o === undefined || o === cfg.origemJogo || o === origemApi;
  };
  const csrfValido = (c: Context, esperado: string): boolean => {
    const t = c.req.header("x-csrf-token");
    return origemValida(c) && t !== undefined && iguais(t, esperado);
  };
  const lerCorpo = async (c: Context): Promise<Record<string, unknown> | Response> => {
    const texto = await c.req.text();
    if (Buffer.byteLength(texto, "utf8") > LIMITE_CORPO_CONTA) return json(c, 413, { erro: "corpo grande demais" });
    if (texto === "") return {};
    if (!(c.req.header("content-type") ?? "").startsWith("application/json")) return json(c, 415, { erro: "o corpo é JSON" });
    try {
      const d = JSON.parse(texto) as unknown;
      if (typeof d === "object" && d !== null && !Array.isArray(d)) return d as Record<string, unknown>;
    } catch { /* cai no 400 abaixo */ }
    return json(c, 400, { erro: "o corpo precisa ser um objeto JSON" });
  };
  /** a sessão de uma rota que muda algo: 401 sem sessão, 403 sem o CSRF */
  const sessaoParaMudar = (c: Context): Sessao | Response => {
    const s = sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    if (!csrfValido(c, s.csrf)) return json(c, 403, { erro: "CSRF: falta o X-CSRF-Token certo" });
    return s;
  };
  const pendenteParaMudar = (c: Context): Pendente | Response => {
    const p = pendenteDe(c);
    if (!p) return json(c, 401, { erro: "sem acesso pendente (entre de novo)" });
    if (!csrfValido(c, p.csrf)) return json(c, 403, { erro: "CSRF: falta o X-CSRF-Token certo" });
    return p;
  };

  /* --- o login --- */
  app.get("/auth/provedores", c => json(c, 200, [...cfg.provedores.values()].map(p => {
    const [ligado, motivo] = p.estado();
    return { nome: p.nome, ligado, motivo };
  })));

  /* o callback antes do /auth/:provedor (o Hono responde pela primeira rota registrada que casa) */
  app.get("/auth/callback", async c => {
    const state = c.req.query("state"), codigo = c.req.query("code");
    const cookieState = getCookie(c, COOKIE_OAUTH);
    deleteCookie(c, COOKIE_OAUTH, { path: "/auth", secure: cfg.cookieSeguro });
    if (!state || !cookieState || !iguais(state, cookieState)) return voltarAoJogo(c, "nao_deu", DESTINO_PADRAO);
    const est = banco.prepare("SELECT provedor, verificador, destino, expira_em FROM estados_oauth WHERE state = ?").get(state) as
      { provedor: NomeProvedor; verificador: string; destino: string; expira_em: number } | undefined;
    banco.prepare("DELETE FROM estados_oauth WHERE state = ?").run(state);
    if (!est || est.expira_em <= agora()) return voltarAoJogo(c, "nao_deu", DESTINO_PADRAO);
    const provedor = cfg.provedores.get(est.provedor);
    if (!codigo || !provedor || !provedor.estado()[0]) return voltarAoJogo(c, "nao_deu", est.destino);
    let perfil: Perfil;
    try {
      perfil = await provedor.trocarCodigo({ codigo, verificador: est.verificador, redirectUri });
    } catch (err) {
      if (err instanceof ErroProvedor || err instanceof TypeError) {
        console.log(`  login pelo ${est.provedor} não deu: ${(err as Error).message}`);
        return voltarAoJogo(c, "nao_deu", est.destino);
      }
      throw err;
    }
    const ident = banco.prepare("SELECT conta_id FROM identidades WHERE provedor = ? AND id_provedor = ?").get(est.provedor, perfil.id) as
      { conta_id: string } | undefined;
    if (ident) {
      /* já tem conta: entra; se este navegador já tinha uma sessão da mesma conta, o aparelho continua o mesmo */
      const antiga = sessaoDe(c);
      if (antiga) banco.prepare("DELETE FROM sessoes WHERE token_hash = ?").run(antiga.token_hash);
      abrirSessao(c, ident.conta_id, nomeDoAparelho(c.req.header("user-agent")), antiga?.conta_id === ident.conta_id ? antiga.aparelho_id : undefined);
      return voltarAoJogo(c, "entrou", est.destino);
    }
    if (!cfg.convidados.contem(est.provedor, perfil)) return voltarAoJogo(c, "fora_da_lista", est.destino);
    limparVencidos();
    const token = aleatorio(32);
    const ocupado = (a: string) => banco.prepare("SELECT 1 FROM contas WHERE apelido = ?").get(a) !== undefined;
    banco.prepare("INSERT INTO acessos_pendentes (token_hash, provedor, id_provedor, apelido, csrf, destino, expira_em) VALUES (?, ?, ?, ?, ?, ?, ?)")
      .run(hash(token), est.provedor, perfil.id, sortearApelido(ocupado), aleatorio(24), est.destino, agora() + DURACAO_PENDENTE_MS);
    setCookie(c, COOKIE_PENDENTE, token, opcoesCookie(DURACAO_PENDENTE_MS));
    return voltarAoJogo(c, "primeiro_acesso", est.destino);
  });

  /* o provedor falso: a página de "autorização" do próprio servidor (só se ele estiver ligado) */
  const falso = cfg.provedores.get("falso");
  if (falso instanceof ProvedorFalso) {
    app.get("/auth/falso/autorizar", c => {
      const state = c.req.query("state") ?? "", desafio = c.req.query("code_challenge") ?? "", volta = c.req.query("redirect_uri") ?? "";
      if (volta !== redirectUri || !state || !desafio) return json(c, 400, { erro: "pedido de autorização inválido" });
      return c.html(paginaAutorizarFalso(state, desafio, volta), 200, { "Cache-Control": "no-store" });
    });
    app.post("/auth/falso/autorizar", async c => {
      const f = await c.req.parseBody();
      const state = String(f.state ?? ""), desafio = String(f.code_challenge ?? ""), volta = String(f.redirect_uri ?? "");
      const usuario = String(f.usuario ?? "").trim().toLowerCase();
      if (volta !== redirectUri || !state || !desafio || !/^[a-z0-9_-]{1,32}$/.test(usuario)) return json(c, 400, { erro: "pedido de autorização inválido" });
      const codigo = falso.emitirCodigo({ id: `id-${usuario}`, login: usuario }, desafio, volta);
      const u = new URL(volta);
      u.search = new URLSearchParams({ code: codigo, state }).toString();
      return c.redirect(u.toString(), 302);
    });
  }

  app.get("/auth/:provedor", c => {
    const nome = c.req.param("provedor") as NomeProvedor;
    const provedor = NOMES_PROVEDOR.includes(nome) ? cfg.provedores.get(nome) : undefined;
    if (!provedor) return json(c, 404, { erro: `provedor desconhecido: ${c.req.param("provedor")}` });
    const [ligado, motivo] = provedor.estado();
    if (!ligado) return json(c, 503, { erro: `o login pelo ${nome} está desligado`, motivo });
    limparVencidos();
    const state = aleatorio(24), verificador = aleatorio(48);
    banco.prepare("INSERT INTO estados_oauth (state, provedor, verificador, destino, expira_em) VALUES (?, ?, ?, ?, ?)")
      .run(state, nome, verificador, destinoSeguro(c.req.query("volta")), agora() + DURACAO_ESTADO_OAUTH_MS);
    setCookie(c, COOKIE_OAUTH, state, opcoesCookie(DURACAO_ESTADO_OAUTH_MS, "/auth"));
    c.header("Cache-Control", "no-store");
    return c.redirect(provedor.urlAutorizacao({ state, desafio: desafioPkce(verificador), redirectUri }), 302);
  });

  app.post("/auth/sair", c => {
    const s = sessaoParaMudar(c);
    if (s instanceof Response) return s;
    /* sair desliga este aparelho: o aparelho e as sessões dele saem */
    banco.prepare("DELETE FROM aparelhos WHERE id = ?").run(s.aparelho_id);
    deleteCookie(c, COOKIE_SESSAO, { path: "/", secure: cfg.cookieSeguro });
    return json(c, 200, { saiu: true });
  });

  /* --- o primeiro acesso --- */
  app.get("/conta/primeiro-acesso", c => {
    const p = pendenteDe(c);
    if (!p) return json(c, 401, { erro: "sem acesso pendente (entre de novo)" });
    return json(c, 200, { apelido: p.apelido, digimons: ROOKIES, idades: IDADES, versao_termos: cfg.versaoTermos,
      versao_privacidade: cfg.versaoPrivacidade, provedor: p.provedor, csrf: p.csrf, expira_em: iso(p.expira_em) });
  });

  app.post("/conta/primeiro-acesso/apelido", async c => {
    const p = pendenteParaMudar(c);
    if (p instanceof Response) return p;
    const d = await lerCorpo(c);
    if (d instanceof Response) return d;
    if (typeof d.digimon !== "string" || !ROOKIES.includes(d.digimon)) return json(c, 400, { erro: "digimon fora da lista", digimons: ROOKIES });
    const ocupado = (a: string) => banco.prepare("SELECT 1 FROM contas WHERE apelido = ?").get(a) !== undefined;
    const apelido = sortearApelido(ocupado, d.digimon);
    banco.prepare("UPDATE acessos_pendentes SET apelido = ? WHERE token_hash = ?").run(apelido, p.token_hash);
    return json(c, 200, { apelido });
  });

  app.post("/conta/primeiro-acesso/cancelar", c => {
    const p = pendenteParaMudar(c);
    if (p instanceof Response) return p;
    banco.prepare("DELETE FROM acessos_pendentes WHERE token_hash = ?").run(p.token_hash);
    deleteCookie(c, COOKIE_PENDENTE, { path: "/", secure: cfg.cookieSeguro });
    return json(c, 200, { cancelado: true });
  });

  app.post("/conta/primeiro-acesso", async c => {
    const p = pendenteParaMudar(c);
    if (p instanceof Response) return p;
    const d = await lerCorpo(c);
    if (d instanceof Response) return d;
    if (!IDADES.includes(d.idade as typeof IDADES[number])) return json(c, 400, { erro: "idade: 18_ou_mais ou menos_de_18", idades: IDADES });
    const esquecer = () => {
      banco.prepare("DELETE FROM acessos_pendentes WHERE token_hash = ?").run(p.token_hash);
      deleteCookie(c, COOKIE_PENDENTE, { path: "/", secure: cfg.cookieSeguro });
    };
    if (d.idade === "menos_de_18") {
      /* CN-10: só adultos até a revisão da LGPD. Nada fica guardado */
      esquecer();
      return json(c, 403, { estado: "menos_de_18", erro: "só convidados com 18 anos ou mais, por enquanto" });
    }
    const aceite = d.aceite as Record<string, unknown> | undefined;
    if (typeof aceite !== "object" || aceite === null || aceite.termos !== cfg.versaoTermos || aceite.privacidade !== cfg.versaoPrivacidade)
      return json(c, 409, { erro: "o aceite precisa da versão atual dos termos e da privacidade",
        versao_termos: cfg.versaoTermos, versao_privacidade: cfg.versaoPrivacidade });
    const nomeAparelho = typeof d.aparelho === "string" && d.aparelho.trim() ? d.aparelho.trim().slice(0, 40) : nomeDoAparelho(c.req.header("user-agent"));
    const t = agora(), contaId = randomUUID();
    const r = transacao(banco, () => {
      if (banco.prepare("SELECT 1 FROM identidades WHERE provedor = ? AND id_provedor = ?").get(p.provedor, p.id_provedor) !== undefined)
        return "ja_existe" as const;
      let apelido = p.apelido;
      if (banco.prepare("SELECT 1 FROM contas WHERE apelido = ?").get(apelido) !== undefined)
        apelido = sortearApelido(a => banco.prepare("SELECT 1 FROM contas WHERE apelido = ?").get(a) !== undefined, apelido.split("#")[0]);
      banco.prepare("INSERT INTO contas (id, apelido, criada_em, idade) VALUES (?, ?, ?, '18_ou_mais')").run(contaId, apelido, t);
      banco.prepare("INSERT INTO identidades (provedor, id_provedor, conta_id, criada_em) VALUES (?, ?, ?, ?)").run(p.provedor, p.id_provedor, contaId, t);
      banco.prepare("INSERT INTO consentimentos (conta_id, versao_termos, versao_privacidade, aceito_em) VALUES (?, ?, ?, ?)")
        .run(contaId, cfg.versaoTermos, cfg.versaoPrivacidade, t);
      banco.prepare("DELETE FROM acessos_pendentes WHERE token_hash = ?").run(p.token_hash);
      return apelido;
    });
    deleteCookie(c, COOKIE_PENDENTE, { path: "/", secure: cfg.cookieSeguro });
    if (r === "ja_existe") return json(c, 409, { erro: "esta identidade já tem conta: entre de novo" });
    abrirSessao(c, contaId, nomeAparelho);
    return json(c, 201, { conta: { id: contaId, apelido: r, criada_em: iso(t) }, destino: p.destino });
  });

  /* --- a conta --- */
  const contaDe = (id: string) => banco.prepare("SELECT id, apelido, criada_em, idade FROM contas WHERE id = ?").get(id) as
    { id: string; apelido: string; criada_em: number; idade: string } | undefined;

  app.get("/conta", c => {
    const s = sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const conta = contaDe(s.conta_id)!;
    const provedores = (banco.prepare("SELECT provedor FROM identidades WHERE conta_id = ? ORDER BY provedor").all(s.conta_id) as { provedor: string }[]).map(r => r.provedor);
    const consentimentos = (banco.prepare("SELECT versao_termos, versao_privacidade, aceito_em FROM consentimentos WHERE conta_id = ? ORDER BY aceito_em").all(s.conta_id) as
      { versao_termos: string; versao_privacidade: string; aceito_em: number }[]).map(r => ({ ...r, aceito_em: iso(r.aceito_em) }));
    return json(c, 200, { conta: { id: conta.id, apelido: conta.apelido, criada_em: iso(conta.criada_em), idade: conta.idade },
      provedores, consentimentos, aparelho: s.aparelho_id, csrf: s.csrf });
  });

  app.get("/conta/aparelhos", c => {
    const s = sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const linhas = banco.prepare("SELECT id, nome, criado_em, visto_em FROM aparelhos WHERE conta_id = ? ORDER BY visto_em DESC").all(s.conta_id) as
      { id: string; nome: string; criado_em: number; visto_em: number }[];
    return json(c, 200, linhas.map(a => ({ id: a.id, nome: a.nome, criado_em: iso(a.criado_em), visto_em: iso(a.visto_em), atual: a.id === s.aparelho_id })));
  });

  app.delete("/conta/aparelhos/:id", c => {
    const s = sessaoParaMudar(c);
    if (s instanceof Response) return s;
    const r = banco.prepare("DELETE FROM aparelhos WHERE id = ? AND conta_id = ?").run(c.req.param("id"), s.conta_id);
    if (r.changes === 0) return json(c, 404, { erro: "aparelho desconhecido" });
    if (c.req.param("id") === s.aparelho_id) deleteCookie(c, COOKIE_SESSAO, { path: "/", secure: cfg.cookieSeguro });
    return json(c, 200, { desconectado: c.req.param("id") });
  });

  app.get("/conta/dados", c => {
    const s = sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const conta = contaDe(s.conta_id)!;
    const todos = <T,>(sql: string) => banco.prepare(sql).all(s.conta_id) as T[];
    const dados = {
      formato: "digilab-conta-dados-v1",
      gerado_em: iso(agora()),
      conta: { id: conta.id, apelido: conta.apelido, criada_em: iso(conta.criada_em), idade: conta.idade },
      identidades: todos<{ provedor: string; id_provedor: string; criada_em: number }>(
        "SELECT provedor, id_provedor, criada_em FROM identidades WHERE conta_id = ? ORDER BY criada_em").map(r => ({ ...r, criada_em: iso(r.criada_em) })),
      consentimentos: todos<{ versao_termos: string; versao_privacidade: string; aceito_em: number }>(
        "SELECT versao_termos, versao_privacidade, aceito_em FROM consentimentos WHERE conta_id = ? ORDER BY aceito_em").map(r => ({ ...r, aceito_em: iso(r.aceito_em) })),
      aparelhos: todos<{ id: string; nome: string; criado_em: number; visto_em: number }>(
        "SELECT id, nome, criado_em, visto_em FROM aparelhos WHERE conta_id = ? ORDER BY criado_em").map(r => ({ ...r, criado_em: iso(r.criado_em), visto_em: iso(r.visto_em) })),
      sessoes: todos<{ aparelho_id: string; criada_em: number; expira_em: number }>(
        "SELECT aparelho_id, criada_em, expira_em FROM sessoes WHERE conta_id = ? ORDER BY criada_em").map(r => ({ ...r, criada_em: iso(r.criada_em), expira_em: iso(r.expira_em) })),
      nao_guardamos: ["o nome", "o e-mail", "o lugar", "a fala", "a senha (não há senha)"],
    };
    const arquivo = `digilab-conta-${conta.apelido.replace(/[^A-Za-z0-9_-]/g, "-")}.json`;
    return c.body(JSON.stringify(dados, null, 2), 200, { "Content-Type": "application/json; charset=utf-8",
      "Content-Disposition": `attachment; filename="${arquivo}"`, "Cache-Control": "no-store" });
  });

  app.delete("/conta", async c => {
    const s = sessaoParaMudar(c);
    if (s instanceof Response) return s;
    const d = await lerCorpo(c);
    if (d instanceof Response) return d;
    if (d.confirmar !== "apagar") return json(c, 400, { erro: 'apagar pede {"confirmar": "apagar"}' });
    /* as chaves estrangeiras com ON DELETE CASCADE levam as identidades, os consentimentos, os aparelhos e as sessões */
    transacao(banco, () => banco.prepare("DELETE FROM contas WHERE id = ?").run(s.conta_id));
    deleteCookie(c, COOKIE_SESSAO, { path: "/", secure: cfg.cookieSeguro });
    return json(c, 200, { apagada: true });
  });

  /* a página de teste do fluxo, só no local */
  if (cfg.local) app.get("/dev/conta", c => c.html(paginaDevConta(), 200, { "Cache-Control": "no-store" }));
}
