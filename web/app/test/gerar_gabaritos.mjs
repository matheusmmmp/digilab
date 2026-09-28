// Gera os gabaritos de paridade do motor web (TAREFA_FRONT_TS, Etapa 1).
//
// Carrega SO o motor do HTML atual (motor_html.mjs), joga vidas sinteticas (semente x versao do pet
// x perfil de dono) e grava, em pontos fixos de um replay incremental do registro, o sha256 de
// assinatura() e os contadores que ela nao cobre. O motor em TypeScript tem que bater com isto.
//
// Rodar SEMPRE em Node: o V8 do Chrome e o do Node diferem no ultimo bit de Math.exp/log (libm), o
// que muda os bracos do bandit. Dentro do mesmo runtime o replay e bit a bit.
//
// uso: node web/app/test/gerar_gabaritos.mjs
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync, readdirSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { carregarMotor } from "./motor_html.mjs";

export const DIR = fileURLToPath(new URL("./gabaritos/", import.meta.url));
export const SIMBOLOS = ["Motor", "criarDono", "criarRng", "hashSemente", "CD", "TPD", "CAT", "CTR", "NOME_BOT", "NPC",
  "CAMPANHA", "REPERTORIO", "ACOES_DONO", "VERSAO_PET", "TICK_INICIAL"];

export const VERSOES = [1, 2, 3];
export const PERFIS = ["atencioso", "relapso", "aleatorio", "incoerente", "exigente"];
export const SEMENTES_POR_GRUPO = 4;          /* 3 versoes x 5 perfis x 4 = 60 vidas, 60 sementes distintas */
export const DIAS = 2.5;                        /* bebe 3 h + crianca 12 h + adolescente 18 h + sparring: sobra o adulto */
export const PASSO_CHECKPOINT = 25;             /* um ponto a cada 25 eventos, mais toda evolucao e o fim */

export const sha256 = s => createHash("sha256").update(s).digest("hex");
export const semente = (iv, ip, j) => 7000 + 100 * iv + 10 * ip + j;

/** o que o gabarito guarda num ponto do replay: a assinatura e o que ela nao cobre */
export function ponto(m, i) {
  return { evento: i, tick: m.e.tick, sha: sha256(m.assinatura()), prox: m.prox, nDecisoes: m.nDecisoes,
    historico: m.historico.length, motivos: m.motivos.length, nDono: m.nDono, estagio: m.estagioAtual,
    forma: JSON.stringify(m.forma) };
}

/** um evento do registro no motor, pelo mesmo caminho de Motor.reproduzir */
export function aplicarEvento(m, [t, tipo, v]) {
  if (m.e.tick !== t) throw new Error(`registro fora de ordem no tick ${t}`);
  if (tipo === "t") m._avancar(v);
  else if (tipo === "d") m._aplicar(v);
  else if (tipo === "l") m._lutar(v.r, v.s);
  else if (tipo === "g") m._gambit(v.op, v.k);
  else if (tipo === "tr") m._treinar(v);
  else throw new Error("tipo de evento desconhecido no registro: " + tipo);
}

/** replay incremental com checkpoints fixos (depende so do registro, nao de como ele foi feito) */
export function checkpoints(M, sem, versao, log) {
  const m = new M.Motor(sem, versao), pts = [ponto(m, 0)];
  let est = m.estagioAtual;
  /* motor em TS: Motor.aplicarEvento; motor do HTML: o mesmo caminho de Motor.reproduzir */
  const passo = typeof m.aplicarEvento === "function" ? ev => m.aplicarEvento(ev) : ev => aplicarEvento(m, ev);
  log.forEach((ev, i) => {
    passo(ev);
    const n = i + 1;
    if (n % PASSO_CHECKPOINT === 0 || m.estagioAtual !== est || n === log.length) pts.push(ponto(m, n));
    est = m.estagioAtual;
  });
  return { m, pts };
}

/* ---------------------------------------------------------------- vidas sinteticas */
const EXERCICIOS = ex => Object.keys(ex);

