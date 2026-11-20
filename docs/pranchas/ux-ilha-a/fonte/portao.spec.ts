/* Copiado para web/app/e2e_capturas/ so na hora de rodar (playwright.capturas.config.ts) e apagado depois: o portao "o que nao e a ilha A nao muda". As telas do telas.spec.ts, a 1920 e a 390, nas duas peles, no build da base
   (a worktree ilha-a-base, origin/main) e no deste branch, com o mesmo relogio parado. Guarda as duas capturas e o DOM (o body, sem a camada nova
   .objetos-ilha) em D:\Trab\digilab\capturas_ux_ilha_aprovar\codigo_a\portao\; a comparacao e feita depois (comparar_portao.py). */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, object> = JSON.parse(readFileSync(new URL("../e2e/saves.json", import.meta.url), "utf8"));
const BASE = "/ilha-a-base", RAMO = process.env.PORTAO_CONTROLE ? BASE : "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const CHAVE = "digilab-web-v21-sprites", OUT = "D:/Trab/digilab/capturas_ux_ilha_aprovar/codigo_a/portao" + (process.env.PORTAO_CONTROLE ? "_controle" : "");
const SAVE_V11 = { semente: 4242, versao: 11, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "d", "alimentar"], [840, "t", 60]] };
const ler = (n: string) => JSON.parse(readFileSync(new URL(`../e2e/${n}`, import.meta.url), "utf8"));
const SAVE_ARENAS = ler("save_arenas.json"), SAVE_TR_PAUSA = ler("save_treino_pausa.json"), SAVE_MUNDO = ler("save_mundo.json");
const TAMER_3 = { versao: 1, log: ["campina", "torre", "floresta"].map((id, i) =>
  ["medalha", { id, n: i + 1, quando: 1 + i, pet: SAVE_ARENAS.semente, forma: "DinoBeemon", tick: 900 + i }]) };
const TELAS: [string, string, object, object?][] = [
  ["pet-estado", "#/pet/estado", SAVES.champion], ["crescer-treinar", "#/crescer/treinar", SAVES.champion], ["crescer-aprend", "#/crescer/aprend", SAVES.champion],
  ["crescer-evolucao", "#/crescer/evolucao", SAVES.champion], ["crescer-itens", "#/crescer/itens", SAVES.champion], ["lutar-arena", "#/lutar/arena", SAVES.champion],
  ["lutar-campanha", "#/lutar/campanha", SAVES.champion], ["lutar-fronteira", "#/lutar/fronteira", SAVES.champion], ["lutar-medalhas", "#/lutar/medalhas", SAVES.champion],
  ["diario-registro", "#/diario/registro", SAVES.champion], ["diario-catalogo", "#/diario/catalogo", SAVES.champion], ["diario-cenarios", "#/diario/cenarios", SAVES.champion],
  ["conversar", "#/conversar/chat", SAVES.champion], ["config", "#/config", SAVES.champion], ["pet-v11", "#/pet/estado", SAVE_V11],
  ["lutar-exploracao-v6", "#/lutar/campanha", SAVE_ARENAS, TAMER_3], ["treino-pausa", "#/crescer/treinar", SAVE_TR_PAUSA], ["pet-v12", "#/pet/estado", SAVE_MUNDO],
];

async function capturar(page: Page, raiz: string, rota: string, save: object, tamer: object, pele: string): Promise<{ png: Buffer; dom: string }> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "5"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(save), JSON.stringify(tamer)] as const);
  const T0 = new Date("2026-10-19T12:00:00Z").getTime();
  await page.clock.install({ time: T0 });
  await page.clock.pauseAt(T0 + 1000);
  await page.goto(`${raiz}/web/dist/?pele=${pele}${rota}`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => !document.querySelector(".pet-cena") || !!document.querySelector(".pet-cena .cena-sala")
    || !!document.querySelector(".pet-cena .cena3d[data-pronto]"));
  await page.waitForFunction(() => !document.querySelector(".camp-tela--expl") || !!document.querySelector(".mapa-expl[data-pronto]"));
  await page.waitForFunction(() => !!document.querySelector(".topo-retrato img, .mm-retrato img") || !!document.querySelector(".avisos .aviso")
    || !document.querySelector(".topo-retrato, .mm-retrato"), undefined, { timeout: 90_000 });
  await page.clock.runFor(1000);
  await page.waitForLoadState("networkidle");
  await page.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => undefined))));
  await page.evaluate(() => { const h = document.documentElement; h.style.display = "none"; void h.offsetHeight; h.style.display = ""; void h.offsetHeight; });
  const dom = await page.evaluate(() => {
    const b = document.body.cloneNode(true) as HTMLElement;
    for (const e of b.querySelectorAll(".objetos-ilha")) e.remove();
    return b.outerHTML;
  });
  const png = await page.screenshot({ fullPage: true, animations: "disabled", caret: "hide" });
  return { png, dom };
}

const PELES = (process.env.PORTAO_PELES ?? "xcom,vidro").split(","), LARGURAS = (process.env.PORTAO_LARGURAS ?? "1920,390").split(",").map(Number);
for (const pele of PELES) for (const largura of LARGURAS) for (const [nome, rota, save, tamer] of TELAS) {
  test(`portao ${nome} ${pele} ${largura}`, async ({ page }) => {
    test.setTimeout(240_000);
    mkdirSync(OUT, { recursive: true });
    await page.setViewportSize({ width: largura, height: largura >= 1900 ? 950 : 844 });
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(e.message));
    const b = await capturar(page, BASE, rota, save, tamer ?? { versao: 1, log: [] }, pele);
    const r = await capturar(page, RAMO, rota, save, tamer ?? { versao: 1, log: [] }, pele);
    const id = `${nome}_${pele}_${largura}`;
    writeFileSync(`${OUT}/${id}_base.png`, b.png); writeFileSync(`${OUT}/${id}_ramo.png`, r.png);
    writeFileSync(`${OUT}/${id}_base.html`, b.dom); writeFileSync(`${OUT}/${id}_ramo.html`, r.dom);
    expect(erros).toEqual([]);
  });
}
