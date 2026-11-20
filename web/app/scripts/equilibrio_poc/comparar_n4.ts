/* LUTA_POC, a investigacao do nucleo, N4 (docs/PLANO_LUTA_NUCLEO.md, secao 8.2): le os resumo.json das 10 medidas da faixa investigacao e
   compara cada contrafactual com a base da mesma luta (as medidas 2 a 8 com a n4_base_v23; a 10 com a n4_base_v29). So leitura: nenhuma luta.
   Para cada meta: se passa, um numero curto de leitura por estagio e as regras da secao 8.2 (move, quebra, nao age), sobre esse numero.
   uso (em web/app): node scripts/equilibrio_poc/comparar_n4.ts -> scripts/medicoes/luta_nucleo/n4/comparacao.json e comparacao.md */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type J = any;
const MED = fileURLToPath(new URL("../medicoes/equilibrio_poc/", import.meta.url)), SAIDA = fileURLToPath(new URL("../medicoes/luta_nucleo/n4/", import.meta.url));
const MEDIDAS: readonly [string, string][] = [
  ["n4_atr100", "n4_base_v23"], ["n4_atr115", "n4_base_v23"], ["n4_atr125", "n4_base_v23"], ["n4_morto", "n4_base_v23"], ["n4_pulo", "n4_base_v23"],
  ["n4_borda", "n4_base_v23"], ["n4_juntas_v23", "n4_base_v23"], ["n4_juntas_v29", "n4_base_v29"],
];
const ler = (fase: string): J => {
  const r = JSON.parse(readFileSync(`${MED}${fase}/investigacao/resumo.json`, "utf-8"));
  if (r.faixa !== "investigacao" || r.parcial) throw new Error(`comparar_n4: ${fase} nao e uma medida inteira da investigacao`);
  return r;
};
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const EST = ["crianca", "adolescente", "adulto", "mega"];
/** um numero de leitura por chave, para cada meta, com a faixa dele (PROPOSTO: o da secao 2 do plano da LP5); null = sem faixa numerica */
type Leitura = Record<string, { v: number; faixa: [number, number] }>;
const npcs = (v: J): Leitura => Object.fromEntries(Object.values(v as Record<string, J>).flatMap((x: J) => [
  [`${x.nome}_sem`, { v: x.sem_treino, faixa: [0, x.limite_sem] }], [`${x.nome}_tip`, { v: x.tipico, faixa: [x.limite_tipico, 1] }]]));
const porEst = (o: Record<string, number>, faixa: [number, number]): Leitura => Object.fromEntries(EST.filter(e => e in o).map(e => [e, { v: o[e], faixa }]));
const LEITURA: Record<string, (v: J) => Leitura> = {
  P1: v => ({ sem: { v: v.sem_treino, faixa: [0, v.limite_sem] }, tip: { v: v.tipico, faixa: [v.limite_tipico, 1] } }),
  P2: npcs, P3: npcs,
  P4: v => porEst({ adolescente: v.fracao_pets_acima_de_0_8.adolescente, adulto: v.fracao_pets_acima_de_0_8.adulto }, [.8, 1]),
  P5: v => ({ mega: { v: v.fracao_mega, faixa: [.8, 1] } }),
  T1: v => porEst(v.taxa, [.8, .97]),
  T2: v => Object.fromEntries(["crianca", "adulto"].map(e => [`${e}_folego`, { v: v.taxa[e].folego, faixa: [.6, 1] }])),
  T3: v => ({ ...Object.fromEntries(Object.entries(porEst(v.no_teto, [0, .95])).map(([k, x]) => [`teto_${k}`, x])), rookie_teto_tipico: { v: v.rookie_teto_contra_tipico, faixa: [0, .7] },
    ...Object.fromEntries(Object.entries(porEst(v.maior_degrau_4_pontos, [0, .25])).map(([k, x]) => [`degrau_${k}`, x])) }),
  E1: v => Object.fromEntries(Object.entries(v.taxa as Record<string, number>).map(([k, x]) => [k, { v: x, faixa: k.includes("teto") ? [0, .5] : /crianca_tipico_contra_adulto|adolescente_tipico_contra_mega/.test(k) ? [0, .05] : [.1, .35] }])),
  D1: v => Object.fromEntries(EST.map(e => [e, { v: v.por_estagio[e].mediana_s, faixa: [15, 40] }])),
  D2: v => ({ empate_total: { v: v.empate_total, faixa: [0, .02] }, empate_max_forma: { v: v.empate_max_forma, faixa: [0, .02] } }),
  D3: v => ({ p90_s: { v: v.p90_s, faixa: [0, 180] } }),
  A1: v => Object.fromEntries(EST.flatMap(e => [[`${e}_soma`, { v: v[e].soma_8_mapas, faixa: [.45, .55] }], [`${e}_ringue`, { v: v[e].por_mapa.ringue, faixa: [.3, .7] }], [`${e}_castelo`, { v: v[e].por_mapa.castelo, faixa: [.3, .7] }]])),
  A2: v => Object.fromEntries(EST.map(e => [e, { v: v[e].mediana_px, faixa: [90, 1e9] }])),
  V1: v => Object.fromEntries(EST.map(e => [e, { v: v[e].amplitude, faixa: [0, .3] }])),
  V2: v => porEst(v.amplitude, [0, .15]),
  G1: v => ({ titulos: { v: v.titulos, faixa: [.25, 1] } }),
  G2: v => ({ recorde_mediano: { v: v.recorde_mediano, faixa: [3, 30] } }),
  G3: v => ({ series: { v: v.ao_menos_uma_serie, faixa: [.25, 1] } }),
  G4: v => porEst(v.taxa, [.7, .95]),
  S1: v => Object.fromEntries(EST.flatMap(e => {
    const xs = Object.entries(v[e].lado_a_com_vencedor as Record<string, number>).filter(([m]) => m !== "praia").map(([, x]) => x);
    return [[`${e}_min`, { v: Math.min(...xs), faixa: [.45, .55] }], [`${e}_max`, { v: Math.max(...xs), faixa: [.45, .55] }]];
  })),
};
/** a distancia ate a faixa (0 dentro) */
const fora = (x: number, [a, b]: [number, number]) => x < a ? a - x : x > b ? x - b : 0;
const porId = (r: J) => Object.fromEntries((r.metas as J[]).map(m => [m.id, m]));

