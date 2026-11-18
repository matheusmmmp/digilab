/* O cais (MMO5; docs/TAREFA_V3_MMO.md, secoes 19 a 21; a prancha docs/pranchas/ux-cais/) no build COM a chave do servidor, contra um
   servidor falso: o `page.route` responde as rotas do servidor_web/src/envio/semanas.ts na mesma origem da pagina. Cobre:
   - trancado (Tamer Nv 9): a marca tracejada do minimapa, o cadeado "Nv 10" sobre o cais, e o cadeado e o endereco abrindo o cartao do
     motivo, sem nenhuma chamada ao servidor;
   - aberto (o marco 10): a semana, a tabela do estagio do pet, a linha de quem olha depois do salto, "Ver todas", os outros estagios,
     "Atualizar", a semana fechada com o resultado e "Conferir a semana" (o segredo), e "Ir para a Arena";
   - sem a conta (401) e sem resposta (a rede fora), e a volta com "Tentar de novo";
   - a folha do celular (390 px): 6 linhas, sem a coluna das lutas, sem rolagem de lado; e o endereco do cais trancado;
   - o cartao de destrave do nivel 10 e o "Ir" dele.
   Os estados saem de uma chave -nivel semeada e do Champion de e2e/saves.json. O relogio da pagina fica parado numa quarta-feira (so o
   Date; os temporizadores correm). Nada aqui muda o motor, o save nem o registro do Tamer. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { APP, CAMINHO_API } from "./comum.ts";

const CHAVE = "digilab-web-v21-sprites";
const CHAMPION = (JSON.parse(readFileSync(new URL("../e2e/saves.json", import.meta.url), "utf8")) as Record<string, object>).champion;
const ATE9 = [1, 2, 3, 4, 5, 6, 7, 8, 9], ATE10 = [...ATE9, 10];
/* quarta, 18/11/2026, 12:00 de Brasilia; a semana abre na segunda 16 e fecha no domingo 22, 23:59 */
const AGORA = new Date("2026-11-18T15:00:00Z");
const ATUAL = "2026-11-16", ANTES = "2026-11-09", SEGREDO = "ab".repeat(32);

const linha = (posicao: number, apelido: string, pontos: number, voce = false) =>
  ({ posicao, apelido, pontos, rivais_vencidos: posicao, lutas_usadas: 10 + posicao, hora_dos_pontos: null, voce });
interface Falso { sessao: boolean; fora: boolean; pedidos: string[] }
/** o servidor falso: as rotas das semanas; qualquer outra rota do servidor responde 404 e fica na lista dos pedidos */
async function servidorFalso(page: Page): Promise<Falso> {
  const s: Falso = { sessao: true, fora: false, pedidos: [] };
  const aberta = Array.from({ length: 12 }, (_, i) => linha(i + 1, `Tamer#${i + 1}`, 300 - i * 20, i === 10));
  const fechada = [linha(1, "Tamer#1", 280), linha(2, "Tamer#11", 240, true), linha(3, "Tamer#2", 200)];
  await page.route(u => u.pathname.startsWith(CAMINHO_API + "/"), async route => {
    const caminho = new URL(route.request().url()).pathname.slice(CAMINHO_API.length);
    s.pedidos.push(caminho);
    if (s.fora) { await route.abort("connectionrefused"); return; }
    const json = (status: number, corpo: unknown) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(corpo) });
    if (caminho === "/semanas") {
      await json(200, { atual: ATUAL, fecha_em: "2026-11-23T03:00:00.000Z", congela_em: "2026-11-23T04:00:00.000Z",
        fechadas: [{ semana: ANTES, publicado_em: "2026-11-16T04:00:00.000Z" }] });
      return;
    }
    const m = /^\/semanas\/(\d{4}-\d{2}-\d{2})\/(tabelas|segredo)$/.exec(caminho);
    if (!m) { await json(404, { erro: "rota desconhecida" }); return; }
    const [, semana, o] = m, eFechada = semana === ANTES;
    if (o === "segredo") {
      if (eFechada) await json(200, { semana, segredo: SEGREDO, publicado_em: "2026-11-16T04:00:00.000Z", como: "..." });
      else await json(404, { motivo: "semana_aberta", erro: "o segredo sai quando a semana congela" });
      return;
    }
    if (!s.sessao) { await json(401, { erro: "sem sessão" }); return; }
    const champion = eFechada ? fechada : aberta;
    await json(200, { semana, estado: eFechada ? "fechada" : "aberta", congela_em: eFechada ? "2026-11-16T04:00:00.000Z" : "2026-11-23T04:00:00.000Z",
      estagios: { Rookie: [linha(1, "Tamer#7", 30)], Champion: champion, Ultimate: [], Mega: [] },
      total: { Rookie: 1, Champion: champion.length, Ultimate: 0, Mega: 0 } });
  });
  return s;
}

