/* O nivel do Tamer e as travas (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.3 a 5; so a vista, P-5 opcao V; prancha docs/pranchas/ux-lugares-menus/lugar_trancado_* e lugar_destravado_*):
   - o lugar trancado, a 1920 e a 390: o cadeado com o "Nv N", o trilho e a coluna apagados, o minimapa, o "Tamer Nv N", e a tecla, a rota e o toque abrindo o cartao do
     motivo no lugar do painel;
   - o destrave: o cartao (Ir, Depois, Esc), uma vez por nivel, o cadeado aberto e o brilho (sem ele com "reduzir movimento"), e as dicas desligadas sem cartao;
   - o piso 4 dos saves de antes, as abas Itens e Fronteira e a peca Forcar trancada (as Regras sairam com o combate por turnos, LP4), o "Ja conheco o jogo" e o "Rever o tutorial".
   Os estados saem de uma chave -nivel semeada ({marcos, cartoes}) e de saves pequenos: um In-Training de 30 min (so o marco 1), um de 70 min (marcos 1 e 2, pela hora de vida),
   um Rookie (1 a 3, o piso leva a 4) e o Champion de e2e/saves.json. Nada aqui muda o motor, o save nem o registro do Tamer. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const CHAMPION = (JSON.parse(readFileSync(new URL("./saves.json", import.meta.url), "utf8")) as Record<string, object>).champion;
const BEBE_30 = { semente: 101, versao: 21, log: [[480, "t", 30]] };
const BEBE_70 = { semente: 101, versao: 21, log: [[480, "t", 70]] };
const ROOKIE = { semente: 101, versao: 21, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER_VAZIO = { versao: 7, log: [] };
const TELAS = [["1920", 1920, 950], ["390", 390, 844]] as const;

interface Semente { save?: object | null; tamer?: object; nivel?: { marcos: number[]; cartoes: number[] } | null; dicas?: boolean; boasVindas?: boolean }
/** semeia por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele ao fechar); sem a chave -nivel quando `nivel` falta (o piso entra) */
async function semear(page: Page, o: Semente = {}): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t, n, dicas, bv]) => {
    localStorage.clear(); localStorage.setItem(chave + "-tamer", t); localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-guardados", "[]");
    if (bv === "1") localStorage.setItem(chave + "-boas-vindas", "1");
    localStorage.setItem(chave + "-dicas-ligadas", dicas);
    if (s) localStorage.setItem(chave, s);
    if (n) localStorage.setItem(chave + "-nivel", n);
  }, [CHAVE, o.save ? JSON.stringify(o.save) : null, JSON.stringify(o.tamer ?? TAMER_VAZIO), o.nivel ? JSON.stringify(o.nivel) : null, o.dicas ? "1" : "0", o.boasVindas ? "0" : "1"] as const);
}
const chaveNivel = (page: Page) => page.evaluate(c => JSON.parse(localStorage.getItem(c + "-nivel") ?? "null") as { marcos: number[]; cartoes: number[] } | null, CHAVE);
const erros = (page: Page): string[] => {
  const e: string[] = [];
  page.on("pageerror", x => e.push("pageerror: " + x.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) e.push("console: " + m.text()); });
  return e;
};
const rota = (page: Page) => page.evaluate(() => location.hash);
const trilho = (page: Page, nome: string) => page.locator(".dl-nav").getByRole("button", { name: new RegExp("^" + nome) });
/** o botao trancado e aria-disabled: o Playwright o tem por desabilitado, mas o toque e o clique de verdade chegam (abrem o cartao do motivo) */
const tocar = (l: ReturnType<Page["locator"]>) => l.click({ force: true });
const coluna = (page: Page, nome: string) => page.locator(".mm-destinos").getByRole("button", { name: new RegExp("^" + nome) });
const painel = (page: Page) => page.locator(".painel-tela--lugar");

