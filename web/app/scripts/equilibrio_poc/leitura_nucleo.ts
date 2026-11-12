/* LUTA_POC, a investigacao do nucleo, N1 (docs/PLANO_LUTA_NUCLEO.md, secoes 1.2 e 2; D-N-1): as releituras (M0) e as contas (M1). So
   leitura: nenhuma luta nova. Le os JSON das medidas inteiras que ja estao no repositorio e separa cada meta pelo atributo do par (o
   triangulo de motor/arena/sim.ts, VENCE: o Vaccine vence o Virus, o Virus o Data, o Data o Vaccine; o Free e o None ficam fora).
   - "+" = o lado lido tem a vantagem do atributo; "-" = a desvantagem; "0" = nenhum dos dois.
   - o piso e o teto dos NPCs (a H-ATR com a H-REGUA): se o "+" sempre vence e o "-" sempre perde, o sem treino fica >= a fracao "+" e o
     tipico <= 1 - a fracao "-". As duas contas sao HIPOTESE: a leitura mostra a taxa medida de cada lado ao lado.
   uso (em web/app): node scripts/equilibrio_poc/leitura_nucleo.ts -> scripts/medicoes/luta_nucleo/n1/leitura.json e leitura.md */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { FORMAS_ARENA, LIGA, chaveSprite, formaLiga, type Forma } from "../../motor/index.ts";
import { VENCE } from "../../motor/arena/index.ts";
import { ESTAGIOS_LUTA, TIPICO, commitAtual, type Conta } from "./comum.ts";
import { limitesNpc } from "./criterios.ts";
import { LP5_3 } from "./candidatos.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type J = any;
const MED = fileURLToPath(new URL("../medicoes/equilibrio_poc/", import.meta.url));
const SAIDA = fileURLToPath(new URL("../medicoes/luta_nucleo/n1/", import.meta.url));
/** as medidas inteiras lidas: a v21 (lp5_0), o fim da LP5-1 (lp5_1_r2), a v23 (lp5_3), a v29 (lp6_3_u120) e a conferencia da v23 (lp5_4) */
const FASES: readonly string[] = ["lp5_0/calibracao", "lp5_1_r2/calibracao", "lp5_3/calibracao", "lp6_3_u120/calibracao", "lp5_4/conferencia"];
const ler = (fase: string, g: string): J => {
  const p = `${MED}${fase}/${g}.json`;
  if (!existsSync(p)) throw new Error(`leitura: falta ${p}`);
  return JSON.parse(readFileSync(p, "utf-8"));
};
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const atr = (chave: string): string => { const f = FORMAS_ARENA[chave]; if (!f) throw new Error(`leitura: ${chave} fora da tabela`); return f.atributo; };
/** o atributo do par, do lado de x contra y */
export function catAtr(x: string, y: string): "+" | "-" | "0" {
  const a = atr(x), b = atr(y);
  if (VENCE[a as keyof typeof VENCE] === b) return "+";
  if (VENCE[b as keyof typeof VENCE] === a) return "-";
  return "0";
}
type Acc = { n: number; v: number; e: number };
const acc = (): Acc => ({ n: 0, v: 0, e: 0 });
const tx = (a: Acc): number | null => a.n ? r3(a.v / a.n) : null;
/** a vitoria do lado x no par (x, y) num mapa, pelos dois lados (como o resumo_metas: a.v + as derrotas do outro lado) */
const doisLados = (P: Record<string, Conta>, x: string, y: string): Acc => {
  const a = P[`${x}|${y}`], b = P[`${y}|${x}`];
  if (!a || !b) throw new Error(`leitura: falta o par ${x}|${y}`);
  return { n: a.n + b.n, v: a.v + (b.n - b.v - b.e), e: a.e + b.e };
};
const somar = (a: Acc, b: Acc) => { a.n += b.n; a.v += b.v; a.e += b.e; };
const atira = (k: string) => !!FORMAS_ARENA[k].golpe.proj;

const out: Record<string, unknown> = { tarefa: "LUTA_POC, investigacao do nucleo, N1", commit: commitAtual(), fases: FASES };

