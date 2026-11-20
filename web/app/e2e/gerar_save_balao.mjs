// Save do e2e do balao da fala (balao_fala.spec.ts): um pet v-atual de vida de verdade que termina com um MOTIVO registrado (o unico que o
// Motor grava hoje na vida e o do treino forcado: `treinar` com a fadiga acima do limiar), para o balao ("cena-fala") existir e o painel
// "Por que ele disse isso" ter causa. O dono atencioso dos Cenarios cuida; o treino insiste (sem respeitar a pausa) ate o motivo sair.
// O save e so {semente, log, versao}, igual aos outros; o replay e conferido aqui. Grava e2e/save_balao.json.
// uso (em web/app): npx tsx e2e/gerar_save_balao.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ACOES_DONO_JOGO_V11, CD, CTR, TPD, Motor, criarDono, criarRng, hashSemente } = M;
const EXERCICIOS = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"];

function comMotivo(semente) {
  const m = new Motor(semente), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  m.liberar(1);
  const dias = 3, passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0, ex = 0;
  for (let p = 0; p < passos && !m.morte; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    for (const a of dono.decidir(v, rng)) if (ACOES_DONO_JOGO_V11.includes(a)) { m.observar(a); gasto++; }
    if (m.estagioAtual === "bebe") continue;
    /* treina sempre que o motor deixa (o intervalo), sem olhar a fadiga: ate o treino forcado gravar o motivo */
    if (m.treino.podeTocar(m.e.tick)) {
      try { m.treinar(EXERCICIOS[ex++ % EXERCICIOS.length]); } catch { /* recusado (dormindo etc.): tenta no proximo passo */ }
      if (m.motivo && m.motivo.origem === "vida" && m.motivo.fatores.length && !m.motivo.exploracao) return m;
    }
  }
  return null;
}
for (let s = 7100; s < 7200; s++) {
  const m = comMotivo(s);
  if (!m) continue;
  const x = Motor.reproduzir(m.semente, m.log);
  if (x.assinatura() !== m.assinatura()) throw new Error("o replay nao confere");
  if (!x.motivo) throw new Error("o replay nao refaz o motivo");
  writeFileSync(fileURLToPath(new URL("./save_balao.json", import.meta.url)), JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao }) + "\n");
  console.log("balao", s, m.log.length, "eventos", m.estagioAtual, JSON.stringify(m.motivo));
  process.exit(0);
}
throw new Error("nenhuma semente deu um motivo registrado");
