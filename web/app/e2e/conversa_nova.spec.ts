/* CONVERSA_PET, M2 (D2, 2026-11-06): a chave "Conversa nova (teste)" (Ajustes, desligada por padrao) liga o prompt conversa-v1 e o historico de
   fronteira. Servidor falso (rota do Playwright, sem GPU): o pedido leva `prompt: "conversa-v1"` e so as trocas desta sessao e do estagio
   atual, cada uma com o estagio. Com a chave desligada o pedido e o de hoje. A fala nunca entra no registro do pet. */
import { expect, test } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 13, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120]] };

test("Conversa nova: desligada por padrao; ligada manda prompt conversa-v1 e o historico de fronteira", async ({ browser }) => {
  test.setTimeout(120_000);
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
    /* um balao antigo no log de apresentacao: aparece na tela, nao vai ao prompt */
    localStorage.setItem(chave + ".fala.jsonl", JSON.stringify({ versao: 2, t: 500, situacao: "conversa", fala_jogador: "conversa de ontem", fala: "Resposta de ontem.",
      fatos_citados: [], fatos: [], estagio: "crianca", modelo: "falso", versao_prompt: "livre-v9", semente: 1, verificacao: null, comando: null, comando_executado: false }) + "\n");
  }, [CHAVE, JSON.stringify(SAVE)] as const);
  const pedidos: Record<string, unknown>[] = [];
  await page.route("**/api/fala-livre/status", r => r.fulfill({ json: { modelo: "falso", carregado: true } }));
  await page.route("**/api/fala-livre/verificar", r => r.fulfill({ json: { nao_suportadas: 0, manipulacao: false, afirmacoes: [] } }));
  await page.route("**/api/fala-livre", async r => {
    pedidos.push(JSON.parse(r.request().postData() ?? "{}"));
    await r.fulfill({ json: { fala: `Resposta ${pedidos.length}.`, fatos_citados: [], fatos: [], estagio: "crianca", modelo: "falso", versao_prompt: "conversa-v1", comando: null } });
  });
  const enviar = async (txt: string, n: number) => {
    await page.locator("#conv-msg").fill(txt);
    await page.getByRole("button", { name: "Enviar" }).click();
    await expect.poll(() => pedidos.length).toBe(n);
    await expect(page.locator(".mc-balao", { hasText: `Resposta ${n}.` })).toBeVisible();
  };
  await page.goto(APP + "#/conversar/chat");
  await page.getByRole("button", { name: "Livre", exact: true }).click();
  await expect(page.locator(".mc-balao", { hasText: "Resposta de ontem." })).toBeVisible();

  /* desligada (padrao): o pedido e o de hoje */
  await enviar("primeira", 1);
  expect(pedidos[0].prompt).toBeUndefined();
  expect(pedidos[0].comando).toBe(true);

  /* liga a chave nos Ajustes (preferencia de tela, fora do registro do pet) */
  await page.goto(APP + "#/config");
  await page.locator(".mc-cfg .hx-linha", { hasText: "Fala do pet" }).click();
  const chave = page.getByRole("switch", { name: /Conversa nova/ });
  await expect(chave).not.toBeChecked();
  await chave.check();
  expect(await page.evaluate(c => localStorage.getItem(c + "-conversa-nova"), CHAVE)).toBe("1");
  await page.goto(APP + "#/conversar/chat");
  const registroAntes = await page.evaluate(() => JSON.parse((window as any).__digilab.registro()).log.length);
  await enviar("segunda", 2);
  await enviar("terceira", 3);
  expect(pedidos[1].prompt).toBe("conversa-v1");
  expect(pedidos[1].comando).toBe(true);
  expect(pedidos[1].historico).toEqual([]);                                   /* so as trocas feitas com a chave ligada nesta sessao */
  const h = pedidos[2].historico as string[][];
  expect(h).toHaveLength(1);
  expect(h[0].slice(0, 2)).toEqual(["segunda", "Resposta 2."]);
  expect(typeof h[0][2]).toBe("string");
  expect(JSON.stringify(h)).not.toContain("ontem");
  expect(await page.evaluate(() => JSON.parse((window as any).__digilab.registro()).log.length)).toBe(registroAntes);
});