/** uma vida: dono sintetico do motor para o cuidado + extras do perfil (treino, lutas, gambits) */
export function viver(M, sem, versao, perfil) {
  const m = new M.Motor(sem, versao);
  const dono = M.criarDono(perfil === "exigente" ? "atencioso" : perfil);
  const r = M.criarRng(M.hashSemente("dono", sem, perfil)), rx = M.criarRng(M.hashSemente("gabarito", sem, perfil));
  const passos = Math.round(DIAS * M.TPD / M.CD.passo), orc = Math.round(M.CD.porDia * DIAS);
  const exs = EXERCICIOS(M.CTR.exercicios), bots = Object.keys(M.NOME_BOT).filter(k => !M.NPC[k]);
  let gasto = 0, vetada = null, travada = null;
  const podeTreinar = () => m.estagioAtual !== "bebe" && m.treino.podeTocar(m.e.tick);
  for (let p = 0; p < passos; p++) {
    m.avancar(M.CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * M.CD.maxPasso), max = Math.min(rest, M.CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, r);
    if (acoes.length > max || acoes.length < min) throw new Error(`dono ${perfil} violou o orcamento no passo ${p}`);
    for (const a of acoes) { m.observar(a); gasto++; }

    /* treino: o exigente treina em todo passo que pode, inclusive cansado (forca e vira sombria);
       atencioso e incoerente respeitam o pedido de pausa; aleatorio treina ao acaso; relapso nao treina */
    if (podeTreinar()) {
      const ex = exs[rx.int(exs.length)];
      if (perfil === "exigente") m.treinar(ex);
      else if ((perfil === "atencioso" || perfil === "incoerente") && !m.treino.pedePausa && p % 4 === 0) m.treinar(ex);
      else if (perfil === "aleatorio" && rx.random() < .3) m.treinar(ex);
    }
    /* exigente: segunda sessao no mesmo passo, 10 min depois (o treino tem intervalo de 10 min) */
    if (perfil === "exigente" && m.estagioAtual !== "bebe") { m.avancar(M.CTR.intervalo); if (podeTreinar()) m.treinar(exs[rx.int(exs.length)]); }

    /* sparring do adolescente (cronograma): uma luta por passo contra o bot aleatorio, ate o minimo */
    if (m.estagioAtual === "adolescente" && m.sparring < M.CAT.sparring) m.lutar("aleatorio", M.hashSemente("sparring", sem, p));

    /* adulto: arena (bots) e campanha (NPC aberto), um passo sim outro nao */
    if (m.estagioAtual === "adulto" && p % 2 === 0) {
      const npcs = M.CAMPANHA.map(c => c.k).filter(k => m.desafioAberto(k));
      const rival = (perfil === "relapso" || rx.random() < .5) && npcs.length ? npcs[rx.int(npcs.length)] : bots[rx.int(bots.length)];
      m.lutar(rival, M.hashSemente("gabarito-luta", sem, p));
    }

    /* intervencoes nos gambits (travar, destravar, vetar, liberar) em momentos fixos depois da crianca */
    if (m.gp && perfil !== "relapso" && p % 12 === 6) {
      const ativas = m.gp.ativas;
      const op = ["travar", "vetar", "destravar", "liberar"][(p / 12 | 0) % 4];
      if (op === "travar" && ativas.length) { travada = ativas[rx.int(ativas.length)]; m.intervirGambit("travar", travada); }
      else if (op === "destravar" && travada) { m.intervirGambit("destravar", travada); travada = null; }
      else if (op === "vetar" && ativas.length) { vetada = ativas[ativas.length - 1]; if (vetada === travada) travada = null; m.intervirGambit("vetar", vetada); }
      else if (op === "liberar" && vetada) { m.intervirGambit("liberar", vetada); vetada = null; }
    }
  }
  if (gasto !== orc) throw new Error(`vida ${perfil}@${sem} terminou com ${gasto}/${orc} interacoes`);
  return m;
}

/* ---------------------------------------------------------------- cobertura */
function cobertura(vidas) {
  const c = { vidas: vidas.length, sementes: new Set(vidas.map(v => v.semente)).size, eventos: {}, acoesDono: {}, exercicios: {},
    gambit: {}, rivais: {}, estagioFinal: {}, versao: {}, perfil: {}, ramos: {}, linhas: {}, adultas: {}, sombrias: 0, falaFria: 0,
    checkpoints: 0, eventosTotal: 0 };
  const inc = (o, k) => { o[k] = (o[k] || 0) + 1; };
  for (const v of vidas) {
    inc(c.versao, v.versao); inc(c.perfil, v.perfil); inc(c.estagioFinal, v.final.estagio);
    c.checkpoints += v.checkpoints.length; c.eventosTotal += v.log.length;
    for (const [, tipo, x] of v.log) {
      inc(c.eventos, tipo);
      if (tipo === "d") inc(c.acoesDono, x);
      if (tipo === "tr") inc(c.exercicios, x);
      if (tipo === "g") inc(c.gambit, x.op);
      if (tipo === "l") inc(c.rivais, x.r);
    }
    const f = JSON.parse(v.final.forma);
    if (f.ramo) inc(c.ramos, f.ramo);
    if (f.linha) inc(c.linhas, f.linha);
    if (f.adulta) inc(c.adultas, f.adulta);
    if (v.sombria) c.sombrias++;
    if (v.falaFria) c.falaFria++;
  }
  return c;
}

