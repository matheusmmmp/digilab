/* Regrava o robots.txt do jogo (web/app/public/robots.txt) da lista de src/protecao/robots.ts (CN4).
     node scripts/gerar_robots.ts
   O teste test/protecao.test.ts reprova se o arquivo e a lista divergirem. */
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { robotsDoJogo } from "../src/protecao/robots.ts";

const destino = fileURLToPath(new URL("../../web/app/public/robots.txt", import.meta.url));
writeFileSync(destino, robotsDoJogo(), "utf8");
console.log(`gravado: ${destino}`);