/* ---------------------------------------------------------------- M0-a: as formas pelo atributo (V1, A1), por fase e estagio */
const formas: Record<string, unknown> = {};
for (const fase of FASES) {
  const porEst: Record<string, unknown> = {};
  for (const e of ESTAGIOS_LUTA) {
    const j = ler(fase, `formas_${e}`).dados, fs = j.formas as string[], P = j.pares as Record<string, Record<string, Conta>>, mapas = Object.keys(P);
    /* cada par ordenado de formas diferentes, num mapa, conta uma vez (o lado a); a "fracao decidida" e a dos pares com taxa <= 0,1 ou >= 0,9 */
    const cat: Record<string, Acc> = { "+": acc(), "0": acc(), "-": acc() };
    let decididos = 0, pares = 0;
    for (const m of mapas) for (const k of Object.keys(P[m])) {
      const [x, y] = k.split("|"); if (x === y) continue;
      const c = P[m][k]; somar(cat[catAtr(x, y)], { n: c.n, v: c.v, e: c.e });
      pares++; if (c.v / c.n <= .1 || c.v / c.n >= .9) decididos++;
    }
    /* V1 previsto so pelo atributo: a taxa de cada forma contra as outras, com a media do estagio em cada classe (+, 0, -) */
    const media = { "+": cat["+"].v / cat["+"].n, "0": cat["0"].v / cat["0"].n, "-": cat["-"].v / cat["-"].n };
    const v1: Record<string, { medida: number; prevista: number; mais: number; menos: number }> = {};
    for (const x of fs) {
      const t = acc(); let prev = 0, nPrev = 0, mais = 0, menos = 0;
      for (const y of fs) if (y !== x) {
        const c = acc(); for (const m of mapas) somar(c, doisLados(P[m], x, y));
        somar(t, c); const k = catAtr(x, y); prev += media[k] * c.n; nPrev += c.n; if (k === "+") mais++; if (k === "-") menos++;
      }
      v1[x] = { medida: r3(t.v / t.n), prevista: r3(prev / nPrev), mais, menos };
    }
    const med = Object.values(v1).map(z => z.medida), pre = Object.values(v1).map(z => z.prevista), mm = med.reduce((a, b) => a + b, 0) / med.length;
    const sst = med.reduce((a, b) => a + (b - mm) ** 2, 0), sse = med.reduce((a, b, i) => a + (b - pre[i]) ** 2, 0);
    /* A1 pelo atributo: a forma que atira contra a de perto, pelos dois lados, so nos pares neutros e em todos (como o resumo_metas) */
    const longe = fs.filter(atira), perto = fs.filter(k => !atira(k));
    const a1: Record<string, { todos: number | null; neutros: number | null; pares_neutros: number; pares: number }> = {};
    for (const m of [...mapas, "soma"]) {
      const todos = acc(), neutros = acc(); let pn = 0, pt = 0;
      for (const x of longe) for (const y of perto) {
        const neutro = catAtr(x, y) === "0"; pt++; if (neutro) pn++;
        for (const mm2 of m === "soma" ? mapas : [m]) { const c = doisLados(P[mm2], x, y); somar(todos, c); if (neutro) somar(neutros, c); }
      }
      a1[m] = { todos: tx(todos), neutros: tx(neutros), pares_neutros: pn, pares: pt };
    }
    porEst[e] = {
      por_atributo: Object.fromEntries(Object.entries(cat).map(([k, a]) => [k, { taxa: tx(a), empates: a.n ? r3(a.e / a.n) : null, lutas: a.n }])),
      fracao_pares_decididos: r3(decididos / pares), pares_mapa: pares,
      v1: { formas: v1, r2_atributo: r3(1 - sse / sst), maior_erro: r3(Math.max(...med.map((x, i) => Math.abs(x - pre[i])))) },
      a1: { longe: longe.length, perto: perto.length, por_mapa: a1 },
    };
  }
  formas[fase] = porEst;
}
out.formas = formas;

/* ---------------------------------------------------------------- M0-b: os NPCs pelo atributo (P2, P3), o piso e o teto */
const DESAFIANTES = new Set(["npc_tier2_sentinela", "npc_tier2_porteiro", "npc_v5_puppetmon", "npc_v5_machinedramon"]);
const lideres: Record<string, unknown> = {};
for (const fase of ["lp5_3/calibracao", "lp5_4/conferencia"]) {
  const L = ler(fase, "lideres").dados, porNpc: Record<string, unknown> = {};
  for (const [k, x] of Object.entries(L as Record<string, J>)) {
    const lim = limitesNpc(x.estagio, DESAFIANTES.has(k)), lados: Record<string, unknown> = {};
    let fMais = 0, fMenos = 0;
    for (const lado of ["sem_treino", "tipico"]) {
      const c: Record<string, Acc> = { "+": acc(), "0": acc(), "-": acc() };
      for (const [f, r] of Object.entries(x[lado].por_forma as Record<string, Conta>)) somar(c[catAtr(f, k)], { n: r.n, v: r.v, e: r.e });
      const n = c["+"].n + c["0"].n + c["-"].n;
      fMais = c["+"].n / n; fMenos = c["-"].n / n;
      lados[lado] = { taxa: r3(x[lado].total.v / x[lado].total.n), por_atributo: Object.fromEntries(Object.entries(c).map(([q, a]) => [q, { taxa: tx(a), lutas: a.n }])) };
    }
    const piso = r3(fMais), teto = r3(1 - fMenos);
    porNpc[k] = {
      nome: x.nome, estagio: x.estagio, mapa: x.mapa, lutas_serie: x.lutas_serie, atributo: atr(k), desafiante: DESAFIANTES.has(k), limites: lim,
      fracao_mais: piso, fracao_menos: r3(fMenos), piso_sem_treino: piso, teto_tipico: teto,
      cabe_pelo_atributo: piso <= lim.sem && teto >= lim.tip, ...lados,
    };
  }
  lideres[fase] = porNpc;
}
out.lideres = lideres;

