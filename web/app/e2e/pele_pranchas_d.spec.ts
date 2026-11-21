/* Os acertos do Vidro e do Militar contra as pranchas D (docs/TAREFA_V3_UX_TELA_PET.md, secao 33): o botao principal, o fechar e a chave dos
   Ajustes, como o navegador os desenha em cada pele. So CSS: o que a chave faz (ligar e desligar pela linha e pelo teclado) e o registro nao
   mudam. A janela Estado atual ficou de fora por decisao do Matheus (2026-11-21). So no desktop. O save e o do camera_livre.spec. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };
/* o mesmo pet 106 minutos depois: ele chama (o cartao do chamado, com o Atender) */
const SAVE_CHAMADO = { ...SAVE, log: [...SAVE.log, [900, "t", 106]] };
/* o ciano dos destaques do Vidro (--hx-escolhido-borda) e o caqui do escolhido do Militar */
const CHEIA = { vidro: "rgb(95, 212, 255)", xcom: "rgb(197, 207, 176)" } as const;
type Pele = keyof typeof CHEIA;

async function abrir(browser: Browser, save: object = SAVE): Promise<{ page: Page; erros: string[]; fechar: () => Promise<void> }> {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1536, height: 1024 } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up_pecas.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(save)] as const);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  return { page, erros, fechar: () => ctx.close() };
}
const registro = (page: Page) => page.evaluate(() => JSON.stringify(JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] !== "t")));
const ir = async (page: Page, pele: Pele, rota: string) => {
  await page.goto(`${APP}?pele=${pele}#/${rota}`);
  await page.reload();
  await expect(page.locator(".cena3d").first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.dataset.pele)).toBe(pele);
};

