/* O cliente da conta (src/conta/conta.ts) contra um servidor falso com as rotas do servidor_web/src/conta/rotas.ts: entrar, os estados
   da volta do provedor, o primeiro acesso, o apelido, o perfil, sair e apagar. Sem DOM e sem rede. */
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  CT, VOLTA_DA_CONTA, abrirConta, apagarConta, apelidoDaConta, cancelarPrimeiro, conferirConta, contaLigada, criarConta, desconectar, desligarConta,
  enderecoDosDados, entrarCom, ligarConta, sair, trocarApelido, voltaDaBusca, voltarAEntrar,
} from "../src/conta/conta.ts";

const API = "http://api.teste";
const ROOKIES = ["Agumon", "Guilmon", "Patamon", "Gabumon"];

/** o servidor falso: uma sessao, um acesso pendente e a rede que cai quando se pede */
function servidor() {
  const s = {
    conta: null as null | { apelido: string },
    pendente: null as null | { apelido: string },
    aparelhos: [{ id: "a1", nome: "Chrome no Windows", atual: true }, { id: "a2", nome: "Chrome no Android", atual: false }],
    termos: "rascunho-2026-11",
    fora: false,
    idas: [] as string[],
    pedidos: [] as { metodo: string; caminho: string; csrf: string | null; corpo: unknown }[],
  };
  const json = (status: number, corpo: unknown): Response => new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });
  const buscar = async (url: string, init?: RequestInit): Promise<Response> => {
    if (s.fora) throw new TypeError("fetch failed");
    const caminho = url.slice(API.length), metodo = init?.method ?? "GET", h = (init?.headers ?? {}) as Record<string, string>;
    const corpo = typeof init?.body === "string" ? JSON.parse(init.body) as Record<string, unknown> : undefined;
    s.pedidos.push({ metodo, caminho, csrf: h["X-CSRF-Token"] ?? null, corpo });
    const muda = metodo !== "GET";
    if (caminho === "/auth/provedores") return json(200, [{ nome: "google", ligado: false, motivo: "sem chave" }, { nome: "falso", ligado: true, motivo: "" }]);
    if (caminho === "/conta" && metodo === "GET") return s.conta
      ? json(200, { conta: { id: "c1", apelido: s.conta.apelido, criada_em: "2026-11-12T12:00:00.000Z", idade: "18_ou_mais" }, provedores: ["falso"],
          consentimentos: [{ versao_termos: s.termos, versao_privacidade: s.termos, aceito_em: "2026-11-12T12:00:00.000Z" }], aparelho: "a1", csrf: "csrf-sessao" })
      : json(401, { erro: "sem sessão" });
    if (caminho === "/conta/aparelhos") return s.conta ? json(200, s.aparelhos.map(a => ({ ...a, criado_em: "2026-11-12T12:00:00.000Z", visto_em: "2026-11-17T12:00:00.000Z" }))) : json(401, {});
    if (caminho === "/conta/primeiro-acesso" && metodo === "GET") return s.pendente
      ? json(200, { apelido: s.pendente.apelido, digimons: ROOKIES, idades: ["18_ou_mais", "menos_de_18"], versao_termos: s.termos, versao_privacidade: s.termos, provedor: "falso",
          csrf: "csrf-pendente", expira_em: "2026-11-17T13:00:00.000Z" })
      : json(401, { erro: "sem acesso pendente" });
    if (caminho.startsWith("/conta/primeiro-acesso") && muda) {
      if (!s.pendente) return json(401, { erro: "sem acesso pendente" });
      if (h["X-CSRF-Token"] !== "csrf-pendente") return json(403, { erro: "CSRF" });
      if (caminho.endsWith("/apelido")) { s.pendente.apelido = `${String(corpo?.digimon)}#7777`; return json(200, { apelido: s.pendente.apelido }); }
      if (caminho.endsWith("/cancelar")) { s.pendente = null; return json(200, { cancelado: true }); }
      if (corpo?.idade === "menos_de_18") { s.pendente = null; return json(403, { estado: "menos_de_18", erro: "só adultos" }); }
      const aceite = corpo?.aceite as { termos?: string } | undefined;
      if (aceite?.termos !== s.termos) return json(409, { erro: "o aceite precisa da versão atual", versao_termos: s.termos });
      s.conta = { apelido: s.pendente.apelido }; s.pendente = null;
      return json(201, { conta: { id: "c1", apelido: s.conta.apelido, criada_em: "2026-11-17T12:00:00.000Z" }, destino: VOLTA_DA_CONTA });
    }
    if (muda && !s.conta) return json(401, { erro: "sem sessão" });
    if (muda && h["X-CSRF-Token"] !== "csrf-sessao") return json(403, { erro: "CSRF" });
    if (caminho === "/auth/sair") { s.conta = null; return json(200, { saiu: true }); }
    if (caminho.startsWith("/conta/aparelhos/") && metodo === "DELETE") { s.aparelhos = s.aparelhos.filter(a => a.id !== caminho.split("/").pop()); return json(200, {}); }
    if (caminho === "/conta" && metodo === "DELETE") {
      if (corpo?.confirmar !== "apagar") return json(400, { erro: "confirmar" });
      s.conta = null; return json(200, { apagada: true });
    }
    return json(404, { erro: `rota desconhecida: ${metodo} ${caminho}` });
  };
  return { s, buscar };
}

