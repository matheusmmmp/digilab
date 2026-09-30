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

const SAVES: Record<string, { semente: number; log: unknown[]; versao?: number }> = JSON.parse(readFileSync(new URL("./saves.json", import.meta.url), "utf8"));
// prefixo = nome da pasta do repositorio (/v1 ou o da worktree), como no servidor_local.py
const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, HTML = `${PREFIXO}/web/digilab_sprites.html?antigo=1`, CHAVE = "digilab-web-v21-sprites";
const ABAS: [string, string, string][] = [
  ["Pet", "", "pet/estado"], ["Crescer", "Treinar", "crescer/treinar"], ["Crescer", "Aprendizado", "crescer/aprend"], ["Crescer", "Evolução", "crescer/evolucao"],
  ["Crescer", "Itens", "crescer/itens"],
  ["Lutar", "Arena", "lutar/arena"], ["Lutar", "Campanha", "lutar/campanha"], ["Lutar", "Medalhas", "lutar/medalhas"], ["Diário", "Registro", "diario/registro"], ["Diário", "Catálogo", "diario/catalogo"],
  ["Diário", "Cenários", "diario/cenarios"], ["Conversar", "", "conversar/chat"],
];

/** semeia o save por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele ao fechar). O registro do Tamer
    (vazio, ou o dado) e o marcador do descarte (versao 5) vao junto: com eles o app entende que o descarte unico ja rodou
    e nao descarta os saves antigos (v1-v3, e o v6) que estes testes jogam */
async function semear(page: Page, save: object | null, tema?: string, tamer: object = { versao: 1, log: [] }): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t, tm]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", tm);
    localStorage.setItem(chave + "-descarte", "5");
    /* dicas do Bit desligadas e sem os pets guardados de exemplo: os testes de fluxo nao dependem deles */
    localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    if (s) localStorage.setItem(chave, s);
    if (t) localStorage.setItem(chave + "-tema", t);
  }, [CHAVE, save ? JSON.stringify(save) : null, tema ?? null, JSON.stringify(tamer)] as const);
}
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
const numLog = (page: Page, tipo: string) => page.evaluate(([t]) => JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] === t).length, [tipo] as const);