for (const [nome, w, h] of TELAS) {
  const largo = w >= 900;

  test(`Nv 1 (so chocou), ${nome} px: Diario, Crescer, Lutar e Conversar trancados, com o cadeado, o Nv N e o motivo`, async ({ page }) => {
    test.setTimeout(120_000);
    await page.setViewportSize({ width: w, height: h });
    const err = erros(page);
    await semear(page, { save: BEBE_30, nivel: { marcos: [1], cartoes: [1] } });
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    if (largo) {
      /* o trilho: o icone igual, apagado, com o nome acessivel completo */
      await expect(trilho(page, "Crescer")).toHaveAttribute("aria-label", "Crescer, trancado, Nv 3: Abre quando ele virar Rookie");
      await expect(trilho(page, "Lutar")).toHaveAttribute("aria-label", "Lutar, trancado, Nv 4: Abre com o primeiro treino");
      await expect(trilho(page, "Diário")).toHaveAttribute("aria-label", "Diário, trancado, Nv 2: Abre com 3 chamados atendidos");
      await expect(trilho(page, "Conversar")).toHaveAttribute("aria-label", "Conversar, trancado, Nv 3: Abre quando ele virar Rookie");
      await expect(trilho(page, "Pet")).not.toHaveAttribute("aria-disabled", "true");
      for (const n of ["Crescer", "Lutar", "Diário", "Conversar"]) await expect(trilho(page, n)).toHaveClass(/hx-nav__bt--trancado/);
      /* o minimapa: o cadeado com o Nv N */
      await expect(page.locator(".minimapa-marca--trancado")).toHaveCount(3);
      await expect(page.locator(".minimapa-marca--trancado .nivel-nv")).toHaveText(["Nv 3", "Nv 4", "Nv 2"]);
      /* o Tamer Nv N na plaquinha */
      await expect(page.locator(".tamer-nv--topo")).toHaveText("Tamer Nv 1");
    } else {
      await expect(page.locator(".mm-destinos .mm-bt--trancado")).toHaveCount(3);
      await expect(page.locator(".mm-coluna .mm-bt--trancado")).toHaveCount(4);          // + Conversar
      await expect(page.locator(".mm-item .nivel-nv")).toHaveText(["Nv 3", "Nv 3", "Nv 4", "Nv 2"]);
      await expect(page.locator(".mm-destinos").getByRole("button", { name: "Crescer, trancado, Nv 3: Abre quando ele virar Rookie" })).toBeVisible();
      /* o leque do retrato traz o Tamer Nv N */
      await page.locator(".mm-retrato").click();
      await expect(page.locator("#leque-pet .mm-tamer")).toHaveText("Tamer Nv 1");
      await page.keyboard.press("Escape");
    }
    /* os cadeados na ilha (DOM sobre a cena 3D): um por lugar trancado, com o motivo no nome */
    const cad = page.locator(".cadeado-ilha:not(.aberto)");
    await expect(cad).toHaveCount(3);
    await expect(page.locator('.cadeado-ilha[data-lugar="saco"]')).toHaveAttribute("aria-label", "Crescer, trancado, Nv 3: Abre quando ele virar Rookie");
    await expect(page.locator('.cadeado-ilha[data-lugar="portao"]')).toHaveAttribute("aria-label", "Lutar, trancado, Nv 4: Abre com o primeiro treino");
    await expect(page.locator('.cadeado-ilha[data-lugar="barraca"]')).toHaveAttribute("aria-label", "Diário, trancado, Nv 2: Abre com 3 chamados atendidos");
    expect(err).toEqual([]);
  });

  test(`lugar trancado, ${nome} px: o toque, a tecla e a rota abrem o cartao do motivo, nao o painel`, async ({ page }) => {
    test.setTimeout(120_000);
    await page.setViewportSize({ width: w, height: h });
    const err = erros(page);
    await semear(page, { save: BEBE_30, nivel: { marcos: [1], cartoes: [1] } });
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    const cartao = page.locator(".cartao-motivo");
    /* o toque: o trilho (desktop) ou a coluna (celular) */
    await tocar(largo ? trilho(page, "Crescer") : coluna(page, "Crescer"));
    await expect(cartao).toBeVisible();
    await expect(cartao).toContainText("Crescer");
    await expect(cartao).toContainText("Nv 3");
    await expect(cartao).toContainText("Abre quando ele virar Rookie.");
    await expect(painel(page)).toHaveCount(0);
    expect(await rota(page)).toBe("#/pet/estado");
    await page.keyboard.press("Escape");                                    // o Esc fecha
    await expect(cartao).toHaveCount(0);
    /* o Entendi fecha tambem */
    await tocar(largo ? trilho(page, "Lutar") : coluna(page, "Lutar"));
    await expect(cartao).toContainText("Abre com o primeiro treino.");
    await cartao.getByRole("button", { name: "Entendi" }).click();
    await expect(cartao).toHaveCount(0);
    /* o toque no cadeado da ilha */
    await page.locator('.cadeado-ilha[data-lugar="barraca"]').dispatchEvent("click");
    await expect(cartao).toContainText("Abre com 3 chamados atendidos.");
    await page.keyboard.press("Escape");
    /* a rota digitada (a tabela de rotas nao muda): abre o cartao, e o endereco volta ao Pet */
    await page.evaluate(() => { location.hash = "#/crescer/treinar"; });
    await expect(cartao).toContainText("Abre quando ele virar Rookie.");
    await expect(painel(page)).toHaveCount(0);
    await expect.poll(() => rota(page)).toBe("#/pet/estado");
    await page.keyboard.press("Escape");
    /* a rota na abertura */
    await page.goto(APP + "#/lutar/arena");
    await expect(page.locator(".cartao-motivo")).toContainText("Abre com o primeiro treino.");
    await expect(painel(page)).toHaveCount(0);
    await expect.poll(() => rota(page)).toBe("#/pet/estado");
    /* a tecla (so com o teclado: o desktop) */
    if (largo) {
      await page.keyboard.press("Escape");
      await page.locator(".pet-tela").click({ position: { x: 5, y: 5 }, force: true }).catch(() => undefined);
      await page.keyboard.press("KeyC");
      await expect(cartao).toContainText("Abre quando ele virar Rookie.");
      await page.keyboard.press("Escape");
      await page.keyboard.press("KeyL");
      await expect(cartao).toContainText("Abre com o primeiro treino.");
      await expect(painel(page)).toHaveCount(0);
      expect(await rota(page)).toBe("#/pet/estado");
    }
    expect(err).toEqual([]);
  });

  test(`destrave do Nv 2, ${nome} px: o cartao do Diario, o cadeado aberto, o Ir e o Depois (uma vez por nivel)`, async ({ page }) => {
    test.setTimeout(120_000);
    await page.setViewportSize({ width: w, height: h });
    const err = erros(page);
    /* o pet de 70 min tem o marco 2 (1 h de vida, sem as chaves de produto); a chave diz que so o 1 estava feito: o 2 e novo */
    await semear(page, { save: BEBE_70, nivel: { marcos: [1], cartoes: [1] }, dicas: true });
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    const cartao = page.locator('.cartao-destrave[data-nivel="2"]');
    await expect(cartao).toBeVisible();
    await expect(cartao).toContainText("Diário");
    await expect(cartao).toContainText("Veja o que ele fez e por quê.");
    await expect(cartao).toHaveAttribute("role", "status");                                              // nao rouba o foco
    await expect(page.locator('div.sr-only[role="status"]').first()).toHaveText("Diário aberto");        // o aviso de leitor de tela
    await expect(cartao.getByRole("button", { name: "Ir" })).toBeVisible();
    await expect(cartao.getByRole("button", { name: "Depois" })).toBeVisible();
    /* o cadeado se abriu: a barraca nao tem mais cadeado de trancada, e o aberto brilha uma vez */
    await expect(page.locator('.cadeado-ilha[data-lugar="barraca"]:not(.aberto)')).toHaveCount(0);
    await expect(page.locator('.cadeado-ilha[data-lugar="saco"]')).toHaveCount(1);
    await expect(page.locator('.cadeado-ilha.aberto[data-lugar="barraca"]')).toHaveAttribute("aria-label", "Diário: aberto");
    expect((await chaveNivel(page))?.marcos).toEqual([1, 2]);
    /* Depois: fecha sem viagem e nao volta (nem depois de recarregar) */
    await cartao.getByRole("button", { name: "Depois" }).click();
    await expect(cartao).toHaveCount(0);
    expect(await rota(page)).toBe("#/pet/estado");
    expect((await chaveNivel(page))?.cartoes).toEqual([1, 2]);
    await page.reload();
    await expect(page.locator(".pet-tela")).toBeVisible();
    await expect(page.locator(".cartao-destrave")).toHaveCount(0);
    /* o lugar abre do mesmo jeito */
    if (largo) await trilho(page, "Diário").click(); else await page.getByRole("button", { name: "Diário" }).click();
    await expect(painel(page)).toBeVisible();
    expect(err).toEqual([]);
  });

  test(`destrave do Nv 2, ${nome} px: o Ir leva a camera ao lugar e o Esc fecha o cartao`, async ({ page }) => {
    test.setTimeout(120_000);
    await page.setViewportSize({ width: w, height: h });
    await semear(page, { save: BEBE_70, nivel: { marcos: [1], cartoes: [1] }, dicas: true });
    await page.goto(APP + "#/pet/estado");
    const cartao = page.locator('.cartao-destrave[data-nivel="2"]');
    await expect(cartao).toBeVisible();
    await cartao.getByRole("button", { name: "Ir" }).click();
    await expect(cartao).toHaveCount(0);
    await expect(painel(page)).toBeVisible();
    await expect.poll(() => rota(page)).toBe("#/diario/registro");
    expect((await chaveNivel(page))?.cartoes).toEqual([1, 2]);
    /* o Esc */
    await semear(page, { save: BEBE_70, nivel: { marcos: [1], cartoes: [1] }, dicas: true });
    await page.goto(APP + "#/pet/estado");
    await expect(cartao).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(cartao).toHaveCount(0);
    expect(await rota(page)).toBe("#/pet/estado");
    expect((await chaveNivel(page))?.cartoes).toEqual([1, 2]);
  });
}

