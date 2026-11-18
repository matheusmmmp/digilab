// Grava o gabarito da Fabrica de hoje (MMO6, antes das sementes vindas de fora): test/gabaritos/mmo6_fabrica_hoje.json.
// Rodar em Node (o V8 do navegador difere no ultimo bit de Math.exp): node web/app/test/gerar_gabarito_mmo6.ts
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { LUTAS_MAX, TENTATIVAS_HOJE, todasHoje } from "./mmo6_fabrica_hoje.ts";

const g = { versao: 1, nota: "MMO6: a Fabrica de hoje (sementeFabrica(n), as sementes de dentro), gravada antes das sementes vindas de fora; poc = sha256 do resultado da luta",
  lutasMax: LUTAS_MAX, tentativas: TENTATIVAS_HOJE, vidas: todasHoje() };
const destino = fileURLToPath(new URL("./gabaritos/mmo6_fabrica_hoje.json", import.meta.url));
writeFileSync(destino, JSON.stringify(g, null, 1) + "\n");
console.log("gravado", destino, g.vidas.length, "tentativas,", g.vidas.reduce((a, v) => a + v.lutas.length, 0), "lutas");