for (const [versao, save] of Object.entries(SAVES)) {
  test(`jogo completo com save ${versao}: assinatura igual à do HTML`, async ({ page, context }) => {
    await semear(page, save);            /* a pagina de semear e um JSON: o favicon dela da 404, fora do app */
    const erros = vigiarErros(page);
    /* ?escala=0: a assinatura se compara com o HTML antigo, que nao tem a escala de stats (a campanha muda com ela) */
    await page.goto(APP + "?escala=0#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    await expect(page.locator(".pet-cab .dl-tag--estagio")).toHaveText(/Champion/i);

    /* os 5 destinos e as 11 abas, pela barra e pelas abas */
    for (const [destino, aba, rota] of ABAS) {
      await page.locator(".dl-nav").getByRole("button", { name: destino, exact: true }).click();
      if (aba) await page.getByRole("tab", { name: aba }).click();
      await expect(page).toHaveURL(new RegExp("#/" + rota + "$"));
    }

    /* cuidar */
    await page.locator(".dl-nav").getByRole("button", { name: "Pet", exact: true }).click();
    const d0 = await numLog(page, "d");
    for (const a of ["Alimentar", "Limpar", "Brincar", "Carinho", "Elogiar"]) await page.locator(".acoes-pet button", { hasText: a }).click();
    expect(await numLog(page, "d")).toBe(d0 + 5);

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

    /* lutar na arena e na campanha */
    const l0 = await numLog(page, "l");
    await page.locator(".dl-nav button", { hasText: "Lutar" }).click();
    await page.getByRole("tab", { name: "Arena" }).click();
    /* a luta abre em tela cheia (#/lutar/luta); no fim, o modal Resultado; Continuar volta para a aba de origem */
    await page.locator(".lutar-grande").click();
    await expect(page).toHaveURL(/#\/lutar\/luta$/);
    await expect(page.locator(".dl-nav")).toHaveCount(0);
    const res = page.locator("dialog.modal-res[open]");
    await expect(res).toBeVisible({ timeout: 90_000 });
    await expect(page.locator(".res-continuar")).toBeFocused();
    await page.keyboard.press("Escape");                     /* Esc faz o mesmo que Continuar */
    await expect(page).toHaveURL(/#\/lutar\/arena$/);
    await expect(page.locator(".lutar-grande")).toBeFocused();
    /* Ver replay: a mesma luta refeita do registro no Diario; o Voltar leva de volta a Arena */
    await page.locator(".lutar-grande").click();
    await expect(res).toBeVisible({ timeout: 90_000 });
    const turnos = await page.locator(".res-num", { hasText: "turnos" }).first().locator(".dl-num").textContent();
    await page.locator(".res-replay").click();
    await expect(page).toHaveURL(/#\/diario\/registro$/);
    await expect(page.locator(".reg-replay")).toContainText(`em ${turnos} turnos`);
    await expect(page.locator(".reg-replay-turnos li")).toHaveCount(Number(turnos));
    /* rever a luta no palco: animada em tela cheia, no fim volta ao Diario, e nada entra no registro */
    const lAntes = await numLog(page, "l");
    await page.getByRole("button", { name: "Ver a luta no palco" }).click();
    await expect(page).toHaveURL(/#\/lutar\/luta$/);
    await expect(page.locator("#fim-rep-tit")).toBeVisible({ timeout: 90_000 });
    await page.getByRole("button", { name: "Voltar ao Diário" }).click();
    await expect(page).toHaveURL(/#\/diario\/registro$/);
    await expect(page.locator(".reg-replay")).toBeVisible();
    expect(await numLog(page, "l")).toBe(lAntes);
    await page.goBack();
    await expect(page).toHaveURL(/#\/lutar\/arena$/);
    await page.getByRole("tab", { name: "Campanha" }).click();
    await page.locator(".camp-lutar:not([disabled])").click();
    await expect(res).toBeVisible({ timeout: 90_000 });
    await page.locator(".res-continuar").click();
    await expect(page).toHaveURL(/#\/lutar\/campanha$/);
    expect(await numLog(page, "l")).toBe(l0 + 3);

    /* pausa o tempo (Ajustes no pe da barra > Registro e replay) e confere a assinatura com o HTML rodando o mesmo registro */
    await page.locator(".dl-nav .nav-quad", { hasText: "Ajustes" }).click();
    await page.getByRole("button", { name: /^Registro e replay/ }).click();
    await page.getByRole("button", { name: "Pausa" }).click();
    await page.waitForTimeout(300);
    const { assinatura, registro } = await page.evaluate(() => ({ assinatura: (window as any).__digilab.assinatura(), registro: (window as any).__digilab.registro() }));
    const html = await context.newPage();
    const errosHtml = vigiarErros(html);
    await html.goto(HTML);
    /* o Motor do HTML e uma classe no topo de um script classico: nao fica em window, so no escopo global */
    await html.waitForFunction(() => { try { return typeof eval("Motor") === "function"; } catch { return false; } });
    const doHtml = await html.evaluate(r => { const d = JSON.parse(r); return eval("Motor").reproduzir(d.semente, d.log, d.versao ?? 1).assinatura(); }, registro);
    expect(doHtml, "assinatura do HTML para o mesmo registro").toBe(assinatura);
    /* controle negativo: um evento a menos no registro da outra assinatura */
    const semUltimo = await html.evaluate(r => { const d = JSON.parse(r); return eval("Motor").reproduzir(d.semente, d.log.slice(0, -1), d.versao ?? 1).assinatura(); }, registro);
    expect(semUltimo).not.toBe(assinatura);
    expect(JSON.parse(registro).versao).toBe(save.versao ?? 1);
    expect(erros, "erros no console do app").toEqual([]);
    expect(errosHtml.filter(e => !/fala-livre|favicon/.test(e)), "erros no console do HTML").toEqual([]);
  });
}

for (const tema of ["light", "dark"] as const) for (const largura of [360, 390]) {
  test(`guia, secao 14: ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVES.v3);
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

/* varios pets, um ativo (pedido do Matheus): a escada de exemplo e criada no primeiro acesso, os guardados ficam parados
   no tempo (o registro deles nao muda enquanto o ativo corre) e Ativar troca o pet */
test("vários pets: só o ativo corre o tempo", async ({ page }) => {
  await semear(page, SAVES.v3);
  await page.evaluate(c => localStorage.removeItem(c + "-guardados"), CHAVE);
  await page.goto(APP + "#/pet/estado");
  await page.waitForFunction(c => localStorage.getItem(c + "-guardados") !== null, CHAVE, { timeout: 60_000 });
  const ler = () => page.evaluate(c => ({ g: localStorage.getItem(c + "-guardados")!, a: localStorage.getItem(c)! }), CHAVE);
  const antes = await ler();
  expect(JSON.parse(antes.g)).toHaveLength(6);
  await page.waitForTimeout(3000);
  const depois = await ler();
  expect(depois.g).toBe(antes.g);                  /* guardados parados */
  expect(depois.a).not.toBe(antes.a);              /* o ativo andou (o registro junta avanços de tempo seguidos) */
  await page.locator(".topo-retrato").click();
  /* desktop (MpListaDesktop): pagina com um espaco por pet (o ativo + 6 guardados) e o painel do escolhido */
  await expect(page.locator(".mpl-slot:not(.mpl-livre)")).toHaveCount(7);
  await page.locator(".mpl-slot").nth(1).click();
  await page.locator(".mpl-detalhe").getByRole("button", { name: "Tornar ativo" }).click();
  await expect(page.locator(".topo-pet .dl-tag--estagio")).toHaveText(/In-Training/i);
  const g = JSON.parse(await page.evaluate(c => localStorage.getItem(c + "-guardados")!, CHAVE));
  expect(g).toHaveLength(6);                       /* o Champion de antes foi para o lugar dele */
});

test("foco visível pelo teclado", async ({ page }) => {
  await semear(page, SAVES.v2);
  await page.goto(APP + "#/pet/estado");
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

/* layouts (tokens.css): abaixo de 900 px o das pranchas de celular (barra embaixo, uma coluna); de 900 a 1099 barra
   lateral e uma coluna; de 1100 em diante o das pranchas *Desktop (conteudo + painel ao lado) */
for (const largura of [390, 899, 900, 1099, 1100, 1280]) {
  test(`layout em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await semear(page, SAVES.v3);
    const lateral = largura >= 900, desktop = largura >= 1100;
    for (const [rota, esq, dir] of [["crescer/evolucao", ".evo-arv", ".evo-hist"], ["lutar/campanha", ".mapa-ilhas", ".camp-lutar"], ["conversar/chat", ".conv-lista", ".conv-status"]]) {
      await page.goto(APP + "#/" + rota);
      await page.waitForTimeout(500);
      const r = await page.evaluate(([e, d]) => {
        const nav = document.querySelector(".dl-nav")!.getBoundingClientRect(), a = document.querySelector(e)!.getBoundingClientRect(), b = document.querySelector(d)!.getBoundingClientRect();
        return { navLateral: nav.height > nav.width, aoLado: b.left >= a.right - 1, larg: document.documentElement.scrollWidth, janela: innerWidth };
      }, [esq, dir] as const);
      expect(r.navLateral, `${rota}: barra lateral`).toBe(lateral);
      expect(r.aoLado, `${rota}: painel ao lado do conteúdo`).toBe(desktop);
      expect(r.larg, `${rota}: rolagem lateral`).toBeLessThanOrEqual(r.janela);
    }
  });
}

/* ---------------------------------------------------------------- medalhas do Tamer (docs/DESIGN_MEDALHAS_ARENAS.md)
   save_medalhas.json (e2e/gerar_save_medalhas.mjs): pet v6 no Rookie, treinado, pronto para evoluir e esperando a 1a
   medalha; a luta do Desafiar contra o Gazimon e vitoria em qualquer hora das proximas 5 h de jogo */
const SAVE_V6 = JSON.parse(readFileSync(new URL("./save_medalhas.json", import.meta.url), "utf8"));
const lerTamer = (page: Page) => page.evaluate(c => JSON.parse(localStorage.getItem(c + "-tamer") ?? "null"), CHAVE);

test("medalhas: vencer o líder dá a medalha e libera a evolução", async ({ page }) => {
  await semear(page, SAVE_V6);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/crescer/evolucao");
  await expect(page.locator(".evo-medalha")).toContainText("Pronto para evoluir. Falta a Medalha da Campina: vença o Gazimon na Campina.");
  await page.goto(APP + "#/lutar/campanha");
  await expect(page.locator(".camp-arena")).toContainText("líder: Gazimon");
  await expect(page.locator(".camp-arena")).toContainText("Vencer Gazimon dá a Medalha da Campina.");
  await expect(page.locator(".camp-lider").first()).toContainText("LÍDER");
  await page.locator(".camp-lutar:not([disabled])").click();
  const res = page.locator("dialog.modal-res[open]");
  await expect(res).toBeVisible({ timeout: 90_000 });
  await expect(res.locator(".res-medalha")).toContainText("Medalha da Campina");
  await page.locator(".res-continuar").click();
  /* o pet evoluiu no tick da medalha: a revelacao abre depois do Resultado */
  const rev = page.locator("dialog.revelacao[open]");
  await expect(rev).toBeVisible();
  await expect(rev.locator(".revel-de")).toContainText("Rookie → Champion");
  await rev.getByRole("button", { name: "Continuar" }).click();
  await expect(page).toHaveURL(/#\/crescer\/evolucao$/);
  const t = await lerTamer(page);
  expect(t.log.map((e: [string, { id: string }]) => e[1].id)).toEqual(["campina", "chip_forca"]);   /* a medalha e o item dela */
  const reg = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro()));
  expect(reg.versao).toBe(6);
  expect(reg.log.filter((e: unknown[]) => e[1] === "u")).toEqual([[expect.any(Number), "u", { n: 1 }]]);
  await page.goto(APP + "#/lutar/medalhas");
  await expect(page.locator(".med-conta .dl-num")).toHaveText("1");
  await expect(page.locator(".med-card.ganha")).toHaveCount(1);
  await expect(page.locator(".med-card.ganha")).toContainText("Medalha da Campina");
  await expect(page.locator(".med-card").nth(2)).toContainText("Vença o Youkomon na Floresta");
  await expect(page.locator(".med-card").nth(3)).toContainText("Vença o Myotismon três vezes seguidas na Cidadela");
  await expect(page.locator(".med-card").nth(4)).toContainText("Vínculo:");
  await expect(page.locator(".med-tela")).not.toContainText("provisória");
  expect(erros).toEqual([]);
});

test("medalhas: a primeira abertura descarta os pets antigos, avisa e pede o brasão do ovo novo", async ({ page }) => {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([c, s]) => {
    localStorage.clear(); localStorage.setItem(c + "-boas-vindas", "1"); localStorage.setItem(c + "-dicas-ligadas", "0");
    localStorage.setItem(c, s); localStorage.setItem(c + "-guardados", JSON.stringify([JSON.parse(s)]));
  }, [CHAVE, JSON.stringify(SAVES.v3)] as const);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  const aviso = page.locator("dialog.med-aviso[open]");
  await expect(aviso).toContainText("os 2 pets que você tinha (o ativo e os guardados) foram descartados");
  await page.keyboard.press("Escape");                             /* o aviso so sai pelo botao */
  await expect(aviso).toBeVisible();
  await aviso.getByRole("button", { name: "Escolher o brasão do ovo novo" }).click();
  const br = page.locator("dialog.brasao-tela[open]");
  await expect(br.locator("#br-tit")).toHaveText("Escolha seu brasão");
  await expect(br.getByRole("button", { name: "Voltar" })).toHaveCount(0);
  await br.locator(".br-card").first().click();
  await expect(page.locator("dialog.brasao-tela[open]")).toHaveCount(0);
  const r = await page.evaluate(c => ({ save: JSON.parse(localStorage.getItem(c)!), g: localStorage.getItem(c + "-guardados"), aviso: localStorage.getItem(c + "-aviso-v6"),
    tamer: JSON.parse(localStorage.getItem(c + "-tamer")!) }), CHAVE);
  expect(r.save.versao).toBe(6);
  expect(r.g).toBe("[]");
  expect(r.aviso).toBeNull();
  expect(r.tamer).toEqual({ versao: 2, log: [] });
  await page.reload();
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator("dialog.med-aviso")).toHaveCount(0);
  expect(erros).toEqual([]);
});

test("combate V21D e arenas: o pet v6 de antes sai com o mesmo aviso, e o Tamer recomeça sem medalhas", async ({ page }) => {
  const tamer = { versao: 1, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: SAVE_V6.semente, forma: "Armadillomon", tick: 900 }]] };
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([c, s, tm]) => {
    /* o descarte das medalhas ja rodou (Tamer gravado, sem o marcador novo): so falta o do V21D */
    localStorage.clear(); localStorage.setItem(c + "-boas-vindas", "1"); localStorage.setItem(c + "-dicas-ligadas", "0");
    localStorage.setItem(c, s); localStorage.setItem(c + "-guardados", "[]"); localStorage.setItem(c + "-tamer", tm);
  }, [CHAVE, JSON.stringify(SAVE_V6), JSON.stringify(tamer)] as const);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  const aviso = page.locator("dialog.med-aviso[open]");
  await expect(aviso).toContainText("o pet que você tinha foi descartado");
  await aviso.getByRole("button", { name: "Escolher o brasão do ovo novo" }).click();
  await page.locator("dialog.brasao-tela[open] .br-card").first().click();
  await expect(page.locator("dialog.brasao-tela[open]")).toHaveCount(0);
  const r = await page.evaluate(c => ({ save: JSON.parse(localStorage.getItem(c)!), marca: localStorage.getItem(c + "-descarte"),
    tamer: JSON.parse(localStorage.getItem(c + "-tamer")!) }), CHAVE);
  expect(r.save.versao).toBe(6);
  expect(r.save.semente).not.toBe(SAVE_V6.semente);
  expect(r.marca).toBe("5");
  expect(r.tamer).toEqual({ versao: 2, log: [] });
  await page.reload();
  await expect(page.locator(".pet-tela")).toBeVisible();
  await expect(page.locator("dialog.med-aviso")).toHaveCount(0);
  expect(erros).toEqual([]);
});

