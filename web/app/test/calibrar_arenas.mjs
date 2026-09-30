// Calibracao dos lideres das arenas (pets v6; docs/DESIGN_MEDALHAS_ARENAS.md, secao 3, parte 2). Mesmo metodo de
// test/calibrar_mega.mjs e de experiments/calibrar_escala.py, no motor web e com as regras das lutas dos pets v6 (combate
// V21D, CV21D) e a regra de cada arena (motor/arenas.ts): pet de referencia = as formas do estagio da arena (Rookie: os 2 ramos
// com a semente de gambits deles; Champion: as 4 linhas com a lista do adolescente e o carater canonico; Ultimate e Mega: as 8
// formas adultas com a lista do bot da forma, a variante V21D na muralha e no vigia), nas 4 especies, com treino uniforme; o
// lider na escala (E = vida do estagio x fator, epsilon CESC.epsNpc), como o motor o monta na luta de arena (lutadorBot com a
// arena). O pet e sempre o lado A, como no jogo (a serie da Cidadela so faz sentido assim). Escala: a dos pets v6 (CESC_V6,
// test/calibrar_escala_v6.mjs), nos dois lados (o pet pela versao, o lider pelas regras V21D).
//
// Metas: sem treino <= 0,05 (decisao do Matheus, 2026-09-30: o pet sem treino vence menos de 5%; antes era <= 0,30) e com o
// treino tipico >= 0,80 (media das formas e das especies), e nenhuma forma travada (cada forma >= 0,5 com o treino tipico). Treino tipico por estagio (calibrar_progressao.ALCANCE e
// CMG.tetoVida): Rookie 8, Champion 22, Ultimate 36, Mega 40.
// Escolha do fator: entre os que passam nas tres metas, o de maior folga min(0,05 - sem, com - 0,80, pior - 0,5); se nenhum
// passar, o de maior folga (registrado como NAO PASSA). Na Cidadela a "vitoria" e a serie inteira (3 vitorias seguidas).
// Com a meta de 0,05 todos os lideres sao recalibrados, inclusive Campina e Montanha Espiral (o fator vale so na arena).
// No Lago a regra (sem travas nem vetos) nao muda nada para os pets de referencia, que nao tem dono.
//
// Limite de turnos: por padrao, a regra do jogo nos pets v6 (decisao do Matheus, 2026-09-30): a luta que chega ao limite sem KO e
// do desafiado (o NPC/lider; nas metas de estagio, o pet do estagio de cima). --limite-fracao: a regra de antes (a fracao de vida
// decide), a que gerou os artefatos de calibracao anteriores a essa decisao.
//
// Pets v9 (rodada de equilibrio geral, fase 2; docs/PLANO_EQUILIBRIO_GERAL.md, meta M-B2): por padrao o script mede os pets v9, com
// as regras das lutas deles (combate V21E, CV21E: as listas V21E nas formas de referencia e nos NPCs de estilo v21), a escala da
// versao 9 (CESC_V9) e os fatores dos lideres dos pets v9 (arenas.FATOR_LIDER_V9, pela arena da luta de um pet v9). --v6: a medicao
// de antes (pets v6, V21D, CESC_V6, os fatores de ARENAS), na pasta de antes. Os pets v9 gravam em artifacts_equilibrio_geral/fase2/.
// --lista-torre <nome>: na Torre, a lista do lider e bots.GAMBITS_ARENA[<nome>] (a alavanca da parte 2; test/explorar_torre.mjs).
//
// uso (em web/app): node test/calibrar_arenas.mjs [--v6] [--validar | --conferir] [--arena <id>] [-n 10]
//   sem --validar: sementes de calibracao, fatores 0,5..4,0 -> arenas_calibracao.json (v9) ou artifacts_campanha/arenas/calibracao.json
//   --conferir: sementes de calibracao, os fatores do motor (sem escolher) -> arenas_conferencia.json (v9)
//   --validar: sementes de validacao, os fatores do motor -> arenas_validacao.json (v9; so na fase 4) ou
//     artifacts_campanha/arenas/validacao.json (--v6)
//   --arena <id>: so uma arena (para rodar em paralelo) -> o arquivo com o sufixo _<id>
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ADOL_V21, ARENAS, CESC, CMG, CRIANCA_V21, CV, CV21D, CV21E, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, LUGARES_V6, NPC, STATS } = M;
const args = process.argv.slice(2), validar = args.includes("--validar"), conferir = args.includes("--conferir"), V6 = args.includes("--v6");
if (validar && conferir) throw new Error("--validar e --conferir juntos");
const opcao = k => args.includes(k) ? args[args.indexOf(k) + 1] : null;
const SO_ARENA = opcao("--arena"), LISTA_TORRE = opcao("--lista-torre");
if (SO_ARENA && !ARENAS.some(a => a.id === SO_ARENA)) throw new Error("arena desconhecida: " + SO_ARENA);
const n = args.includes("-n") ? Number(args[args.indexOf("-n") + 1]) : 10;
const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505], SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505];
const sementes = validar ? SEM_VALIDACAO : SEM_CALIBRACAO;
const META_SEM = 0.05, META_COM = 0.80, META_FORMA = 0.5;
const FATORES = Array.from({ length: 36 }, (_, i) => Math.round((0.5 + 0.1 * i) * 10) / 10);   /* 0,5..4,0 */
const TIPICO = { crianca: 8, adolescente: 22, adulto: 36, mega: CMG.tetoVida };
/* com a meta de 0,05 nenhum lider fica so medido */
const SO_MEDIR = new Set();
/* as regras da luta e a versao do pet (a escala: escalaDe(..., VERSAO); o fator do lider: a arena da luta de um pet desta versao) */
const R = V6 ? CV21D : CV21E, VERSAO = R.versaoPet, FRACAO = args.includes("--limite-fracao"), DESAFIADO = FRACAO ? null : 1;
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
  return { nome: `${nome}+${nivel}@${esp}`, estilo: { nome, gambits: M.copiarGambits(g), eps: CV.eps }, cond: M.perfilDe(f, car, 1, tr, true, VERSAO) };
}
function taxa(a, b, arena) {
  let soma = 0, tot = 0;
  for (const s of sementes) for (let k = 0; k < n; k++) {
    const serie = M.jogarArena(a, b, M.hashSemente("calib-arena", s, a.nome, b.nome, k), R, arena.lutas ?? 1, DESAFIADO);
    const ult = serie[serie.length - 1];
    soma += serie.length === (arena.lutas ?? 1) ? ult.pontosA : 0; tot++;
  }
  return soma / tot;
}
function medir(arena, fator) {
  const est = LUGARES_V6[arena.lugar].est, formas = formasDe(est), nv = TIPICO[est], ar = { ...arena, fator, ...(LISTA_TORRE && arena.id === "torre" ? { lista: LISTA_TORRE } : {}) };
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
const fatorDe = V6 ? a => a.fator ?? NPC[a.lider].fator ?? CESC.fatorNpc[a.lider] : a => {
  const f = M.arenaDaLuta(a.lider, VERSAO)?.fator;
  if (f === undefined) throw new Error("lider sem fator dos pets v9: " + a.id);
  return f;
};

const out = {
  descricao: V6 ? "Calibracao dos lideres das arenas (pets v6, medalhas parte 2): motor web, escala ligada, regras V21D, regra de cada arena."
    : `${conferir ? "Conferencia" : "Calibracao"} dos lideres das arenas (pets v9, rodada de equilibrio geral fase 2): motor web, escala ligada (CESC_V9), regras V21E, regra de cada arena.`,
  conjunto: validar ? "validacao" : "calibracao", limite: FRACAO ? "fracao" : "desafiado", ...(V6 ? {} : { regras: "v21e", versao_pet: VERSAO }),
  ...(LISTA_TORRE ? { lista_torre: LISTA_TORRE } : {}), sementes, n_por_semente: n, pet_lado: "A",
  metas: { sem_treino_max: META_SEM, com_treino_min: META_COM, pior_forma_min: META_FORMA }, treino_tipico: TIPICO, arenas: {},
};
for (const a of ARENAS.filter(x => !SO_ARENA || x.id === SO_ARENA)) {
  const est = LUGARES_V6[a.lugar].est, cab = `${a.id} (${NPC[a.lider].nome}, ${est}, ${a.regra})`;
  let r;
  if (validar || conferir || SO_MEDIR.has(a.id)) { r = medir(a, fatorDe(a)); out.arenas[a.id] = { lider: a.lider, regra: a.regra, estagio: est, ...r }; }
  else {
    const med = FATORES.map(f => medir(a, f)), pool = med.some(m => m.passa) ? med.filter(m => m.passa) : med;
    r = pool.reduce((x, y) => y.folga > x.folga ? y : x);
    out.arenas[a.id] = { lider: a.lider, regra: a.regra, estagio: est, escolha: r, medidas: med.map(({ por_forma, ...x }) => x) };
  }
  console.log(`${cab}: fator ${r.fator} sem ${r.sem} com ${r.com} pior ${r.pior} (${r.pior_forma}) ${r.passa ? "OK" : "NAO PASSA"}${r.travados.length ? " travados " + r.travados : ""}`);
}
const pasta = fileURLToPath(new URL(V6 ? "../../../artifacts_campanha/arenas/" : "../../../artifacts_equilibrio_geral/fase2/", import.meta.url));
mkdirSync(pasta, { recursive: true });
const nome = (validar ? "validacao" : conferir ? "conferencia" : "calibracao") + (LISTA_TORRE ? "_" + LISTA_TORRE : "") + (SO_ARENA ? "_" + SO_ARENA : "");
writeFileSync(pasta + (V6 ? "" : "arenas_") + nome + ".json", JSON.stringify(out, null, 1) + "\n");
