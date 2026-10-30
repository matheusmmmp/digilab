// Save do teste ponta a ponta da Liga dos Lideres (Fronteira, medalhas parte 4a, docs/DESIGN_FRONTEIRA.md): um pet v13 Mega, treinado
// ate o teto, que conhece as 6 medalhas do Tamer (o registro comeca com o "u" das 6, como um pet novo de um Tamer que ja as tem). A vida
// e de verdade (o dono atencioso dos Cenarios, treino em rodizio em cada estagio, lutas de treino contra o aleatorio, lesao tratada),
// entao o app a reproduz. O registro termina num avanco de tempo: o relogio do app so estica esse avanco e o tamanho do registro (que
// entra na semente da luta) nao muda. Conferido aqui, com a escala ligada como no app: a tentativa do botao Desafiar a Liga (semente
// hashSemente("luta", semente, tamanho do registro)) vence as 6 lutas em qualquer ponto das proximas 5 h de jogo.
// uso (em web/app): npx tsx e2e/gerar_save_liga.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CAT, CD, CMG, CTR, TPD, Motor, RIVAL_LIGA, criarDono, criarRng, hashSemente } = M;
M.ligarEscala(true);
const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"];

function treinarSePuder(m, ex) {
  if (m.estagioAtual === "bebe" || !m.treino.podeTocar(m.e.tick) || m.treino.fadiga + CTR.fadigaSessao >= CTR.limiarPausa) return ex;
  try { m.treinar(EX[ex % EX.length]); return ex + 1; } catch { return ex; }
}
/** a vida: dono atencioso (orcamento de 16 acoes por dia), treino sempre que der e as lutas de treino do Champion e do Ultimate */
function megaTreinado(semente, dias = 5) {
  const m = new Motor(semente), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  m.liberar(M.MEDALHAS_LIGA);
  const passos = Math.round(dias * TPD / CD.passo), orc = Math.round(CD.porDia * dias);
  let gasto = 0, ex = 0, k = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    if (m.morte) return null;
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, rng);
    if (m.lesionadoDesde !== null) acoes.unshift("tratar_lesao");
    for (const a of acoes) if (M.ACOES_DONO_JOGO_V11.includes(a)) { m.observar(a); gasto++; }
    ex = treinarSePuder(m, ex);
    if ((m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) || (m.estagioAtual === "adulto" && m.lutas.lutas < 12)) {
      m.lutar("aleatorio", hashSemente("sparring", semente, k++));
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    }
    if (m.estagioAtual === "mega" && m.treino.total >= CMG.tetoVida) break;
  }
  if (m.estagioAtual !== "mega" || m.morte) return null;
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  m.avancar(CD.passo);                                       /* o registro termina num avanco de tempo */
  return m;
}
function venceSempre(m) {
  const x = Motor.reproduzir(m.semente, m.log);
  if (x.assinatura() !== m.assinatura()) throw new Error("o replay do save nao bate");
  for (let o = 0; o <= 300; o += 5) {
    if (o) x.avancar(5);
    if (x.log.length !== m.log.length) throw new Error("o avanco nao juntou com o ultimo");
    const serie = x.montarLuta(RIVAL_LIGA, hashSemente("luta", x.semente, x.log.length)).serie;
    if (serie.length !== M.LIGA.length || serie[serie.length - 1].pontosA !== 1) return false;
  }
  return true;
}
for (let s = 9100; s < 9400; s++) {
  const m = megaTreinado(s);
  if (!m) { console.log("semente", s, "nao chegou a Mega"); continue; }
  const ok = m.log[m.log.length - 1][1] === "t" && venceSempre(m);
  console.log("semente", s, M.nomeForma(m.forma), M.NOME_ARQ[m.forma.adulta], "treino", m.treino.total, ok ? "VENCE" : "nao vence sempre");
  if (!ok) continue;
  const save = { semente: m.semente, log: m.log, versao: m.versao };
  writeFileSync(fileURLToPath(new URL("./save_liga.json", import.meta.url)), JSON.stringify(save) + "\n");
  console.log("gravado: semente", s, "eventos", m.log.length);
  process.exit(0);
}
throw new Error("nenhuma semente deu um Mega que vence a Liga em todas as horas");
