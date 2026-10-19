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
  ["Lutar", "Arena", "lutar/arena"], ["Lutar", "Campanha", "lutar/campanha"], ["Lutar", "Fronteira", "lutar/fronteira"], ["Lutar", "Medalhas", "lutar/medalhas"], ["Diário", "Registro", "diario/registro"], ["Diário", "Catálogo", "diario/catalogo"],
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

/* o relogio do jogo para durante a luta no palco e com o Resultado aberto (so a interface: a luta ja entrou no registro na hora);
   fechado o Resultado, volta a andar. Na velocidade alta (1 h por segundo) 1,5 s parado seriam 90 min de jogo */
test("tempo: o relógio para durante a animação da luta e com o Resultado aberto, e volta a andar depois", async ({ page }) => {
  test.setTimeout(120_000);
  await semear(page, SAVES.v3);
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
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
  /* a luta ja esta no registro, antes da animacao */
  expect(await numLog(page, "l")).toBe(l0 + 1);
  /* durante a animacao: o tick nao muda */
  const t1 = await tick();
  await page.waitForTimeout(1500);
  expect(await tick(), "o tempo andou durante a animação da luta").toBe(t1);
  /* com o Resultado aberto: tambem nao */
  const res = page.locator("dialog.modal-res[open]");
  await expect(res).toBeVisible({ timeout: 90_000 });
  const t2 = await tick();
  expect(t2).toBe(t1);
  await page.waitForTimeout(1500);
  expect(await tick(), "o tempo andou com o Resultado aberto").toBe(t2);
  /* fechou o Resultado: volta a andar, sem compensar o tempo parado (1 h/s: menos de 3 h de jogo nos proximos 2 s) */
  await page.locator(".res-continuar").click();
  await expect(page).toHaveURL(/#\/lutar\/arena$/);
  await expect.poll(tick).toBeGreaterThan(t2);
  const t3 = await tick();
  expect(t3 - t2, "o tempo parado nao volta de uma vez").toBeLessThan(180);
  /* o registro so ganhou a luta (e os avancos de tempo de depois): nenhum evento novo da interface */
  expect(await numLog(page, "l")).toBe(l0 + 1);
  expect(erros).toEqual([]);
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
  expect(r.save.versao).toBe(11);                    /* o ovo novo nasce na versao atual (v11: o cerebro A e o corpo) */
  expect(r.g).toBe("[]");
  expect(r.aviso).toBeNull();
  expect(r.tamer).toEqual({ versao: 6, log: [] });
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
  expect(r.save.versao).toBe(11);                    /* o ovo novo nasce na versao atual (v11) */
  expect(r.save.semente).not.toBe(SAVE_V6.semente);
  expect(r.marca).toBe("5");
  expect(r.tamer).toEqual({ versao: 6, log: [] });
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
  await expect(page.locator(".mapa-ilhas img.ilha")).toHaveCount(7);
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

/* a campanha dos pets v6: seis ilhas e a Fronteira no alto (trancada com 3 medalhas), celular (360, 390) e desktop (1280), claro e escuro */
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`arenas: campanha com 6 ilhas e a Fronteira em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVE_ARENAS, undefined, TAMER_3);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/lutar/campanha");
    await expect(page.locator(".mapa-ilhas img.ilha")).toHaveCount(7);
    await expect(page.locator(".mapa-ilhas .lugar")).toHaveCount(7);
    await expect(page.locator(".mapa-ilhas .lugar--fronteira")).toContainText("6 medalhas");
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
    expect(r.nomes).toEqual(["Campina", "Torre de pedra", "Floresta", "Cidadela", "Lago", "Montanha Espiral", "Fronteira"]);
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

/* ---------------------------------------------------------------- a Fronteira de Batalha: a Liga dos Lideres e o fim do jogo (medalhas
   parte 4a, docs/DESIGN_FRONTEIRA.md). save_liga.json (e2e/gerar_save_liga.mjs): pet v6 Mega treinado ate o teto que conhece as 6
   medalhas; a tentativa do botao Desafiar a Liga vence as 6 lutas em qualquer hora das proximas 5 h de jogo. O Tamer do teste tem as 6 */
const SAVE_LIGA = JSON.parse(readFileSync(new URL("./save_liga.json", import.meta.url), "utf8"));
const TAMER_6 = { versao: 2, log: ["campina", "torre", "floresta", "cidadela", "lago", "espiral"].map((id, i) =>
  ["medalha", { id, n: i + 1, quando: 1 + i, pet: 1, forma: "Valkyrimon", tick: 900 + i }]) };

test("fronteira: com as 6 medalhas a ilha abre; a Liga tem 6 lutas sem cura, dá o título ao Tamer, a medalha de ouro e a conclusão", async ({ page }) => {
  test.setTimeout(240_000);
  await semear(page, SAVE_LIGA, undefined, TAMER_6);
  const erros = vigiarErros(page);
  /* a ilha no alto do mapa, aberta, leva a Lutar · Fronteira */
  await page.goto(APP + "#/lutar/campanha");
  const ilha = page.locator(".mapa-ilhas .lugar--fronteira");
  await expect(ilha).toContainText("LIGA");
  await ilha.click();
  await expect(page).toHaveURL(/#\/lutar\/fronteira$/);
  await expect(page.locator(".fr-card")).toHaveCount(6);
  await expect(page.locator(".fr-card").first()).toContainText("Gazimon");
  await expect(page.locator(".fr-card").first()).toContainText("WarGreymon");
  await expect(page.locator(".fr-card").last()).toContainText("Imperialdramon Dragon Mode");
  await expect(page.locator(".fr-regras")).toContainText("cartas não valem");
  /* sem escolha de carta na Liga */
  await expect(page.locator(".carta-escolha")).toHaveCount(0);
  const lutar = page.locator(".fr-lutar:not([disabled])");
  await expect(lutar).toContainText("Desafiar a Liga (6 lutas seguidas)");
  const l0 = await numLog(page, "l");
  await lutar.click();
  await expect(page.locator(".luta-topo-sub")).toContainText("luta 1 de 6");
  await expect(page.locator(".luta-liga")).toContainText("Liga dos Líderes · luta 1 de 6");
  await expect(page.locator(".luta-liga")).toContainText("as cartas não valem");
  await page.locator(".luta-ctl--x2").click();
  await expect(page.locator(".luta-liga")).toContainText("luta 2 de 6", { timeout: 90_000 });
  const res = page.locator("dialog.modal-res[open]");
  await expect(res).toBeVisible({ timeout: 200_000 });
  await expect(res.locator(".res-tit")).toHaveText("Campeão!");
  await expect(res.locator(".res-serie li")).toHaveCount(6);
  await expect(res.locator(".res-serie")).not.toContainText("perdeu");
  await expect(res.locator(".res-serie")).toContainText("Seraphimon");
  await expect(res.locator(".res-titulo")).toContainText("Campeão da Liga dos Líderes");
  await page.locator(".res-continuar").click();
  /* uma luta so no registro do pet: a tentativa inteira, {r, s} */
  expect(await numLog(page, "l")).toBe(l0 + 1);
  const reg = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro()));
  const lutas = reg.log.filter((e: unknown[]) => e[1] === "l");
  expect(lutas[lutas.length - 1][2]).toEqual({ r: "liga", s: expect.any(Number) });
  /* o titulo no Tamer, com o pet e a forma */
  const t = await lerTamer(page);
  expect(t.versao).toBe(6);
  const c = t.log.filter((e: [string]) => e[0] === "campeao");
  expect(c).toHaveLength(1);
  expect(c[0][1]).toMatchObject({ n: 1, pet: SAVE_LIGA.semente, forma: "Valkyrimon" });
  /* a conclusao da jornada vem da Liga */
  const cc = page.locator("dialog.conclusao-tela[open]");
  await expect(cc).toBeVisible();
  await expect(cc.locator("#cc-tit")).toHaveText("Campeão!");
  await expect(cc).toContainText("venceu os 6 líderes da Liga");
  await expect(cc.locator(".cc-marcos li.feito", { hasText: "Venceu a Liga dos Líderes" })).toHaveCount(1);
  await cc.getByRole("button", { name: /Continuar com/ }).click();
  await expect(cc).toHaveCount(0);
  /* a tela da Liga com a ultima tentativa e o titulo; a medalha de ouro em Medalhas */
  await expect(page).toHaveURL(/#\/lutar\/fronteira$/);
  await expect(page.locator(".fr-titulo")).toContainText("Campeão da Liga");
  await expect(page.locator(".fr-ultima")).toContainText("venceu os 6");
  await expect(page.locator(".fr-card--vit")).toHaveCount(6);
  await irPara(page, "Lutar", "Medalhas", "lutar/medalhas");
  await expect(page.locator(".med-ouro.ganha")).toContainText("Campeão da Liga dos Líderes com Valkyrimon");
  /* recarregar: a conclusao nao volta */
  await page.reload();
  await expect(page.locator(".med-tela")).toBeVisible();
  await page.waitForTimeout(800);
  await expect(page.locator("dialog.conclusao-tela")).toHaveCount(0);
  expect(erros).toEqual([]);
});

test("fronteira: sem as 6 medalhas a Liga fica trancada e diz o que falta", async ({ page }) => {
  await semear(page, SAVE_ARENAS, undefined, TAMER_3);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/fronteira");
  await expect(page.locator(".fr-card")).toHaveCount(6);
  await expect(page.locator(".fr-lutar")).toBeDisabled();
  await expect(page.locator(".fr-cab .med-espera")).toContainText("A Fronteira abre com as 6 medalhas.");
  await expect(page.locator(".fr-cab .med-espera")).toContainText("Faltam 3 medalhas");
  await irPara(page, "Lutar", "Medalhas", "lutar/medalhas");
  await expect(page.locator(".med-ouro")).not.toHaveClass(/ganha/);
  await expect(page.locator(".med-ouro")).toContainText("Ainda não");
  expect(erros).toEqual([]);
});

/* a tela da Liga: celular (360, 390) e desktop (1280), claro e escuro */
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`fronteira: tela da Liga em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVE_LIGA, undefined, TAMER_6);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/lutar/fronteira");
    await expect(page.locator(".fr-card")).toHaveCount(6);
    await page.waitForTimeout(600);
    const r = await page.evaluate(desk => {
      const visivel = (e: Element) => (e as HTMLElement).offsetParent !== null;
      const pequenos = [...document.querySelector(desk ? ".fr-tela" : "body")!.querySelectorAll("button, select, input, summary, a")].filter(visivel).flatMap(e => {
        const b = e.getBoundingClientRect();
        return b.height < 44 || b.width < 44 ? [`${e.tagName}.${(e as HTMLElement).className} ${Math.round(b.width)}x${Math.round(b.height)}`] : [];
      });
      const lista = document.querySelector(".fr-lista")!.getBoundingClientRect(), cab = document.querySelector(".fr-cab")!.getBoundingClientRect();
      return { larg: document.documentElement.scrollWidth, janela: innerWidth, pequenos, aoLado: lista.left >= cab.right - 1 };
    }, largura >= 1100);
    expect(r.larg, "rolagem lateral").toBeLessThanOrEqual(r.janela);
    expect(r.pequenos, "alvos menores que 44 px").toEqual([]);
    expect(r.aoLado, "desktop: os lideres ao lado das regras").toBe(largura >= 1100);
    /* a medalha de ouro apagada em Medalhas, no mesmo tamanho */
    await irPara(page, "Lutar", "Medalhas", "lutar/medalhas");
    await expect(page.locator(".med-ouro")).toBeVisible();
    const m = await page.evaluate(() => ({ larg: document.documentElement.scrollWidth, janela: innerWidth }));
    expect(m.larg).toBeLessThanOrEqual(m.janela);
    expect(erros).toEqual([]);
  });
}