test("destrave: com 'Mostrar dicas' desligado nao ha cartao, e o lugar abre do mesmo jeito; com 'reduzir movimento' nao ha brilho", async ({ page }) => {
  test.setTimeout(120_000);
  await page.setViewportSize({ width: 1920, height: 950 });
  await semear(page, { save: BEBE_70, nivel: { marcos: [1], cartoes: [1] }, dicas: false });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator('.cadeado-ilha.aberto[data-lugar="barraca"]')).toBeVisible();           // o cadeado se abre mesmo assim
  await expect(page.locator(".cartao-destrave")).toHaveCount(0);
  await trilho(page, "Diário").click();
  await expect(painel(page)).toBeVisible();
  /* o brilho existe, e some com "reduzir movimento" */
  await semear(page, { save: BEBE_70, nivel: { marcos: [1], cartoes: [1] }, dicas: true });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".brilho-ilha")).toHaveCount(1);
  await expect(page.locator(".brilho-ilha")).toHaveCSS("display", "block");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(page.locator(".brilho-ilha")).toHaveCSS("display", "none");
});

test("o piso 4: um save de hoje sem a chave abre Diario, Crescer e Lutar, sem cartao, e guarda os marcos que tem", async ({ page }) => {
  test.setTimeout(120_000);
  await page.setViewportSize({ width: 1920, height: 950 });
  const err = erros(page);
  await semear(page, { save: CHAMPION, dicas: true });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  expect(await chaveNivel(page)).toEqual({ marcos: [1, 2, 3, 4, 6], cartoes: [1, 2, 3, 4, 6] });
  await expect(page.locator(".tamer-nv--topo")).toHaveText("Tamer Nv 5");
  await expect(page.locator(".cartao-destrave")).toHaveCount(0);
  await expect(page.locator(".cadeado-ilha")).toHaveCount(0);
  for (const n of ["Crescer", "Lutar", "Diário", "Conversar"]) await expect(trilho(page, n)).not.toHaveAttribute("aria-disabled", "true");
  /* o Champion tem o Forcar; a primeira medalha falta: o Itens fica trancado (Nv 5) com o motivo, e a Fronteira (Nv 8) tambem */
  await page.goto(APP + "#/lutar/arena");
  await expect(painel(page)).toBeVisible();
  await page.goto(APP + "#/crescer/itens");
  await expect(page.getByRole("tab", { name: "Itens, Nv 5" })).toBeVisible();
  await expect(page.locator(".lg-trava")).toHaveText("Abre com a primeira medalha");
  await page.goto(APP + "#/lutar/fronteira");
  await expect(page.getByRole("tab", { name: "Fronteira, Nv 8" })).toBeVisible();
  await expect(page.locator(".lg-trava")).toHaveText("Abre com 6 medalhas");
  /* com 6 medalhas e o titulo, nada fica trancado */
  expect(err).toEqual([]);
});

