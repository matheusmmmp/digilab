/* EQUILIBRIO_CUIDADO, E0: junta os 30 JSON das vidas (scripts/medicoes/equilibrio_cuidado_e0/) nas tabelas do retrato, com as metas
   PROPOSTAS da secao 6 do plano ao lado, e grava o resumo.json e o tabelas.md na mesma pasta.

     node scripts/equilibrio_cuidado/e0_resumo.ts

   A conta por semente (secao 4 e 6 do plano): no grupo, as razoes (racao comida, fome < 0,45, explorar, brincar, chutes por lance) somam
   os dois pets, e as contagens (minutos de fome alta, cochilos, saude, energia ao acordar) sao a media dos dois. Depois, a media das 5
   sementes, o minimo e o maximo. "Passa" = a media cumpre a meta; nas metas de sim ou nao (M-E1, M-D1), as 5 sementes. */
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { DONOS, PASTA_E0, SEMENTES_E0, VERSOES, type NomeDono, type NomeVersao } from "./e0.ts";

interface Cel {
  estagio: string; dia: number; minutos: number; fome_025: number; fome_045: number; postas: number; comidas: number; comidas_por_ele: number;
  cochilos: number; decisoes: number; explorar: number; brincar: number; lances: number; chutes: number; energia_mediana_ao_acordar: number | null;
}
interface Pet { ident: string; celulas: Cel[]; saude_fim_do_dia: { dia: number; saude: number }[]; morte: unknown; pronto_champion_pelo_tempo: number | null }
interface Vida { versao: NomeVersao; numero_versao: number; dono: NomeDono; semente: number; pets: Pet[];
  tamer: { bits_total: number; bits_por_dia: Record<string, number>; bits_por_origem: Record<string, number>; tick_150: number | null; dia_150: number | null;
    tick_pronto_champion: number | null; ha_150_antes_do_champion: boolean | null } }

let PASTA = PASTA_E0;
const ler = (v: NomeVersao, d: NomeDono, s: number): Vida => JSON.parse(readFileSync(`${PASTA}${v}_${d}_${s}.json`, "utf8"));
const media = (xs: number[]): number => xs.reduce((a, b) => a + b, 0) / xs.length;
const razao = (a: number, b: number): number | null => b > 0 ? a / b : null;
/** media, minimo e maximo das sementes que tem o valor (n = quantas) */
interface Est { media: number | null; min: number | null; max: number | null; n: number }
function est(xs: (number | null)[]): Est {
  const v = xs.filter((x): x is number => x !== null && Number.isFinite(x));
  return v.length ? { media: media(v), min: Math.min(...v), max: Math.max(...v), n: v.length } : { media: null, min: null, max: null, n: 0 };
}
const CELULAS = [["In-Training", 1], ["Rookie", 1], ["Rookie", 2], ["Rookie", 3]] as const;
const DIAS = [1, 2, 3] as const;

/** as medidas de uma celula numa vida (secao 4) */
function medidasCelula(vd: Vida, estagio: string, dia: number) {
  const cs = vd.pets.map(p => p.celulas.find(c => c.estagio === estagio && c.dia === dia) ?? null);
  if (cs.some(c => c === null)) throw new Error(`celula ${estagio}/${dia} faltando em ${vd.versao}/${vd.dono}/${vd.semente}`);
  const c = cs as Cel[], soma = (k: keyof Cel) => c.reduce((a, x) => a + (x[k] as number), 0);
  const energias = c.map(x => x.energia_mediana_ao_acordar).filter((x): x is number => x !== null);
  return {
    racao_comida: razao(soma("comidas"), soma("postas")), postas: soma("postas") / c.length,
    fome_025_min: soma("fome_025") / c.length, fome_045_frac: razao(soma("fome_045"), soma("minutos")),
    cochilos: soma("cochilos") / c.length, energia_ao_acordar: energias.length ? media(energias) : null,
    explorar_frac: razao(soma("explorar"), soma("decisoes")), brincar_frac: razao(soma("brincar"), soma("decisoes")),
    lances: soma("lances") / c.length, chutes_por_lance: razao(soma("chutes"), soma("lances")),
  };
}
type Medidas = ReturnType<typeof medidasCelula>;
/** as medidas de um dia inteiro (as celulas do dia somadas): a fome alta, os cochilos, a saude no fim e os Bits */
function medidasDia(vd: Vida, dia: number) {
  const cs = vd.pets.map(p => p.celulas.filter(c => c.dia === dia));
  const porPet = (k: keyof Cel) => media(cs.map(l => l.reduce((a, x) => a + (x[k] as number), 0)));
  return {
    fome_025_min: porPet("fome_025"), cochilos: porPet("cochilos"),
    saude_fim: media(vd.pets.map(p => p.saude_fim_do_dia.find(x => x.dia === dia)!.saude)),
    bits: vd.tamer.bits_por_dia[String(dia)] ?? 0,
  };
}

