/* O mapa e a camera do habitat (src/habitat.ts): preferencia de tela, como a pele. Sem DOM (vitest em node): o endereco e o
   localStorage sao objetos simples, e o modulo e recarregado a cada caso (o estado dele e de modulo). A troca na tela (a cena religando
   com o jogo rodando) e conferida no navegador; os cartoes, por renderToStaticMarkup. */
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";

type Mod = typeof import("../src/habitat.ts");
const CHAVE = "digilab-web-v21-sprites-habitat";

async function carregar(busca: string, guardado: Record<string, string> | null): Promise<{ m: Mod; guardado: Record<string, string> | null }> {
  vi.resetModules();
  vi.stubGlobal("location", { search: busca });
  vi.stubGlobal("localStorage", guardado === null ? {
    getItem: () => { throw new Error("sem armazenamento"); }, setItem: () => { throw new Error("sem armazenamento"); },
  } : { getItem: (k: string) => guardado[k] ?? null, setItem: (k: string, v: string) => { guardado[k] = v; } });
  return { m: await import("../src/habitat.ts"), guardado };
}
afterEach(() => { vi.unstubAllGlobals(); });

describe("habitat.ts", () => {
  it("padrao: a ilha com a camera de tras, numa chave propria ao lado da do save", async () => {
    const { m } = await carregar("", {});
    m.iniciarHabitat(false);
    expect(m.CHAVE_HABITAT).toBe(CHAVE);
    expect(m.habitatAtual()).toEqual({ mapa: "ilha", camera: "atras", visual: "normal", controle: "livre" });
  });
  it("os mapas com assets fora do repositorio so aparecem no dev", async () => {
    const { m } = await carregar("", {});
    expect(m.mapasDisponiveis(false)).toEqual(["ilha", "voxel"]);
    expect(m.mapasDisponiveis(true)).toEqual(["ilha", "voxel", "floresta", "cassette"]);
    /* no build, um floresta gravado (de uma sessao do dev) ou no endereco cai na ilha */
    const b = await carregar("?mapa=cassette", { [CHAVE]: JSON.stringify({ mapa: "floresta", camera: "lateral", visual: "normal" }) });
    b.m.iniciarHabitat(false);
    expect(b.m.habitatAtual()).toEqual({ mapa: "ilha", camera: "lateral", visual: "normal", controle: "livre" });
  });
  it("escolher grava e vale ao recarregar; ?mapa= e ?camera= sobrepoem sem gravar", async () => {
    const { m, guardado } = await carregar("", {});
    m.iniciarHabitat(true);
    m.escolherMapa("cassette");
    m.escolherCamera("lateral");
    m.escolherVisual("gba-hd");
    expect(JSON.parse(guardado![CHAVE])).toEqual({ mapa: "cassette", camera: "lateral", visual: "gba-hd", controle: "livre" });
    const outra = await carregar("", guardado);
    outra.m.iniciarHabitat(true);
    expect(outra.m.habitatAtual()).toEqual({ mapa: "cassette", camera: "lateral", visual: "gba-hd", controle: "livre" });
    const end = await carregar("?mapa=voxel&camera=atras&visual=hd-2d", guardado);
    end.m.iniciarHabitat(true);
    expect(end.m.habitatAtual()).toEqual({ mapa: "voxel", camera: "atras", visual: "hd-2d", controle: "livre" });
    expect(JSON.parse(end.guardado![CHAVE])).toEqual({ mapa: "cassette", camera: "lateral", visual: "gba-hd", controle: "livre" });
  });
  it("o controle da camera: livre por padrao, fixa grava e vale ao recarregar; ?controle= sobrepoe sem gravar", async () => {
    const { m, guardado } = await carregar("", {});
    m.iniciarHabitat(true);
    expect(m.habitatAtual().controle).toBe("livre");
    m.escolherControle("fixa");
    expect(JSON.parse(guardado![CHAVE]).controle).toBe("fixa");
    const outra = await carregar("", guardado);
    outra.m.iniciarHabitat(true);
    expect(outra.m.habitatAtual().controle).toBe("fixa");
    const end = await carregar("?controle=livre", guardado);
    end.m.iniciarHabitat(true);
    expect(end.m.habitatAtual().controle).toBe("livre");
    expect(JSON.parse(end.guardado![CHAVE]).controle).toBe("fixa");
  });
  it("valor invalido ou lixo no armazenamento: o padrao; sem armazenamento, escolher troca sem erro", async () => {
    const a = await carregar("?mapa=lua&camera=cima&visual=snes", { [CHAVE]: "{nao e json" });
    a.m.iniciarHabitat(true);
    expect(a.m.habitatAtual()).toEqual({ mapa: "ilha", camera: "atras", visual: "normal", controle: "livre" });
    const b = await carregar("", null);
    b.m.iniciarHabitat(true);
    b.m.escolherMapa("voxel");
    expect(b.m.habitatAtual().mapa).toBe("voxel");
  });
  it("um mapa que nao carregou volta para a ilha sem mexer na escolha gravada; escolher de novo tenta outra vez", async () => {
    const { m, guardado } = await carregar("", {});
    m.iniciarHabitat(true);
    m.escolherMapa("floresta");
    m.voltarParaIlha("floresta");
    expect(m.habitatAtual()).toEqual({ mapa: "ilha", camera: "atras", visual: "normal", controle: "livre" });
    expect(m.habitatEscolhido().mapa).toBe("floresta");
    expect(m.mapaCaido()).toBe("floresta");
    expect(JSON.parse(guardado![CHAVE]).mapa).toBe("floresta");
    m.voltarParaIlha("ilha");
    expect(m.mapaCaido()).toBe("floresta");
    m.escolherMapa("floresta");
    expect(m.habitatAtual().mapa).toBe("floresta");
    expect(m.mapaCaido()).toBeNull();
  });
});

