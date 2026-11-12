/* A TV no jogo (GOSTO_VISUAL, as decisoes A a E da captura ligada ao cerebro; docs/registro/2026-11.md, D-GV-TVJOGO), no desktop (1440 x 900)
   e no celular (390 x 844):
     - o pet de exemplo do primeiro acesso nasce v35; com a TV do jogo ligada pelo painel, ele vai ate a TV sozinho ("No cerebro: indo ate a
       TV.") e o "Gosta mais de" vem do cerebro (`data-gosto-fonte="cerebro"`), com o porque aberto;
     - parar a TV grava a TV desligada ("tv|desligada") e o painel diz "No cerebro: a TV esta desligada.";
     - um pet v35 semeado com uma imagem parada (o mesmo "st" por dois dias, levado ate a TV) mostra o enjoo: "enjoado dela".
   As capturas vao para DIGILAB_CAPTURAS (tvjogo_*.png), quando a variavel existe. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";
import { CELULA_PERTO_DA_TV_JOGO, Motor, centroDaCelula, valorSentidoTela } from "../motor/index.ts";
import { CMU_GRANDE } from "../motor/constantes.ts";
import { ligarProduto } from "../src/produto.ts";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const CAPTURAS = process.env.DIGILAB_CAPTURAS ?? null;
const TAMANHOS = [["desktop", 1440, 900], ["celular", 390, 844]] as const;

async function abrir(browser: Browser, largura: number, altura: number, save: string | null = null) {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: altura } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    if (s !== null) localStorage.setItem(chave, s);
  }, [CHAVE, save] as const);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
  return { ctx, page, erros };
}
const registro = (page: Page) => page.evaluate(() => {
  const r = JSON.parse((window as any).__digilab.registro());
  return { versao: r.versao as number, st: (r.log as unknown[][]).filter(e => e[1] === "st").map(e => e[2] as string) };
});
async function abrirPainelTv(page: Page, movel: boolean) {
  if (movel) {
    await page.locator(".mm-retrato").click();
    await page.locator("#leque-pet").getByRole("button", { name: "TV", exact: true }).click();
  } else {
    await page.locator(".pet-hud [data-painel-pet='tv'] button").click();
  }
  return page.getByTestId("painel-tv");
}
/** anda o jogo ate a frase do cerebro no painel conter `texto` (a reacao com a TV ligada, ou a frase com ela parada); pausa o relogio */
const esperarFrase = (page: Page, texto: string, levar = false) => page.evaluate(async ([t, lv]) => {
  const d = (window as any).__digilab, t0 = performance.now();
  let levou = 0;
  while (performance.now() - t0 < 180_000) {
    const el = document.querySelector("[data-testid='tv-reacao'], [data-testid='tv-cerebro']");
    if (el && el.textContent && el.textContent.includes(t)) { d.velocidade(0); return el.textContent; }
    const b = document.querySelector<HTMLButtonElement>("[data-tv-levar]");
    if (lv && b && performance.now() - levou > 1500) { b.click(); levou = performance.now(); }
    await new Promise(r => setTimeout(r, 20));
  }
  return null;
}, [texto, levar] as const);
const capturar = async (page: Page, nome: string) => { if (CAPTURAS) await page.screenshot({ path: join(CAPTURAS, nome) }); };

/** um pet v35 com uma imagem parada: o mesmo "st" desde a primeira hora, levado ate a TV a cada 2 h, por dois dias */
function petComImagemParada(): string {
  const m = ligarProduto(new Motor(4242, 33));
  const [x, y] = centroDaCelula(CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE);
  for (let h = 1; h <= 48; h++) {
    m.avancar(60);
    if (h % 3 === 0) m.observar("alimentar");
    if (h % 5 === 0 && !m.e.dormindo) m.observar("acariciar");
    if (h % 8 === 0) m.observar("limpar");
    if (h === 1) m.sentidoTela(valorSentidoTela("tv", [10, 6, 2, 8, 5, 5, 5]));
    if (h % 2 === 0 && !m.e.dormindo) m.levarPet(x, y);
  }
  if (m.e.dormindo) throw new Error("o pet semeado ficou dormindo");
  m.levarPet(x, y);
  return JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao });
}

for (const [onde, largura, altura] of TAMANHOS) {
  const movel = onde === "celular";
  test(`a v35 no ${onde}: o pet vai ate a TV sozinho, o gosto vem do cerebro e parar desliga a TV`, async ({ browser }) => {
    test.setTimeout(240_000);
    const { ctx, page, erros } = await abrir(browser, largura, altura);
    expect((await registro(page)).versao).toBe(33);
    let painel = await abrirPainelTv(page, movel);
    await painel.getByRole("button", { name: "Ligar a TV" }).click();
    await expect(painel.getByTestId("tv-reacao")).toContainText("No cérebro:", { timeout: 15_000 });
    expect(await esperarFrase(page, "indo até a TV")).not.toBeNull();
    await page.waitForTimeout(600);
    await capturar(page, `tvjogo_indo_${onde}.png`);
    /* o gosto do cerebro, com o porque aberto (no celular, pelo "Mais") */
    if (movel) await painel.getByRole("button", { name: "Mais" }).click();
    await expect(painel.getByTestId("tv-gosto")).toHaveAttribute("data-gosto-fonte", "cerebro");
    await expect(painel.getByTestId("tv-gosto")).toContainText("Gosta mais de:");
    await expect(painel.getByTestId("tv-prot")).toContainText("é o do cérebro");
    await painel.getByRole("button", { name: "Por quê" }).click();
    await painel.getByTestId("tv-gosto").scrollIntoViewIfNeeded();
    await page.waitForTimeout(400);
    await capturar(page, `tvjogo_gosto_${onde}.png`);
    /* parar: a TV desligada no registro e no painel */
    await page.evaluate(() => (window as any).__digilab.velocidade(10));
    await painel.getByRole("button", { name: "Parar" }).first().click();
    await expect.poll(async () => (await registro(page)).st.at(-1)).toBe("tv|desligada");
    painel = page.getByTestId("painel-tv");
    expect(await esperarFrase(page, "a TV está desligada")).not.toBeNull();
    await page.waitForTimeout(400);
    await capturar(page, `tvjogo_desligada_${onde}.png`);
    expect(erros).toEqual([]);
    await ctx.close();
  });

  test(`a v35 no ${onde}: uma imagem parada cansa o pet (enjoado dela)`, async ({ browser }) => {
    test.setTimeout(240_000);
    const { ctx, page, erros } = await abrir(browser, largura, altura, petComImagemParada());
    expect((await registro(page)).versao).toBe(33);
    await abrirPainelTv(page, movel);
    const frase = await esperarFrase(page, "enjoado dela", true);
    expect(frase).not.toBeNull();
    await page.waitForTimeout(600);
    await capturar(page, `tvjogo_enjoado_${onde}.png`);
    expect((await registro(page)).st).toEqual(["tv|10|6|2|8|5|5|5"]);       // a TV do P0 nao ligou: a mesma imagem
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