/** as tabelas e as metas das 30 vidas de uma pasta (a do E0, ou a de uma rodada do E1); grava o resumo.json e o tabelas.md nela */
export function resumir(pasta: string = PASTA_E0, descricao = "o retrato do E0 (docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md): media [min; max] das 5 sementes",
                        sementes: readonly number[] = SEMENTES_E0) {
PASTA = pasta;
if (sementes.length !== 5) throw new Error(`o resumo e de 5 sementes: ${sementes.length}`);
const resumo: Record<string, unknown> = {};
const linhas: string[] = [];
const f = (x: number | null, d = 2): string => x === null ? "—" : x.toFixed(d);
const fe = (e: Est, d = 2): string => e.n === 0 ? "—" : `${f(e.media, d)} [${f(e.min, d)}; ${f(e.max, d)}]`;
/** a meta: o teste sobre a media; null = nao se aplica ou sem dado */
interface Meta { id: string; medida: string; meta: string; dono: NomeDono; hoje: string; passa: boolean | null }
const metas: Meta[] = [];
const passaMedia = (e: Est, ok: (x: number) => boolean): boolean | null => e.media === null ? null : ok(e.media);
const todas = (xs: (boolean | null)[]): boolean | null => xs.some(x => x === false) ? false : xs.every(x => x === null) ? null : true;
const sn = (b: boolean | null): string => b === null ? "sem dado" : b ? "passa" : "**não passa**";

for (const versao of VERSOES) {
  for (const dono of DONOS) {
    const vidas = sementes.map(s => ler(versao, dono, s));
    const numero = vidas[0]!.numero_versao;
    const porCel: Record<string, Record<string, Est>> = {};
    for (const [estagio, dia] of CELULAS) {
      const ms = vidas.map(v => medidasCelula(v, estagio, dia));
      porCel[`${estagio}|${dia}`] = Object.fromEntries((Object.keys(ms[0]!) as (keyof Medidas)[]).map(k => [k, est(ms.map(m => m[k]))]));
    }
    const porDia: Record<string, Record<string, Est>> = {};
    for (const dia of DIAS) {
      const ms = vidas.map(v => medidasDia(v, dia));
      porDia[String(dia)] = Object.fromEntries((Object.keys(ms[0]!) as (keyof typeof ms[0])[]).map(k => [k, est(ms.map(m => m[k]))]));
    }
    /* os chutes por lance da vida inteira (os lances sao poucos por celula) */
    const chutesVida = est(vidas.map(v => razao(v.pets.reduce((a, p) => a + p.celulas.reduce((b, c) => b + c.chutes, 0), 0),
                                                 v.pets.reduce((a, p) => a + p.celulas.reduce((b, c) => b + c.lances, 0), 0))));
    const lancesVida = est(vidas.map(v => v.pets.reduce((a, p) => a + p.celulas.reduce((b, c) => b + c.lances, 0), 0) / v.pets.length));
    const t = {
      bits_total: est(vidas.map(v => v.tamer.bits_total)), dia_150: est(vidas.map(v => v.tamer.dia_150)),
      tick_150_pet: est(vidas.map(v => v.tamer.tick_150 === null ? null : v.tamer.tick_150 - 480)),
      tick_pronto_champion_pet: est(vidas.map(v => v.tamer.tick_pronto_champion === null ? null : v.tamer.tick_pronto_champion - 480)),
      ha_150_antes: vidas.map(v => v.tamer.ha_150_antes_do_champion),
      bits_por_origem: Object.fromEntries(["chamado", "cuidado", "evolucao", "nivel", "pausa", "luta"].map(o => [o, est(vidas.map(v => v.tamer.bits_por_origem[o] ?? 0))])),
      mortes: vidas.reduce((a, v) => a + v.pets.filter(p => p.morte !== null).length, 0),
    };
    resumo[`${versao}|${dono}`] = { numero_versao: numero, celulas: porCel, dias: porDia, chutes_por_lance_vida: chutesVida, lances_por_pet_vida: lancesVida, tamer: t };

    /* as metas (secao 6 do plano) */
    const rook = ["Rookie|1", "Rookie|2", "Rookie|3"], cels = ["In-Training|1", ...rook];
    const m = (id: string, medida: string, meta: string, hoje: string, passa: boolean | null) => metas.push({ id, medida, meta, dono, hoje: `v${numero}: ${hoje}`, passa });
    const mostra = (ks: string[], k: string, d = 2) => ks.map(c => `${c.replace("|", " d")} ${fe(porCel[c]![k]!, d)}`).join("; ");
    const mostraDia = (k: string, d = 0) => DIAS.map(x => `d${x} ${fe(porDia[String(x)]![k]!, d)}`).join("; ");
    if (dono !== "relapso") m("M-A1", "ração comida", "≥ 0,8 em cada estágio", mostra(cels, "racao_comida"), todas(cels.map(c => passaMedia(porCel[c]!["racao_comida"]!, x => x >= .8))));
    if (dono === "atento") {
      m("M-A2", "fome < 0,25 (min)", "≤ 60 min/dia; 0 no In-Training", `In-Training ${fe(porCel["In-Training|1"]!["fome_025_min"]!, 0)}; ${mostraDia("fome_025_min")}`,
        todas([passaMedia(porCel["In-Training|1"]!["fome_025_min"]!, x => x === 0), ...DIAS.map(x => passaMedia(porDia[String(x)]!["fome_025_min"]!, y => y <= 60))]));
      m("M-A4", "fome < 0,45 (fração do tempo)", "≤ 0,30", mostra(cels, "fome_045_frac"), todas(cels.map(c => passaMedia(porCel[c]!["fome_045_frac"]!, x => x <= .3))));
      m("M-B4", "brincar (fração das decisões)", "≥ 0,05 no Rookie", mostra(rook, "brincar_frac", 3), todas(rook.map(c => passaMedia(porCel[c]!["brincar_frac"]!, x => x >= .05))));
      m("M-E2", "Bits por dia", "≥ 20 nos três dias", mostraDia("bits"), todas(DIAS.map(x => passaMedia(porDia[String(x)]!["bits"]!, y => y >= 20))));
    }
    if (dono === "medio") m("M-A3", "fome < 0,25 (min)", "≤ 180 min/dia", mostraDia("fome_025_min"), todas(DIAS.map(x => passaMedia(porDia[String(x)]!["fome_025_min"]!, y => y <= 180))));
    const lim = { atento: .9, medio: .7, relapso: .3 }[dono];
    m("M-A5", "saúde no fim do dia", `≥ ${String(lim).replace(".", ",")}`, mostraDia("saude_fim", 2), todas(DIAS.map(x => passaMedia(porDia[String(x)]!["saude_fim"]!, y => y >= lim))));
    m("M-B1", "cochilos por dia", "de 2 a 6 nos dias 2 e 3", mostraDia("cochilos", 1), todas([2, 3].map(x => passaMedia(porDia[String(x)]!["cochilos"]!, y => y >= 2 && y <= 6))));
    m("M-B2", "energia mediana ao acordar", "≥ 0,9", mostra(rook, "energia_ao_acordar"), todas(rook.map(c => passaMedia(porCel[c]!["energia_ao_acordar"]!, x => x >= .9))));
    if (dono !== "relapso") m("M-B3", "explorar (fração das decisões)", "≥ 0,10 no Rookie", mostra(rook, "explorar_frac"), todas(rook.map(c => passaMedia(porCel[c]!["explorar_frac"]!, x => x >= .1))));
    m("M-C1", "chutes por lance (a vida)", "≥ 0,8", `${fe(chutesVida)} (lances por pet ${fe(lancesVida, 1)})`, passaMedia(chutesVida, x => x >= .8));
    if (dono !== "relapso") m("M-E1", "★★ (150 Bits) antes do Champion", "nas 5 sementes",
      `150 no min ${fe(t.tick_150_pet, 0)} do pet; o tempo do Champion no min ${fe(t.tick_pronto_champion_pet, 0)}; ${t.ha_150_antes.filter(x => x).length}/5`,
      t.ha_150_antes.every(x => x === true));
    m("M-D1", "mortes", "0", String(t.mortes), t.mortes === 0);
  }
}

/* o tabelas.md: por versao, uma tabela por dono com as celulas, uma com os dias, e a das metas */
for (const versao of VERSOES) for (const dono of DONOS) {
  const r = resumo[`${versao}|${dono}`] as { numero_versao: number; celulas: Record<string, Record<string, Est>>; dias: Record<string, Record<string, Est>>; tamer: Record<string, any> };
  linhas.push(`### ${versao === "pet" ? "O ovo de um pet" : "O grupo do brasão"} (v${r.numero_versao}), o ${dono}`, "",
    "| estágio, dia | ração comida | rações postas | fome < 0,25 (min) | fome < 0,45 (fração) | cochilos | energia ao acordar | explorar | brincar | lances | chutes por lance |",
    "|---|---|---|---|---|---|---|---|---|---|---|");
  for (const [estagio, dia] of CELULAS) {
    const c = r.celulas[`${estagio}|${dia}`]!;
    linhas.push(`| ${estagio}, ${dia} | ${fe(c["racao_comida"]!)} | ${fe(c["postas"]!, 1)} | ${fe(c["fome_025_min"]!, 0)} | ${fe(c["fome_045_frac"]!)} | ${fe(c["cochilos"]!, 1)} | ${fe(c["energia_ao_acordar"]!)} | ${fe(c["explorar_frac"]!)} | ${fe(c["brincar_frac"]!, 3)} | ${fe(c["lances"]!, 1)} | ${fe(c["chutes_por_lance"]!)} |`);
  }
  linhas.push("", "| dia | fome < 0,25 (min) | cochilos | saúde no fim | Bits do Tamer |", "|---|---|---|---|---|");
  for (const dia of DIAS) { const d = r.dias[String(dia)]!; linhas.push(`| ${dia} | ${fe(d["fome_025_min"]!, 0)} | ${fe(d["cochilos"]!, 1)} | ${fe(d["saude_fim"]!)} | ${fe(d["bits"]!, 0)} |`); }
  const t = r.tamer, o = t["bits_por_origem"] as Record<string, Est>;
  linhas.push("", `Bits no total: ${fe(t["bits_total"], 0)} (chamado ${fe(o["chamado"]!, 0)}, cuidado na hora ${fe(o["cuidado"]!, 0)}, evolução ${fe(o["evolucao"]!, 0)}, nível do Tamer ${fe(o["nivel"]!, 0)}); `
    + `os 150 no minuto ${fe(t["tick_150_pet"], 0)} do pet (dia ${fe(t["dia_150"], 0)}); o tempo do Champion no minuto ${fe(t["tick_pronto_champion_pet"], 0)}; mortes: ${t["mortes"]}.`, "");
}
linhas.push("### As metas PROPOSTAS (seção 6 do plano)", "", "| id | medida | meta PROPOSTA | dono | hoje: média [mín; máx] | passa hoje? |", "|---|---|---|---|---|---|");
for (const x of [...metas].sort((a, b) => a.id.localeCompare(b.id) || DONOS.indexOf(a.dono) - DONOS.indexOf(b.dono) || a.hoje.localeCompare(b.hoje)))
  linhas.push(`| ${x.id} | ${x.medida} | ${x.meta} | ${x.dono} | ${x.hoje} | ${sn(x.passa)} |`);

writeFileSync(`${PASTA}resumo.json`, JSON.stringify({ descricao, resumo, metas }, null, 1) + "\n");
writeFileSync(`${PASTA}tabelas.md`, linhas.join("\n") + "\n");
return { resumo, metas, linhas };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) console.log(resumir().linhas.join("\n"));
