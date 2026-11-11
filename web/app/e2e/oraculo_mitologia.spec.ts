/* MITOLOGIA, E0 (docs/TAREFA_V3_MITOLOGIA.md): o balao do oraculo Jijimon. O save (e2e/save_oraculo.json, gerado por
   e2e/gerar_save_oraculo.mjs) e um Rookie com duas hybris (derrotas para o Gazimon muito acima dele, em dois dias). Com a chave `mitologia`
   ligada e o oraculo sem ter contado nada a este pet, ele conta o primeiro pedaco da lenda, depois o segundo, e some. Sem nada gravado, a chave comeca ligada (2026-11-11). Desligada, nada
   aparece; um pet que o oraculo ainda nao conhecia comeca calado (as lutas de antes de ligar a chave nao falam). So le a tela. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";
import { LENDA_DO_MACACO } from "../motor/lendas.ts";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = JSON.parse(readFileSync(fileURLToPath(new URL("./save_oraculo.json", import.meta.url)), "utf8"));

async function semear(page: Page, mitologia: "1" | "0" | null, ouvidas: Record<string, number> | null): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, mit, ouv]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    if (mit !== null) localStorage.setItem(chave + "-mitologia", mit);
    if (ouv !== null) localStorage.setItem(chave + "-mitologia-ouvidas", ouv);
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE), mitologia, ouvidas === null ? null : JSON.stringify(ouvidas)] as const);
}

function errosDa(page: Page): string[] {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  return erros;
}

for (const largura of [390, 1280]) {
  test(`o oráculo conta a lenda em pedaços, um por hybris, em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: largura >= 1100 ? 800 : 844 });
    await semear(page, "1", { [String(SAVE.semente)]: 0 });
    const erros = errosDa(page);
    await page.goto(APP + "#/pet");
    const balao = page.getByTestId("oraculo-balao");
    await expect(balao).toBeVisible();
    await expect(balao).toContainText("Jijimon:");
    await expect(balao).toContainText(LENDA_DO_MACACO[0]);
    await balao.getByRole("button", { name: "Entendi" }).click();
    await expect(balao).toContainText(LENDA_DO_MACACO[1]);
    await balao.getByRole("button", { name: "Entendi" }).click();
    await expect(balao).toHaveCount(0);
    /* o que ele ja contou fica contado: recarregar nao repete */
    await page.reload();
    await expect(page.locator(".app")).toBeVisible();
    await expect(page.getByTestId("oraculo-balao")).toHaveCount(0);
    expect(erros).toEqual([]);
  });
}

test("sem nada gravado, a chave começa ligada e o oráculo fala", async ({ page }) => {
  await semear(page, null, { [String(SAVE.semente)]: 0 });
  const erros = errosDa(page);
  await page.goto(APP + "#/pet");
  await expect(page.getByTestId("oraculo-balao")).toContainText(LENDA_DO_MACACO[0]);
  expect(erros).toEqual([]);
});

test("com a chave desligada o oráculo não fala", async ({ page }) => {
  await semear(page, "0", { [String(SAVE.semente)]: 0 });
  const erros = errosDa(page);
  await page.goto(APP + "#/pet");
  await expect(page.locator(".app")).toBeVisible();
  await page.waitForTimeout(1500);
  await expect(page.getByTestId("oraculo-balao")).toHaveCount(0);
  expect(erros).toEqual([]);
});

test("um pet que o oráculo ainda não conhecia começa calado", async ({ page }) => {
  await semear(page, "1", null);
  const erros = errosDa(page);
  await page.goto(APP + "#/pet");
  await expect(page.locator(".app")).toBeVisible();
  await page.waitForTimeout(1500);
  await expect(page.getByTestId("oraculo-balao")).toHaveCount(0);
  const ouvidas = await page.evaluate(c => localStorage.getItem(c + "-mitologia-ouvidas"), CHAVE);
  expect(JSON.parse(ouvidas!)[String(SAVE.semente)]).toMatchObject({ h: 2 });
  expect(erros).toEqual([]);
});
