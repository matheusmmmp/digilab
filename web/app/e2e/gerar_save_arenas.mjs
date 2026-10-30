// Save do teste ponta a ponta das arenas (medalhas parte 2, docs/DESIGN_MEDALHAS_ARENAS.md secao 3): um pet v13 Ultimate,
// treinado, que ja venceu a Campina, a Torre de pedra e a Floresta (o Tamer do teste tem as 3 medalhas; o registro do pet ja
// tem o "u" das 3). O registro termina num avanco de tempo, entao o relogio do app so estica esse avanco e o tamanho do
// registro (que entra na semente da luta) nao muda. Conferido aqui, com a escala ligada como no app: a luta do botao
// Desafiar contra o Myotismon (Cidadela: tres lutas seguidas, semente hashSemente("luta", semente, tamanho do registro)) e a
// serie inteira vencida em qualquer ponto das proximas 5 h de jogo (o relogio do app anda enquanto o teste clica).
// uso (em web/app): node e2e/gerar_save_arenas.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CAT, CD, CTR, DUR_EVO, Motor, hashSemente } = M;
M.ligarEscala(true);
const MYOTISMON = "npc_v5_myotismon";
const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"];

/** cuidado basico (comida, limpeza, carinho) e lesao tratada: o pet de teste nao morre nem adoece */
function cuidar(m) {
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  if (m.e.fome < CD.limAlim) m.observar("alimentar");
  if (m.e.higiene < CD.limLimpar || m.e.sujeira >= CD.sujLimpar) m.observar("limpar");
  if (m.e.humor < .4) m.observar("acariciar");
}
function treinarSePuder(m, ex) {
  if (m.estagioAtual === "bebe" || !m.treino.podeTocar(m.e.tick) || m.treino.fadiga + CTR.fadigaSessao >= CTR.limiarPausa) return ex;
  try { m.treinar(EX[ex % EX.length]); return ex + 1; } catch { return ex; }
}
function ultimateTreinado(semente) {
  const m = new Motor(semente);
  m.liberar(3);
  let ex = 0, k = 0;
  const fimChampion = DUR_EVO.bebe + DUR_EVO.crianca + DUR_EVO.adolescente + 60;
  for (let t = 0; t < fimChampion || m.estagioAtual !== "adulto"; t += CD.passo) {
    if (t > fimChampion + 2000) return null;
    m.avancar(CD.passo);
    cuidar(m);
    ex = treinarSePuder(m, ex);
    if (m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) { m.lutar("aleatorio", hashSemente("sp", semente, k++)); cuidar(m); }
  }
  /* Ultimate: mais um dia de treino */
  for (let t = 0; t < 1200; t += CD.passo) { m.avancar(CD.passo); cuidar(m); ex = treinarSePuder(m, ex); }
  return m;
}
/** vence o primeiro rival de cada lugar ate a Floresta, com a primeira semente que ganha */
function abrirCidadela(m) {
  for (let i = 0; i < 3; i++) {
    const r = m.lugares[i].rivais[0];
    for (let n = 0; !m.lugarVencido(i); n++) {
      if (n > 50) return false;
      const s = hashSemente("abrir", m.semente, i, n);
      if (m.montarLuta(r, s).serie.at(-1).pontosA !== 1) continue;
      m.lutar(r, s); cuidar(m);
    }
  }
  return true;
}
function venceSempre(m) {
  for (let o = 0; o <= 300; o += 5) {
    const x = Motor.reproduzir(m.semente, m.log);
    if (o) x.avancar(o);
    if (x.log.length !== m.log.length) throw new Error("o avanco nao juntou com o ultimo");
    const r = x.lutar(MYOTISMON, hashSemente("luta", x.semente, x.log.length));
    if (!r.venceu || r.serie.length !== 3) return false;
  }
  return true;
}
for (let s = 7100; s < 7300; s++) {
  const m = ultimateTreinado(s);
  if (!m || m.estagioAtual !== "adulto" || m.morte || !abrirCidadela(m)) continue;
  m.avancar(CD.passo);                                        /* o registro termina num avanco de tempo */
  if (m.log[m.log.length - 1][1] !== "t" || !venceSempre(m)) continue;
  const save = { semente: m.semente, log: m.log, versao: m.versao };
  writeFileSync(fileURLToPath(new URL("./save_arenas.json", import.meta.url)), JSON.stringify(save) + "\n");
  console.log("semente", s, "eventos", m.log.length, M.nomeForma(m.forma), "treino", m.treino.total, "vencidos", m.lugares.map((_, i) => m.lugarVencido(i)));
  process.exit(0);
}
throw new Error("nenhuma semente deu um Ultimate que vence a serie da Cidadela em todas as horas");
