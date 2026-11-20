/* As recompensas e o mural (MMO7; docs/TAREFA_V3_MMO.md, a secao da MMO7) no build COM a chave do servidor, contra um servidor falso (o
   `page.route`, na mesma origem da pagina), como o cais.spec.ts. A prancha do mural e dos selos esta pendente com o Matheus: a tela e o
   minimo, e o teste confere o que ela mostra, nao o desenho. Cobre:
   - o cais aberto busca os premios uma vez (as tacas da ilha) e "Mural e premios" mostra o titulo no perfil, o Respeito, os selos, as tacas,
     os recordes das tres instalacoes e os campeoes; "Voltar a semana" volta a tabela;
   - sem a conta (401), o mural pede a conta;
   - no celular (390 px), sem rolagem de lado.
   Nada aqui muda o motor, o save nem o registro do Tamer. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { APP, CAMINHO_API } from "./comum.ts";

const CHAVE = "digilab-web-v21-sprites";
const CHAMPION = (JSON.parse(readFileSync(new URL("../e2e/saves.json", import.meta.url), "utf8")) as Record<string, object>).champion;
const ATE10 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const AGORA = new Date("2026-11-25T15:00:00Z");
const PREMIOS = {
  titulo_atual: [{ semana: "2026-11-16", numero: 47, estagio: "Champion", texto: "Campeão Champion da semana 47", congelou_em: "2026-11-23T04:00:00.000Z", no_perfil_ate: "2026-11-30T04:00:00.000Z" }],
  titulos: [{ semana: "2026-11-16", numero: 47, estagio: "Champion", texto: "Campeão Champion da semana 47", congelou_em: "2026-11-23T04:00:00.000Z", no_perfil_ate: "2026-11-30T04:00:00.000Z" }],
  selos: { total: 2, lista: [{ dia: "2026-11-24", posicao: 1, vitorias: 4 }, { dia: "2026-11-19", posicao: 6, vitorias: 2 }] },
  enfeites: [{ temporada: 1, de: "2026-11-02", ate: "2026-11-23", melhor: { semana: "2026-11-16", estagio: "Champion", posicao: 1 } }],
  recordes: { torre: { valor: 7, visto_em: "2026-11-18T15:00:00.000Z" }, fabrica: null, salao: null },
  respeito: { conferido: 140, titulos: 100, selos: 40, como: "..." }, temporada_atual: 1,
};
const MURAL = {
  recordes: { torre: [{ posicao: 1, apelido: "Agumon#1001", valor: 12, visto_em: "x", voce: false }, { posicao: 2, apelido: "Gabumon#1002", valor: 7, visto_em: "x", voce: true }],
    fabrica: [{ posicao: 1, apelido: "Agumon#1001", valor: 3, visto_em: "x", voce: false }], salao: [] },
  total: { torre: 2, fabrica: 1, salao: 0 },
  titulos: [{ semana: "2026-11-16", numero: 47, estagio: "Champion", texto: "Campeão Champion da semana 47", apelido: "Gabumon#1002", voce: true },
    { semana: "2026-11-16", numero: 47, estagio: "Rookie", texto: "Campeão Rookie da semana 47", apelido: "Agumon#1001", voce: false }],
};
const linha = (posicao: number, apelido: string, pontos: number, voce = false) =>
  ({ posicao, apelido, pontos, rivais_vencidos: posicao, lutas_usadas: 10 + posicao, hora_dos_pontos: null, voce });

async function servidorFalso(page: Page): Promise<{ sessao: boolean; pedidos: string[] }> {
  const s = { sessao: true, pedidos: [] as string[] };
  await page.route(u => u.pathname.startsWith(CAMINHO_API + "/"), async route => {
    const caminho = new URL(route.request().url()).pathname.slice(CAMINHO_API.length);
    s.pedidos.push(caminho);
    const json = (status: number, corpo: unknown) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(corpo) });
    if (caminho === "/semanas") { await json(200, { atual: "2026-11-23", fecha_em: "2026-11-30T03:00:00.000Z", congela_em: "2026-11-30T04:00:00.000Z", fechadas: [] }); return; }
    if (!s.sessao) { await json(401, { erro: "sem sessão" }); return; }
    if (caminho === "/premios") { await json(200, PREMIOS); return; }
    if (caminho === "/mural") { await json(200, MURAL); return; }
    if (caminho === "/semanas/2026-11-23/tabelas") {
      await json(200, { semana: "2026-11-23", estado: "aberta", congela_em: "2026-11-30T04:00:00.000Z",
        estagios: { Rookie: [], Champion: [linha(1, "Gabumon#1002", 40, true)], Ultimate: [], Mega: [] }, total: { Rookie: 0, Champion: 1, Ultimate: 0, Mega: 0 } });
      return;
    }
    await json(404, { erro: "rota desconhecida" });
  });
  return s;
}
async function abrir(page: Page, w: number, h: number): Promise<{ sessao: boolean; pedidos: string[] }> {
  await page.setViewportSize({ width: w, height: h });
  await page.clock.setFixedTime(AGORA);
  const s = await servidorFalso(page);
  await page.goto("/Assets/digilab_atlas_up_pecas.json");
  await page.evaluate(([chave, save, nivel]) => {
    localStorage.clear();
    localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 7, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-guardados", "[]"); localStorage.setItem(chave + "-dicas-ligadas", "0");
    localStorage.setItem(chave + "-nivel", nivel); localStorage.setItem(chave, save);
  }, [CHAVE, JSON.stringify(CHAMPION), JSON.stringify({ marcos: ATE10, cartoes: ATE10 })] as const);
  await page.goto(APP + "?cameradev=1#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  return s;
}

test("o cais aberto busca as taças, e o mural mostra os prêmios e os recordes (1920 px)", async ({ page }, info) => {
  const err: string[] = [];
  page.on("pageerror", x => err.push("pageerror: " + x.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) err.push("console: " + m.text()); });
  const s = await abrir(page, 1920, 950);
  await expect.poll(() => s.pedidos.filter(p => p === "/premios").length).toBe(1);
  /* a taca perto do cais (so vista): a foto vai para o relatorio */
  await page.waitForFunction(() => typeof (window as any).__camera?.ir === "function");
  await page.evaluate(() => (window as any).__camera.ir("cais", { zoom: 0.7 }));
  await page.waitForTimeout(1500);
  await page.screenshot({ path: info.outputPath("ilha_taca.png") });
  await page.evaluate(() => { location.hash = "#/cais"; });
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  await page.getByTestId("ca-abrir-mural").click();
  await expect(page.getByTestId("ca-premios")).toBeVisible();
  await expect(page.getByTestId("ca-mural")).toContainText("Campeão Champion da semana 47");
  await expect(page.getByTestId("ca-respeito")).toHaveText("140");
  await expect(page.getByTestId("ca-selos")).toContainText("2");
  await expect(page.getByTestId("ca-selos")).toContainText("24/11");
  await expect(page.getByTestId("ca-tacas")).toHaveText("T1");
  await expect(page.getByTestId("ca-mural-torre").locator("tbody tr")).toHaveCount(2);
  await expect(page.getByTestId("ca-mural-torre").locator("tr.ca-eu")).toContainText("Gabumon#1002");
  await expect(page.getByTestId("ca-mural-salao")).toContainText("Ninguém tem recorde conferido ainda.");
  await expect(page.getByTestId("ca-mural-titulos").locator("tbody tr")).toHaveCount(2);
  await page.screenshot({ path: info.outputPath("mural_1920.png") });
  await page.getByTestId("ca-voltar-semana").click();
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  expect(s.pedidos.filter(p => p === "/mural")).toHaveLength(1);
  expect(err).toEqual([]);
});

test("sem a conta, o mural pede a conta", async ({ page }) => {
  const s = await abrir(page, 1920, 950);
  await page.evaluate(() => { location.hash = "#/cais"; });
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  s.sessao = false;
  await page.getByTestId("ca-abrir-mural").click();
  await expect(page.getByTestId("ca-mural")).toContainText("O mural pede a conta");
});

test("no celular (390 px), o mural cabe sem rolar de lado", async ({ page }, info) => {
  await abrir(page, 390, 844);
  await page.evaluate(() => { location.hash = "#/cais"; });
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  await page.getByTestId("ca-abrir-mural").click();
  await expect(page.getByTestId("ca-premios")).toBeVisible();
  await page.screenshot({ path: info.outputPath("mural_390.png"), fullPage: true });
  const lado = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(lado).toBeLessThanOrEqual(0);
});
