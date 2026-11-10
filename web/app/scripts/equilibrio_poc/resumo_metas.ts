/* LUTA_POC, LP5 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 2): le os JSON dos grupos da bancada e da a tabela das 20 metas, com o criterio,
   o valor e se passa. Os criterios sao sobre a estimativa pontual; o intervalo de Wilson a 95 % vai ao lado, so para leitura.
   uso (em web/app): node scripts/equilibrio_poc/resumo_metas.ts --faixa calibracao --fase lp5_0 -> resumo.json e resumo.md na pasta da fase */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { FORMAS_ARENA } from "../../motor/index.ts";
import { ESTAGIOS_LUTA, argumento, atira, juntar, novaConta, quantil, wilson, type Conta } from "./comum.ts";

const faixa = argumento("faixa"), fase = argumento("fase");
/* --pasta: a fumaca (os JSON do --rapido, fora das medicoes) ou um ponto da grade (grade.ts). --parcial: so as metas dos grupos que
   estao na pasta (a grade da LP5-1 nao roda os lideres, a vida e os torneios); nunca numa medida inteira */
const parcial = process.argv.includes("--parcial");
const pasta = argumento("pasta", ""), dir = pasta ? pasta.replace(/[\\/]?$/, "/") : fileURLToPath(new URL(`../medicoes/equilibrio_poc/${fase}/${faixa}/`, import.meta.url));
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type J = any;
const ler = (g: string): J => JSON.parse(readFileSync(dir + `${g}.json`, "utf-8"));
const TODOS = ["lideres", "sparring", "vida", "treino", "estagio", "torneios", ...ESTAGIOS_LUTA.map(e => `formas_${e}`)];
if (parcial && !pasta) throw new Error("resumo: o --parcial so vale com --pasta (a grade)");
const G: Record<string, J> = Object.fromEntries(TODOS.filter(g => !parcial || existsSync(dir + `${g}.json`)).map(g => [g, ler(g)]));
const tem = (...gs: string[]) => gs.every(g => g in G);
if (!Object.keys(G).length) throw new Error(`resumo: nenhum grupo em ${dir}`);
const commits = new Set(Object.values(G).map(x => x.commit)), candidatos = new Set(Object.values(G).map(x => JSON.stringify(x.candidato)));
if (commits.size !== 1) throw new Error(`resumo: os grupos sao de commits diferentes (${[...commits].join(", ")})`);
if (candidatos.size !== 1) throw new Error("resumo: os grupos sao de candidatos diferentes");
for (const [g, x] of Object.entries(G)) if (((x.rapido || x.grade) && !pasta) || (x.grade && !parcial) || x.faixa !== faixa || x.fase !== fase) throw new Error(`resumo: o grupo ${g} nao e desta medida`);

const r3 = (x: number) => Math.round(x * 1000) / 1000;
const tx = (c: Conta) => { if (!c.n) throw new Error("resumo: conta vazia"); return c.v / c.n; };
const ic = (c: Conta) => wilson(c.v, c.n).map(r3);
interface Meta { id: string; meta: string; criterio: string; passa: boolean; valores: Record<string, unknown> }
const metas: Meta[] = [];
const meta = (id: string, nome: string, criterio: string, passa: boolean, valores: Record<string, unknown>) => metas.push({ id, meta: nome, criterio, passa, valores });
const dentro = (x: number, a: number, b: number) => x >= a && x <= b;

