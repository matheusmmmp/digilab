/* A "Vida do pet", passo 2 (docs/registro/2026-11.md, a seção "VIDA DO PET, a cena e o toque"): o toque no pet e a cena. O toque e o `acariciar` do botao (um evento "d" so, igual),
   a reacao vem do corpo (window.__digilab.reacao), um arrasto ou um toque fora do pet nao conta, e nada disso mexe no replay. Com a cena 3D e
   com a reserva do mundo (sem WebGL). Os dados vem do motor por window.__digilab (so leitura). */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
/* o save do Pet (Home) do jogo.spec: um v13 com um carinho e um tapa no registro */
const SAVE = { semente: 4242, versao: 13, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };

async function semear(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE)] as const);
}
type Cena = { pet: [number, number]; ret: { x: number; y: number; w: number; h: number } | null };
const lerCena = (page: Page) => page.evaluate(() => (window as any).__digilab.cena() as Cena | null);
const eventosD = (page: Page) => page.evaluate(() => JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] === "d").map((e: unknown[]) => e[2]));
const reacao = (page: Page) => page.evaluate(() => (window as any).__digilab.reacao() as { tipo: string; carinho: number; medo: number } | null);
/** o centro do sprite do pet no cliente: o retangulo que a vista informa (CENA.ret) e relativo a cena */
async function centroDoPet(page: Page): Promise<[number, number]> {
  await expect.poll(async () => (await lerCena(page))?.ret?.w ?? 0, { timeout: 30_000, message: "a vista informou o retangulo do pet" }).toBeGreaterThan(0);
  const c = (await lerCena(page))!.ret!, cena = (await page.locator(".pet-cena").boundingBox())!;
  return [cena.x + c.x + c.w / 2, cena.y + c.y + c.h / 2];
}

for (const [nome, largura, semWebGL] of [["a cena 3D", 390, false], ["a reserva sem WebGL", 390, true], ["a cena 3D no desktop", 1280, false]] as const) {
  test(`toque no pet: é o carinho do botão, a reação vem do corpo, e arrasto ou toque fora não contam, com ${nome}`, async ({ browser }) => {
    test.setTimeout(120_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: largura >= 1100 ? 800 : 844 } });
    const page = await ctx.newPage();
    if (semWebGL) await page.addInitScript(() => {
      const orig = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, tipo: string, ...r: unknown[]) {
        return /webgl/.test(tipo) ? null : (orig as (...a: unknown[]) => unknown).call(this, tipo, ...r);
      } as typeof orig;
    });
    await semear(page);
    const erros: string[] = [];
    page.on("pageerror", e => erros.push("pageerror: " + e.message));
    page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(semWebGL ? ".pet-cena .cena-mundo" : ".pet-cena .cena3d")).toBeVisible();
    const antes = await eventosD(page);
    expect(antes).toEqual(["acariciar", "tapa"]);
    expect(await reacao(page)).toBeNull();
    /* um toque fora do pet (no alto da cena) nao faz nada */
    const cena = (await page.locator(".pet-cena").boundingBox())!;
    await page.mouse.click(cena.x + 12, cena.y + 130);
    expect(await eventosD(page)).toEqual(antes);
    /* um arrasto que comeca no pet nao e toque */
    const [px, py] = await centroDoPet(page);
    await page.mouse.move(px, py); await page.mouse.down(); await page.mouse.move(px + 60, py + 10, { steps: 6 }); await page.mouse.up();
    expect(await eventosD(page)).toEqual(antes);
    /* o toque no pet: um "acariciar" so, o mesmo evento do botao, e a reacao do corpo */
    const [qx, qy] = await centroDoPet(page);
    await page.mouse.click(qx, qy);
    await expect.poll(() => eventosD(page)).toEqual([...antes, "acariciar"]);
    const r = await reacao(page);
    expect(r, "a reacao do corpo ficou na vista").not.toBeNull();
    expect(["relaxou", "calmo"]).toContain(r!.tipo);
    expect(r!.carinho + r!.medo).toBeCloseTo(1, 9);
    /* o botao Carinho grava o mesmo evento (no celular ele mora no Mais, M1-2) */
    if (largura < 900) await page.locator(".acoes-pet .acao-mais").click();
    await page.getByRole("button", { name: "Carinho", exact: true }).first().click();
    await expect.poll(() => eventosD(page)).toEqual([...antes, "acariciar", "acariciar"]);
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
