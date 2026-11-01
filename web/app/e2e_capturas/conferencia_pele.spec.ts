/* Conferencia da pele dos menus (docs/TAREFA_V2_TEMA_MENUS.md, missao T3): so roda com DIGILAB_CONFERENCIA_PELE=<pasta> (fora do repositorio);
   sem ela, os testes daqui ficam de fora do portao de capturas. Em 1920 x 950 (D10), com o sprite de reserva, nas duas peles x claro/escuro:
   - as telas que o portao nao alcanca (paineis da tela Pet abertos, DigiBrain, "Por que ele disse isso", Meus pets, Ajustes > Aparencia,
     Boas-vindas, Como jogar, luta em tela cheia e Resultado), gravadas como PNG na pasta;
   - o contraste de todo texto visivel contra o fundo de verdade: o texto fica transparente, a pagina e fotografada e, em cada retangulo de
     texto, o pior pixel do fundo da a razao (WCAG 2.x); o resultado vai para contraste_<pele>_<tema>[_opaco].json na pasta;
   - o anel de foco pelo teclado (cor e largura) e a borda do escolhido, em contraste_*.json;
   - com prefers-reduced-transparency: reduce (pelo CDP), o desfoque e o alfa da superficie do vidro. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const PASTA = process.env.DIGILAB_CONFERENCIA_PELE ?? "";
const SAVES: Record<string, { semente: number; log: unknown[]; versao?: number }> = JSON.parse(readFileSync(new URL("../e2e/saves.json", import.meta.url), "utf8"));
const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
/* o pet v11 do DigiBrain (e2e/jogo.spec.ts) e o v13 da luta em tempo real */
const SAVE_V11 = { semente: 4242, versao: 13, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };
const SAVE_V13 = { semente: 101, versao: 13, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER_V13 = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
/* as rotas do portao, para o contraste */
const ROTAS = ["#/pet/estado", "#/crescer/treinar", "#/crescer/aprend", "#/crescer/evolucao", "#/crescer/itens", "#/lutar/arena", "#/lutar/campanha",
  "#/lutar/fronteira", "#/lutar/medalhas", "#/diario/registro", "#/diario/catalogo", "#/diario/cenarios", "#/conversar/chat", "#/config",
  "#/config/aparencia", "#/config/dados", "#/config/fala", "#/config/sobre"];

interface Medida { tela: string; texto: string; ret: number[]; seletor: string; cor: string; tam: number; peso: number; razao: number; piorPixel: number; minimo: number; desabilitado: boolean }

async function semear(page: Page, save: object | null, tamer: object = { versao: 1, log: [] }, boasVindas = true): Promise<void> {
  await page.unrouteAll();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t, bv]) => {
    localStorage.clear(); if (bv) localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    if (s) localStorage.setItem(chave, s);
  }, [CHAVE, save ? JSON.stringify(save) : null, JSON.stringify(tamer), boasVindas] as const);
}
const RESERVA = /\/Assets\/(digilab_atlas_up|digilab_decoracao_up|decoracao_up\/|digilab_clipes)/;
let relogioParado = false;
async function abrir(page: Page, pele: string, tema: string, rota: string): Promise<void> {
  /* o sprite de reserva (sem o atlas e sem a decoracao do UP); a rota so depois de semear, que usa o endereco do atlas */
  await page.route(RESERVA, r => r.abort());
  /* uma pagina nova a cada tela: um goto que so troca o hash nao recarrega (e deixaria aberto o que estava aberto, como Meus pets) */
  await page.goto("about:blank");
  await page.goto(`${APP}?pele=${pele}&tema=${tema}${rota}`);
  await page.addStyleTag({ content: ".app > .aviso, .avisos > .aviso{display:none}" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => !document.querySelector(".pet-cena") || !!document.querySelector(".pet-cena .cena-sala")
    || !!document.querySelector(".pet-cena .cena3d[data-pronto]"));
  await page.waitForFunction(() => !document.querySelector(".camp-tela--expl") || !!document.querySelector(".mapa-expl[data-pronto]"));
  /* com o relogio parado (as medidas), ele anda 1 s depois de abrir, como no portao: a cena desenha e o jogo nao muda entre a coleta dos
     textos e a foto do fundo */
  if (relogioParado) await page.clock.runFor(1000);
  await page.waitForTimeout(400);
}
async function foto(page: Page, nome: string): Promise<void> {
  await page.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => undefined))));
  await page.screenshot({ path: join(PASTA, nome + ".png"), animations: "disabled", caret: "hide" });
}

