/* O laboratorio do modular (docs/TAREFA_V3_LAB_MODULAR.md, LM5b): a chave desligada, chocar o ovo de teste (v16), abrir (o pet aparece na tela Pet
   com o selo "experimental", sem trocar o pet ativo), o painel do DigiBrain mostra o motivo, e descartar com confirmacao (so o save do teste some). */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";
import { VERSAO_PET } from "../motor/constantes";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";

async function semear(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(chave => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
  }, CHAVE);
}
const guardado = (page: Page, chave: string) => page.evaluate(k => localStorage.getItem(k), chave);
/** o pet de hoje no save: a semente e a versao (o registro cresce com o tempo enquanto ele e o ativo; o do teste nunca o toca) */
const hoje = async (page: Page) => { const s = JSON.parse((await guardado(page, CHAVE))!); return { semente: s.semente, versao: s.versao }; };

test("o laboratorio: chocar, abrir, ver o motivo, descartar com confirmacao", async ({ page }) => {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await semear(page);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator(".lab-selo")).toHaveCount(0);       // a chave desligada: nada do laboratorio na tela Pet
  await page.locator(".acoes-pet button", { hasText: "Carinho" }).click();      // uma acao do dono grava o save do pet de hoje
  const petDeHoje = await hoje(page);
  expect(petDeHoje.versao).toBe(VERSAO_PET); // o ovo padrao de hoje (a versao atual; era a v17 ate a v18 do empurrao, #661)

  /* Ajustes > Laboratorio: a chave vem desligada e o ovo de teste so aparece com ela ligada */
  await page.goto(APP + "#/config/laboratorio");
  await expect(page.getByText("Modo laboratório · desligado")).toBeVisible();
  await expect(page.getByRole("button", { name: "Chocar o ovo de teste" })).toHaveCount(0);
  await page.getByRole("switch").first().check();
  await expect(page.getByText("Modo laboratório · ligado")).toBeVisible();
  await page.getByRole("button", { name: "Chocar o ovo de teste" }).click();
  await expect(page.getByText("cérebro modular · versão 16")).toBeVisible();
  await expect(page.getByRole("button", { name: "Chocar o ovo de teste" })).toHaveCount(0);      // so um por vez
  expect(JSON.parse((await guardado(page, CHAVE + "-lab"))!).versao).toBe(16);
  expect(await hoje(page)).toEqual(petDeHoje);

  /* Abrir: o pet de teste na tela Pet, com o selo; o pet de hoje segue o ativo */
  await page.getByRole("button", { name: "Abrir", exact: true }).click();
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator(".topo-lab .lab-selo")).toBeVisible();
  expect(JSON.parse(await page.evaluate(() => (window as any).__digilab.registro() as string)).versao).toBe(16);

  /* o DigiBrain do modular abre no scan (o mesmo modal pequeno do A, pedido do Matheus de 2026-11-11): o mapa dos modulos com a decisao (o tempo
     anda a 10 min/s: a primeira decisao sai em poucos segundos); o motivo inteiro fica no mapa em texto */
  await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
  const painel = page.locator("#pet-painel");
  await expect(painel).toHaveClass(/scan--lab/);
  await expect(painel.locator("svg.mp--lab")).toBeVisible({ timeout: 90_000 });
  await expect(painel.locator("svg.mp--lab .mp-esc")).toHaveCount(1);
  await expect(painel.locator("svg.mp--lab [data-termo]").first()).toBeAttached();
  /* a captura da prancha (docs/pranchas/digibrain-lab/), so com DIGILAB_CAPTURA: o mapa e o mapa em texto */
  const captura = process.env.DIGILAB_CAPTURA;
  if (captura) await painel.locator(".scan-in").screenshot({ path: `${captura}/scan_lab_mapa_${page.viewportSize()!.width}.png` });
  await painel.getByRole("button", { name: "O mapa em texto" }).click();
  await expect(painel.getByRole("heading", { name: "O peso de cada módulo nesta escolha" })).toBeVisible();
  await expect(painel.getByRole("heading", { name: "O que aconteceu antes" })).toBeVisible();
  if (captura) await painel.locator(".scan-in").screenshot({ path: `${captura}/scan_lab_texto_${page.viewportSize()!.width}.png` });
  await expect(painel.getByRole("heading", { name: "Lembrança da vez" })).toBeVisible();
  await expect(painel.getByRole("heading", { name: "Intenção em curso" })).toBeVisible();
  await expect(painel.getByRole("heading", { name: "As opções e a chance de cada uma" })).toBeVisible();
  await expect(painel.getByRole("heading", { name: "O que mudaria a escolha" })).toBeVisible();
  await expect(painel.locator(".db-barras--div li").first()).toBeVisible();
  await expect(painel.getByText(/[Pp]ensando|[Ss]entindo|[Qq]uerendo/)).toHaveCount(0);
  await page.getByRole("button", { name: "Fechar DigiBrain" }).click();

  /* o save do pet de hoje nao foi tocado pelo pet de teste */
  expect(await hoje(page)).toEqual(petDeHoje);

  /* Descartar: confirmacao sem digitar, o foco em Cancelar; Cancelar nao apaga; Descartar apaga so o save do teste */
  await page.goto(APP + "#/config/laboratorio");
  await page.getByRole("button", { name: "Descartar", exact: true }).click();
  const dialogo = page.getByRole("alertdialog");
  await expect(dialogo).toBeVisible();
  await expect(dialogo.getByRole("button", { name: "Cancelar" })).toBeFocused();
  await expect(dialogo.getByText("Seus pets de hoje não são tocados")).toBeVisible();
  await dialogo.getByRole("button", { name: "Cancelar" }).click();
  await expect(page.getByRole("alertdialog")).toHaveCount(0);
  expect(await guardado(page, CHAVE + "-lab")).not.toBeNull();
  await page.getByRole("button", { name: "Descartar", exact: true }).click();
  await page.getByRole("alertdialog").getByRole("button", { name: "Descartar" }).click();
  await expect(page.getByText(/Nenhum pet de teste ainda/)).toBeVisible();
  expect(await guardado(page, CHAVE + "-lab")).toBeNull();
  expect(await hoje(page)).toEqual(petDeHoje);
  expect(erros).toEqual([]);
});