/** semeia por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele ao fechar) */
async function semear(page: Page, marcos: number[], o: { cartoes?: number[]; dicas?: boolean } = {}): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, save, nivel, dicas]) => {
    localStorage.clear();
    localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 7, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-guardados", "[]"); localStorage.setItem(chave + "-dicas-ligadas", dicas);
    localStorage.setItem(chave + "-nivel", nivel); localStorage.setItem(chave, save);
  }, [CHAVE, JSON.stringify(CHAMPION), JSON.stringify({ marcos, cartoes: o.cartoes ?? marcos }), o.dicas ? "1" : "0"] as const);
}
/** os erros da pagina. `rede`: tambem os do console (um 401 ou a rede fora escrevem la, entao o teste deles nao olha o console) */
const erros = (page: Page, rede = true): string[] => {
  const e: string[] = [];
  page.on("pageerror", x => e.push("pageerror: " + x.message));
  if (rede) page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) e.push("console: " + m.text()); });
  return e;
};
const rota = (page: Page) => page.evaluate(() => location.hash);
const irPara = (page: Page, hash: string) => page.evaluate(h => { location.hash = h; }, hash);
async function abrir(page: Page, w: number, h: number, marcos: number[], endereco: string, o: { cartoes?: number[]; dicas?: boolean } = {}): Promise<Falso> {
  await page.setViewportSize({ width: w, height: h });
  await page.clock.setFixedTime(AGORA);
  const s = await servidorFalso(page);
  await semear(page, marcos, o);
  await page.goto(APP + endereco);
  await expect(page.locator(".pet-tela")).toBeVisible();
  return s;
}
const linhas = (page: Page) => page.locator('[data-testid="ca-tabela"] tbody tr:not(.ca-salto)');
const semana = (page: Page) => page.getByTestId("ca-semana");
const estagio = (page: Page, e: string) => page.getByTestId(`ca-estagio-${e}`);

test("trancado (Tamer Nv 9), 1920 px: a marca tracejada, o cadeado Nv 10 e o cartao do motivo, sem chamar o servidor", async ({ page }) => {
  const err = erros(page);
  const s = await abrir(page, 1920, 950, ATE9, "?cameradev=1#/pet/estado");
  /* o minimapa: a ancora tracejada, com o cadeado e o nivel */
  const marca = page.locator('.minimapa-marca[data-lugar="cais"]');
  await expect(marca).toHaveCount(1);
  await expect(marca).toHaveClass(/minimapa-marca--trancado/);
  await expect(marca).toContainText("Nv 10");
  /* o cadeado sobre o cais, com a camera nele */
  await page.waitForFunction(() => typeof (window as any).__camera?.ir === "function");
  await page.evaluate(() => (window as any).__camera.ir("cais", { zoom: 0.7 }));
  const cadeado = page.locator('.cadeado-ilha[data-lugar="cais"]');
  await expect(cadeado).toBeVisible();
  await expect(cadeado).toHaveAttribute("aria-label", "Cais, trancado, Nv 10: Abre com o primeiro Mega");
  const motivo = page.locator(".cartao-motivo");
  await cadeado.click();
  await expect(motivo).toBeVisible();
  await expect(motivo).toContainText("Cais");
  await expect(motivo).toContainText("Nv 10");
  await expect(motivo).toContainText("Abre com o primeiro Mega");
  await page.getByRole("button", { name: "Entendi" }).click();
  await expect(motivo).toHaveCount(0);
  /* o endereco do cais trancado: o cartao do motivo no lugar do painel, e o endereco volta */
  await irPara(page, "#/cais");
  await expect(motivo).toBeVisible();
  expect(await rota(page)).toBe("#/pet/estado");
  await expect(page.getByTestId("ca-pronto")).toHaveCount(0);
  await expect(page.getByTestId("ca-buscando")).toHaveCount(0);
  expect(s.pedidos).toEqual([]);
  expect(err).toEqual([]);
});

