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
  ["Lutar", "Arena", "lutar/arena"], ["Lutar", "Exploração", "lutar/campanha"], ["Lutar", "Fronteira", "lutar/fronteira"], ["Lutar", "Medalhas", "lutar/medalhas"], ["Diário", "Registro", "diario/registro"], ["Diário", "Catálogo", "diario/catalogo"],
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
    /* a tela Pet da Home (TAREFA_V2_TELA_PET): tres acoes em destaque e as outras em Mais */
    await page.locator(".acoes-pet .acao-mais").click();
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
    await page.getByRole("tab", { name: "Exploração" }).click();
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
  /* sem as transicoes do dl-btn: o teste compara o estilo com e sem foco logo depois de trocar, e uma transicao no meio (a maquina
     ocupada com a cena 3D nos outros workers) dava um falso "sem foco" */
  await page.emulateMedia({ reducedMotion: "reduce" });
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
    /* a Exploracao: o mapa 3D e, no desktop, o lugar na coluna da direita (no celular o lugar abre na folha: o cartao fica no mapa) */
    for (const [rota, esq, dir] of [["crescer/evolucao", ".evo-arv", ".evo-hist"], ["lutar/campanha", ".mapa-expl", desktop ? ".camp-lutar" : ".expl-cartao"], ["conversar/chat", ".conv-lista", ".conv-status"]]) {
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
  /* a evolucao caiu no tick do evento "u" que deu a 1a medalha: a derivacao e exata, e o momento diz qual medalha a liberou */
  await expect(rev.locator(".evm-medalhas")).toContainText("Esta evolução pediu 1 medalha do Tamer. Foi liberada pela Medalha da Campina.");
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
  expect(r.save.versao).toBe(12);                    /* o ovo novo nasce na versao atual (v12: o cerebro A, o corpo e o mundo) */
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
  expect(r.save.versao).toBe(12);                    /* o ovo novo nasce na versao atual (v12) */
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
  await expect(page.locator(".expl-cartao")).toHaveCount(7);
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

/* a Exploracao dos pets v6 (docs/TAREFA_V2_EXPLORACAO.md): o mapa 3D de seis ilhas e a Fronteira no alto (trancada com 3 medalhas), os
   cartoes com o que o motor tem e o marcador do proximo desafio; no celular o cartao abre a folha do lugar. Celular (360, 390) e desktop
   (1280), claro e escuro */
for (const tema of ["light", "dark"] as const) for (const largura of [360, 390, 1280]) {
  test(`exploração: o mapa 3D com 6 ilhas e a Fronteira em ${largura} px, tema ${tema === "light" ? "claro" : "escuro"}`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await page.emulateMedia({ colorScheme: tema });
    await semear(page, SAVE_ARENAS, undefined, TAMER_3);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/lutar/campanha");
    await expect(page.getByRole("tab", { name: "Exploração" })).toHaveAttribute("aria-selected", "true");
    await expect(page.locator(".mapa-expl[data-pronto]")).toBeVisible();
    await expect(page.locator(".mapa-ilhas")).toHaveCount(0);
    await expect(page.locator(".expl-cartao")).toHaveCount(7);
    await expect(page.locator(".expl-cartao--fronteira")).toContainText("abre com as 6 medalhas (3 de 6)");
    await expect(page.locator(".expl-cartao").nth(0)).toContainText("vencido · ");
    await expect(page.locator(".expl-cartao").nth(3)).toContainText("sugerido: Ultimate");
    await expect(page.locator(".expl-cartao").nth(4)).toContainText("vença alguém em Cidadela");
    await expect(page.locator(".expl-cartao.expl-cartao--trancado")).toHaveCount(3);
    await expect(page.locator(".expl-marcador")).toContainText("próximo desafio");
    await expect(page.locator(".expl-cartao").nth(3)).toHaveAttribute("aria-label", "4. Cidadela: sugerido: Ultimate; próximo desafio");
    /* nada do que o motor nao tem: nem nivel numerico, nem "???" */
    await expect(page.locator(".mapa-expl")).not.toContainText(/Nv\.|\?\?\?/);
    await page.waitForTimeout(400);
    const r = await page.evaluate(desk => {
      const mapa = document.querySelector(".mapa-expl-mundo")!.getBoundingClientRect(), tela = document.querySelector<HTMLCanvasElement>(".mapa-expl-tela")!;
      const caixas = [...document.querySelectorAll(".expl-cartao")].map(e => e.getBoundingClientRect());
      const sobrepoe = caixas.some((a, i) => caixas.some((b, j) => j > i && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom));
      const fora = caixas.filter(b => b.left < mapa.left - 1 || b.right > mapa.right + 1 || b.top < mapa.top - 1 || b.bottom > mapa.bottom + 1).length;
      const visivel = (e: Element) => (e as HTMLElement).offsetParent !== null;
      const pequenos = [...document.querySelector(desk ? ".camp-tela" : "body")!.querySelectorAll("button, select, input, summary, a")].filter(visivel).flatMap(e => {
        const b = e.getBoundingClientRect();
        return b.height < 44 || b.width < 44 ? [`${e.tagName}.${(e as HTMLElement).className} ${Math.round(b.width)}x${Math.round(b.height)}`] : [];
      });
      const nomes = [...document.querySelectorAll(".expl-nome")].map(e => e.textContent);
      return { larg: document.documentElement.scrollWidth, janela: innerWidth, sobrepoe, fora, pequenos, nomes, alt: mapa.height, largMapa: mapa.width,
        canvas: [tela.width, tela.height] };
    }, largura >= 1100);
    expect(r.nomes).toEqual(["Campina", "Torre de pedra", "Floresta", "Cidadela", "Lago", "Montanha Espiral", "Fronteira"]);
    expect(r.larg, "rolagem lateral").toBeLessThanOrEqual(r.janela);
    expect(r.sobrepoe, "cartões dos lugares sobrepostos").toBe(false);
    expect(r.fora, "cartões fora do mapa").toBe(0);
    expect(r.pequenos, "alvos menores que 44 px").toEqual([]);
    expect(r.canvas[0] * r.canvas[1], "a vista 3D desenhou").toBeGreaterThan(0);
    if (largura < 1100) {
      expect(r.alt / r.largMapa, "no celular o mapa é mais alto que largo e a página rola").toBeGreaterThan(2);
      /* o cartao do lugar abre a folha com o detalhe (a arena, o Desafiar) */
      await expect(page.locator(".camp-arena")).toHaveCount(0);
      await page.locator(".expl-cartao").nth(3).click();
      const folha = page.locator("dialog.folha[open]");
      await expect(folha).toHaveAttribute("aria-label", "Cidadela");
      await expect(folha.locator(".camp-arena")).toContainText("líder: Myotismon");
      await expect(folha.locator(".camp-lutar")).toContainText("Desafiar Myotismon (3 lutas seguidas)");
      await folha.locator(".folha-x").click();
      await expect(page.locator("dialog.folha[open]")).toHaveCount(0);
      /* um lugar trancado tambem abre: o detalhe diz o que falta */
      await page.locator(".expl-cartao").nth(4).click();
      await expect(page.locator("dialog.folha[open] .camp-det-txt")).toContainText("Trancado: vença alguém em Cidadela antes.");
    } else {
      await expect(page.locator(".camp-lado .camp-arena")).toContainText("líder: Myotismon");
      await page.locator(".expl-cartao").nth(1).click();
      await expect(page.locator(".camp-lado .campd-faixa")).toContainText("Torre de pedra");
      await expect(page.locator(".expl-cartao").nth(1)).toHaveClass(/\bsel\b/);
    }
    expect(erros).toEqual([]);
  });
}
/* sem WebGL: a Exploracao fica com a tela de antes (o mapa 2D das ilhas e o cartao do lugar), sem erro */
test("exploração: sem WebGL, o mapa 2D de antes", async ({ browser }) => {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 390, height: 844 } });
  const p = await ctx.newPage();
  await p.addInitScript(() => {
    const orig = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, tipo: string, ...r: unknown[]) {
      return /webgl/.test(tipo) ? null : (orig as (...a: unknown[]) => unknown).call(this, tipo, ...r);
    } as typeof orig;
  });
  await semear(p, SAVE_ARENAS, undefined, TAMER_3);
  const erros = vigiarErros(p);
  await p.goto(APP + "#/lutar/campanha");
  await expect(p.locator(".mapa-ilhas .lugar")).toHaveCount(7);
  await expect(p.locator(".mapa-expl")).toHaveCount(0);
  await expect(p.locator(".camp-arena")).toContainText("líder: Myotismon");
  expect(erros).toEqual([]);
  await ctx.close();
});

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
    await irPara(page, "Lutar", "Exploração", "lutar/campanha");
    /* no celular a escolha da carta fica na folha do lugar */
    if (largura < 1100) await page.locator(".expl-cartao.sel").click();
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
  const ilha = page.locator(".expl-cartao--fronteira");
  await expect(ilha).toContainText("a Liga dos Líderes está aberta");
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
   pranchas DigiBrainDesktop e DigiBrain390): so nos pets v11 (PW-7). Sob demanda (TAREFA_V2_TELA_PET): no desktop, o botao do cenario
   abre a coluna de detalhes, a direita do cenario, com o painel; em 390 px, uma folha aberta pelo botao do cenario, com o Conversar no
   cabecalho do Pet. Os numeros sao os do motor (Motor.digibrain) */
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
      await expect(page.locator(".db-botao")).toHaveCount(0);
      const card = page.locator("#mod-digibrain .digibrain");                         /* o modulo DigiBrain do quadro, aberto */
      await expect(card).toBeVisible();
      const r = await page.evaluate(() => {
        const cena = document.querySelector(".pet-cena")!.getBoundingClientRect(), db = document.querySelector(".digibrain")!.getBoundingClientRect();
        return { aDireita: db.left >= cena.right - 1, larg: document.documentElement.scrollWidth, janela: innerWidth };
      });
      expect(r.aDireita, "o painel na coluna lateral do quadro, a direita do cenario").toBe(true);
      expect(r.larg).toBeLessThanOrEqual(r.janela);
    } else {
      await expect(page.locator(".digibrain")).toBeHidden();
      await expect(page.locator(".pet-cab-bt--conversar")).toBeVisible();          /* o Conversar continua no cabecalho do Pet */
      await page.locator(".db-botao").click();
      await expect(page.locator("dialog.folha[open]")).toHaveAttribute("aria-label", "DigiBrain");
    }
    const raiz = desktop ? page.locator("#mod-digibrain") : page.locator("dialog.folha[open]");
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
/* o mapa dos pesos (MapaPesos.tsx), no lugar do icone estatico: cada traco e um peso do motor (Motor.digibrain().mapa), e a cada decisao
   acendem a regra, os candidatos com a chance, a acao escolhida e o lobo que pesou mais; entre duas decisoes nada anima */
