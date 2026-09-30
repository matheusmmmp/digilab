// Calibracao dos lideres das arenas (pets v6; docs/DESIGN_MEDALHAS_ARENAS.md, secao 3, parte 2). Mesmo metodo de
// test/calibrar_mega.mjs e de experiments/calibrar_escala.py, no motor web e com as regras das lutas dos pets v6 (combate
// V21D, CV21D) e a regra de cada arena (motor/arenas.ts): pet de referencia = as formas do estagio da arena (Rookie: os 2 ramos
// com a semente de gambits deles; Champion: as 4 linhas com a lista do adolescente e o carater canonico; Ultimate e Mega: as 8
// formas adultas com a lista do bot da forma, a variante V21D na muralha e no vigia), nas 4 especies, com treino uniforme; o
// lider na escala (E = vida do estagio x fator, epsilon CESC.epsNpc), como o motor o monta na luta de arena (lutadorBot com a
// arena). O pet e sempre o lado A, como no jogo (a serie da Cidadela so faz sentido assim).
//
// Metas (as de sempre, fixadas antes): sem treino <= 0,30 e com o treino tipico >= 0,80 (media das formas e das especies), e
// nenhuma forma travada (cada forma >= 0,5 com o treino tipico). Treino tipico por estagio (calibrar_progressao.ALCANCE e
// CMG.tetoVida): Rookie 8, Champion 22, Ultimate 36, Mega 40.
// Escolha do fator: entre os que passam nas tres metas, o de maior folga min(0,30 - sem, com - 0,80, pior - 0,5); se nenhum
// passar, o de maior folga (registrado como NAO PASSA). Na Cidadela a "vitoria" e a serie inteira (3 vitorias seguidas).
// Campina e Montanha Espiral nao mudaram de regra: so se mede o fator de hoje (se nao passar, o relatorio diz).
// No Lago a regra (sem travas nem vetos) nao muda nada para os pets de referencia, que nao tem dono.
//
// uso (em web/app): node test/calibrar_arenas.mjs [--validar] [-n 10]
//   sem --validar: sementes de calibracao, fatores 0,5..3,0 -> artifacts_campanha/arenas/calibracao.json
//   --validar: sementes de validacao, os fatores de motor/arenas.ts (ou do NPC) -> artifacts_campanha/arenas/validacao.json
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ADOL_V21, ARENAS, CESC, CMG, CRIANCA_V21, CV, CV21D, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, LUGARES_V6, NPC, STATS } = M;
const args = process.argv.slice(2), validar = args.includes("--validar");
const n = args.includes("-n") ? Number(args[args.indexOf("-n") + 1]) : 10;
const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505], SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505];
const sementes = validar ? SEM_VALIDACAO : SEM_CALIBRACAO;
const META_SEM = 0.30, META_COM = 0.80, META_FORMA = 0.5;
const FATORES = Array.from({ length: 26 }, (_, i) => Math.round((0.5 + 0.1 * i) * 10) / 10);
const TIPICO = { crianca: 8, adolescente: 22, adulto: 36, mega: CMG.tetoVida };
/* lideres que a parte 2 nao mudou (so a validacao do fator de hoje) */
const SO_MEDIR = new Set(["campina", "espiral"]);
const R = CV21D;
M.ligarEscala(true);

