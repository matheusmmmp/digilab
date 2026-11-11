/* MITOLOGIA, E1 (docs/TAREFA_V3_MITOLOGIA.md, secao 10): o oraculo conta a pedra achada, o Codice das lendas no Diario mostra o que o par
   viveu (e "???" no que falta), e o enigma dos 7 toques no retrato do Jijimon. O save (e2e/save_mitologia_e1.json, gerado por
   e2e/gerar_save_mitologia_e1.mjs) e um pet que o dono acaricia e faz brincar (a Amizade) e leva ate a pedra numa noite. So le a tela,
   menos o enigma, que grava o "decifrado" fora do save. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";
import { ENIGMA, FALA_PEDRA } from "../motor/lendas_e1.ts";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = JSON.parse(readFileSync(fileURLToPath(new URL("./save_mitologia_e1.json", import.meta.url)), "utf8"));

async function semear(page: Page, mitologia: boolean): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, mit]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave + "-mitologia", mit ? "1" : "0");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE), mitologia] as const);
}
function errosDa(page: Page): string[] {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  return erros;
}

for (const largura of [390, 1280]) {
  test(`o oráculo conta a pedra achada, uma vez, em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: largura >= 1100 ? 800 : 844 });
    await semear(page, true);
    const erros = errosDa(page);
    await page.goto(APP + "#/pet");
    const balao = page.getByTestId("oraculo-balao");
    await expect(balao).toHaveAttribute("data-fala", "pedra");
    await expect(balao).toContainText(FALA_PEDRA);
    await balao.getByRole("button", { name: "Entendi" }).click();
    await expect(balao).toHaveCount(0);
    await page.reload();
    await expect(page.locator(".app")).toBeVisible();
    await page.waitForTimeout(1000);
    await expect(page.getByTestId("oraculo-balao")).toHaveCount(0);
    expect(erros).toEqual([]);
  });

  test(`o Códice mostra o vivido e esconde o resto; o enigma se abre com 7 toques, em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: largura >= 1100 ? 800 : 844 });
    await semear(page, true);
    const erros = errosDa(page);
    await page.goto(APP + "#/diario/registro");
    const codice = page.getByTestId("codice");
    await expect(codice).toBeVisible();
    await codice.locator("summary").click();
    await expect(codice.locator(".codice-lenda li.codice-oculto")).toHaveCount(7);          // nenhuma hybris: a lenda inteira escondida
    await expect(codice.locator("li[data-deus='amizade']")).toContainText("Amizade");
    await expect(codice.locator("li[data-deus='coragem']")).toHaveClass(/codice-oculto/);
    await expect(codice).toContainText("A pedra do macaco");
    await expect(codice.locator("li[data-segredo='montanha']")).toHaveClass(/codice-oculto/);   // E2: sem Piedmon vencido, a montanha escondida
    const retrato = page.getByTestId("codice-oraculo");
    for (let i = 0; i < 6; i++) await retrato.click();
    await expect(page.getByTestId("codice-enigma")).toHaveCount(0);
    await retrato.click();
    const enigma = page.getByTestId("codice-enigma");
    await expect(enigma).toContainText(ENIGMA.pergunta);
    await enigma.getByRole("button", { name: "O vento" }).click();
    await expect(enigma).toContainText(ENIGMA.erro);
    await enigma.getByRole("button", { name: "A nuvem" }).click();
    await expect(page.getByTestId("codice-enigma")).toContainText(ENIGMA.acerto);
    await page.reload();
    await page.getByTestId("codice").locator("summary").click();
    await expect(page.getByTestId("codice")).toContainText("O enigma");
    expect(erros).toEqual([]);
  });
}

test("com a chave desligada não há Códice nem oráculo", async ({ page }) => {
  await semear(page, false);
  const erros = errosDa(page);
  await page.goto(APP + "#/diario/registro");
  await expect(page.locator(".app")).toBeVisible();
  await page.waitForTimeout(1000);
  await expect(page.getByTestId("codice")).toHaveCount(0);
  await expect(page.getByTestId("oraculo-balao")).toHaveCount(0);
  expect(erros).toEqual([]);
});
