// Calibracao dos desafiantes da campanha v6 (os NPCs que nao sao lideres de arena: Tortomon e Devidramon na Torre de pedra,
// Puppetmon e Machinedramon na Montanha Espiral) na escala dos pets v6 (CESC_V6). Mesmo metodo de calibrar_arenas.mjs, sem
// regra de arena: pet de referencia = as formas do estagio do lugar (Champion: as 4 linhas com a lista do adolescente e o
// carater canonico; Mega: as 8 formas com a lista do bot da forma, as variantes V21D), nas 4 especies, treino uniforme, lado
// A; o NPC como o motor o monta na luta de um pet v6 (lutadorBot com as regras V21D: E = vida do estagio na CESC_V6 x fator,
// epsilon CESC.epsNpc).
//
// Metas (as de sempre da campanha; os lideres tem as de 0,05): sem treino <= 0,30, com o treino tipico >= 0,80 (Champion 22,
// Mega 40) e nenhuma forma < 0,5. Escolha: entre os fatores que passam, o de maior folga; se nenhum passar, o de maior folga
// (NAO PASSA). O fator vale so nas lutas dos pets v6 (CESC_V6.fatorNpc); os v1-v5 seguem com os de sempre.
//
// Limite de turnos: por padrao, a regra do jogo nos pets v6 (decisao do Matheus, 2026-09-30): a luta que chega ao limite sem KO e
// do desafiado (o NPC/lider; nas metas de estagio, o pet do estagio de cima). --limite-fracao: a regra de antes (a fracao de vida
// decide), a que gerou os artefatos de calibracao anteriores a essa decisao.
//
// uso (em web/app): node test/calibrar_desafiantes_v6.mjs [--validar] [-n 10]
//   sem --validar: sementes de calibracao, fatores 0,5..4,0 -> artifacts_campanha/escala_v6/desafiantes_calibracao.json
//   --validar: sementes de validacao, os fatores de CESC_V6.fatorNpc -> artifacts_campanha/escala_v6/desafiantes_validacao.json
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ADOL_V21, ARENAS, CAMPANHA_V6, CESC_V6, CV, CV21D, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, LUGARES_V6, STATS } = M;
const args = process.argv.slice(2), validar = args.includes("--validar");
const n = args.includes("-n") ? Number(args[args.indexOf("-n") + 1]) : 10;
const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505], SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505];
const sementes = validar ? SEM_VALIDACAO : SEM_CALIBRACAO;
const META_SEM = 0.30, META_COM = 0.80, META_FORMA = 0.5;
const FATORES = Array.from({ length: 36 }, (_, i) => Math.round((0.5 + 0.1 * i) * 10) / 10);   /* 0,5..4,0 */
const TIPICO = { crianca: 8, adolescente: 22, adulto: 36, mega: 40 };
const R = CV21D, FRACAO = args.includes("--limite-fracao"), DESAFIADO = FRACAO ? null : 1;
M.ligarEscala(true);

