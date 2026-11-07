// Grava o gabarito das vidas de hoje (DC3d da CONVERSA_PET, antes do porte da `fala_unidades`): test/gabaritos/dc3d_vidas_hoje.json.
// Rodar em Node (o V8 do navegador difere no ultimo bit de Math.exp): node web/app/test/gerar_gabarito_dc3d.ts
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { DIAS_HOJE, SEMENTES_HOJE, VARIANTES_HOJE, todasHoje } from "./dc3d_hoje.ts";

const g = { versao: 1, nota: "DC3d: as vidas de hoje (v13 a v19 e o pet de teste v16), gravadas antes do porte da fala_unidades; sha256",
  dias: DIAS_HOJE, sementes: SEMENTES_HOJE, variantes: VARIANTES_HOJE, vidas: todasHoje() };
const destino = fileURLToPath(new URL("./gabaritos/dc3d_vidas_hoje.json", import.meta.url));
writeFileSync(destino, JSON.stringify(g, null, 1) + "\n");
console.log("gravado", destino, g.vidas.length, "vidas");
