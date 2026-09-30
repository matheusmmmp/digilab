// Pets guardados do teste ponta a ponta do Salao (Fronteira, medalhas parte 4c, docs/DESIGN_FRONTEIRA.md): um Rookie, um Champion e um
// Ultimate v6 de vida de verdade (o dono atencioso dos Cenarios, treino em rodizio, lutas de treino contra o aleatorio, lesao tratada; o
// registro comeca com o "u" das 6 medalhas, como um pet de um Tamer que ja as tem), para ficarem guardados ao lado do Mega do teste da
// Liga (e2e/save_liga.json), o ativo. Conferido aqui, com a escala ligada como no app: na primeira tentativa do Salao (a Fronteira aberta
// pelo "f", a semente da primeira luta de cada um la) cada guardado vence a luta do nivel dele (guardado nao anda no tempo: o resultado e
// fixo), e o Mega vence a dele em qualquer ponto das proximas 5 h de jogo. Grava e2e/save_salao.json: {guardados: [Rookie, Champion,
// Ultimate]}, cada um {semente, log, versao}.
// uso (em web/app): npx tsx e2e/gerar_save_salao.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CAT, CD, CTR, TPD, Motor, RIVAL_SALAO, criarDono, criarRng, hashSemente } = M;
M.ligarEscala(true);
const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"];

function treinarSePuder(m, ex) {
  if (m.estagioAtual === "bebe" || !m.treino.podeTocar(m.e.tick) || m.treino.fadiga + CTR.fadigaSessao >= CTR.limiarPausa) return ex;
  try { m.treinar(EX[ex % EX.length]); return ex + 1; } catch { return ex; }
}
/** a vida (a de e2e/gerar_save_liga.mjs) ate o pet chegar ao estagio pedido e treinar nele o quanto der em `horas` de jogo */
function petAte(semente, alvo, horas = 8) {
  const m = new Motor(semente, 6), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  m.liberar(M.MEDALHAS_LIGA);
  const dias = 5, passos = Math.round(dias * TPD / CD.passo), orc = Math.round(CD.porDia * dias);
  let gasto = 0, ex = 0, k = 0, chegou = null;
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    if (m.morte) return null;
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, rng);
    if (m.lesionadoDesde !== null) acoes.unshift("tratar_lesao");
    for (const a of acoes) { m.observar(a); gasto++; }
    ex = treinarSePuder(m, ex);
    if ((m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) || (m.estagioAtual === "adulto" && m.lutas.lutas < 12)) {
      m.lutar("aleatorio", hashSemente("sparring", semente, k++));
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    }
    if (m.estagioAtual === alvo && chegou === null) chegou = m.e.tick;
    if (chegou !== null && (m.estagioAtual !== alvo || m.e.tick - chegou >= horas * 60)) break;
  }
  if (m.estagioAtual !== alvo || m.morte) return null;
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  return m;
}
/** a primeira luta do pet no Salao (numa copia com a Fronteira aberta, como o app faz): venceu? */
function venceSalao(m, avancar = 0) {
  const x = Motor.reproduzir(m.semente, m.log, 6);
  if (x.assinatura() !== m.assinatura()) throw new Error("o replay do pet nao bate");
  if (avancar) x.avancar(avancar);
  x.abrirFronteira();
  return x.lutar(RIVAL_SALAO, x.sementeSalao()).venceu;
}
/* o Mega do teste da Liga, o ativo: vence a dele em qualquer hora das proximas 5 h */
const LIGA = JSON.parse(readFileSync(new URL("./save_liga.json", import.meta.url), "utf8"));
const mega = Motor.reproduzir(LIGA.semente, LIGA.log, LIGA.versao);
for (let o = 0; o <= 300; o += 5) if (!venceSalao(mega, o)) throw new Error(`o Mega do save da Liga perde a luta do Salao com ${o} min a mais`);
console.log("Mega do save da Liga:", M.nomeForma(mega.forma), "vence a luta do Salao nas proximas 5 h");
const guardados = [];
for (const [alvo, ini] of [["crianca", 9500], ["adolescente", 9600], ["adulto", 9700]]) {
  let achou = null;
  for (let s = ini; s < ini + 100 && !achou; s++) {
    const m = petAte(s, alvo);
    if (!m) { console.log(alvo, "semente", s, "nao chegou"); continue; }
    const ok = venceSalao(m);
    console.log(alvo, "semente", s, M.nomeForma(m.forma), "treino", m.treino.total, ok ? "VENCE" : "perde");
    if (ok) achou = m;
  }
  if (!achou) throw new Error("nenhuma semente deu um " + alvo + " que vence a luta do Salao");
  guardados.push({ semente: achou.semente, log: achou.log, versao: achou.versao });
}
writeFileSync(fileURLToPath(new URL("./save_salao.json", import.meta.url)), JSON.stringify({ guardados }) + "\n");
console.log("gravado: e2e/save_salao.json");
