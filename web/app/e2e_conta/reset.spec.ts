/* O reset e as duas pontuacoes (MMO8; a prancha docs/pranchas/ux-reset/, UX-RS-1 a 7 APROVADAS em 2026-11-19) no build COM a chave do
   servidor, contra um servidor falso (o `page.route`, na mesma origem da pagina), como o mural.spec.ts. Cobre:
   - Aposentar em Meus pets com o Champion do e2e (antes do Ultimate: "sem bonus"): a confirmacao em dois passos, o feito, a escolha do
     brasao sem "Voltar", o ovo novo, o aposentado em Geracoes, o reset no registro do Tamer (versao 11) e o envio sozinho do registro do
     aposentado (POST /envios, UX-RS-4);
   - as abas do cais: Tamers (o Respeito, o nivel, "Lendario", a sua linha depois do salto) e Digimon (o maximo historico, "aposentado");
   - o perfil com as duas pontuacoes (o Respeito conferido grande, o do jogo ao lado, o nivel, o melhor Digimon) e "Ver os rankings no cais";
   - no celular (390 px), o cais com as abas e o Aposentar sem rolar de lado.
   O pet Ultimate, Mega e com a Liga nao tem save no e2e (chegar la pelo motor leva dias de vida simulada): a escada e o bonus estao nos
   testes do Vitest (test/mmo8_reset.test.ts, a previa). */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { GrupoDoJogo, VERSAO_GRUPO } from "../motor/index.ts";
import { APP, CAMINHO_API } from "./comum.ts";

const CHAVE = "digilab-web-v21-sprites";
const CHAMPION = (JSON.parse(readFileSync(new URL("../e2e/saves.json", import.meta.url), "utf8")) as Record<string, { semente: number }>).champion;
const ATE10 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const AGORA = new Date("2026-11-25T15:00:00Z");
const RESPEITO = { conferido: 2340, lideres: 600, liga: 500, resets: 900, titulos: 200, selos: 140, contagem: { lideres: 6, liga: true, resets: 2, titulos: 2, selos: 7 },
  nivel: 12, titulo: null, chegou_em: "2026-11-24T15:00:00.000Z", como: "..." };
const PREMIOS = { titulo_atual: [], titulos: [], selos: { total: 0, lista: [] }, enfeites: [], recordes: { torre: null, fabrica: null, salao: null }, respeito: RESPEITO, temporada_atual: 1 };
const t = (posicao: number, apelido: string, respeito: number, voce = false, titulo: string | null = null) =>
  ({ posicao, apelido, respeito, nivel: 10 + Math.floor(respeito / 1000), titulo, chegou_em: "2026-11-20T15:00:00.000Z", voce });
const TAMERS = { linhas: [t(1, "Gabumon#0317", 11240, false, "Tamer Lendário"), ...[2, 3, 4, 5, 6, 7, 8].map(p => t(p, `Palmon#77${p}0`, 9000 - p * 800)), t(14, "Agumon#4821", 2340, true)], total: 20 };
const d = (posicao: number, forma: string, apelido: string, pontos: number, aposentado: boolean, voce = false, pet?: number) =>
  ({ posicao, apelido, forma, estagio: "Ultimate", pontos, aposentado, voce, ...(pet !== undefined ? { pet } : {}) });
const DIGIMONS = { linhas: [d(1, "Gallantmon", "Palmon#7740", 2310, false), d(2, "MetalGarurumon", "Gabumon#0317", 1940, true),
  d(3, "WarGrowlmon", "Agumon#4821", 1120, true, true, 999), d(4, "Angewomon", "Patamon#5589", 1080, false)], total: 4 };

