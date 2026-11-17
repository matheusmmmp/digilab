/* MMO3: grava a vida de teste do envio (test/gabaritos/vida_101.json), o save {semente, log, versao} de uma vida roteirizada da MMO0
   (web/app/scripts/mmo0/vida.ts, a semente 101 com o DigiBrain modular). O roteiro passa pelo src/produto.ts do jogo, que chega ao React:
   por isso a vida é gravada aqui, com o node_modules do web/app instalado, e os testes (e o CI do servidor) só a leem.
     cd servidor_web && node scripts/gerar_vida_teste.ts */
import { writeFileSync } from "node:fs";
import { viver } from "../../web/app/scripts/mmo0/vida.ts";

const SEMENTE = 101;
const v = viver(SEMENTE, "modular");
const destino = new URL("../test/gabaritos/vida_101.json", import.meta.url);
writeFileSync(destino, JSON.stringify({ semente: v.semente, log: v.log, versao: v.versao }) + "\n");
console.log(`vida ${SEMENTE}: ${v.log.length} eventos, ${v.lutas.length} lutas, ${v.passos} passos, morreu: ${v.morreu}`);
