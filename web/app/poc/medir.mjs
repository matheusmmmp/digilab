// As medidas do WORLD-POC-01a que rodam no Node (docs/TAREFA_V2_WORLD_POC_01.md, etapa E4), só descritivas:
//   M5  o tempo de refazer pelo log 1 "dia" de sala (1.440 ticks, a mediana de 5), e o hash, igual em todas as repetições;
//   M6  o tamanho do build da página (web/dist_poc/, de `npm run poc:build`), cru e em gzip.
// Grava artifacts_v2_world_poc/node.json. O tempo é o desta máquina; não é paridade nem pesquisa.
//
//   npm run poc:build && npm run poc:medir
import { gzipSync } from "node:zlib";
import { mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { cpus } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { Simulacao, reproduzir } from "./mundo3d/simulacao.ts";

const DIA = 1440, REPETICOES = 5, SEMENTE = 101;
const DIST = fileURLToPath(new URL("../../dist_poc/", import.meta.url));
const SAIDA = fileURLToPath(new URL("../../../artifacts_v2_world_poc/", import.meta.url));

const vida = new Simulacao(SEMENTE);
vida.avancar(DIA);
const tempos = [], hashes = new Set();
for (let i = 0; i < REPETICOES; i++) {
  const t0 = performance.now();
  const r = reproduzir(SEMENTE, vida.log);
  tempos.push(performance.now() - t0);
  hashes.add(r.hash());
}
if (hashes.size !== 1 || !hashes.has(vida.hash())) throw new Error("o replay nao refez a vida");
tempos.sort((a, b) => a - b);

const arquivos = [];
const andar = d => { for (const n of readdirSync(d)) { const c = join(d, n); statSync(c).isDirectory() ? andar(c) : arquivos.push(c); } };
andar(DIST);
const tamanhos = arquivos.sort().map(f => {
  const b = readFileSync(f);
  return { arquivo: f.slice(DIST.length).replaceAll("\\", "/"), bytes: b.length, gzip: gzipSync(b, { level: 9 }).length };
});

const saida = {
  M5_replay_node: { semente: SEMENTE, ticks: DIA, decisoes: vida.registros.length, eventos: vida.log.length, hash: vida.hash(),
    repeticoes: REPETICOES, mediana_ms: +tempos[Math.floor(REPETICOES / 2)].toFixed(2), tempos_ms: tempos.map(t => +t.toFixed(2)),
    node: process.version, cpu: cpus()[0]?.model ?? "?" },
  M6_build: { arquivos: tamanhos, total_bytes: tamanhos.reduce((a, t) => a + t.bytes, 0), total_gzip: tamanhos.reduce((a, t) => a + t.gzip, 0) },
};
mkdirSync(SAIDA, { recursive: true });
writeFileSync(join(SAIDA, "node.json"), JSON.stringify(saida, null, 1) + "\n");
console.log(JSON.stringify(saida, null, 1));