/* ---------------------------------------------------------------- M0-c: a especie (V2) e o colosso (P5) pelo atributo */
const sp = ler("lp5_3/calibracao", "sparring").dados, especie: Record<string, unknown> = {};
for (const e of ESTAGIOS_LUTA) {
  const rv = sp[e].rivais as string[], porEsp: Record<string, { pets: number; fracao_mais: number; fracao_menos: number; taxa: number }> = {};
  const soma: Record<string, { p: number; mais: number; menos: number; n: number; v: number }> = {};
  for (const p of sp[e].pets as { chave: string; especie: string; n: number; v: number }[]) {
    const s = soma[p.especie] ??= { p: 0, mais: 0, menos: 0, n: 0, v: 0 };
    s.p++; s.n += p.n; s.v += p.v;
    s.mais += rv.filter(y => catAtr(p.chave, y) === "+").length / rv.length; s.menos += rv.filter(y => catAtr(p.chave, y) === "-").length / rv.length;
  }
  for (const [k, s] of Object.entries(soma)) porEsp[k] = { pets: s.p, fracao_mais: r3(s.mais / s.p), fracao_menos: r3(s.menos / s.p), taxa: r3(s.v / s.n) };
  especie[e] = porEsp;
}
const vida = ler("lp5_2/leitura_vida", "leitura"), rvChamp = sp.adolescente.rivais as string[];
out.especie_lp5_3 = especie;
out.colosso_lp5_2 = Object.fromEntries(Object.entries(vida.por_forma as Record<string, J>).map(([k, x]) => [k, {
  digimon: FORMAS_ARENA[k].digimon, atributo: atr(k), de_perto: !atira(k), taxa_sparring: x.motor, n: x.n,
  fracao_mais: r3(rvChamp.filter(y => catAtr(k, y) === "+").length / rvChamp.length), fracao_menos: r3(rvChamp.filter(y => catAtr(k, y) === "-").length / rvChamp.length),
}]));

/* ---------------------------------------------------------------- M1-a: as series pelo atributo (G1, G2) */
const megas = Object.keys(FORMAS_ARENA).filter(k => FORMAS_ARENA[k].estagio === "Mega" && !k.startsWith("npc_"));
const liga = LIGA.map((_, i) => chaveSprite(formaLiga(i) as Forma));
out.liga_atributo = {
  rivais: liga.map(k => ({ chave: k, digimon: FORMAS_ARENA[k].digimon, atributo: atr(k) })),
  por_forma_do_pet: Object.fromEntries(megas.map(k => [k, { atributo: atr(k), rivais_com_desvantagem: liga.filter(y => catAtr(k, y) === "-").length, rivais_com_vantagem: liga.filter(y => catAtr(k, y) === "+").length }])),
  fracao_formas_sem_rival_mais_forte: r3(megas.filter(k => liga.every(y => catAtr(k, y) !== "-")).length / megas.length),
};
const tor = ler("lp5_3/calibracao", "torneios").dados;
out.torneios_lp5_3 = { liga_vitorias: tor.liga.vitorias, torre_vitorias: tor.torre.vitorias, fabrica_series: tor.fabrica.series };

/* ---------------------------------------------------------------- M1-b: as contas sobre as constantes (o gama da v23, o pulo) */
const G = LP5_3.gama, pot = (s: number, g: number) => s ** g;
const neutro = LP5_3.mapa.neutro, medioMega = neutro + LP5_3.pesoPonto * TIPICO.mega / 6, folego8 = neutro + LP5_3.pesoPonto * 8;
const agil8 = pot(folego8 / neutro, LP5_3.esquiva.gamaFolego);
out.contas_v23 = {
  gama: G,
  fator_no_stat: Object.fromEntries([.1, .5, 2, 8].map(f => [String(f), Object.fromEntries(Object.entries(G).map(([k, g]) => [k, r3(pot(f, g))]))])),
  tipico_mega_stat_medio: r3(medioMega), tipico_mega_razao: Object.fromEntries(Object.entries(G).map(([k, g]) => [k, r3(pot(medioMega / neutro, g))])),
  atributo_razao_do_dano: r3(1.5 * 1.5),
  folego_com_8_pontos: folego8, agilidade_com_8_pontos: r3(agil8), pulo_px_neutro: r3(380 * .18), pulo_px_8_pontos: r3(380 * agil8 * .18),
  fabrica_com_cura_a_0_5: .125,
};