/** falha alto se faltar algum tipo de evento, acao do dono, exercicio, intervencao ou estagio */
export function exigirCobertura(c, M) {
  const falta = [];
  for (const t of ["t", "d", "l", "g", "tr"]) if (!c.eventos[t]) falta.push("evento " + t);
  for (const a of M.ACOES_DONO) if (!c.acoesDono[a]) falta.push("acao do dono " + a);
  for (const ex of Object.keys(M.CTR.exercicios)) if (!c.exercicios[ex]) falta.push("exercicio " + ex);
  for (const op of ["travar", "destravar", "vetar", "liberar"]) if (!c.gambit[op]) falta.push("gambit " + op);
  for (const k of M.CAMPANHA.map(x => x.k)) if (!c.rivais[k]) falta.push("NPC " + k);
  if (!c.adultas.devastador) falta.push("devastador (regra fora do repertorio)");
  for (const r of ["sereno", "arisco"]) if (!c.ramos[r]) falta.push("ramo " + r);
  if (!c.estagioFinal.adulto) falta.push("estagio adulto");
  if (!c.sombrias) falta.push("forma sombria");
  if (c.sementes < 50) falta.push(`so ${c.sementes} sementes (minimo 50)`);
  if (falta.length) throw new Error("cobertura insuficiente: " + falta.join(", "));
}

/* ---------------------------------------------------------------- principal */
function main() {
  const M = carregarMotor(SIMBOLOS);
  if (M.VERSAO_PET !== 3) throw new Error("VERSAO_PET mudou: " + M.VERSAO_PET);
  mkdirSync(DIR, { recursive: true });
  for (const f of readdirSync(DIR)) if (/^vidas_.*\.json$/.test(f)) rmSync(DIR + f);
  const todas = [];
  VERSOES.forEach((versao, iv) => PERFIS.forEach((perfil, ip) => {
    const grupo = [];
    for (let j = 0; j < SEMENTES_POR_GRUPO; j++) {
      const sem = semente(iv, ip, j), vivo = viver(M, sem, versao, perfil);
      const log = vivo.log.map(x => [...x]);
      const { m, pts } = checkpoints(M, sem, versao, log);
      /* o replay tem que dar o que a vida deu (dentro do mesmo runtime) */
      if (m.assinatura() !== vivo.assinatura()) throw new Error(`replay diverge da vida: ${perfil} v${versao} @${sem}`);
      const rep = M.Motor.reproduzir(sem, log, versao);
      if (rep.assinatura() !== vivo.assinatura()) throw new Error(`Motor.reproduzir diverge da vida: ${perfil} v${versao} @${sem}`);
      grupo.push({ semente: sem, versao, perfil, log, checkpoints: pts, final: pts[pts.length - 1], assinaturaFinal: vivo.assinatura(),
        sombria: vivo.sombria, falaFria: vivo.falaFria });
    }
    writeFileSync(`${DIR}vidas_v${versao}_${perfil}.json`, JSON.stringify({ versao, perfil, dias: DIAS, passoCheckpoint: PASSO_CHECKPOINT, vidas: grupo }) + "\n");
    todas.push(...grupo);
    process.stdout.write(`v${versao} ${perfil}: ${grupo.map(v => `${v.semente}:${v.final.estagio}${v.sombria ? "*" : ""}`).join(" ")}\n`);
  }));
  const cob = cobertura(todas);
  exigirCobertura(cob, M);
  writeFileSync(DIR + "cobertura.json", JSON.stringify({ runtime: "node " + process.version, ...cob }, null, 1) + "\n");
  console.log(`${todas.length} vidas, ${cob.sementes} sementes, ${cob.eventosTotal} eventos, ${cob.checkpoints} checkpoints; sombrias ${cob.sombrias}`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) main();