test("a peca Forcar: trancada ate o Champion (Nv 6), com o motivo; o motor segue igual", async ({ page }) => {
  test.setTimeout(120_000);
  await page.setViewportSize({ width: 1920, height: 950 });
  await semear(page, { save: ROOKIE, nivel: { marcos: [1, 2, 3, 4], cartoes: [1, 2, 3, 4] } });
  await page.goto(APP + "#/crescer/treinar");
  await expect(page.getByRole("button", { name: "Forçar, trancado, Nv 6: Abre quando ele virar Champion" })).toBeVisible();
  await expect(page.locator("button.treino-forcar")).toHaveCount(0);
});

test("o Tamer com medalhas: o nivel segue os marcos (Itens no Nv 5, Fronteira so com 6) e o Itens abre sem o Champion", async ({ page }) => {
  test.setTimeout(120_000);
  await page.setViewportSize({ width: 1920, height: 950 });
  const tamer = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
  await semear(page, { save: ROOKIE, tamer });
  await page.goto(APP + "#/crescer/itens");
  await expect(painel(page)).toBeVisible();
  await expect(page.getByRole("tab", { name: "Itens" })).not.toHaveAttribute("aria-label", /Nv 5/);
  await expect(page.locator(".lg-trava")).toHaveCount(0);
  /* Rookie (1 a 4 pelo piso) + a medalha = Nv 5; o Forcar (marco 6) ainda fechado */
  expect(await chaveNivel(page)).toEqual({ marcos: [1, 2, 3, 4, 5], cartoes: [1, 2, 3, 4, 5] });
  await expect(page.locator(".tamer-nv--topo")).toHaveText("Tamer Nv 5");
});

