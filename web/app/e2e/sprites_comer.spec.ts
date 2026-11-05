/* O Comer na ilha, ponta a ponta (docs/TAREFA_V3_SPRITES_ACOES.md, M4; so a vista):
   1. sem o atlas do UP (o CI, a queda da M3): o pet que come faz o gesto de hoje (window.__digilab.comer() === "gesto") e o palco 2D por
      cima (.lcd, PalcoPet.tsx) desenha a carne sobre a cabeca e as migalhas;
   2. com um atlas de clipes sintetico servido pela rota (arte propria, gerada aqui; as tags Comer e Comer_objeto nas 60 formas): o clipe
      toca (=== "clipe"), e o gesto, a carne e as migalhas saem (o palco 2D fica vazio em volta do pet).
   O pet: o save "comer" das capturas da Vida do pet (e2e_capturas/saves_cena.json), um v13 que termina comendo. O relogio do jogo
   (src/tempo.ts, o unico setInterval de 100 ms) fica parado, como nas capturas: o motor segue na acao "comer" o teste inteiro. O atlas
   atual (Assets/digilab_atlas_up.json, fora do git) vem do disco no caso 2; os clipes, so da rota. */
import { expect, test, type BrowserContext, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";
import { deflateSync } from "node:zlib";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("../e2e_capturas/saves_cena.json", import.meta.url), "utf8"));
const SAVE = SAVES.comer;

/* ------------------------------------------------------------------ o atlas de clipes sintetico (arte propria: retangulos de cor chapada) */
/** um PNG RGBA sem compressao de filtro (filtro 0 em cada linha), feito a mao: assinatura, IHDR, IDAT (zlib) e IEND */
function png(w: number, h: number, px: (x: number, y: number) => [number, number, number, number]): Buffer {
  const tabela = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
  const crc = (b: Buffer) => { let c = 0xffffffff; for (const x of b) c = tabela[(c ^ x) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
  const bloco = (tipo: string, dados: Buffer) => {
    const t = Buffer.concat([Buffer.from(tipo, "ascii"), dados]), n = Buffer.alloc(4), c = Buffer.alloc(4);
    n.writeUInt32BE(dados.length); c.writeUInt32BE(crc(t));
    return Buffer.concat([n, t, c]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 6;
  const cru = Buffer.alloc(h * (1 + 4 * w));
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) cru.set(px(x, y), y * (1 + 4 * w) + 1 + 4 * x);
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), bloco("IHDR", ihdr), bloco("IDAT", deflateSync(cru)), bloco("IEND", Buffer.alloc(0))]);
}
/* a folha 64 x 32: o Idle (magenta, 20 x 24), dois quadros do Comer (ciano: de pe e agachado) e a comida (amarela, 4 x 4) */
const MAGENTA: [number, number, number, number] = [214, 40, 160, 255], CIANO: [number, number, number, number] = [30, 200, 220, 255];
const AMARELO: [number, number, number, number] = [240, 200, 40, 255], VAZIO: [number, number, number, number] = [0, 0, 0, 0];
const PNG_SINTETICO = png(64, 32, (x, y) =>
  x < 20 && y < 24 ? MAGENTA : x >= 20 && x < 40 && y < 24 ? CIANO : x >= 40 && x < 60 && y < 20 ? CIANO : x >= 60 && y < 4 ? AMARELO : VAZIO);
/* quadro = [x, y, w, h, dx, dy] na caixa 32 x 32; [0,0,0,0,0,0] e o quadro vazio */
const CLIPES_SINTETICOS = {
  Idle: { quadros: [[0, 0, 20, 24, 6, 8], [0, 0, 20, 24, 6, 8]], ms: [200, 200], loop: true },
  Comer: { quadros: [[20, 0, 20, 24, 6, 8], [40, 0, 20, 20, 6, 12]], ms: [160, 160], loop: true },
  Comer_objeto: { quadros: [[60, 0, 4, 4, 27, 28], [0, 0, 0, 0, 0, 0]], ms: [160, 160], loop: true },
};
/* as 60 formas (4 especies x 15 formas): todas com o Comer, senao o juntarClipes falha alto (uma acao em umas formas e nao em outras) */
const FORMAS = ["bebe", "crianca_sereno", "crianca_arisco", "adolescente_brigao", "adulto_duelista", "adulto_furioso", "adolescente_guardiao",
  "adulto_espelho", "adulto_muralha", "adolescente_cacador", "adulto_sentinela", "adulto_emboscador", "adolescente_colosso", "adulto_vigia", "adulto_tita"];
const ATLAS_CLIPES_SINTETICO = {
  versao: 1, fonte: "sintetico, para o e2e do Comer (TAREFA_V3_SPRITES_ACOES, M4); arte propria, sem PNG da Bandai", atlas: "digilab_atlas_up_clipes.png",
  sprites: Object.fromEntries(["brasa", "cirro", "ferrugem", "limo"].flatMap(e => FORMAS.map(f => [`${e}_${f}`, { digimon: "Sintetico", caixa: [32, 32], clipes: CLIPES_SINTETICOS }]))),
};

