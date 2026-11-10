/* Verificacao ponta a ponta (TAREFA_FRONT_TS, Etapa 5), no build servido pelo servidor local:
   1. um save de cada versao (1 sem "versao", 2 e 3): abre, passa pelos 5 destinos e 10 abas, cuida, treina ate o
      FORCAR e forca, luta uma vez na arena e uma na campanha, pausa o tempo; a assinatura do pet vivo no app tem
      que ser a do HTML atual rodando o mesmo registro (Motor.reproduzir do digilab_sprites.html);
   2. checklist do guia (secao 14) nas 9 abas, em 360 e 390 px, claro e escuro: sem rolagem lateral, alvos de
      toque >= 44 px, sem erro no console; foco visivel pelo teclado. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";
import { VERSAO_PET } from "../motor/constantes";

const SAVES: Record<string, { semente: number; log: unknown[]; versao?: number }> = JSON.parse(readFileSync(new URL("./saves.json", import.meta.url), "utf8"));
// prefixo = nome da pasta do repositorio (/v1 ou o da worktree), como no servidor_local.py
const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, HTML = `${PREFIXO}/web/digilab_sprites.html?antigo=1`, CHAVE = "digilab-web-v21-sprites";
const ABAS: [string, string, string][] = [
  ["Pet", "", "pet/estado"], ["Crescer", "Treinar", "crescer/treinar"], ["Crescer", "Aprendizado", "crescer/aprend"], ["Crescer", "Evolução", "crescer/evolucao"],
  ["Crescer", "Itens", "crescer/itens"],
  ["Lutar", "Arena", "lutar/arena"], ["Lutar", "Exploração", "lutar/campanha"], ["Lutar", "Fronteira", "lutar/fronteira"], ["Lutar", "Medalhas", "lutar/medalhas"], ["Diário", "Registro", "diario/registro"], ["Diário", "Catálogo", "diario/catalogo"],
  ["Diário", "Cenários", "diario/cenarios"], ["Conversar", "", "conversar/chat"],
];

/** semeia o save por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele ao fechar). O registro do Tamer
    (vazio, ou o dado) e o marcador do descarte (versao 8, a da LP4 da LUTA_POC) vao junto: com eles o app entende que o descarte unico
    ja rodou. Os saves destes testes sao v21 (os de antes nao abrem mais) */
async function semear(page: Page, save: object | null, tema?: string, tamer: object = { versao: 1, log: [] }): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t, tm]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", tm);
    localStorage.setItem(chave + "-descarte", "8");
    /* dicas do Bit desligadas e sem os pets guardados de exemplo: os testes de fluxo nao dependem deles */
    localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    if (s) localStorage.setItem(chave, s);
    if (t) localStorage.setItem(chave + "-tema", t);
  }, [CHAVE, save ? JSON.stringify(save) : null, tema ?? null, JSON.stringify(tamer)] as const);
}
/** abaixo de 900 px (mobile minimo, M1) o retrato abre o leque dos vitais e dos paineis (Estado atual, Evolucao, Ultimas acoes, DigiBrain, Configuracoes, Meus
    pets); o leque fecha ao escolher um item, entao cada painel pede o leque aberto de novo. Um so leque por vez: nao abre se ja esta aberto */
const abrirLeque = async (page: Page) => { if (!await page.locator("#leque-pet").count()) await page.getByRole("button", { name: "Painéis do pet", exact: true }).click(); };
/** erros de console e de pagina (falhar alto: qualquer um reprova) */
function vigiarErros(page: Page): string[] {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  /* o favicon da pagina de semear (um JSON) as vezes termina de falhar depois que a vigia comeca: fora do app */
  page.on("console", m => {
    if (m.type() !== "error") return;
    const url = m.location().url ?? "";
    if (/favicon\.ico$/.test(url)) return;
    erros.push("console: " + m.text() + (url ? ` (${url})` : ""));
  });
  return erros;
}
/** vai para a aba pela barra e pelas abas (dentro do app, sem recarregar) */
async function irPara(page: Page, destino: string, aba: string, rota: string): Promise<void> {
  /* abaixo de 900 px não há barra de abas (M1 do mobile mínimo, 2026-11-06): o destino fica na coluna de ícones da tela Pet, e de
     dentro de uma folha volta-se ao Pet pelo × antes */
  if ((page.viewportSize()?.width ?? 1280) < 900) {
    const fechar = page.getByRole("button", { name: "Fechar e voltar ao Pet" });
    if (await fechar.count() > 0) await fechar.first().click();
    await page.locator(".mm-destinos").getByRole("button", { name: destino, exact: true }).click();
  } else await page.locator(".dl-nav").getByRole("button", { name: destino, exact: true }).click();
  await page.getByRole("tab", { name: aba }).click();
  await expect(page).toHaveURL(new RegExp("#/" + rota + "$"));
}
const numLog = (page: Page, tipo: string) => page.evaluate(([t]) => JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] === t).length, [tipo] as const);

for (const [versao, save] of Object.entries(SAVES)) {
  test(`jogo completo com save ${versao}: o fluxo inteiro, e o replay do app igual`, async ({ page }) => {
    await semear(page, save);            /* a pagina de semear e um JSON: o favicon dela da 404, fora do app */
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    /* o nivel do pet: no topo do desktop (o viewport padrao e de desktop; a tela Pet do desktop nao tem o cabecalho do celular) */
    await expect(page.locator(".topo-pet .dl-tag--estagio")).toHaveText(/Champion/i);

    /* os 5 destinos e as 11 abas, pela barra e pelas abas */
    for (const [destino, aba, rota] of ABAS) {
      await page.locator(".dl-nav").getByRole("button", { name: destino, exact: true }).click();
      if (aba) await page.getByRole("tab", { name: aba }).click();
      await expect(page).toHaveURL(new RegExp("#/" + rota + "$"));
    }

    /* cuidar */
    await page.locator(".dl-nav").getByRole("button", { name: "Pet", exact: true }).click();
    const d0 = await numLog(page, "d");
    /* a tela Pet no habitat (M3): o dock tem as seis acoes no desktop (o Mais so tem o Por racao dos pets com mundo) */
    /* o Alimentar dos pets v12 em diante poe a racao no comedouro (o evento "dc"); os pets v13 nao tem elogio */
    const dc0 = await numLog(page, "dc");
    for (const a of ["Alimentar", "Limpar", "Brincar", "Carinho"]) await page.locator(".acoes-pet button", { hasText: a }).click();
    expect(await numLog(page, "d") + await numLog(page, "dc")).toBe(d0 + dc0 + 4);

    /* treinar ate o FORCAR (fadiga 60) e forcar (com a confirmacao) */
    await page.locator(".dl-nav button", { hasText: "Crescer" }).click();
    await page.getByRole("tab", { name: "Treinar" }).click();
    let forcou = false;
    for (let i = 0; i < 40 && !forcou; i++) {
      const forcar = page.locator("button.treino-ex.forcar:not([disabled])").first();
      const treinar = page.locator("button.treino-ex:not(.forcar):not([disabled])").first();
      if (await forcar.count()) {
        await forcar.click();
        await page.locator("dialog.folha").getByRole("button", { name: "Forçar mesmo assim" }).click();
        await expect(page.locator("dialog.folha")).toHaveCount(0);
        forcou = true;
      }
      else if (await treinar.count()) await treinar.click();
      await page.waitForTimeout(1100);            /* 10 min/s: o intervalo entre treinos e de 10 min de jogo */
    }
    expect(forcou, "o FORCAR apareceu e foi usado").toBe(true);
    expect(await numLog(page, "tr")).toBeGreaterThanOrEqual(3);

    /* lutar na Arena e na Campanha (a luta da POC, LP3 e LP4): a luta entra no registro e o palco a mostra ate o fim; Continuar volta para a aba */
    const l0 = await numLog(page, "l");
    await page.locator(".dl-nav button", { hasText: "Lutar" }).click();
    await page.getByRole("tab", { name: "Arena" }).click();
    await page.getByTestId("poc-mapa-campo").click();
    await page.getByTestId("poc-lutar").click();
    await expect(page.getByTestId("luta-poc")).toBeVisible();
    await expect(page.locator(".dl-nav")).toHaveCount(0);
    await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 90_000 });
    await page.getByTestId("poc-resultado").getByRole("button", { name: "Continuar" }).click();
    await expect(page.getByTestId("poc-arena")).toBeVisible();
    await page.getByRole("tab", { name: "Exploração" }).click();
    await page.locator("[data-testid^=poc-desafio-]:not([disabled])").first().click();
    await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 90_000 });
    await page.getByTestId("poc-resultado").getByRole("button", { name: "Continuar" }).click();
    await expect(page.getByTestId("poc-campanha")).toBeVisible();
    expect(await numLog(page, "l")).toBe(l0 + 2);

    /* pausa o tempo (Ajustes no pe da barra > Registro e replay) e confere o replay pelo app: o motor do HTML antigo so conhecia os pets
       v1-v3, que nao abrem mais (o descarte 6, COMBATE-TR, etapa R2b) */
    await page.locator(".dl-nav .nav-quad", { hasText: "Ajustes" }).click();
    await page.getByRole("button", { name: /^Registro e replay/ }).click();
    await page.getByRole("button", { name: "Pausa" }).click();
    await page.waitForTimeout(300);
    await page.getByRole("button", { name: "Verificar replay" }).click();
    await expect(page.getByText(/^Replay idêntico:/)).toBeVisible();
    /* o save semeado e v21; ao abrir ele passa para a ilha com agua (o "mi"; ILHA_AGUA, IA4) e segue v21 */
    expect(JSON.parse(await page.evaluate(() => (window as any).__digilab.registro())).versao).toBe(21);
    expect(erros, "erros no console do app").toEqual([]);
  });
}

