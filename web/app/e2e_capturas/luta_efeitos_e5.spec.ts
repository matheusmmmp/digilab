/* As capturas e os quadros dos GIFs da E5, o nocaute e a camera (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 4): o Gabumon v18 (o das capturas
   da E3 e da E4), em 390 e 1280 px, nas peles vidro e militar (xcom).
   - A luta inteira ate o nocaute: contra o Monochromon (o agressivo, o rival que ja vem escolhido), os quadros da tela do comeco ate a tela do
     resultado (o GIF).
   - As fotos da folha, na mesma luta: o palco parado no comeco (os dois longe), na primeira vez com o zoom maior, no pedaco branco e no
     vermelho da barra, no escuro antes do "K.O.", no "K.O." ainda grande e no "K.O." no tamanho final; o .txt diz o zoom e a escala de cada.
   - A camera: contra o Zudomon (o vigia), DIGILAB_E5_ZOOM_S segundos de quadros desde o comeco (longe e perto, o empurrao).
   Roda com: npx playwright test -c e2e_capturas/luta_efeitos_e5.config.ts, com DIGILAB_CAPTURAS_E5=<pasta>. Nao e referencia das capturas. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_E5 ?? "";
const CHAVE = "digilab-web-v21-sprites";
const GABUMON = { semente: 101, versao: 18, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
const ZOOM_S = Number(process.env.DIGILAB_E5_ZOOM_S ?? 12);
const PELES = (process.env.DIGILAB_E5_PELES ?? "vidro,xcom").split(",");
const LARGURAS = ([[390, 844], [1280, 720]] as [number, number][]).filter(([w]) => !process.env.DIGILAB_E5_LARGURA || String(w) === process.env.DIGILAB_E5_LARGURA);
const nomePele = (p: string) => p === "xcom" ? "militar" : "vidro";

async function semear(page: Page): Promise<void> {
  /* o save e semeado por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele por cima ao fechar) */
  await page.goto("/motor/index.ts");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(GABUMON), JSON.stringify(TAMER)] as const);
}
/** abre a luta contra o rival; pausada: comeca parada (para a gravacao comecar no primeiro quadro) */
async function abrirLuta(page: Page, pele: string, rival: string, pausada = false): Promise<void> {
  await semear(page);
  await page.goto(`/?pele=${pele}&clipes_up=1#/lutar/arena`);
  await expect(page.locator(".lutar-grande")).toBeVisible();
  await page.evaluate(async (k) => { const L = await import("/src/luta.ts" as string); L.escolherRival(k); (window as unknown as { __luta: unknown }).__luta = L.LUTA; }, rival);
  await page.locator(".lutar-grande").click();
  if (pausada) await page.evaluate(() => { (window as unknown as { __luta: { pausado: boolean } }).__luta.pausado = true; });
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
  await page.waitForFunction(() => !!document.querySelector(".arena-cv") && (document.querySelector(".arena-cv") as HTMLElement).dataset.esc !== undefined, null, { timeout: 60_000 });
}
const pausar = (page: Page, p: boolean) => page.evaluate((v) => { (window as unknown as { __luta: { pausado: boolean } }).__luta.pausado = v; }, p);
/** grava os quadros da tela (o screencast do Chrome) enquanto corre(): de 30 em 30 por segundo, sem um screenshot por quadro */
async function gravar(page: Page, nome: string, corre: () => Promise<void>): Promise<number> {
  const cdp = await page.context().newCDPSession(page);
  let n = 0, gravando = true;
  cdp.on("Page.screencastFrame", async (ev: { data: string; sessionId: number }) => {
    if (gravando) writeFileSync(join(PASTA, `${nome}_f${String(n++).padStart(4, "0")}.jpg`), Buffer.from(ev.data, "base64"));
    await cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId }).catch(() => undefined);
  });
  await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, everyNthFrame: 1 });
  await corre();
  gravando = false;
  await cdp.send("Page.stopScreencast");
  return n;
}

