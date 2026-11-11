// Os saves das capturas do kit medico e do coco na ilha (docs/TAREFA_V3_ITENS_3D.md, secao 13). O ponto de partida e o do saco
// (gerar_saves_saco.mjs): a semente 4242, o dono usa o Alimentar a cada 2 h, ate o Rookie acordado de dia. Dois saves:
//   - "coco": daqui, mais horas so com o Alimentar (sem o Limpar), ate a sujeira chegar a 3, de dia e acordado;
//   - "kit": daqui, lutas de treino contra o bot agressivo, a semente 1, 2, ..., ate a primeira derrota com lesao (o kit aparece
//     enquanto o pet esta lesionado).
// Nenhum numero novo do jogo; os horarios, o bot e a contagem sao da captura.
// uso (em web/app): node --experimental-strip-types e2e_capturas/gerar_saves_kit_coco.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { TPD, VERSAO_PET, Motor } = M;
const SEMENTE = 4242, PASSO_DONO = 120, DIA = [540, 1020], SUJEIRA = 3;

function rookie() {
  const m = new Motor(SEMENTE, VERSAO_PET);
  const hora = () => m.e.tick % TPD;
  while (!(m.estagioAtual === "crianca" && hora() >= DIA[0] && hora() < DIA[1] && m.acao !== "dormir" && m.treino.podeTocar(m.e.tick))) {
    if (m.morte) throw new Error("o pet morreu no tick " + m.e.tick);
    if ((m.e.tick - 480) % PASSO_DONO === 0) m.observar("alimentar");
    m.avancar(15);
  }
  return m;
}
const deDia = m => m.e.tick % TPD >= DIA[0] && m.e.tick % TPD < DIA[1] && m.acao !== "dormir";

const coco = rookie();
while (!(coco.e.sujeira >= SUJEIRA && deDia(coco))) {
  if (coco.morte) throw new Error("o pet do coco morreu no tick " + coco.e.tick);
  if (coco.e.tick > 30 * TPD) throw new Error("a sujeira nao chegou a " + SUJEIRA);
  if ((coco.e.tick - 480) % PASSO_DONO === 0) coco.observar("alimentar");
  coco.avancar(15);
}

const kit = rookie();
for (let s = 1; kit.lesionadoDesde === null; s++) {
  if (s > 200) throw new Error("nenhuma lesao em 200 lutas");
  /* a luta da POC (LUTA_POC, LP4): uma forma do estagio, no Campo de treino, ate a primeira lesao */
  const rv = kit.rivaisArenaPoc();
  kit.lutarPoc(rv[s % rv.length], s, "campo");
}

const saves = {};
for (const [nome, m] of Object.entries({ coco, kit })) {
  const r = Motor.reproduzir(m.semente, m.log, VERSAO_PET);
  if (r.assinatura() !== m.assinatura()) throw new Error("o replay do save " + nome + " nao bate");
  saves[nome] = { semente: m.semente, log: m.log, versao: m.versao };
  console.log(nome, "tick", m.e.tick, "eventos", m.log.length, "sujeira", m.e.sujeira, "lesionado", m.lesionadoDesde !== null, "acao", m.acao);
}
writeFileSync(fileURLToPath(new URL("./saves_kit_coco.json", import.meta.url)), JSON.stringify(saves) + "\n");