test("Ja conheco o jogo: pula o Como jogar e os cartoes, abre os niveis 1 a 4; Comecar mostra o Como jogar de uma pagina so", async ({ page }) => {
  test.setTimeout(180_000);
  await page.setViewportSize({ width: 1920, height: 950 });
  const err = erros(page);
  await semear(page, { boasVindas: true, dicas: true });
  await page.goto(APP);
  const bv = page.locator("dialog.boas-vindas-tela[open]");
  await expect(bv).toBeVisible();
  expect((await chaveNivel(page))).toEqual({ marcos: [], cartoes: [] });         // a primeira visita: Nv 0
  await bv.getByRole("button", { name: "Já conheço o jogo" }).click();
  await expect(page.locator("dialog.como-tela")).toHaveCount(0);
  const br = page.locator("dialog.brasao-tela[open]");
  await expect(br).toBeVisible();
  await br.locator(".br-card").first().click();
  await expect(page.locator("dialog.brasao-tela[open]")).toHaveCount(0);
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator(".tamer-nv--topo")).toHaveText("Tamer Nv 4");
  expect(await chaveNivel(page)).toEqual({ marcos: [1, 2, 3, 4], cartoes: [1, 2, 3, 4] });
  await expect(page.locator(".cartao-destrave")).toHaveCount(0);
  await trilho(page, "Crescer").click();
  await expect(painel(page)).toBeVisible();
  expect(err).toEqual([]);
  /* sem o atalho: o Como jogar tem a pagina Cuide e nada de elogio */
  await semear(page, { boasVindas: true, dicas: true });
  await page.goto(APP);
  await page.locator("dialog.boas-vindas-tela[open]").getByRole("button", { name: "Começar" }).click();
  const cj = page.locator("dialog.como-tela[open]");
  await expect(cj).toBeVisible();
  await expect(cj.locator("#cj-tit")).toHaveText("Cuide");
  await expect(cj).not.toContainText(/elogie|repreend/i);
  await expect(cj.getByRole("button", { name: "Próximo" })).toHaveCount(0);
  await expect(cj.locator(".cj-pontos")).toHaveCount(0);
  await cj.getByRole("button", { name: "Chocar meu ovo" }).click();
  await page.locator("dialog.brasao-tela[open] .br-card").first().click();
  /* chocou: Nv 1 e o cartao do Cuide dele, antes da dica do ovo */
  await expect(page.locator('.cartao-destrave[data-nivel="1"]')).toBeVisible({ timeout: 30_000 });
  await expect(page.locator(".tamer-nv--topo")).toHaveText("Tamer Nv 1");
  await expect(trilho(page, "Crescer")).toHaveAttribute("aria-disabled", "true");
});

