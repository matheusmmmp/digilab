/* Rodada de equilibrio do combate em tempo real, fase 1: o relogio (docs/PLANO_EQUILIBRIO_COMBATE_TR.md, metas T-1 a T-5). So o motor,
   sem tela, CPU contra CPU, com semente. Mede, com o relogio dado (o dos pets v13 ou um candidato), sobre as 8 formas adultas (os bots
   canonicos, perfil neutro, regras CV21E_TR):
   - T-1 a duracao e T-2 a fracao no limite, em todos os pares (o espelho incluido), com os lados trocados;
   - T-3 a serie da Cidadela (3 lutas contra o lider, sem cura), cada forma como o pet;
   - T-4 o lado A no espelho (a mesma forma dos dois lados), so nas lutas que acabam em nocaute;
   - T-5 as reacoes ao pesado anunciado: as vezes em que o lado A estava livre para decidir enquanto o rival preparava, quantas delas a
     regra "rival preparando" decidiu, e quantos preparos do rival tiveram ao menos uma decisao livre do lado A.
   As sementes: a faixa reservada (experiments/bancada/faixas.py) da calibracao (68101 a 68505) ou da conferencia (70101 a 70505), as 5
   bases X101, X202, ..., X505, e 20 sementes por base (hashSemente("equilibrio-tr", base, k)): 100 sementes x os dois lados = 200 lutas
   por par (plano, secao 3).
   uso (em web/app): npx tsx scripts/equilibrio_tr/fase1_relogio.ts --faixa calibracao [--base v14] [--relogio '{"ritmo":12}'] --saida <arquivo.json> */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { execSync } from "node:child_process";
import {
  ARENA_POR_ID, CTR_TR, CV21E_TR, FORMAS_AD, PASSO_TR_MS, RELOGIO_V13, RELOGIO_V14, criarLutaTR, hashSemente, jogarArena, lutadorBot, passoTR,
  type Lutador, type RegrasLuta, type RelogioTR,
} from "../../motor/index.ts";

const arg = (k: string): string | null => { const i = process.argv.indexOf("--" + k); return i < 0 ? null : process.argv[i + 1] ?? null; };
const FAIXAS: Record<string, number> = { calibracao: 68101, conferencia: 70101 };
const faixa = arg("faixa"), saida = arg("saida");
if (!faixa || !(faixa in FAIXAS)) throw new Error("--faixa calibracao | conferencia");
if (!saida) throw new Error("--saida <arquivo.json>");
/* --base v14: o relogio candidato da fase 1 (RELOGIO_V14); sem ele, o dos pets v13 */
const relogio: RelogioTR = { ...(arg("base") === "v14" ? RELOGIO_V14 : RELOGIO_V13), ...JSON.parse(arg("relogio") ?? "{}") };
for (const k of Object.keys(relogio)) if (!(k in RELOGIO_V13)) throw new Error("numero do relogio desconhecido: " + k);
const R: RegrasLuta = { ...CV21E_TR, relogio };
const SEMENTES_POR_BASE = 20;
const bases = [0, 1, 2, 3, 4].map(i => FAIXAS[faixa] + 101 * i);
const sementes = bases.flatMap(b => Array.from({ length: SEMENTES_POR_BASE }, (_, k) => hashSemente("equilibrio-tr", b, k)));
const seg = (passos: number): number => passos * PASSO_TR_MS / 1000;
const LIMITE = CTR_TR.limite;

/** as condicoes "rival preparando" de uma lista: os indices das regras que a pedem */
const regrasPreparo = (L: Lutador): Set<number> =>
  new Set((L.estilo.gambits?.regras ?? []).flatMap((r, i) => r.se.some(c => c.n === "oponente_preparando") ? [i] : []));

/** uma luta passo a passo: a duracao, o fim, os pontos e as contas de T-5 do lado 0 */
function luta(A: Lutador, B: Lutador, s: number) {
  const Lt = criarLutaTR(A, B, s, { R, desafiado: 1 }), S = Lt.S, prep = regrasPreparo(A);
  let livresNoPreparo = 0, reagiu = 0, preparos = 0, preparosComChance = 0, chanceNeste = false, emPreparo = false;
  for (;;) {
    const b = S.L[1], a = S.L[0], preparando = b.acao?.nome === "preparar_pesado";
    if (preparando && !emPreparo) { preparos++; chanceNeste = false; }
    if (!preparando && emPreparo && chanceNeste) preparosComChance++;
    emPreparo = preparando;
    const livre = preparando && a.acao === null && S.passo >= a.atordoadoAte && S.passo % S.C.ritmo === 0 && a.hp > 0;
    const antes = Lt.acoes.length;
    const f = passoTR(Lt, 1);
    if (livre) {
      livresNoPreparo++; chanceNeste = true;
      const nova = Lt.acoes.slice(antes).find(x => x.lado === 0);
      if (nova && typeof nova.motivo === "number" && prep.has(nova.motivo)) reagiu++;
    }
    if (f) {
      if (emPreparo && chanceNeste) preparosComChance++;
      return { passos: S.passo, fim: f[1], pontosA: f[0], livresNoPreparo, reagiu, preparos, preparosComChance, temRegra: prep.size > 0 };
    }
  }
}