/* ---------------------------------------------------------------- P1, P2, P3, D3 */
if (tem("lideres")) {
const L = G.lideres.dados;
const lider = (k: string, sem: number, tip: number, pior: number | null) => {
  const x = L[k], s = tx(x.sem_treino.total), t = tx(x.tipico.total);
  const esp = Object.fromEntries(Object.entries(x.tipico.por_especie as Record<string, Conta>).map(([e, c]) => [e, r3(tx(c))]));
  const piorV = Math.min(...Object.values(esp) as number[]);
  return { passa: s <= sem && t >= tip && (pior === null || piorV >= pior), v: { nome: x.nome, estagio: x.estagio, mapa: x.mapa, sem_treino: r3(s), ic_sem: ic(x.sem_treino.total), tipico: r3(t), ic_tipico: ic(x.tipico.total), pior_especie: piorV, por_especie: esp } };
};
{ const g = lider("npc_tier1_brutamontes", .2, .7, .5); meta("P1", "o Gazimon", "sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50", g.passa, g.v); }
{
  const ls = ["npc_tier1_brutamontes", "npc_tier2_carcereiro", "npc_v6_youkomon", "npc_v5_myotismon", "npc_v6_marinbullmon", "npc_v5_piedmon"].map(k => lider(k, .2, .7, .5));
  meta("P2", "os 6 lideres", "cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3)", ls.every(x => x.passa), Object.fromEntries(ls.map(x => [x.v.nome, { ...x.v, passa: x.passa }])));
}
{
  const ds = ["npc_tier2_sentinela", "npc_tier2_porteiro", "npc_v5_puppetmon", "npc_v5_machinedramon"].map(k => lider(k, .35, .75, null));
  meta("P3", "os 4 desafiantes", "cada um: sem treino <= 0,35; tipico >= 0,75", ds.every(x => x.passa), Object.fromEntries(ds.map(x => [x.v.nome, { ...x.v, passa: x.passa }])));
}
{
  const h = L.npc_v5_myotismon.tipico.relogio_serie, p90 = quantil(h, .9);
  meta("D3", "a Cidadela cabe", "a serie de 3 (pet tipico) no p90 <= 180 s", p90 <= 180, { p90_s: p90, mediana_s: quantil(h, .5) });
}
}
/* ---------------------------------------------------------------- P4, V2 */
if (tem("sparring")) {
  const S = G.sparring.dados, f = (e: string) => { const ps = S[e].pets as { n: number; v: number }[]; return ps.filter(p => p.v / p.n >= .8).length / ps.length; };
  const v = { adolescente: r3(f("adolescente")), adulto: r3(f("adulto")), crianca: r3(f("crianca")), mega: r3(f("mega")) };
  meta("P4", "o sparring nao trava", ">= 80 % dos pets tipicos a >= 0,8 contra as formas do estagio, no Champion e no Ultimate", v.adolescente >= .8 && v.adulto >= .8,
    { fracao_pets_acima_de_0_8: v, taxa_media: Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, r3(tx((S[e].pets as Conta[]).reduce((a, p) => ({ ...a, n: a.n + p.n, v: a.v + p.v }), novaConta())))])) });
  const esp = Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, Object.fromEntries(Object.entries(S[e].por_especie as Record<string, Conta>).map(([k, c]) => [k, r3(tx(c))]))]));
  const amp = Object.fromEntries(ESTAGIOS_LUTA.map(e => { const xs = Object.values(esp[e]) as number[]; return [e, r3(Math.max(...xs) - Math.min(...xs))]; }));
  meta("V2", "a especie nao decide sozinha", "da melhor a pior especie <= 0,15, em cada estagio (o pet tipico contra as formas do estagio)", Object.values(amp).every(x => (x as number) <= .15), { amplitude: amp, por_especie: esp });
}
/* ---------------------------------------------------------------- P5 */
if (tem("vida")) {
  const vs = G.vida.dados.vidas as { mega: boolean; estagio: string; morte: string | null }[];
  const f = vs.filter(v => v.mega).length / vs.length, est: Record<string, number> = {};
  for (const v of vs) est[v.estagio] = (est[v.estagio] ?? 0) + 1;
  meta("P5", "o dono simulado chega ao fim", ">= 80 % das vidas chegam ao Mega", f >= .8, { fracao_mega: r3(f), vidas: vs.length, estagio_final: est, mortes: vs.filter(v => v.morte).length });
}
/* ---------------------------------------------------------------- T1, T2, T3 */
if (tem("treino")) {
  const T = G.treino.dados;
  const t1 = Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, r3(tx(T.t1_tipico_contra_sem[e]))]));
  meta("T1", "o treino pesa", "o tipico contra o mesmo pet sem treino de 0,80 a 0,97, em cada estagio (8 mapas)", Object.values(t1).every(x => dentro(x as number, .8, .97)), { taxa: t1 });
  const t2 = Object.fromEntries(Object.entries(T.t2_um_stat_contra_sem as Record<string, Record<string, Conta>>).map(([e, m]) => [e, Object.fromEntries(Object.entries(m).map(([s, c]) => [s, r3(tx(c))]))]));
  const ok2 = Object.values(t2).every(m => { const xs = Object.values(m) as number[]; return Math.min(...xs) >= .6 && Math.max(...xs) - Math.min(...xs) <= .25; });
  meta("T2", "nenhum stat morto, nenhum dominante", "8 pontos num stat so contra o mesmo pet sem treino: cada stat >= 0,60; amplitude <= 0,25 (Rookie e Ultimate)", ok2, { taxa: t2 });
  const curva = Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, Object.fromEntries(Object.entries(T.t3_grade_contra_rivais[e] as Record<string, Conta>).map(([n, c]) => [n, r3(tx(c))]))]));
  let ok3 = true; const degrau: Record<string, number> = {}, noTeto: Record<string, number> = {};
  for (const e of ESTAGIOS_LUTA) {
    const ns = Object.keys(curva[e]).map(Number).sort((a, b) => a - b), xs = ns.map(n => curva[e][n] as number);
    let mx = 0; for (let i = 0; i + 2 < xs.length; i++) mx = Math.max(mx, xs[i + 2] - xs[i]);
    degrau[e] = r3(mx); noTeto[e] = xs[xs.length - 1];
    if (mx > .25 || xs[xs.length - 1] > .95) ok3 = false;
  }
  const tetoTip = r3(tx(T.t3_teto_contra_tipico.crianca));
  meta("T3", "o teto do treino", "no teto contra os rivais do estagio <= 0,95; degrau <= 0,25 a cada 4 pontos; no Rookie, o teto (10) contra o tipico (8) <= 0,70", ok3 && tetoTip <= .7,
    { no_teto: noTeto, maior_degrau_4_pontos: degrau, rookie_teto_contra_tipico: tetoTip, curva });
}
/* ---------------------------------------------------------------- E1 */
if (tem("estagio")) {
  const E = G.estagio.dados, v = Object.fromEntries(Object.entries(E as Record<string, Conta>).map(([k, c]) => [k, r3(tx(c))]));
  const ok = ["crianca_tipico_contra_adolescente", "adolescente_tipico_contra_adulto", "adulto_tipico_contra_mega"].every(k => dentro(v[k] as number, .1, .35))
    && ["crianca_tipico_contra_adulto", "adolescente_tipico_contra_mega"].every(k => (v[k] as number) <= .05)
    && ["crianca_teto_contra_adolescente", "adolescente_teto_contra_adulto", "adulto_teto_contra_mega"].every(k => (v[k] as number) <= .5);
  meta("E1", "a evolucao pesa mais que o treino", "tipico contra o estagio seguinte de 0,10 a 0,35; dois acima <= 0,05; o teto contra o seguinte <= 0,50", ok, { taxa: v });
}
/* ---------------------------------------------------------------- D1, D2: todas as lutas de todos os grupos */
{
  const est: Record<string, Conta> = {}, forma: Record<string, Conta> = {};
  for (const x of Object.values(G)) {
    for (const [e, c] of Object.entries(x.duracao.por_estagio as Record<string, Conta>)) est[e] = est[e] ? juntar(est[e], c) : c;
    for (const [f, c] of Object.entries(x.duracao.por_forma as Record<string, Conta>)) forma[f] = forma[f] ? juntar(forma[f], c) : c;
  }
  const porEst = Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, { mediana_s: quantil(est[e].relogio, .5), p90_s: quantil(est[e].relogio, .9), lutas: est[e].n }]));
  const medForma = Object.fromEntries(Object.entries(forma).map(([f, c]) => [f, quantil(c.relogio, .5)]));
  const curtas = Object.entries(medForma).filter(([, m]) => m < 8).map(([f, m]) => `${f} (${m} s)`);
  const ok1 = Object.values(porEst).every(x => dentro(x.mediana_s, 15, 40) && x.p90_s <= 60) && curtas.length === 0;
  meta("D1", "a duracao", "mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s", ok1,
    { por_estagio: porEst, formas_curtas: curtas, mediana_min_forma: Math.min(...Object.values(medForma)), mediana_max_forma: Math.max(...Object.values(medForma)) });
  const tot = Object.values(est).reduce((a, c) => juntar(a, c), novaConta()), semFim = tot.sem_fim / tot.n;
  const emp = Object.fromEntries(Object.entries(forma).map(([f, c]) => [f, c.e / c.n])), piores = Object.entries(emp).filter(([, x]) => x > .02).map(([f, x]) => `${f} (${r3(x)})`);
  meta("D2", "sem fim e empate", "lutas no limite <= 0,5 %; empates <= 2 % em cada forma", semFim <= .005 && piores.length === 0,
    { sem_fim: r3(semFim), lutas: tot.n, empate_total: r3(tot.e / tot.n), empate_max_forma: r3(Math.max(...Object.values(emp))), formas_acima_de_2pc: piores });
}
/* ---------------------------------------------------------------- A1, V1, S1 */
if (tem(...ESTAGIOS_LUTA.map(e => `formas_${e}`))) {
  const a1: Record<string, unknown> = {}, v1: Record<string, unknown> = {}, s1: Record<string, unknown> = {};
  let okA = true, okV = true, okS = true;
  const empForaEspelho: Record<string, Record<string, number>> = {};
  for (const e of ESTAGIOS_LUTA) {
    const F = G[`formas_${e}`].dados, fs = F.formas as string[], P = F.pares as Record<string, Record<string, Conta>>;
    const longe = fs.filter(atira), perto = fs.filter(f => !atira(f));
    /* A1: a forma que atira contra a de perto, nos dois lados */
    const lp = (m: string) => { let v = 0, n = 0; for (const x of longe) for (const y of perto) { const a = P[m][`${x}|${y}`], b = P[m][`${y}|${x}`]; v += a.v + (b.n - b.v - b.e); n += a.n + b.n; } return v / n; };
    const mapas = Object.keys(P), porMapa = Object.fromEntries(mapas.map(m => [m, r3(lp(m))]));
    let vs = 0, ns = 0; for (const m of mapas) for (const x of longe) for (const y of perto) { const a = P[m][`${x}|${y}`], b = P[m][`${y}|${x}`]; vs += a.v + (b.n - b.v - b.e); ns += a.n + b.n; }
    const soma = r3(vs / ns);
    if (!dentro(soma, .45, .55) || Object.values(porMapa).some(x => !dentro(x, .3, .7))) okA = false;
    a1[e] = { longe: longe.length, perto: perto.length, soma_8_mapas: soma, por_mapa: porMapa };
    /* V1: cada forma contra as outras, nos dois lados e nos 8 mapas */
    const taxaF: Record<string, number> = {}, vence: Record<string, number> = {};
    for (const x of fs) {
      let v = 0, n = 0, ganhos = 0;
      for (const y of fs) if (y !== x) {
        let vv = 0, nn = 0;
        for (const m of mapas) { const a = P[m][`${x}|${y}`], b = P[m][`${y}|${x}`]; vv += a.v + (b.n - b.v - b.e); nn += a.n + b.n; }
        v += vv; n += nn; if (vv / nn > .5) ganhos++;
      }
      taxaF[x] = r3(v / n); vence[x] = ganhos;
    }
    const xs = Object.values(taxaF), amp = r3(Math.max(...xs) - Math.min(...xs));
    if (xs.some(x => !dentro(x, .35, .65)) || amp > .3 || Object.values(vence).some(g => g < 2)) okV = false;
    v1[e] = { amplitude: amp, taxa: taxaF, vence_quantas: vence, nomes: Object.fromEntries(fs.map(f => [f, FORMAS_ARENA[f].nome])) };
    /* S1: o espelho, por mapa */
    /* a D-LP5-11: o lado A so nas lutas com vencedor; os empates ficam no D2 (e vao ao lado, para leitura) */
    const esp = Object.fromEntries(mapas.map(m => { const c = fs.reduce((a, f) => juntar(a, P[m][`${f}|${f}`]), novaConta()); if (c.n === c.e) throw new Error(`resumo: o espelho do ${e} no ${m} so empatou`); return [m, r3(c.v / (c.n - c.e))]; }));
    if (Object.values(esp).some(x => !dentro(x, .45, .55))) okS = false;
    const tudo = mapas.reduce((a, m) => fs.reduce((b, f) => juntar(b, P[m][`${f}|${f}`]), a), novaConta());
    s1[e] = { lado_a_com_vencedor: esp, leitura: { a: r3(tudo.v / tudo.n), b: r3((tudo.n - tudo.v - tudo.e) / tudo.n), empate: r3(tudo.e / tudo.n), a_sem_empates: r3(tudo.v / (tudo.n - tudo.e)) } };
    /* so leitura: os empates de cada forma fora do espelho (o D2 conta o espelho junto) */
    empForaEspelho[e] = Object.fromEntries(fs.map(f => { let em = 0, n = 0; for (const m of mapas) for (const y of fs) if (y !== f) for (const k of [`${f}|${y}`, `${y}|${f}`]) { em += P[m][k].e; n += P[m][k].n; } return [f, r3(em / n)]; }));
  }
  meta("A1", "de longe x de perto", "as que atiram contra as de perto: de 0,45 a 0,55 na soma dos 8 mapas; de 0,30 a 0,70 em cada mapa", okA, a1);
  meta("V1", "a variedade no estagio", "cada forma contra as outras de 0,35 a 0,65; amplitude <= 0,30; toda forma vence >= 2 outras", okV, v1);
  const D2 = metas.find(m => m.id === "D2");
  if (!D2) throw new Error("resumo: o D2 sumiu");
  D2.valores.leitura_empate_fora_do_espelho = Object.fromEntries(Object.entries(empForaEspelho).map(([e, m]) => [e, { max: Math.max(...Object.values(m)), acima_de_2pc: Object.entries(m).filter(([, x]) => x > .02).map(([f, x]) => `${f} (${x})`) }]));
  meta("S1", "o espelho", "o mesmo lutador dos dois lados: o lado A de 0,45 a 0,55 em cada mapa, so nas lutas com vencedor (D-LP5-11)", okS, s1);
}
/* ---------------------------------------------------------------- G1-G4 */
if (tem("torneios")) {
  const T = G.torneios.dados, liga = T.liga, g1 = liga.titulos / liga.tentativas;
  const porForma = Object.fromEntries(Object.entries(liga.por_forma as Record<string, { n: number; v: number }>).map(([f, x]) => [f, r3(x.v / x.n)]));
  const maxF = Math.max(...Object.values(porForma));
  meta("G1", "a Liga", "o Mega tipico ganha o titulo em >= 0,25 das tentativas; nenhuma forma acima de 0,85", g1 >= .25 && maxF <= .85, { titulos: r3(g1), max_forma: maxF, por_forma: porForma, vitorias: liga.vitorias });
  const rec = [...T.torre.recordes].sort((a: number, b: number) => a - b), med = rec.length % 2 ? rec[(rec.length - 1) / 2] : (rec[rec.length / 2 - 1] + rec[rec.length / 2]) / 2;
  const teto = T.torre.no_teto / T.torre.tentativas;
  meta("G2", "a Torre de Batalha", "recorde mediano de 3 a 30; o teto de 100 em <= 5 % das tentativas", dentro(med, 3, 30) && teto <= .05, { recorde_mediano: med, no_teto: r3(teto), recorde_min: rec[0], recorde_max: rec[rec.length - 1] });
  const fs = T.fabrica.series as Record<string, number>, umaSerie = Object.entries(fs).filter(([k]) => Number(k) >= 1).reduce((a, [, x]) => a + x, 0) / T.fabrica.tentativas;
  meta("G3", "a Fabrica", "uma serie de 3 vencida em >= 0,25 das tentativas", umaSerie >= .25, { ao_menos_uma_serie: r3(umaSerie), series: fs, tentativas: T.fabrica.tentativas });
  const sal = Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, r3(tx(T.salao[e]))]));
  meta("G4", "o Salao", "o pet tipico vence o rival do Salao de 0,70 a 0,95 em cada estagio", Object.values(sal).every(x => dentro(x as number, .7, .95)), { taxa: sal });
}

