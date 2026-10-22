// Saves da aba Treinar (docs/TAREFA_V2_TREINO.md): um pet v11 no Rookie, cuidado por um dono atencioso, que treina em seguida, com 10 min
// de intervalo, ate a fadiga passar do ponto de cada save:
//   save_treino_pausa.json: 3 sessoes, fadiga entre 40 (pede pausa) e 60;
//   save_treino_forcar.json: 4 sessoes, fadiga acima de 60 (so Forcar).
// O registro termina num avanco de tempo de 1 min. Conferido aqui: refeito do registro e com mais 10 min de jogo (o que o relogio da captura
// anda), ele continua acordado, no Rookie, com a fadiga na faixa do save. uso (em web/app): node e2e/gerar_save_treino.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ACOES_DONO_JOGO_V11, CD, CTR, TPD, VERSAO_PET, Motor, criarDono, criarRng, hashSemente } = M;
const EX = ["levantar_pedra", "corrida", "alvo", "esquiva"];

/** o Rookie a 3 h do comeco do estagio, cuidado; depois `n` treinos seguidos (null se ele dormir no meio) */
function treinado(semente, n) {
  const m = new Motor(semente, VERSAO_PET), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  const dias = 1, passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0;
  for (let p = 0; p < passos; p++) {
    if (m.estagioAtual === "crianca" && m.e.tick - m.evolucoes[0].tick >= 180) break;
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    /* o dono atencioso do Cenarios, so com as acoes que os pets v11 tem */
    for (const a of dono.decidir(v, rng)) if (ACOES_DONO_JOGO_V11.includes(a)) { m.observar(a); gasto++; }
  }
  if (m.estagioAtual !== "crianca") return null;
  for (let k = 0; k < n; k++) {
    if (m.acao === "dormir") return null;
    m.treinar(EX[k]);
    if (k < n - 1) m.avancar(CTR.intervalo);
  }
  m.avancar(1);                                                  /* o registro termina num avanco de tempo */
  return m;
}
const naFaixa = (m, lo, hi) => m.treino.fadiga >= lo && m.treino.fadiga < hi && m.acao !== "dormir" && m.estagioAtual === "crianca";
function procura(n, lo, hi, arquivo) {
  for (let s = 6400; s < 6500; s++) {
    const m = treinado(s, n);
    if (!m || m.morte || m.log[m.log.length - 1][1] !== "t" || !naFaixa(m, lo, hi)) continue;
    const x = Motor.reproduzir(m.semente, m.log, VERSAO_PET);
    if (!naFaixa(x, lo, hi)) continue;
    x.avancar(10);
    if (!naFaixa(x, lo, hi)) continue;
    writeFileSync(fileURLToPath(new URL(`./${arquivo}`, import.meta.url)), JSON.stringify({ semente: m.semente, log: m.log, versao: m.versao }) + "\n");
    console.log(arquivo, "semente", s, "eventos", m.log.length, M.nomeForma(m.forma), "fadiga", m.treino.fadiga.toFixed(1), "sobrecarga", m.treino.sobrecarga);
    return;
  }
  throw new Error("nenhuma semente deu o save " + arquivo);
}
procura(3, CTR.limiarPausa, CTR.limiteForcar, "save_treino_pausa.json");
procura(4, CTR.limiteForcar, 101, "save_treino_forcar.json");
