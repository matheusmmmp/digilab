/* O gabarito dos objetos da grade da ilha de hoje (docs/TAREFA_V3_MUNDO_ENFEITES.md, gate E-G0), gravado num commit proprio antes dos
   enfeites: os objetos de cada layout do motor, item a item. O teste test/ilha_enfeites.test.ts confere que a grade continua dando os
   mesmos. uso (em web/app): node --experimental-strip-types scripts/gabarito_ilha_objetos.ts */
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";

const g: Record<string, unknown> = {};
for (const cm of [CMU_MVP, CMU]) g[cm.layout.nome] = ilhaDe(cm).objetos;
writeFileSync(fileURLToPath(new URL("../test/gabaritos/ilha_objetos.json", import.meta.url)), JSON.stringify(g) + "\n");
console.log("GABARITO", Object.entries(g).map(([k, v]) => `${k}: ${(v as unknown[]).length}`).join(", "));