for (const tema of ["light", "dark"] as const) for (const largura of [360, 390]) {
  test(`guia, secao 14: ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVES.champion);
    const erros = vigiarErros(page);
    for (const [, , rota] of ABAS) {
      await page.goto(APP + "#/" + rota);
      await page.waitForTimeout(600);
      const r = await page.evaluate(() => {
        const visivel = (e: Element) => (e as HTMLElement).offsetParent !== null;
        const pequenos = [...document.querySelectorAll("button, select, input, summary, a")].filter(visivel).flatMap(e => {
          const b = e.getBoundingClientRect(), alvo = (e as HTMLInputElement).type === "checkbox" && e.closest("label") ? e.closest("label")!.getBoundingClientRect() : b;
          return alvo.height < 44 || alvo.width < 44 ? [`${e.tagName}.${(e as HTMLElement).className} "${(e.textContent || "").trim().slice(0, 20)}" ${Math.round(alvo.width)}x${Math.round(alvo.height)}`] : [];
        });
        return { larg: document.documentElement.scrollWidth, janela: innerWidth, pequenos };
      });
      expect(r.larg, `${rota}: rolagem lateral`).toBeLessThanOrEqual(r.janela);
      expect(r.pequenos, `${rota}: alvos menores que 44 px`).toEqual([]);
    }
    expect(erros).toEqual([]);
  });
}

/* varios pets, um ativo (pedido do Matheus): os guardados ficam parados no tempo (o registro deles nao muda enquanto o ativo corre) e Ativar
   troca o pet. Desde a LP2 da LUTA_POC (para todos desde a LP4) a escada de exemplo nao e semeada: o guardado aqui e um In-Training v21 */
const BEBE_GUARDADO = { semente: 101, versao: 21, log: [[480, "t", 30]] };
test("vários pets: só o ativo corre o tempo", async ({ page }) => {
  await semear(page, SAVES.champion);
  await page.evaluate(([c, g]) => localStorage.setItem(c + "-guardados", g), [CHAVE, JSON.stringify([BEBE_GUARDADO])] as const);
  await page.goto(APP + "#/pet/estado");
  const ler = () => page.evaluate(c => ({ g: localStorage.getItem(c + "-guardados")!, a: localStorage.getItem(c)! }), CHAVE);
  await expect(page.locator(".pet-tela")).toBeVisible();
  const antes = await ler();
  expect(JSON.parse(antes.g)).toHaveLength(1);
  await page.waitForTimeout(3000);
  const depois = await ler();
  expect(depois.g).toBe(antes.g);                  /* guardados parados */
  expect(depois.a).not.toBe(antes.a);              /* o ativo andou (o registro junta avanços de tempo seguidos) */
  await page.locator(".topo-retrato").click();
  /* desktop (MpListaDesktop): pagina com um espaco por pet (o ativo + o guardado) e o painel do escolhido */
  await expect(page.locator(".mc-slot:not(.mc-slot--livre)")).toHaveCount(2);
  await page.locator(".mc-slot").nth(1).click();
  await page.locator(".mc-detalhe").getByRole("button", { name: "Tornar ativo" }).click();
  await expect(page.locator(".topo-pet .dl-tag--estagio")).toHaveText(/In-Training/i);
  const g = JSON.parse(await page.evaluate(c => localStorage.getItem(c + "-guardados")!, CHAVE));
  expect(g).toHaveLength(1);                       /* o Champion de antes foi para o lugar dele */
});

/* o relogio do jogo para durante a luta no palco e com o resultado aberto (so a interface: a luta ja entrou no registro na hora);
   fechado o resultado, volta a andar. Na velocidade alta (1 h por segundo) 1,5 s parado seriam 90 min de jogo. Desde a LP4, o palco da luta da POC */
test("tempo: o relógio para durante a animação da luta e com o Resultado aberto, e volta a andar depois", async ({ page }) => {
  test.setTimeout(120_000);
  await semear(page, SAVES.champion);
  const erros = vigiarErros(page);
  const tick = (): Promise<number> => page.evaluate(() => (window as any).__digilab.tick());
  await page.goto(APP + "#/pet/estado");
  await page.locator(".dl-nav .nav-quad", { hasText: "Ajustes" }).click();
  await page.getByRole("button", { name: /^Registro e replay/ }).click();
  await page.getByRole("button", { name: "1 h/s" }).click();
  await irPara(page, "Lutar", "Arena", "lutar/arena");
  const t0 = await tick();
  await expect.poll(tick).toBeGreaterThan(t0);                       /* fora da luta o tempo anda */
  const l0 = await numLog(page, "l");
  await page.getByTestId("poc-lutar").click();
  await expect(page.getByTestId("luta-poc")).toBeVisible();
  /* a luta ja esta no registro, antes da animacao */
  expect(await numLog(page, "l")).toBe(l0 + 1);
  /* durante a animacao: o tick nao muda */
  const t1 = await tick();
  await page.waitForTimeout(1500);
  expect(await tick(), "o tempo andou durante a animação da luta").toBe(t1);
  /* com o resultado aberto: tambem nao */
  const res = page.getByTestId("poc-resultado");
  await expect(res).toBeVisible({ timeout: 90_000 });
  const t2 = await tick();
  expect(t2).toBe(t1);
  await page.waitForTimeout(1500);
  expect(await tick(), "o tempo andou com o Resultado aberto").toBe(t2);
  /* fechou o resultado: volta a andar, sem compensar o tempo parado (1 h/s: menos de 3 h de jogo nos proximos 2 s) */
  await res.getByRole("button", { name: "Continuar" }).click();
  await expect(page.getByTestId("poc-arena")).toBeVisible();
  await expect.poll(tick).toBeGreaterThan(t2);
  const t3 = await tick();
  expect(t3 - t2, "o tempo parado nao volta de uma vez").toBeLessThan(180);
  /* o registro so ganhou a luta (e os avancos de tempo de depois): nenhum evento novo da interface */
  expect(await numLog(page, "l")).toBe(l0 + 1);
  expect(erros).toEqual([]);
});

/* nas duas peles dos menus (docs/TAREFA_V2_TEMA_MENUS.md, T3) */
for (const pele of ["vidro", "xcom"]) test(`foco visível pelo teclado (pele ${pele})`, async ({ page }) => {
  /* sem as transicoes do dl-btn: o teste compara o estilo com e sem foco logo depois de trocar, e uma transicao no meio (a maquina
     ocupada com a cena 3D nos outros workers) dava um falso "sem foco" */
  await page.emulateMedia({ reducedMotion: "reduce" });
  await semear(page, SAVES.champion);
  await page.goto(APP + `?pele=${pele}#/pet/estado`);
  await expect(page.locator(".pet-tela")).toBeVisible();
  const semFoco: string[] = [];
  let focados = 0;
  for (let i = 0; i < 25; i++) {
    await page.keyboard.press("Tab");
    const r = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null;
      if (!el || el === document.body) return "corpo";
      const estilo = (x: Element) => { const c = getComputedStyle(x); return [c.outlineStyle !== "none" && parseFloat(c.outlineWidth) > 0 ? "outline" : "", c.boxShadow].join("|"); };
      const alvo = el.querySelector(".circ, .quad, .evo-cx") ?? el, com = estilo(alvo);
      el.blur(); const sem = estilo(alvo); el.focus({ focusVisible: true } as FocusOptions);
      return com !== sem ? null : `${el.tagName}.${el.className} "${(el.textContent || "").trim().slice(0, 20)}"`;
    });
    if (r !== "corpo") focados++;
    if (r && r !== "corpo") semFoco.push(r);
  }
  expect(focados, "o teclado percorreu a tela").toBeGreaterThanOrEqual(10);
  expect(semFoco, "elementos sem indicação de foco").toEqual([]);
});

/* layouts (tokens.css): abaixo de 900 px o das pranchas de celular (sem barra: os destinos na coluna do topo da tela Pet, uma coluna); de 900 a 1099 barra
   lateral e uma coluna; de 1100 em diante o das pranchas *Desktop (conteudo + painel ao lado) */
