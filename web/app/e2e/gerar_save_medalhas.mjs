// Save do teste ponta a ponta das medalhas (docs/DESIGN_MEDALHAS_ARENAS.md): um pet v6 no Rookie, treinado, com o tempo
// do Rookie ja cumprido (pronto para evoluir, esperando a 1a medalha). O registro termina num avanco de tempo, entao o
// relogio do app so estica esse avanco e o tamanho do registro (que entra na semente da luta) nao muda. Conferido aqui:
// a proxima luta contra o Gazimon (a do botao Desafiar, semente hashSemente("luta", semente, tamanho do registro)) e
// vitoria em qualquer ponto das proximas 5 h de jogo (o relogio do app anda enquanto o teste clica), com a escala ligada
// como no app. uso (em web/app): node e2e/gerar_save_medalhas.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CD, CTR, DUR_EVO, TPD, Motor, criarDono, criarRng, hashSemente } = M;
M.ligarEscala(true);
const GAZIMON = "npc_tier1_brutamontes", FIM_ROOKIE = DUR_EVO.bebe + DUR_EVO.crianca;
const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"];

/** dono atencioso (Cenarios) + treino em rodizio no Rookie, sem forcar, ate o fim do Rookie + 30 min */
function rookiePronto(semente) {
  const m = new Motor(semente, 6), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  const dias = (FIM_ROOKIE + 30) / TPD, passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0, ex = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    for (const a of dono.decidir(v, rng)) { m.observar(a); gasto++; }
    if (m.estagioAtual === "crianca" && m.treino.podeTocar(m.e.tick) && m.treino.fadiga + CTR.fadigaSessao < CTR.limiarPausa) {
      try { m.treinar(EX[ex++ % EX.length]); } catch { /* dormindo: tenta depois */ }
    }
  }
  m.avancar(CD.passo);                                        /* o registro termina num avanco de tempo */
  return m;
}
function venceSempre(m) {
  for (let o = 0; o <= 300; o += 5) {
    const x = Motor.reproduzir(m.semente, m.log, 6);
    if (o) x.avancar(o);
    if (x.log.length !== m.log.length) throw new Error("o avanco nao juntou com o ultimo");
    if (x.lutar(GAZIMON, hashSemente("luta", x.semente, x.log.length)).res.pontosA !== 1) return false;
  }
  return true;
}
for (let s = 6100; s < 6200; s++) {
  const m = rookiePronto(s);
  if (m.estagioAtual !== "crianca" || !m.esperandoMedalha() || m.log[m.log.length - 1][1] !== "t") continue;
  if (!venceSempre(m)) continue;
  const save = { semente: m.semente, log: m.log, versao: m.versao };
  writeFileSync(fileURLToPath(new URL("./save_medalhas.json", import.meta.url)), JSON.stringify(save) + "\n");
  console.log("semente", s, "eventos", m.log.length, M.nomeForma(m.forma), "treino", m.treino.total ?? "");
  process.exit(0);
}
throw new Error("nenhuma semente deu um Rookie que vence o Gazimon em todas as horas");
