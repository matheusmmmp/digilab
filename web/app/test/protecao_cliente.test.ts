/* O cliente da proteção (CN4) com a chave ligada: as URLs assinadas dos assets (src/protecao/assets.ts) contra um servidor falso com as
   rotas de servidor_web/src/protecao/rotas.ts; o Turnstile na criação da conta (src/conta/conta.ts); e a fala que vai à API com o cookie.
   A chave desligada está no test/assets_desligados.test.ts (o gabarito). Sem DOM e sem rede. */
import { afterEach, describe, expect, it, vi } from "vitest";
import { assinarAsset, buscarAsset, caminhoDoAsset, CAMINHOS_POR_PEDIDO, ligarAssets, MARGEM_MS, srcDoAsset, type AmbienteAssets } from "../src/protecao/assets.ts";
import { CT, abrirConta, criarConta, desligarConta, ligarConta, tentativaTurnstile } from "../src/conta/conta.ts";

const API = "http://api.teste";
const PAGINA = "http://127.0.0.1:8765/v1/web/dist/";
const json = (status: number, corpo: unknown): Response => new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });

/** o servidor falso dos assets: assina com "?verify=<hora>-x", e só com a sessão ou o visitante */
function servidorAssets(opcoes: { sessao?: boolean; chaveSite?: string | null } = {}) {
  const s = { sessao: opcoes.sessao ?? true, visitante: false, relogio: 1_000_000, pedidos: [] as { caminho: string; corpo: any; credentials?: string }[],
    tokens: [] as [string, string][] };
  const buscar = async (url: string, init?: RequestInit): Promise<Response> => {
    const caminho = url.slice(API.length), corpo = JSON.parse(String(init?.body ?? "{}"));
    s.pedidos.push({ caminho, corpo, credentials: init?.credentials });
    if (caminho === "/assets/visitante") {
      if (opcoes.chaveSite && corpo.turnstile !== "token-bom") return json(403, { erro: "o Turnstile não passou", motivo: "nao_passou" });
      s.visitante = true;
      return json(200, { visitante: true });
    }
    if (caminho === "/assets/assinar") {
      if (!s.sessao && !s.visitante) return json(401, { erro: "sem sessão e sem visitante", turnstile: opcoes.chaveSite ?? null });
      const urls = Object.fromEntries((corpo.caminhos as string[]).map(c => [c, `${API}/assets${c}?verify=${s.relogio}-x`]));
      return json(200, { urls, validade_s: 600, expira_em: "x" });
    }
    return json(404, {});
  };
  const amb: AmbienteAssets = { api: API, buscar, base: () => PAGINA, agora: () => s.relogio,
    turnstile: async (chave, acao) => { s.tokens.push([chave, acao]); return "token-bom"; } };
  return { s, amb };
}

afterEach(() => { ligarAssets(null); vi.unstubAllGlobals(); vi.unstubAllEnvs(); vi.resetModules(); });