/* ---------------------------------------------------------------- as instalacoes da Fronteira: a Torre de Batalha e o Palacio (medalhas
   parte 4b, docs/DESIGN_FRONTEIRA.md). O save preparado e o da Liga (e2e/save_liga.json) com um Tamer que ja tem o titulo (de outro pet):
   na abertura o app grava no registro do pet o evento "f" (as instalacoes abrem). A semente da tentativa sai do registro do pet (a primeira
   tentativa de cada instalacao), entao o resultado e fixo: na Torre 7 vitorias seguidas (8 lutas), no Palacio 9 (conferido com o motor em
   qualquer hora das proximas 5 h de jogo) */
const TAMER_CAMPEAO = { versao: 3, log: [...TAMER_6.log, ["campeao", { n: 1, quando: 10, pet: 1, forma: "WarGreymon", tick: 950 }]] };
const TAMER_RECORDE = { versao: 4, log: [...TAMER_CAMPEAO.log, ["recorde", { inst: "torre_batalha", valor: 4, quando: 11, pet: 1, forma: "WarGreymon", tick: 960 }]] };

test("fronteira: antes do título as instalações ficam trancadas", async ({ page }) => {
  await semear(page, SAVE_LIGA, undefined, TAMER_6);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/fronteira");
  /* as quatro instalacoes (4b e 4c), todas trancadas */
  await expect(page.locator(".fr-inst-card")).toHaveCount(4);
  await expect(page.locator(".fr-inst-card").first()).toContainText("Torre de Batalha");
  await expect(page.locator(".fr-inst-card").nth(1)).toContainText("Palácio");
  await expect(page.locator(".fr-inst-card").nth(2)).toContainText("Fábrica");
  await expect(page.locator(".fr-inst-card").nth(3)).toContainText("Salão");
  for (const c of await page.locator(".fr-inst-card").all()) await expect(c).toContainText("Abre depois do título da Liga dos Líderes.");
  await expect(page.locator(".fr-inst-tentar")).toHaveCount(4);
  for (const b of await page.locator(".fr-inst-tentar").all()) await expect(b).toBeDisabled();
  await expect(page.locator(".sl-niveis")).toHaveCount(0);
  expect(await numLog(page, "f")).toBe(0);
  await irPara(page, "Lutar", "Medalhas", "lutar/medalhas");
  await expect(page.locator(".med-recordes li")).toHaveCount(4);
  await expect(page.locator(".med-recordes")).toContainText("Abre depois do título");
  expect(erros).toEqual([]);
});