interface Falso { sessao: boolean; pedidos: string[]; envios: unknown[] }
async function servidorFalso(page: Page): Promise<Falso> {
  const s: Falso = { sessao: true, pedidos: [], envios: [] };
  await page.route(u => u.pathname.startsWith(CAMINHO_API + "/"), async route => {
    const caminho = new URL(route.request().url()).pathname.slice(CAMINHO_API.length);
    s.pedidos.push(route.request().method() + " " + caminho);
    const json = (status: number, corpo: unknown) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(corpo) });
    if (caminho === "/semanas") { await json(200, { atual: "2026-11-23", fecha_em: "2026-11-30T03:00:00.000Z", congela_em: "2026-11-30T04:00:00.000Z", fechadas: [] }); return; }
    if (caminho === "/auth/provedores") { await json(200, [{ nome: "falso", ligado: true }]); return; }
    if (!s.sessao) { await json(401, { erro: "sem sessão" }); return; }
    if (caminho === "/conta") { await json(200, { conta: { apelido: "Agumon#4821", criada_em: "2026-11-12T15:00:00.000Z" }, provedores: ["google"], consentimentos: [], csrf: "csrf-falso" }); return; }
    if (caminho === "/conta/aparelhos") { await json(200, [{ id: "a1", nome: "Chrome no Windows", visto_em: "2026-11-25T14:00:00.000Z", atual: true }]); return; }
    if (caminho === "/premios") { await json(200, PREMIOS); return; }
    if (caminho === "/tamers") { await json(200, TAMERS); return; }
    if (caminho === "/digimons") { await json(200, DIGIMONS); return; }
    if (caminho === "/mural") { await json(200, { recordes: { torre: [], fabrica: [], salao: [] }, total: { torre: 0, fabrica: 0, salao: 0 }, titulos: [] }); return; }
    if (caminho === "/envios" && route.request().method() === "POST") { s.envios.push(route.request().postDataJSON()); await json(201, { resultado: "aceito", lutas: [], semanas: [], ms: {} }); return; }
    if (caminho === "/semanas/2026-11-23/tabelas") {
      await json(200, { semana: "2026-11-23", estado: "aberta", congela_em: "2026-11-30T04:00:00.000Z",
        estagios: { Rookie: [], Champion: [], Ultimate: [], Mega: [] }, total: { Rookie: 0, Champion: 0, Ultimate: 0, Mega: 0 } });
      return;
    }
    await json(404, { erro: "rota desconhecida" });
  });
  return s;
}
/** o par dos dois pets (os ovos novos nascem em par): um grupo de hoje, com meia hora de vida */
function savePar(): string {
  const g = new GrupoDoJogo(424242, VERSAO_GRUPO);
  g.avancar(30);
  return JSON.stringify({ semente: g.semente, log: g.log, versao: g.versao, grupo: true, foco: g.ids[0] });
}
async function abrir(page: Page, w: number, h: number, rota = "#/pet/estado", save: string = JSON.stringify(CHAMPION)): Promise<Falso> {
  await page.setViewportSize({ width: w, height: h });
  await page.clock.setFixedTime(AGORA);
  const s = await servidorFalso(page);
  await page.goto("/Assets/digilab_atlas_up_pecas.json");
  await page.evaluate(([chave, save, nivel]) => {
    localStorage.clear();
    localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 10, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-guardados", "[]"); localStorage.setItem(chave + "-dicas-ligadas", "0");
    localStorage.setItem(chave + "-nivel", nivel); localStorage.setItem(chave, save);
  }, [CHAVE, save, JSON.stringify({ marcos: ATE10, cartoes: ATE10 })] as const);
  await page.goto(APP + "?cameradev=1" + rota);
  return s;
}
const erros = (page: Page): string[] => {
  const err: string[] = [];
  page.on("pageerror", x => err.push("pageerror: " + x.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) err.push("console: " + m.text()); });
  return err;
};

