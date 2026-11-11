/* LUTA_POC, LP5-0 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.1): a prova de reproducao. A bancada (o CANDIDATO_V21, o lutar() e o npc() de
   comum.ts) refaz o scripts/medicoes/lp4_gazimon.json campo a campo, com as sementes de teste da LP4 (os pets 11, 21, 23, 101 e 202, as lutas
   0 a 199) e o TREINO_8 dela. Sementes ja usadas, fora das faixas: nao contam como calibracao. Falha alto (codigo 1) num campo diferente.
   uso (em web/app): node scripts/equilibrio_poc/reproducao_lp4.ts -> scripts/medicoes/equilibrio_poc/lp5_0/reproducao_lp4.json */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { CIT, DUR_EVO, Motor, condicaoDe, statsDoPet, type Stats } from "../../motor/index.ts";
import { CANDIDATO_V21, commitAtual, lutar, npc, statsLuta } from "./comum.ts";

const c = CANDIDATO_V21, GAZIMON = "npc_tier1_brutamontes";
const lp4 = JSON.parse(readFileSync(fileURLToPath(new URL("../medicoes/lp4_gazimon.json", import.meta.url)), "utf-8"));
const LUTAS: number = lp4.lutas_por_pet, TREINO_8: Stats = lp4.treino_8;
if (Object.values(TREINO_8).reduce((a, b) => a + b, 0) !== CIT.tipico.crianca) throw new Error("o treino tipico do Rookie mudou");
const rival = { forma: GAZIMON, stats: npc(c, GAZIMON) };
const taxaDe = (a: { forma: string; stats: ReturnType<typeof statsLuta> }): number => {
  let v = 0;
  for (let s = 0; s < LUTAS; s++) if (lutar("campo", s, a, rival).vencedor === "a") v++;
  return v / LUTAS;
};
const pets = (lp4.pets as { semente: number }[]).map(({ semente }) => {
  const m = new Motor(semente);
  m.avancar(DUR_EVO.bebe + 30);
  const cond = condicaoDe(m.e.saude), forma = m.formaLutaPoc;
  const sem = { forma, stats: statsLuta(c, statsDoPet(m.forma, m.carater(), null), m.forma.est, cond) };
  const com = { forma, stats: statsLuta(c, statsDoPet(m.forma, m.carater(), TREINO_8), m.forma.est, cond) };
  return { semente, especie: m.especie, forma, hp_sem_treino: sem.stats.hp, vitoria_sem_treino: taxaDe(sem), hp_com_8: com.stats.hp, vitoria_com_8: taxaDe(com) };
});
const refeito = { tarefa: lp4.tarefa, mapa: "campo", rival: GAZIMON, hp_rival: rival.stats.hp, lutas_por_pet: LUTAS, treino_8: TREINO_8, pets };
const diferencas: string[] = [];
const comparar = (a: unknown, b: unknown, onde: string): void => {
  if (a !== null && typeof a === "object" && b !== null && typeof b === "object") {
    const ks = new Set([...Object.keys(a), ...Object.keys(b)]);
    for (const k of ks) comparar((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k], `${onde}.${k}`);
  } else if (a !== b) diferencas.push(`${onde}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);
};
comparar(lp4, refeito, "lp4_gazimon");
const dir = fileURLToPath(new URL("../medicoes/equilibrio_poc/lp5_0/", import.meta.url));
mkdirSync(dir, { recursive: true });
writeFileSync(dir + "reproducao_lp4.json", JSON.stringify({ tarefa: "LUTA_POC, LP5-0, a prova de reproducao", commit: commitAtual(), igual: diferencas.length === 0, diferencas, refeito }, null, 1) + "\n");
if (diferencas.length) { console.error("a bancada NAO refaz o lp4_gazimon.json:\n" + diferencas.join("\n")); process.exit(1); }
console.log(`a bancada refaz o lp4_gazimon.json campo a campo (${pets.length} pets, ${2 * LUTAS * pets.length} lutas)`);
