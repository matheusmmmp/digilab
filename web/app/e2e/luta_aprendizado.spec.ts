/* O painel "O que o pet aprendeu" na Arena (TAREFA da frente v3-luta-aprendizado): so leitura do GambitsPet. Antes da luta o painel mostra a lista de
   partida; depois de uma luta inteira (x2 ate o Resultado) mostra "Em 1 luta" e as notas; travar uma regra no editor a poe em "Travadas".
   Sem rolagem horizontal em 390, 1280 e 1920, nas duas peles. Com DIGILAB_CAPTURAS_APRENDIZADO=<pasta> grava as capturas (docs/capturas_luta_aprendizado/). */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const PASTA = process.env.DIGILAB_CAPTURAS_APRENDIZADO ?? "";
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
const semRolagem = (page: Page) => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth && document.body.scrollWidth <= innerWidth);

for (const pele of ["vidro", "xcom"]) for (const [nome, w, h] of TELAS) {
  test(`painel de aprendizado: ${pele} ${nome}`, async ({ page }) => {
    test.setTimeout(300_000);
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(e.message));
    await page.setViewportSize({ width: w, height: h });
    await semear(page);
    await page.goto(`${APP}?pele=${pele}#/lutar/arena`);
    const painel = page.getByTestId("painel-aprendizado");
    /* L3: as regras e o que o pet aprendeu ficam no bloco "Regras", fechado ao abrir a Arena */
    const abrirRegras = async () => { if (!(await painel.isVisible())) await page.locator(".ar2-regras > summary").click(); };
    await abrirRegras();
    await painel.scrollIntoViewIfNeeded();
    await expect(painel).toBeVisible();
    await expect(page.getByTestId("ap-vazio")).toBeVisible();
    const n = await page.getByTestId("ap-regra").count();
    expect(n).toBeGreaterThanOrEqual(1);
    await expect(page.getByTestId("ap-dono")).toContainText("não travou nem vetou");
    expect(await semRolagem(page)).toBe(true);
    /* uma luta inteira */
    await page.locator(".lutar-grande").click();
    await expect(page).toHaveURL(/#\/lutar\/luta$/);
    await expect(page.getByTestId("luta-relogio")).toHaveText(/^0:0[1-9]$/, { timeout: 10_000 });
    await page.getByRole("button", { name: "Velocidade dobrada" }).click();
    await expect(page.locator("dialog.modal-res[open]")).toBeVisible({ timeout: 120_000 });
    await page.keyboard.press("Escape");
    await expect(page).toHaveURL(/#\/lutar\/arena$/);
    await abrirRegras();
    await painel.scrollIntoViewIfNeeded();
    await expect(page.getByTestId("ap-vazio")).toHaveCount(0);
    await expect(painel).toContainText("Em 1 luta");
    await expect(page.getByTestId("ap-regra")).toHaveCount(n);
    await expect(page.getByTestId("ap-nota").first()).toContainText(/nota [+-]\d,\d\d/);
    await expect(page.getByTestId("ap-hist")).toBeVisible();
    /* o dono trava a primeira regra: aparece em "Travadas" */
    await page.getByRole("button", { name: "Travar nesta posição" }).first().click();
    await expect(painel).toContainText("Travadas (1)");
    expect(await semRolagem(page)).toBe(true);
    if (PASTA) {
      mkdirSync(PASTA, { recursive: true });
      await painel.scrollIntoViewIfNeeded();
      await painel.screenshot({ path: join(PASTA, `aprendizado_${w}_${pele === "xcom" ? "militar" : "vidro"}.png`), animations: "disabled" });
    }
    expect(erros).toEqual([]);
  });
}
