/* As capturas da P2 de pegar o pet (docs/TAREFA_V3_PEGAR_PET.md): o dono pega o pet, ele balanca com a careta e cai onde foi solto.
   Duas formas: o bebe (sem as reacoes de rosto: o Stun) e o Rookie (com elas: o Medo e a gota), em 1280 px (mouse) e 390 px (o dedo,
   por eventos de toque do CDP), nas peles vidro e militar (xcom). Para cada uma: as fotos (no chao, na mao e logo depois de soltar) e os
   quadros da tela para o GIF (o screencast), do pointerdown ate 1 s depois de soltar.
   Roda com: npx playwright test -c e2e_capturas/pegar_pet_p2.config.ts, com DIGILAB_CAPTURAS_PP2=<pasta>. Nao e referencia das capturas. */
import { expect, test, type CDPSession, type Page } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_PP2 ?? "";
const CHAVE = "digilab-web-v21-sprites";
/* o mesmo pet (semente 4242, v19): bebe as 10h do primeiro dia; Rookie (limo arisco), acordado e com a saude cheia, as 18h */
const FORMAS = [
  { nome: "bebe_stun", save: { semente: 4242, versao: 21, log: [[480, "t", 120]] } },
  { nome: "rookie_medo", save: { semente: 4242, versao: 21, log: [[480, "t", 600]] } },
] as const;

async function abrir(page: Page, pele: string, save: unknown): Promise<void> {
  await page.goto("/motor/index.ts");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(save)] as const);
  await page.goto(`/?pele=${pele}&clipes_up=1#/pet/estado`);
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await page.locator(".pet-cena [data-objetos]").waitFor({ state: "attached", timeout: 60_000 }).catch(() => undefined);
  await page.waitForTimeout(1500);
}
async function centroDoPet(page: Page): Promise<[number, number]> {
  await expect.poll(() => page.evaluate(() => (window as any).__digilab.cena()?.ret?.w ?? 0), { timeout: 30_000 }).toBeGreaterThan(0);
  const c = await page.evaluate(() => (window as any).__digilab.cena().ret), cena = (await page.locator(".pet-cena").boundingBox())!;
  return [cena.x + c.x + c.w / 2, cena.y + c.y + c.h / 2];
}

/** o ponteiro: o mouse no desktop, o dedo (toque do CDP) no celular */
function ponteiro(page: Page, cdp: CDPSession, dedo: boolean) {
  const toque = (type: string, x: number, y: number) =>
    cdp.send("Input.dispatchTouchEvent", { type, touchPoints: type === "touchEnd" ? [] : [{ x, y, id: 1, radiusX: 8, radiusY: 8, force: 1 }] });
  return {
    baixo: (x: number, y: number) => dedo ? toque("touchStart", x, y) : page.mouse.move(x, y).then(() => page.mouse.down()),
    move: (x: number, y: number) => dedo ? toque("touchMove", x, y) : page.mouse.move(x, y),
    cima: (x: number, y: number) => dedo ? toque("touchEnd", x, y) : page.mouse.up(),
  };
}

test.describe("capturas da P2 de pegar o pet", () => {
  test.skip(!PASTA, "so com DIGILAB_CAPTURAS_PP2");
  for (const forma of FORMAS) for (const pele of ["vidro", "xcom"]) for (const [w, h] of [[390, 844], [1280, 720]] as [number, number][]) test(`${forma.nome}: ${pele} ${w}`, async ({ browser }) => {
    test.setTimeout(240_000);
    mkdirSync(PASTA, { recursive: true });
    const dedo = w < 768;
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1, hasTouch: dedo, isMobile: dedo, baseURL: test.info().project.use.baseURL });
    const page = await ctx.newPage(), cdp = await ctx.newCDPSession(page);
    await abrir(page, pele, forma.save);
    const nome = `pegar_${forma.nome}_${w}_${pele === "xcom" ? "militar" : "vidro"}`;
    let n = 0, gravando = false;
    cdp.on("Page.screencastFrame", async (ev: { data: string; sessionId: number }) => {
      if (gravando) writeFileSync(join(PASTA, `${nome}_gif_f${String(n++).padStart(4, "0")}.jpg`), Buffer.from(ev.data, "base64"));
      await cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId }).catch(() => undefined);
    });
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, everyNthFrame: 1 });
    const [px, py] = await centroDoPet(page);
    await page.screenshot({ path: join(PASTA, `${nome}_1_chao.png`) });
    const p = ponteiro(page, cdp, dedo), dx = w >= 1100 ? 220 : 110, dy = w >= 1100 ? 60 : 90;
    gravando = true;
    await page.waitForTimeout(400);
    await p.baixo(px, py);
    /* sobe devagar, anda para a direita, para (balanca sozinho), volta um pouco para a esquerda e solta */
    for (let i = 1; i <= 30; i++) { await p.move(px + (dx * i) / 30, py - 20 * Math.sin((Math.PI * i) / 30) + (dy * i) / 30); await page.waitForTimeout(25); }
    expect(await page.evaluate(() => (window as any).__digilab.petNaMao())).toBe(true);
    await page.waitForTimeout(700);
    await page.screenshot({ path: join(PASTA, `${nome}_2_na_mao.png`) });
    await page.waitForTimeout(500);
    for (let i = 1; i <= 15; i++) { await p.move(px + dx - (dx * 0.4 * i) / 15, py + dy); await page.waitForTimeout(25); }
    await page.waitForTimeout(250);
    await page.screenshot({ path: join(PASTA, `${nome}_3_balanco.png`) });
    await p.cima(px + dx * 0.6, py + dy);
    await page.waitForTimeout(160);
    await page.screenshot({ path: join(PASTA, `${nome}_4_quique.png`) });
    await page.waitForTimeout(900);
    gravando = false;
    await cdp.send("Page.stopScreencast");
    await page.screenshot({ path: join(PASTA, `${nome}_5_caiu.png`) });
    const lp = await page.evaluate(() => JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] === "lp"));
    const rosto = await page.evaluate(() => (window as any).__digilab.reacaoRosto());
    writeFileSync(join(PASTA, `${nome}.txt`), `lp: ${JSON.stringify(lp)}\nreacaoRosto depois de soltar: ${rosto}\nquadros do gif: ${n}\n`);
    expect(lp).toHaveLength(1);
    expect(n).toBeGreaterThan(20);
    await ctx.close();
  });
});
