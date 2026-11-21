/* O gabarito dos assets com a proteção desligada (CN4): o que o jogo pede hoje ao carregar o atlas (os dois JSON e as duas imagens), o mapa
   da cena da evolução e os pacotes dela, os sons e a fala, com os mesmos endereços e na mesma ordem. O gabarito
   (test/gabaritos/cn4_assets_desligados.json) foi gravado num commit anterior ao das URLs assinadas; com a chave desligada (sem
   VITE_DIGILAB_PROTECAO=1), nada muda. Regravar só com decisão: GRAVAR_GABARITO_CN4=1 npx vitest run test/assets_desligados.test.ts */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";

const ARQUIVO = fileURLToPath(new URL("./gabaritos/cn4_assets_desligados.json", import.meta.url));
const BASE = "http://127.0.0.1:8765/v1/web/dist/";

interface Pedido { tipo: "fetch" | "imagem"; url: string; init?: unknown }

function montarNavegador(pedidos: Pedido[]): void {
  const respostas: Record<string, unknown> = {
    "digilab_atlas_up_pecas.json": { atlas: "digilab_atlas_up_pecas.png", ms_por_quadro: 100,
      pecas: { fundo_hex: [0, 0, 2, 2], anel_plataforma: [0, 0, 2, 2] } },
    "digilab_atlas_up_clipes.json": { atlas: "digilab_atlas_up_clipes.png", ms_por_quadro: 100, sprites: {} },
    "mapa.json": { versao: 1 },
  };
  vi.stubGlobal("fetch", async (url: string, init?: unknown) => {
    pedidos.push(init === undefined ? { tipo: "fetch", url } : { tipo: "fetch", url, init });
    const nome = url.split("/").at(-1)!;
    if (nome.endsWith(".bin")) return new Response(new Uint8Array(64));
    return new Response(JSON.stringify(respostas[nome] ?? { versao: 1 }), { status: 200 });
  });
  class ImagemFalsa {
    onload: (() => void) | null = null;
    onerror: (() => void) | null = null;
    crossOrigin: string | null = null;
    set src(v: string) { pedidos.push({ tipo: "imagem", url: v, ...(this.crossOrigin ? { init: { crossOrigin: this.crossOrigin } } : {}) }); queueMicrotask(() => this.onload?.()); }
  }
  vi.stubGlobal("Image", ImagemFalsa);
  vi.stubGlobal("document", {
    baseURI: BASE,
    documentElement: { style: { setProperty() { /* nada */ } }, dataset: {} },
    createElement: () => ({ width: 0, height: 0, getContext: () => ({ drawImage() { /* nada */ }, fillRect() { /* nada */ } }), toDataURL: () => "data:," }),
  });
}

async function coletar(): Promise<Pedido[]> {
  const pedidos: Pedido[] = [];
  montarNavegador(pedidos);
  vi.resetModules();
  const atlas = await import("../src/atlas.ts");
  atlas.carregarAtlas();
  for (let i = 0; i < 50 && pedidos.filter(p => p.tipo === "imagem").length < 2; i++) await new Promise(r => setTimeout(r, 0));
  const evolucao = await import("../src/evolucaoUp.ts");
  await evolucao.carregarMapaEvolucao();
  await evolucao.baixarPacotes([{ pacote: "adventure", pedacos: [[0, 32]] } as never, { pacote: "zero2", pedacos: [[0, 16]] } as never], () => { /* nada */ });
  const som = await import("../src/som.ts");
  await som.buscarAsset(som.SONS_URL + "mapa.json");
  await som.buscarAsset(som.SONS_URL + "bgm/ilha.ogg");
  /* a fala: o status e um pedido (a CN4 só a manda para a API com a chave ligada) */
  const fala = await import("../src/fala.ts");
  await fala.verificarLLM();
  fala.FALA_LLM.on = true; fala.FALA_LLM.ativo = true;
  fala.falaLLM({ origem: "vida", acao: "comer", fatores: ["fome"], evento_ref: [3], intensidade: 0.7, exploracao: false, tick: 1 }, "adulto", 0.5);
  await new Promise(r => setTimeout(r, 0));
  return pedidos;
}

describe("os assets com a proteção desligada (CN4)", () => {
  afterEach(() => { vi.unstubAllGlobals(); vi.resetModules(); });

  it("pede os mesmos endereços, na mesma ordem, do gabarito gravado antes das URLs assinadas", async () => {
    const pedidos = await coletar();
    if (process.env.GRAVAR_GABARITO_CN4 === "1") writeFileSync(ARQUIVO, JSON.stringify({ base: BASE, pedidos }, null, 1) + "\n", "utf8");
    const gabarito = JSON.parse(readFileSync(ARQUIVO, "utf8")) as { base: string; pedidos: Pedido[] };
    expect(gabarito.base).toBe(BASE);
    expect(pedidos).toEqual(gabarito.pedidos);
    expect(pedidos.some(p => p.url.includes("/assets/"))).toBe(false);
  });
});
