/* LUTA_POC, LP3 (docs/TAREFA_V3_LUTA_POC.md, secao 5.1): a tela da luta nova no build. Com a chave ligada por parametro:
   - a luta montada direto no nucleo (?palco_poc=...) passa no palco do comeco ao fim, com o dock da tela de antes (Pausar, x2 e Desistir;
     decisao do Matheus de 2026-11-09), e o resultado so aparece depois; o projetil e os efeitos aparecem; nada e gravado;
   - o dock: pausar para o relogio, Desistir (com a confirmacao) pula a animacao e volta, Ver replay mostra a luta de novo e Sair do replay
     fecha; o registro fica com a mesma luta;
   - um pet v21 luta na Arena: Lutar grava a luta no registro (evento "l" com o mapa) e o palco a mostra ate o fim (o palco confere o fim com
     o do motor e falha alto se nao bater);
   - com o movimento reduzido, sem tremida. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";

async function semear(page: Page, save: string | null): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 7, log: [] }));
    localStorage.setItem(chave + "-descarte", "7"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    if (s) localStorage.setItem(chave, s);
  }, [CHAVE, save] as const);
}
function errosDa(page: Page): string[] {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$|\/api\//.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  return erros;
}
const dado = (page: Page, k: string) => page.getByTestId("poc-canvas").evaluate((el, k) => (el as HTMLElement).dataset[k] ?? "", k);

test("a luta montada no nucleo passa no palco ate o fim, com o dock da tela de antes", async ({ page }) => {
  test.setTimeout(120_000);
  const erros = errosDa(page);
  await semear(page, null);
  await page.goto(APP + "?luta_poc=1&palco_poc=floresta,cirro_crianca_arisco,brasa_crianca_sereno,101");
  await expect(page.getByTestId("luta-poc")).toBeVisible();
  await expect(page.getByTestId("luta-poc")).toHaveAttribute("data-lutando", "1");
  const dock = page.getByTestId("poc-dock");
  await expect(dock.getByRole("button")).toHaveText(["", "×2", "Desistir"]);
  await expect(dock.getByRole("button", { name: "Pausar a animação" })).toBeVisible();
  await expect.poll(() => dado(page, "nossos"), { timeout: 30_000 }).not.toBe("0");
  await expect.poll(async () => Number(await dado(page, "tremidaMax")), { timeout: 30_000 }).toBeGreaterThan(0);
  await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 60_000 });
  /* o vencedor e o do nucleo (a LP3b mudou esta luta: o Gabumon atira de longe e o Agumon vence); a tela so mostra */
  await expect(page.getByTestId("poc-resultado")).toContainText(/(Gabumon|Agumon) venceu|Empate/);
  await page.getByTestId("poc-resultado").getByRole("button", { name: "Continuar" }).click();
  await expect(page.getByTestId("luta-poc")).toHaveCount(0);
  expect(erros).toEqual([]);
});

test("um pet v21 luta na Arena: a luta entra no registro e o palco a mostra ate o fim", async ({ page }) => {
  test.setTimeout(120_000);
  const erros = errosDa(page);
  await semear(page, JSON.stringify({ semente: 4242, versao: 21, log: [[480, "t", 4000]] }));
  await page.goto(APP + "?luta_poc=1#/lutar/arena");
  await expect(page.getByTestId("poc-arena")).toBeVisible();
  await page.getByTestId("poc-mapa-ringue").click();
  await page.getByTestId("poc-lutar").click();
  await expect(page.getByTestId("luta-poc")).toBeVisible();
  await expect(page.locator(".luta-modo")).toContainText("Arena · Ringue D-1 Grand Prix");
  await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 90_000 });
  const l = await page.evaluate(k => (JSON.parse(localStorage.getItem(k)!) as { log: [number, string, { m?: string }][] }).log.filter(e => e[1] === "l"), CHAVE);
  expect(l.length).toBe(1); expect(l[0][2].m).toBe("ringue");
  await page.getByTestId("poc-resultado").getByRole("button", { name: "Continuar" }).click();
  await expect(page.getByTestId("poc-arena")).toBeVisible();
  expect(erros).toEqual([]);
});

