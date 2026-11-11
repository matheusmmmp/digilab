// Save do e2e da E1 da mitologia (mitologia_e1.spec.ts; docs/TAREFA_V3_MITOLOGIA.md, secao 10): um pet da versao de hoje que o dono
// cuida, acaricia e faz brincar (a Amizade), e que numa noite o dono leva ate a pedra do macaco na mata (a pedra achada). O save e so
// {semente, log, versao}; o replay e conferido aqui. Grava e2e/save_mitologia_e1.json.
// uso (em web/app): npx tsx e2e/gerar_save_mitologia_e1.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CD, TPD, Motor, pedraAchadaDe, pedraEm, sinaisDe } = M;
const SEMENTE = 303;
const m = new Motor(SEMENTE);
const [px, py] = pedraEm();
let levou = false;
for (let p = 0; p < Math.round(3.3 * TPD / CD.passo); p++) {
  m.avancar(CD.passo);
  if (m.e.fome < .6) m.observar("alimentar");
  if (m.e.sujeira >= 2) m.observar("limpar");
  if (p % 3 === 0) m.observar("brincar");
  if (p % 4 === 0) m.observar("acariciar");
  const hora = m.e.tick % TPD;
  if (!levou && (hora >= 22 * 60 || hora < 7 * 60) && !m.e.dormindo) { m.levarPet(px, py); levou = true; }
}
const x = Motor.reproduzir(m.semente, m.log, m.versao);
if (x.assinatura() !== m.assinatura()) throw new Error("o replay nao confere");
const pedra = pedraAchadaDe(x);
if (pedra === null) throw new Error("a vida nao achou a pedra");
if (!sinaisDe(x).some(s => s.deus === "amizade")) throw new Error("a vida nao tem o sinal da Amizade");
writeFileSync(fileURLToPath(new URL("./save_mitologia_e1.json", import.meta.url)), JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao }) + "\n");
console.log("mitologia e1", SEMENTE, m.log.length, "eventos", "pedra no tick", pedra, "sinais", JSON.stringify(sinaisDe(x).map(s => [s.deus, s.tick])));
