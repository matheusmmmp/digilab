/* A luta no layout habitat (B3, etapa 2; docs/TAREFA_V3_LUTA_LAYOUT.md, testes 5 e 6): a luta de ponta a ponta nas duas peles (Vidro e Militar)
   em 390, 1280 e 1920 x 950: alvos >= 44 px, sem rolagem horizontal, Pausar / x2 / Desistir funcionam, Desistir pede confirmacao, o Voltar do
   navegador continua pedindo Desistir, o foco volta ao botao de origem, o fim vai ao Resultado; e com prefers-reduced-transparency e
   prefers-reduced-motion o vidro fica opaco e nao ha animacao nova. Com DIGILAB_CAPTURAS_B3=<pasta> grava tambem as capturas do PR
   (a luta pausada, por pele e largura). */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const PASTA = process.env.DIGILAB_CAPTURAS_B3 ?? "";
/* o Rookie v13 da luta em tempo real (como em jogo.spec.ts) */
const SAVE = { semente: 101, versao: 13, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
const TELAS = [["390", 390, 844], ["1280", 1280, 720], ["1920", 1920, 950]] as const;

async function semear(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE), JSON.stringify(TAMER)] as const);
}
function vigiar(page: Page): string[] {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  return erros;
}
async function abrirLuta(page: Page, pele: string): Promise<void> {
  await semear(page);
  await page.goto(`${APP}?pele=${pele}#/lutar/arena`);
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
  await expect(page.getByTestId("luta-relogio")).toHaveText(/^0:0[1-9]$/, { timeout: 10_000 });
}

for (const pele of ["vidro", "xcom"]) for (const [nome, w, h] of TELAS) {
  test(`luta no layout habitat: ${pele} ${nome}`, async ({ page }) => {
    test.setTimeout(300_000);
    const erros = vigiar(page);
    await page.setViewportSize({ width: w, height: h });
    await abrirLuta(page, pele);
    /* a estrutura: HUD, etiqueta do modo, regra em uso e o dock; o palco cobre a tela inteira */
    await expect(page.locator(".luta-tela .hud-lado")).toHaveCount(2);
    await expect(page.locator(".luta-modo")).toContainText("Arena");
    await expect(page.getByTestId("luta-regra")).not.toBeEmpty();
    const arena = await page.locator(".luta-arena--tr").boundingBox();
    expect(arena!.width).toBeGreaterThanOrEqual(w - 1); expect(arena!.height).toBeGreaterThanOrEqual(h - 1);
    /* sem rolagem horizontal; alvos do dock >= 44 px */
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth && document.body.scrollWidth <= innerWidth)).toBe(true);
    for (const b of await page.locator(".luta-dock button").all()) {
      const r = await b.boundingBox(); expect(r!.width).toBeGreaterThanOrEqual(44); expect(r!.height).toBeGreaterThanOrEqual(44);
    }
    /* nada do HUD sai da tela */
    for (const sel of [".luta-hud", ".luta-contexto", ".luta-card", ".luta-dock"]) {
      const r = (await page.locator(sel).first().boundingBox())!;
      expect(r.x, sel).toBeGreaterThanOrEqual(-1); expect(r.x + r.width, sel).toBeLessThanOrEqual(w + 1); expect(r.y + r.height, sel).toBeLessThanOrEqual(h + 1);
    }
    /* Pausar para o relogio; Continuar volta */
    await page.getByRole("button", { name: "Pausar a animação" }).click();
    const parado = await page.getByTestId("luta-relogio").textContent();
    await page.waitForTimeout(700);
    await expect(page.getByTestId("luta-relogio")).toHaveText(parado!);
    if (PASTA) { mkdirSync(PASTA, { recursive: true }); await page.screenshot({ path: join(PASTA, `luta_${w}_${pele === "xcom" ? "militar" : "vidro"}.png`), animations: "disabled" }); }
    /* Desistir pede confirmacao; Continuar vendo devolve o foco ao Desistir; o Voltar do navegador tambem pede */
    await page.locator(".luta-desistir").click();
    const conf = page.locator("dialog.modal-conf[open]");
    await expect(conf).toBeVisible();
    await conf.getByRole("button", { name: "Continuar vendo" }).click();
    await expect(page.locator("dialog.modal-conf")).toHaveCount(0);     /* desmontado (o evento close e assincrono): so entao o Voltar */
    await expect(page.locator(".luta-desistir")).toBeFocused();
    await page.goBack();
    await expect(conf).toBeVisible();
    await conf.getByRole("button", { name: "Continuar vendo" }).click();
    await expect(page).toHaveURL(/#\/lutar\/luta$/);
    /* (a luta segue pausada ate aqui: um nocaute em 20 s a terminaria antes dos cliques) */
    await page.getByRole("button", { name: "Continuar a animação" }).click();
    /* x2 e o fim: o Resultado; Continuar volta a Arena */
    await page.getByRole("button", { name: "Velocidade dobrada" }).click();
    await expect(page.locator("dialog.modal-res[open]")).toBeVisible({ timeout: 90_000 });
    await page.keyboard.press("Escape");
    await expect(page).toHaveURL(/#\/lutar\/arena$/);
    expect(erros).toEqual([]);
  });
}

test("luta no layout habitat: Desistir confirmado volta a Arena", async ({ page }) => {
  const erros = vigiar(page);
  await abrirLuta(page, "vidro");
  await page.locator(".luta-desistir").click();
  await page.locator("dialog.modal-conf[open]").getByRole("button", { name: "Desistir" }).click();
  await expect(page).toHaveURL(/#\/lutar\/arena$/);
  expect(erros).toEqual([]);
});

test("luta no layout habitat: transparência reduzida deixa o vidro sem desfoque, e movimento reduzido sem animação nem transição", async ({ page }) => {
  const erros = vigiar(page);
  await page.setViewportSize({ width: 1280, height: 720 });
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-transparency", value: "reduce" }, { name: "prefers-reduced-motion", value: "reduce" }] });
  await abrirLuta(page, "vidro");
  const m = await page.evaluate(() => {
    const e = (s: string) => getComputedStyle(document.querySelector(s)!);
    return ["hud-lado", "luta-card", "luta-dock", "luta-contexto"].map(c => ({ c, f: e("." + c).backdropFilter, f2: e("." + c).getPropertyValue("-webkit-backdrop-filter") }))
      .concat([{ c: "anim", f: [...document.querySelectorAll(".luta-tela *")].map(x => getComputedStyle(x).animationName).filter(n => n !== "none").join(","), f2: "" },
               { c: "trans", f: [...document.querySelectorAll(".luta-tela *")].map(x => getComputedStyle(x).transitionDuration).filter(n => !/^0s(, 0s)*$/.test(n)).join(","), f2: "" }]);
  });
  for (const x of m.slice(0, 4)) expect(x.f === "none" || x.f === "", x.c).toBe(true);
  expect(m[4].f, "sem animação").toBe("");
  expect(m[5].f, "sem transição").toBe("");
  expect(erros).toEqual([]);
});