/** contraste de todo texto visivel: o pior pixel do fundo (com o texto transparente) em cada retangulo do texto */
async function medirContraste(page: Page, tela: string): Promise<Medida[]> {
  const alvos = await page.evaluate(() => {
    const out: { texto: string; seletor: string; cor: string; tam: number; peso: number; rets: number[][]; desabilitado: boolean }[] = [];
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      const t = (n.textContent ?? "").trim(), el = n.parentElement;
      if (!t || !el || el.closest("script, style, noscript, [aria-hidden='true'] svg, .sr-only, .visualmente-oculto")) continue;
      const c = getComputedStyle(el);
      if (c.visibility !== "visible" || parseFloat(c.opacity) === 0) continue;
      const r = document.createRange(); r.selectNodeContents(n);
      const rets = [...r.getClientRects()].filter(q => q.width >= 2 && q.height >= 4 && q.bottom > 0 && q.right > 0 && q.top < innerHeight && q.left < innerWidth)
        /* so o que se ve inteiro: o meio e os dois cantos do retangulo caem no proprio elemento (nao coberto por modal, nem cortado pela
           rolagem de uma lista; o texto cortado pela metade fica de fora da medida) */
        .filter(q => [[q.left + q.width / 2, q.top + q.height / 2], [q.left + 1, q.top + 1], [q.right - 1, q.bottom - 1]].every(([x, y]) => {
          const h = document.elementFromPoint(x, y); return !!h && (el.contains(h) || h.contains(el)); }))
        .map(q => [q.left, q.top, q.width, q.height]);
      if (!rets.length) continue;
      /* a opacidade acumulada dos ancestrais entra no alfa do texto */
      let op = 1; for (let a: Element | null = el; a; a = a.parentElement) op *= parseFloat(getComputedStyle(a).opacity);
      /* o texto do SVG pinta com fill */
      const svg = el instanceof SVGElement, m = (svg ? c.fill : c.color).match(/[\d.]+/g)?.map(Number);
      if (!m || (svg && !c.fill.startsWith("rgb"))) continue;
      const caminho = (x: Element) => [x.tagName.toLowerCase(), ...[...x.classList].slice(0, 2)].join(".");
      out.push({ texto: t.slice(0, 40), seletor: [el.parentElement, el].filter(Boolean).map(x => caminho(x!)).join(" > "),
        cor: `${m[0]},${m[1]},${m[2]},${(m[3] ?? 1) * op}`, tam: parseFloat(c.fontSize), peso: Number(c.fontWeight), rets,
        desabilitado: !!el.closest(":disabled, [aria-disabled='true']") });
    }
    return out;
  });
  const sem = await page.addStyleTag({ content: "*,*::before,*::after{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important;-webkit-text-stroke:0!important;caret-color:transparent!important}text,tspan{fill:transparent!important;stroke:transparent!important}" });
  /* a foto do fundo fica na pasta, para conferir a medida */
  const fundo = await page.screenshot({ animations: "disabled" });
  mkdirSync(join(PASTA, "fundos"), { recursive: true });
  writeFileSync(join(PASTA, "fundos", `${(await page.evaluate(() => document.documentElement.dataset.pele))}_${tela.replace(/[^a-z0-9]+/gi, "-")}.png`), fundo);
  const png = fundo.toString("base64");
  await sem.evaluate(e => (e as Element).remove());
  return page.evaluate(async ([png, alvos, tela]) => {
    const img = new Image(); img.src = "data:image/png;base64," + png; await img.decode();
    const cv = document.createElement("canvas"); cv.width = img.width; cv.height = img.height;
    const g = cv.getContext("2d")!; g.drawImage(img, 0, 0);
    const px = g.getImageData(0, 0, cv.width, cv.height).data;
    const lin = (v: number) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    const lum = (r: number, gg: number, b: number) => 0.2126 * lin(r) + 0.7152 * lin(gg) + 0.0722 * lin(b);
    return alvos.map(a => {
      const [r, gg, b, al] = a.cor.split(",").map(Number);
      /* a razao de cada pixel do fundo; o pior pixel pega tambem bordas e linhas que cruzam o retangulo, entao a medida principal e o
         percentil 10 (o fundo de 90 % da area do texto) e o pior pixel fica ao lado */
      const qs: number[] = [];
      for (const [x, y, w, h] of a.rets) {
        for (let j = Math.ceil(y); j < Math.min(cv.height, Math.floor(y + h)); j++) for (let i = Math.ceil(x); i < Math.min(cv.width, Math.floor(x + w)); i++) {
          const k = (j * cv.width + i) * 4, br = px[k], bg = px[k + 1], bb = px[k + 2];
          /* o texto com alfa se mistura ao fundo daquele pixel */
          const lt = lum(r * al + br * (1 - al), gg * al + bg * (1 - al), b * al + bb * (1 - al)), lf = lum(br, bg, bb);
          qs.push((Math.max(lt, lf) + 0.05) / (Math.min(lt, lf) + 0.05));
        }
      }
      qs.sort((p, q) => p - q);
      const pior = qs[Math.floor(qs.length * 0.1)] ?? Infinity, minPx = qs[0] ?? Infinity;
      const grande = a.tam >= 24 || (a.tam >= 18.66 && a.peso >= 700);
      return { tela, texto: a.texto, seletor: a.seletor, ret: a.rets[0].map(Math.round), cor: a.cor, tam: a.tam, peso: a.peso, razao: Math.round(pior * 100) / 100, piorPixel: Math.round(minPx * 100) / 100, minimo: grande ? 3 : 4.5, desabilitado: a.desabilitado };
    }).filter(m => Number.isFinite(m.razao));
  }, [png, alvos, tela] as const);
}

