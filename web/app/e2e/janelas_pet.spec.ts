/* As janelas da tela do pet, etapa JN1 (docs/PLANO_UX_JANELAS.md): em Ajustes > Exibir ha uma chave por janela; esconder uma tira so
   ela da tela do pet; a escolha fica no navegador e nada entra no registro. E a chave unica de antes ("-detalhes-pet" = "0") comeca
   com as quatro janelas dela escondidas. So no desktop (a pilha e o minimapa sao de 900 px em diante). O save e o do camera_livre.spec. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };

async function abrir(browser: Browser, extra: Record<string, string> = {}): Promise<{ page: Page; erros: string[]; fechar: () => Promise<void> }> {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1920, height: 950 } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, ex]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
    for (const [k, v] of Object.entries(JSON.parse(ex) as Record<string, string>)) localStorage.setItem(chave + k, v);
  }, [CHAVE, JSON.stringify(SAVE), JSON.stringify(extra)] as const);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  return { page, erros, fechar: () => ctx.close() };
}
const registro = (page: Page) => page.evaluate(() => JSON.stringify(JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] !== "t")));
const janela = (page: Page, id: string) => page.locator(`.pet-hud [data-painel-pet='${id}']`);

test("Ajustes > Exibir: uma chave por janela; esconder tira só aquela janela, e nada entra no registro", async ({ browser }) => {
  test.setTimeout(120_000);
  const { page, erros, fechar } = await abrir(browser);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  /* o arranjo de hoje: as quatro janelas da pilha, a linha do agora e o minimapa */
  for (const id of ["estado", "acoes", "digibrain"]) await expect(janela(page, id)).toBeVisible();
  await expect(page.getByLabel("Minimapa da ilha")).toBeVisible({ timeout: 30_000 });
  await expect(page.locator(".agora-rot")).toBeVisible();
  const antes = await registro(page);

  await page.goto(APP + "#/config");
  await page.locator(".mc-cfg").getByRole("button", { name: "Exibir as janelas do pet" }).click();
  await expect(page).toHaveURL(/#\/config\/exibir$/);
  const chaves = page.locator(".mc-cfg").getByRole("switch");
  await expect(chaves).toHaveCount(6);
  for (const n of ["Estado atual", "Evolução", "Últimas ações", "DigiBrain", "Agora", "Minimapa"]) await expect(page.getByRole("switch", { name: "Exibir " + n })).toBeChecked();
  await page.getByRole("switch", { name: "Exibir Últimas ações" }).uncheck();
  await page.getByRole("switch", { name: "Exibir Minimapa" }).uncheck();
  /* a captura do relato (docs/pranchas/ux-janelas/capturas_codigo/), so com DIGILAB_CAPTURA */
  if (process.env.DIGILAB_CAPTURA) await page.screenshot({ path: `${process.env.DIGILAB_CAPTURA}/jn1_exibir_1920.png` });
  expect(JSON.parse(await page.evaluate(c => localStorage.getItem(c + "-janelas") ?? "null", CHAVE)).exibir).toMatchObject({ acoes: false, minimapa: false, estado: true, digibrain: true });

  await page.goto(APP + "#/pet/estado");
  await expect(janela(page, "estado")).toBeVisible();
  await expect(janela(page, "digibrain")).toBeVisible();
  await expect(janela(page, "acoes")).toHaveCount(0);
  await expect(page.getByLabel("Minimapa da ilha")).toHaveCount(0);
  if (process.env.DIGILAB_CAPTURA) await page.screenshot({ path: `${process.env.DIGILAB_CAPTURA}/jn1_pet_sem_acoes_1920.png` });
  /* a escolha sobrevive a recarregar */
  await page.reload();
  await expect(janela(page, "estado")).toBeVisible();
  await expect(janela(page, "acoes")).toHaveCount(0);
  expect(await registro(page)).toBe(antes);
  expect(erros).toEqual([]);
  await fechar();
});

test('a chave única de antes desligada: as quatro janelas dela começam escondidas, e ligar uma traz só ela', async ({ browser }) => {
  test.setTimeout(120_000);
  const { page, erros, fechar } = await abrir(browser, { "-detalhes-pet": "0" });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect(page.getByLabel("Minimapa da ilha")).toBeVisible({ timeout: 30_000 });
  /* a pilha pode continuar na tela so com a linha "TV" (o gosto visual vem ligado); as quatro janelas da chave antiga nao estao nela */
  for (const id of ["estado", "evolucao", "acoes", "digibrain"]) await expect(janela(page, id)).toHaveCount(0);
  await page.goto(APP + "#/config/exibir");
  for (const n of ["Estado atual", "Evolução", "Últimas ações", "DigiBrain"]) await expect(page.getByRole("switch", { name: "Exibir " + n })).not.toBeChecked();
  await expect(page.getByRole("switch", { name: "Exibir Agora" })).toBeChecked();
  await page.getByRole("switch", { name: "Exibir DigiBrain" }).check();
  await page.goto(APP + "#/pet/estado");
  await expect(janela(page, "digibrain")).toBeVisible();
  await expect(janela(page, "estado")).toHaveCount(0);
  expect(erros).toEqual([]);
  await fechar();
});
