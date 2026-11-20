/* LUTA_POC, LP5-1 (desvio D-LP5-1-4): o S1 pela regua da D-LP5-11 (o lado A so nas lutas com vencedor), por estagio e mapa, lido dos JSON
   das formas de uma medida inteira ja feita. So leitura: nenhuma luta nova.
   uso (em web/app): node scripts/equilibrio_poc/releitura_s1.ts --fase lp5_0 -> scripts/medicoes/equilibrio_poc/lp5_1/s1_releitura_<fase>.json */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { ESTAGIOS_LUTA, argumento, type Conta } from "./comum.ts";

const fase = argumento("fase"), dir = fileURLToPath(new URL(`../medicoes/equilibrio_poc/${fase}/calibracao/`, import.meta.url));
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const out: Record<string, unknown> = {};
let commit = "";
for (const e of ESTAGIOS_LUTA) {
  const j = JSON.parse(readFileSync(dir + `formas_${e}.json`, "utf-8")), P = j.dados.pares as Record<string, Record<string, Conta>>;
  commit = j.commit;
  out[e] = Object.fromEntries(Object.entries(P).map(([m, d]) => {
    let v = 0, n = 0, em = 0;
    for (const [k, c] of Object.entries(d)) { const [a, b] = k.split("|"); if (a !== b) continue; v += c.v; n += c.n - c.e; em += c.e; }
    if (!n) throw new Error(`releitura: o espelho do ${e} no ${m} so empatou`);
    return [m, { lado_a_com_vencedor: r3(v / n), lutas_com_vencedor: n, empates: em, fora_da_faixa: v / n < .45 || v / n > .55 }];
  }));
}
const saida = { tarefa: "LUTA_POC, LP5-1, o S1 relido pela D-LP5-11", fase, commit_da_medida: commit, estagios: out };
writeFileSync(fileURLToPath(new URL(`../medicoes/equilibrio_poc/lp5_1/s1_releitura_${fase}.json`, import.meta.url)), JSON.stringify(saida, null, 1) + "\n");
console.log(JSON.stringify(Object.fromEntries(Object.entries(out).map(([e, m]) => [e, Object.fromEntries(Object.entries(m as Record<string, { lado_a_com_vencedor: number }>).map(([k, x]) => [k, x.lado_a_com_vencedor]))]))));