let srv: ReturnType<typeof servidor>;
beforeEach(() => {
  srv = servidor();
  ligarConta({ api: API + "/", buscar: srv.buscar, ir: u => { srv.s.idas.push(u); } });
});

describe("a chave", () => {
  it("desligada, nada roda", async () => {
    desligarConta();
    expect(contaLigada()).toBe(false);
    await conferirConta();
    expect(CT.passo).toBeNull();
    expect(srv.s.pedidos).toEqual([]);
    await expect(abrirConta()).rejects.toThrow("desligada");
  });
});

describe("entrar", () => {
  it("sem sessão: a tela Entrar com os provedores ligados", async () => {
    await abrirConta();
    expect(CT.passo).toEqual({ tipo: "sem_conta" });
    expect(CT.provedores).toEqual([{ nome: "google", ligado: false }, { nome: "falso", ligado: true }]);
    expect(apelidoDaConta()).toBeNull();
  });
  it("sai para o provedor com a volta na parte Conta, e recusa o provedor desligado", async () => {
    await abrirConta();
    expect(() => entrarCom("google")).toThrow("não está ligado");
    entrarCom("falso");
    expect(CT.passo).toEqual({ tipo: "saindo", provedor: "falso" });
    expect(srv.s.idas).toEqual([`${API}/auth/falso?volta=${encodeURIComponent("#/config/conta")}`]);
    voltarAEntrar();
    expect(CT.passo).toEqual({ tipo: "sem_conta" });
  });
  it("lê só os estados conhecidos do ?conta=", () => {
    expect(voltaDaBusca("?conta=entrou")).toBe("entrou");
    expect(voltaDaBusca("?luta_poc=1&conta=fora_da_lista")).toBe("fora_da_lista");
    expect(voltaDaBusca("?conta=outra_coisa")).toBeNull();
    expect(voltaDaBusca("")).toBeNull();
  });
  it("a volta: não deu e fora da lista ficam como o servidor disse", async () => {
    await abrirConta("nao_deu");
    expect(CT.passo).toEqual({ tipo: "nao_deu" });
    await abrirConta("fora_da_lista");
    expect(CT.passo).toEqual({ tipo: "fora_da_lista" });
  });
  it("a volta diz que entrou e a sessão não veio: não deu", async () => {
    await abrirConta("entrou");
    expect(CT.passo).toEqual({ tipo: "nao_deu" });
  });
  it("o servidor fora: não deu, sem erro alto; a linha dos Ajustes fica sem conta", async () => {
    srv.s.fora = true;
    await abrirConta();
    expect(CT.passo).toEqual({ tipo: "nao_deu" });
    ligarConta({ api: API, buscar: srv.buscar, ir: () => {} });
    await conferirConta();
    expect(CT.passo).toBeNull();
    expect(apelidoDaConta()).toBeNull();
  });
});

describe("o primeiro acesso", () => {
  beforeEach(async () => { srv.s.pendente = { apelido: "Agumon#4821" }; await abrirConta("primeiro_acesso"); });
  it("traz o apelido, a lista e a versão dos termos", () => {
    expect(CT.passo).toEqual({ tipo: "primeiro", dados: { apelido: "Agumon#4821", digimons: ROOKIES, versaoTermos: "rascunho-2026-11", versaoPrivacidade: "rascunho-2026-11", provedor: "falso", turnstile: null } });
  });
  it("troca o Digimon do apelido pela lista fechada, com o CSRF do acesso pendente", async () => {
    await trocarApelido("Gabumon");
    expect(CT.passo).toMatchObject({ tipo: "primeiro", dados: { apelido: "Gabumon#7777" } });
    expect(srv.s.pedidos.at(-1)).toMatchObject({ metodo: "POST", caminho: "/conta/primeiro-acesso/apelido", csrf: "csrf-pendente", corpo: { digimon: "Gabumon" } });
    await expect(trocarApelido("Pikachu")).rejects.toThrow("fora da lista");
  });
  it("cria a conta com a idade e o aceite da versão mostrada, e abre o perfil", async () => {
    await criarConta("18_ou_mais");
    expect(srv.s.pedidos.find(p => p.caminho === "/conta/primeiro-acesso" && p.metodo === "POST")?.corpo)
      .toEqual({ idade: "18_ou_mais", aceite: { termos: "rascunho-2026-11", privacidade: "rascunho-2026-11" } });
    expect(CT.passo?.tipo).toBe("conta");
    expect(apelidoDaConta()).toBe("Agumon#4821");
    expect(CT.ocupado).toBe(false);
  });
  it("menos de 18: o estado da idade, e nada fica no servidor", async () => {
    await criarConta("menos_de_18");
    expect(CT.passo).toEqual({ tipo: "menos_de_18" });
    expect(srv.s.conta).toBeNull();
    expect(srv.s.pendente).toBeNull();
  });
  it("os termos mudaram no meio: pede o aceite de novo, com a versão nova", async () => {
    srv.s.termos = "2026-12";
    await criarConta("18_ou_mais");
    expect(CT.passo).toMatchObject({ tipo: "primeiro", dados: { versaoTermos: "2026-12" } });
    expect(CT.erro).toContain("termos mudaram");
    expect(srv.s.conta).toBeNull();
  });
  it("menos de 18 e depois Entrar: a lista dos provedores vem do servidor", async () => {
    await criarConta("menos_de_18");
    expect(CT.provedores).toEqual([]);
    voltarAEntrar();
    await vi.waitFor(() => expect(CT.passo).toEqual({ tipo: "sem_conta" }));
    expect(CT.provedores.filter(p => p.ligado)).toEqual([{ nome: "falso", ligado: true }]);
  });
  it("cancelar não cria nada e volta à tela Entrar", async () => {
    await cancelarPrimeiro();
    expect(CT.passo).toEqual({ tipo: "sem_conta" });
    expect(srv.s.pendente).toBeNull();
    expect(srv.s.conta).toBeNull();
  });
  it("o servidor fora no meio: uma frase na tela, e o passo não muda", async () => {
    srv.s.fora = true;
    await criarConta("18_ou_mais");
    expect(CT.erro).toBe("Sem resposta do servidor. Nada mudou.");
    expect(CT.passo?.tipo).toBe("primeiro");
    expect(CT.ocupado).toBe(false);
  });
  it("recarregar no meio do primeiro acesso volta a ele", async () => {
    ligarConta({ api: API, buscar: srv.buscar, ir: () => {} });
    await abrirConta();
    expect(CT.passo?.tipo).toBe("primeiro");
  });
});

