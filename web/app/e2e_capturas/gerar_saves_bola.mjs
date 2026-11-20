// Os saves da captura de referencia da bola na ilha (docs/TAREFA_V3_ITENS_3D.md, secao 7): um pet da versao de hoje, cujo dono usou o
// Alimentar a cada 2 h desde o nascimento, e no fim pos a bola 2 celulas a leste do pet (o lugar "perto do pet" da tela, como o
// gerar_save_mundo.mjs da racao). Dois saves: o dia (13:00) e a noite (22:30). A captura para o relogio do jogo, entao o pet e a bola ficam
// parados onde o save termina. A semente 4242 e a do save das capturas da HABITAT_OBJETOS. Nenhum numero novo do jogo; os horarios sao da
// captura.
// uso (em web/app): node --experimental-strip-types e2e_capturas/gerar_saves_bola.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CMU_MVP, VERSAO_PET, Motor, deslocar } = M;
const SEMENTE = 4242, PASSO_DONO = 120, HORAS = { dia: 480 + 300, noite: 480 + 870 };

function vida(ate) {
  const m = new Motor(SEMENTE, VERSAO_PET);
  while (m.e.tick < ate) {
    if ((m.e.tick - 480) % PASSO_DONO === 0 && !m.morte) m.observar("alimentar");
    m.avancar(Math.min(15, ate - m.e.tick));
  }
  if (m.morte) throw new Error("o pet morreu antes do tick " + ate);
  const [x, y] = deslocar(m.mundo.pet[0], m.mundo.pet[1], 0, CMU_MVP.perto_max_celulas * CMU_MVP.sub, CMU_MVP);
  m.deixarBola(x, y);
  return m;
}
const saves = {};
for (const [nome, ate] of Object.entries(HORAS)) {
  const m = vida(ate);
  const r = Motor.reproduzir(m.semente, m.log, VERSAO_PET);
  if (r.assinatura() !== m.assinatura()) throw new Error("o replay do save " + nome + " nao bate");
  saves[nome] = { semente: m.semente, log: m.log, versao: m.versao };
  console.log(nome, "tick", m.e.tick, "eventos", m.log.length, M.nomeForma(m.forma), "pet", m.mundo.pet, "bola", m.mundo.bola);
}
writeFileSync(fileURLToPath(new URL("./saves_bola.json", import.meta.url)), JSON.stringify(saves) + "\n");