/* tela de medalhas com uma medalha ganha: celular (360, 390) e desktop (1280), claro e escuro */
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`medalhas: tela em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    const tamer = { versao: 1, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: SAVE_V6.semente, forma: "Armadillomon", tick: 900 }]] };
    await semear(page, SAVE_V6, undefined, tamer);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/lutar/medalhas");
    await expect(page.locator(".med-card")).toHaveCount(6);
    await expect(page.locator(".med-card.ganha")).toContainText("ganha com Armadillomon");
    await page.waitForTimeout(600);
    /* no desktop, so a tela (as abas em pilula do topo da casca tem 40 px nas pranchas *Desktop; o guia 14 e do celular) */
    const r = await page.evaluate(desk => {
      const visivel = (e: Element) => (e as HTMLElement).offsetParent !== null;
      const pequenos = [...document.querySelector(desk ? ".med-tela" : "body")!.querySelectorAll("button, select, input, summary, a")].filter(visivel).flatMap(e => {
        const b = e.getBoundingClientRect();
        return b.height < 44 || b.width < 44 ? [`${e.tagName}.${(e as HTMLElement).className} ${Math.round(b.width)}x${Math.round(b.height)}`] : [];
      });
      const lista = document.querySelector(".med-lista")!.getBoundingClientRect(), resumo = document.querySelector(".med-resumo")!.getBoundingClientRect();
      return { larg: document.documentElement.scrollWidth, janela: innerWidth, pequenos, aoLado: lista.left >= resumo.right - 1 };
    }, largura >= 1100);
    expect(r.larg, "rolagem lateral").toBeLessThanOrEqual(r.janela);
    expect(r.pequenos, "alvos menores que 44 px").toEqual([]);
    expect(r.aoLado, "desktop: a lista ao lado do resumo").toBe(largura >= 1100);
    await expect(page.locator(".med-regras li.ok")).toHaveCount(1);
    expect(erros).toEqual([]);
  });
}

/* ---------------------------------------------------------------- arenas com lideres (medalhas parte 2)
   save_arenas.json (e2e/gerar_save_arenas.mjs): pet v6 Ultimate treinado, com a Campina, a Torre e a Floresta vencidas e o
   Tamer com as 3 medalhas; a luta do Desafiar contra o Myotismon (Cidadela: tres lutas seguidas) e a serie vencida em
   qualquer hora das proximas 5 h de jogo */
const SAVE_ARENAS = JSON.parse(readFileSync(new URL("./save_arenas.json", import.meta.url), "utf8"));
const TAMER_3 = { versao: 1, log: ["campina", "torre", "floresta"].map((id, i) =>
  ["medalha", { id, n: i + 1, quando: 1 + i, pet: SAVE_ARENAS.semente, forma: "DinoBeemon", tick: 900 + i }]) };

test("arenas: a Cidadela pede três lutas seguidas sem cura e dá a medalha; no Lago as travas não valem", async ({ page }) => {
  test.setTimeout(240_000);
  await semear(page, SAVE_ARENAS, undefined, TAMER_3);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/campanha");
  await expect(page.locator(".mapa-ilhas img.ilha")).toHaveCount(6);
  const cartao = page.locator(".camp-arena");
  await expect(cartao).toContainText("Arena · Resistência");
  await expect(cartao).toContainText("líder: Myotismon");
  await expect(cartao).toContainText("Três lutas seguidas, sem cura");
  const lutar = page.locator(".camp-lutar:not([disabled])");
  await expect(lutar).toContainText("Desafiar Myotismon (3 lutas seguidas)");
  await lutar.click();
  await expect(page.locator(".luta-topo-sub")).toContainText("luta 1 de 3");
  await expect(page.locator(".luta-serie")).toContainText("sem cura entre as lutas");
  await page.locator(".luta-ctl--x2").click();
  await expect(page.locator(".luta-serie")).toContainText("Luta 2 de 3", { timeout: 90_000 });
  const res = page.locator("dialog.modal-res[open]");
  await expect(res).toBeVisible({ timeout: 150_000 });
  await expect(res.locator(".res-serie li")).toHaveCount(3);
  await expect(res.locator(".res-serie")).not.toContainText("perdeu");
  await expect(res.locator(".res-sub")).toContainText("venceu as 3 lutas seguidas");
  await expect(res.locator(".res-medalha")).toContainText("Medalha da Cidadela");
  await page.locator(".res-continuar").click();
  const t = await lerTamer(page);
  /* as medalhas (os itens das 3 primeiras entraram na abertura; o da Cidadela, com ela) */
  expect(t.log.filter((e: [string]) => e[0] === "medalha").map((e: [string, { id: string }]) => e[1].id)).toEqual(["campina", "torre", "floresta", "cidadela"]);
  expect(t.log.filter((e: [string]) => e[0] === "item").map((e: [string, { id: string }]) => e[1].id)).toEqual(["chip_forca", "chip_recuo", "chip_oportunista", "chip_guarda"]);
  const reg = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro()));
  const lutas = reg.log.filter((e: unknown[]) => e[1] === "l");
  expect(lutas[lutas.length - 1][2]).toEqual({ r: "npc_v5_myotismon", s: expect.any(Number) });   /* o evento continua so rival e semente */
  expect(reg.log.filter((e: unknown[]) => e[1] === "u").map((e: [number, string, { n: number }]) => e[2].n)).toEqual([3, 4]);
  /* o Lago abriu: a regra do vinculo aparece no cartao e na luta */
  await page.goto(APP + "#/lutar/campanha");
  await expect(page.locator(".camp-arena")).toContainText("Arena · Vínculo");
  await page.locator(".camp-lutar:not([disabled])").click();
  await expect(page.locator(".luta-arena-aviso")).toContainText("Arena do Lago: aqui as suas travas e vetos não valem");
  await expect(page.locator(".regra-travar")).toHaveCount(0);
  await page.locator(".luta-ctl--x2").click();
  await expect(res).toBeVisible({ timeout: 90_000 });
  await expect(res.locator(".res-arena-nota")).toContainText("sem as suas travas e vetos");
  await page.locator(".res-continuar").click();
  expect(erros).toEqual([]);
});

/* a campanha dos pets v6: seis ilhas, celular (360, 390) e desktop (1280), claro e escuro */
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`arenas: campanha com 6 ilhas em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVE_ARENAS, undefined, TAMER_3);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/lutar/campanha");
    await expect(page.locator(".mapa-ilhas img.ilha")).toHaveCount(6);
    await expect(page.locator(".mapa-ilhas .lugar")).toHaveCount(6);
    await expect(page.locator(".camp-arena")).toBeVisible();
    await page.waitForTimeout(600);
    const r = await page.evaluate(desk => {
      const mapa = document.querySelector(".mapa-ilhas")!.getBoundingClientRect();
      const caixas = [...document.querySelectorAll(".mapa-ilhas .lugar")].map(e => e.getBoundingClientRect());
      const ilhas = [...document.querySelectorAll(".mapa-ilhas img.ilha")].map(e => e.getBoundingClientRect());
      const sobrepoe = caixas.some((a, i) => caixas.some((b, j) => j > i && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom));
      const fora = ilhas.filter(b => b.left < mapa.left - 1 || b.right > mapa.right + 1 || b.top < mapa.top - 1 || b.bottom > mapa.bottom + 1).length;
      /* no celular o cartao do lugar sobe sobre o pe do mapa: nenhuma plaquinha pode ficar embaixo dele */
      const det = document.querySelector(".camp-det"), limite = det ? Math.min(mapa.bottom, det.getBoundingClientRect().top) : mapa.bottom;
      const placasFora = caixas.filter(b => b.left < mapa.left - 1 || b.right > mapa.right + 1 || b.bottom > limite + 1).length;
      const visivel = (e: Element) => (e as HTMLElement).offsetParent !== null;
      const pequenos = [...document.querySelector(desk ? ".camp-tela" : "body")!.querySelectorAll("button, select, input, summary, a")].filter(visivel).flatMap(e => {
        const b = e.getBoundingClientRect();
        return b.height < 44 || b.width < 44 ? [`${e.tagName}.${(e as HTMLElement).className} ${Math.round(b.width)}x${Math.round(b.height)}`] : [];
      });
      const nomes = [...document.querySelectorAll(".mapa-ilhas .lugar-placa")].map(e => e.textContent);
      return { larg: document.documentElement.scrollWidth, janela: innerWidth, sobrepoe, fora, placasFora, pequenos, nomes, alt: mapa.height, largMapa: mapa.width };
    }, largura >= 1100);
    expect(r.nomes).toEqual(["Campina", "Torre de pedra", "Floresta", "Cidadela", "Lago", "Montanha Espiral"]);
    expect(r.larg, "rolagem lateral").toBeLessThanOrEqual(r.janela);
    expect(r.sobrepoe, "plaquinhas dos lugares sobrepostas").toBe(false);
    expect(r.fora, "ilhas fora do mapa").toBe(0);
    expect(r.placasFora, "plaquinhas fora do mapa").toBe(0);
    expect(r.pequenos, "alvos menores que 44 px").toEqual([]);
    expect(r.alt / r.largMapa, "o mapa das seis ilhas e mais alto que largo").toBeGreaterThan(1.3);
    await expect(page.locator(".camp-arena")).toContainText("líder: Myotismon");
    expect(erros).toEqual([]);
  });
}