describe("as URLs assinadas no jogo", () => {
  it("o caminho é o que vem depois de /Assets", () => {
    expect(caminhoDoAsset("../../../Assets/sons/mapa.json", PAGINA)).toBe("/sons/mapa.json");
    expect(caminhoDoAsset("http://127.0.0.1:8765/Assets/digilab_atlas_up_pecas.png", PAGINA)).toBe("/digilab_atlas_up_pecas.png");
    expect(caminhoDoAsset("../../../Assets/evolucao_up/pacotes/zero2.bin?x=1", PAGINA)).toBe("/evolucao_up/pacotes/zero2.bin");
    expect(() => caminhoDoAsset("/enfeites/tv.glb", PAGINA)).toThrow(/fora da pasta Assets/);
  });

  it("junta os pedidos do mesmo instante num só, com o cookie, e guarda a URL até perto de vencer", async () => {
    const { s, amb } = servidorAssets();
    ligarAssets(amb);
    const [a, b, c] = await Promise.all([assinarAsset("../../../Assets/sons/mapa.json"), assinarAsset("../../../Assets/sons/a.ogg"),
      assinarAsset("../../../Assets/sons/mapa.json")]);
    expect(a).toBe(`${API}/assets/sons/mapa.json?verify=1000000-x`);
    expect(c).toBe(a);
    expect(b).toBe(`${API}/assets/sons/a.ogg?verify=1000000-x`);
    expect(s.pedidos).toEqual([{ caminho: "/assets/assinar", corpo: { caminhos: ["/sons/mapa.json", "/sons/a.ogg"] }, credentials: "include" }]);
    /* a guardada serve até 600 s menos a margem; depois, pede de novo */
    s.relogio += 600_000 - MARGEM_MS - 1;
    expect(await assinarAsset("../../../Assets/sons/mapa.json")).toBe(a);
    expect(s.pedidos).toHaveLength(1);
    s.relogio += 1;
    expect(await assinarAsset("../../../Assets/sons/mapa.json")).not.toBe(a);
    expect(s.pedidos).toHaveLength(2);
  });

  it("mais caminhos que o teto vão em mais de um pedido", async () => {
    const { s, amb } = servidorAssets();
    ligarAssets(amb);
    const n = CAMINHOS_POR_PEDIDO + 3;
    const urls = await Promise.all(Array.from({ length: n }, (_, i) => assinarAsset(`../../../Assets/sons/${i}.ogg`)));
    expect(urls).toHaveLength(n);
    expect(s.pedidos.map(p => p.corpo.caminhos.length)).toEqual([CAMINHOS_POR_PEDIDO, 3]);
  });

  it("sem a sessão: vira visitante pelo Turnstile (a chave que o servidor mandou) e tenta de novo", async () => {
    const { s, amb } = servidorAssets({ sessao: false, chaveSite: "1x00000000000000000000AA" });
    ligarAssets(amb);
    expect(await assinarAsset("../../../Assets/sons/mapa.json")).toMatch(/verify=/);
    expect(s.tokens).toEqual([["1x00000000000000000000AA", "visitante"]]);
    expect(s.pedidos.map(p => p.caminho)).toEqual(["/assets/assinar", "/assets/visitante", "/assets/assinar"]);
    expect(s.pedidos[1]!.corpo).toEqual({ turnstile: "token-bom" });
  });

  it("sem a sessão e sem o Turnstile (o local): vira visitante sem token", async () => {
    const { s, amb } = servidorAssets({ sessao: false, chaveSite: null });
    ligarAssets(amb);
    await assinarAsset("../../../Assets/sons/mapa.json");
    expect(s.tokens).toEqual([]);
    expect(s.pedidos[1]).toMatchObject({ caminho: "/assets/visitante", corpo: {} });
  });

  it("o servidor que recusa falha alto (quem carrega o asset mostra o aviso)", async () => {
    const { amb } = servidorAssets();
    ligarAssets({ ...amb, buscar: async () => json(503, { erro: "as URLs assinadas estão desligadas" }) });
    await expect(assinarAsset("../../../Assets/sons/mapa.json")).rejects.toThrow(/503/);
  });

  it("buscarAsset e srcDoAsset usam a URL assinada; a imagem pede o CORS", async () => {
    const { amb } = servidorAssets();
    ligarAssets(amb);
    const buscados: unknown[][] = [];
    vi.stubGlobal("fetch", async (...a: unknown[]) => { buscados.push(a); return new Response("ok"); });
    await buscarAsset("../../../Assets/evolucao_up/mapa.json");
    expect(buscados).toEqual([[`${API}/assets/evolucao_up/mapa.json?verify=1000000-x`]]);
    expect(await srcDoAsset("../../../Assets/digilab_atlas_up_clipes.png")).toEqual({ src: `${API}/assets/digilab_atlas_up_clipes.png?verify=1000000-x`, crossOrigin: "anonymous" });
  });

  it("desligada (sem ambiente e sem a chave no build), assinar falha alto e srcDoAsset devolve o mesmo", async () => {
    expect(() => assinarAsset("../../../Assets/sons/mapa.json")).toThrow(/desligadas/);
    expect(await srcDoAsset("x.png")).toEqual({ src: "x.png", crossOrigin: null });
  });
});