const LIDERES = new Set(ARENAS.map(a => a.lider));
const DESAFIANTES = CAMPANHA_V6.filter(c => !LIDERES.has(c.k));
const primeiraForma = l => FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l);
function formasDe(est) {
  if (est === "adolescente") return LINHAS.map(l => [l, e => ({ esp: e, est, ramo: "sereno", linha: l }), M.caraterCanonico(primeiraForma(l)), ADOL_V21[l]]);
  if (est === "adulto" || est === "mega")
    return FORMAS_AD.map(f => [f, e => ({ esp: e, est, ramo: "sereno", linha: LINHA_DA_FORMA[f], adulta: f }), M.caraterCanonico(f), M.gambitsAdulto(f, R)]);
  throw new Error("estagio sem desafiante: " + est);
}
function pet([nome, forma, car, g], esp, nivel) {
  const tr = nivel ? Object.fromEntries(STATS.map(k => [k, nivel / STATS.length])) : null;
  return { nome: `${nome}+${nivel}@${esp}`, estilo: { nome, gambits: M.copiarGambits(g), eps: CV.eps }, cond: M.perfilDe(forma(esp), car, 1, tr, true, M.VERSAO_ESCALA_V6) };
}
function taxa(a, b) {
  let soma = 0, tot = 0;
  for (const s of sementes) for (let k = 0; k < n; k++) { soma += M.jogarV2(a, b, M.hashSemente("calib-desafiante", s, a.nome, b.nome, k), R, null, DESAFIADO).pontosA; tot++; }
  return soma / tot;
}
function medir(c, fator) {
  const est = LUGARES_V6[c.lug].est, formas = formasDe(est), nv = TIPICO[est];
  const B0 = M.lutadorBot(c.k, R), B = { ...B0, cond: { ...B0.cond, escala: M.escalaDe(est, 0, M.VERSAO_ESCALA_V6) * fator } };
  const por = {};
  for (const fo of formas) {
    const v = [0, nv].map(nivel => ESPECIES.reduce((s, e) => s + taxa(pet(fo, e, nivel), B), 0) / ESPECIES.length);
    por[fo[0]] = { sem: +v[0].toFixed(4), com: +v[1].toFixed(4) };
  }
  const ks = Object.keys(por), sem = ks.reduce((s, k) => s + por[k].sem, 0) / ks.length, com = ks.reduce((s, k) => s + por[k].com, 0) / ks.length;
  const pior = Math.min(...ks.map(k => por[k].com)), piorForma = ks.find(k => por[k].com === pior);
  return { fator, sem: +sem.toFixed(4), com: +com.toFixed(4), pior: +pior.toFixed(4), pior_forma: piorForma,
    passa: sem <= META_SEM && com >= META_COM && pior >= META_FORMA,
    folga: +Math.min(META_SEM - sem, com - META_COM, pior - META_FORMA).toFixed(4),
    travados: ks.filter(k => por[k].com < META_FORMA), por_forma: por };
}

const out = {
  descricao: "Calibracao dos desafiantes da campanha v6 (NPCs que nao sao lideres) na escala dos pets v6: motor web, regras V21D.",
  conjunto: validar ? "validacao" : "calibracao", limite: FRACAO ? "fracao" : "desafiado", sementes, n_por_semente: n, pet_lado: "A",
  escala: { vida: CESC_V6.vida, beta: CESC_V6.beta },
  metas: { sem_treino_max: META_SEM, com_treino_min: META_COM, pior_forma_min: META_FORMA }, treino_tipico: TIPICO, desafiantes: {},
};
for (const c of DESAFIANTES) {
  const est = LUGARES_V6[c.lug].est;
  let r;
  if (validar) {
    const f = CESC_V6.fatorNpc[c.k];
    if (f === undefined) throw new Error(`${c.nome} sem fator na CESC_V6`);
    r = medir(c, f);
    /* o NPC como o motor o monta tem de ter a escala medida */
    if (M.lutadorBot(c.k, R).cond.escala !== M.escalaDe(est, 0, M.VERSAO_ESCALA_V6) * f) throw new Error("escala do NPC diferente da medida: " + c.k);
    out.desafiantes[c.k] = { nome: c.nome, lugar: LUGARES_V6[c.lug].nome, estagio: est, ...r };
  } else {
    const med = FATORES.map(f => medir(c, f)), pool = med.some(m => m.passa) ? med.filter(m => m.passa) : med;
    r = pool.reduce((x, y) => y.folga > x.folga ? y : x);
    out.desafiantes[c.k] = { nome: c.nome, lugar: LUGARES_V6[c.lug].nome, estagio: est, escolha: r, medidas: med.map(({ por_forma, ...x }) => x) };
  }
  console.log(`${c.nome} (${LUGARES_V6[c.lug].nome}, ${est}): fator ${r.fator} sem ${r.sem} com ${r.com} pior ${r.pior} (${r.pior_forma}) ${r.passa ? "OK" : "NAO PASSA"}${r.travados.length ? " travados " + r.travados : ""}`);
}
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/escala_v6/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + (validar ? "desafiantes_validacao.json" : "desafiantes_calibracao.json"), JSON.stringify(out, null, 1) + "\n");