for (const largura of [390, 899, 900, 1099, 1100, 1280]) {
  test(`layout em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await semear(page, SAVES.champion);
    const lateral = largura >= 900, desktop = largura >= 1100;
    /* a Campanha da luta da POC (o mapa 3D da Exploracao saiu na LP4): numa coluna so */
    for (const [rota, esq, dir] of [["crescer/evolucao", ".evl-arv", ".evl-hist"], ["lutar/campanha", ".poc-nota", ".poc-desafios"]]) {
      await page.goto(APP + "#/" + rota);
      await page.waitForTimeout(500);
      const r = await page.evaluate(([e, d]) => {
        const nav = document.querySelector(".dl-nav")?.getBoundingClientRect(), a = document.querySelector(e)!.getBoundingClientRect(), b = document.querySelector(d)!.getBoundingClientRect();
        return { navLateral: nav ? nav.height > nav.width : null, aoLado: b.left >= a.right - 1, larg: document.documentElement.scrollWidth, janela: innerWidth };
      }, [esq, dir] as const);
      expect(r.navLateral, `${rota}: barra lateral (abaixo de 900 px nao ha barra: os destinos sao a coluna do topo da tela Pet)`).toBe(lateral ? true : null);
      /* as telas do painel (Crescer, Lutar) ficam numa coluna so (M4); a Conversar e da M5 */
      expect(r.aoLado, `${rota}: painel ao lado do conteúdo`).toBe(rota.startsWith("conversar") && desktop);
      expect(r.larg, `${rota}: rolagem lateral`).toBeLessThanOrEqual(r.janela);
    }
  });
}

/* o monitor do Matheus (D10, docs/TAREFA_V2_LAYOUT_HABITAT.md): 1920 x 950 (janela util do Chrome a 100 %). O pet fica visivel no centro do
   habitat: na tela Pet, com o painel de Estado aberto e com o dock em baixo; nas outras telas, com o painel grande a direita */
test("monitor 1920x950: o pet fica visível com o painel aberto", async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 950 });
  await semear(page, SAVES.champion);
  const centro = () => page.evaluate(() => {
    const h = document.querySelector(".habitat")!.getBoundingClientRect(), cx = (h.left + h.right) / 2, cy = (h.top + h.bottom) / 2;
    const alvo = document.elementFromPoint(cx, cy);
    return { cx, cy, noHabitat: !!alvo?.closest(".habitat"), larg: h.width, alt: h.height, direita: h.right, rolagem: document.documentElement.scrollWidth };
  });
  await page.goto(APP + "#/pet/estado");
  /* o HUD (TAREFA_V3_LAYOUT_HUD): no desktop o Estado fica aberto na pilha da direita, sem clicar */
  await expect(page.locator(".pet-hud [data-painel-pet='estado'] .necessidades4")).toBeVisible();
  let c = await centro();
  expect(c.noHabitat, "tela Pet: nada cobre o pet").toBe(true);
  expect(c.alt, "o habitat tem a altura toda (dock flutuante)").toBe(950);
  const dock = await page.locator(".pet-dock .dock").boundingBox();
  expect(dock!.width, "o dock é uma barra flutuante, não a faixa inteira").toBeLessThan(900);
  /* Lutar, o Diario e os Ajustes sao lugares da ilha (L3): o painel cabe na tela, sem rolagem lateral, e a ilha a esquerda dele nao fica coberta */
  for (const rota of ["lutar/arena", "lutar/campanha", "diario/registro", "config"]) {
    await page.goto(APP + "#/" + rota);
    await expect(page.locator(".painel-tela--lugar-lado")).toBeVisible();
    const g = await page.evaluate(rotaAtual => {
      const p = document.querySelector(".painel-tela--lugar-lado")!.getBoundingClientRect(), h = document.querySelector(".habitat")!.getBoundingClientRect();
      const alvo = document.elementFromPoint(innerWidth * (rotaAtual === "config" ? 0.6 : 0.2), innerHeight * 0.6);
      return { esq: p.left, dir: p.right, topo: p.top, base: p.bottom, larg: innerWidth, alt: innerHeight, rolagem: document.documentElement.scrollWidth, noHabitat: !!alvo?.closest(".habitat"), habLarg: h.width };
    }, rota);
    expect(g.esq, `${rota}: o painel cabe na tela`).toBeGreaterThanOrEqual(0);
    expect(g.dir, `${rota}: o painel cabe na tela`).toBeLessThanOrEqual(g.larg);
    expect(g.topo, `${rota}: o painel cabe na tela`).toBeGreaterThanOrEqual(0);
    expect(g.base, `${rota}: o painel cabe na tela`).toBeLessThanOrEqual(g.alt);
    expect(g.rolagem, `${rota}: sem rolagem lateral`).toBeLessThanOrEqual(g.larg);
    expect(g.habLarg, `${rota}: a ilha ocupa a tela toda`).toBeGreaterThanOrEqual(g.larg - 1);
    /* os Ajustes ficam sobre a tela Pet (a camada do pet e a pilha da direita seguem la): so os lugares deixam a ilha livre a esquerda do painel */
    if (rota !== "config") expect(g.noHabitat, `${rota}: a ilha a esquerda do painel nao esta coberta`).toBe(true);
  }
  for (const rota of ["conversar/chat"]) {
    await page.goto(APP + "#/" + rota);
    await expect(page.locator(".painel-tela--lado")).toBeVisible();
    c = await centro();
    const painel = (await page.locator(".painel-tela--lado").boundingBox())!;
    expect(c.noHabitat, `${rota}: o centro do habitat não está coberto`).toBe(true);
    expect(c.larg, `${rota}: habitat com largura para o pet`).toBeGreaterThanOrEqual(900);
    expect(painel.x, `${rota}: o painel fica à direita do habitat`).toBeGreaterThanOrEqual(c.direita - 1);
    expect(c.rolagem, `${rota}: sem rolagem lateral`).toBeLessThanOrEqual(1920);
  }
});

/* ---------------------------------------------------------------- o descarte (LUTA_POC, LP4; o 7 da LP2 e da LP-6 junto): a luta do jogo e a
   da POC; os pets de antes (v1 a v19) saem com o aviso da luta nova, que oferece o arquivo deles e pede o brasao do ovo novo; o Tamer fica
   (as medalhas), sem a Fabrica de antes. Os testes das telas da luta de antes (o Resultado, as travas, as cartas, a Exploracao 3D, a Liga, a
   Torre, a Fabrica e o Salao do combate por turnos) sairam com elas; a luta nova esta em e2e/luta_poc_lp2.spec.ts e e2e/luta_poc_lp3.spec.ts */
const SAVE_ANTIGO_V3 = { semente: 910303, versao: 3, log: [[480, "t", 300], [780, "d", "alimentar"], [780, "t", 120]] };
const SAVE_ANTIGO_V19 = { semente: 6100, versao: 19, log: [[480, "t", 300], [780, "d", "acariciar"], [780, "t", 120]] };
const lerTamer = (page: Page) => page.evaluate(c => JSON.parse(localStorage.getItem(c + "-tamer") ?? "null"), CHAVE);
test("luta da POC: a primeira abertura descarta os pets de antes, avisa, oferece o arquivo e pede o brasão do ovo novo", async ({ page }) => {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([c, s]) => {
    localStorage.clear(); localStorage.setItem(c + "-boas-vindas", "1"); localStorage.setItem(c + "-dicas-ligadas", "0");
    localStorage.setItem(c, s); localStorage.setItem(c + "-guardados", JSON.stringify([JSON.parse(s)]));
  }, [CHAVE, JSON.stringify(SAVE_ANTIGO_V3)] as const);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  const aviso = page.locator("dialog.aviso-poc[open]");
  await expect(aviso).toContainText("A luta agora é na arena");
  await expect(aviso).toContainText("os 2 pets que você tinha (o ativo e os guardados) foram descartados");
  await page.keyboard.press("Escape");                             /* o aviso so sai pelo botao */
  await expect(aviso).toBeVisible();
  /* o arquivo dos pets de antes: os dois saves, como estavam */
  const [baixado] = await Promise.all([page.waitForEvent("download"), aviso.getByRole("button", { name: "Baixar o arquivo dos pets antigos" }).click()]);
  expect(baixado.suggestedFilename()).toBe("pets-antigos.json");
  await aviso.getByRole("button", { name: "Escolher o brasão do ovo novo" }).click();
  const br = page.locator("dialog.brasao-tela[open]");
  await expect(br.locator("#br-tit")).toHaveText("Escolha seu brasão");
  await expect(br.getByRole("button", { name: "Voltar" })).toHaveCount(0);
  await br.locator(".br-card").first().click();
  await expect(page.locator("dialog.brasao-tela[open]")).toHaveCount(0);
  const r = await page.evaluate(c => ({ save: JSON.parse(localStorage.getItem(c)!), g: localStorage.getItem(c + "-guardados"), aviso: localStorage.getItem(c + "-aviso-poc"),
    tamer: JSON.parse(localStorage.getItem(c + "-tamer")!), marca: localStorage.getItem(c + "-descarte"), antigos: JSON.parse(localStorage.getItem(c + "-descartados")!) }), CHAVE);
  expect(r.save.versao).toBe(VERSAO_PET);            /* o ovo novo nasce na versao atual (a v22: a v21 que nasce na ilha com agua) */
  expect(r.g).toBe("[]");
  expect(r.aviso).toBeNull();
  expect(r.marca).toBe("8");
  expect(r.antigos).toHaveLength(2);
  expect(r.tamer).toEqual({ versao: 8, log: [] });
  await page.reload();
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator("dialog.aviso-poc")).toHaveCount(0);
  expect(erros).toEqual([]);
});

test("luta da POC: o pet v19 de antes sai com o aviso, e o Tamer fica com as medalhas", async ({ page }) => {
  const tamer = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: SAVE_ANTIGO_V19.semente, forma: "Armadillomon", tick: 900 }],
    ["item", { id: "chip_forca", n: 1, quando: 1, origem: "medalha", lider: "npc_tier1_brutamontes", pet: SAVE_ANTIGO_V19.semente, forma: "Armadillomon", est: "crianca", tick: 900 }]] };
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([c, s, tm]) => {
    /* os descartes de antes ja rodaram (marcador 6): so falta o da luta da POC */
    localStorage.clear(); localStorage.setItem(c + "-boas-vindas", "1"); localStorage.setItem(c + "-dicas-ligadas", "0");
    localStorage.setItem(c, s); localStorage.setItem(c + "-guardados", "[]"); localStorage.setItem(c + "-tamer", tm); localStorage.setItem(c + "-descarte", "6");
  }, [CHAVE, JSON.stringify(SAVE_ANTIGO_V19), JSON.stringify(tamer)] as const);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  const aviso = page.locator("dialog.aviso-poc[open]");
  await expect(aviso).toContainText("o pet que você tinha foi descartado");
  await expect(aviso).toContainText("As suas medalhas, os itens, o título e os recordes ficam");
  await aviso.getByRole("button", { name: "Escolher o brasão do ovo novo" }).click();
  await page.locator("dialog.brasao-tela[open] .br-card").first().click();
  await expect(page.locator("dialog.brasao-tela[open]")).toHaveCount(0);
  const r = await page.evaluate(c => ({ save: JSON.parse(localStorage.getItem(c)!), marca: localStorage.getItem(c + "-descarte"),
    tamer: JSON.parse(localStorage.getItem(c + "-tamer")!) }), CHAVE);
  expect(r.save.versao).toBe(VERSAO_PET);
  expect(r.save.semente).not.toBe(SAVE_ANTIGO_V19.semente);
  expect(r.marca).toBe("8");
  /* a medalha e o item dela ficam; sem a Fabrica de antes no registro, o Tamer fica como estava */
  expect(r.tamer).toEqual(tamer);
  /* o ovo novo conhece a medalha do Tamer (o "u" no registro dele) */
  expect(r.save.log.filter((e: unknown[]) => e[1] === "u")).toEqual([[expect.any(Number), "u", { n: 1 }]]);
  await page.reload();
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator("dialog.aviso-poc")).toHaveCount(0);
  expect(erros).toEqual([]);
});

/* a Fronteira sem as 6 medalhas fica trancada e diz o que falta (o Champion do save conhece 1) */
test("fronteira: sem as 6 medalhas a Liga fica trancada e diz o que falta", async ({ page }) => {
  await semear(page, SAVES.champion);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/fronteira");
  await expect(page.locator(".fr-card")).toHaveCount(6);
  await expect(page.locator(".med-espera")).toContainText("A Fronteira abre com as 6 medalhas.");
  await expect(page.locator(".fr-lutar")).toBeDisabled();
  expect(erros).toEqual([]);
});

/* a tela dos itens (LP4: so os chips de stat; os itens de antes que o Tamer tem, a parte e sem efeito): celular (360, 390) e desktop (1280) */
const TAMER_ITENS = { versao: 2, log: [
  ["medalha", { id: "campina", n: 1, quando: 1, pet: 1, forma: "Armadillomon", tick: 900 }],
  ["item", { id: "chip_forca", n: 1, quando: 1, origem: "medalha", lider: "npc_tier1_brutamontes", pet: 1, forma: "Armadillomon", est: "crianca", tick: 900 }],
  ["item", { id: "carta_folego", n: 2, quando: 2, origem: "revanche", lider: "npc_tier1_brutamontes", pet: 1, forma: "Armadillomon", est: "crianca", tick: 900 }],
] };
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`itens: tela em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVES.champion, undefined, TAMER_ITENS);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/crescer/itens");
    await expect(page.locator(".it2-card")).toHaveCount(2);
    await expect(page.locator(".it2-card.it2--falta")).toHaveCount(1);
    await expect(page.getByTestId("itens-antigos")).toContainText("Carta de Fôlego");
    await expect(page.getByTestId("itens-antigos")).toContainText("sem efeito");
    await page.locator(".it2-card", { hasText: "Chip de Força" }).getByRole("button", { name: "Equipar" }).click();
    await expect(page.locator(".it2-card.it2--eq")).toHaveCount(1);
    expect((await lerTamer(page)).log.filter((ev: [string]) => ev[0] === "item")).toHaveLength(2);   /* a medalha nao deu item novo de regra */
    const r = await page.evaluate(() => ({ larg: document.documentElement.scrollWidth, janela: innerWidth }));
    expect(r.larg, "rolagem lateral").toBeLessThanOrEqual(r.janela);
    expect(erros).toEqual([]);
  });
}

/* ---------------------------------------------------------------- o painel DigiBrain (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 5;
   pranchas DigiBrainDesktop e DigiBrain390): so nos pets v11 (PW-7). Sob demanda (TAREFA_V2_TELA_PET): no desktop, o botao do cenario
   abre a coluna de detalhes, a direita do cenario, com o painel; em 390 px, uma folha aberta pelo botao do cenario, com o Conversar no
   cabecalho do Pet. Os numeros sao os do motor (Motor.digibrain) */