/** o anel de foco de cada controle alcancado pelo Tab, e a borda dos escolhidos da tela sem foco */
async function medirFoco(page: Page, voltas: number): Promise<{ foco: string[]; semFoco: string[]; escolhido: string[] }> {
  const foco = new Map<string, string>(), semFoco: string[] = [];
  for (let i = 0; i < voltas; i++) {
    await page.keyboard.press("Tab");
    const r = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null;
      if (!el || el === document.body) return null;
      const est = (x: Element) => { const c = getComputedStyle(x); return { o: c.outlineStyle !== "none" && parseFloat(c.outlineWidth) > 0 ? `${c.outlineWidth} ${c.outlineColor}` : "", s: c.boxShadow, b: c.borderColor }; };
      const com = est(el); el.blur(); const sem = est(el); el.focus({ focusVisible: true } as FocusOptions);
      const nome = `${el.tagName.toLowerCase()}.${[...el.classList].slice(0, 2).join(".")}`;
      return { nome, igual: JSON.stringify(com) === JSON.stringify(sem), anel: com.o || com.s };
    });
    if (!r) continue;
    if (r.igual) semFoco.push(r.nome); else if (!foco.has(r.anel)) foco.set(r.anel, r.nome);
  }
  const escolhido = await page.evaluate(() => [...document.querySelectorAll("[aria-current='page'], [aria-current='true'], [aria-checked='true'], [aria-selected='true'], [aria-pressed='true']")]
    .map(e => { const c = getComputedStyle(e); return `${e.tagName.toLowerCase()}.${[...e.classList].slice(0, 2).join(".")}: borda ${c.borderTopColor} ${c.borderTopWidth}`; }));
  return { foco: [...foco].map(([anel, nome]) => `${anel} (${nome})`), semFoco, escolhido: [...new Set(escolhido)] };
}

