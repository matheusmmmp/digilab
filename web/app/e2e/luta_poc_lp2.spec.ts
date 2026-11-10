/* LUTA_POC, LP2 (docs/TAREFA_V3_LUTA_POC.md): a chave da luta da POC no app. Desligada (o padrao), o jogo de hoje: o pet v19 abre, sem aviso.
   Ligada por ?luta_poc=1: o descarte 7 tira o pet v19 com o aviso da luta nova (LP-6), e um pet v21 abre; a Arena e a Campanha abrem as telas
   da luta nova (desde a LP3), em vez das telas do combate de antes. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const save = (versao: number) => JSON.stringify({ semente: 4242, versao, log: [[480, "t", 120]] });

async function semear(page: Page, s: string, descarte: string): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, d]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", d); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, s, descarte] as const);
}
const versaoDoSave = (page: Page) => page.evaluate(k => { const t = localStorage.getItem(k); return t === null ? null : (JSON.parse(t) as { versao: number }).versao; }, CHAVE);
function errosDa(page: Page): string[] {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  return erros;
}

test("chave desligada: o pet v19 abre como hoje, sem o aviso da luta nova", async ({ page }) => {
  const erros = errosDa(page);
  await semear(page, save(19), "6");
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena")).toBeVisible();
  await expect(page.locator(".aviso-poc")).toHaveCount(0);
  expect(await versaoDoSave(page)).toBe(19);
  expect(await page.evaluate(k => localStorage.getItem(k + "-descarte"), CHAVE)).toBe("6");
  expect(erros).toEqual([]);
});

test("chave ligada (?luta_poc=1): o descarte 7 tira o pet v19, com o aviso da luta nova", async ({ page }) => {
  const erros = errosDa(page);
  await semear(page, save(19), "6");
  await page.goto(APP + "?luta_poc=1#/pet/estado");
  const aviso = page.locator("dialog.aviso-poc");
  await expect(aviso).toBeVisible();
  await expect(aviso.getByRole("heading", { name: "A luta agora é na arena" })).toBeVisible();
  await expect(aviso).toContainText("o pet que você tinha foi descartado");
  expect(await page.evaluate(k => localStorage.getItem(k + "-descarte"), CHAVE)).toBe("7");
  expect(await page.evaluate(k => JSON.parse(localStorage.getItem(k + "-descartados") ?? "[]").length, CHAVE)).toBe(1);
  expect(erros).toEqual([]);
});

test("chave ligada: um pet v21 abre, e a Arena e a Campanha abrem as telas da luta nova (LP3)", async ({ page }) => {
  const erros = errosDa(page);
  await semear(page, save(21), "7");
  await page.goto(APP + "?luta_poc=1#/pet/estado");
  await expect(page.locator(".pet-cena")).toBeVisible();
  expect(await versaoDoSave(page)).toBe(21);
  for (const rota of ["#/lutar/arena", "#/lutar/campanha"]) {
    await page.goto(APP + "?luta_poc=1" + rota);
    await expect(page.getByTestId(rota.endsWith("arena") ? "poc-arena" : "poc-campanha")).toBeVisible();
  }
  expect(erros).toEqual([]);
});