for (const largura of [390, 1280]) {
  test(`DigiBrain: o mapa dos pesos acende a cada decisão em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await semear(page, SAVE_V11);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    const desktop = largura >= 1100;
    if (!desktop) await page.locator(".db-botao").click();
    const raiz = desktop ? page.locator(".digibrain") : page.locator("dialog.folha[open]");
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
          dest: [...s.querySelectorAll(".mp-dest")].map(g => g.getAttribute("data-lobo")), db,
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
      expect(r.dest).toEqual([m.acesas.lobo_decisivo]);
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
test("DigiBrain: os pets v1 a v10 não têm o painel (PW-7)", async ({ page }) => {
  for (const largura of [390, 1280]) {
    await page.setViewportSize({ width: largura, height: 800 });
    await semear(page, SAVES.v3);
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    await expect(page.locator(".digibrain, .db-botao")).toHaveCount(0);
  }
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
      const cena = r(".pet-cena"), doca = r(".pet-doca"), cv = document.querySelector<HTMLCanvasElement>(".pet-cena canvas")!;
      return { cena: cena.width * cena.height, doca: doca.width * doca.height, pix: getComputedStyle(cv).imageRendering, larg: document.documentElement.scrollWidth, janela: innerWidth };
    });
    expect(g.cena, "o cenario e a maior area").toBeGreaterThan(g.doca * 2);
    expect(g.pix).toBe("pixelated");
    expect(g.larg).toBeLessThanOrEqual(g.janela);
    await expect(page.locator(".acoes-pet .acao-destaque")).toHaveCount(3);
    await expect(page.locator(".acoes-pet .acao-extra")).toHaveCount(0);
    await page.locator(".acoes-pet .acao-mais").click();
    await expect(page.locator(".acoes-pet .acao-extra")).toHaveCount(3);           /* v11: seis acoes, tres em destaque */
    /* sem fundo de hexagonos no cenario e sem retrato redondo no cabecalho do Pet */
    expect(await page.locator(".pet-cena .dl-hexcard, .pet-retrato").count()).toBe(0);
    /* os detalhes: o balao da fala abre o porque */
    await page.locator(".cena-fala").click();
    if (desktop) {
      /* no desktop o porque e um modulo do quadro, recolhido no comeco: o balao o abre */
      await expect(page.locator("#mod-fala .mod-corpo")).toBeVisible();
      await expect(page.locator("#mod-fala .det-fala .fala-status")).toBeVisible();
      await page.getByRole("button", { name: "Recolher Por que ele disse isso" }).click();
      await expect(page.locator("#mod-fala .mod-corpo")).toHaveCount(0);
    } else {
      await expect(page.locator("dialog.folha[open]")).toHaveAttribute("aria-label", "Como ele está");
      await expect(page.locator("dialog.folha[open] .necessidades4")).toBeVisible();
      await page.locator("dialog.folha[open] .folha-x").click();
      await expect(page.locator("dialog.folha[open]")).toHaveCount(0);
    }
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
  await expect(p2.locator(".pet-cena .cena-sala")).toBeVisible();
  await expect(p2.locator(".pet-cena .cena-sala")).toHaveAttribute("aria-hidden", "true");
  await expect(p2.locator(".pet-cena .cena3d")).toHaveCount(0);
  expect(erros2).toEqual([]);
  await ctx.close();
});

/* o quadro modular da tela Pet no desktop (docs/TAREFA_V2_PET_QUADRO.md): os modulos que o motor sustenta, arrastaveis entre as duas
   colunas, com o menu (mover pelo teclado), o recolher de cada modulo e da coluna lateral; o arranjo fica no localStorage (preferencia
   de quem joga, fora do save) e volta depois de recarregar. No celular nao ha quadro */
test("Pet (quadro): arrastar, mover pelo menu, recolher e o arranjo salvo", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await semear(page, SAVE_V11);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  const col = (c: string) => page.evaluate(sel => [...document.querySelectorAll(sel + " > .quadro-vaga")].map(e => e.getAttribute("data-modulo")), `.quadro-col--${c}`);
  await expect(page.locator(".quadro")).toBeVisible();
  expect(await col("principal")).toEqual(["cenario", "acoes"]);
  /* a lateral: os modulos do motor (a proxima evolucao so com a proxima forma; o DigiBrain no v11) */
  expect(await col("lado")).toEqual(["estado", "desejo", "evolucao", "registro", "digibrain", "fala"]);
  await expect(page.locator("#mod-estado .palco-emocao")).toBeVisible();          /* a emocao registrada a direita do titulo */
  await expect(page.locator("#mod-evolucao")).toContainText("até virar");
  await expect(page.locator("#mod-evolucao")).not.toContainText(/n[ií]vel|xp/i);
  /* o "Ver tudo" do registro leva ao Diario */
  await page.locator("#mod-registro").getByRole("button", { name: "Ver tudo" }).click();
  await expect(page).toHaveURL(/#\/diario\/registro$/);
  await page.locator(".dl-nav").getByRole("button", { name: "Pet", exact: true }).click();
  /* arrastar as Ultimas acoes para a coluna principal, acima das Acoes */
  await page.locator("#mod-registro .mod-cab").dragTo(page.locator('.quadro-col--principal [data-modulo="acoes"]'), { targetPosition: { x: 40, y: 8 } });
  expect(await col("principal")).toEqual(["cenario", "registro", "acoes"]);
  /* o menu: mover as Acoes para a coluna lateral (o arrastar pelo teclado) */
  await page.getByRole("button", { name: "Opções do quadro Ações" }).click();
  await page.getByRole("menuitem", { name: "Mover para a coluna lateral" }).click();
  expect(await col("principal")).toEqual(["cenario", "registro"]);
  expect((await col("lado")).at(-1)).toBe("acoes");
  /* recolher o Estado atual: o corpo some */
  await page.getByRole("button", { name: "Recolher Estado atual" }).click();
  await expect(page.locator("#mod-estado .mod-corpo")).toHaveCount(0);
  /* recolher a coluna lateral: o habitat ganha a largura */
  const largura = () => page.evaluate(() => document.querySelector(".pet-cena")!.getBoundingClientRect().width);
  const antes = await largura();
  await page.getByRole("button", { name: "Recolher a coluna lateral" }).click();
  await expect(page.locator(".quadro-col--recolhida")).toBeVisible();
  await expect.poll(largura).toBeGreaterThan(antes + 250);
  /* o arranjo volta depois de recarregar (localStorage), e o save do pet nao muda */
  const save = await page.evaluate(c => localStorage.getItem(c), CHAVE);
  await page.reload();
  await expect(page.locator(".quadro-col--recolhida")).toBeVisible();
  await page.getByRole("button", { name: "Mostrar a coluna lateral" }).click();
  expect(await col("principal")).toEqual(["cenario", "registro"]);
  await expect(page.locator("#mod-estado .mod-corpo")).toHaveCount(0);
  /* o arranjo fica numa chave propria; o save do pet so tem o registro (semente, versao e log), nada do quadro */
  const arranjo = JSON.parse(await page.evaluate(c => localStorage.getItem(c + "-quadro-pet"), CHAVE) ?? "null");
  expect(arranjo.principal).toEqual(["cenario", "registro"]);
  expect(Object.keys(JSON.parse(save ?? "{}")).sort()).toEqual(["log", "semente", "versao"]);
  expect(erros).toEqual([]);
});
test("Pet (quadro): no celular não há quadro", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_V11);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena")).toBeVisible();
  await expect(page.locator(".quadro, .mod-cab")).toHaveCount(0);
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
    await expect(rev.locator(".evm-nome")).toHaveText("Greymon");
    await expect(rev.locator(".evm-estagio")).toHaveText("Champion");
    await expect(rev.locator(".evm-brasao")).toContainText("brasão Coragem");
    await expect(rev.locator(".evm-depara")).toContainText("Agumon");
    await expect(rev.locator(".evm-depara")).toContainText("Greymon");
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
    await expect(page.locator(".evt-heroi .evt-nome")).toHaveText("Greymon");
    await expect(page.locator(".evt-heroi .evt-prazo")).toContainText("até virar Ultimate");
    await expect(page.locator(".evt-prox .evt-selos")).toContainText("1 de 3 medalhas do Tamer");
    await expect(page.locator(".evo-arv")).toBeVisible();
    await expect(page.locator(".evt-porque")).toContainText("Por que Greymon?");
    await expect(page.locator(".evo-hist li")).toHaveCount(3);
    expect(JAPONES.test(await page.locator(".evo-tela").textContent() ?? "")).toBe(false);
    /* o historico reabre o momento de qualquer evolucao */
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
  await expect(page.locator(".evt-heroi .evm-spr--reserva")).toBeVisible();
});

/* a aba Treinar (docs/TAREFA_V2_TREINO.md). save_treino_pausa.json e save_treino_forcar.json (e2e/gerar_save_treino.mjs): um Palmon v11 no
   Rookie que treinou 3 vezes (fadiga entre 40 e 60: pede pausa) ou 4 (fadiga acima de 60: so Forcar) */
const SAVE_TR_PAUSA = JSON.parse(readFileSync(new URL("./save_treino_pausa.json", import.meta.url), "utf8"));
const SAVE_TR_FORCAR = JSON.parse(readFileSync(new URL("./save_treino_forcar.json", import.meta.url), "utf8"));
const SEM_JAPONES = /[぀-ヿ㐀-鿿ｦ-ﾟ]/;
for (const largura of [390, 1280]) {
  test(`treino: a sala, o stat em foco, o cansaço, os exercícios e a pausa em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: largura >= 1100 ? 800 : 844 });
    await semear(page, SAVE_TR_PAUSA);
    const erros = vigiarErros(page);
    await page.goto(APP + "#/crescer/treinar");
    await expect(page.locator(".trn-sala")).toBeVisible();
    await expect(page.locator(".trn-estado")).toHaveText("pediu pausa");
    await expect(page.locator(".trn-balao")).toContainText("pausa?");
    await expect(page.locator(".trn-pet .evm-spr")).toBeVisible();
    /* o stat em foco: o principal do ultimo exercicio (Alvo: mira), de 10, e o do estagio e da vida */
    await expect(page.locator(".trn-foco")).toContainText("stat do último treino · Alvo");
    await expect(page.locator(".trn-foco")).toContainText(/Mira \+\d+,\d de 10/);
    await expect(page.locator(".trn-foco")).toContainText(/no estágio [\d,]+ de 10 · na vida [\d,]+ de 36/);
    await expect(page.locator(".trn-vida li")).toHaveCount(6);
    await expect(page.locator(".treino-ex")).toHaveCount(6);
    await expect(page.locator(".treino-ex.forcar")).toHaveCount(0);
    await expect(page.locator(".trn-ultimo")).toContainText("Alvo · mira e fôlego");
    const texto = await page.locator(".treino-tela").textContent() ?? "";
    expect(SEM_JAPONES.test(texto), "nenhum caractere japonês").toBe(false);
    expect(/\b(Nv|Lv|XP)\b/.test(texto), "nem nível nem XP").toBe(false);
    const r = await page.evaluate(() => Object.fromEntries([".trn-sala", ".trn-foco", ".trn-medidores", ".trn-exercicios", ".trn-vida", ".trn-ultimo"]
      .map(c => { const b = document.querySelector(c)!.getBoundingClientRect(); return [c, [b.left, b.top]]; })));
    if (largura < 1100) {
      /* celular: uma coluna, nesta ordem */
      const tops = [".trn-sala", ".trn-foco", ".trn-medidores", ".trn-exercicios", ".trn-vida", ".trn-ultimo"].map(c => r[c][1]);
      expect(tops).toEqual([...tops].sort((a, b) => a - b));
    } else {
      /* desktop: a sala, o stat em foco e o treinado na vida a esquerda; o cansaco e os exercicios a direita */
      expect(r[".trn-medidores"][0]).toBeGreaterThan(r[".trn-sala"][0] + 200);
      expect(r[".trn-exercicios"][0]).toBeGreaterThan(r[".trn-vida"][0] + 200);
    }
    expect(erros).toEqual([]);
  });
}
test("treino: com fadiga acima de 60 os exercícios viram Forçar, a folha confirma e o treino entra no registro", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_TR_FORCAR);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/crescer/treinar");
  await expect(page.locator(".treino-ex.forcar")).toHaveCount(6);
  const l0 = await numLog(page, "tr");
  /* o intervalo de 10 min passa com o relogio do app (10 min/s) */
  await page.locator(".treino-ex.forcar:not([disabled])").first().click();
  const folha = page.locator("dialog.folha[open]");
  await expect(folha).toContainText("Forçar levantar pedra?");
  await folha.getByRole("button", { name: "Forçar mesmo assim" }).click();
  await expect(page.locator(".trn-msg")).toContainText("Forçado:");
  expect(await numLog(page, "tr")).toBe(l0 + 1);
  await expect(page.locator(".trn-medidores")).toContainText("25 / 100");
  await expect(page.locator(".trn-ultimo")).toContainText("Levantar pedra");
  expect(erros).toEqual([]);
});
/* sem o atlas do UP (o CI, as capturas do repositorio): a sala em CSS, o pet da grade de reserva e os icones do lucide */
test("treino: sem o atlas, a sala em CSS, o pet de reserva e os ícones de reserva", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_TR_PAUSA);
  await page.route(/\/Assets\/(digilab_atlas_up|digilab_decoracao_up|decoracao_up\/)/, r => r.abort());
  await page.goto(APP + "#/crescer/treinar");
  await expect(page.locator(".trn-sala .trn-janela")).toBeVisible();
  await expect(page.locator(".trn-sala.trn-sala--up")).toHaveCount(0);
  await expect(page.locator(".trn-pet .evm-spr--reserva")).toBeVisible();
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
/** arrasta "Por racao" ate o ponto do cliente, com o mouse (o gesto) */
async function arrastarRacao(page: Page, alvo: [number, number]): Promise<void> {
  const b = (await page.locator(".racao-bt").boundingBox())!;
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
    await expect(page.locator(".mundo-info")).toContainText("rações no chão");
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
test("mundo: o caminho acessível, pelo toque no chão e por um lugar nomeado pelo teclado; Esc fecha sem pôr nada", async ({ page }) => {
  test.setTimeout(180_000);
  await page.setViewportSize({ width: 390, height: 844 });
  await semear(page, SAVE_MUNDO);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  await expect.poll(() => lerCena(page)).not.toBeNull();
  const bt = page.getByRole("button", { name: /^Pôr ração/ });
  /* o toque: tocar no botao abre a faixa; tocar no chao poe ali */
  await bt.click();
  await expect(page.locator(".racao-faixa")).toContainText("Toque no chão para pôr a ração");
  await expect(bt).toHaveAttribute("aria-pressed", "true");
  const m0 = await lerMundo(page), [cx, cy] = await naTela(page, m0.lugares.perto[0] + 32, m0.lugares.perto[1]);
  await page.mouse.click(cx, cy);
  await expect(page.locator(".racao-faixa")).toHaveCount(0);
  const dc1 = await ultimoDc(page);
  expect(Math.abs(dc1[2].x - (m0.lugares.perto[0] + 32)) + Math.abs(dc1[2].y - m0.lugares.perto[1])).toBeLessThanOrEqual(2);
  /* Esc fecha sem por nada */
  const n1 = JSON.parse(await page.evaluate(() => (window as any).__digilab.registro())).log.filter((e: unknown[]) => e[1] === "dc").length;
  await bt.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".racao-faixa")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator(".racao-faixa")).toHaveCount(0);
  expect(JSON.parse(await page.evaluate(() => (window as any).__digilab.registro())).log.filter((e: unknown[]) => e[1] === "dc").length).toBe(n1);
  /* o teclado: Enter abre, o foco vai ao Comedouro; Tab ao "Perto do pet" e Enter poe exatamente no lugar nomeado */
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
  /* pelo teclado, e recarregar: o evento dc fica no registro, e a vida refeita tem a racao no mesmo lugar */
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
  await expect(page.locator(".racao-dica")).toContainText("Alimentar é a reserva: põe no comedouro.");
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
  }, [CHAVE, JSON.stringify(SAVES.v3)] as const);
  const erros = vigiarErros(page);
  await page.goto(APP + "#/pet/estado");
  await page.locator("dialog.med-aviso[open]").getByRole("button", { name: "Escolher o brasão do ovo novo" }).click();
  await page.locator("dialog.brasao-tela[open] .br-card").first().click();
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect.poll(() => page.evaluate(() => document.querySelector<HTMLCanvasElement>(".cena3d canvas")?.width ?? 0)).toBeGreaterThan(0);
  const lcd = page.locator(".pet-cena canvas.lcd");
  await expect(lcd).toHaveAttribute("aria-label", "Tela do pet: ovo");
  await expect(lcd).not.toHaveAttribute("aria-label", "Tela do pet: ovo", { timeout: 20_000 });
  await expect(page.locator(".mundo-info")).toBeVisible();
  expect(erros).toEqual([]);
});

