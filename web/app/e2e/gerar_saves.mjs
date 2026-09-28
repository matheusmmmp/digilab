// Saves do teste ponta a ponta (Etapa 5): um pet de cada versao no Champion, tirados das vidas dos gabaritos
// (prefixo do registro). O v1 vai no formato antigo, sem "versao". uso: node e2e/gerar_saves.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const G = fileURLToPath(new URL("../test/gabaritos/", import.meta.url));
function champion(arq) {
  const v = JSON.parse(readFileSync(G + arq, "utf8")).vidas[0], m = new M.Motor(v.semente, v.versao);
  for (let i = 0; i < v.log.length; i++) {
    m.aplicarEvento(v.log[i]);
    if (m.estagioAtual === "adolescente" && m.treino.fadiga < 20 && !m.chamadosAbertos().length)
      return { semente: v.semente, log: v.log.slice(0, i + 1), versao: v.versao, forma: M.nomeForma(m.forma) };
  }
  throw new Error("sem Champion em " + arq);
}
const saves = { v1: champion("vidas_v1_atencioso.json"), v2: champion("vidas_v2_incoerente.json"), v3: champion("vidas_v3_atencioso.json") };
delete saves.v1.versao;
for (const [k, s] of Object.entries(saves)) { console.log(k, s.semente, s.log.length, s.forma); delete s.forma; }
writeFileSync(fileURLToPath(new URL("./saves.json", import.meta.url)), JSON.stringify(saves) + "\n");
