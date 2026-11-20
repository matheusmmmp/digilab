/* T1 do tema dos menus (docs/TAREFA_V2_TEMA_MENUS.md §4): a pele e preferencia de tela. Sem DOM (vitest em node): o <html>, o
   endereco e o localStorage sao trocados por objetos simples, e o modulo e recarregado a cada caso (o estado dele e de modulo). */
import { afterEach, describe, expect, it, vi } from "vitest";

type Mod = typeof import("../src/pele.ts");
const html = { dataset: {} as Record<string, string> };

/** carrega pele.ts com o endereco e o armazenamento dados; armazenamento null = sem localStorage (lanca, como no modo privado) */
async function carregar(busca: string, guardado: Record<string, string> | null): Promise<{ m: Mod; guardado: Record<string, string> | null }> {
  vi.resetModules();
  html.dataset = {};
  vi.stubGlobal("document", { documentElement: html });
  vi.stubGlobal("location", { search: busca });
  vi.stubGlobal("localStorage", guardado === null ? {
    getItem: () => { throw new Error("sem armazenamento"); }, setItem: () => { throw new Error("sem armazenamento"); },
  } : { getItem: (k: string) => guardado[k] ?? null, setItem: (k: string, v: string) => { guardado[k] = v; } });
  return { m: await import("../src/pele.ts"), guardado };
}
afterEach(() => { vi.unstubAllGlobals(); });

describe("pele.ts", () => {
  it("padrao Holografico (vidro), com data-pele sempre no <html>, e os nomes da tela sem XCOM", async () => {
    const { m } = await carregar("", {});
    m.iniciarPele();
    expect(m.PELE_PADRAO).toBe("vidro");
    expect(m.peleAtual()).toBe("vidro");
    expect(html.dataset.pele).toBe("vidro");
    expect(m.NOME_PELE).toEqual({ xcom: "Militar", vidro: "Sci-fi", estencil: "Estêncil", zine: "Zine" });
    /* a ordem dos cartoes: o padrao primeiro; a Estencil (PE1 das peles de rua) por ultimo e em previa */
    expect(m.PELES).toEqual(["vidro", "xcom", "estencil", "zine"]);
    expect(m.PELES_EM_PREVIA).toEqual(["estencil", "zine"]);
    expect(Object.values(m.NOME_PELE).join(" ")).not.toMatch(/xcom/i);
  });
  it("chave propria ao lado da do save; a escolha grava e vale ao recarregar", async () => {
    const { m, guardado } = await carregar("", {});
    expect(m.CHAVE_PELE).toBe("digilab-web-v21-sprites-pele");
    m.iniciarPele();
    m.escolherPele("xcom");
    expect(html.dataset.pele).toBe("xcom");
    expect(guardado).toEqual({ "digilab-web-v21-sprites-pele": "xcom" });
    const outra = await carregar("", guardado);
    outra.m.iniciarPele();
    expect(outra.m.peleAtual()).toBe("xcom");
    expect(html.dataset.pele).toBe("xcom");
  });
  it("?pele= sobrepoe a escolha gravada sem gravar", async () => {
    const { m, guardado } = await carregar("?pele=vidro", { "digilab-web-v21-sprites-pele": "xcom" });
    m.iniciarPele();
    expect(m.peleAtual()).toBe("vidro");
    expect(html.dataset.pele).toBe("vidro");
    expect(guardado).toEqual({ "digilab-web-v21-sprites-pele": "xcom" });
    const xcom = await carregar("?tema=claro&pele=xcom", {});
    xcom.m.iniciarPele();
    expect(xcom.m.peleAtual()).toBe("xcom");
    expect(xcom.guardado).toEqual({});
  });
  it("valor invalido no endereco ou no armazenamento cai no que vem depois (gravado, depois o padrao)", async () => {
    const a = await carregar("?pele=XCOM", { "digilab-web-v21-sprites-pele": "xcom" });
    a.m.iniciarPele();
    expect(a.m.peleAtual()).toBe("xcom");
    const b = await carregar("?pele=claro", { "digilab-web-v21-sprites-pele": "militar" });
    b.m.iniciarPele();
    expect(b.m.peleAtual()).toBe("vidro");
    expect(html.dataset.pele).toBe("vidro");
  });
  it("sem armazenamento: o padrao, e escolher troca a pele na hora sem levantar erro", async () => {
    const { m } = await carregar("", null);
    m.iniciarPele();
    expect(m.peleAtual()).toBe("vidro");
    m.escolherPele("xcom");
    expect(m.peleAtual()).toBe("xcom");
    expect(html.dataset.pele).toBe("xcom");
  });
  it("a Estencil entra pelo endereco e pela escolha; um id desconhecido cai no padrao", async () => {
    const est = await carregar("?pele=estencil", {});
    est.m.iniciarPele();
    expect(est.m.peleAtual()).toBe("estencil");
    expect(html.dataset.pele).toBe("estencil");
    expect(est.guardado).toEqual({});
    const esc = await carregar("", {});
    esc.m.iniciarPele();
    esc.m.escolherPele("estencil");
    expect(esc.guardado).toEqual({ "digilab-web-v21-sprites-pele": "estencil" });
    const volta = await carregar("", esc.guardado);
    volta.m.iniciarPele();
    expect(volta.m.peleAtual()).toBe("estencil");
    /* o Zine (a unica pele clara) entra do mesmo jeito */
    const zn = await carregar("?pele=zine", {});
    zn.m.iniciarPele();
    expect(zn.m.peleAtual()).toBe("zine");
    expect(html.dataset.pele).toBe("zine");
    expect(zn.guardado).toEqual({});
    for (const ruim of ["?pele=arcade", "?pele=", "?pele=Estencil", "?pele=Zine"]) {
      const r = await carregar(ruim, { "digilab-web-v21-sprites-pele": "arcade" });
      r.m.iniciarPele();
      expect(r.m.peleAtual(), ruim).toBe("vidro");
    }
  });
});