describe("o Turnstile na criação da conta", () => {
  function servidorConta(passa: boolean) {
    const pedidos: any[] = [];
    let conta = false;
    const buscar = async (url: string, init?: RequestInit): Promise<Response> => {
      const caminho = url.slice(API.length), metodo = init?.method ?? "GET", corpo = init?.body ? JSON.parse(String(init.body)) : undefined;
      pedidos.push({ metodo, caminho, corpo });
      if (caminho === "/auth/provedores") return json(200, [{ nome: "falso", ligado: true }]);
      if (caminho === "/conta" && metodo === "GET") return conta
        ? json(200, { conta: { id: "c1", apelido: "Agumon#1", criada_em: "2026-11-20T12:00:00.000Z" }, provedores: ["falso"], consentimentos: [], csrf: "c" })
        : json(401, {});
      if (caminho === "/conta/aparelhos") return json(200, []);
      if (caminho === "/conta/primeiro-acesso" && metodo === "GET") return json(200, { apelido: "Agumon#1", digimons: ["Agumon"], versao_termos: "v",
        versao_privacidade: "v", provedor: "falso", csrf: "p", turnstile: "1x00000000000000000000AA" });
      if (caminho === "/conta/primeiro-acesso" && metodo === "POST") {
        if (!passa || corpo.turnstile !== "token") return json(403, { estado: "turnstile", erro: "o Turnstile não passou", motivo: "nao_passou" });
        conta = true;
        return json(201, { conta: { id: "c1" } });
      }
      return json(404, {});
    };
    return { pedidos, buscar };
  }

  it("a chave do site vem no primeiro acesso, e o token vai no pedido", async () => {
    const srv = servidorConta(true);
    ligarConta({ api: API, buscar: srv.buscar, ir: () => { /* nada */ } });
    await abrirConta("primeiro_acesso");
    expect(CT.passo).toMatchObject({ tipo: "primeiro", dados: { turnstile: "1x00000000000000000000AA" } });
    await expect(criarConta("18_ou_mais")).rejects.toThrow(/token do Turnstile/);
    await criarConta("18_ou_mais", "token");
    expect(srv.pedidos.find(p => p.metodo === "POST")?.corpo).toMatchObject({ idade: "18_ou_mais", turnstile: "token" });
    expect(CT.passo?.tipo).toBe("conta");
    desligarConta();
  });

  it("o token que não passa: o erro na tela, o primeiro acesso fica, e o widget volta", async () => {
    const srv = servidorConta(false);
    ligarConta({ api: API, buscar: srv.buscar, ir: () => { /* nada */ } });
    await abrirConta("primeiro_acesso");
    const antes = tentativaTurnstile();
    await criarConta("18_ou_mais", "token");
    expect(CT.passo?.tipo).toBe("primeiro");
    expect(CT.erro).toBe("A verificação contra robôs não passou. Tente de novo.");
    expect(tentativaTurnstile()).toBe(antes + 1);
    desligarConta();
  });
});

describe("a fala com a proteção ligada", () => {
  it("vai ao servidor da conta, com o cookie", async () => {
    vi.stubEnv("VITE_DIGILAB_API", API + "/");
    vi.stubEnv("VITE_DIGILAB_PROTECAO", "1");
    const buscados: [string, RequestInit][] = [];
    vi.stubGlobal("fetch", async (u: string, i: RequestInit) => { buscados.push([u, i]); return json(200, { ativo: true, texto: "oi", fonte: "llm" }); });
    vi.resetModules();
    const fala = await import("../src/fala.ts");
    await fala.verificarLLM();
    fala.FALA_LLM.on = true;
    fala.falaLLM({ origem: "vida", acao: "comer" }, "adulto", 0.5);
    await new Promise(r => setTimeout(r, 0));
    expect(buscados.map(([u, i]) => [u, i.credentials])).toEqual([[`${API}/api/fala/status`, "include"], [`${API}/api/fala`, "include"]]);
  });
});