test("fronteira: com o título, a Torre de Batalha dá 7 vitórias seguidas sem cura e o recorde; o Palácio sem as travas", async ({ page }) => {
  test.setTimeout(240_000);
  await semear(page, SAVE_LIGA, undefined, TAMER_CAMPEAO);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/fronteira");
  /* o pet passou a saber do titulo do Tamer: o evento "f" no registro dele */
  await expect(page.locator(".fr-inst-card")).toHaveCount(4);
  expect(await numLog(page, "f")).toBe(1);
  /* sem pausar o tempo: a derrota que fecha a sequencia pode machucar o pet, e na velocidade de teste (10 min por segundo) a lesao sem
     tratar o mataria em 36 s; o relogio do jogo fica parado durante a animacao e com o Resultado aberto (luta.lutaSeguraTempo), entao a
     pausa manual que este teste fazia nao e mais necessaria */
  const torre =page.locator(".fr-inst-card", { hasText: "Torre de Batalha" });
  await expect(torre).toContainText("Megas sorteados");
  await expect(torre).toContainText("Sem recorde ainda");
  const l0 = await numLog(page, "l");
  await torre.locator(".fr-inst-tentar:not([disabled])").click();
  await expect(page.locator(".luta-inst")).toContainText("Torre de Batalha · vitória 1");
  await expect(page.locator(".luta-topo-sub")).toContainText("vitória 1");
  await page.locator(".luta-ctl--x2").click();
  await expect(page.locator(".luta-inst")).toContainText("vitória 2", { timeout: 90_000 });
  await expect(page.locator(".luta-inst")).toContainText("sem cura, seu pet começou esta luta com");
  const res = page.locator("dialog.modal-res[open]");
  await expect(res).toBeVisible({ timeout: 200_000 });
  await expect(res.locator(".res-tag")).toHaveText("Fronteira · Torre de Batalha");
  await expect(res.locator(".res-tit")).toHaveText("Recorde!");
  await expect(res.locator(".res-sub")).toContainText("7 vitórias seguidas; parou na luta 8");
  await expect(res.locator(".res-serie li")).toHaveCount(8);
  await expect(res.locator(".res-recorde")).toContainText("7 vitórias seguidas");
  await page.locator(".res-continuar").click();
  /* uma luta so no registro do pet: a tentativa inteira, {r, s}; o recorde no Tamer */
  expect(await numLog(page, "l")).toBe(l0 + 1);
  const reg = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro()));
  const lutas = reg.log.filter((e: unknown[]) => e[1] === "l");
  expect(lutas[lutas.length - 1][2]).toEqual({ r: "torre_batalha", s: expect.any(Number) });
  let t = await lerTamer(page);
  expect(t.versao).toBe(6);
  expect(t.log.filter((e: [string]) => e[0] === "recorde")).toEqual([["recorde", expect.objectContaining({ inst: "torre_batalha", valor: 7, pet: SAVE_LIGA.semente, forma: "Valkyrimon" })]]);
  await expect(page).toHaveURL(/#\/lutar\/fronteira$/);
  await expect(torre.locator(".fr-inst-rec .dl-num")).toHaveText("7");
  await expect(torre).toContainText("Este pet: 1 tentativa, melhor 7, última 7");
  /* o Palacio: o aviso de que o pet decide sozinho; a animacao pulada (a tentativa ja foi decidida e gravada) */
  const palacio = page.locator(".fr-inst-card", { hasText: "Palácio" });
  await palacio.locator(".fr-inst-tentar:not([disabled])").click();
  await expect(page.locator(".luta-inst")).toContainText("Palácio · vitória 1");
  await expect(page.locator(".luta-inst")).toContainText("travas, vetos e chips de regra não valem");
  await page.locator(".luta-desistir").click();
  await page.locator("dialog.modal-conf[open]").getByRole("button", { name: "Desistir" }).click();
  await expect(page).toHaveURL(/#\/lutar\/fronteira$/);
  await expect(palacio.locator(".fr-inst-rec .dl-num")).toHaveText("9");
  t = await lerTamer(page);
  expect(t.log.filter((e: [string]) => e[0] === "recorde").map((e: [string, { inst: string; valor: number }]) => [e[1].inst, e[1].valor])).toEqual([["torre_batalha", 7], ["palacio", 9]]);
  /* os recordes na tela de Medalhas */
  await irPara(page, "Lutar", "Medalhas", "lutar/medalhas");
  await expect(page.locator(".med-recordes li.ganha")).toHaveCount(2);
  await expect(page.locator(".med-recordes li", { hasText: "Torre de Batalha" })).toContainText("7 vitórias seguidas, com Valkyrimon");
  await expect(page.locator(".med-recordes li", { hasText: "Palácio" })).toContainText("9 vitórias seguidas");
  expect(erros).toEqual([]);
});

