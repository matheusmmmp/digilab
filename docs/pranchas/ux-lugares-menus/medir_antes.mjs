// le o texto visivel (rodar com o servidor da prancha em D:/Trab/digilab, porta 8765; node medir_antes.mjs <pasta>) e captura Crescer > Itens e Evolucao do jogo de hoje (build de v3-ux-a2), com o save "champion" das capturas
import { chromium } from "file:///D:/Trab/digilab/v3-ux-a2/web/app/node_modules/playwright/index.mjs";
import { readFileSync, writeFileSync } from "node:fs";
const SAVES = JSON.parse(readFileSync("D:/Trab/digilab/v3-ux-a2/web/app/e2e/saves.json", "utf8"));
const OUT = process.argv[2], B = "http://127.0.0.1:8765", CH = "digilab-web-v21-sprites";
const br = await chromium.launch({ channel: "chrome" }); const res = {};
for (const pele of ["xcom", "vidro"]) for (const [w, h] of (process.env.LARG==="390"?[[390,844]]:[[1920,950],[390,844]])) for (const aba of ["itens", "evolucao"]) {
  const pg = await br.newPage({ viewport: { width: w, height: h }, locale: "pt-BR" });
  await pg.goto(B + "/Assets/digilab_atlas_up.json");
  await pg.evaluate(([c, s]) => { localStorage.clear(); for (const [k, v] of [["-boas-vindas","1"],["-tamer",JSON.stringify({versao:1,log:[]})],["-descarte","5"],["-dicas-ligadas","0"],["-guardados","[]"]]) localStorage.setItem(c+k, v); localStorage.setItem(c, s); }, [CH, JSON.stringify(SAVES.champion)]);
  await pg.goto(`${B}/${process.env.DIST ?? "v3-ux-a2"}/web/dist/?pele=${pele}#/crescer/${aba}`);
  await pg.waitForSelector(".painel-tela__folha"); await pg.waitForTimeout(2500);
  const t = await pg.evaluate(() => { const f = document.querySelector(".painel-tela__folha"); const hx = f.closest(".painel-tela") ?? f;
    return { folha: f.innerText, painel: hx.innerText }; });
  const n = pele === "xcom" ? "militar" : "vidro";
  await pg.screenshot({ path: `${OUT}/antes_${aba}_${w}_${n}.png` });
  const pal = s => (s.match(/[\p{L}\p{N}]+(?:[-'’][\p{L}\p{N}]+)*/gu) ?? []).length;
  res[`${aba}_${w}_${n}`] = { palavras_painel: pal(t.painel), palavras_folha: pal(t.folha), texto: t.painel };
  await pg.close();
}
writeFileSync(`${OUT}/antes_palavras.json`, JSON.stringify(res, null, 1)); await br.close();
for (const [k, v] of Object.entries(res)) console.log(k, v.palavras_painel, v.palavras_folha);
