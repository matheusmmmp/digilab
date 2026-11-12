/* CONVERSA_PET, M1 (D1, 2026-11-06): na tela Conversar, "vai comer" vira a ação do dono pelo mesmo caminho do botão. O servidor da fala livre é
   falso (rota do Playwright): a conversa manda `comando: true` (e não `voz`), o servidor devolve `comando: "alimentar"` e o app valida de novo
   e grava o evento "dc" da ração, como o botão Alimentar. A fala nunca entra no registro do pet. */
import { expect, test } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120]] };

test("Conversar: 'vai comer' manda comando:true e grava o evento do botão Alimentar", async ({ browser }) => {
  test.setTimeout(120_000);
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE)] as const);
  const pedidos: Record<string, unknown>[] = [];
  await page.route("**/api/fala-livre/status", r => r.fulfill({ json: { modelo: "falso", carregado: true } }));
  await page.route("**/api/fala-livre/verificar", r => r.fulfill({ json: { nao_suportadas: 0, manipulacao: false, afirmacoes: [] } }));
  await page.route("**/api/fala-livre", async r => {
    pedidos.push(JSON.parse(r.request().postData() ?? "{}"));
    await r.fulfill({ json: { fala: "Nhã, comida!", fatos_citados: [], fatos: [], estagio: "crianca", modelo: "falso", versao_prompt: "livre-v9", comando: "alimentar" } });
  });
  await page.goto(APP + "#/conversar/chat");
  await page.getByRole("button", { name: "Livre", exact: true }).click();
  const eventosD = () => page.evaluate(() => JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] === "d" || e[1] === "dc"));
  const antes = (await eventosD()).length;
  await page.locator("#conv-msg").fill("vai comer");
  await page.getByRole("button", { name: "Enviar" }).click();
  await expect.poll(() => pedidos.length).toBe(1);
  expect(pedidos[0].comando).toBe(true);
  expect(pedidos[0].voz).toBeUndefined();
  expect(pedidos[0].situacao).toBe("conversa");
  await expect.poll(async () => (await eventosD()).length).toBe(antes + 1);
  const novo = (await eventosD()).slice(-1)[0];
  expect(["d", "dc"]).toContain(novo[1]);
  expect(JSON.stringify(novo)).toMatch(/alimentar|racao/);
  await expect(page.locator(".mc-balao", { hasText: "Nhã, comida!" })).toBeVisible();
});

/* a mensagem nao some calada (2026-11-12): sem o servidor da fala livre a barra fica travada e diz por que; com o servidor e a fala falhando, a nota
   do erro aparece na conversa */
async function abrirConversa(browser: import("@playwright/test").Browser) {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE)] as const);
  return page;
}

test("Conversar: sem o servidor da fala livre, a barra fica travada e diz por quê", async ({ browser }) => {
  test.setTimeout(120_000);
  const page = await abrirConversa(browser);
  await page.route("**/api/fala-livre/status", r => r.abort());
  await page.goto(APP + "#/conversar/chat");
  await page.getByRole("button", { name: "Livre", exact: true }).click();
  await expect(page.locator("#conv-msg")).toBeDisabled();
  await expect(page.locator("#conv-msg")).toHaveAttribute("placeholder", "A fala livre precisa do servidor local ligado");
  await expect(page.getByRole("button", { name: "Enviar" })).toBeDisabled();
});

test("Conversar: a fala que falha mostra o erro em vez de sumir", async ({ browser }) => {
  test.setTimeout(120_000);
  const page = await abrirConversa(browser);
  await page.route("**/api/fala-livre/status", r => r.fulfill({ json: { modelo: "falso", carregado: true } }));
  await page.route("**/api/fala-livre", r => r.fulfill({ status: 503, json: { erro: "modelo fora do ar" } }));
  await page.goto(APP + "#/conversar/chat");
  await page.getByRole("button", { name: "Livre", exact: true }).click();
  await page.locator("#conv-msg").fill("oi");
  await page.getByRole("button", { name: "Enviar" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "A fala não saiu: modelo fora do ar" })).toBeVisible();
});