describe("o perfil", () => {
  beforeEach(async () => { srv.s.conta = { apelido: "Patamon#1234" }; await abrirConta("entrou"); });
  it("traz o apelido, o provedor, o aceite e os aparelhos", () => {
    expect(CT.passo).toEqual({ tipo: "conta", conta: { apelido: "Patamon#1234", criadaEm: Date.parse("2026-11-12T12:00:00.000Z"), provedores: ["falso"],
      aceitoEm: Date.parse("2026-11-12T12:00:00.000Z"), aparelhos: [
        { id: "a1", nome: "Chrome no Windows", vistoEm: Date.parse("2026-11-17T12:00:00.000Z"), atual: true },
        { id: "a2", nome: "Chrome no Android", vistoEm: Date.parse("2026-11-17T12:00:00.000Z"), atual: false }] } });
    expect(enderecoDosDados()).toBe(`${API}/conta/dados`);
  });
  it("a linha dos Ajustes pergunta uma vez só", async () => {
    const antes = srv.s.pedidos.length;
    await conferirConta();
    expect(srv.s.pedidos.length).toBe(antes);
    expect(apelidoDaConta()).toBe("Patamon#1234");
  });
  it("desconecta outro aparelho com o CSRF da sessão; o daqui sai pelo Sair", async () => {
    await desconectar("a2");
    expect(srv.s.pedidos.at(-1)).toMatchObject({ metodo: "DELETE", caminho: "/conta/aparelhos/a2", csrf: "csrf-sessao" });
    expect(CT.passo).toMatchObject({ tipo: "conta", conta: { aparelhos: [{ id: "a1" }] } });
    await expect(desconectar("a1")).rejects.toThrow("Sair");
    await expect(desconectar("a9")).rejects.toThrow("desconhecido");
  });
  it("sair volta à tela Entrar", async () => {
    await sair();
    expect(CT.passo).toEqual({ tipo: "sem_conta" });
    expect(srv.s.conta).toBeNull();
    expect(apelidoDaConta()).toBeNull();
  });
  it("apagar manda a confirmação e mostra que apagou", async () => {
    await apagarConta();
    expect(srv.s.pedidos.at(-1)).toMatchObject({ metodo: "DELETE", caminho: "/conta", csrf: "csrf-sessao", corpo: { confirmar: "apagar" } });
    expect(CT.passo).toEqual({ tipo: "apagada" });
    expect(srv.s.conta).toBeNull();
  });
  it("a sessão acabou no meio: volta à tela Entrar com a frase", async () => {
    srv.s.conta = null;
    await apagarConta();
    expect(CT.passo).toEqual({ tipo: "sem_conta" });
    expect(CT.erro).toContain("sessão acabou");
  });
  it("o servidor fora ao sair: a conta continua na tela", async () => {
    srv.s.fora = true;
    await sair();
    expect(CT.passo?.tipo).toBe("conta");
    expect(CT.erro).toBe("Sem resposta do servidor. Nada mudou.");
  });
  it("as ações fora do passo certo levantam erro", async () => {
    await expect(criarConta("18_ou_mais")).rejects.toThrow("primeiro acesso");
    await sair();
    await expect(sair()).rejects.toThrow("conta aberta");
    await expect(apagarConta()).rejects.toThrow("conta aberta");
  });
});
