/* EQUILIBRIO_CUIDADO, E0: roda as 30 vidas do retrato (2 versoes x 3 donos x 5 sementes da calibracao; secao 5 do plano) num processo so
   (o teto da maquina e 4; uma vida leva segundos) e grava um JSON por vida em scripts/medicoes/equilibrio_cuidado_e0/. Depois, o
   e0_resumo.ts junta as tabelas.

     node scripts/equilibrio_cuidado/e0_rodar.ts */
import { mkdirSync, writeFileSync } from "node:fs";
import { DONOS, PASTA_E0, SEMENTES_E0, VERSOES, vida } from "./e0.ts";

mkdirSync(PASTA_E0, { recursive: true });
for (const versao of VERSOES) for (const dono of DONOS) for (const s of SEMENTES_E0) {
  const t0 = Date.now(), r = vida(versao, dono, s);
  writeFileSync(`${PASTA_E0}${versao}_${dono}_${s}.json`, JSON.stringify(r, null, 1) + "\n");
  console.log(`${versao} ${dono} ${s}: ${((Date.now() - t0) / 1000).toFixed(1)} s`);
}