const primeiraForma = l => FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l);
/** as formas de referencia do estagio: [nome, forma(esp), carater, gambits] */
function formasDe(est) {
  if (est === "crianca") return ["sereno", "arisco"].map(r => [r, e => ({ esp: e, est, ramo: r }), null, CRIANCA_V21[r]]);
  if (est === "adolescente") return LINHAS.map(l => [l, e => ({ esp: e, est, ramo: "sereno", linha: l }), M.caraterCanonico(primeiraForma(l)), ADOL_V21[l]]);
  return FORMAS_AD.map(f => [f, e => ({ esp: e, est, ramo: "sereno", linha: LINHA_DA_FORMA[f], adulta: f }), M.caraterCanonico(f), M.gambitsAdulto(f, R)]);
}
function pet([nome, forma, car, g], esp, nivel) {
  const tr = nivel ? Object.fromEntries(STATS.map(k => [k, nivel / STATS.length])) : null, f = forma(esp);
  return { nome: `${nome}+${nivel}@${esp}`, estilo: { nome, gambits: M.copiarGambits(g), eps: CV.eps }, cond: M.perfilDe(f, car, 1, tr, true) };
}
function taxa(a, b, arena) {
  let soma = 0, tot = 0;
  for (const s of sementes) for (let k = 0; k < n; k++) {
    const serie = M.jogarArena(a, b, M.hashSemente("calib-arena", s, a.nome, b.nome, k), R, arena.lutas ?? 1);
    const ult = serie[serie.length - 1];
    soma += serie.length === (arena.lutas ?? 1) ? ult.pontosA : 0; tot++;
  }
  return soma / tot;
}
function medir(arena, fator) {
  const est = LUGARES_V6[arena.lugar].est, formas = formasDe(est), nv = TIPICO[est], ar = { ...arena, fator };
  const B = M.lutadorBot(arena.lider, R, ar);
  const por = {};
  for (const fo of formas) {
    const v = [0, nv].map(nivel => ESPECIES.reduce((s, e) => s + taxa(pet(fo, e, nivel), B, ar), 0) / ESPECIES.length);
    por[fo[0]] = { sem: +v[0].toFixed(4), com: +v[1].toFixed(4) };
  }
  const ks = Object.keys(por), sem = ks.reduce((s, k) => s + por[k].sem, 0) / ks.length, com = ks.reduce((s, k) => s + por[k].com, 0) / ks.length;
  const pior = Math.min(...ks.map(k => por[k].com)), piorForma = ks.find(k => por[k].com === pior);
  return { fator, sem: +sem.toFixed(4), com: +com.toFixed(4), pior: +pior.toFixed(4), pior_forma: piorForma,
    passa: sem <= META_SEM && com >= META_COM && pior >= META_FORMA,
    folga: +Math.min(META_SEM - sem, com - META_COM, pior - META_FORMA).toFixed(4),
    travados: ks.filter(k => por[k].com < META_FORMA), por_forma: por };
}
const fatorDe = a => a.fator ?? NPC[a.lider].fator ?? CESC.fatorNpc[a.lider];

const out = {
  descricao: "Calibracao dos lideres das arenas (pets v6, medalhas parte 2): motor web, escala ligada, regras V21D, regra de cada arena.",
  conjunto: validar ? "validacao" : "calibracao", sementes, n_por_semente: n, pet_lado: "A",
  metas: { sem_treino_max: META_SEM, com_treino_min: META_COM, pior_forma_min: META_FORMA }, treino_tipico: TIPICO, arenas: {},
};
for (const a of ARENAS) {
  const est = LUGARES_V6[a.lugar].est, cab = `${a.id} (${NPC[a.lider].nome}, ${est}, ${a.regra})`;
  let r;
  if (validar || SO_MEDIR.has(a.id)) { r = medir(a, fatorDe(a)); out.arenas[a.id] = { lider: a.lider, regra: a.regra, estagio: est, ...r }; }
  else {
    const med = FATORES.map(f => medir(a, f)), pool = med.some(m => m.passa) ? med.filter(m => m.passa) : med;
    r = pool.reduce((x, y) => y.folga > x.folga ? y : x);
    out.arenas[a.id] = { lider: a.lider, regra: a.regra, estagio: est, escolha: r, medidas: med.map(({ por_forma, ...x }) => x) };
  }
  console.log(`${cab}: fator ${r.fator} sem ${r.sem} com ${r.com} pior ${r.pior} (${r.pior_forma}) ${r.passa ? "OK" : "NAO PASSA"}${r.travados.length ? " travados " + r.travados : ""}`);
}
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/arenas/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + (validar ? "validacao.json" : "calibracao.json"), JSON.stringify(out, null, 1) + "\n");