/* ---------------------------------------------------------------- itens do Tamer (medalhas parte 3, docs/DESIGN_MEDALHAS_ARENAS.md
   secao 13): o lider da o item com a medalha; o chip se equipa em Crescer · Itens e vale na luta; a carta se escolhe antes da luta */
const numTamer = (page: Page, tipo: string) => page.evaluate(([c, t]) => JSON.parse(localStorage.getItem(c + "-tamer")!).log.filter((e: unknown[]) => e[0] === t).length, [CHAVE, tipo] as const);
/** vai para a aba pela barra e pelas abas (dentro do app, sem recarregar) */
async function irPara(page: Page, destino: string, aba: string, rota: string): Promise<void> {
  await page.locator(".dl-nav").getByRole("button", { name: destino, exact: true }).click();
  await page.getByRole("tab", { name: aba }).click();
  await expect(page).toHaveURL(new RegExp("#/" + rota + "$"));
}

test("itens: o líder dá o chip com a medalha, o chip se equipa e vale na luta", async ({ page }) => {
  test.setTimeout(180_000);
  await semear(page, SAVE_V6);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/campanha");
  await page.locator(".camp-lutar:not([disabled])").click();
  const res = page.locator("dialog.modal-res[open]");
  await expect(res).toBeVisible({ timeout: 90_000 });
  await expect(res.locator(".res-medalha")).toContainText("Medalha da Campina");
  await expect(res.locator(".res-item")).toContainText("Chip de Força");
  await expect(res.locator(".res-item")).toContainText("item novo");
  await page.locator(".res-continuar").click();
  /* o pet evoluiu no tick da medalha: a revelacao abre depois do Resultado */
  const rev = page.locator("dialog.revelacao[open]");
  await expect(rev).toBeVisible();
  await rev.getByRole("button", { name: "Continuar" }).click();
  await expect(page).toHaveURL(/#\/crescer\/evolucao$/);
  /* Crescer · Itens: o chip e do Tamer, e o Champion tem 1 vaga (1 medalha) */
  await page.getByRole("tab", { name: "Itens" }).click();
  await expect(page.locator(".itens-vagas")).toContainText("0 de 1 vaga");
  const chip = page.locator(".item-card", { hasText: "Chip de Força" });
  await expect(chip).not.toHaveClass(/item-falta/);
  await expect(page.locator(".item-card", { hasText: "Chip Aparo" })).toContainText("Ainda não é seu: vença o Piedmon");
  const i0 = await numLog(page, "i");
  await chip.getByRole("button", { name: "Equipar" }).click();
  await expect(chip).toHaveClass(/item-eq/);
  await expect(chip).toContainText("Agora soma +1 de vigor, +1 de força");
  await expect(page.locator(".itens-vagas")).toContainText("1 de 1 vaga");
  expect(await numLog(page, "i")).toBe(i0 + 1);
  /* sem vaga: o outro chip do Tamer (se houvesse) nao entraria; lutar com o chip na arena */
  const l0 = await numLog(page, "l");
  await irPara(page, "Lutar", "Arena", "lutar/arena");
  await page.locator(".lutar-grande").click();
  await expect(res).toBeVisible({ timeout: 90_000 });
  await page.locator(".res-continuar").click();
  expect(await numLog(page, "l")).toBe(l0 + 1);
  const reg = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro()));
  const eventos = reg.log.map((e: unknown[]) => e[1]);
  expect(eventos.lastIndexOf("i")).toBeLessThan(eventos.lastIndexOf("l"));
  expect(reg.log.find((e: unknown[]) => e[1] === "i")[2]).toEqual({ op: "equipar", id: "chip_forca" });
  /* desequipar volta a vaga */
  await irPara(page, "Crescer", "Itens", "crescer/itens");
  await page.locator(".item-card", { hasText: "Chip de Força" }).getByRole("button", { name: "Desequipar" }).click();
  await expect(page.locator(".itens-vagas")).toContainText("0 de 1 vaga");
  expect(erros).toEqual([]);
});

