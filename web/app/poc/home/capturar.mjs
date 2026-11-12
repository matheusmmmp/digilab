/* As capturas da página de entrada (POC) nas seis larguras pedidas: a página inteira e a primeira dobra, com o movimento reduzido (tudo no
   lugar, pets no quadro 0). Precisa do Vite da POC no modo dev (o atlas dos pets só é servido nele) e grava em
   D:\Trab\digilab\capturas_ux_home_poc\ (fora do git); as de 390 e 1440 vão para docs/pranchas/ux-pagina-inicial/capturas/ à mão.

     npm run poc                                       # em outro terminal
     node poc/home/capturar.mjs [pasta]                # DIGILAB_URL_HOME muda o endereço (padrão http://127.0.0.1:5173/home/) */
import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const URL_HOME = process.env.DIGILAB_URL_HOME ?? "http://127.0.0.1:5173/home/";
const PASTA = process.argv[2] ?? "D:/Trab/digilab/capturas_ux_home_poc";
const TELAS = [[360, 780], [390, 844], [768, 1024], [1024, 768], [1440, 900], [1920, 1080]];
mkdirSync(PASTA, { recursive: true });

const nav = await chromium.launch({ channel: "chrome" });
for (const [w, h] of TELAS) {
  const ctx = await nav.newContext({ viewport: { width: w, height: h }, reducedMotion: "reduce", deviceScaleFactor: 1 });
  const pg = await ctx.newPage();
  await pg.goto(URL_HOME, { waitUntil: "networkidle" });
  await pg.evaluate(() => document.fonts.ready);
  /* desce a página para as imagens com loading="lazy" carregarem, e volta ao topo */
  await pg.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += innerHeight / 2) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); });
  await pg.waitForLoadState("networkidle");
  await pg.waitForTimeout(300);
  const larg = await pg.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
  await pg.screenshot({ path: join(PASTA, `home_${w}_dobra.jpg`), quality: 85 });
  await pg.screenshot({ path: join(PASTA, `home_${w}.jpg`), fullPage: true, quality: 82 });
  console.log(`${w} x ${h}: scrollWidth ${larg[0]} / innerWidth ${larg[1]}`);
  await ctx.close();
}
await nav.close();