const SAVE_V11 = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };
for (const largura of [390, 1280]) {
  test(`DigiBrain: o painel do pet v11 em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await semear(page, SAVE_V11);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    await expect(page.locator(".digibrain")).toBeHidden();
    if (largura < 900) await expect(page.locator(".topo-bt[aria-label=\"Conversar\"]")).toBeVisible();          /* o Conversar fica no topo flutuante (< 900 px) */
    if (largura < 900) await abrirLeque(page);                                         /* o DigiBrain mora no leque do retrato (< 900 px) */
    await page.getByRole("button", { name: "DigiBrain", exact: true }).click();       /* o botao do leque (celular) ou a etiqueta do cenario (desktop) abre o painel */
    const raiz = page.locator("#pet-painel");
    await expect(raiz.locator(".digibrain")).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    /* o selo so como forma, com o nome acessivel (D1b-5): o tempo do jogo andando */
    await expect(raiz.getByRole("img", { name: "ao vivo" })).toBeVisible();
    /* o modal pequeno (D1b): so o mapa dos pesos do motor, sem os cartoes nem a legenda do rodape */
    const db = await page.evaluate(() => (window as any).__digilab.digibrain());
    expect(db).not.toBeNull();
    expect(db.decisao).not.toBeNull();
    await expect(raiz.locator("svg.mp")).toBeVisible();
    await expect(raiz.locator(".db-barras, .db-opcoes, .db-ultimas, .db-emo, .mp-nota")).toHaveCount(0);
    await expect(raiz.locator(".mp-leg")).toBeHidden();                               /* a legenda mora na dica do "i" (D1b-7) */
    await raiz.getByRole("button", { name: "O que é este desenho" }).click();
    await expect(raiz.locator("#db-dica")).toContainText("só desenho");
    await expect(raiz.locator(".mp-leg")).toBeVisible();
    await page.keyboard.press("Escape");                                              /* o Esc com a dica aberta fecha so a dica */
    await expect(raiz.locator("#db-dica")).toBeHidden();
    await expect(raiz).toBeVisible();
    /* o campo pequeno (D1c): o titulo e so o icone, com o nome para o leitor de tela; no desktop um painel de 420 px a direita, sob o relogio,
       com o pet a vista; no celular uma folha de 210 px presa embaixo, com os botoes numa coluna a esquerda do desenho */
    await expect(raiz.locator("#db-titulo svg")).toBeVisible();
    await expect(raiz.locator("#db-titulo")).toHaveText("DigiBrain");
    const caixa = (await raiz.locator(".scan-in").boundingBox())!;
    if (largura >= 900) {
      expect(Math.round(caixa.width)).toBe(420);
      expect(caixa.y).toBeGreaterThanOrEqual(60);
      expect(caixa.x).toBeGreaterThan(largura / 2);
    } else {
      expect(Math.round(caixa.y + caixa.height)).toBe(800);
      expect(Math.round(caixa.height)).toBe(210);
      const fechar = (await raiz.getByRole("button", { name: "Fechar DigiBrain" }).boundingBox())!, desenho = (await raiz.locator(".scan-moldura").boundingBox())!;
      expect(fechar.x + fechar.width).toBeLessThanOrEqual(desenho.x + 0.5);
    }
    /* nada promete mais do que uma soma de pesos */
    expect(await raiz.innerText()).not.toMatch(/pensando|sentindo/i);
    await page.screenshot({ path: test.info().outputPath(`digibrain-${largura}.png`) });     /* a captura do gate da etapa 5 */
    await page.getByRole("button", { name: "Fechar DigiBrain" }).click();
    await expect(page.locator("#pet-painel")).toHaveCount(0);
    expect(erros).toEqual([]);
  });
}
/* o mapa dos pesos (ScanDigiBrain.tsx, MapaScan), no lugar do icone estatico: cada traco e um peso do motor (Motor.digibrain().mapa), e a cada
   decisao acendem a regra, os candidatos com a chance e a acao escolhida (o "pesou mais" saiu no modal pequeno, D1b-6). Com "reduzir movimento" (D1-8, o contrato do
   reduzir: zero animacao) so o destaque troca; o movimento sem o reduzir tem o teste logo abaixo */
for (const largura of [390, 1280]) {
  test(`DigiBrain: o mapa dos pesos acende a cada decisão em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await semear(page, SAVE_V11);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    if (largura < 900) await abrirLeque(page);
    await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
    const raiz = page.locator("#pet-painel");
    const mapa = raiz.locator("svg.mp");
    await expect(mapa).toBeVisible();
    await expect(raiz.locator(".db-cab .db-icone, .db-folha-selo .db-icone")).toHaveCount(0);      /* o icone estatico saiu do painel */
    /* o mapa e o do motor: o mesmo numero de pesos, a regra, a escolhida, os candidatos, as arestas acesas e o lobo destacado */
    const conferir = async (): Promise<number> => {
      const r = await page.evaluate(() => {
        const s = document.querySelector(".digibrain svg.mp, dialog.folha[open] svg.mp")!, db = (window as any).__digilab.digibrain();
        return {
          n: Number(s.getAttribute("data-n")), pesos: s.querySelectorAll(".mp-pesos path").length, acesas: s.querySelectorAll(".mp-acesas path").length,
          regra: [...s.querySelectorAll("[data-regra].mp-lit")].map(g => g.getAttribute("data-regra")),
          esc: [...s.querySelectorAll(".mp-esc")].map(g => g.getAttribute("data-acao")),
          cand: [...s.querySelectorAll(".mp-cand")].map(g => g.getAttribute("data-acao")).sort(),
          pct: s.querySelectorAll(".mp-pct").length, top: [...s.querySelectorAll("[data-entrada].mp-lit")].map(g => g.getAttribute("data-entrada")).sort(),
          dest: s.querySelectorAll(".mp-dest").length, regioes: [...s.querySelectorAll(".mp-reg")].map(t => t.textContent), db,
        };
      });
      const m = r.db.mapa, d = r.db.decisao;
      expect(r.n).toBe(m.acesas.n);
      expect(r.pesos).toBe(m.arestas.length);
      expect(r.acesas).toBe(m.acesas.arestas.length);
      expect(r.regra).toEqual([m.acesas.regra]);
      expect(r.esc).toEqual([m.acesas.acao]);
      expect(r.cand).toEqual(d.chances.map((c: { acao: string }) => c.acao).sort());
      expect(r.pct).toBe(d.chances.length);
      expect(r.top).toEqual(d.percepcao.map((p: { entrada: string }) => p.entrada).sort());
      expect(r.dest).toBe(0);
      expect(r.regioes).toEqual(["ações", "regras", "percepção"]);
      return r.n;
    };
    const n0 = await conferir();
    /* sem animacao nem transicao no mapa */
    const animado = await page.evaluate(() => {
      const s = document.querySelector(".digibrain svg.mp, dialog.folha[open] svg.mp")!;
      return { anim: s.getAnimations({ subtree: true }).length, trans: getComputedStyle(s.querySelector(".mp-acesas path, .mp-pesos path")!).transitionDuration };
    });
    expect(animado).toEqual({ anim: 0, trans: "0s" });
    await mapa.screenshot({ path: test.info().outputPath(`digibrain-mapa-${largura}-n${n0}.png`) });
    /* o tempo anda e a proxima decisao acende o mapa de novo */
    await expect.poll(() => page.evaluate(() => (window as any).__digilab.digibrain().mapa.acesas.n), { timeout: 30000 }).toBeGreaterThan(n0);
    const n1 = await conferir();
    expect(n1).toBeGreaterThan(n0);
    await mapa.screenshot({ path: test.info().outputPath(`digibrain-mapa-${largura}-n${n1}.png`) });
    expect(await raiz.innerText()).not.toMatch(/pensando|sentindo|conectoma|connectome/i);
    expect(erros).toEqual([]);
  });
}

/* o movimento do scan (D1-2, D1-8): sem "reduzir movimento", numa decisao NOVA a varredura passa uma vez e o pulso percorre as arestas acesas
   logo depois, e os dois terminam (saem do DOM e nao deixam animacao); o primeiro quadro ao abrir nao pulsa; o unico movimento que fica e o
   giro lento do plano (so no desktop). Em 10 min/s do pet as decisoes (uma a cada 15 min dele) chegam mais depressa que a animacao e so o
   destaque troca, entao o teste poe o tempo em 1x (uma decisao a cada 15 s) */
test("DigiBrain: sem reduzir o movimento, a varredura e o pulso passam numa decisão nova e terminam", async ({ page }) => {
  test.setTimeout(120_000);
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await semear(page, SAVE_V11);
  await page.clock.install({ time: new Date("2026-10-19T12:00:00Z") });   /* o relogio da pagina corre sozinho; a decisao nova vem do runFor abaixo */
  const erros = vigiarErros(page);
  await page.goto(APP + "#/config");
  await page.getByRole("button", { name: /^Registro e replay/ }).click();
  await page.getByRole("button", { name: "1x", exact: true }).click();
  await page.evaluate(() => { location.hash = "#/pet/estado"; });
  await expect(page.locator(".pet-tela")).toBeVisible();
  await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
  const raiz = page.locator("#pet-painel");
  await expect(raiz.locator("svg.mp")).toBeVisible();
  /* o primeiro quadro, ao abrir, nao pulsa */
  await expect(raiz.locator(".scan-varredura, .mp-pulso")).toHaveCount(0);
  const animacoes = () => page.evaluate(() => (document.getAnimations() as any[])
    .filter(a => a.effect?.target?.closest?.("#pet-painel"))
    .map(a => { const t = a.effect.getTiming(); return { nome: a.animationName as string, duracao: t.duration as number, atraso: t.delay as number, infinita: t.iterations === Infinity }; }));
  /* uma decisao nova (1x e 1 min do pet por minuto do relogio, uma decisao a cada 15 min dele): o relogio falso salta 16 min (fastForward dispara cada timer uma vez: o passo do tempo cobre os 16 min e o repinte e um so), e o gap
     desde a decisao anterior e de mais de 2,15 s */
  await page.clock.fastForward(16 * 60_000);
  await expect(raiz.locator(".scan-varredura")).toBeAttached({ timeout: 10_000 });
  const durante = await animacoes();
  expect(durante.filter(a => a.nome === "scan-varre")).toEqual([{ nome: "scan-varre", duracao: 1200, atraso: 0, infinita: false }]);
  const acesas = await raiz.locator("svg.mp .mp-acesas path").count();
  const pulsos = durante.filter(a => a.nome === "scan-pulso");
  expect(pulsos, "um pulso por aresta acesa").toHaveLength(acesas);
  expect(pulsos.every(p => p.duracao === 800 && p.atraso === 1200 && !p.infinita)).toBe(true);
  /* e terminam: o timer do componente (no relogio falso) tira os dois do DOM, e do scan so fica o giro lento do plano */
  await page.clock.fastForward(3000);
  await expect(raiz.locator(".scan-varredura")).toHaveCount(0, { timeout: 6000 });
  await expect(raiz.locator(".mp-pulso")).toHaveCount(0);
  const depois = await animacoes();
  expect(depois.map(a => a.nome)).toEqual(["scan-giro"]);
  expect(depois[0]!.infinita).toBe(true);
  expect(erros).toEqual([]);
});
/* o scan e um dialogo modal: o foco fica preso enquanto aberto, o Esc fecha e o foco volta a quem abriu. A pilha (4a linha) desmonta enquanto o
   scan esta aberto, entao o foco tem de voltar ao botao remontado; a linha do agora (no topo) continua la */
