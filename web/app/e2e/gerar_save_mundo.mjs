// Save do e2e do mundo no jogo (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2; E2E-COMIDA): um pet v12 cujo dono usou o botao Alimentar (a
// racao no comedouro, a reserva temporaria) a cada 2 h desde o nascimento, parado pouco antes de uma refeicao. O cerebro do momento (o A v11, MV-2) vai pouco a comida: nas sementes
// 6500 a 6519, uma ou duas refeicoes em dois dias, o primeiro no comeco do Rookie. O save fica num ponto em que a racao posta "perto do
// pet" (o lugar nomeado da tela: 2 celulas a leste, src/telas/pet/vistaMundo.ts), com o relogio do app andando de 0 a 60 min de jogo, e
// a que o pet come em ate ESPERA min de jogo, com a fome do motor caindo (a saciedade `e.fome` sobe). O registro termina num avanco de
// tempo. Nenhum numero novo do jogo: os do motor (CMU_MVP); ESPERA, PASSO_DONO e a faixa de pontos sao do teste.
// uso (em web/app): node --experimental-strip-types e2e/gerar_save_mundo.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CMU_MVP, VERSAO_PET, Motor, deslocar } = M;
if (VERSAO_PET !== 12) throw new Error("o save do mundo e de pets v12; a versao de hoje e " + VERSAO_PET);
const PASSO_DONO = 120, ESPERA = 240, OFFSETS = [0, 10, 20, 30, 40, 50, 60];

/** o lugar "perto do pet" da tela: 2 celulas (perto_max_celulas) para leste (a direcao 0), dentro do mapa */
const perto = m => deslocar(m.mundo.pet[0], m.mundo.pet[1], 0, CMU_MVP.perto_max_celulas * CMU_MVP.sub, CMU_MVP);

/** a vida do dono que usa o Alimentar (a racao no comedouro) a cada PASSO_DONO min, ate o tick `ate` (um avanco no fim) */
function vida(semente, ate) {
  const m = new Motor(semente, VERSAO_PET);
  while (m.e.tick < ate) {
    if ((m.e.tick - 480) % PASSO_DONO === 0 && !m.morte) m.observar("alimentar");
    m.avancar(Math.min(15, ate - m.e.tick));
  }
  return m;
}
/** com o relogio do app em `o` min, a racao posta perto do pet e a que ele come em ate ESPERA min, com a saciedade subindo */
function come(m, o) {
  const x = Motor.reproduzir(m.semente, m.log, VERSAO_PET);
  if (o) x.avancar(o);
  if (x.morte) return false;
  const antes = x.e.fome;
  x.deixarComida("racao", ...perto(x));
  const id = Math.max(...x.mundo.comidas.keys());
  for (let t = 0; t < ESPERA; t++) {
    x.avancar(1);
    const c = x.mundo.consumos.find(r => r.id === id);
    if (c) return c.situacao === "madura" && x.e.fome > antes;
    if (x.mundo.consumos.some(r => r.tick > m.e.tick + o)) return false;      /* comeu outra antes */
  }
  return false;
}
for (let s = 6500; s < 6600; s++) {
  const toda = vida(s, 480 + 2 * 1440), t1 = toda.mundo.consumos[0]?.tick;
  if (!t1) continue;
  for (let ate = t1 - 180; ate <= t1 - 30; ate += 15) {
    if (ate <= 480) continue;
    const m = vida(s, ate);
    if (m.morte || m.log[m.log.length - 1][1] !== "t" || m.mundo.consumos.length) continue;
    if (!OFFSETS.every(o => come(m, o))) continue;
    writeFileSync(fileURLToPath(new URL("./save_mundo.json", import.meta.url)), JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao }) + "\n");
    console.log("semente", s, "tick", m.e.tick, "eventos", m.log.length, M.nomeForma(m.forma), "fome", m.e.fome.toFixed(3), "pet", m.mundo.pet, "comidas", m.mundo.comidas.size);
    process.exit(0);
  }
}
throw new Error("nenhuma semente deu um pet v12 que come a racao posta perto dele");
