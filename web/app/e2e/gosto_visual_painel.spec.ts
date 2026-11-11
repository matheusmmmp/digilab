/* O painel da TV do gosto visual (docs/PLANO_UX_GOSTO_VISUAL.md, etapa 1; a prancha docs/pranchas/ux-gosto-visual/): com ?gosto_visual=1 a
   linha "TV" da pilha abre o painel, "Ligar a TV" liga a TV do jogo, a reação e o que passa aparecem, o Esc fecha o painel sem desligar
   a TV e o foco volta à linha; "Parar" desliga. No celular o painel é a folha recolhida. Sem a chave, nada disso existe. Nada entra no
   registro: o protótipo fica fora do motor, do log e do save. O save é o do abertura.spec. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };

async function abrir(browser: Browser, busca: string, largura: number, altura: number, extra: Record<string, string> = {}) {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: altura } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, mais]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
    for (const [k, v] of Object.entries(mais)) localStorage.setItem(chave + k, v);
  }, [CHAVE, JSON.stringify(SAVE), extra] as const);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await page.goto(APP + busca + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
  return { ctx, page, erros };
}
const registro = (page: Page) => page.evaluate(() => JSON.stringify(JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] !== "t")));

test("gosto visual: a TV da pilha abre o painel, liga, o Esc fecha sem desligar e o Parar desliga; nada entra no registro", async ({ browser }) => {
  test.setTimeout(120_000);
  const { ctx, page, erros } = await abrir(browser, "?gosto_visual=1", 1440, 900);
  const antes = await registro(page);
  await expect(page.locator(".gv-canto")).toHaveCount(0);   /* o cartão do canto saiu (UX-GV-1) */
  const linha = page.locator(".pet-hud [data-painel-pet='tv'] button");
  await linha.click();
  const painel = page.getByTestId("painel-tv");
  await expect(painel).toBeVisible();
  await expect(painel.getByRole("button", { name: "Ligar a TV" })).toBeVisible();
  await expect(painel.getByTestId("tv-gosto")).toContainText("Gosta mais de: ");
  await expect(painel).not.toContainText(/carinhos/i);
  await painel.getByRole("button", { name: "Ligar a TV" }).click();
  await expect(painel.getByTestId("tv-passando")).toContainText("a TV do jogo, ", { timeout: 5_000 });
  await expect(painel.getByTestId("tv-reacao")).not.toHaveText("Ligando…", { timeout: 5_000 });
  await expect(page.getByTestId("tv-selo")).toHaveCount(0);   /* o selo é só da captura da tela do dono */
  /* o porquê e o que está passando abrem a um toque */
  await painel.getByRole("button", { name: "Por quê" }).click();
  await expect(painel.locator(".tvp-linha").first()).toBeVisible();
  await painel.getByRole("button", { name: "O que está passando" }).click();
  await expect(painel.locator(".tvp-agora").first()).toBeVisible();
  /* o Esc fecha o painel, a TV continua e o foco volta à linha da pilha */
  await page.keyboard.press("Escape");
  await expect(painel).toHaveCount(0);
  await expect(linha).toBeFocused();
  await expect(page.getByTestId("tv-anuncio")).toContainText("A TV do jogo está ligada.");
  /* reabrir: a TV ainda ligada; Parar desliga */
  await linha.click();
  await painel.getByRole("button", { name: "Parar" }).click();
  await expect(painel.getByRole("button", { name: "Ligar a TV" })).toBeVisible();
  await expect(page.getByTestId("tv-anuncio")).toContainText("A TV foi desligada.");
  expect(await registro(page)).toBe(antes);
  expect(erros).toEqual([]);
  await ctx.close();
});

test("gosto visual: no celular o painel é a folha recolhida, e sem a chave não há TV", async ({ browser }) => {
  test.setTimeout(120_000);
  const c = await abrir(browser, "?gosto_visual=1", 390, 844);
  await c.page.locator(".mm-retrato").click();
  await c.page.locator("#leque-pet").getByRole("button", { name: "TV", exact: true }).click();
  const painel = c.page.getByTestId("painel-tv");
  await expect(painel).toHaveClass(/tvp--recolhida/);
  await expect(painel.getByRole("button", { name: "Ligar a TV" })).toBeVisible();
  await expect(painel.getByRole("button", { name: "Por quê" })).toHaveCount(0);
  await painel.getByRole("button", { name: "Mais" }).click();
  await expect(painel.getByRole("button", { name: "Por quê" })).toBeVisible();
  await expect(painel.getByRole("button", { name: "Mostrar minha tela" })).toHaveCount(0);
  expect(c.erros).toEqual([]);
  await c.ctx.close();
  const s = await abrir(browser, "", 1440, 900);
  await expect(s.page.locator(".pet-hud [data-painel-pet='digibrain']")).toHaveCount(1);
  await expect(s.page.locator("[data-painel-pet='tv']")).toHaveCount(0);
  await expect(s.page.getByTestId("tv-anuncio")).toHaveCount(0);
  expect(s.erros).toEqual([]);
  await s.ctx.close();
});