/* ------------------------------------------------------------------ a pagina */
async function abrir(ctx: BrowserContext): Promise<{ page: Page; erros: string[] }> {
  /* o relogio do jogo parado: o motor fica na acao "comer" em que o registro termina */
  await ctx.addInitScript(() => {
    const orig = window.setInterval.bind(window);
    (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
  });
  const page = await ctx.newPage();
  /* semeia por uma pagina da mesma origem que nao e o app (web/app/CLAUDE.md) */
  await page.goto(`${PREFIXO}/web/app/package.json`);
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE)] as const);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  expect(await page.evaluate(() => (window as any).__digilab.mundo().acao)).toBe("comer");
  return { page, erros };
}
type Leitura = { tocou: "clipe" | "gesto" | null; acao: string; icone: number; migalhas: number; total: number };
/** num quadro: o que tocou no comer e os pixels opacos do palco 2D por cima da ilha (.lcd): na faixa da carne (acima do pet, a direita),
    na das migalhas (a metade de baixo e a direita do sprite, ate a queda) e no canvas inteiro */
const ler = (page: Page) => page.evaluate((): Leitura | null => {
  const d = (window as any).__digilab, r = d.cena()?.ret as { x: number; y: number; w: number; h: number } | null;
  const cv = document.querySelector<HTMLCanvasElement>(".pet-cena > .lcd");
  if (!r || !cv || r.w <= 0) return null;
  const cx = cv.getContext("2d")!, K = cv.width / cv.clientWidth, img = cx.getImageData(0, 0, cv.width, cv.height).data;
  const opacos = (x0: number, y0: number, x1: number, y1: number) => {
    let n = 0;
    const a = Math.max(0, Math.floor(x0 * K)), b = Math.min(cv.width, Math.ceil(x1 * K)), c = Math.max(0, Math.floor(y0 * K)), e = Math.min(cv.height, Math.ceil(y1 * K));
    for (let y = c; y < e; y++) for (let x = a; x < b; x++) if (img[(y * cv.width + x) * 4 + 3] > 0) n++;
    return n;
  };
  /* a carne: o icone fica acima e a direita do sprite (desenharIcone e desenharIconeGrade: x + w - 6, ate 30 px acima, nunca acima de 56 px) */
  const topo = Math.max(0, r.y - 70), base = Math.max(r.y + 4, 56 + 40);
  return {
    tocou: d.comer(), acao: d.mundo().acao,
    icone: opacos(r.x + r.w / 2, topo, r.x + r.w + 40, base),
    migalhas: opacos(r.x + r.w * 0.5, r.y + r.h * 0.6, r.x + r.w + 8, r.y + r.h + 18),
    total: opacos(0, 0, cv.clientWidth, cv.clientHeight),
  };
});

for (const [largura, altura] of [[390, 844], [1280, 800]] as const) {
  test(`comer sem o atlas, ${largura} px: o gesto de hoje, com a carne e as migalhas por cima`, async ({ browser }) => {
    test.setTimeout(120_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: altura } });
    await ctx.route(/\/Assets\/(digilab_atlas_up|digilab_decoracao_up|decoracao_up\/)/, r => r.abort());
    const { page, erros } = await abrir(ctx);
    /* o gesto, e por cima a carne e as migalhas, no mesmo quadro */
    await expect.poll(async () => { const l = await ler(page); return l && l.tocou === "gesto" && l.icone > 0 && l.migalhas > 0; },
      { timeout: 30_000, message: "o gesto do comer com a carne e as migalhas" }).toBe(true);
    /* e fica: o pet segue comendo, e o clipe nunca aparece sem o atlas */
    for (let i = 0; i < 6; i++) {
      await page.waitForTimeout(250);
      const l = (await ler(page))!;
      expect(l.acao).toBe("comer");
      expect(l.tocou, "sem o atlas, o gesto (a queda explicita da M3)").toBe("gesto");
      expect(l.icone, "a carne sobre a cabeca").toBeGreaterThan(0);
    }
    /* os unicos erros esperados sao os do atlas e da decoracao que nao carregaram (a rota os corta) */
    expect(erros.filter(e => !/falha ao carregar (o atlas|a decora)|Failed to load resource/.test(e))).toEqual([]);
    await ctx.close();
  });

  test(`comer com o atlas de clipes sintético, ${largura} px: o clipe Comer toca e o gesto, a carne e as migalhas saem`, async ({ browser }) => {
    test.setTimeout(120_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: altura } });
    await ctx.route(/\/Assets\/digilab_atlas_up_clipes\.json/, r => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(ATLAS_CLIPES_SINTETICO) }));
    await ctx.route(/\/Assets\/digilab_atlas_up_clipes\.png/, r => r.fulfill({ status: 200, contentType: "image/png", body: PNG_SINTETICO }));
    const { page, erros } = await abrir(ctx);
    /* o clipe toca (o laco da acao comer) e o palco 2D fica vazio: nem a carne nem as migalhas */
    await expect.poll(async () => { const l = await ler(page); return l && l.tocou === "clipe" && l.total === 0; },
      { timeout: 30_000, message: "o clipe Comer no corpo, sem a carne e sem as migalhas" }).toBe(true);
    /* por mais de dez ciclos do clipe (320 ms): sempre o clipe, nunca o gesto, e nada por cima */
    for (let i = 0; i < 12; i++) {
      await page.waitForTimeout(300);
      const l = (await ler(page))!;
      expect(l.acao).toBe("comer");
      expect(l.tocou, "com o Comer no atlas, o clipe").toBe("clipe");
      expect(l, "sem a carne e sem as migalhas").toMatchObject({ icone: 0, migalhas: 0, total: 0 });
    }
    await expect(page.getByText("Atlas de sprites não carregou.")).toHaveCount(0);
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