test("aposentar o Champion: dois passos, o feito, o ovo novo do brasão, Gerações, o reset no Tamer e o envio (1920 px)", async ({ page }, info) => {
  const err = erros(page), s = await abrir(page, 1920, 950);
  await expect(page.locator(".pet-tela")).toBeVisible();
  await page.getByRole("button", { name: /Meus pets/ }).first().click();
  await page.getByTestId("mp-aposentar").click();
  await expect(page.getByTestId("rs-sem-bonus")).toContainText("O bônus começa no Ultimate");
  await page.screenshot({ path: info.outputPath("reset_sem_bonus_1920.png") });
  await page.getByTestId("rs-aposentar").click();
  await expect(page.getByTestId("rs-confirmar")).toBeVisible();
  await expect(page.getByTestId("rs-aposentar-sempre")).toBeDisabled();
  await page.getByTestId("rs-entendi").click();
  await page.screenshot({ path: info.outputPath("reset_confirmar_1920.png") });
  await page.getByTestId("rs-aposentar-sempre").click();
  await expect(page.getByTestId("rs-feito")).toContainText("foi para Gerações");
  await page.screenshot({ path: info.outputPath("reset_feito_1920.png") });
  /* o reset no Tamer (a versao 11), o aposentado em Geracoes e o envio sozinho do registro dele */
  const salvo = await page.evaluate(chave => ({ tamer: JSON.parse(localStorage.getItem(chave + "-tamer")!), ger: JSON.parse(localStorage.getItem(chave + "-geracoes") || "[]") }), CHAVE);
  expect(salvo.tamer.versao).toBe(11);
  expect(salvo.tamer.log.filter((e: unknown[]) => e[0] === "reset")).toHaveLength(1);
  expect(salvo.ger.map((g: { semente: number }) => g.semente)).toEqual([CHAMPION.semente]);
  await expect.poll(() => s.envios.length).toBe(1);
  const env = s.envios[0] as { pet: { semente: number }; tamer: { versao: number; log: unknown[][] } };
  expect(env.pet.semente).toBe(CHAMPION.semente);
  expect(env.tamer.versao).toBe(11);
  /* o ovo novo: a escolha do brasao sem "Voltar" */
  await page.getByTestId("rs-brasao").click();
  await expect(page.locator(".brasao-tela")).toBeVisible();
  await expect(page.locator(".brasao-tela").getByRole("button", { name: "Voltar" })).toHaveCount(0);
  await page.screenshot({ path: info.outputPath("reset_brasao_1920.png") });
  await page.locator(".br-card").first().click();
  await expect(page.locator(".brasao-tela")).toHaveCount(0);
  const depois = await page.evaluate(chave => ({ pet: JSON.parse(localStorage.getItem(chave)!), pendente: localStorage.getItem(chave + "-reset-pendente"),
    guardados: JSON.parse(localStorage.getItem(chave + "-guardados") || "[]") }), CHAVE);
  expect(depois.pendente).toBeNull();
  expect(depois.guardados).toEqual([]);
  expect(depois.pet.semente ?? depois.pet.pets?.[0]?.semente).not.toBe(CHAMPION.semente);
  expect(err).toEqual([]);
});

test("o reset que espera o ovo sobrevive a recarregar: a escolha do brasão abre sozinha, sem Voltar", async ({ page }) => {
  await abrir(page, 1920, 950);
  await page.getByRole("button", { name: /Meus pets/ }).first().click();
  await page.getByTestId("mp-aposentar").click();
  await page.getByTestId("rs-aposentar").click();
  await page.getByTestId("rs-entendi").click();
  await page.getByTestId("rs-aposentar-sempre").click();
  await expect(page.getByTestId("rs-feito")).toBeVisible();
  await page.reload();
  await expect(page.locator(".brasao-tela")).toBeVisible();
  await expect(page.locator(".brasao-tela").getByRole("button", { name: "Voltar" })).toHaveCount(0);
});

test("o par se aposenta junto, num reset só, e o ovo novo é outro par (1920 px)", async ({ page }, info) => {
  const err = erros(page), par = JSON.parse(savePar());
  await abrir(page, 1920, 950, "#/pet/estado", JSON.stringify(par));
  await expect(page.locator(".pet-tela")).toBeVisible();
  await page.getByRole("button", { name: /Meus pets/ }).first().click();
  await page.getByTestId("mp-aposentar").click();
  await expect(page.getByTestId("rs-sem-bonus")).toBeVisible();
  await expect(page.getByTestId("rs-pet")).toHaveCount(2);
  await page.screenshot({ path: info.outputPath("reset_par_1920.png") });
  await page.getByTestId("rs-aposentar").click();
  await page.getByTestId("rs-entendi").click();
  await page.getByTestId("rs-aposentar-sempre").click();
  await expect(page.getByTestId("rs-feito")).toContainText("foram para Gerações");
  const salvo = await page.evaluate(chave => ({ tamer: JSON.parse(localStorage.getItem(chave + "-tamer")!), ger: JSON.parse(localStorage.getItem(chave + "-geracoes") || "[]") }), CHAVE);
  expect(salvo.tamer.log.filter((e: unknown[]) => e[0] === "reset")).toHaveLength(1);
  expect(salvo.ger).toHaveLength(1);
  expect(salvo.ger[0]).toMatchObject({ semente: par.semente, grupo: true });
  await page.getByTestId("rs-brasao").click();
  await page.locator(".br-card").first().click();
  await expect(page.locator(".brasao-tela")).toHaveCount(0);
  const depois = await page.evaluate(chave => JSON.parse(localStorage.getItem(chave)!), CHAVE);
  expect(depois.grupo).toBe(true);
  expect(depois.semente).not.toBe(par.semente);
  expect(err).toEqual([]);
});