/* a tela das instalacoes, com o titulo e um recorde: celular (360, 390) e desktop (1280), claro e escuro */
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`fronteira: instalações em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVE_LIGA, undefined, TAMER_RECORDE);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/lutar/fronteira");
    await expect(page.locator(".fr-inst-card")).toHaveCount(4);
    await expect(page.locator(".fr-inst-card").first().locator(".fr-inst-rec .dl-num")).toHaveText("4");
    await expect(page.locator(".fr-inst-card").first()).toContainText("Recorde do Tamer: 4 vitórias seguidas, com WarGreymon");
    await page.waitForTimeout(600);
    const r = await page.evaluate(desk => {
      const visivel = (e: Element) => (e as HTMLElement).offsetParent !== null;
      const pequenos = [...document.querySelector(desk ? ".fr-tela" : "body")!.querySelectorAll("button, select, input, summary, a")].filter(visivel).flatMap(e => {
        const b = e.getBoundingClientRect();
        return b.height < 44 || b.width < 44 ? [`${e.tagName}.${(e as HTMLElement).className} ${Math.round(b.width)}x${Math.round(b.height)}`] : [];
      });
      const lista = document.querySelector(".fr-lista")!.getBoundingClientRect(), inst = document.querySelector(".fr-inst")!.getBoundingClientRect();
      return { larg: document.documentElement.scrollWidth, janela: innerWidth, pequenos, aoLado: lista.left >= inst.right - 1 };
    }, largura >= 1100);
    expect(r.larg, "rolagem lateral").toBeLessThanOrEqual(r.janela);
    expect(r.pequenos, "alvos menores que 44 px").toEqual([]);
    expect(r.aoLado, "desktop: as instalações na coluna da Liga, ao lado dos líderes").toBe(largura >= 1100);
    await page.screenshot({ path: `test-results/fronteira-instalacoes-${largura}-${tema}.png`, fullPage: true });
    await irPara(page, "Lutar", "Medalhas", "lutar/medalhas");
    await expect(page.locator(".med-recordes li.ganha")).toHaveCount(1);
    const m = await page.evaluate(() => ({ larg: document.documentElement.scrollWidth, janela: innerWidth }));
    expect(m.larg).toBeLessThanOrEqual(m.janela);
    await page.screenshot({ path: `test-results/fronteira-medalhas-${largura}-${tema}.png`, fullPage: true });
    expect(erros).toEqual([]);
  });
}

/* ---------------------------------------------------------------- a Fabrica e o Salao da Fronteira (medalhas parte 4c,
   docs/DESIGN_FRONTEIRA.md). A Fabrica nao usa pet: a tentativa 1 do Tamer (semente do numero da tentativa) oferece Sakuyamon (muralha),
   HerculesKabuterimon (vigia) e Imperialdramon Dragon Mode (duelista); com a Sakuyamon a luta 1 e vitoria contra Imperialdramon Fighter Mode
   e, trocando por ele, a luta 2 e derrota (conferido com o motor; a Fabrica nao depende da hora nem do pet). O Salao: o Mega do teste da Liga
   (o ativo) e os guardados de e2e/save_salao.json (e2e/gerar_save_salao.mjs: um Rookie, um Champion e um Ultimate), que vencem a primeira
   luta de cada um la (os guardados nao andam no tempo; o Mega vence em qualquer hora das proximas 5 h) */
const SALAO = JSON.parse(readFileSync(new URL("./save_salao.json", import.meta.url), "utf8")) as { guardados: { semente: number; log: unknown[]; versao: number }[] };
/** o Tamer campeao e os pets guardados do Salao (a semeadura de sempre deixa os guardados vazios) */
async function semearSalao(page: Page, tamer: object = TAMER_CAMPEAO): Promise<void> {
  await semear(page, SAVE_LIGA, undefined, tamer);
  await page.evaluate(([c, g]) => localStorage.setItem(c + "-guardados", g), [CHAVE, JSON.stringify(SALAO.guardados)] as const);
}
const lerGuardadosE2e = (page: Page) => page.evaluate(c => JSON.parse(localStorage.getItem(c + "-guardados") ?? "[]"), CHAVE);

test("fronteira: a Fábrica aluga 1 de 3 Megas, luta, oferece a troca depois da vitória e grava tudo só no Tamer", async ({ page }) => {
  await semear(page, SAVE_LIGA, undefined, TAMER_CAMPEAO);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/fronteira");
  const fab = page.locator(".fb-card");
  await expect(fab).toContainText("Você não usa o seu pet");
  await expect(fab).toContainText("Sem recorde ainda");
  const l0 = await numLog(page, "l");
  await fab.locator(".fr-inst-tentar:not([disabled])").click();
  /* a escolha: os 3 alugados, com o Digimon, o arquetipo e o nivel */
  const alug = fab.locator(".fb-aluguel");
  await expect(alug).toHaveCount(3);
  await expect(alug.nth(0)).toContainText("Sakuyamon");
  await expect(alug.nth(0)).toContainText("Muralha");
  await expect(alug.nth(0)).toContainText("Mega");
  await expect(alug.nth(1)).toContainText("HerculesKabuterimon");
  await expect(alug.nth(2)).toContainText("Imperialdramon Dragon Mode");
  await alug.nth(0).click();
  await expect(fab.locator(".fb-status")).toContainText("Tentativa 1 · série 1, luta 1 de 3 · 0 séries vencidas");
  await expect(fab.locator(".fb-alugado")).toContainText("Sakuyamon");
  await fab.locator(".fb-lutar").click();
  await expect(fab.locator(".fb-ultima")).toContainText("Luta 1: venceu Imperialdramon Fighter Mode (Duelista)");
  /* a oferta de troca depois da vitoria; trocando, o alugado passa a ser o rival derrotado, que entra com a vida cheia (as regras dos v9,
     fase 3 do equilibrio geral: a tentativa nova grava a versao das regras no registro do Tamer) */
  await expect(fab.locator(".fb-troca")).toContainText("entra com a vida cheia");
  await fab.locator(".fb-trocar").click();
  await expect(fab.locator(".fb-troca")).toHaveCount(0);
  await expect(fab.locator(".fb-alugado")).toContainText("Imperialdramon Fighter Mode");
  await expect(fab.locator(".fb-status")).toContainText("série 1, luta 2 de 3");
  await fab.locator(".fb-lutar").click();
  await expect(fab.locator(".fb-ultima")).toContainText("Luta 2: venceu SlashAngemon (Espelho)");
  await expect(fab.locator(".fb-status")).toContainText("série 1, luta 3 de 3");
  await fab.locator(".fb-lutar").click();
  /* perdeu, acabou: o resumo e "Tentar de novo" */
  await expect(fab.locator(".fb-ultima")).toContainText("Última tentativa: 0 séries vencidas; perdeu para");
  await expect(fab.locator(".fb-ultima")).toContainText("na série 1, luta 3");
  await expect(fab.locator(".fr-inst-tentar")).toHaveText("Tentar de novo");
  await expect(fab.locator(".fb-lutas li")).toHaveCount(3);
  /* so no registro do Tamer (versao 6, a tentativa com as regras dos v9): o comeco, as tres lutas e a troca; nenhuma luta no registro do pet */
  const t = await lerTamer(page);
  expect(t.versao).toBe(6);
  expect(t.log.find((e: [string]) => e[0] === "fabrica")[1].v).toBe(9);
  expect(t.log.filter((e: [string]) => e[0].startsWith("fabrica")).map((e: [string, { n: number; k?: number; alugado?: number }]) => [e[0], e[1].n, e[1].k ?? e[1].alugado]))
    .toEqual([["fabrica", 1, 0], ["fabrica_luta", 1, 0], ["fabrica_troca", 1, 0], ["fabrica_luta", 1, 1], ["fabrica_luta", 1, 2]]);
  expect(await numLog(page, "l")).toBe(l0);
  /* a proxima tentativa oferece outros alugados (a semente da tentativa 2) */
  await fab.locator(".fr-inst-tentar").click();
  await expect(fab.locator(".fb-aluguel")).toHaveCount(3);
  await expect(fab.locator(".fb-status")).toContainText("Tentativa 2");
  await fab.locator(".fb-voltar").click();
  await irPara(page, "Lutar", "Medalhas", "lutar/medalhas");
  await expect(page.locator(".med-recordes li", { hasText: "Fábrica" })).toContainText("Nenhum ainda");
  expect(erros).toEqual([]);
});

test("fronteira: o Salão, com um pet de cada nível (o ativo e os guardados), grava a luta no registro de cada um e o recorde no Tamer", async ({ page }) => {
  await semearSalao(page);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/fronteira");
  const sl = page.locator(".sl-card");
  await expect(sl).toContainText("Um pet seu de cada nível");
  const sels = sl.locator(".sl-sel");
  await expect(sels).toHaveCount(4);
  await expect(sl.locator(".sl-niveis li").nth(0)).toContainText("Rookie");
  await expect(sels.nth(0).locator("option:checked")).toHaveText("Patamon (guardado)");
  await expect(sels.nth(1).locator("option:checked")).toHaveText("Growlmon (guardado)");
  await expect(sels.nth(2).locator("option:checked")).toHaveText("MegaSeadramon (guardado)");
  await expect(sels.nth(3).locator("option:checked")).toHaveText("Valkyrimon (ativo)");
  await expect(sl.locator(".med-espera")).toHaveCount(0);
  const l0 = await numLog(page, "l"), g0 = (await lerGuardadosE2e(page)).map((g: { log: unknown[] }) => g.log.length);
  await sl.locator(".fr-inst-tentar:not([disabled])").click();
  await expect(sl.locator("p[role=status]", { hasText: "Venceu os 4 níveis!" })).toBeVisible();
  await expect(sl.locator(".fr-inst-rec .dl-num")).toHaveText("4");
  await expect(sl.locator(".sl-ultima li.vit")).toHaveCount(4);
  /* a luta de cada pet no registro dele: o ativo (uma luta a mais) e os guardados (o "f" e a luta), que continuam guardados */
  expect(await numLog(page, "l")).toBe(l0 + 1);
  const reg = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro()));
  expect(reg.log.filter((e: unknown[]) => e[1] === "l").pop()[2]).toEqual({ r: "salao", s: expect.any(Number) });
  const gs = await lerGuardadosE2e(page);
  gs.forEach((g: { log: [number, string, { r?: string }][] }, i: number) => {
    expect(g.log.length).toBe(g0[i] + 2);
    expect(g.log[g.log.length - 1][2]).toEqual({ r: "salao", s: expect.any(Number) });
  });
  const t = await lerTamer(page);
  const ev = t.log.filter((e: [string]) => e[0] === "salao");
  expect(ev).toHaveLength(1);
  expect(ev[0][1].lutas.map((l: { est: string; forma: string; venceu: boolean }) => [l.est, l.forma, l.venceu]))
    .toEqual([["crianca", "Patamon", true], ["adolescente", "Growlmon", true], ["adulto", "MegaSeadramon", true], ["mega", "Valkyrimon", true]]);
  await irPara(page, "Lutar", "Medalhas", "lutar/medalhas");
  await expect(page.locator(".med-recordes li", { hasText: "Salão" })).toContainText("4 de 4 níveis seguidos, na tentativa 1.");
  expect(erros).toEqual([]);
});

test("fronteira: sem pet de algum nível o Salão diz qual falta e não deixa tentar", async ({ page }) => {
  await semear(page, SAVE_LIGA, undefined, TAMER_CAMPEAO);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/lutar/fronteira");
  const sl = page.locator(".sl-card");
  await expect(sl.locator(".sl-sel")).toHaveCount(1);
  await expect(sl.locator(".sl-falta")).toHaveCount(3);
  await expect(sl.locator(".med-espera")).toContainText("Falta pet dos níveis Rookie, Champion e Ultimate.");
  await expect(sl.locator(".fr-inst-tentar")).toBeDisabled();
  expect(erros).toEqual([]);
});

/* a Fabrica e o Salao na tela: a escolha dos alugados aberta e os pets de cada nivel, celular (360, 390) e desktop (1280), claro e escuro */
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`fronteira: Fábrica e Salão em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semearSalao(page);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/lutar/fronteira");
    await page.locator(".fb-card .fr-inst-tentar:not([disabled])").click();
    await expect(page.locator(".fb-aluguel")).toHaveCount(3);
    await expect(page.locator(".sl-sel")).toHaveCount(4);
    await page.waitForTimeout(600);
    const r = await page.evaluate(desk => {
      const visivel = (e: Element) => (e as HTMLElement).offsetParent !== null;
      const pequenos = [...document.querySelector(desk ? ".fr-tela" : "body")!.querySelectorAll("button, select, input, summary, a")].filter(visivel).flatMap(e => {
        const b = e.getBoundingClientRect();
        return b.height < 44 || b.width < 44 ? [`${e.tagName}.${(e as HTMLElement).className} ${Math.round(b.width)}x${Math.round(b.height)}`] : [];
      });
      const fora = [...document.querySelectorAll(".fb-card *, .sl-card *")].filter(e => { const b = e.getBoundingClientRect(); return b.width > 0 && (b.right > innerWidth + 1 || b.left < -1); })
        .map(e => (e as HTMLElement).className);
      return { larg: document.documentElement.scrollWidth, janela: innerWidth, pequenos, fora };
    }, largura >= 1100);
    expect(r.larg, "rolagem lateral").toBeLessThanOrEqual(r.janela);
    expect(r.pequenos, "alvos menores que 44 px").toEqual([]);
    expect(r.fora, "elementos da Fábrica e do Salão fora da tela").toEqual([]);
    await page.locator(".fb-card").screenshot({ path: `test-results/fronteira-fabrica-${largura}-${tema}.png` });
    await page.locator(".sl-card").screenshot({ path: `test-results/fronteira-salao-${largura}-${tema}.png` });
    await page.screenshot({ path: `test-results/fronteira-4c-${largura}-${tema}.png`, fullPage: true });
    /* uma luta da Fabrica: o alugado com a vida e a oferta de troca */
    await page.locator(".fb-aluguel").first().click();
    await page.locator(".fb-lutar").click();
    await expect(page.locator(".fb-troca")).toBeVisible();
    const r2 = await page.evaluate(() => ({ larg: document.documentElement.scrollWidth, janela: innerWidth }));
    expect(r2.larg).toBeLessThanOrEqual(r2.janela);
    await page.locator(".fb-card").screenshot({ path: `test-results/fronteira-fabrica-troca-${largura}-${tema}.png` });
    expect(erros).toEqual([]);
  });
}

