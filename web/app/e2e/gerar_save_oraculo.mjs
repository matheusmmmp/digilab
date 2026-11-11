// Save do e2e do oraculo (oraculo_mitologia.spec.ts; MITOLOGIA, E0, docs/TAREFA_V3_MITOLOGIA.md): um Rookie da versao de hoje que luta
// contra o Gazimon na Campina a cada 7 passos e perde ao menos uma vez muito abaixo da forca dele (a hybris), e brinca variado (a nuvem).
// A mesma vida do test/lendas.test.ts. O save e so {semente, log, versao}; o replay e conferido aqui. Grava e2e/save_oraculo.json.
// uso (em web/app): npx tsx e2e/gerar_save_oraculo.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CD, TPD, Motor, hashSemente, lendas } = M;
const SEMENTE = 101, DIAS = 1.2;
const m = new Motor(SEMENTE);
const passos = Math.round(DIAS * TPD / CD.passo);
for (let p = 0; p < passos; p++) {
  m.avancar(CD.passo);
  if (m.e.fome < .6) m.observar("alimentar");
  if (m.e.sujeira >= 2) m.observar("limpar");
  if (p % 3 === 0) m.observar("brincar");
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  if (m.estagioAtual === "crianca" && p % 7 === 0 && !m.morte) m.lutarPoc("npc_tier1_brutamontes", hashSemente("camp", SEMENTE, p), "campo");
}
const x = Motor.reproduzir(m.semente, m.log, m.versao);
if (x.assinatura() !== m.assinatura()) throw new Error("o replay nao confere");
const ev = lendas(x);
if (!ev.some(e => e.tipo === "hybris")) throw new Error("a vida nao tem hybris");
writeFileSync(fileURLToPath(new URL("./save_oraculo.json", import.meta.url)), JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao }) + "\n");
console.log("oraculo", SEMENTE, m.log.length, "eventos", m.estagioAtual, JSON.stringify(ev.map(e => [e.tipo, e.tick])));