test("aberto (o marco 10), 1920 px: a semana, as tabelas, Ver todas, a semana fechada, o segredo e Ir para a Arena", async ({ page }) => {
  const err = erros(page);
  const s = await abrir(page, 1920, 950, ATE10, "#/pet/estado");
  /* a ilha: a marca cheia e nenhum cadeado */
  const marca = page.locator('.minimapa-marca[data-lugar="cais"]');
  await expect(marca).toHaveCount(1);
  await expect(marca).not.toHaveClass(/minimapa-marca--trancado/);
  await expect(page.locator('.cadeado-ilha[data-lugar="cais"]')).toHaveCount(0);
  expect(s.pedidos).toEqual([]);

  await irPara(page, "#/cais");
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  await expect(page.locator(".painel-tela--lugar")).toContainText("Cais");
  expect(s.pedidos).toEqual(["/semanas", `/semanas/${ATUAL}/tabelas`]);
  /* a semana de agora, aberta */
  await expect(semana(page)).toHaveAttribute("data-estado", "aberta");
  await expect(semana(page)).toContainText("16 a 22 de novembro");
  await expect(semana(page)).toContainText("Fecha domingo, 23:59 · faltam 4 d 12 h");
  await expect(page.getByTestId("ca-seguinte")).toBeDisabled();
  /* a tabela do estagio do pet (Champion): as 8 de cima e a linha de quem olha (a 11a) depois do salto */
  await expect(estagio(page, "Champion")).toHaveAttribute("aria-checked", "true");
  await expect(estagio(page, "Champion")).toHaveAttribute("aria-label", "Champion, 12 Tamers, o estágio do seu pet");
  await expect(linhas(page)).toHaveCount(9);
  await expect(page.locator(".ca-salto")).toHaveCount(1);
  await expect(page.getByTestId("ca-voce")).toContainText("11º");
  await expect(page.getByTestId("ca-voce")).toContainText("Tamer#11");
  await expect(page.getByTestId("ca-voce")).toContainText("você");
  await expect(page.getByTestId("ca-tabela").locator("thead th")).toHaveText(["#", "Tamer", "Pontos", "Rivais", "Lutas"]);
  await page.getByTestId("ca-ver-todas").click();
  await expect(linhas(page)).toHaveCount(12);
  await expect(page.locator(".ca-salto")).toHaveCount(0);
  await expect(page.getByTestId("ca-ver-todas")).toHaveCount(0);
  /* os outros estagios: um em que quem olha nao lutou, e um vazio */
  await estagio(page, "Rookie").click();
  await expect(linhas(page)).toHaveCount(1);
  await expect(page.getByTestId("ca-fora")).toHaveText("Você não lutou com um Rookie nesta semana.");
  await estagio(page, "Ultimate").click();
  await expect(page.getByTestId("ca-vazia")).toContainText("Ninguém pontuou em Ultimate nesta semana");
  await expect(page.getByTestId("ca-tabela")).toHaveCount(0);
  /* Atualizar busca de novo a mesma semana e guarda o estagio escolhido */
  await page.getByTestId("ca-atualizar").click();
  await expect(page.getByTestId("ca-vazia")).toBeVisible();
  expect(s.pedidos).toEqual(["/semanas", `/semanas/${ATUAL}/tabelas`, "/semanas", `/semanas/${ATUAL}/tabelas`]);

  /* a semana de antes, fechada: o resultado de quem olha e "Conferir a semana" no lugar dos botoes */
  await page.getByTestId("ca-anterior").click();
  await expect(semana(page)).toHaveAttribute("data-estado", "fechada");
  await expect(semana(page)).toContainText("9 a 15 de novembro");
  await expect(semana(page)).toContainText("Fechou em 16/11, à 1h");
  await expect(page.getByTestId("ca-anterior")).toBeDisabled();
  await estagio(page, "Champion").click();
  const pronto = page.getByTestId("ca-pronto");
  await expect(pronto).toContainText("O seu resultado · Champion");
  await expect(pronto).toContainText("2º lugar de 3");
  await expect(pronto).toContainText("240 pontos · 2 rivais vencidos · 12 lutas");
  await expect(linhas(page)).toHaveCount(3);
  await expect(page.getByTestId("ca-arena")).toHaveCount(0);
  await expect(page.getByTestId("ca-atualizar")).toHaveCount(0);
  await page.getByTestId("ca-conferir").click();
  await expect(page.getByTestId("ca-segredo-texto")).toHaveText(SEGREDO);
  expect(s.pedidos.at(-1)).toBe(`/semanas/${ANTES}/segredo`);
  await page.getByTestId("ca-voltar-tabela").click();
  await expect(page.getByTestId("ca-segredo")).toHaveCount(0);
  await expect(linhas(page)).toHaveCount(3);

  /* de volta a semana de agora, e dela para a Arena */
  await page.getByTestId("ca-seguinte").click();
  await expect(semana(page)).toHaveAttribute("data-estado", "aberta");
  await page.getByTestId("ca-arena").click();
  await expect.poll(() => rota(page)).toBe("#/lutar/arena");
  await expect(page.getByTestId("ca-pronto")).toHaveCount(0);
  /* o cais so pediu as rotas das semanas */
  expect(s.pedidos.filter(p => !p.startsWith("/semanas"))).toEqual([]);
  expect(err).toEqual([]);
});