/* Tamer com a medalha da Campina, o item dela e uma Carta de Folego da revanche (um Rookie de antes a ganhou) */
const TAMER_ITENS = { versao: 2, log: [
  ["medalha", { id: "campina", n: 1, quando: 1, pet: SAVE_V6.semente, forma: "Armadillomon", tick: 900 }],
  ["item", { id: "chip_forca", n: 1, quando: 1, origem: "medalha", lider: "npc_tier1_brutamontes", pet: SAVE_V6.semente, forma: "Armadillomon", est: "crianca", tick: 900 }],
  ["item", { id: "carta_folego", n: 2, quando: 2, origem: "revanche", lider: "npc_tier1_brutamontes", pet: 1, forma: "Armadillomon", est: "crianca", tick: 900 }],
] };

test("itens: a carta se escolhe antes da luta, entra no registro do pet e sai do inventário do Tamer", async ({ page }) => {
  test.setTimeout(180_000);
  await semear(page, SAVE_V6, undefined, TAMER_ITENS);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/campanha");
  const escolha = page.locator(".carta-escolha select");
  await expect(escolha).toBeVisible();
  await escolha.selectOption("carta_folego");
  await expect(page.locator(".carta-escolha")).toContainText("+20 de guts");
  await page.locator(".camp-lutar:not([disabled])").click();
  const res = page.locator("dialog.modal-res[open]");
  await expect(res).toBeVisible({ timeout: 90_000 });
  await expect(res.locator(".res-carta")).toContainText("Carta usada: Carta de Fôlego");
  await page.locator(".res-continuar").click();
  const reg = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro()));
  const k = reg.log.findIndex((e: unknown[]) => e[1] === "k");
  expect(reg.log[k][2]).toEqual({ id: "carta_folego" });
  expect(reg.log[k + 1][1]).toBe("l");
  expect(await numTamer(page, "carta_usada")).toBe(1);
  /* acabou a carta: a escolha some */
  await expect(page).toHaveURL(/#\/lutar\/campanha$/);
  await expect(page.locator(".carta-escolha")).toHaveCount(0);
  await irPara(page, "Crescer", "Itens", "crescer/itens");
  await expect(page.locator(".item-card", { hasText: "Carta de Fôlego" })).toContainText("×0");
  expect(erros).toEqual([]);
});

