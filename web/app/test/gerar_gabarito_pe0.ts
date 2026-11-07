// Grava o gabarito das lutas de hoje (PE0 da ponte da luta, docs/TAREFA_V3_PONTE_LUTA.md, 3.5): test/gabaritos/ponte_luta_pe0.json.gz.
// Rodar em Node (o V8 do navegador difere no ultimo bit de Math.exp): node web/app/test/gerar_gabarito_pe0.ts
import { writeFileSync } from "node:fs";
import { gzipSync } from "node:zlib";
import { fileURLToPath } from "node:url";
import { DIAS, SEMENTES, VARIANTES, gravar, todasAsVidas } from "./ponte_luta_pe0.ts";

const g = { versao: 1, nota: "PE0: as lutas de hoje do v16, do v17 com o modular, do v17 com o A e do v17 com um cb entre duas lutas; sha256 das assinaturas",
  dias: DIAS, sementes: SEMENTES, variantes: VARIANTES, vidas: todasAsVidas().map(gravar) };
const destino = fileURLToPath(new URL("./gabaritos/ponte_luta_pe0.json.gz", import.meta.url));
writeFileSync(destino, gzipSync(Buffer.from(JSON.stringify(g)), { level: 9, mtime: 0 } as never));
console.log("gravado", destino, g.vidas.length, "vidas,", g.vidas.reduce((n, v) => n + v.lutas.length, 0), "lutas");
