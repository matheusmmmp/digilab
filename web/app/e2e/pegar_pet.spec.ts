/* Pegar o pet e solta-lo (docs/TAREFA_V3_PEGAR_PET.md, P2): na ilha 3D, o arrasto que comeca no pet o pega (window.__digilab.petNaMao), e
   soltar grava o "levar pet" ("lp") no registro, e o pet do motor vai para la. O arrasto nao vira carinho. Em 1280 px e em 390 px. Os
   dados vem do motor por window.__digilab (so leitura). */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
/* um pet v19 bebe, acordado as 10h do primeiro dia */
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120]] };

async function semear(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE)] as const);
}
type Cena = { pet: [number, number]; ret: { x: number; y: number; w: number; h: number } | null };
const lerCena = (page: Page) => page.evaluate(() => (window as any).__digilab.cena() as Cena | null);
const log = (page: Page) => page.evaluate(() => JSON.parse((window as any).__digilab.registro()).log as [number, string, unknown][]);
const petMotor = (page: Page) => page.evaluate(() => (window as any).__digilab.mundo().pet as [number, number]);

async function centroDoPet(page: Page): Promise<[number, number]> {
  await expect.poll(async () => (await lerCena(page))?.ret?.w ?? 0, { timeout: 30_000, message: "a vista informou o retangulo do pet" }).toBeGreaterThan(0);
  const c = (await lerCena(page))!.ret!, cena = (await page.locator(".pet-cena").boundingBox())!;
  return [cena.x + c.x + c.w / 2, cena.y + c.y + c.h / 2];
}

for (const largura of [1280, 390]) {
  test(`pegar o pet: o arrasto o pega, soltar grava o "levar pet" e o pet do motor muda de lugar, em ${largura} px`, async ({ browser }) => {
    test.setTimeout(120_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: largura >= 1100 ? 800 : 844 } });
    const page = await ctx.newPage();
    await semear(page);
    const erros: string[] = [];
    page.on("pageerror", e => erros.push("pageerror: " + e.message));
    page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
    const antes = await log(page), antesD = antes.filter(e => e[1] === "d").length;
    const [px, py] = await centroDoPet(page), pet0 = await petMotor(page);
    await page.mouse.move(px, py); await page.mouse.down();
    await page.mouse.move(px + 4, py, { steps: 2 });
    expect(await page.evaluate(() => (window as any).__digilab.petNaMao()), "4 px ainda nao pega").toBe(false);
    const dx = largura >= 1100 ? 160 : 90;
    await page.mouse.move(px + dx, py + 30, { steps: 12 });
    expect(await page.evaluate(() => (window as any).__digilab.petNaMao())).toBe(true);
    await page.waitForTimeout(300);
    await page.mouse.up();
    expect(await page.evaluate(() => (window as any).__digilab.petNaMao())).toBe(false);
    const depois = await log(page), lp = depois.filter(e => e[1] === "lp");
    expect(lp).toHaveLength(1);
    const alvo = lp[0][2] as { x: number; y: number };
    expect(Number.isInteger(alvo.x) && Number.isInteger(alvo.y)).toBe(true);
    /* o pet do motor foi para onde o dono soltou (no meio do mapa, o proprio ponto; o tempo pode ja te-lo movido um passo) */
    const pet1 = await petMotor(page);
    expect(Math.hypot(pet1[0] - pet0[0], pet1[1] - pet0[1])).toBeGreaterThan(Math.hypot(pet1[0] - alvo.x, pet1[1] - alvo.y));
    expect(Math.hypot(pet1[0] - alvo.x, pet1[1] - alvo.y)).toBeLessThanOrEqual(16);
    expect(depois.filter(e => e[1] === "d").length, "o arrasto nao vira carinho").toBe(antesD);
    /* o desenho fica onde ele caiu: a vista nao o faz caminhar de volta */
    await page.waitForTimeout(600);
    const cena = (await lerCena(page))!;
    expect(Math.hypot(cena.pet[0] - pet0[0], cena.pet[1] - pet0[1])).toBeGreaterThan(Math.hypot(cena.pet[0] - alvo.x, cena.pet[1] - alvo.y));
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
