/* Mede o contraste de cada texto da página de entrada contra o que está de fato atrás dele (a foto do herói, o véu, a faixa azul).
   Como: com o movimento reduzido (tudo no lugar), uma captura da página inteira com TODO o texto transparente; para cada trecho de texto,
   os retângulos das linhas (Range.getClientRects) e, em cada pixel de fundo deles, o contraste WCAG 2 da cor do texto. Sai o pior pixel
   (min) e o 5º percentil (p5), por largura. Nenhuma dependência nova: o PNG é lido num canvas da própria página.

     npm run poc                                   # em outro terminal (porta 5173 do Vite da POC, ou DIGILAB_URL_HOME)
     node poc/home/medir_contraste.mjs [saida.json]

   O mínimo pedido é 4,5:1 (guia, seção 4.1, e a tarefa). */
import { chromium } from "@playwright/test";
import { writeFileSync } from "node:fs";

const URL_HOME = process.env.DIGILAB_URL_HOME ?? "http://127.0.0.1:5173/home/";
const LARGURAS = [360, 390, 768, 1024, 1440, 1920];
const saida = process.argv[2];

const nav = await chromium.launch({ channel: "chrome" });
const todas = {};
for (const w of LARGURAS) {
  const ctx = await nav.newContext({ viewport: { width: w, height: 900 }, reducedMotion: "reduce", deviceScaleFactor: 1 });
  const pg = await ctx.newPage();
  await pg.goto(URL_HOME, { waitUntil: "networkidle" });
  await pg.evaluate(() => document.fonts.ready);
  /* os trechos: cada nó de texto visível, com a cor do pai e os retângulos das linhas em coordenadas da página */
  const trechos = await pg.evaluate(() => {
    const r = [];
    const it = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = it.nextNode(); n; n = it.nextNode()) {
      const t = n.textContent.trim();
      const el = n.parentElement;
      if (!t || !el || el.closest(".cortina,.pular,noscript,.fixo")) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility === "hidden" || cs.display === "none" || Number(cs.opacity) === 0) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      const rets = [...rg.getClientRects()].filter(q => q.width > 1 && q.height > 1)
        /* recua 2 px em cima e embaixo: a caixa da linha encosta na borda de selos como o "exemplo" */
        .map(q => [q.left + scrollX, q.top + scrollY + 2, q.width, Math.max(1, q.height - 4)]);
      if (rets.length) r.push({ texto: t.slice(0, 40), cor: cs.color, tam: cs.fontSize, peso: cs.fontWeight, rets });
    }
    return r;
  });
  await pg.addStyleTag({ content: "*{color:transparent !important;text-shadow:none !important;caret-color:transparent !important}" });
  const png = (await pg.screenshot({ fullPage: true })).toString("base64");
  const res = await pg.evaluate(async ({ png, trechos }) => {
    const img = new Image(); img.src = "data:image/png;base64," + png; await img.decode();
    const c = document.createElement("canvas"); c.width = img.width; c.height = img.height;
    const g = c.getContext("2d", { willReadFrequently: true }); g.drawImage(img, 0, 0);
    const lin = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    const lum = (r, gg, b) => 0.2126 * lin(r) + 0.7152 * lin(gg) + 0.0722 * lin(b);
    const cont = (a, b) => (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    const pc = document.createElement("canvas").getContext("2d");
    return trechos.map(t => {
      pc.fillStyle = "#000"; pc.fillStyle = t.cor; pc.fillRect(0, 0, 1, 1);
      const [r, gg, b, a] = pc.getImageData(0, 0, 1, 1).data;
      const vals = [];
      for (const [x, y, w, h] of t.rets) {
        const x0 = Math.max(0, Math.floor(x)), y0 = Math.max(0, Math.floor(y));
        const ww = Math.min(c.width - x0, Math.ceil(w)), hh = Math.min(c.height - y0, Math.ceil(h));
        if (ww < 1 || hh < 1) continue;
        const d = g.getImageData(x0, y0, ww, hh).data;
        for (let i = 0; i < d.length; i += 4) {
          /* a cor do texto sobre o fundo daquele pixel (o alfa do texto, se houver) */
          const al = a / 255;
          const tr = r * al + d[i] * (1 - al), tg = gg * al + d[i + 1] * (1 - al), tb = b * al + d[i + 2] * (1 - al);
          vals.push(cont(lum(tr, tg, tb), lum(d[i], d[i + 1], d[i + 2])));
        }
      }
      vals.sort((p, q) => p - q);
      return { texto: t.texto, tam: t.tam, peso: t.peso, min: vals[0], p5: vals[Math.floor(vals.length * 0.05)] };
    }).filter(t => t.min !== undefined);
  }, { png, trechos });
  todas[w] = res;
  const ruins = res.filter(t => t.min < 4.5);
  const pior = res.reduce((p, q) => (q.min < p.min ? q : p));
  console.log(`${w} px: ${res.length} trechos; pior ${pior.min.toFixed(2)} ("${pior.texto}"); abaixo de 4,5: ${ruins.length}`);
  for (const t of ruins) console.log(`   ${t.min.toFixed(2)} (p5 ${t.p5.toFixed(2)})  ${t.tam} ${t.peso}  "${t.texto}"`);
  await ctx.close();
}
await nav.close();
if (saida) writeFileSync(saida, JSON.stringify(todas, null, 1));
