/* A camera solta e o minimapa (L1 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md), no desktop: o D solta a camera e o "seguir o
   pet" aparece, o F volta, o clique no minimapa leva a camera, o retrato vira "Seguir o pet" com ela solta, e o DigiBrain abre pela 4a linha
   da pilha. Nada disso entra no registro (so vista). No celular nada disso existe. O save e o do vida_pet_cena.spec (um v13 com o mundo). */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };

async function semear(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE)] as const);
}
/** os eventos do registro fora o tempo (o "t" cresce sozinho com o relogio do jogo) */
const registro = (page: Page) => page.evaluate(() => JSON.stringify(JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] !== "t")));

test("a camera solta e o minimapa no desktop: D solta, F volta, o minimapa leva a camera, nada entra no registro", async ({ browser }) => {
  test.setTimeout(120_000);
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1920, height: 950 } });
  const page = await ctx.newPage();
  await semear(page);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  const mini = page.getByLabel("Minimapa da ilha");
  await expect(mini).toBeVisible({ timeout: 30_000 });
  /* a etiqueta do canto saiu; o DigiBrain e a 4a linha da pilha */
  await expect(page.locator(".pet-etiqueta-db")).toHaveCount(0);
  await expect(page.locator(".pet-hud [data-painel-pet='digibrain'] button")).toBeVisible();
  const antes = await registro(page);
  const seguir = page.getByRole("button", { name: "Seguir o pet" }).first();
  await expect(seguir).toHaveCount(0);
  await expect(page.locator(".topo-retrato")).toHaveAttribute("aria-label", "Meus pets");

  /* o D segurado: a camera anda para a direita, longe do pet */
  await page.locator("body").focus();
  await page.keyboard.down("d"); await page.waitForTimeout(900); await page.keyboard.up("d");
  await expect(page.locator(".pet-seguir")).toBeVisible();
  await expect(page.locator(".topo-retrato")).toHaveAttribute("aria-label", "Seguir o pet");
  /* o F volta ao pet: o botao some e o retrato volta a abrir Meus pets */
  await page.keyboard.press("f");
  await expect(page.locator(".pet-seguir")).toHaveCount(0);
  await expect(page.locator(".topo-retrato")).toHaveAttribute("aria-label", "Meus pets");

  /* o clique na beira direita do minimapa (a mata) leva a camera ate la; o botao "seguir o pet" volta */
  const caixa = (await mini.boundingBox())!;
  await page.mouse.click(caixa.x + caixa.width * 0.85, caixa.y + caixa.height / 2);
  await expect(page.locator(".pet-seguir")).toBeVisible();
  await page.locator(".pet-seguir").click();
  await expect(page.locator(".pet-seguir")).toHaveCount(0);

  /* o DigiBrain pela pilha abre o painel; o minimapa sai enquanto ele esta aberto */
  await page.locator(".pet-hud [data-painel-pet='digibrain'] button").click();
  await expect(page.locator("#pet-painel")).toBeVisible();
  await expect(mini).toHaveCount(0);
  await page.keyboard.press("Escape");
  await expect(mini).toBeVisible();

  /* so vista: nenhum evento novo no registro (so o tempo andou) */
  expect(await registro(page)).toBe(antes);
  expect(erros).toEqual([]);
  await ctx.close();
});

test("no celular nao ha minimapa nem camera solta", async ({ browser }) => {
  test.setTimeout(120_000);
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await semear(page);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await page.locator("body").focus();
  await page.keyboard.down("d"); await page.waitForTimeout(600); await page.keyboard.up("d");
  await expect(page.locator(".minimapa")).toHaveCount(0);
  await expect(page.locator(".pet-seguir")).toHaveCount(0);
  /* abaixo de 900 px o retrato e o do mobile minimo (#619, M1-1): `.mm-retrato`, "Painéis do pet" (o leque); o `.topo-retrato` "Meus pets" so existe
     de 900 px em diante. Conflito da soma #619 + #636: o spec da L1 ainda procurava o retrato de antes */
  await expect(page.locator(".mm-retrato")).toHaveAttribute("aria-label", "Painéis do pet");
  await expect(page.locator(".topo-retrato")).toHaveCount(0);
  await ctx.close();
});