for (const pele of ["vidro", "xcom"] as const) {
  test(`${pele}: a chave dos Ajustes e o interruptor retangular, e continua ligando pela linha e pelo teclado`, async ({ browser }) => {
    test.setTimeout(120_000);
    const { page, erros, fechar } = await abrir(browser);
    await ir(page, pele, "config");
    const antes = await registro(page);
    const linha = page.locator("label.aj:has(input[role='switch'])").first(), chave = linha.locator("input");
    const desenho = () => chave.evaluate(e => { const s = getComputedStyle(e), r = e.getBoundingClientRect();
      return { larg: r.width, alt: r.height, aparencia: s.appearance, canto: s.borderRadius, fundo: s.backgroundColor, cursor: s.backgroundPositionX, ligada: (e as HTMLInputElement).checked }; });
    const d0 = await desenho();
    expect(d0).toMatchObject({ larg: 46, alt: 24, aparencia: "none", canto: "0px", ligada: false, fundo: "rgba(0, 0, 0, 0)", cursor: "3px" });
    /* a linha inteira e o alvo: o toque no nome liga */
    await linha.locator(".aj-nome").click();
    await expect(chave).toBeChecked();
    await expect(chave).toHaveCSS("background-color", CHEIA[pele]);
    expect((await desenho()).cursor).toBe("calc(100% - 3px)");
    /* pelo teclado: o Espaco desliga, e o foco aparece na chave */
    await chave.focus();
    await page.keyboard.press("Space");
    await expect(chave).not.toBeChecked();
    await expect(chave).toHaveCSS("background-color", "rgba(0, 0, 0, 0)");
    await page.keyboard.press("Shift+Tab");
    await page.keyboard.press("Tab");
    await expect(chave).toBeFocused();
    await expect(chave).toHaveCSS("outline-style", "solid");
    /* todas as chaves da lista e das partes tem a mesma forma; as desligadas de fabrica ficam apagadas */
    for (const r of ["config", "config/fala"]) {
      await ir(page, pele, r);
      const todas = page.locator("input[type='checkbox'][role='switch']");
      const n = await todas.count();
      expect(n, r).toBeGreaterThan(0);
      for (let i = 0; i < n; i++) {
        const c = await todas.nth(i).evaluate(e => { const s = getComputedStyle(e), b = e.getBoundingClientRect(); return { larg: b.width, alt: b.height, aparencia: s.appearance, opaca: s.opacity, parada: (e as HTMLInputElement).disabled }; });
        expect(c, `${r} #${i}`).toMatchObject({ larg: 46, alt: 24, aparencia: "none", opaca: c.parada ? "0.5" : "1" });
      }
    }
    expect(await registro(page)).toBe(antes);
    expect(erros).toEqual([]);
    await fechar();
  });

  test(`${pele}: o fechar com o x de traco fino e o botao principal com a forma da pele`, async ({ browser }) => {
    test.setTimeout(120_000);
    const { page, erros, fechar } = await abrir(browser);
    await ir(page, pele, "lutar/arena");
    const x = page.locator(".painel-tela .hx-quad").first();
    await expect(x).toHaveAccessibleName(/.+/);
    const f = await x.evaluate(e => { const s = getComputedStyle(e), a = getComputedStyle(e, "::before"), r = e.getBoundingClientRect();
      return { larg: r.width, alt: r.height, letra: getComputedStyle(e.querySelector("span")!).display, xLarg: a.width, xAlt: a.height, mascara: a.maskImage || a.webkitMaskImage, borda: s.borderTopWidth, cor: s.color, bordaCor: s.borderTopColor }; });
    expect(f).toMatchObject({ larg: 44, alt: 44, letra: "none", xLarg: "20px", xAlt: "20px" });
    expect(f.mascara).toContain("data:image/svg+xml");
    if (pele === "xcom") expect(f).toMatchObject({ borda: "2px", cor: CHEIA.xcom, bordaCor: CHEIA.xcom });
    /* o anel de foco do fechar: no Vidro, para dentro do chanfro do painel */
    await x.focus();
    await page.keyboard.press("Shift+Tab");
    await page.keyboard.press("Tab");
    await expect(x).toBeFocused();
    await expect(x).toHaveCSS("outline-offset", pele === "vidro" ? "-8px" : "-3px");
    /* o botao principal: no Vidro, 13 px, 2 px entre as letras, 48 px e o canto cortado; no Militar, como era */
    const lutar = page.getByTestId("poc-lutar");
    const b = await lutar.evaluate(e => { const s = getComputedStyle(e); return { alt: e.getBoundingClientRect().height, letra: s.fontSize, vao: s.letterSpacing, caixa: s.textTransform, corte: s.clipPath }; });
    if (pele === "vidro") {
      expect(b).toMatchObject({ alt: 48, letra: "13px", vao: "2px", caixa: "uppercase" });
      expect(b.corte).toContain("polygon");
    } else expect(b).toMatchObject({ caixa: "uppercase", corte: "none" });
    /* o Verificar do Registro: caixa alta nas duas; no Militar com a hachura no topo, no Vidro com o canto cortado */
    await ir(page, pele, "diario/registro");
    const v = await page.locator(".rg2-bt--acao").first().evaluate(e => { const s = getComputedStyle(e), a = getComputedStyle(e, "::before");
      return { caixa: s.textTransform, corte: s.clipPath, letra: s.fontSize, hachura: a.content === "none" ? "" : a.backgroundImage, hachuraAlt: a.height }; });
    expect(v.caixa).toBe("uppercase");
    if (pele === "vidro") { expect(v.letra).toBe("13px"); expect(v.corte).toContain("polygon"); }
    else { expect(v.letra).toBe("16px"); expect(v.hachura).toContain("repeating-linear-gradient"); expect(v.hachuraAlt).toBe("6px"); }
    /* o Copiar, o botao secundario, fica em caixa mista (como na prancha) */
    expect(await page.locator(".rg2-bt:not(.rg2-bt--acao)").first().evaluate(e => getComputedStyle(e).textTransform)).toBe("none");
    /* o fechar continua fechando */
    await page.locator(".painel-tela .hx-quad").first().click();
    await expect(page.locator(".painel-tela .hx-quad")).toHaveCount(0);
    expect(erros).toEqual([]);
    await fechar();
  });
}

test("vidro: o Atender do chamado tem a forma e a altura do botao principal", async ({ browser }) => {
  test.setTimeout(120_000);
  const { page, erros, fechar } = await abrir(browser, SAVE_CHAMADO);
  await page.goto(`${APP}?pele=vidro#/pet/estado`);
  await expect(page.locator(".cena3d").first()).toBeVisible();
  const atender = page.locator(".pet-alerta .chamado .hx-continuar");
  await expect(atender).toBeVisible();
  const b = await atender.evaluate(e => { const s = getComputedStyle(e); return { alt: e.getBoundingClientRect().height, letra: s.fontSize, vao: s.letterSpacing, caixa: s.textTransform, corte: s.clipPath }; });
  expect(b).toMatchObject({ alt: 48, letra: "13px", vao: "2px", caixa: "uppercase" });
  expect(b.corte).toContain("polygon");
  expect(erros).toEqual([]);
  await fechar();
});