test("sem a conta e sem resposta, 1920 px: os dois avisos, Entrar, Agora nao e Tentar de novo", async ({ page }) => {
  const err = erros(page, false);
  const s = await abrir(page, 1920, 950, ATE10, "#/pet/estado");
  /* sem a sessao (401): as tabelas pedem a conta */
  s.sessao = false;
  await irPara(page, "#/cais");
  const semConta = page.getByTestId("ca-sem-conta");
  await expect(semConta).toBeVisible();
  await expect(semConta).toContainText("As tabelas pedem a conta");
  await expect(page.getByTestId("ca-entrar")).toHaveAttribute("href", "#/config/conta");
  await expect(page.getByTestId("ca-tabela")).toHaveCount(0);
  await page.getByTestId("ca-agora-nao").click();
  await expect(semConta).toHaveCount(0);
  await expect.poll(() => rota(page)).toBe("#/pet/estado");
  /* a rede fora: a tabela nao veio; com a rede e a sessao de volta, "Tentar de novo" traz a tabela */
  s.fora = true;
  await irPara(page, "#/cais");
  const semResposta = page.getByTestId("ca-sem-resposta");
  await expect(semResposta).toBeVisible();
  await expect(semResposta).toContainText("A tabela não veio");
  s.fora = false; s.sessao = true;
  await page.getByTestId("ca-tentar").click();
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  await expect(linhas(page)).toHaveCount(9);
  expect(err).toEqual([]);
});

test("a folha do celular (390 px): 6 linhas, sem a coluna das lutas e sem rolagem de lado", async ({ page }) => {
  const err = erros(page);
  await abrir(page, 390, 844, ATE10, "#/cais");
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  await expect(semana(page)).toContainText("16 a 22 de novembro");
  await expect(estagio(page, "Champion")).toHaveAttribute("aria-checked", "true");
  /* as 6 de cima e a linha de quem olha */
  await expect(linhas(page)).toHaveCount(7);
  await expect(page.getByTestId("ca-voce")).toContainText("11º");
  await expect(page.getByTestId("ca-tabela").locator("thead th")).toHaveText(["#", "Tamer", "Pontos", "Rivais"]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  /* "Ver todas" tambem mostra a coluna das lutas */
  await page.getByTestId("ca-ver-todas").click();
  await expect(linhas(page)).toHaveCount(12);
  await expect(page.getByTestId("ca-tabela").locator("thead th")).toHaveText(["#", "Tamer", "Pontos", "Rivais", "Lutas"]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(err).toEqual([]);
});

test("trancado no celular (390 px): o endereco do cais abre o cartao do motivo, sem a tela e sem chamar o servidor", async ({ page }) => {
  const err = erros(page);
  const s = await abrir(page, 390, 844, ATE9, "#/pet/estado");
  await irPara(page, "#/cais");
  const motivo = page.locator(".cartao-motivo");
  await expect(motivo).toBeVisible();
  await expect(motivo).toContainText("Abre com o primeiro Mega");
  expect(await rota(page)).toBe("#/pet/estado");
  await page.getByRole("button", { name: "Entendi" }).click();
  await expect(motivo).toHaveCount(0);
  await expect(page.getByTestId("ca-pronto")).toHaveCount(0);
  expect(s.pedidos).toEqual([]);
  expect(err).toEqual([]);
});

test("o cartao de destrave do nivel 10: o Cais, a frase, e o Ir abre o ranking da semana", async ({ page }) => {
  const err = erros(page);
  await abrir(page, 1920, 950, ATE10, "#/pet/estado", { cartoes: ATE9, dicas: true });
  const cartao = page.locator('.cartao-destrave[data-nivel="10"]');
  await expect(cartao).toBeVisible();
  await expect(cartao).toContainText("Nv 10");
  await expect(cartao).toContainText("Cais");
  await expect(cartao).toContainText("Veja o ranking da semana.");
  await cartao.getByRole("button", { name: "Ir" }).click();
  await expect(cartao).toHaveCount(0);
  await expect.poll(() => rota(page)).toBe("#/cais");
  await expect(page.getByTestId("ca-pronto")).toBeVisible();
  expect(await page.evaluate(c => (JSON.parse(localStorage.getItem(c + "-nivel")!) as { cartoes: number[] }).cartoes.includes(10), CHAVE)).toBe(true);
  expect(err).toEqual([]);
});
