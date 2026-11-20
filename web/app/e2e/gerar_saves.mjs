// Saves do teste ponta a ponta (Etapa 5): um pet no Champion, de vida de verdade, que os testes de fluxo usam como "um pet qualquer".
// Desde o descarte 6 (COMBATE-TR, etapa R2b) e um pet v13, o unico que abre: o dono atencioso dos Cenarios (so as acoes do dono dos v11 em
// diante), treino em rodizio e o "u" da medalha que a passagem para o Champion pede, logo no comeco. Os saves v1, v2 e v3 de antes saem
// (os pets de antes nao abrem mais). uso (em web/app): node e2e/gerar_saves.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ACOES_DONO_JOGO_V11, CD, CTR, TPD, Motor, criarDono, criarRng, hashSemente, nomeForma } = M;
const EXERCICIOS = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"];

function champion(semente) {
  const m = new Motor(semente), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  m.liberar(1);
  const dias = 2, passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0, ex = 0;
  for (let p = 0; p < passos && !m.morte; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    for (const a of dono.decidir(v, rng)) if (ACOES_DONO_JOGO_V11.includes(a)) { m.observar(a); gasto++; }
    /* o Champion pronto: descansado, acordado e sem chamado (antes do treino do passo, que sobe a fadiga) */
    if (m.estagioAtual === "adolescente" && m.treino.fadiga < 20 && !m.chamadosAbertos().length && !m.e.dormindo) return m;
    if (m.estagioAtual === "crianca" && m.treino.podeTocar(m.e.tick) && m.treino.fadiga + CTR.fadigaSessao < CTR.limiarPausa) {
      try { m.treinar(EXERCICIOS[ex++ % EXERCICIOS.length]); } catch { /* o motor recusou (ex.: dormindo): tenta no proximo passo */ }
    }
  }
  return null;
}
for (let s = 7000; s < 7100; s++) {
  const m = champion(s);
  if (!m) continue;
  const x = Motor.reproduzir(m.semente, m.log);
  if (x.assinatura() !== m.assinatura()) throw new Error("o replay nao confere");
  const saves = { champion: { semente: m.semente, log: m.log, versao: m.versao } };
  writeFileSync(fileURLToPath(new URL("./saves.json", import.meta.url)), JSON.stringify(saves) + "\n");
  console.log("champion", s, m.log.length, "eventos", nomeForma(m.forma));
  process.exit(0);
}
throw new Error("nenhuma semente deu um Champion");
