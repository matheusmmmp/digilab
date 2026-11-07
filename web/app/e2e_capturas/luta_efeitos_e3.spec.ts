/* As capturas e os quadros do GIF da E3, a telegrafia e o chao (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 4): o Gabumon (cirro, o Rookie
   v18 do GIF do empurrao) contra o Vigia (Zudomon, limo), que prepara o pesado e acerta, enquanto o Gabumon carrega, em 390 e 1280 px, nas peles vidro e militar (xcom). Para cada uma, o palco parado em: a elipse do preparo no meio do fechamento (data-preparos-meio),
   o pesado pronto (data-telegrafias-prontas), a onda de choque do acerto (data-ondas), a marca no piso depois (data-marcas, sem onda) e a
   elipse do carregar (data-carregar-meio), cada uma na primeira vez que a luta a mostra (a lista do que saiu fica no .txt). Em cada largura
   e pele, grava tambem os quadros da tela para o GIF, da primeira elipse ate 2,5 s depois do primeiro acerto do pesado.
   Roda com: npx playwright test -c e2e_capturas/luta_efeitos_e3.config.ts, com DIGILAB_CAPTURAS_E3=<pasta>. Nao e referencia das capturas. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_E3 ?? "";
const CHAVE = "digilab-web-v21-sprites";
const GABUMON = { semente: 101, versao: 18, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
/* os rivais (DIGILAB_E3_RIVAIS troca a lista, para procurar uma luta que mostre tudo); o nome da captura e gabumon_<rival> */
const PARES = (process.env.DIGILAB_E3_RIVAIS ?? "vigia").split(",").map(r => ({ nome: "gabumon_" + r, rival: r }));
const SO_1280 = !!process.env.DIGILAB_E3_SO_1280;

async function abrirLuta(page: Page, pele: string, rival: string): Promise<void> {
  /* o save e semeado por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele por cima ao fechar) */
  await page.goto("/motor/index.ts");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(GABUMON), JSON.stringify(TAMER)] as const);
  await page.goto(`/?pele=${pele}&clipes_up=1#/lutar/arena`);
  await expect(page.locator(".lutar-grande")).toBeVisible();
  await page.evaluate(async (k) => { (await import("/src/luta.ts" as string)).escolherRival(k); }, rival);
  /* o LUTA do app, para parar a luta no quadro certo (a mesma pausa do botao da tela) */
  await page.evaluate(async () => { (window as unknown as { __luta: unknown }).__luta = (await import("/src/luta.ts" as string)).LUTA; });
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
}
type Campo = "preparosMeio" | "telegrafiasProntas" | "ondas" | "marcas" | "carregarMeio";
/** espera o canvas mostrar o primeiro dos campos pedidos e para a luta no mesmo quadro; as marcas so contam sem onda (a onda ja passou).
    Devolve o campo, ou null se a luta acabou antes */
async function pararQuando(page: Page, campos: Campo[]): Promise<Campo | null> {
  const h = await page.waitForFunction((cs) => {
    const cv = document.querySelector(".arena-cv") as HTMLElement | null;
    if (!location.hash.endsWith("/luta")) return "fim";
    if (!cv) return false;
    const c = cs.find(c => Number(cv.dataset[c] ?? 0) > 0 && !(c === "marcas" && Number(cv.dataset.ondas ?? 0) > 0));
    if (!c) return false;
    (window as unknown as { __luta: { pausado: boolean } }).__luta.pausado = true; return c;
  }, campos, { timeout: 150_000, polling: "raf" }).catch(() => null);
  const v = await h?.jsonValue();
  return v && v !== "fim" ? v as Campo : null;
}
const seguir = (page: Page) => page.evaluate(() => { (window as unknown as { __luta: { pausado: boolean } }).__luta.pausado = false; });

test.describe("capturas da E3", () => {
  test.skip(!PASTA, "so com DIGILAB_CAPTURAS_E3");
  for (const par of PARES) for (const pele of SO_1280 ? ["vidro"] : ["vidro", "xcom"]) for (const [w, h] of (SO_1280 ? [[1280, 720]] : [[390, 844], [1280, 720]]) as [number, number][]) test(`${par.nome}: ${pele} ${w}`, async ({ page }) => {
    test.setTimeout(400_000);
    mkdirSync(PASTA, { recursive: true });
    await page.setViewportSize({ width: w, height: h });
    await abrirLuta(page, pele, par.rival);
    const nome = `luta_e3_${par.nome}_${w}_${pele === "xcom" ? "militar" : "vidro"}`, feitas: string[] = [];
    const ROTULO: Record<Campo, string> = { preparosMeio: "preparo", telegrafiasProntas: "pronto", ondas: "onda", marcas: "marca", carregarMeio: "carregar" };
    const faltam = Object.keys(ROTULO) as Campo[];
    while (faltam.length) {
      const c = await pararQuando(page, faltam); if (!c) break;
      await page.waitForTimeout(150);
      await page.screenshot({ path: join(PASTA, `${nome}_${ROTULO[c]}.png`) }); feitas.push(ROTULO[c]);
      faltam.splice(faltam.indexOf(c), 1);
      await seguir(page);
    }
    writeFileSync(join(PASTA, `${nome}.txt`), feitas.join("\n") + "\n");
    expect(feitas.length).toBeGreaterThan(0);
  });
  for (const par of PARES) for (const pele of SO_1280 ? ["vidro"] : ["vidro", "xcom"]) for (const [w, h] of (SO_1280 ? [[1280, 720]] : [[390, 844], [1280, 720]]) as [number, number][]) test(`${par.nome}: quadros do GIF ${pele} ${w}`, async ({ page }) => {
    test.setTimeout(300_000);
    mkdirSync(PASTA, { recursive: true });
    await page.setViewportSize({ width: w, height: h });
    await abrirLuta(page, pele, par.rival);
    const nome = `luta_e3_${par.nome}_${w}_${pele === "xcom" ? "militar" : "vidro"}_gif`, cdp = await page.context().newCDPSession(page);
    let n = 0, gravando = false;
    cdp.on("Page.screencastFrame", async (ev: { data: string; sessionId: number }) => {
      if (gravando) writeFileSync(join(PASTA, `${nome}_f${String(n++).padStart(4, "0")}.jpg`), Buffer.from(ev.data, "base64"));
      await cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId }).catch(() => undefined);
    });
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, everyNthFrame: 1 });
    await page.waitForFunction(() => Number((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset.telegrafias ?? 0) > 0, null, { timeout: 120_000, polling: "raf" });
    gravando = true;
    await page.waitForFunction(() => Number((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset.ondas ?? 0) > 0, null, { timeout: 120_000, polling: "raf" }).catch(() => undefined);
    await page.waitForTimeout(2500);
    gravando = false;
    await cdp.send("Page.stopScreencast");
    expect(n).toBeGreaterThan(20);
  });
});
