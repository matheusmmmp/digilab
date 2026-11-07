/* As capturas e os quadros do GIF da E2, os projeteis e os golpes por elemento (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 4): o Gabumon
   (cirro) contra o Vigia (Zudomon, limo) e o Agumon (brasa) contra o Gabumon (cirro), em 390 e 1280 px, nas peles vidro e militar (xcom).
   Para cada uma: o palco parado com o projetil no ar (o canvas expoe data-projeteis) e parado no estouro de um acerto (data-impactos). Em
   1280 px no vidro, grava tambem os quadros da tela (screencast do Chrome, ~30 por segundo) para o GIF, montado por fora.
   Roda com: npx playwright test -c e2e_capturas/luta_efeitos_e2.config.ts, com DIGILAB_CAPTURAS_E2=<pasta>. Nao e referencia das capturas. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_E2 ?? "";
const CHAVE = "digilab-web-v21-sprites";
/* o Gabumon: o Rookie v18 do GIF do empurrao (semente 101, sem atender os chamados: ramo arisco). O Agumon: a semente 102 com os chamados do
   bebe atendidos (ramo sereno), gravado em save_agumon_v18.json */
const GABUMON = { semente: 101, versao: 18, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const AGUMON = JSON.parse(readFileSync(new URL("./save_agumon_v18.json", import.meta.url), "utf-8"));
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
/* voo: o par tem disparo. Nas lutas do Gabumon contra o Vigia e do Agumon contra o Gabumon ninguem dispara (so golpes corpo a corpo: o que
   se ve e o estouro por elemento); o Tankmon (o bot atirador) dispara, e mostra o projetil */
const PARES = [{ nome: "gabumon_vigia", pet: GABUMON, rival: "vigia", voo: false }, { nome: "agumon_gabumon", pet: AGUMON, rival: GABUMON, voo: false },
  { nome: "gabumon_tankmon", pet: GABUMON, rival: "atirador", voo: true }] as const;

async function abrirLuta(page: Page, pele: string, pet: object, rival: string | object): Promise<void> {
  /* o save e semeado por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele por cima ao fechar) */
  await page.goto("/motor/index.ts");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(pet), JSON.stringify(TAMER)] as const);
  await page.goto(`/?pele=${pele}&clipes_up=1#/lutar/arena`);
  await expect(page.locator(".lutar-grande")).toBeVisible();
  if (typeof rival === "string") await page.evaluate(async (k) => { (await import("/src/luta.ts" as string)).escolherRival(k); }, rival);
  else {
    /* o rival fixo (o mesmo caminho dos Cenarios do Lab): os modulos do app, servidos pelo Vite, sao os mesmos que a tela usa */
    await page.evaluate(async (r) => {
      const L = await import("/src/luta.ts" as string), M = await import("/motor/index.ts" as string);
      L.LUTA.rivalFixo = { rival: M.Motor.reproduzir(r.semente, r.log, r.versao), dias: 1, tipo: "atencioso" };
      L.previa("arena");
    }, rival as { semente: number; log: unknown[]; versao: number });
  }
  /* o LUTA do app, para parar a luta no quadro certo (a mesma pausa do botao da tela) */
  await page.evaluate(async () => { (window as unknown as { __luta: unknown }).__luta = (await import("/src/luta.ts" as string)).LUTA; });
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
}
/** espera o canvas mostrar o que o campo pede (data-projeteis-meio, data-estouros-meio, data-rajadas ou data-impactos > 0) e para a luta no mesmo quadro */
const pararQuando = (page: Page, campo: "projeteisMeio" | "estourosMeio" | "rajadas" | "impactos") => page.waitForFunction((c) => {
  const cv = document.querySelector(".arena-cv") as HTMLElement | null;
  if (!cv || Number(cv.dataset[c] ?? 0) <= 0) return false;
  (window as unknown as { __luta: { pausado: boolean } }).__luta.pausado = true; return true;
}, campo, { timeout: 120_000, polling: "raf" });
const seguir = (page: Page) => page.evaluate(() => { (window as unknown as { __luta: { pausado: boolean } }).__luta.pausado = false; });

test.describe("capturas da E2", () => {
  test.skip(!PASTA, "so com DIGILAB_CAPTURAS_E2");
  /* paradas: o projetil no ar e o estouro de um acerto */
  for (const par of PARES) for (const pele of ["vidro", "xcom"]) for (const [w, h] of [[390, 844], [1280, 720]] as const) test(`${par.nome}: ${pele} ${w}`, async ({ page }) => {
    test.setTimeout(300_000);
    mkdirSync(PASTA, { recursive: true });
    await page.setViewportSize({ width: w, height: h });
    await abrirLuta(page, pele, par.pet, par.rival);
    const nome = `luta_e2_${par.nome}_${w}_${pele === "xcom" ? "militar" : "vidro"}`;
    if (par.voo) {
      await pararQuando(page, "projeteisMeio");
      await page.waitForTimeout(150);
      await page.screenshot({ path: join(PASTA, `${nome}_voo.png`) });
      await seguir(page);
      await page.waitForFunction(() => Number((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset.impactos ?? 0) === 0, null, { timeout: 120_000, polling: "raf" });
    } else {
      /* os golpes corpo a corpo: a rajada da boca de quem bate a frente do alvo */
      await pararQuando(page, "rajadas");
      await page.waitForTimeout(150);
      await page.screenshot({ path: join(PASTA, `${nome}_golpe.png`) });
      await seguir(page);
    }
    await pararQuando(page, "estourosMeio");
    await page.waitForTimeout(150);
    await page.screenshot({ path: join(PASTA, `${nome}_estouro.png`) });
  });
  /* o GIF: em 1280 px no vidro, a luta corre sem parar e o screencast grava ate 3 s depois do primeiro projetil (ou do primeiro acerto) */
  for (const par of PARES) test(`${par.nome}: quadros do GIF`, async ({ page }) => {
    test.setTimeout(300_000);
    mkdirSync(PASTA, { recursive: true });
    await page.setViewportSize({ width: 1280, height: 720 });
    await abrirLuta(page, "vidro", par.pet, par.rival);
    const nome = `luta_e2_${par.nome}_gif`, cdp = await page.context().newCDPSession(page);
    let n = 0;
    cdp.on("Page.screencastFrame", async (ev: { data: string; sessionId: number }) => {
      writeFileSync(join(PASTA, `${nome}_f${String(n++).padStart(4, "0")}.jpg`), Buffer.from(ev.data, "base64"));
      /* o ultimo quadro pode chegar com a pagina ja fechada: o ack dele nao importa */
      await cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId }).catch(() => undefined);
    });
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, everyNthFrame: 1 });
    await page.waitForFunction((c) => Number((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset[c] ?? 0) > 0, par.voo ? "projeteis" : "impactos", { timeout: 120_000, polling: "raf" });
    await page.waitForTimeout(3000);
    await cdp.send("Page.stopScreencast");
    expect(n).toBeGreaterThan(20);
  });
});