test("Rever o tutorial: limpa os cartoes e as dicas vistas; os cartoes dos niveis voltam um a um", async ({ page }) => {
  test.setTimeout(120_000);
  await page.setViewportSize({ width: 1920, height: 950 });
  await semear(page, { save: CHAMPION, dicas: true });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator(".cartao-destrave")).toHaveCount(0);
  await page.evaluate(c => localStorage.setItem(c + "-dicas", JSON.stringify(["ovo", "chamado"])), CHAVE);
  await page.getByRole("button", { name: "Ajustes", exact: true }).click();
  await page.getByRole("button", { name: /^Rever o tutorial/ }).click();
  await expect(page.getByText("Tutorial reiniciado")).toBeAttached();
  expect((await chaveNivel(page))?.cartoes).toEqual([]);
  expect(await page.evaluate(c => localStorage.getItem(c + "-dicas"), CHAVE)).toBeNull();
  await page.locator(".painel-tela--lugar").getByRole("button", { name: /Fechar/ }).click();
  await expect(page.locator('.cartao-destrave[data-nivel="1"]')).toBeVisible();
  await page.locator('.cartao-destrave[data-nivel="1"]').getByRole("button", { name: "Entendi" }).click();
  await expect(page.locator('.cartao-destrave[data-nivel="2"]')).toBeVisible();
});

test("celular: o Esc com o leque do retrato e o cartao abertos fecha so o de cima; o foco volta a quem o tinha", async ({ page }) => {
  test.setTimeout(120_000);
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, { save: BEBE_70, nivel: { marcos: [1], cartoes: [1] }, dicas: true });
  await page.goto(APP + "#/pet/estado");
  const cartao = page.locator('.cartao-destrave[data-nivel="2"]');
  await expect(cartao).toBeVisible();
  await page.locator(".mm-retrato").click();
  await expect(page.locator("#leque-pet .mm-tamer")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator("#leque-pet")).toHaveCount(0);
  await expect(cartao).toBeVisible();
  /* o teclado: foca o Depois (vindo do retrato) e fecha; o foco volta ao retrato, nao ao body */
  await page.locator(".mm-retrato").focus();
  await cartao.getByRole("button", { name: "Depois" }).focus();
  await page.keyboard.press("Enter");
  await expect(cartao).toHaveCount(0);
  expect(await page.evaluate(() => document.activeElement === document.body)).toBe(false);
});

/* o cartao do motivo dentro da folha no celular era o das Regras de luta (a PecaTrancada da Arena), que sairam com o combate por turnos (LP4);
   o Forcar trancado do Treinar e um botao desabilitado com o motivo no nome */
for (const [w, h] of [[390, 844], [360, 800]] as const) {
  test(`celular ${w}x${h}: o selo "Nv N" da coluna nao cruza o cartao de chamado nem o relogio e passa no maximo 10 px do botao`, async ({ page }) => {
    test.setTimeout(120_000);
    await page.setViewportSize({ width: w, height: h });
    await semear(page, { save: BEBE_70, nivel: { marcos: [1], cartoes: [1] } });
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    const selos = page.locator(".mm-item .nivel-nv");
    await expect(selos).toHaveCount(3);                                // o BEBE_70 abriu o Diario (marco 2): faltam Conversar, Crescer e Lutar
    /* o cartao de chamado (o BEBE_70 tem um aberto) e o relogio */
    const chamado = page.locator(".dl-card.chamado");
    await expect(chamado).toBeVisible();
    const caixas = [(await chamado.boundingBox())!, (await page.locator(".mm-relogio").boundingBox())!];
    expect(caixas.every(Boolean)).toBe(true);
    for (let i = 0; i < 3; i++) {
      const selo = (await selos.nth(i).boundingBox())!, botao = (await selos.nth(i).locator("xpath=preceding-sibling::button").boundingBox())!;
      expect(botao.x - selo.x, "para fora do botao").toBeLessThanOrEqual(10.5);
      for (const c of caixas) {
        const cruza = selo.x < c.x + c.width && selo.x + selo.width > c.x && selo.y < c.y + c.height && selo.y + selo.height > c.y;
        expect(cruza, `selo ${i} cruza ${JSON.stringify(c)}`).toBe(false);
      }
    }
  });
}