/* ---------------------------------------------------------------- a saida */
mkdirSync(SAIDA, { recursive: true });
writeFileSync(SAIDA + "leitura.json", JSON.stringify(out, null, 1) + "\n");
const md: string[] = [`# A leitura da N1 (LUTA_POC, investigacao do nucleo)`, "", `commit \`${out.commit}\`; so leitura dos JSON de ${FASES.join(", ")}. O inteiro esta no leitura.json.`, "",
  "## As formas pelo atributo (a taxa do lado a, por classe do par)", "", "| fase | estagio | + | 0 | - | empates 0 | pares decididos | V1: R2 do atributo | V1: maior erro |", "|---|---|---|---|---|---|---|---|---|"];
for (const [fase, pe] of Object.entries(formas as Record<string, Record<string, J>>)) for (const [e, x] of Object.entries(pe))
  md.push(`| ${fase} | ${e} | ${x.por_atributo["+"].taxa} | ${x.por_atributo["0"].taxa} | ${x.por_atributo["-"].taxa} | ${x.por_atributo["0"].empates} | ${x.fracao_pares_decididos} | ${x.v1.r2_atributo} | ${x.v1.maior_erro} |`);
md.push("", "## O A1 nos pares neutros (v23, lp5_3 e v29, lp6_3_u120)", "", "| fase | estagio | mapa | todos | neutros | pares neutros |", "|---|---|---|---|---|---|");
for (const fase of ["lp5_3/calibracao", "lp6_3_u120/calibracao"]) for (const e of ESTAGIOS_LUTA) { const a = (formas as J)[fase][e].a1; for (const [m, z] of Object.entries(a.por_mapa as Record<string, J>)) md.push(`| ${fase} | ${e} | ${m} | ${z.todos} | ${z.neutros} | ${z.pares_neutros} de ${z.pares} |`); }
md.push("", "## Os NPCs: o piso e o teto pelo atributo (lp5_3, calibracao)", "", "| NPC | atributo | limite sem / tipico | sem treino | tipico | piso (fracao +) | teto (1 - fracao -) | cabe? | sem: + / 0 / - | tipico: + / 0 / - |", "|---|---|---|---|---|---|---|---|---|---|");
for (const z of Object.values((lideres as J)["lp5_3/calibracao"] as Record<string, J>)) {
  const t = (l: string) => ["+", "0", "-"].map(q => z[l].por_atributo[q].taxa ?? "—").join(" / ");
  md.push(`| ${z.nome} | ${z.atributo} | ${z.limites.sem} / ${z.limites.tip} | ${z.sem_treino.taxa} | ${z.tipico.taxa} | ${z.piso_sem_treino} | ${z.teto_tipico} | ${z.cabe_pelo_atributo ? "sim" : "nao"} | ${t("sem_treino")} | ${t("tipico")} |`);
}
md.push("", "## O colosso (P5) pelo atributo", "", "| forma | Digimon | atributo | de perto | sparring | fracao + | fracao - |", "|---|---|---|---|---|---|---|");
for (const [k, z] of Object.entries(out.colosso_lp5_2 as Record<string, J>)) md.push(`| ${k} | ${z.digimon} | ${z.atributo} | ${z.de_perto ? "sim" : "nao"} | ${z.taxa_sparring} | ${z.fracao_mais} | ${z.fracao_menos} |`);
md.push("", "## A especie (V2) pelo atributo (lp5_3, o pet tipico no sparring)", "", "| estagio | especie | pets | fracao + | fracao - | taxa |", "|---|---|---|---|---|---|");
for (const [e, pe] of Object.entries(especie as Record<string, Record<string, J>>)) for (const [k, z] of Object.entries(pe)) md.push(`| ${e} | ${k} | ${z.pets} | ${z.fracao_mais} | ${z.fracao_menos} | ${z.taxa} |`);
const la = out.liga_atributo as J;
md.push("", "## A Liga pelo atributo", "", `Rivais: ${la.rivais.map((r: J) => `${r.digimon} (${r.atributo})`).join(", ")}. Fracao das formas Mega sem nenhum rival com vantagem sobre elas: ${la.fracao_formas_sem_rival_mais_forte}.`,
  "", `As vitorias na Liga (lp5_3): ${JSON.stringify(tor.liga.vitorias)}. Na Torre: ${JSON.stringify(tor.torre.vitorias)}. As series da Fabrica: ${JSON.stringify(tor.fabrica.series)}.`,
  "", "## As contas sobre as constantes (v23)", "", "```", JSON.stringify(out.contas_v23, null, 1), "```", "");
writeFileSync(SAIDA + "leitura.md", md.join("\n"));
console.log(`leitura: ${SAIDA}leitura.json e leitura.md`);