const media = (xs: number[]): number => xs.reduce((a, b) => a + b, 0) / xs.length;
const quantil = (xs: number[], q: number): number => { const o = [...xs].sort((a, b) => a - b); return o[Math.min(o.length - 1, Math.floor(q * o.length))]; };
const r3 = (x: number): number => Math.round(x * 1000) / 1000;

const t0 = performance.now();
const pares: { a: string; b: string; duracao_media_s: number; no_limite: number; vitorias_a: number; lutas: number }[] = [];
const todas: number[] = [];
let noLimite = 0, total = 0, livres = 0, reacoes = 0, preparosTot = 0, comChance = 0, livresComRegra = 0, reacoesComRegra = 0;
const espelho: { forma: string; vitorias_a: number; derrotas_a: number; empates: number }[] = [];
for (let i = 0; i < FORMAS_AD.length; i++) for (let j = i; j < FORMAS_AD.length; j++) {
  const fa = FORMAS_AD[i], fb = FORMAS_AD[j], A = lutadorBot(fa, R), B = lutadorBot(fb, R);
  const durs: number[] = [];
  let lim = 0, vA = 0, n = 0, eV = 0, eD = 0, eE = 0;
  for (const s of sementes) for (const lados of [[A, B], [B, A]] as const) {
    const r = luta(lados[0], lados[1], s), d = seg(r.passos);
    durs.push(d); todas.push(d); n++; total++;
    if (r.passos >= LIMITE) { lim++; noLimite++; }
    /* o lado do par "a" (fa) venceu? */
    const pontosFa = lados[0] === A ? r.pontosA : 1 - r.pontosA;
    vA += pontosFa;
    /* T-4: so as lutas decididas por nocaute (no limite a luta fica com o desafiado, o lado B: e a regra, nao o lado) */
    if (i === j && r.fim === "ko") { if (r.pontosA === 1) eV++; else if (r.pontosA === 0) eD++; else eE++; }
    livres += r.livresNoPreparo; reacoes += r.reagiu; preparosTot += r.preparos; comChance += r.preparosComChance;
    if (r.temRegra) { livresComRegra += r.livresNoPreparo; reacoesComRegra += r.reagiu; }
  }
  pares.push({ a: fa, b: fb, duracao_media_s: r3(media(durs)), no_limite: r3(lim / n), vitorias_a: r3(vA / n), lutas: n });
  if (i === j) espelho.push({ forma: fa, vitorias_a: eV, derrotas_a: eD, empates: eE });
}
/* T-3: a Cidadela, cada forma como o pet contra o lider (3 lutas sem cura; o limite fica com o desafiado, o lider) */
const cid = ARENA_POR_ID.cidadela, lider = lutadorBot(cid.lider, R, cid), series: number[] = [];
for (const f of FORMAS_AD) for (const s of sementes) {
  const serie = jogarArena(lutadorBot(f, R), lider, s, R, cid.lutas ?? 1, 1);
  series.push(serie.reduce((a, x) => a + seg(x.tr.passos), 0));
}
const decididasEsp = espelho.reduce((a, e) => a + e.vitorias_a + e.derrotas_a, 0), vEsp = espelho.reduce((a, e) => a + e.vitorias_a, 0);
const out = {
  gerado_por: "web/app/scripts/equilibrio_tr/fase1_relogio.ts", data: new Date().toISOString().slice(0, 10),
  commit: execSync("git rev-parse --short HEAD").toString().trim(), node: process.version,
  faixa, bases, sementes_por_base: SEMENTES_POR_BASE, relogio, lutas: total,
  metas: {
    "T-1": { duracao_media_s: r3(media(todas)), duracao_mediana_s: r3(quantil(todas, .5)), p90_s: r3(quantil(todas, .9)),
      passa: media(todas) >= 40 && media(todas) <= 60 && quantil(todas, .5) >= 35 && quantil(todas, .5) <= 55 },
    "T-2": { no_limite_total: r3(noLimite / total), no_limite_pior_par: Math.max(...pares.map(p => p.no_limite)), passa: Math.max(...pares.map(p => p.no_limite)) <= .05 },
    "T-3": { cidadela_media_s: r3(media(series)), cidadela_p90_s: r3(quantil(series, .9)), passa: quantil(series, .9) <= 180 },
    "T-4": { espelho_vitorias_a_entre_decididas: r3(vEsp / decididasEsp), passa: vEsp / decididasEsp >= .45 && vEsp / decididasEsp <= .55 },
    "T-5": { reagiu_quando_livre_com_regra: r3(reacoesComRegra / Math.max(1, livresComRegra)), livres_com_regra: livresComRegra,
      preparos_com_alguma_decisao_livre: r3(comChance / Math.max(1, preparosTot)), preparos: preparosTot, passa: reacoesComRegra / Math.max(1, livresComRegra) >= .5 },
  },
  piores_pares_no_limite: [...pares].sort((x, y) => y.no_limite - x.no_limite).slice(0, 8).map(p => `${p.a} x ${p.b}: ${p.no_limite}`),
  espelho, pares, custo_s: r3((performance.now() - t0) / 1000),
};
mkdirSync(dirname(saida), { recursive: true });
writeFileSync(saida, JSON.stringify(out, null, 1) + "\n");
console.log(JSON.stringify(out.metas, null, 1));