test("DigiBrain: o scan prende o foco, o Esc fecha e o foco volta a quem abriu (a pilha e a linha do agora)", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await semear(page, SAVE_V11);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  const raiz = page.locator("#pet-painel");
  const abridores = [page.locator(".pet-hud [data-painel-pet='digibrain'] .hud-painel__bt"), page.locator("button.pet-agora")];
  for (const abre of abridores) {
    await abre.click();
    await expect(raiz.locator(".digibrain")).toBeVisible();
    /* o Tab alem do ultimo item de um <dialog> modal sai para a interface do navegador (document.activeElement vira o body): isso nao e vazar para a
       pagina de tras. O que nao pode acontecer e o foco cair num elemento de fora do dialogo */
    for (let i = 0; i < 12; i++) {
      await page.keyboard.press("Tab");
      expect(await page.evaluate(() => { const a = document.activeElement; return a === document.body || !!a?.closest("#pet-painel"); }), `o foco vazou do scan no Tab ${i + 1}`).toBe(true);
    }
    /* e a pagina de tras e inerte: nem por script um botao dela recebe o foco */
    expect(await page.evaluate(() => { const b = document.querySelector<HTMLElement>("button.pet-agora")!; b.focus(); return document.activeElement === b; })).toBe(false);
    await page.keyboard.press("Escape");
    await expect(raiz).toHaveCount(0);
    await expect(abre).toBeFocused();
  }
  expect(erros).toEqual([]);
});
/* nenhum texto do desenho abaixo de 11 px na tela (a fonte do SVG e max(base, 11px / escala)); no celular so os rotulos acesos e os das candidatas */
for (const [largura, altura] of [[390, 844], [1280, 800], [1920, 950]]) {
  test(`DigiBrain: nenhum texto do mapa fica abaixo de 11 px em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura!, height: altura! });
    await semear(page, SAVE_V11);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    if (largura! < 900) await abrirLeque(page);
    await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
    const mapa = page.locator("#pet-painel svg.mp");
    await expect(mapa).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    const pequenos = await mapa.evaluate(svg => [...svg.querySelectorAll("text")]
      .filter(t => getComputedStyle(t).display !== "none")
      .map(t => ({ txt: t.textContent, h: t.getBoundingClientRect().height }))
      .filter(t => t.h < 11));
    expect(pequenos, "textos do mapa com menos de 11 px de altura").toEqual([]);
    /* os rotulos de regiao (.mp-reg, .mp-sub) nao se sobrepoem entre si */
    const colisoes = await page.evaluate(() => {
      const c = (e: Element) => { const r = e.getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top, b: r.bottom }; };
      const cruza = (a: ReturnType<typeof c>, b: ReturnType<typeof c>) => a.l < b.r && b.l < a.r && a.t < b.b && b.t < a.b;
      const rot = [...document.querySelectorAll("#pet-painel .mp-reg, #pet-painel .mp-sub")].filter(t => getComputedStyle(t).display !== "none");
      const out: string[] = [];
      rot.forEach((a, i) => {
        rot.slice(i + 1).forEach(b => { if (cruza(c(a), c(b))) out.push(`"${a.textContent}" cobre "${b.textContent}"`); });
      });
      return out;
    });
    expect(colisoes, "rotulos de regiao que se sobrepoem").toEqual([]);
    expect(erros).toEqual([]);
  });
}
/* o zoom de 200% numa janela baixa (rev-a11y da D1b): uma janela de 1920 x 800 ou de 1280 x 720 com 200% vira 960 x 400 ou 640 x 360 em CSS, e
   uma janela ainda mais baixa, 960 x 300. Em todas, o campo cabe inteiro na janela, e o topo (o icone, o selo e os tres botoes) cabe na largura */
for (const [l, a] of [[960, 400], [960, 300], [640, 360]] as const) {
  test(`DigiBrain: com zoom de 200% (${l}x${a} em CSS) o campo cabe na janela`, async ({ page }) => {
    await page.setViewportSize({ width: l, height: a });
    await semear(page, SAVE_V11);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    if (l < 900) await abrirLeque(page);
    await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
    const raiz = page.locator("#pet-painel");
    await expect(raiz.locator("svg.mp")).toBeVisible();
    const r = await page.evaluate(() => {
      const q = (s: string) => document.querySelector(s)!.getBoundingClientRect(), cx = q("#pet-painel .scan-in");
      const topo = document.querySelector("#pet-painel .scan-topo")!, bts = [...topo.querySelectorAll("button")].map(b => b.getBoundingClientRect());
      return { cima: cx.top, baixo: cx.bottom, esq: cx.left, dir: cx.right, alto: innerHeight, largo: innerWidth,
        botoesDentro: bts.every(b => b.left >= cx.left - 0.5 && b.right <= cx.right + 0.5 && b.top >= cx.top - 0.5 && b.bottom <= cx.bottom + 0.5) };
    });
    expect(r.cima).toBeGreaterThanOrEqual(0);
    expect(r.baixo, "o campo passa do fim da janela").toBeLessThanOrEqual(r.alto + 0.5);
    expect(r.esq).toBeGreaterThanOrEqual(0);
    expect(r.dir).toBeLessThanOrEqual(r.largo + 0.5);
    expect(r.botoesDentro, "um botao do topo sai do campo").toBe(true);
    await raiz.getByRole("button", { name: "Fechar DigiBrain" }).click();
    await expect(raiz).toHaveCount(0);
    expect(erros).toEqual([]);
  });
}
/* o mapa em texto troca o desenho, no mesmo tamanho: nao cobre os botoes do topo, e o modal cabe inteiro numa janela baixa */
test("DigiBrain: o mapa em texto fica no lugar do desenho e o modal cabe a 1280x540", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 540 });
  await semear(page, SAVE_V11);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
  const raiz = page.locator("#pet-painel");
  const bt = raiz.getByRole("button", { name: "O mapa em texto" });
  await expect(bt).toHaveAttribute("aria-pressed", "false");
  await bt.click();
  await expect(bt).toHaveAttribute("aria-pressed", "true");
  await expect(raiz.locator(".scan-texto")).toBeVisible();
  await expect(raiz.locator("svg.mp")).toHaveCount(0);
  const r = await page.evaluate(() => {
    const q = (s: string) => document.querySelector(s)!.getBoundingClientRect();
    const t = q("#pet-painel .scan-texto"), topo = q("#pet-painel .scan-topo"), cx = q("#pet-painel .scan-in");
    const cruza = (a: DOMRect, b: DOMRect) => a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
    return { topo: cruza(t, topo), h: t.height, fundo: cx.bottom, alto: innerHeight };
  });
  expect(r.topo, "o texto cobre o topo com os botoes").toBe(false);
  expect(r.h).toBeGreaterThan(40);
  expect(r.fundo, "o modal passa do fim da janela").toBeLessThanOrEqual(r.alto);
  await bt.click();
  await expect(raiz.locator("svg.mp")).toBeVisible();
  expect(erros).toEqual([]);
});
/* um clique fora do modal (no veu) fecha, e o foco volta a quem abriu; o CENA.coberto saiu (D1b-3), conferido na fonte pelo Vitest */
test("DigiBrain: um clique fora fecha o modal", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await semear(page, SAVE_V11);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  const abre = page.locator("button.pet-agora");
  await abre.click();
  const raiz = page.locator("#pet-painel");
  await expect(raiz.locator("svg.mp")).toBeVisible();
  const antes = (await numLog(page, "d")) + (await numLog(page, "dc"));
  await page.mouse.click(200, 600);
  await expect(raiz).toHaveCount(0);
  /* o clique cai no veu, nao na ilha: nenhum carinho nem evento do dono (rev-replay da D1b) */
  expect((await numLog(page, "d")) + (await numLog(page, "dc"))).toBe(antes);
  await expect(abre).toBeFocused();
  expect(erros).toEqual([]);
});
/* o campo pequeno (D1c): so os rotulos do caminho aceso e das candidatas ficam a vista; o de outro ponto aparece ao passar o mouse (desktop) ou
   ao tocar nele (celular), e tocar nao grava evento */
for (const largura of [390, 1280]) {
  test(`DigiBrain: os rotulos so no caminho aceso, o resto ao passar o mouse ou tocar (${largura} px)`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await semear(page, SAVE_V11);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    if (largura < 900) await abrirLeque(page);
    await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
    const raiz = page.locator("#pet-painel");
    await expect(raiz.locator("svg.mp")).toBeVisible();
    const r = await page.evaluate(() => {
      const ac = (window as any).__digilab.digibrain().mapa.acesas;
      const vis = (g: Element) => [...g.querySelectorAll("text")].some(t => getComputedStyle(t).display !== "none");
      const nos = [...document.querySelectorAll("#pet-painel .mp-no")];
      return {
        caminho: ac.arestas.map((x: any) => x.entrada).sort(), regra: ac.regra, acao: ac.acao,
        entradas: nos.filter(g => g.hasAttribute("data-entrada") && vis(g)).map(g => g.getAttribute("data-entrada")).sort(),
        regras: nos.filter(g => g.hasAttribute("data-regra") && vis(g)).map(g => g.getAttribute("data-regra")),
        acoesOk: nos.filter(g => g.hasAttribute("data-acao")).every(g => vis(g) === g.classList.contains("mp-cand")),
        log: JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] !== "t").length,
      };
    });
    expect(r.entradas).toEqual(r.caminho);
    expect(r.regras).toEqual([r.regra]);
    expect(r.acoesOk).toBe(true);
    const outro = raiz.locator(".mp-no[data-regra]:not(.mp-lit)").first(), rot = outro.locator("text");
    await expect(rot).toBeHidden();
    if (largura >= 900) { await outro.hover(); await expect(rot).toBeVisible(); }
    else { await outro.locator("circle:not(.mp-alvo)").click(); await expect(outro).toHaveClass(/mp-toque/); await expect(rot).toBeVisible(); }
    expect(await page.evaluate(() => JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] !== "t").length)).toBe(r.log);
    expect(erros).toEqual([]);
  });
}
/* o "Atender" do cartao do chamado, dentro do scan aberto, grava um unico evento do dono. Um bebe v13 com o chamado de carinho em urgencia (55 min depois
   do inicio, restam 5 min da janela de 15: o cartao so aparece em urgencia, e o de fome so com a comida abaixo de FOME_FALA). O relogio da pagina fica parado (page.clock), senao a janela de
   5 min do pet fecharia em segundos de relogio antes do clique */
test("DigiBrain: o Atender do chamado dentro do scan grava um único evento", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await semear(page, { semente: 4242, versao: 21, log: [[480, "t", 55]] });
  await page.clock.install({ time: new Date("2026-10-19T12:00:00Z") });
  await page.clock.pauseAt(new Date("2026-10-19T12:00:01Z"));
  const erros = vigiarErros(page);
  const eventos = async () => (await numLog(page, "d")) + (await numLog(page, "dc"));
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-tela")).toBeVisible();
  await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
  const raiz = page.locator("#pet-painel");
  await expect(raiz.locator(".digibrain")).toBeVisible();
  const cartao = raiz.locator(".pet-alerta .chamado");
  await expect(cartao).toBeVisible();
  /* com um chamado aberto, o foco ao abrir fica no topo do modal (o Fechar), nao num botao do chamado (rev-a11y da D1b) */
  expect(await page.evaluate(() => !!document.activeElement?.closest("#pet-painel .scan-topo"))).toBe(true);
  await expect(raiz.locator("[role=status]")).toContainText(/Chamado/);
  const antes = await eventos();
  await cartao.getByRole("button", { name: "Atender" }).click();
  await expect.poll(eventos).toBe(antes + 1);
  await page.waitForTimeout(500);
  expect(await eventos(), "o Atender gravou mais de um evento").toBe(antes + 1);
  expect(erros).toEqual([]);
});

/* ---------------------------------------------------------------- a tela Pet como a Home da referencia (docs/TAREFA_V2_TELA_PET.md): o cenario
   com a maior area, tres acoes em destaque (as outras em Mais) e os detalhes sob demanda (folha no celular, coluna no desktop) */
for (const [largura, altura] of [[360, 800], [390, 844], [1280, 800]]) {
  test(`Pet (Home): cenário, prioridade, três ações e detalhes sob demanda em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: altura });
    await semear(page, SAVE_V11);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-cena")).toBeVisible();
    const desktop = largura >= 1100;
    const g = await page.evaluate(() => {
      const r = (s: string) => document.querySelector(s)!.getBoundingClientRect();
      const cena = r(".pet-cena"), doca = r(".pet-dock"), cv = document.querySelector<HTMLCanvasElement>(".pet-cena canvas")!;
      return { cena: cena.width * cena.height, doca: doca.width * doca.height, pix: getComputedStyle(cv).imageRendering, larg: document.documentElement.scrollWidth, janela: innerWidth };
    });
    /* o pet com o mundo (v12 em diante; o v13 de hoje): no desktop a doca tem tambem a barra da racao, e o cenario continua a maior area,
       mas nao o dobro dela (achado da R2b, COMBATE-TR: no celular, o dobro como antes) */
    expect(g.cena, "o cenario e a maior area").toBeGreaterThan(g.doca * 2);
    expect(g.pix).toBe("pixelated");
    expect(g.larg).toBeLessThanOrEqual(g.janela);
    /* o dock: seis acoes no desktop; no celular tres (Alimentar, Brincar, Limpar) e o Mais, com o Carinho, o Tapa, o Tratar e o Por racao (so pets com mundo) */
    await expect(page.locator(".acoes-pet .acao-destaque")).toHaveCount(largura >= 900 ? 6 : 3);
    await expect(page.locator(".acoes-pet .acao-extra")).toHaveCount(0);
    await page.locator(".acoes-pet .acao-mais").click();
    await expect(page.locator(".acoes-pet .acao-extra")).toHaveCount(largura >= 900 ? 0 : 3);
    await expect(page.locator(".acoes-pet .racao-bt:not(.bola-bt)")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator("#acoes-mais")).toHaveCount(0);
    /* sem fundo de hexagonos no cenario e sem retrato redondo no cabecalho do Pet */
    expect(await page.locator(".pet-cena .dl-hexcard, .pet-retrato").count()).toBe(0);
    /* os paineis (HUD, TAREFA_V3_LAYOUT_HUD): a partir de 900 px empilhados a direita, o Estado aberto e os outros recolhiveis, cada um
       com o seu botao; no celular, um aberto por vez, pelos botoes da borda direita. O balao da fala abre o porque */
    if (largura >= 900) {
      const pilha = page.locator(".pet-hud");
      await expect(pilha.locator("[data-painel-pet='estado'] .necessidades4")).toBeVisible();
      await expect(pilha.locator("[data-painel-pet='estado'] .hx-medidor__txt").first()).toHaveText(/^\d+%$/);     /* o valor do motor em % */
      const evo = page.getByRole("button", { name: "Evolução", exact: true });
      await expect(evo).toHaveAttribute("aria-expanded", "false");
      await expect(pilha.locator("[data-painel-pet='evolucao']")).toContainText("próxima forma em");                /* o resumo fechado */
      await evo.click();
      await expect(pilha.locator("[data-painel-pet='evolucao']")).toContainText("até virar");
      await page.getByRole("button", { name: "Últimas ações", exact: true }).click();
      await expect(pilha.locator("[data-painel-pet='acoes'] .mod-registro li").first()).toBeVisible();
      await expect(pilha.locator("[data-painel-pet='estado'] .necessidades4")).toBeVisible();                     /* os tres abertos juntos */
      await page.getByRole("button", { name: "Estado atual", exact: true }).click();
      await expect(pilha.locator(".necessidades4")).toHaveCount(0);
      await expect(page.locator("#pet-painel")).toHaveCount(0);
      /* a escolha fica no navegador: recarregar mantem Evolucao aberta e Estado recolhido */
      await page.reload();
      await expect(page.getByRole("button", { name: "Evolução", exact: true })).toHaveAttribute("aria-expanded", "true");
      await expect(page.getByRole("button", { name: "Estado atual", exact: true })).toHaveAttribute("aria-expanded", "false");
    } else {
      /* celular (M1): os vitais e os paineis moram no leque do retrato, que fecha ao escolher um deles */
      await abrirLeque(page);
      await page.getByRole("button", { name: "Estado atual", exact: true }).click();
      await expect(page.locator("#pet-painel .necessidades4")).toBeVisible();
      await abrirLeque(page);
      await page.getByRole("button", { name: "Evolução", exact: true }).click();
      await expect(page.locator("#pet-painel")).toHaveCount(1);
      await expect(page.locator("#pet-painel")).toContainText("até virar");
      await abrirLeque(page);
      await page.getByRole("button", { name: "Últimas ações", exact: true }).click();
      await expect(page.locator("#pet-painel .mod-registro li").first()).toBeVisible();
      await page.keyboard.press("Escape");
      await expect(page.locator("#pet-painel")).toHaveCount(0);
    }
    /* o balao da fala (PR #559): so aparece com uma fala registrada, por 15 s depois de cada reacao. Este save termina com o pet dormindo e
       sem motivo registrado, entao o balao vazio ("…") de antes nao aparece mais, nem ao recarregar */
    await expect(page.locator(".cena-fala")).toHaveCount(0);
    expect(erros).toEqual([]);
  });
}
/* o cenario da tela Pet: a cena 3D (a vista do POC, import dinamico) quando ha WebGL; sem WebGL, o cenario de reserva em CSS e SVG.
   Os dois sao decorativos (aria-hidden) */