test.describe("movimento reduzido", () => {
  test.use({ reducedMotion: "reduce" });
  test("sem tremida; o resultado aparece", async ({ page }) => {
    test.setTimeout(120_000);
    await semear(page, null);
    await page.goto(APP + "?luta_poc=1&palco_poc=ringue,brasa_adulto_furioso,cirro_adulto_furioso,108");
    await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 60_000 });
    expect(await dado(page, "tremidaMax")).toBe("0");
  });
});

test("o dock: pausar, Desistir com a confirmacao, Ver replay e Sair do replay; o registro fica com a mesma luta", async ({ page }) => {
  test.setTimeout(150_000);
  const erros = errosDa(page);
  await semear(page, JSON.stringify({ semente: 4242, versao: 21, log: [[480, "t", 4000]] }));
  await page.goto(APP + "?luta_poc=1#/lutar/arena");
  await page.getByTestId("poc-mapa-floresta").click();
  await page.getByTestId("poc-lutar").click();
  const dock = page.getByTestId("poc-dock"), relogio = page.getByTestId("poc-relogio");
  /* as lutas do registro (os eventos "l"); os avancos de tempo ("t") crescem sozinhos com o relogio de verdade */
  const registro = () => page.evaluate(k => JSON.stringify((JSON.parse(localStorage.getItem(k)!) as { log: unknown[][] }).log.filter(e => e[1] === "l")), CHAVE);
  const antes = await registro();
  await expect.poll(async () => (await relogio.textContent()) !== "0:00", { timeout: 20_000 }).toBe(true);
  /* pausar: o relogio para; continuar: anda de novo */
  await dock.getByRole("button", { name: "Pausar a animação" }).click();
  await page.waitForTimeout(300); /* o canvas mostra o passo no quadro seguinte do navegador */
  const parado = await relogio.textContent(), passo = await dado(page, "passo");
  await page.waitForTimeout(1200);
  expect(await relogio.textContent()).toBe(parado); expect(await dado(page, "passo")).toBe(passo);
  await dock.getByRole("button", { name: "Continuar a animação" }).click();
  await expect.poll(() => dado(page, "passo"), { timeout: 10_000 }).not.toBe(passo);
  await dock.getByRole("button", { name: "Velocidade dobrada" }).click();
  await expect(dock.getByRole("button", { name: "Velocidade dobrada" })).toHaveAttribute("aria-pressed", "true");
  /* Desistir: a confirmacao; Continuar vendo fica; Desistir pula e volta para a Arena */
  await dock.getByRole("button", { name: "Desistir" }).click();
  await page.getByTestId("poc-desistir-conf").getByRole("button", { name: "Continuar vendo" }).click();
  await expect(page.getByTestId("luta-poc")).toHaveAttribute("data-lutando", "1");
  await dock.getByRole("button", { name: "Desistir" }).click();
  await page.getByTestId("poc-desistir-conf").getByRole("button", { name: "Desistir" }).click();
  await expect(page.getByTestId("poc-arena")).toBeVisible();
  expect(await registro()).toBe(antes);
  /* outra luta ate o fim; Ver replay mostra a mesma luta de novo, e Sair do replay fecha */
  await page.getByTestId("poc-lutar").click();
  await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 90_000 });
  const depois = await registro(), titulo = await page.getByTestId("poc-resultado").locator("h2").textContent();
  await page.getByTestId("poc-ver-replay").click();
  await expect(page.locator(".luta-modo")).toContainText("Replay · ");
  await expect(dock.getByRole("button", { name: "Sair do replay" })).toBeVisible();
  await dock.getByRole("button", { name: "Velocidade dobrada" }).click();
  await expect(page.getByTestId("poc-resultado")).toContainText("Fim do replay", { timeout: 90_000 });
  expect(await page.getByTestId("poc-resultado").textContent()).toContain(titulo!);
  await page.getByTestId("poc-ver-replay").click();
  await expect(dock.getByRole("button", { name: "Sair do replay" })).toBeVisible();
  await dock.getByRole("button", { name: "Sair do replay" }).click();
  await expect(page.getByTestId("poc-arena")).toBeVisible();
  expect(await registro()).toBe(depois);
  expect(erros).toEqual([]);
});
