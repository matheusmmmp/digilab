/* Regrava os arquivos dos robôs no build do jogo (web/app/public/), de uma fonte só (CN4 e PI-6):
     - o robots.txt, da lista de src/protecao/robots.ts;
     - o .well-known/tdmrep.json e o _headers do Cloudflare Pages (o aviso de mineração reservada), de src/protecao/tdmrep.ts.
     node scripts/gerar_robots.ts
   O teste test/protecao.test.ts reprova se algum arquivo e a fonte divergirem. O deploy/montar_site.sh leva os três para a raiz do site. */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { robotsDoJogo } from "../src/protecao/robots.ts";
import { headersDoPages, tdmrepJson } from "../src/protecao/tdmrep.ts";

const publico = (caminho: string): string => fileURLToPath(new URL("../../web/app/public/" + caminho, import.meta.url));
const saidas: [string, string][] = [["robots.txt", robotsDoJogo()], [".well-known/tdmrep.json", tdmrepJson()], ["_headers", headersDoPages()]];
for (const [caminho, texto] of saidas) {
  const destino = publico(caminho);
  mkdirSync(dirname(destino), { recursive: true });
  writeFileSync(destino, texto, "utf8");
  console.log(`gravado: ${destino}`);
}