/* ---------------------------------------------------------------- o painel DigiBrain (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 5;
   pranchas DigiBrainDesktop e DigiBrain390): so nos pets v11 (PW-7). No desktop, uma coluna entre o habitat e a coluna de sempre; em
   390 px, uma folha aberta pelo botao do palco, com o Conversar no cabecalho do Pet. Os numeros sao os do motor (Motor.digibrain) */
const SAVE_V11 = { semente: 4242, versao: 11, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "d", "alimentar"], [840, "t", 60]] };
for (const largura of [390, 1280]) {
  test(`DigiBrain: o painel do pet v11 em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await semear(page, SAVE_V11);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    const desktop = largura >= 1100;
    if (desktop) {
      await expect(page.locator(".db-botao")).toBeHidden();
      const card = page.locator(".digibrain");
      await expect(card).toBeVisible();
      const r = await page.evaluate(() => {
        const hab = document.querySelector(".palco-card")!.getBoundingClientRect(), db = document.querySelector(".digibrain")!.getBoundingClientRect(),
          lado = document.querySelector(".lado-cards")!.getBoundingClientRect();
        return { aDireita: db.left >= hab.right - 1 && lado.left >= db.right - 1, larg: document.documentElement.scrollWidth, janela: innerWidth };
      });
      expect(r.aDireita, "o painel entre o habitat e a coluna de sempre").toBe(true);
      expect(r.larg).toBeLessThanOrEqual(r.janela);
    } else {
      await expect(page.locator(".digibrain")).toBeHidden();
      await expect(page.locator(".pet-cab-bt--conversar")).toBeVisible();          /* o Conversar continua no cabecalho do Pet */
      await page.locator(".db-botao").click();
      await expect(page.locator("dialog.folha[open]")).toHaveAttribute("aria-label", "DigiBrain");
    }
    const raiz = desktop ? page.locator(".digibrain") : page.locator("dialog.folha[open]");
    await expect(raiz.locator(".db-selo")).toHaveText("ao vivo");                    /* o tempo do jogo andando */
    /* o painel le o motor: uma decisao, as barras dos lobos (o piso so quando entra na conta) e uma escolhida */
    const db = await page.evaluate(() => (window as any).__digilab.digibrain());
    expect(db).not.toBeNull();
    expect(db.decisao).not.toBeNull();
    await expect(raiz.locator(".db-barras li")).toHaveCount(db.decisao.barras.piso === 0 ? 4 : 5);
    await expect(raiz.locator(".db-barras li[data-lobo='impulsos']")).toBeVisible();
    await expect(raiz.locator(".db-opcoes li.esc")).toHaveCount(1);
    await expect(raiz.locator(".db-emo")).toContainText(/memória do pet/);
    await expect(raiz.locator(".db-ultimas li").first()).toBeVisible();
    /* nada promete mais do que uma soma de pesos */
    expect(await raiz.innerText()).not.toMatch(/pensando|sentindo/i);
    await page.screenshot({ path: test.info().outputPath(`digibrain-${largura}.png`) });     /* a captura do gate da etapa 5 */
    if (!desktop) {
      await page.locator("dialog.folha[open] .folha-x").click();
      await expect(page.locator("dialog.folha[open]")).toHaveCount(0);
    }
    expect(erros).toEqual([]);
  });
}
test("DigiBrain: os pets v1 a v10 não têm o painel (PW-7)", async ({ page }) => {
  for (const largura of [390, 1280]) {
    await page.setViewportSize({ width: largura, height: 800 });
    await semear(page, SAVES.v3);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    await expect(page.locator(".digibrain, .db-botao")).toHaveCount(0);
  }
});