describe("EscolhaHabitat", () => {
  it("quatro radiogroups rotulados (mapa, camera, controle da camera e visual), so o escolhido na ordem de Tab; desligados para os pets sem mundo", async () => {
    const { m } = await carregar("", {});
    m.iniciarHabitat(true);
    m.escolherMapa("voxel");
    const { EscolhaHabitat } = await import("../src/telas/config/EscolhaHabitat.tsx");
    const s = renderToStaticMarkup(h(EscolhaHabitat, { temMundo: true }));
    expect(s).toContain('role="radiogroup" aria-labelledby="cfg-mapa"');
    expect(s).toContain('role="radiogroup" aria-labelledby="cfg-camera"');
    expect(s).toContain('role="radiogroup" aria-labelledby="cfg-controle"');
    expect(s).toContain('class="mc-opcoes mc-opcoes--3" role="radiogroup" aria-labelledby="cfg-visual"');
    expect(s.match(/role="radio"/g)).toHaveLength(m.mapasDisponiveis().length + 2 + 2 + 3);
    expect(s).toMatch(/role="radio" aria-checked="true" tabindex="0" class="mc-opcao"><b>Normal<\/b>/);
    expect(s).toMatch(/role="radio" aria-checked="true" tabindex="0" class="mc-opcao"><b>Voxel<\/b>/);
    expect(s).toMatch(/role="radio" aria-checked="true" tabindex="0" class="mc-opcao"><b>Atrás<\/b>/);
    expect(s).not.toContain("disabled");
    const sala = renderToStaticMarkup(h(EscolhaHabitat, { temMundo: false }));
    expect(sala.match(/disabled=""/g)).toHaveLength(m.mapasDisponiveis().length + 2 + 2 + 3);
    expect(sala).toContain("fica na sala");
  });
});

describe("Ajustes > Visual", () => {
  it("a subarea Visual junta a pele, o tema, o mapa, a camera e o visual; #/config/aparencia leva a ela", async () => {
    const { configDoEndereco } = await import("../src/rotas.ts");
    expect(configDoEndereco("#/config/visual")).toBe("visual");
    expect(configDoEndereco("#/config/aparencia")).toBe("visual");
    const { m } = await carregar("", {});
    m.iniciarHabitat(true);
    m.escolherVisual("hd-2d");
    const { resumoVisual } = await import("../src/telas/config/EscolhaHabitat.tsx");
    expect(resumoVisual("vidro", "claro", m.habitatAtual(), true)).toBe("pele Sci-fi · tema claro · mapa Ilha · HD-2D");
    expect(resumoVisual("vidro", "claro", m.habitatAtual(), false)).toBe("pele Sci-fi · tema claro");
  });
});
