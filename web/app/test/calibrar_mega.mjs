// Calibracao dos NPCs da Montanha Espiral (pets v5, evolucao canonica; docs/DESIGN_EVOLUCAO_CANONICA.md, secao 5).
// Mesmo metodo de experiments/calibrar_escala.py, no motor web (o Mega so existe no jogo): pet de referencia = as 8
// formas adultas canonicas (carater canonico, gambits do bot da forma), agora Mega, nas 4 especies, com treino uniforme;
// NPC na escala (E = vida do Mega x fator, epsilon CESC.epsNpc). Metas de sempre, fixadas antes: sem treino <= 0,30 e
// com o treino tipico (CMG.tetoVida pontos) >= 0,80, media das formas e especies. Escolha: o fator que passa com a maior
// folga min(0,30 - sem, com - 0,80); se nenhum passar, o de maior folga. A Cidadela dos pets v5 (Myotismon = o Piedmon
// de sempre, fator 1,2) e medida com Ultimates (treino tipico 36), so para conferir.
//
// uso (em web/app): node test/calibrar_mega.mjs [--validar] [-n 10]
//   sem --validar: sementes de calibracao, fatores 0,8..3,0 -> artifacts_campanha/mega/calibracao.json
//   --validar: sementes de validacao, fatores de CAMPANHA_V5 -> artifacts_campanha/mega/validacao.json
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CAMPANHA_V5, CESC, CMG, ESPECIES, FORMAS_AD, LINHA_DA_FORMA, STATS } = M;
const args = process.argv.slice(2), validar = args.includes("--validar");
const n = args.includes("-n") ? Number(args[args.indexOf("-n") + 1]) : 10;
const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505], SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505];
const sementes = validar ? SEM_VALIDACAO : SEM_CALIBRACAO;
const META_SEM = 0.30, META_COM = 0.80;
const FATORES = Array.from({ length: 23 }, (_, i) => Math.round((0.8 + 0.1 * i) * 10) / 10);
M.ligarEscala(true);

function pet(forma, esp, nivel, mega) {
  const f = { esp, est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[forma], adulta: forma, ...(mega ? { mega: true } : {}) };
  const tr = nivel ? Object.fromEntries(STATS.map(k => [k, nivel / STATS.length])) : null;
  return { nome: `${forma}+${nivel}@${esp}${mega ? ":mega" : ""}`, estilo: M.estiloBot(forma), cond: M.perfilDe(f, M.caraterCanonico(forma), 1, tr, true) };
}
function npc(c, fator, mega) {
  return { nome: `${c.k}x${fator}`, estilo: { ...M.estiloBot(c.k), eps: CESC.epsNpc },
    cond: M.perfilNPC(c.total, "adulto", M.escalaDe("adulto", 0, mega) * fator, mega) };
}
function taxa(a, b) {
  let soma = 0, tot = 0;
  for (const s of sementes) for (let k = 0; k < n; k++) {
    const sp = M.hashSemente("calib-mega", s, a.nome, b.nome, k);
    soma += k < n / 2 ? M.jogarV2(a, b, sp).pontosA : 1 - M.jogarV2(b, a, sp).pontosA; tot++;
  }
  return soma / tot;
}
function medir(c, fator, mega, nivelTipico) {
  const por = {};
  for (const forma of FORMAS_AD) {
    const v = [0, nivelTipico].map(nv => ESPECIES.reduce((s, e) => s + taxa(pet(forma, e, nv, mega), npc(c, fator, mega)), 0) / ESPECIES.length);
    por[forma] = { sem: +v[0].toFixed(4), com: +v[1].toFixed(4) };
  }
  const sem = FORMAS_AD.reduce((s, f) => s + por[f].sem, 0) / FORMAS_AD.length, com = FORMAS_AD.reduce((s, f) => s + por[f].com, 0) / FORMAS_AD.length;
  return { fator, sem: +sem.toFixed(4), com: +com.toFixed(4), passa: sem <= META_SEM && com >= META_COM,
    folga: +Math.min(META_SEM - sem, com - META_COM).toFixed(4), travados: FORMAS_AD.filter(f => por[f].com < 0.5), por_forma: por };
}

const espiral = CAMPANHA_V5.filter(c => c.lug === 3), cidadela = CAMPANHA_V5.filter(c => c.lug === 2);
const out = { descricao: "Calibracao dos NPCs da Montanha Espiral (pets v5): motor web, escala ligada.", conjunto: validar ? "validacao" : "calibracao",
  sementes, n_por_semente: n, metas: { sem_treino_max: META_SEM, com_treino_min: META_COM }, treino_tipico: { mega: CMG.tetoVida, ultimate: 36 },
  espiral: {}, cidadela: {} };
for (const c of espiral) {
  if (validar) { out.espiral[c.k] = medir(c, c.fator, true, CMG.tetoVida); }
  else {
    const med = FATORES.map(fa => medir(c, fa, true, CMG.tetoVida)), pool = med.some(m => m.passa) ? med.filter(m => m.passa) : med;
    const esc = pool.reduce((a, b) => b.folga > a.folga ? b : a);
    out.espiral[c.k] = { escolha: esc, medidas: med.map(({ por_forma, ...x }) => x) };
  }
  const r = validar ? out.espiral[c.k] : out.espiral[c.k].escolha;
  console.log(`${c.nome}: fator ${r.fator} sem ${r.sem} com ${r.com} ${r.passa ? "OK" : "NAO PASSA"} travados ${r.travados}`);
}
for (const c of cidadela) {
  out.cidadela[c.k] = medir(c, c.fator, false, 36);
  const r = out.cidadela[c.k];
  console.log(`${c.nome} (Cidadela, Ultimate): fator ${r.fator} sem ${r.sem} com ${r.com} ${r.passa ? "OK" : "NAO PASSA"}`);
}
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/mega/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + (validar ? "validacao.json" : "calibracao.json"), JSON.stringify(out, null, 1) + "\n");
