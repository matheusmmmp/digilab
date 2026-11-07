/* CONVERSA_PET, DC2b (decisao DR-1, 2026-11-06): a chave "Fala pela rede (teste)" (Ajustes, desligada por padrao). Servidor falso (rota do Playwright,
   sem GPU nem API): desligada, o pedido e o de hoje; ligada num pet que nao e modular, nada muda e a tela diz isso; ligada no pet de teste do
   modular (v16, com decisao), o pedido leva so os `conceitos` do dec-v2 e a identidade, e a verificacao leva os mesmos conceitos. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 13, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120]] };

async function semear(page: Page, save?: object): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    if (s) localStorage.setItem(chave, s);
  }, [CHAVE, save ? JSON.stringify(save) : ""] as const);
}
type Pedido = Record<string, any>;
async function servidorFalso(page: Page): Promise<{ fala: Pedido[]; verif: Pedido[] }> {
  const fala: Pedido[] = [], verif: Pedido[] = [];
  await page.route("**/api/fala-livre/status", r => r.fulfill({ json: { modelo: "falso", carregado: true } }));
  await page.route("**/api/fala-livre/verificar", async r => {
    verif.push(JSON.parse(r.request().postData() ?? "{}"));
    await r.fulfill({ json: { versao: "verif-v8", nao_suportadas: 0, manipulacao: false, afirmacoes: [] } });
  });
  await page.route("**/api/fala-livre", async r => {
    fala.push(JSON.parse(r.request().postData() ?? "{}"));
    await r.fulfill({ json: { fala: `Resposta ${fala.length}.`, fatos_citados: [], fatos: [], estagio: "crianca", modelo: "falso", versao_prompt: "voz-v2", comando: null } });
  });
  return { fala, verif };
}
async function enviar(page: Page, pedidos: Pedido[], txt: string): Promise<void> {
  const n = pedidos.length + 1;
  await page.locator("#conv-msg").fill(txt);
  await page.getByRole("button", { name: "Enviar" }).click();
  await expect.poll(() => pedidos.length).toBe(n);
  await expect(page.locator(".mc-balao", { hasText: `Resposta ${n}.` })).toBeVisible();
}
const irPara = (page: Page, rota: string) => page.evaluate(r => { location.hash = r; }, rota);
async function ligarRede(page: Page): Promise<void> {
  await irPara(page, "#/config");
  await page.locator(".mc-cfg .hx-linha", { hasText: "Fala do pet" }).click();
  await page.getByRole("radio", { name: /^Livre/ }).click();                  /* em Ajustes os modos sao radios */
  const chave = page.getByRole("switch", { name: /Fala pela rede/ });
  await expect(chave).not.toBeChecked();                                   /* desligada por padrao */
  await chave.check();
  expect(await page.evaluate(c => localStorage.getItem(c + "-fala-rede"), CHAVE)).toBe("1");
}

test("Fala pela rede: desligada por padrao e, num pet que nao e modular, a chave nao muda nada e a tela diz isso", async ({ browser }) => {
  test.setTimeout(120_000);
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  await semear(page, SAVE);
  const { fala, verif } = await servidorFalso(page);
  await page.goto(APP + "#/conversar/chat");
  await page.getByRole("button", { name: "Livre", exact: true }).click();
  await enviar(page, fala, "primeira");
  expect(fala[0].conceitos).toBeUndefined();
  expect(fala[0].estado.estado).toBeDefined();                              /* o estadoDoPet de sempre */
  await expect.poll(() => verif.length).toBe(1);
  expect(verif[0].conceitos).toBeUndefined();

  await ligarRede(page);
  await expect(page.getByText("Este pet não tem uma decisão do cérebro modular")).toBeVisible();
  await irPara(page, "#/conversar/chat");
  await enviar(page, fala, "segunda");
  expect(fala[1].conceitos).toBeUndefined();
  expect(Object.keys(fala[1]).sort()).toEqual(Object.keys(fala[0]).sort());
  expect(fala[1].estado.estado).toBeDefined();
  await ctx.close();
});

test("Fala pela rede: no pet de teste do modular o pedido leva so os conceitos do dec-v2 e a identidade", async ({ browser }) => {
  test.setTimeout(240_000);
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  await semear(page);
  const { fala, verif } = await servidorFalso(page);
  /* chocar o ovo de teste (v16, modular) e abri-lo, como no e2e do laboratorio */
  await page.goto(APP + "#/config/laboratorio");
  await page.getByRole("switch").first().check();
  await page.getByRole("button", { name: "Chocar o ovo de teste" }).click();
  await page.getByRole("button", { name: "Abrir", exact: true }).click();
  await expect(page.locator(".topo-lab .lab-selo")).toBeVisible();
  await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
  await expect(page.locator("#pet-painel").getByRole("heading", { name: "O peso de cada módulo nesta escolha" })).toBeVisible({ timeout: 90_000 });

  await ligarRede(page);
  await expect(page.getByText("Este pet não tem uma decisão do cérebro modular")).toHaveCount(0);
  await irPara(page, "#/conversar/chat");
  await enviar(page, fala, "oi, tudo bem?");
  const p = fala[0];
  expect(Object.keys(p.estado)).toEqual(["identidade"]);
  expect(Object.keys(p.estado.identidade).sort()).toEqual(["estagio", "forma"]);
  expect(p.conceitos.versao).toBe("dec-v2");
  expect(p.conceitos.conceitos).toHaveLength(12);
  expect(p.comando).toBe(true);
  for (const proibido of ["motivos", "memorias", "desejo", "temperamento", "carater", "vinculo"]) expect(JSON.stringify(p)).not.toContain(proibido);
  await expect.poll(() => verif.length).toBe(1);
  expect(verif[0].conceitos.versao).toBe("dec-v2");
  expect(verif[0].fatos).toEqual([]);
  await ctx.close();
});
