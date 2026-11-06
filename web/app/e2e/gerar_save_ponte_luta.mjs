// Saves do e2e da PE0 da ponte da luta (docs/TAREFA_V3_PONTE_LUTA.md, 3.5): o pet de teste v16, o v17 com o modular e o v17 com o A, cada um
// com a vida do dono da PE0 (test/ponte_luta_pe0.ts, semente 101) ate logo antes da primeira luta, mais as 6 medalhas (a Liga abre). O app
// reproduz o registro e o e2e manda lutar. uso (em web/app): node e2e/gerar_save_ponte_luta.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { Motor, MEDALHAS_LIGA, petDeTeste } from "../motor/index.ts";
import { viverComLutas } from "../test/ponte_luta_pe0.ts";

const SEMENTE = 101, saves = {};
// os tres da PE0 (a vida de hoje) e os tres com a marca "pl" da PE3 (a dor da luta no corpo e, com o modular, o episodio luta)
for (const [chave, variante, ponte] of [["v16", "v16", false], ["v17_modular", "v17_modular", false], ["v17_a", "v17_a", false],
  ["v16_ponte", "v16", true], ["v17_modular_ponte", "v17_modular", true], ["v17_a_ponte", "v17_a", true]]) {
  const vida = viverComLutas(variante, SEMENTE, undefined, ponte), i = vida.log.findIndex(ev => ev[1] === "l");
  if (i < 0) throw new Error("a vida nao lutou: " + variante);
  const m = variante === "v16" ? petDeTeste(SEMENTE) : new Motor(SEMENTE);
  for (const ev of vida.log.slice(0, i)) m.aplicarEvento(ev);
  if (m.estagioAtual === "bebe") throw new Error("ainda bebe: " + variante);
  if (m.medalhas < MEDALHAS_LIGA) m.liberar(MEDALHAS_LIGA);      // o aplicarEvento nao grava no registro: o "u" e o unico evento do m.log
  const log = [...vida.log.slice(0, i), ...m.log];
  const prova = Motor.reproduzir(SEMENTE, log, m.versao);
  if (prova.assinatura() !== m.assinatura()) throw new Error("o replay do save nao fecha: " + variante);
  saves[chave] = { semente: SEMENTE, versao: m.versao, log };
}
const destino = fileURLToPath(new URL("./save_ponte_luta.json", import.meta.url));
writeFileSync(destino, JSON.stringify(saves));
console.log("gravado", destino, Object.entries(saves).map(([k, s]) => `${k}: v${s.versao}, ${s.log.length} eventos`).join("; "));