/** um ponto do cliente (px) em que a TV da ilha está (a cena diz, pela mesma conta do toque), longe do pet e das bordas; null se ela não está na tela */
const pontoDaTv = (page: Page) => page.evaluate(() => {
  const d = (window as any).__digilab, pts: [number, number][] = [];
  for (let y = 80; y < innerHeight - 160; y += 6) for (let x = 120; x < innerWidth - 480; x += 6) if (d.tvEm(x, y)) pts.push([x, y]);
  if (!pts.length) return null;
  const mx = pts.reduce((a, p) => a + p[0], 0) / pts.length, my = pts.reduce((a, p) => a + p[1], 0) / pts.length;
  return pts.reduce((a, p) => (Math.hypot(p[0] - mx, p[1] - my) < Math.hypot(a[0] - mx, a[1] - my) ? p : a));
});

test("gosto visual: o toque na TV da ilha abre o painel, a câmera vai ao cantinho e o sinal da reação é um ícone do jogo", async ({ browser }) => {
  test.setTimeout(180_000);
  /* com "Exibir detalhes do pet" desligado a pilha fica só com a linha "TV" (o caminho do teclado) */
  const { ctx, page, erros } = await abrir(browser, "?gosto_visual=1", 1440, 900, { "-detalhes-pet": "0" });
  const antes = await registro(page);
  await expect(page.locator(".pet-hud [data-painel-pet]")).toHaveCount(1);
  const linha = page.locator(".pet-hud [data-painel-pet='tv'] button");
  await expect(linha).toBeVisible();
  /* a câmera segue o pet, e a TV pode estar fora da tela: a linha abre o painel, a câmera vai ao cantinho e a TV aparece */
  await linha.click();
  const painel = page.getByTestId("painel-tv");
  await expect(painel).toBeVisible();
  await expect.poll(() => pontoDaTv(page), { timeout: 20_000 }).not.toBeNull();
  await page.keyboard.press("Escape");
  await expect(painel).toHaveCount(0);
  /* de novo pela linha, liga a TV e fecha: o pet vai à almofada, a câmera o segue e a TV fica na tela */
  await linha.click();
  await painel.getByRole("button", { name: "Ligar a TV" }).click();
  /* o botão que tinha o foco saiu: o foco vai para o Parar, e o Esc ainda fecha o painel */
  await expect(painel.getByRole("button", { name: "Parar" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(painel).toHaveCount(0);
  /* o sinal da reação: um ícone das grades do jogo, só com o pet sentado (as reações sem ícone ficam null) */
  await expect.poll(() => page.evaluate(() => (window as any).__digilab.sinalTv()), { timeout: 90_000, intervals: [250] }).toMatch(/^(coracao|pergunta|reticencias|x)$/);
  /* o toque na TV abre o painel */
  await expect.poll(() => pontoDaTv(page), { timeout: 20_000 }).not.toBeNull();
  const p = (await pontoDaTv(page))!;
  await page.mouse.move(p[0], p[1]);
  await expect(page.locator(".pet-cena")).toHaveCSS("cursor", "pointer");
  await page.mouse.click(p[0], p[1]);
  await expect(painel).toBeVisible();
  await expect(painel.getByTestId("tv-passando")).toContainText("a TV do jogo");
  await painel.getByRole("button", { name: "Parar" }).click();
  expect(await registro(page)).toBe(antes);
  expect(erros).toEqual([]);
  await ctx.close();
  /* sem a chave: nenhuma TV tocável e nenhum sinal */
  const s = await abrir(browser, "", 1440, 900);
  expect(await s.page.evaluate(() => { const d = (window as any).__digilab; return [d.tvEm(700, 400), d.sinalTv()]; })).toEqual([false, null]);
  await s.ctx.close();
});