const out: Record<string, unknown> = { tarefa: "LUTA_POC, investigacao do nucleo, N4", medidas: {} };
const md: string[] = ["# A N4: os contrafactuais contra a base (faixa investigacao)", "", "Le os resumo.json de scripts/medicoes/equilibrio_poc/n4_*/investigacao/. As regras sao as da secao 8.2 do plano: **move** = entra na faixa ou chega 0,05 mais perto dela; **quebra** = passava na base e falha; **nao age** = toda diferenca abaixo de 0,02. O G1 conta titulos (0 na base).", ""];
const bases: Record<string, J> = { n4_base_v23: ler("n4_base_v23"), n4_base_v29: ler("n4_base_v29") };
md.push("## Quantas metas passam", "", "| medida | passam | as que passam |", "|---|---|---|");
for (const f of ["n4_base_v23", ...MEDIDAS.slice(0, 7).map(x => x[0]), "n4_base_v29", "n4_juntas_v29"]) {
  const r = f in bases ? bases[f] : ler(f), p = (r.metas as J[]).filter(m => m.passa).map(m => m.id);
  md.push(`| ${f} | ${p.length} | ${p.join(", ")} |`);
}
for (const [fase, baseF] of MEDIDAS) {
  const r = ler(fase), mb = porId(bases[baseF]), mr = porId(r), metas: Record<string, unknown> = {};
  md.push("", `## ${fase} contra ${baseF}`, "", "| meta | base | com a chave | o que muda (a leitura: base -> chave) |", "|---|---|---|---|");
  for (const id of Object.keys(LEITURA)) {
    const lb = LEITURA[id](mb[id].valores), lr = LEITURA[id](mr[id].valores), mudou: string[] = [];
    let move = false, naoAge = true;
    for (const k of Object.keys(lb)) {
      const a = lb[k], b = lr[k]; if (!b) throw new Error(`comparar_n4: ${fase} ${id} sem ${k}`);
      const d = b.v - a.v; if (Math.abs(d) >= .02 * (Math.abs(a.v) > 2 ? Math.abs(a.v) : 1)) naoAge = false;
      if ((fora(b.v, b.faixa) === 0 && fora(a.v, a.faixa) > 0) || fora(a.v, a.faixa) - fora(b.v, b.faixa) >= .05 * (a.faixa[1] > 2 ? a.faixa[1] : 1)) move = true;
      if (Math.abs(d) >= .02) mudou.push(`${k} ${r3(a.v)} -> ${r3(b.v)}`);
    }
    const quebra = mb[id].passa && !mr[id].passa;
    const leitura = quebra ? "quebra" : mr[id].passa && !mb[id].passa ? "passa a passar" : move ? "move" : naoAge ? "nao age" : "muda sem chegar";
    metas[id] = { base_passa: mb[id].passa, passa: mr[id].passa, leitura, base: lb, chave: lr };
    md.push(`| ${id} | ${mb[id].passa ? "passa" : "falha"} | ${mr[id].passa ? "passa" : "falha"} (${leitura}) | ${mudou.slice(0, 8).join("; ") || "—"} |`);
  }
  (out.medidas as Record<string, unknown>)[fase] = { base: baseF, commit: r.commit, metas };
}
mkdirSync(SAIDA, { recursive: true });
writeFileSync(SAIDA + "comparacao.json", JSON.stringify(out, null, 1) + "\n");
writeFileSync(SAIDA + "comparacao.md", md.join("\n") + "\n");
console.log(`comparar_n4: ${SAIDA}comparacao.json e comparacao.md`);
