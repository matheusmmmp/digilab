// O save das capturas do saco de pancada na ilha (docs/TAREFA_V3_ITENS_3D.md, secao 12): um pet da versao de hoje, cujo dono usou o
// Alimentar a cada 2 h desde o nascimento, ate o primeiro tick de dia (das 9 h as 17 h) ja no Rookie, acordado e com o treino liberado.
// A semente 4242 e a do save da bola. Nenhum numero novo do jogo; o horario e da captura.
// uso (em web/app): node --experimental-strip-types e2e_capturas/gerar_saves_saco.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { TPD, VERSAO_PET, Motor } = M;
const SEMENTE = 4242, PASSO_DONO = 120, DIA = [540, 1020];

const m = new Motor(SEMENTE, VERSAO_PET);
const hora = () => m.e.tick % TPD;
while (!(m.estagioAtual === "crianca" && hora() >= DIA[0] && hora() < DIA[1] && m.acao !== "dormir" && m.treino.podeTocar(m.e.tick))) {
  if (m.morte) throw new Error("o pet morreu no tick " + m.e.tick);
  if (m.e.tick > 20 * TPD) throw new Error("nao achei um Rookie acordado de dia em 20 dias");
  if ((m.e.tick - 480) % PASSO_DONO === 0) m.observar("alimentar");
  m.avancar(15);
}
const r = Motor.reproduzir(m.semente, m.log, VERSAO_PET);
if (r.assinatura() !== m.assinatura()) throw new Error("o replay do save nao bate");
console.log("tick", m.e.tick, "hora", hora(), "eventos", m.log.length, M.nomeForma(m.forma), "pet", m.mundo.pet);
writeFileSync(fileURLToPath(new URL("./saves_saco.json", import.meta.url)), JSON.stringify({ dia: { semente: m.semente, log: m.log, versao: m.versao } }) + "\n");
