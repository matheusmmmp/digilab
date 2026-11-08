// A sonda e o save da noite da prancha ux-ilha-a (LEIA.md, "Refazer"): o pet da semente 6521 que decide comer longe da tigela. Uso, em web/app: node --experimental-strip-types e2e/_sonda_ilha_a.mjs 1446
import * as M from "../motor/index.ts";
import { writeFileSync } from "node:fs";
const { VERSAO_PET, Motor } = M;
const S = 6521, ATE = Number(process.argv[2] ?? 1466);
const m = new Motor(S, VERSAO_PET);
while (m.e.tick < ATE) { if ((m.e.tick - 480) % 120 === 0) m.observar("alimentar"); m.avancar(Math.min(15 - ((m.e.tick - 480) % 15 || 0) || 15, ATE - m.e.tick)); }
const x = Motor.reproduzir(S, m.log, VERSAO_PET);
for (let i = 0; i < 12; i++) { x.avancar(1); const d = x.digibrain()?.decisao; console.log(x.e.tick, x.acao, x.mundo.pet, x.mundo.comedouro, x.mundo.comidas.size, d && d.chances.map(c => c.acao + ":" + c.chance.toFixed(2)).join(" "), JSON.stringify(x.digibrain()?.aprendido)); }
console.log("forma", M.nomeForma(m.forma), "eventos", m.log.length, "fome", m.e.fome.toFixed(2));
writeFileSync("e2e/_save_ilha_a.json", JSON.stringify({ semente: S, log: m.log, versao: m.versao }));