const ORDEM_METAS = ["P1", "P2", "P3", "P4", "P5", "T1", "T2", "T3", "E1", "D1", "D2", "D3", "A1", "V1", "V2", "G1", "G2", "G3", "G4", "S1"];
metas.sort((a, b) => ORDEM_METAS.indexOf(a.id) - ORDEM_METAS.indexOf(b.id));
if ((!parcial && metas.length !== 20) || metas.some(m => !ORDEM_METAS.includes(m.id))) throw new Error("resumo: as metas nao sao as 20 do plano");
const lutas = Object.values(G).reduce((a, x) => a + x.lutas, 0), segundos = Object.values(G).reduce((a, x) => a + x.segundos, 0);
const saida = { tarefa: "LUTA_POC, LP5, o resumo das metas", fase, faixa, parcial, grupos: Object.keys(G), commit: [...commits][0], candidato: JSON.parse([...candidatos][0]), lutas, segundos_somados: r3(segundos),
  passam: metas.filter(m => m.passa).map(m => m.id), falham: metas.filter(m => !m.passa).map(m => m.id), metas };
writeFileSync(dir + "resumo.json", JSON.stringify(saida, null, 1) + "\n");
const curto = (v: Record<string, unknown>): string => JSON.stringify(v).replace(/"/g, "").slice(0, 220);
const md = [`# Resumo das metas, ${fase}, ${faixa}`, "", `commit \`${saida.commit}\`, candidato \`${saida.candidato.nome}\`, ${lutas} lutas, ${r3(segundos)} s somados nos processos.`, "",
  `**Passam (${saida.passam.length}):** ${saida.passam.join(", ") || "nenhuma"}. **Falham (${saida.falham.length}):** ${saida.falham.join(", ") || "nenhuma"}.`, "",
  "| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |", "|---|---|---|---|---|",
  ...metas.map(m => `| ${m.id} | ${m.meta} | ${m.criterio} | ${m.passa ? "sim" : "**nao**"} | ${curto(m.valores).replace(/\|/g, "/")} |`), ""].join("\n");
writeFileSync(dir + "resumo.md", md);
console.log(md);
