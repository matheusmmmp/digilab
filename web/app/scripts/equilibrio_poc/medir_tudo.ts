/* LUTA_POC, LP5 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secoes 4.1 e 4.5): roda os grupos da bancada em ate 4 processos (a V3-D8) e, no fim, o
   resumo das metas. Um grupo que falha para tudo (codigo 1), sem resumo.
   uso (em web/app): node scripts/equilibrio_poc/medir_tudo.ts --faixa calibracao --fase lp5_0 [--candidato v21] [--processos 4] */
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { argumento } from "./comum.ts";
import { GRUPOS } from "./bancada.ts";

const faixa = argumento("faixa"), fase = argumento("fase"), candidato = argumento("candidato", "v21"), processos = Number(argumento("processos", "4"));
if (!(Number.isInteger(processos) && processos >= 1 && processos <= 4)) throw new Error(`medir_tudo: de 1 a 4 processos (V3-D8), nao ${processos}`);
/* os grupos mais caros primeiro, para os 4 processos acabarem juntos */
const ORDEM = ["formas_adolescente", "formas_adulto", "formas_mega", "treino", "torneios", "sparring", "lideres", "formas_crianca", "estagio", "vida"];
if (ORDEM.length !== GRUPOS.length || !GRUPOS.every(g => ORDEM.includes(g))) throw new Error("medir_tudo: a ordem nao tem todos os grupos");
const aqui = (f: string) => fileURLToPath(new URL(f, import.meta.url));
const rodar = (script: string, args: string[]): Promise<void> => new Promise((ok, falha) => {
  const p = spawn(process.execPath, [aqui(script), ...args], { stdio: "inherit" });
  p.on("exit", cod => cod === 0 ? ok() : falha(new Error(`${script} ${args.join(" ")}: codigo ${cod}`)));
});
const t0 = Date.now(), fila = [...ORDEM];
await Promise.all(Array.from({ length: processos }, async () => {
  for (let g = fila.shift(); g; g = fila.shift()) await rodar("bancada.ts", ["--grupo", g, "--faixa", faixa, "--fase", fase, "--candidato", candidato]);
}));
console.log(`medir_tudo: ${ORDEM.length} grupos em ${((Date.now() - t0) / 1000).toFixed(0)} s`);
await rodar("resumo_metas.ts", ["--faixa", faixa, "--fase", fase]);
