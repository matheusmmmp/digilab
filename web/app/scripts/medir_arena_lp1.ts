/* O custo de uma luta do nucleo novo no Node (docs/TAREFA_V3_LUTA_POC.md, LP1, item 4): a mesma ideia da medida da R0 da COMBATE_TR
   (scripts/medicoes/replay_tr.json no efb2ded: 1,19 ms por luta 1 contra 1), agora sobre motor/arena/ com a tabela do git. As lutas sao as
   do gabarito do CI (test/gabaritos/arena_poc_1x1.json: as 60 formas nos 8 mapas, stats genericos da POC), repetidas; o tempo e o de
   lutar() inteiro (montar e rodar ate o fim). So engenharia, nenhuma run de pesquisa.
     node scripts/medir_arena_lp1.ts     # grava scripts/medicoes/arena_custo_lp1.json */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { lutar, type IdCena, type Stats } from "../motor/arena/index.ts";

const REPETICOES = 5;
const gab = JSON.parse(readFileSync(new URL("../test/gabaritos/arena_poc_1x1.json", import.meta.url), "utf8")) as
  { stats: Stats; lutas: { cena: IdCena; a: string; b: string; semente: number }[] };
const entradas = gab.lutas.map(l => ({ cena: l.cena, semente: l.semente, a: { forma: l.a, stats: gab.stats }, b: { forma: l.b, stats: gab.stats } }));

/* aquecimento: uma volta inteira sem medir (o JIT) */
let passos = 0, segundos: number[] = [], semFim = 0;
for (const e of entradas) { const r = lutar(e); passos += r.passos; segundos.push(r.relogio / 1000); if (!r.fim) semFim++; }
const msPorLuta: number[] = [];
for (let k = 0; k < REPETICOES; k++) {
  const t = performance.now();
  for (const e of entradas) lutar(e);
  msPorLuta.push(+((performance.now() - t) / entradas.length).toFixed(3));
}
const ord = [...msPorLuta].sort((a, b) => a - b), mediana = ord[Math.floor(ord.length / 2)];
segundos.sort((a, b) => a - b);
const porCena: Record<string, number> = {};
for (const c of new Set(entradas.map(e => e.cena))) {
  const es = entradas.filter(e => e.cena === c), t = performance.now();
  for (const e of es) lutar(e);
  porCena[c] = +((performance.now() - t) / es.length).toFixed(3);
}
const saida = {
  gerado_por: "web/app/scripts/medir_arena_lp1.ts", commit: execSync("git rev-parse --short HEAD").toString().trim(), data: new Date().toISOString().slice(0, 10),
  maquina: { cpu: os.cpus()[0]?.model ?? "?", nucleos: os.cpus().length, plataforma: `${process.platform} ${os.release()}` },
  node: process.version, lutas: entradas.length, repeticoes: REPETICOES,
  passosMedio: Math.round(passos / entradas.length), segundosJogoMedio: +(segundos.reduce((a, b) => a + b, 0) / segundos.length).toFixed(1),
  segundosJogoP90: segundos[Math.floor(segundos.length * 0.9)], semFim,
  msPorLuta: mediana, msPorLutaRepeticoes: msPorLuta, usPorPasso: +(1000 * mediana / (passos / entradas.length)).toFixed(3), msPorLutaPorMapa: porCena,
  vida1000Lutas_s: +(mediana * 1000 / 1000).toFixed(2),
  nota: "um processo, sem paralelismo; a R0 da COMBATE_TR mediu 1,185 ms por luta 1x1 (29,6 s de jogo) na POC do efb2ded com os status do Digimon UP; aqui os stats sao os genericos da POC, e as lutas sao mais curtas (segundosJogoMedio). O custo no celular segue SEM FONTE (a LP2 mede o replay)",
};
const DEST = fileURLToPath(new URL("./medicoes/", import.meta.url));
mkdirSync(DEST, { recursive: true });
writeFileSync(DEST + "arena_custo_lp1.json", JSON.stringify(saida, null, 1) + "\n");
console.log(`arena_custo_lp1.json: ${mediana} ms por luta (${saida.segundosJogoMedio} s de jogo, ${saida.passosMedio} passos), ${saida.usPorPasso} us por passo`);
