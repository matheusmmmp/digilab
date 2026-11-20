/* A pele Estencil das peles de rua (docs/PLANO_UX_PELES_RUA.md): a pele entra pelo endereco (?pele=estencil) e pelo terceiro cartao de
   Ajustes > Visual, desenha a HUD com a forma dela (a caixa de tinta com o contorno de osso e a sombra dura, a letra vazada, o indice das
   janelas, os icones em traco), fica gravada e nao muda o registro.
   O padrao continua sendo o Vidro. So no desktop. O save e o do camera_livre.spec. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };
const TINTA = "rgb(23, 25, 31)", OSSO = "rgb(240, 234, 219)";

async function abrir(browser: Browser): Promise<{ page: Page; erros: string[]; fechar: () => Promise<void> }> {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1920, height: 950 } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up_pecas.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE)] as const);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  return { page, erros, fechar: () => ctx.close() };
}
const registro = (page: Page) => page.evaluate(() => JSON.stringify(JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] !== "t")));
const pele = (page: Page) => page.evaluate(() => document.documentElement.dataset.pele);
/** a caixa do cartao do pet, no topo, como o navegador a calculou: o contorno (::before), o miolo (::after), o texto, a sombra e a letra do nome */
const cartao = (page: Page) => page.locator(".topo-pet").first().evaluate(e => ({
  contorno: getComputedStyle(e, "::before").backgroundColor, miolo: getComputedStyle(e, "::after").backgroundColor, texto: getComputedStyle(e).color,
  sombra: getComputedStyle(e).filter, letra: getComputedStyle(e.querySelector(".topo-pet-nome b")!).fontFamily }));

test("?pele=estencil pinta a HUD com a tinta e o osso, sem gravar; sem o parametro, o padrao e o Vidro", async ({ browser }) => {
  test.setTimeout(120_000);
  const { page, erros, fechar } = await abrir(browser);
  await page.goto(APP + "?pele=estencil#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  expect(await pele(page)).toBe("estencil");
  const c = await cartao(page);
  expect(c.contorno).toBe(OSSO);
  expect(c.miolo).toBe(TINTA);
  expect(c.texto).toBe(OSSO);
  expect(c.sombra).toContain("drop-shadow");
  expect(c.letra).toContain("Saira Stencil One");
  expect(await page.evaluate(k => localStorage.getItem(k + "-pele"), CHAVE)).toBeNull();
  /* as janelas da direita e as acoes de baixo seguem a pele */
  await expect(page.locator(".pet-hud [data-painel-pet='estado']")).toBeVisible();
  const janela = page.locator(".pet-hud .hud-painel").first();
  expect(await janela.evaluate(e => getComputedStyle(e, "::before").backgroundColor)).toBe(OSSO);
  /* o indice da janela (a ordem na pilha) e o icone em traco da acao, no lugar da figura */
  expect(await janela.locator(".hud-painel__bt").evaluate(e => getComputedStyle(e, "::before").content)).toContain("es-janela");
  const alimentar = page.locator('.pet-dock .dock-bt[data-acao="alimentar"]');
  await expect(alimentar).toBeVisible();
  await expect(alimentar.locator("img, svg").first()).toBeHidden();
  expect(await alimentar.evaluate(e => { const c = getComputedStyle(e, "::before"); return c.maskImage || c.webkitMaskImage; })).toContain("data:image/svg+xml");
  if (process.env.DIGILAB_CAPTURA) { await page.waitForTimeout(2500); await page.screenshot({ path: `${process.env.DIGILAB_CAPTURA}/estencil_pet_1920.png` }); }
  await page.goto(APP + "#/pet/estado");
  await page.reload();
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  expect(await pele(page)).toBe("vidro");
  /* sem a pele, a figura da acao continua la */
  await expect(page.locator('.pet-dock .dock-bt[data-acao="alimentar"]').locator("img, svg").first()).toBeVisible();
  expect(erros).toEqual([]);
  await fechar();
});

test("Ajustes > Visual: tres cartoes de pele; escolher a Estencil vale na hora, fica gravada e nao entra no registro", async ({ browser }) => {
  test.setTimeout(120_000);
  const { page, erros, fechar } = await abrir(browser);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  const antes = await registro(page);
  await page.goto(APP + "#/config/visual");
  const grupo = page.getByRole("radiogroup", { name: "Pele dos menus" });
  await expect(grupo.getByRole("radio")).toHaveCount(3);
  await expect(grupo.getByRole("radio", { name: /Sci-fi/ })).toBeChecked();
  const est = grupo.getByRole("radio", { name: /Estêncil/ });
  await expect(est).toContainText("prévia");
  await est.click();
  await expect(est).toBeChecked();
  expect(await pele(page)).toBe("estencil");
  expect(await page.evaluate(k => localStorage.getItem(k + "-pele"), CHAVE)).toBe("estencil");
  if (process.env.DIGILAB_CAPTURA) { await page.waitForTimeout(1500); await page.screenshot({ path: `${process.env.DIGILAB_CAPTURA}/estencil_visual_1920.png` }); }
  /* as setas andam pelos tres cartoes (o radiogroup do WAI-ARIA) */
  await est.press("ArrowLeft");
  await expect(grupo.getByRole("radio", { name: /Militar/ })).toBeChecked();
  await grupo.getByRole("radio", { name: /Militar/ }).press("ArrowRight");
  await expect(est).toBeChecked();
  /* a escolha sobrevive a recarregar */
  await page.goto(APP + "#/pet/estado");
  await page.reload();
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  expect(await pele(page)).toBe("estencil");
  expect((await cartao(page)).contorno).toBe(OSSO);
  expect(await registro(page)).toBe(antes);
  expect(erros).toEqual([]);
  await fechar();
});