test("Pet (Home): a cena 3D com WebGL e o cenário de reserva sem ele", async ({ page, browser }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_V11);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  const cena = page.locator(".pet-cena .cena3d");
  await expect(cena).toHaveAttribute("aria-hidden", "true");
  await expect.poll(() => page.evaluate(() => { const c = document.querySelector<HTMLCanvasElement>(".cena3d canvas"); return c ? c.width * c.height : 0; })).toBeGreaterThan(0);
  await expect(page.locator(".pet-cena .cena-sala")).toHaveCount(0);
  expect(erros).toEqual([]);
  /* sem WebGL: o getContext do WebGL devolve null e a tela fica com a reserva, sem erro */
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 390, height: 844 } });
  const p2 = await ctx.newPage();
  await p2.addInitScript(() => {
    const orig = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, tipo: string, ...r: unknown[]) {
      return /webgl/.test(tipo) ? null : (orig as (...a: unknown[]) => unknown).call(this, tipo, ...r);
    } as typeof orig;
  });
  await semear(p2, SAVE_V11);
  const erros2 = vigiarErros(p2);
  await p2.goto(APP + "#/pet/estado");
  /* o pet com o mundo (o v13 de hoje): a reserva e a do mundo (MundoReserva.tsx), nao o cenario em CSS dos pets sem mundo */
  await expect(p2.locator(".pet-cena .cena-mundo")).toBeVisible();
  await expect(p2.locator(".pet-cena .cena-mundo")).toHaveAttribute("aria-hidden", "true");
  await expect(p2.locator(".pet-cena .cena3d")).toHaveCount(0);
  expect(erros2).toEqual([]);
  await ctx.close();
});

/* o momento da evolucao e a aba Crescer · Evolucao (docs/TAREFA_V2_EVOLUCAO.md). save_evolucao.json (e2e/gerar_save_evolucao.mjs): um pet
   v11 no Rookie a 4 min do fim do estagio, que ja conhece a medalha que o Champion pede; o relogio do app anda e ele evolui na hora */
const SAVE_EVO = JSON.parse(readFileSync(new URL("./save_evolucao.json", import.meta.url), "utf8"));
const TAMER_1 = { versao: 1, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: SAVE_EVO.semente, forma: "Agumon", tick: 490 }]] };
const JAPONES = /[぀-ヿ㐀-鿿ｦ-ﾟ]/;
for (const largura of [390, 1280]) {
  test(`evolução: o momento em ${largura} px, a aba nova e o "Ver a revelação de novo"`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: largura >= 1100 ? 800 : 844 });
    await semear(page, SAVE_EVO, undefined, TAMER_1);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/crescer/evolucao");
    const rev = page.locator("dialog.revelacao[open]");
    await expect(rev).toBeVisible();
    await expect(rev.locator(".revel-tit")).toHaveText("EVOLUÇÃO!");
    await expect(rev.locator(".revel-de")).toHaveText("Rookie → Champion");
    await expect(rev.locator(".evm-nome")).toHaveText("Growlmon");
    await expect(rev.locator(".evm-estagio")).toHaveText("Champion");
    await expect(rev.locator(".evm-brasao")).toContainText("brasão Coragem");
    await expect(rev.locator(".evm-depara")).toContainText("Agumon");
    await expect(rev.locator(".evm-depara")).toContainText("Growlmon");
    await expect(rev.locator(".revel-porque")).toContainText("decidido pelo caráter");
    /* a medalha veio antes (o "u" do comeco): pediu 1, sem dizer qual liberou */
    await expect(rev.locator(".evm-medalhas")).toHaveText(/Esta evolução pediu 1 medalha do Tamer\.$/);
    await expect(page).toHaveURL(/#\/evolucao$/);
    const r = await rev.evaluate((d, j) => {
      const spr = d.querySelector<HTMLElement>(".evm-pet .evm-spr")!.getBoundingClientRect(), ok = d.querySelector<HTMLElement>(".evm-continuar")!.getBoundingClientRect();
      return { spr: [spr.width, spr.height], okVisivel: ok.bottom <= innerHeight + 1 && ok.top >= 0, japones: new RegExp(j).test(d.textContent ?? ""), nivel: /\b(Nv|Lv|XP)\b/.test(d.textContent ?? "") };
    }, JAPONES.source);
    expect(r.spr[0], "o pet grande").toBeGreaterThan(150);
    expect(r.okVisivel, "o Continuar à vista, sem rolar").toBe(true);
    expect(r.japones, "nenhum caractere japonês").toBe(false);
    expect(r.nivel, "nem nível nem XP").toBe(false);
    await rev.getByRole("button", { name: "Continuar" }).click();
    await expect(page).toHaveURL(/#\/crescer\/evolucao$/);
    await expect(page.locator("dialog.revelacao[open]")).toHaveCount(0);
    /* a aba: a forma atual em destaque, a proxima evolucao com as medalhas, a arvore, o porque e o historico */
    await expect(page.locator(".evl-nome b")).toHaveText("Growlmon");
    await expect(page.locator(".evl-prazo")).toContainText("até Ultimate");
    /* os selos so da conta do Tamer (L2): ele tem 1 de 3 */
    await expect(page.locator(".evl-reqs")).toContainText("1/3");
    await expect(page.locator(".evl-arv")).toBeVisible();
    await expect(page.locator(".evl-porque")).toContainText("decidido pelo caráter");
    await expect(page.locator(".evl-hist li")).toHaveCount(3);
    expect(JAPONES.test(await page.locator(".evl").textContent() ?? "")).toBe(false);
    /* o historico reabre o momento de qualquer evolucao */
    /* o historico fica num details fechado (L2, regra do texto): abre antes */
    await page.locator(".evl-det", { hasText: "Histórico" }).locator("summary").click();
    await page.getByRole("button", { name: "Ver a revelação de novo: Agumon" }).click();
    await expect(rev).toBeVisible();
    await expect(rev.locator(".revel-de")).toHaveText("In-Training → Rookie");
    await expect(rev.locator(".evm-nome")).toHaveText("Agumon");
    await expect(rev.locator(".revel-porque")).toContainText("decidido pelo cuidado");
    await expect(rev.locator(".evm-medalhas")).toHaveCount(0);
    await rev.getByRole("button", { name: "Continuar" }).click();
    await expect(page.locator("dialog.revelacao[open]")).toHaveCount(0);
    await expect(page).toHaveURL(/#\/crescer\/evolucao$/);
    expect(erros).toEqual([]);
  });
}
/* sem o atlas do UP (o CI, as capturas do repositorio): o pet do momento e o do destaque saem da grade de pixels de reserva, nitidos */
test("evolução: sem o atlas, o pet de reserva no momento e na aba", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_EVO, undefined, TAMER_1);
  await page.route(/\/Assets\/(digilab_atlas_up|digilab_decoracao_up|decoracao_up\/)/, r => r.abort());
  await page.goto(APP + "#/crescer/evolucao");
  const rev = page.locator("dialog.revelacao[open]");
  await expect(rev).toBeVisible();
  await expect(rev.locator(".evm-pet .evm-spr--reserva")).toBeVisible();
  const w = await rev.locator(".evm-pet .evm-spr--reserva").evaluate(e => (e as HTMLImageElement).naturalWidth);
  expect(w).toBeGreaterThan(100);
  await rev.getByRole("button", { name: "Continuar" }).click();
  await expect(page.locator(".evl-palco .evm-spr--reserva")).toBeVisible();
});

/* a aba Treinar (docs/TAREFA_V2_TREINO.md). save_treino_pausa.json e save_treino_forcar.json (e2e/gerar_save_treino.mjs): um Palmon v11 no
   Rookie que treinou 3 vezes (fadiga entre 40 e 60: pede pausa) ou 4 (fadiga acima de 60: so Forcar) */