test.describe("conferência da pele dos menus (T3)", () => {
  test.skip(!PASTA, "só com DIGILAB_CONFERENCIA_PELE=<pasta>");
  test.beforeAll(() => { if (PASTA) mkdirSync(PASTA, { recursive: true }); });
  test.beforeEach(async ({ page }) => {
    relogioParado = false;
    await page.setViewportSize({ width: 1920, height: 950 });
  });

  for (const pele of ["vidro", "xcom"]) for (const tema of ["claro", "escuro"]) {
    const sufixo = `${pele === "vidro" ? "holografico" : "militar"}_${tema}`;

    test(`telas extras: ${sufixo}`, async ({ page }) => {
      const erros: string[] = []; page.on("pageerror", e => erros.push(e.message));
      await semear(page, SAVE_V11);
      await abrir(page, pele, tema, "#/pet/estado");
      await foto(page, `pet-hud_${sufixo}_1920`);
      await page.getByRole("button", { name: "Evolução", exact: true }).click();
      await page.getByRole("button", { name: "Últimas ações", exact: true }).click();
      await page.waitForTimeout(300);
      await foto(page, `pet-paineis-abertos_${sufixo}_1920`);
      await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
      await expect(page.locator("#pet-painel .digibrain")).toBeVisible();
      await page.waitForTimeout(300);
      await foto(page, `pet-digibrain_${sufixo}_1920`);
      await page.getByRole("button", { name: "Fechar DigiBrain" }).click();
      await page.locator(".cena-fala").click();
      await expect(page.locator("#pet-painel .det-fala")).toBeVisible();
      await page.waitForTimeout(300);
      await foto(page, `pet-porque_${sufixo}_1920`);
      await page.getByRole("button", { name: "Fechar Por que ele disse isso" }).click();
      await page.locator(".acoes-pet .acao-mais").click();
      await page.waitForTimeout(200);
      await foto(page, `pet-dock-mais_${sufixo}_1920`);
      await page.keyboard.press("Escape");
      await page.locator(".topo-retrato").click();
      await page.waitForTimeout(300);
      await foto(page, `meus-pets_${sufixo}_1920`);
      await abrir(page, pele, tema, "#/config/aparencia");
      await foto(page, `config-aparencia_${sufixo}_1920`);
      /* o foco pelo teclado sobre o escolhido e sobre o outro cartao: o anel tem de se distinguir da borda do escolhido */
      const grupo = page.getByRole("radiogroup", { name: "Pele dos menus" });
      for (const [sel, nome] of [["[aria-checked='true']", "escolhido"], ["[aria-checked='false']", "outro"]]) {
        await grupo.locator(sel).evaluate(e => (e as HTMLElement).focus({ focusVisible: true } as FocusOptions));
        /* o recorte com 8 px de folga: o anel do cartao nao escolhido fica 2 px para fora */
        const c = (await grupo.boundingBox())!;
        await page.screenshot({ path: join(PASTA, `foco-${nome}_${sufixo}.png`), animations: "disabled",
          clip: { x: c.x - 8, y: c.y - 8, width: c.width + 16, height: c.height + 16 } });
      }
      /* Boas-vindas e Como jogar: a primeira visita, sem pet */
      await semear(page, null, { versao: 1, log: [] }, false);
      await abrir(page, pele, tema, "#/pet/estado");
      await expect(page.locator("dialog.boas-vindas-tela[open]")).toBeVisible();
      await foto(page, `boas-vindas_${sufixo}_1920`);
      await page.locator("dialog.boas-vindas-tela[open] button").last().click();
      await page.waitForTimeout(500);
      await foto(page, `como-jogar_${sufixo}_1920`);
      expect(erros).toEqual([]);
    });

    test(`luta e resultado: ${sufixo}`, async ({ page }) => {
      const erros: string[] = []; page.on("pageerror", e => erros.push(e.message));
      await semear(page, SAVE_V13, TAMER_V13);
      await abrir(page, pele, tema, "#/lutar/arena");
      await page.locator(".lutar-grande").click();
      await expect(page).toHaveURL(/#\/lutar\/luta$/);
      await expect(page.getByTestId("luta-relogio")).toHaveText(/^0:0[2-9]$/, { timeout: 15_000 });
      await page.getByRole("button", { name: "Pausar a animação" }).click();
      await foto(page, `luta_${sufixo}_1920`);
      await page.getByRole("button", { name: "Continuar a animação" }).click();
      await page.getByRole("button", { name: "Velocidade dobrada" }).click();
      await expect(page.locator("dialog.modal-res[open]")).toBeVisible({ timeout: 120_000 });
      await page.waitForTimeout(500);
      await foto(page, `luta-resultado_${sufixo}_1920`);
      expect(erros).toEqual([]);
    });
  }

  /* a tela Pet sobre a ilha nas duas peles, no mesmo estado e no mesmo tamanho (a folha lado a lado da refeitura de 2026-10-31): o pet v11,
     tema claro, em 1280 x 800 e 390 x 844, mais uma tela aberta (Crescer > Treinar) em cada largura */
  test("ilha nas duas peles", async ({ page }) => {
    const erros: string[] = []; page.on("pageerror", e => erros.push(e.message));
    for (const [w, hh] of [[1280, 800], [390, 844]]) for (const pele of ["xcom", "vidro"]) {
      await page.setViewportSize({ width: w, height: hh });
      await semear(page, SAVE_V11);
      await abrir(page, pele, "claro", "#/pet/estado");
      await foto(page, `ilha_${pele}_${w}`);
      await semear(page, SAVES.champion);
      await abrir(page, pele, "claro", "#/crescer/treinar");
      await foto(page, `crescer_${pele}_${w}`);
    }
    expect(erros).toEqual([]);
  });

  for (const pele of ["vidro", "xcom"]) for (const opaco of [false, true]) {
    if (pele === "xcom" && opaco) continue;
    test(`contraste e foco: ${pele} claro${opaco ? " opaco" : ""}`, async ({ page }) => {
      test.setTimeout(600_000);
      const T0 = new Date("2026-10-19T12:00:00Z").getTime();
      await page.clock.install({ time: T0 });
      await page.clock.pauseAt(T0 + 1000);
      relogioParado = true;
      if (opaco) {
        const cdp = await page.context().newCDPSession(page);
        await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-transparency", value: "reduce" }] });
      }
      const medidas: Medida[] = [];
      await semear(page, SAVES.champion);
      for (const rota of ROTAS) { await abrir(page, pele, "claro", rota); medidas.push(...await medirContraste(page, rota)); }
      await semear(page, SAVE_V11);
      await abrir(page, pele, "claro", "#/pet/estado");
      await page.getByRole("button", { name: "Evolução", exact: true }).click();
      await page.getByRole("button", { name: "Últimas ações", exact: true }).click();
      await page.waitForTimeout(300);
      medidas.push(...await medirContraste(page, "pet: os três painéis"));
      await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
      await page.waitForTimeout(300);
      medidas.push(...await medirContraste(page, "pet: DigiBrain"));
      await page.getByRole("button", { name: "Fechar DigiBrain" }).click();
      await page.locator(".cena-fala").click();
      await page.waitForTimeout(300);
      medidas.push(...await medirContraste(page, "pet: Por que ele disse isso"));
      await page.getByRole("button", { name: "Fechar Por que ele disse isso" }).click();
      await page.locator(".topo-retrato").click();
      await page.waitForTimeout(300);
      medidas.push(...await medirContraste(page, "Meus pets"));
      await semear(page, null, { versao: 1, log: [] }, false);
      await abrir(page, pele, "claro", "#/pet/estado");
      medidas.push(...await medirContraste(page, "Boas-vindas"));
      await page.locator("dialog.boas-vindas-tela[open] button").last().click();
      await page.waitForTimeout(500);
      medidas.push(...await medirContraste(page, "Como jogar"));

      /* o vidro: desfoque e superficie do painel lateral */
      await semear(page, SAVES.champion);
      await abrir(page, pele, "claro", "#/crescer/treinar");
      const vidro = await page.evaluate(() => [".painel-tela .hx-painel", ".hx-nav"].map(s => {
        const e = document.querySelector(s); if (!e) return `${s}: ausente`;
        const c = getComputedStyle(e); return `${s}: backdrop-filter ${c.backdropFilter}`;
      }).concat(["--hx-miolo-2", "--hx-miolo", "--hx-chao"].map(v => `${v}: ${getComputedStyle(document.documentElement).getPropertyValue(v).trim()}`)));
      const focoTreinar = await medirFoco(page, 30);
      await abrir(page, pele, "claro", "#/config/aparencia");
      const focoAparencia = await medirFoco(page, 25);
      await semear(page, SAVE_V11);
      await abrir(page, pele, "claro", "#/pet/estado");
      const focoPet = await medirFoco(page, 25);

      const falhas = medidas.filter(m => m.razao < m.minimo);
      const pior = [...medidas].sort((a, b) => a.razao / a.minimo - b.razao / b.minimo).slice(0, 15);
      writeFileSync(join(PASTA, `contraste_${pele}_claro${opaco ? "_opaco" : ""}.json`), JSON.stringify({ pele, tema: "claro", opaco, n: medidas.length,
        falhas: falhas.length, falhasAtivas: falhas.filter(f => !f.desabilitado).length, pior, vidro, foco: { treinar: focoTreinar, aparencia: focoAparencia, pet: focoPet },
        medidas }, null, 1));
    });
  }
});
