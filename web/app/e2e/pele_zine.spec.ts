/* A pele Zine das peles de rua (docs/PLANO_UX_PELES_RUA.md), a unica clara: entra pelo endereco (?pele=zine) e pelo quarto cartao de
   Ajustes > Visual, desenha a HUD como recortes de papel (o papel, o traco de tinta de 3 px e a sombra dura no ::after, pelo filtro do
   corte a mao; a letra Rubik), fica gravada e nao muda o registro. O padrao continua sendo o Vidro. So no desktop. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };
const PAPEL = "rgb(246, 240, 224)", TINTA = "rgb(19, 19, 19)", ANIL = "rgb(43, 80, 255)";

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
/** o recorte do cartao do pet, no topo, como o navegador o calculou: o papel, o traco e o filtro (::after), o texto e a letra do nome */
const cartao = (page: Page) => page.locator(".topo-pet").first().evaluate(e => { const d = getComputedStyle(e, "::after"); return {
  papel: d.backgroundColor, traco: d.borderTopColor, largura: d.borderTopWidth, filtro: d.filter, texto: getComputedStyle(e).color,
  letra: getComputedStyle(e.querySelector(".topo-pet-nome b")!).fontFamily }; });

test("?pele=zine desenha a HUD em recortes de papel, sem gravar; sem o parametro, o padrao e o Vidro", async ({ browser }) => {
  test.setTimeout(120_000);
  const { page, erros, fechar } = await abrir(browser);
  await page.goto(APP + "?pele=zine#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  expect(await pele(page)).toBe("zine");
  const c = await cartao(page);
  expect(c.papel).toBe(PAPEL);
  expect(c.traco).toBe(TINTA);
  expect(c.largura).toBe("3px");
  expect(c.filtro).toContain("rabisco");
  expect(c.texto).toBe(TINTA);
  expect(c.letra).toContain("Rubik");
  expect(await page.locator("#rabisco").count()).toBe(1);
  expect(await page.evaluate(k => localStorage.getItem(k + "-pele"), CHAVE)).toBeNull();
  /* o destino atual do trilho e um adesivo anil; a primeira janela tem a tira de tinta com o indice */
  expect(await page.locator('.hx-nav__bt[aria-current="page"]').evaluate(e => getComputedStyle(e).backgroundColor)).toBe(ANIL);
  const janela = page.locator(".pet-hud .hud-painel").first();
  expect(await janela.locator(".hud-painel__bt").evaluate(e => getComputedStyle(e).backgroundColor)).toBe(TINTA);
  expect(await janela.locator(".hud-painel__bt").evaluate(e => getComputedStyle(e, "::before").content)).toContain("zn-janela");
  /* o icone em traco da acao, no lugar da figura */
  const alimentar = page.locator('.pet-dock .dock-bt[data-acao="alimentar"]');
  await expect(alimentar.locator("img, svg").first()).toBeHidden();
  expect(await alimentar.evaluate(e => { const d = getComputedStyle(e, "::before"); return d.maskImage || d.webkitMaskImage; })).toContain("data:image/svg+xml");
  await page.goto(APP + "#/pet/estado");
  await page.reload();
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  expect(await pele(page)).toBe("vidro");
  expect(erros).toEqual([]);
  await fechar();
});

test("Ajustes > Visual: quatro cartoes de pele; escolher o Zine vale na hora, fica gravado e nao entra no registro", async ({ browser }) => {
  test.setTimeout(120_000);
  const { page, erros, fechar } = await abrir(browser);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  const antes = await registro(page);
  await page.goto(APP + "#/config/visual");
  const grupo = page.getByRole("radiogroup", { name: "Pele dos menus" });
  await expect(grupo.getByRole("radio")).toHaveCount(4);
  const zn = grupo.getByRole("radio", { name: /Zine/ });
  await expect(zn).toContainText("prévia");
  await zn.click();
  await expect(zn).toBeChecked();
  expect(await pele(page)).toBe("zine");
  expect(await page.evaluate(k => localStorage.getItem(k + "-pele"), CHAVE)).toBe("zine");
  /* o cartao escolhido vira anil */
  await expect(zn).toHaveCSS("background-color", ANIL);
  /* a escolha sobrevive a recarregar */
  await page.goto(APP + "#/pet/estado");
  await page.reload();
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  expect(await pele(page)).toBe("zine");
  expect((await cartao(page)).papel).toBe(PAPEL);
  expect(await registro(page)).toBe(antes);
  expect(erros).toEqual([]);
  await fechar();
});
