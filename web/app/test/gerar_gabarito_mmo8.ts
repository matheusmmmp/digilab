// Grava o gabarito dos registros do Tamer de hoje (MMO8, antes do evento "reset"): test/gabaritos/mmo8_tamer_hoje.json.
// Rodar em Node: node web/app/test/gerar_gabarito_mmo8.ts
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { jogarHoje } from "./mmo8_tamer_hoje.ts";

const g = { versao: 1, nota: "MMO8: os registros do Tamer de hoje (o texto gravado e o estado lido), gravados antes do evento reset e da versao 11", casos: jogarHoje() };
const destino = fileURLToPath(new URL("./gabaritos/mmo8_tamer_hoje.json", import.meta.url));
writeFileSync(destino, JSON.stringify(g, null, 1) + "\n");
console.log("gravado", destino, g.casos.length, "casos");