/* UP-SOM: o som e desligado por padrao. Desligado, nenhuma requisicao de audio sai (nem em uma luta inteira); ligar e lembrado ao
   recarregar e nao entra no save exportado; ligado com os arquivos ausentes, o aviso aparece e o jogo segue. */
test("som: desligado por padrão não pede áudio nem em uma luta; ligar é lembrado e fica fora do save", async ({ page }) => {
  test.setTimeout(180_000);
  await semear(page, SAVES.v3);
  const erros = vigiarErros(page), pedidos: string[] = [];
  page.on("request", r => { if (/\/Assets\/sons\/|\.mp3(\?|$)/.test(r.url())) pedidos.push(r.url()); });
  await page.goto(APP + "#/pet/estado");
  await irPara(page, "Lutar", "Arena", "lutar/arena");
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
  await expect(page.locator("dialog.modal-res[open]")).toBeVisible({ timeout: 90_000 });
  expect(pedidos, "pediu áudio com o som desligado").toEqual([]);
  await page.locator(".res-continuar").click();
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
  await semear(page, SAVES.v3);
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
  await semear(page, SAVES.v3);
  await page.route(/\/Assets\/digilab_atlas_up_clipes/, r => r.abort());
  await page.goto(APP + "?clipes_up=1#/pet/estado");
  await expect(page.getByText("Atlas de sprites não carregou.")).toBeVisible();
});
