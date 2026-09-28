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
  ["Lutar", "Arena", "lutar/arena"], ["Lutar", "Campanha", "lutar/campanha"], ["Diário", "Registro", "diario/registro"], ["Diário", "Catálogo", "diario/catalogo"],
  ["Diário", "Cenários", "diario/cenarios"], ["Conversar", "", "conversar/chat"],
];

/** semeia o save por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele ao fechar) */
async function semear(page: Page, save: object | null, tema?: string): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1");
    if (s) localStorage.setItem(chave, s);
    if (t) localStorage.setItem(chave + "-tema", t);
  }, [CHAVE, save ? JSON.stringify(save) : null, tema ?? null] as const);
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
    await page.goto(APP + "#/pet/estado");
    await expect(page.locator(".pet-tela")).toBeVisible();
    await expect(page.locator(".pet-cab .dl-tag--estagio")).toHaveText(/Champion/i);

    /* os 5 destinos e as 10 abas, pela barra e pelas abas */
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
    await expect(page.locator("dialog.modal-res[open]")).toBeVisible({ timeout: 90_000 });
    await page.getByRole("button", { name: "Continuar" }).click();
    await expect(page).toHaveURL(/#\/lutar\/arena$/);
    await page.getByRole("tab", { name: "Campanha" }).click();
    await page.locator(".camp-lutar:not([disabled])").click();
    await expect(page.locator("dialog.modal-res[open]")).toBeVisible({ timeout: 90_000 });
    await page.getByRole("button", { name: "Continuar" }).click();
    await expect(page).toHaveURL(/#\/lutar\/campanha$/);
    expect(await numLog(page, "l")).toBe(l0 + 2);

    /* pausa o tempo (Diario > engrenagem > Registro e replay) e confere a assinatura com o HTML rodando o mesmo registro */
    await page.locator(".dl-nav").getByRole("button", { name: "Diário", exact: true }).click();
    await page.locator(".cab-engrenagem").click();
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
      const alvo = el.querySelector(".circ, .evo-cx") ?? el, com = estilo(alvo);
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
    for (const [rota, esq, dir] of [["crescer/evolucao", ".evo-arv", ".evo-hist"], ["lutar/campanha", ".mapa-ilhas", ".camp-det"], ["conversar/chat", ".conv-lista", ".conv-status"]]) {
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