test("as abas do cais: Tamers pelo Respeito e Digimon pelo total da vida (1920 px)", async ({ page }, info) => {
  const err = erros(page);
  await abrir(page, 1920, 950, "#/cais");
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  await page.getByTestId("ca-aba-tamers").click();
  await expect(page.getByTestId("rs-tamers")).toBeVisible();
  await expect(page.getByTestId("rs-tamers").locator("tbody tr").first()).toContainText("Lendário");
  await expect(page.getByTestId("rs-tamers-voce")).toContainText("2 340");
  await expect(page.getByTestId("rs-tamers-voce")).toContainText("Nv 12");
  await page.screenshot({ path: info.outputPath("rankings_tamers_1920.png") });
  await page.getByTestId("ca-aba-digimon").click();
  await expect(page.getByTestId("rs-digimons")).toBeVisible();
  await expect(page.getByTestId("rs-digimons-seu")).toContainText("WarGrowlmon");
  await expect(page.getByTestId("rs-digimons-seu")).toContainText("aposentado");
  await page.screenshot({ path: info.outputPath("rankings_digimon_1920.png") });
  await page.getByTestId("ca-abrir-mural").click();
  await expect(page.getByTestId("ca-mural")).toBeVisible();
  await page.getByTestId("ca-aba-semana").click();
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  expect(err).toEqual([]);
});

test("o perfil com as duas pontuações e o caminho para os rankings (1920 px)", async ({ page }, info) => {
  const err = erros(page);
  await abrir(page, 1920, 950, "#/config/conta");
  await expect(page.getByTestId("ct-perfil")).toBeVisible();
  await expect(page.getByTestId("ct-respeito-conferido")).toHaveText("2 340");
  await expect(page.getByTestId("ct-respeito")).toContainText("0 no jogo");
  await expect(page.getByTestId("ct-nivel")).toHaveText("Nv 12");
  await expect(page.getByTestId("ct-digimon-pontos")).toHaveText("1 120");
  await expect(page.getByTestId("ct-digimon")).toContainText("3º");
  await page.getByTestId("ct-de-onde").locator("summary").click();
  await expect(page.getByTestId("ct-de-onde")).toContainText("+600");
  await page.screenshot({ path: info.outputPath("perfil_1920.png") });
  await page.getByTestId("ct-ver-rankings").click();
  await expect(page.getByTestId("rs-tamers")).toBeVisible();
  expect(err).toEqual([]);
});

test("no celular (390 px), o cais com as abas e o Aposentar cabem sem rolar de lado", async ({ page }, info) => {
  await abrir(page, 390, 844, "#/cais");
  await page.getByTestId("ca-aba-tamers").click();
  await expect(page.getByTestId("rs-tamers")).toBeVisible();
  await page.screenshot({ path: info.outputPath("rankings_tamers_390.png") });
  const lado = () => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(await lado()).toBeLessThanOrEqual(0);
  await page.goto(APP + "?cameradev=1#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  /* abaixo de 900 px, Meus pets fica no leque do retrato (o mobile minimo) */
  await page.locator(".mm-retrato").click();
  await page.getByRole("button", { name: "Meus pets" }).click();
  await page.getByTestId("mp-aposentar").click();
  await expect(page.getByTestId("rs-sem-bonus")).toBeVisible();
  await page.screenshot({ path: info.outputPath("reset_sem_bonus_390.png") });
  expect(await lado()).toBeLessThanOrEqual(0);
});