/* a tela dos itens: celular (360, 390) e desktop (1280), claro e escuro */
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`itens: tela em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVE_V6, undefined, TAMER_ITENS);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/crescer/itens");
    await expect(page.locator(".item-card")).toHaveCount(9);
    await expect(page.locator(".item-card.item-falta")).toHaveCount(7);
    await page.locator(".item-card", { hasText: "Chip de Força" }).getByRole("button", { name: "Equipar" }).click();
    await expect(page.locator(".item-card.item-eq")).toHaveCount(1);
    await page.waitForTimeout(600);
    const r = await page.evaluate(desk => {
      const visivel = (e: Element) => (e as HTMLElement).offsetParent !== null;
      const pequenos = [...document.querySelector(desk ? ".itens-tela" : "body")!.querySelectorAll("button, select, input, summary, a")].filter(visivel).flatMap(e => {
        const b = e.getBoundingClientRect();
        return b.height < 44 || b.width < 44 ? [`${e.tagName}.${(e as HTMLElement).className} ${Math.round(b.width)}x${Math.round(b.height)}`] : [];
      });
      const lista = document.querySelector(".itens-col")!.getBoundingClientRect(), resumo = document.querySelector(".itens-resumo")!.getBoundingClientRect();
      return { larg: document.documentElement.scrollWidth, janela: innerWidth, pequenos, aoLado: lista.left >= resumo.right - 1 };
    }, largura >= 1100);
    expect(r.larg, "rolagem lateral").toBeLessThanOrEqual(r.janela);
    expect(r.pequenos, "alvos menores que 44 px").toEqual([]);
    expect(r.aoLado, "desktop: os itens ao lado do resumo").toBe(largura >= 1100);
    /* a escolha da carta na campanha, no mesmo tamanho */
    await irPara(page, "Lutar", "Campanha", "lutar/campanha");
    await expect(page.locator(".carta-escolha select")).toBeVisible();
    const c = await page.evaluate(() => ({ larg: document.documentElement.scrollWidth, janela: innerWidth, alt: document.querySelector(".carta-escolha select")!.getBoundingClientRect().height }));
    expect(c.larg).toBeLessThanOrEqual(c.janela);
    expect(c.alt).toBeGreaterThanOrEqual(44);
    expect(erros).toEqual([]);
  });
}