const SAVE_TR_PAUSA = JSON.parse(readFileSync(new URL("./save_treino_pausa.json", import.meta.url), "utf8"));
const SAVE_TR_FORCAR = JSON.parse(readFileSync(new URL("./save_treino_forcar.json", import.meta.url), "utf8"));
const SEM_JAPONES = /[぀-ヿ㐀-鿿ｦ-ﾟ]/;
for (const largura of [390, 1280]) {
  test(`treino: o estado, os exercícios e o cansaço em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: largura >= 1100 ? 800 : 844 });
    await semear(page, SAVE_TR_PAUSA);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/crescer/treinar");
    /* L2: o estado numa palavra, o último treino sem a frase do intervalo (que fica no balão) e os números do cansaço */
    await expect(page.locator(".trn2-estado")).toHaveText("Pausa");
    await expect(page.locator(".trn2-ultimo")).toContainText("Alvo");
    await expect(page.locator(".treino-ex")).toHaveCount(6);
    await expect(page.locator(".treino-ex.forcar")).toHaveCount(0);
    await expect(page.locator(".trn2-cansaco .trn2-med")).toHaveCount(2);
    const texto = await page.locator(".trn2-tela").textContent() ?? "";
    expect(SEM_JAPONES.test(texto), "nenhum caractere japonês").toBe(false);
    expect(/(Nv|Lv|XP)/.test(texto), "nem nível nem XP").toBe(false);
    expect(erros).toEqual([]);
  });
}
test("treino: com fadiga acima de 60 os exercícios viram Forçar, a folha confirma e o treino entra no registro", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_TR_FORCAR);
  const erros = vigiarErros(page);
  /* o relogio da pagina e falso e, com o app de pe, para: o Forcar so fica habilitado ~3 min de jogo (o intervalo de 10 min passou, a
     fadiga ainda esta acima de 60), uns 300 ms a 10 min/s, e a espera do Playwright (que tenta de novo em intervalos que crescem ate 1 s)
     podia pular essa janela; o "Forçar mesmo assim" tambem podia cair depois dela. Com o relogio parado, o teste anda 100 ms por vez */
  await page.clock.install();
  await page.goto(APP + "#/crescer/treinar");
  await expect(page.locator(".treino-ex.forcar")).toHaveCount(6);
  await page.clock.pauseAt(new Date(await page.evaluate(() => Date.now()) + 250));
  const l0 = await numLog(page, "tr");
  /* o intervalo de 10 min passa com o relogio do app (10 min/s) */
  const habilitado = page.locator(".treino-ex.forcar:not([disabled])");
  for (let i = 0; i < 40 && await habilitado.count() === 0; i++) await page.clock.runFor(100);
  await habilitado.first().click();
  const folha = page.locator("dialog.folha[open]");
  await expect(folha).toContainText("Forçar levantar pedra?");
  await folha.getByRole("button", { name: "Forçar mesmo assim" }).click();
  await expect(page.locator(".trn2-msg")).toContainText("Forçado:");
  expect(await numLog(page, "tr")).toBe(l0 + 1);
  await expect(page.locator(".trn2-cansaco .trn2-barra--sombrio")).toHaveAttribute("aria-label", /^Sobrecarga 25 de 100/);
  await expect(page.locator(".trn2-ultimo")).toContainText("Levantar pedra");
  expect(erros).toEqual([]);
});
/* sem o atlas do UP (o CI, as capturas do repositorio): os icones do lucide */
test("treino: sem o atlas, os ícones de reserva", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_TR_PAUSA);
  await page.route(/\/Assets\/(digilab_atlas_up|digilab_decoracao_up|decoracao_up\/)/, r => r.abort());
  await page.goto(APP + "#/crescer/treinar");
  await expect(page.locator(".treino-grade .treino-ic--reserva")).toHaveCount(6);
});

/* ---------------------------------------------------------------- o mundo no jogo, etapa 2 (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md: o
   E2E-COMIDA e o E2E-CENA). save_mundo.json (e2e/gerar_save_mundo.mjs): um Gomamon v12 com fome, que come a racao posta perto dele em
   qualquer ponto da proxima hora de jogo (o relogio do app anda enquanto o teste mexe). A tela poe a racao pelo gesto (arrastar "Por
   racao" e soltar no chao), pelo toque (tocar no botao e depois no chao) e pelo teclado (um lugar nomeado); a cena (3D e a reserva) desenha
   o pet e a racao onde o motor diz. Os dados vem do motor por window.__digilab (so leitura) */
const SAVE_MUNDO = JSON.parse(readFileSync(new URL("./save_mundo.json", import.meta.url), "utf8"));
type MundoE2e = { pet: [number, number]; comedouro: [number, number]; comidas: { id: number; x: number; y: number; situacao: string | null }[];
  consumos: { id: number; tick: number; situacao: string; fome_antes: number; fome_depois: number }[]; fome: number; acao: string;
  lugares: Record<"comedouro" | "perto" | "longe", [number, number]> };
const lerMundo = (page: Page) => page.evaluate(() => (window as any).__digilab.mundo() as MundoE2e);
const lerCena = (page: Page) => page.evaluate(() => (window as any).__digilab.cena() as { pet: [number, number]; modo3d: boolean } | null);
const naTela = (page: Page, x: number, y: number) => page.evaluate(([a, b]) => (window as any).__digilab.cenaPara(a, b) as [number, number], [x, y] as const);
const ultimoDc = async (page: Page) => JSON.parse(await page.evaluate(() => (window as any).__digilab.registro())).log.filter((e: unknown[]) => e[1] === "dc").at(-1);
/** o "Por racao" fica no menu Mais do dock (M3 do layout habitat) */
const abrirMais = async (page: Page) => { if (!await page.locator("#acoes-mais").count()) await page.locator(".acoes-pet .acao-mais").click(); };
/** a info do mundo fica no Estado, em "Detalhes" (fora da cena): no desktop na pilha da direita (o Estado aberto), no celular no painel
    da borda; abre, confere e fecha */
async function infoMundoNoEstado(page: Page, texto: string | null): Promise<void> {
  const pilha = await page.locator(".pet-hud").count() > 0;
  const bt = page.getByRole("button", { name: "Estado atual", exact: true });
  if (!pilha) await abrirLeque(page);                  /* celular: o "Estado atual" mora no leque do retrato */
  if (!pilha || await bt.getAttribute("aria-expanded") === "false") await bt.click();
  const raiz = page.locator(pilha ? ".pet-hud [data-painel-pet='estado']" : ".pet-painel"), det = raiz.getByRole("button", { name: "Detalhes" });
  if (await det.getAttribute("aria-expanded") === "false") await det.click();
  const info = raiz.locator(".mundo-info");
  if (texto === null) await expect(info).toBeVisible(); else await expect(info).toContainText(texto);
  await expect(page.locator(".pet-balcao .mundo-info")).toHaveCount(0);
  await det.click();
  await expect(info).toHaveCount(0);
  if (!pilha) { await page.getByRole("button", { name: "Fechar Estado atual" }).click(); await expect(page.locator(".pet-painel")).toHaveCount(0); }
}
/** arrasta "Por racao" ate o ponto do cliente, com o mouse (o gesto) */
async function arrastarRacao(page: Page, alvo: [number, number]): Promise<void> {
  await abrirMais(page);
  const b = (await page.locator(".racao-bt:not(.bola-bt)").boundingBox())!;
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2);
  await page.mouse.down();
  await page.mouse.move(b.x + b.width / 2 + 20, b.y - 20, { steps: 4 });
  await page.mouse.move(alvo[0], alvo[1], { steps: 12 });
  await page.mouse.up();
}
/** o pet come a racao `id` (o E2E-COMIDA): a refeicao entra nos consumos do motor, madura, e a fome cai (a saciedade sobe) */
async function esperarComer(page: Page, id: number): Promise<void> {
  await expect.poll(async () => (await lerMundo(page)).consumos.some(c => c.id === id), { timeout: 90_000, message: "o pet comeu a ração posta" }).toBe(true);
  const c = (await lerMundo(page)).consumos.find(x => x.id === id)!;
  expect(c.situacao).toBe("madura");
  expect(c.fome_depois, "a fome cai: a saciedade sobe").toBeGreaterThan(c.fome_antes);
}
/** a cena segue o motor (o E2E-CENA): a posicao desenhada do pet chega a do motor */
async function cenaSegueMotor(page: Page): Promise<void> {
  await expect.poll(async () => {
    const [m, c] = [await lerMundo(page), await lerCena(page)];
    return c ? Math.hypot(c.pet[0] - m.pet[0], c.pet[1] - m.pet[1]) : 1e9;
  }, { timeout: 10_000, message: "a posição desenhada do pet segue a do motor" }).toBeLessThan(1);
}
for (const [nome, largura, semWebGL] of [["a cena 3D", 390, false], ["a reserva sem WebGL", 390, true], ["a cena 3D no desktop", 1280, false]] as const) {
  test(`mundo: arrastar a ração até o chão, o pet anda até ela e come, com ${nome}`, async ({ browser }) => {
    test.setTimeout(180_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: largura >= 1100 ? 800 : 844 } });
    const page = await ctx.newPage();
    if (semWebGL) await page.addInitScript(() => {
      const orig = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, tipo: string, ...r: unknown[]) {
        return /webgl/.test(tipo) ? null : (orig as (...a: unknown[]) => unknown).call(this, tipo, ...r);
      } as typeof orig;
    });
    await semear(page, SAVE_MUNDO);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(semWebGL ? ".pet-cena .cena-mundo" : ".pet-cena .cena3d")).toBeVisible();
    await expect(page.locator(semWebGL ? ".pet-cena .cena3d" : ".pet-cena .cena-mundo")).toHaveCount(0);
    await expect.poll(() => lerCena(page)).not.toBeNull();
    await cenaSegueMotor(page);
    await infoMundoNoEstado(page, "rações no chão");
    /* o gesto: soltar 2 celulas a leste do pet (o "perto"), no ponto da tela que a vista da */
    const m0 = await lerMundo(page), alvo = m0.lugares.perto, ids0 = m0.comidas.map(c => c.id);
    await arrastarRacao(page, await naTela(page, alvo[0], alvo[1]));
    const dc = await ultimoDc(page);
    expect(dc[2].tipo).toBe("racao");
    expect(Math.abs(dc[2].x - alvo[0]) + Math.abs(dc[2].y - alvo[1]), "o ponto solto vira a posição do mapa").toBeLessThanOrEqual(2);
    const nova = (await lerMundo(page)).comidas.find(c => !ids0.includes(c.id))!;
    expect([nova.x, nova.y]).toEqual([dc[2].x, dc[2].y]);
    await expect(page.locator(".racao-dica")).toContainText("Ração posta na casa.");
    /* a cena desenha a racao onde o motor diz (no 3D, o ponto do mapa volta ao mesmo ponto da tela; na reserva, o elemento) */
    if (semWebGL) await expect(page.locator(".cena-mundo-racao")).toHaveCount((await lerMundo(page)).comidas.filter(c => c.situacao).length);
    await esperarComer(page, nova.id);
    await cenaSegueMotor(page);
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
/* a ilha 3D (docs/TAREFA_V3_HABITAT_ILHA_3D.md, H5): o ponto da tela, longe do pet e na diagonal, passa pela dobra do mundo curvo e
   cai no motor dentro de 1 celula (16 subunidades) do ponto do mapa que a vista desenhou ali */
for (const largura of [390, 1280] as const) {
  test(`ilha: soltar a ração num ponto da tela cai no ponto do mapa, com 1 célula de folga (${largura} px)`, async ({ browser }) => {
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: largura >= 1100 ? 800 : 844 } });
    const page = await ctx.newPage();
    await semear(page, SAVE_MUNDO);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-cena .cena3d canvas")).toBeVisible();
    await expect.poll(() => lerCena(page)).not.toBeNull();
    expect((await lerCena(page))!.modo3d).toBe(true);
    await cenaSegueMotor(page);
    /* 3 celulas a leste e 3 ao norte do pet (o ponto ainda esta na tela nas duas larguras), preso no mapa */
    const m0 = await lerMundo(page), sub = 16;
    const alvo: [number, number] = [Math.min(63 * sub, m0.pet[0] + 3 * sub), Math.max(sub, m0.pet[1] - 3 * sub)];
    const ponto = await naTela(page, alvo[0], alvo[1]);
    const caixa = (await page.locator(".pet-cena .cena3d canvas").boundingBox())!;
    expect(ponto[0]).toBeGreaterThan(caixa.x); expect(ponto[0]).toBeLessThan(caixa.x + caixa.width);
    expect(ponto[1]).toBeGreaterThan(caixa.y); expect(ponto[1]).toBeLessThan(caixa.y + caixa.height);
    await arrastarRacao(page, ponto);
    const dc = await ultimoDc(page);
    expect(dc[2].tipo).toBe("racao");
    expect(Math.abs(dc[2].x - alvo[0]), "x do ponto solto").toBeLessThanOrEqual(sub);
    expect(Math.abs(dc[2].y - alvo[1]), "y do ponto solto").toBeLessThanOrEqual(sub);
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
test("mundo: o caminho acessível, pelo toque no chão e por um lugar nomeado pelo teclado; Esc fecha sem pôr nada", async ({ page }) => {
  test.setTimeout(180_000);
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_MUNDO);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  await expect.poll(() => lerCena(page)).not.toBeNull();
  const bt = page.getByRole("button", { name: /^Pôr ração/ });
  /* o toque: tocar no botao abre a faixa; tocar no chao poe ali */
  await abrirMais(page);
  await bt.click();
  await expect(page.locator(".racao-faixa")).toContainText("Toque no chão para pôr a ração");
  await abrirMais(page);
  await expect(bt).toHaveAttribute("aria-pressed", "true");
  await page.locator(".acoes-pet .acao-mais").click();                 /* o menu aberto cobre parte do chao: fecha antes de tocar nele */
  const m0 = await lerMundo(page), [cx, cy] = await naTela(page, m0.lugares.perto[0] + 32, m0.lugares.perto[1]);
  await page.mouse.click(cx, cy);
  await expect(page.locator(".racao-faixa")).toHaveCount(0);
  const dc1 = await ultimoDc(page);
  expect(Math.abs(dc1[2].x - (m0.lugares.perto[0] + 32)) + Math.abs(dc1[2].y - m0.lugares.perto[1])).toBeLessThanOrEqual(2);
  /* Esc fecha sem por nada */
  const n1 = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro())).log.filter((e: unknown[]) => e[1] === "dc").length;
  await abrirMais(page);
  await bt.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".racao-faixa")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator(".racao-faixa")).toHaveCount(0);
  expect(JSON.parse(await page.evaluate(() => (window as any).__digilab.registro())).log.filter((e: unknown[]) => e[1] === "dc").length).toBe(n1);
  /* o teclado: Enter abre, o foco vai ao Comedouro; Tab ao "Perto do pet" e Enter poe exatamente no lugar nomeado */
  await abrirMais(page);
  await bt.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("button", { name: "Comedouro", exact: true })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Perto do pet", exact: true })).toBeFocused();
  const perto = (await lerMundo(page)).lugares.perto;
  await page.keyboard.press("Enter");
  const dc2 = await ultimoDc(page);
  expect([dc2[2].x, dc2[2].y]).toEqual(perto);
  expect(erros).toEqual([]);
});
test("mundo: soltar fora do chão não põe nada; recarregar refaz a vida com a ração do registro", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_MUNDO);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  await expect.poll(() => lerCena(page)).not.toBeNull();
  const reg = async () => JSON.parse(await page.evaluate(() => (window as any).__digilab.registro())).log as unknown[][];
  const n0 = (await reg()).filter(e => e[1] === "dc").length;
  /* no ceu da cena (acima do chao) e fora da cena: nenhum evento */
  const caixa = (await page.locator(".pet-cena").boundingBox())!;
  await arrastarRacao(page, [caixa.x + caixa.width / 2, caixa.y + 8]);
  await arrastarRacao(page, [caixa.x + caixa.width / 2, caixa.y + caixa.height + 120]);
  expect((await reg()).filter(e => e[1] === "dc").length).toBe(n0);
  await expect(page.locator(".racao-dica")).toContainText("fora do mapa nada é posto");
  /* o aviso some sozinho; a regiao aria-live fica montada */
  await expect(page.locator(".racao-dica")).toBeEmpty({ timeout: 10_000 });
  await expect(page.locator(".racao-dica")).toHaveAttribute("aria-live", "polite");
  /* pelo teclado, e recarregar: o evento dc fica no registro, e a vida refeita tem a racao no mesmo lugar */
  await abrirMais(page);
  await page.getByRole("button", { name: /^Pôr ração/ }).click();
  await page.getByRole("button", { name: "Longe", exact: true }).click();
  const antes = await reg(), dc = antes.filter(e => e[1] === "dc").at(-1)!, i = antes.lastIndexOf(dc);
  await page.reload();
  await expect.poll(() => lerCena(page)).not.toBeNull();
  const depois = await reg();
  expect(depois.slice(0, i + 1)).toEqual(antes.slice(0, i + 1));
  const m = await lerMundo(page), p = dc[2] as { x: number; y: number };
  expect(m.comidas.some(c => c.x === p.x && c.y === p.y) || m.consumos.length > 0).toBe(true);
  expect(erros).toEqual([]);
});
test("mundo: o Alimentar dos v12 é a reserva temporária, descrita assim, e põe a ração no comedouro", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_MUNDO);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  const al = page.getByRole("button", { name: "Alimentar (reserva: põe a ração no comedouro)" });
  await expect(al).toHaveAttribute("title", "Reserva temporária: põe a ração no comedouro");
  /* a dica fica na faixa do Pôr ração (fora da cena) */
  await abrirMais(page);
  await page.getByRole("button", { name: /^Pôr ração/ }).click();
  await expect(page.locator(".racao-faixa")).toContainText("Alimentar é a reserva: põe no comedouro.");
  await page.locator(".racao-faixa").getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(page.locator(".racao-faixa")).toHaveCount(0);
  await al.click();
  const dc = await ultimoDc(page), m = await lerMundo(page);
  expect([dc[2].x, dc[2].y]).toEqual(m.comedouro);
  expect(erros).toEqual([]);
});
/* o ovo de um pet novo (v12) chocando na cena 3D: a contagem dos quadros do ovo continua no PalcoPet com a cena 3D (o conserto do #398) */
test("mundo: o ovo novo choca na cena 3D", async ({ page }) => {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([c, s]) => {
    localStorage.clear(); localStorage.setItem(c + "-boas-vindas", "1"); localStorage.setItem(c + "-dicas-ligadas", "0");
    localStorage.setItem(c, s); localStorage.setItem(c + "-guardados", "[]");
  }, [CHAVE, JSON.stringify(SAVE_ANTIGO_V3)] as const);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  /* o pet de antes sai com o descarte 6 (a luta em tempo real), e o aviso leva ao brasao do ovo novo */
  await page.locator("dialog.aviso-tr[open]").getByRole("button", { name: "Escolher o brasão do ovo novo" }).click();
  await page.locator("dialog.brasao-tela[open] .br-card").first().click();
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect.poll(() => page.evaluate(() => document.querySelector<HTMLCanvasElement>(".cena3d canvas")?.width ?? 0)).toBeGreaterThan(0);
  const lcd = page.locator(".pet-cena canvas.lcd");
  await expect(lcd).toHaveAttribute("aria-label", "Tela do pet: ovo");
  await expect(lcd).not.toHaveAttribute("aria-label", "Tela do pet: ovo", { timeout: 20_000 });
  await infoMundoNoEstado(page, null);
  expect(erros).toEqual([]);
});

/* UP-SOM: o som e desligado por padrao. Desligado, nenhuma requisicao de audio sai (nem em uma luta inteira); ligar e lembrado ao
   recarregar e nao entra no save exportado; ligado com os arquivos ausentes, o aviso aparece e o jogo segue. */
test("som: desligado por padrão não pede áudio nem em uma luta; ligar é lembrado e fica fora do save", async ({ page }) => {
  test.setTimeout(180_000);
  await semear(page, SAVES.champion);
  const erros = vigiarErros(page), pedidos: string[] = [];
  page.on("request", r => { if (/\/Assets\/sons\/|\.mp3(\?|$)/.test(r.url())) pedidos.push(r.url()); });
  await page.goto(APP + "#/pet/estado");
  await irPara(page, "Lutar", "Arena", "lutar/arena");
  await page.getByTestId("poc-lutar").click();
  await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 90_000 });
  expect(pedidos, "pediu áudio com o som desligado").toEqual([]);
  await page.getByTestId("poc-resultado").getByRole("button", { name: "Continuar" }).click();
  /* Configuração: padrão desligado; ligar e mexer no volume ficam no localStorage do app e voltam ao recarregar */
  await page.locator(".dl-nav .nav-quad", { hasText: "Ajustes" }).click();
  const chave = page.getByRole("switch", { name: /Som do jogo/ }), vol = page.getByLabel("Volume do som");
  await expect(chave).not.toBeChecked();
  await chave.check();
  await vol.fill("0.3");
  await page.reload();
  await page.locator(".dl-nav .nav-quad", { hasText: "Ajustes" }).click();
  await expect(page.getByRole("switch", { name: /Som do jogo/ })).toBeChecked();
  await expect(page.getByLabel("Volume do som")).toHaveValue("0.3");
  const guardado = await page.evaluate(([c]) => ({ som: localStorage.getItem(c + "-som"), vol: localStorage.getItem(c + "-som-volume"), save: localStorage.getItem(c) }), [CHAVE] as const);
  expect(guardado.som).toBe("1"); expect(guardado.vol).toBe("0.3");
  expect(guardado.save).not.toMatch(/som/i);
  const reg = await page.evaluate(() => (window as any).__digilab.registro());
  expect(reg).not.toMatch(/som/i);
  expect(erros.filter(e => !/sons?\//i.test(e) && !/mp3|mapa de sons|Failed to load resource/i.test(e))).toEqual([]);
});

test("som: ligado com os arquivos ausentes mostra o aviso e a tela segue", async ({ page }) => {
  await semear(page, SAVES.champion);
  await page.route(/\/Assets\/sons\//, r => r.fulfill({ status: 404, body: "ausente" }));
  await page.goto(APP + "#/pet/estado");
  await page.locator(".dl-nav .nav-quad", { hasText: "Ajustes" }).click();
  await page.getByRole("switch", { name: /Som do jogo/ }).check();
  await expect(page.getByTestId("aviso-som").first()).toBeVisible();
  await expect(page.getByTestId("aviso-som").first()).toContainText("mapa de sons");
  await page.getByRole("switch", { name: /Som do jogo/ }).uncheck();
  await expect(page.getByRole("switch", { name: /Som do jogo/ })).not.toBeChecked();
});

/* TAREFA_V2_UP_ATLAS: com a chave dos clipes ligada (?clipes_up=1) e o atlas de clipes ausente, o aviso do atlas aparece; nao cai calado no atlas atual */
test("clipes do UP: ligados e sem o atlas de clipes, o aviso de atlas que não carregou", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVES.champion);
  await page.route(/\/Assets\/digilab_atlas_up_clipes/, r => r.abort());
  await page.goto(APP + "?clipes_up=1#/pet/estado");
  await expect(page.getByText("Atlas de sprites não carregou.")).toBeVisible();
});

/* T2 do tema dos menus (docs/TAREFA_V2_TEMA_MENUS.md §5): a pele em Ajustes > Aparencia. Padrao Holografico; os cartoes trocam o
   data-pele na hora (sem recarregar), pelo clique e pelas setas; a escolha fica gravada e sobrevive ao recarregar; "XCOM" nao aparece */
test("pele dos menus: Ajustes › Visual troca na hora e a escolha sobrevive ao recarregar", async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 950 });
  await semear(page, SAVES.champion);
  const erros = vigiarErros(page);
  const pele = () => page.evaluate(() => document.documentElement.dataset.pele);
  const gravada = () => page.evaluate(c => localStorage.getItem(c + "-pele"), CHAVE);
  await page.goto(APP + "#/config");
  await expect(page.locator(".mc-cfg")).toContainText("pele Sci-fi · tema");
  await page.locator(".mc-cfg .aj", { hasText: "Visual" }).click();
  const grupo = page.getByRole("radiogroup", { name: "Pele dos menus" });
  const militar = grupo.getByRole("radio", { name: "Militar" }), holo = grupo.getByRole("radio", { name: "Sci-fi" });
  await expect(holo).toHaveAttribute("aria-checked", "true");
  expect(await pele()).toBe("vidro");
  /* a secao vem acima do Tema do habitat; alvos de toque >= 44 px */
  const [g, t] = [await grupo.boundingBox(), await page.getByRole("radiogroup", { name: "Tema do habitat" }).boundingBox()];
  expect(g!.y).toBeLessThan(t!.y);
  for (const c of [militar, holo]) expect((await c.boundingBox())!.height).toBeGreaterThanOrEqual(44);
  await expect(page.locator("body")).not.toContainText(/xcom/i);
  await page.screenshot({ path: "test-results/pele-aparencia-vidro.png" });

  await militar.click();
  expect(await pele()).toBe("xcom");
  await page.screenshot({ path: "test-results/pele-aparencia-militar.png" });
  await expect(militar).toHaveAttribute("aria-checked", "true");
  expect(await gravada()).toBe("xcom");
  /* pelas setas: a seta volta ao Holografico e leva o foco junto */
  await page.keyboard.press("ArrowLeft");
  await expect(holo).toHaveAttribute("aria-checked", "true");
  await expect(holo).toBeFocused();
  expect(await pele()).toBe("vidro");
  await page.keyboard.press("End");
  await expect(militar).toBeFocused();
  expect(await pele()).toBe("xcom");

  await page.reload();
  expect(await pele()).toBe("xcom");
  await expect(page.getByRole("radiogroup", { name: "Pele dos menus" }).getByRole("radio", { name: "Militar" })).toHaveAttribute("aria-checked", "true");
  await page.goto(APP + "#/config");
  await expect(page.locator(".mc-cfg")).toContainText("pele Militar · tema");
  await page.screenshot({ path: "test-results/pele-ajustes-militar.png" });
  /* ?pele= no endereco sobrepoe sem gravar (T3): vale so nesta abertura */
  await page.goto(APP + "?pele=vidro#/config");
  await expect(page.locator(".mc-cfg")).toContainText("pele Sci-fi · tema");
  expect(await pele()).toBe("vidro");
  expect(await gravada()).toBe("xcom");
  await page.goto(APP + "#/config");
  await expect(page.locator(".mc-cfg")).toContainText("pele Militar · tema");
  expect(await pele()).toBe("xcom");
  expect(erros).toEqual([]);
});