/** os momentos da folha: o nome e a condicao no palco (avaliada a cada quadro) */
const MOMENTOS = [
  ["1_longe", "true"],
  ["2_perto", "zoomMax"],
  ["3_barra_branca", "branco"],
  ["4_barra_vermelha", "vermelho"],
  ["5_escuro", "escuro"],
  ["6_ko_grande", "koGrande"],
  ["7_ko_final", "koFinal"],
] as const;
/** espera o primeiro momento da lista e para a luta no mesmo quadro; devolve o momento e o que o palco dizia; null se a luta acabou antes */
async function pararNo(page: Page, conds: string[]): Promise<{ c: string; esc: string; zoom: string; ko: string } | null> {
  const h = await page.waitForFunction((cs) => {
    const cv = document.querySelector(".arena-cv") as HTMLElement | null, w = window as unknown as { __luta: { pausado: boolean } };
    if (!location.hash.endsWith("/luta")) return "fim";
    if (!cv) return false;
    const d = cv.dataset, ko = Number(d.ko || 0), z = Number(d.zoom ?? 1);
    const ver: Record<string, boolean> = {
      true: true,
      /* a camera perto (zoom de 1,3 ou mais, fora da passagem de um nivel ao outro) */
      zoomMax: z >= 1.3 && d.passagem !== "1",
      branco: !!document.querySelector(".hud-vida-atraso--branco"),
      vermelho: !!document.querySelector(".hud-vida-atraso:not(.hud-vida-atraso--branco)") && !d.ko,
      escuro: Number(d.escuro) > 0 && !ko,
      koGrande: ko > 0 && d.koPronto !== "1",
      koFinal: ko > 0 && d.koPronto === "1",
    };
    const c = cs.find(x => ver[x]); if (!c) return false;
    w.__luta.pausado = true;
    return JSON.stringify({ c, esc: d.esc, zoom: d.zoom, ko: d.ko });
  }, conds, { timeout: 150_000, polling: "raf" }).catch(() => null);
  const v = await h?.jsonValue();
  return v && v !== "fim" ? JSON.parse(v as string) : null;
}

test.describe("capturas da E5", () => {
  test.skip(!PASTA, "so com DIGILAB_CAPTURAS_E5");

  for (const pele of PELES) for (const [w, h] of LARGURAS) {
    test(`luta inteira ate o nocaute: ${pele} ${w}`, async ({ page }) => {
      test.setTimeout(300_000);
      mkdirSync(PASTA, { recursive: true });
      await page.setViewportSize({ width: w, height: h });
      await abrirLuta(page, pele, "agressivo", true);
      const nome = `luta_e5_nocaute_${w}_${nomePele(pele)}_gif`;
      const n = await gravar(page, nome, async () => {
        await pausar(page, false);
        /* ate a luta acabar (a tela do resultado abre na mesma rota) e mais um pouco do resultado */
        await page.waitForFunction(() => !(window as unknown as { __luta: { lutando: boolean } }).__luta.lutando, null, { timeout: 200_000, polling: 100 });
        await page.waitForTimeout(800);
      });
      expect(n).toBeGreaterThan(40);
    });

    test(`folha do nocaute: ${pele} ${w}`, async ({ page }) => {
      test.setTimeout(300_000);
      mkdirSync(PASTA, { recursive: true });
      await page.setViewportSize({ width: w, height: h });
      await abrirLuta(page, pele, "agressivo", true);
      await page.waitForTimeout(400);
      const nome = `luta_e5_folha_${w}_${nomePele(pele)}`, feitas: string[] = [], faltam: string[] = MOMENTOS.map(m => m[1]);
      while (faltam.length) {
        const r = await pararNo(page, faltam); if (!r) break;
        await page.waitForTimeout(120);
        const m = MOMENTOS.find(x => x[1] === r.c)!;
        await page.screenshot({ path: join(PASTA, `${nome}_${m[0]}.png`) });
        feitas.push(`${m[0]}: esc ${r.esc}, zoom ${r.zoom}${r.ko ? `, K.O. ${r.ko} px` : ""}`);
        faltam.splice(faltam.indexOf(r.c), 1);
        /* os momentos sao em ordem: o que passou sem foto nao volta */
        while (faltam.length && MOMENTOS.findIndex(x => x[1] === faltam[0]) < MOMENTOS.findIndex(x => x[1] === r.c)) faltam.shift();
        await pausar(page, false);
      }
      writeFileSync(join(PASTA, `${nome}.txt`), feitas.join("\n") + "\n" + (faltam.length ? `nao saiu: ${faltam.join(" ")}\n` : ""));
      expect(feitas.length).toBeGreaterThan(3);
    });

    test(`a camera, longe e perto: ${pele} ${w}`, async ({ page }) => {
      test.setTimeout(300_000);
      mkdirSync(PASTA, { recursive: true });
      await page.setViewportSize({ width: w, height: h });
      await abrirLuta(page, pele, "vigia", true);
      const nome = `luta_e5_camera_vigia_${w}_${nomePele(pele)}_gif`, zooms: string[] = [];
      const n = await gravar(page, nome, async () => {
        await pausar(page, false);
        const t0 = Date.now();
        while (Date.now() - t0 < ZOOM_S * 1000) {
          const z = await page.locator(".arena-cv").evaluate(c => `${(c as HTMLElement).dataset.esc}/${(c as HTMLElement).dataset.zoom}`).catch(() => "");
          if (z && zooms[zooms.length - 1] !== z) zooms.push(z);
          await page.waitForTimeout(100);
        }
      });
      writeFileSync(join(PASTA, `${nome}.txt`), `escala/zoom vistos, em ordem: ${zooms.join(" ")}\n`);
      expect(n).toBeGreaterThan(40);
    });
  }
});
