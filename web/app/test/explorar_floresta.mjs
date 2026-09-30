// Exploracao da lista do lider da Floresta (medalhas parte 2), SO nas sementes de calibracao (as de validacao ficam para
// test/calibrar_arenas.mjs --validar): 5 variantes da fase 2 x troca no turno 5, 10 ou 20 x final carregar/defender, fatores
// 1,0..2,0, 6 lutas por semente (as 4 linhas do Champion, 4 especies, sem treino e com 22). A primeira versao (v0, com o
// pesado e "oponente preparando -> golpe rapido" na fase 2) nao fechava as metas; a escolhida e a de maior folga (v3, turno 10,
// carregar). Saida: artifacts_campanha/arenas/floresta_variantes.json.
// uso (em web/app): node test/explorar_floresta.mjs
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";
const { ADOL_V21, CESC, CV, CV21D, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, NPC, STATS, Cd, Rg } = M;
const R = CV21D; M.ligarEscala(true);
const SEM = [3101, 3202, 3303, 3404, 3505], n = 6;
const PREP = Cd("oponente_preparando"), D0 = Cd("distancia_eh", 0), D1 = Cd("distancia_eh", 1), D2 = Cd("distancia_eh", 2);
const GA = g => Cd("guts_proprio_acima", g), FQ = a => Cd("oponente_frequente", a);
const V = t => { const T = Cd("turno_execucao", t); return {
  v0: [Rg([T, PREP], "golpe_rapido"), Rg([T, D2], "avancar"), Rg([T, D1], "avancar"), Rg([T, GA(40)], "preparar_pesado"), Rg([T, GA(20)], "golpe_rapido"), Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(GA(20), "disparo")],
  v1: [Rg([T, D2], "avancar"), Rg([T, D1], "avancar"), Rg([T, GA(40)], "preparar_pesado"), Rg([T, GA(20)], "golpe_rapido"), Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(GA(20), "disparo")],
  v2: [Rg([T, PREP], "golpe_rapido"), Rg([T, D2], "avancar"), Rg([T, D1], "avancar"), Rg([T, GA(20)], "golpe_rapido"), Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(GA(20), "disparo")],
  v3: [Rg([T, D2], "avancar"), Rg([T, D1], "avancar"), Rg([T, GA(20)], "golpe_rapido"), Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(GA(20), "disparo")],
  v4: [Rg([T, PREP], "esquivar"), Rg([T, D2], "avancar"), Rg([T, D1], "avancar"), Rg([T, GA(40)], "preparar_pesado"), Rg([T, GA(20)], "golpe_rapido"), Rg([PREP, D0], "esquivar"), Rg(D0, "recuar"), Rg(GA(20), "disparo")],
}; };
const prim = l => FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l);
const pet = (l, e, nv) => ({ nome: `${l}${nv}${e}`, estilo: { nome: l, gambits: ADOL_V21[l], eps: CV.eps },
  cond: M.perfilDe({ esp: e, est: "adolescente", ramo: "sereno", linha: l }, M.caraterCanonico(prim(l)), 1, nv ? Object.fromEntries(STATS.map(k => [k, nv / 6])) : null, true) });
function med(regras, final, fator, total) {
  const B = { nome: "Y", estilo: { nome: "y", gambits: { regras, final }, eps: CESC.epsNpc }, cond: M.perfilNPC(total, "adulto", M.escalaDe("adolescente", 0) * fator) };
  const por = {};
  for (const l of LINHAS) por[l] = [0, 22].map(nv => { let s = 0, t = 0; for (const e of ESPECIES) for (const se of SEM) for (let k = 0; k < n; k++) { s += M.jogarV2(pet(l, e, nv), B, M.hashSemente("x", se, e, l, nv, k), R).pontosA; t++; } return s / t; });
  const sem = LINHAS.reduce((a, l) => a + por[l][0], 0) / 4, com = LINHAS.reduce((a, l) => a + por[l][1], 0) / 4, pior = Math.min(...LINHAS.map(l => por[l][1]));
  return { f: fator, sem: sem.toFixed(3), com: com.toFixed(3), pior: pior.toFixed(3), folga: Math.min(.3 - sem, com - .8, pior - .5).toFixed(3), por: LINHAS.map(l => por[l].map(x => x.toFixed(2)).join("/")).join(" ") };
}
const saida = [];
for (const t of [5, 10, 20]) for (const [nome, rg] of Object.entries(V(t))) for (const fin of ["carregar", "defender"]) {
  let best = null;
  for (let f = 1.0; f <= 2.01; f += .1) { const r = med(rg, fin, +f.toFixed(1), 90); if (!best || +r.folga > +best.folga) best = r; }
  console.log(t, nome, fin, JSON.stringify(best));
  saida.push({ turno: t, variante: nome, final: fin, melhor: best });
}
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/arenas/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + "floresta_variantes.json", JSON.stringify({ descricao: "variantes da lista do lider da Floresta, sementes de calibracao", sementes: SEM, n_por_semente: n,
  por: "linha: sem/com (22)", variantes: saida }, null, 1) + "\n");
