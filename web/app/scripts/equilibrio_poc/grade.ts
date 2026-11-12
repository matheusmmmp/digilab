/* LUTA_POC, LP5-1 a LP5-3 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.2): a grade. Le um JSON com os candidatos (as trocas sobre o v21, de
   candidatos.ts), os grupos, os tamanhos menores e o numero de bases da calibracao; roda cada (candidato, grupo) em ate 4 processos (a V3-D8)
   e, no fim, o resumo parcial de cada candidato e a tabela da grade. A grade so escolhe: o candidato escolhido roda a medida inteira depois.
   uso (em web/app): node scripts/equilibrio_poc/grade.ts --grade scripts/medicoes/equilibrio_poc/lp5_1/r1/grade.json [--processos 4]
   -> ao lado do grade.json: uma pasta por candidato (os JSON dos grupos e o resumo) e o tabela.json e tabela.md */
import { spawn } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { argumento } from "./comum.ts";
import { candidatoDe, type Troca } from "./candidatos.ts";
import { GRUPOS } from "./bancada.ts";

interface Grade { fase: string; bases: number; grupos: string[]; tam: Record<string, number>; candidatos: Troca[] }
const arq = resolve(argumento("grade")), processos = Number(argumento("processos", "4"));
if (!(Number.isInteger(processos) && processos >= 1 && processos <= 4)) throw new Error(`grade: de 1 a 4 processos (V3-D8), nao ${processos}`);
const g = JSON.parse(readFileSync(arq, "utf-8")) as Grade, raiz = dirname(arq);
if (!/^lp5_[123]$|^lp6_3$/.test(g.fase)) throw new Error(`grade: fase invalida ${g.fase}`);
for (const x of g.grupos) if (!(GRUPOS as readonly string[]).includes(x) || x === "vida") throw new Error(`grade: grupo invalido ${x}`);
const nomes = new Set<string>();
for (const t of g.candidatos) { candidatoDe(t); if (nomes.has(t.nome)) throw new Error(`grade: candidato repetido ${t.nome}`); nomes.add(t.nome); }

const aqui = (f: string) => fileURLToPath(new URL(f, import.meta.url));
const rodar = (script: string, args: string[]): Promise<void> => new Promise((ok, falha) => {
  const p = spawn(process.execPath, [aqui(script), ...args], { stdio: ["ignore", "ignore", "inherit"] });
  p.on("exit", cod => cod === 0 ? ok() : falha(new Error(`${script} ${args.join(" ")}: codigo ${cod}`)));
});
/* os grupos caros primeiro */
const PESO: Record<string, number> = { tiro: 4.5, formas_mega: 9, formas_adulto: 8, formas_adolescente: 7, treino: 6, torneios: 5, sparring: 4, lideres: 3, formas_crianca: 2, estagio: 1 };
const fila: { t: Troca; grupo: string }[] = [];
for (const t of g.candidatos) {
  const dir = `${raiz}/${t.nome}/`;
  mkdirSync(dir, { recursive: true });
  writeFileSync(dir + "candidato.json", JSON.stringify(t, null, 1) + "\n");
  for (const grupo of g.grupos) fila.push({ t, grupo });
}
fila.sort((a, b) => (PESO[b.grupo] ?? 0) - (PESO[a.grupo] ?? 0));
const t0 = Date.now();
let feitos = 0;
await Promise.all(Array.from({ length: processos }, async () => {
  for (let x = fila.shift(); x; x = fila.shift()) {
    const dir = `${raiz}/${x.t.nome}/`;
    await rodar("bancada.ts", ["--grade", "--grupo", x.grupo, "--faixa", "calibracao", "--fase", g.fase, "--candidato-json", dir + "candidato.json",
      "--tam", JSON.stringify(g.tam), "--bases", String(g.bases), "--saida", dir]);
    feitos++;
    if (feitos % 10 === 0) console.log(`grade: ${feitos} de ${g.candidatos.length * g.grupos.length} em ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
}));
for (const t of g.candidatos) await rodar("resumo_metas.ts", ["--faixa", "calibracao", "--fase", g.fase, "--pasta", `${raiz}/${t.nome}/`, "--parcial"]);

/* a tabela: o passa e os numeros que decidem de cada meta, por candidato */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type J = any;
const r2 = (x: number) => Math.round(x * 100) / 100;
const linha = (m: J): string => {
  const v = m.valores;
  switch (m.id) {
    case "T1": return Object.values(v.taxa).map(x => r2(x as number)).join("/");
    case "T2": return Object.entries(v.taxa as Record<string, Record<string, number>>).map(([, s]) => { const xs = Object.values(s); return `${r2(Math.min(...xs))}-${r2(Math.max(...xs))}`; }).join(" ");
    case "T3": return `teto ${Object.values(v.no_teto).map(x => r2(x as number)).join("/")}; degrau ${Object.values(v.maior_degrau_4_pontos).map(x => r2(x as number)).join("/")}; r10x8 ${r2(v.rookie_teto_contra_tipico)}`;
    case "E1": return ["crianca_tipico_contra_adolescente", "adolescente_tipico_contra_adulto", "adulto_tipico_contra_mega"].map(k => r2(v.taxa[k])).join("/")
      + `; 2x ${["crianca_tipico_contra_adulto", "adolescente_tipico_contra_mega"].map(k => r2(v.taxa[k])).join("/")}; teto ${["crianca_teto_contra_adolescente", "adolescente_teto_contra_adulto", "adulto_teto_contra_mega"].map(k => r2(v.taxa[k])).join("/")}`;
    case "D1": return Object.values(v.por_estagio as Record<string, { mediana_s: number; p90_s: number }>).map(x => `${x.mediana_s}|${x.p90_s}`).join(" ") + `; min forma ${v.mediana_min_forma}`;
    case "D2": return `max ${v.empate_max_forma}; sem fim ${v.sem_fim}`;
    case "A1": return Object.values(v as Record<string, { soma_8_mapas: number }>).map(x => r2(x.soma_8_mapas)).join("/");
    case "V1": return Object.values(v as Record<string, { amplitude: number; taxa: Record<string, number> }>).map(x => `${r2(Math.min(...Object.values(x.taxa)))}-${r2(Math.max(...Object.values(x.taxa)))}`).join(" ");
    case "V2": return Object.values(v.amplitude).map(x => r2(x as number)).join("/");
    case "S1": return Object.values(v as Record<string, { lado_a_com_vencedor: Record<string, number> }>).map(x => { const xs = Object.values(x.lado_a_com_vencedor); return `${r2(Math.min(...xs))}-${r2(Math.max(...xs))}`; }).join(" ");
    case "A2": return Object.values(v as Record<string, { mediana_px: number; ate_48px: number }>).map(x => `${x.mediana_px}|${r2(x.ate_48px)}`).join(" ");
    case "P4": return Object.values(v.taxa_media).map(x => r2(x as number)).join("/");
    default: return JSON.stringify(v).slice(0, 80);
  }
};
const tabela = g.candidatos.map(t => {
  const r = JSON.parse(readFileSync(`${raiz}/${t.nome}/resumo.json`, "utf-8"));
  return { nome: t.nome, troca: t, passam: r.passam as string[], falham: r.falham as string[], metas: Object.fromEntries((r.metas as J[]).map(m => [m.id, { passa: m.passa, curto: linha(m) }])) };
});
writeFileSync(`${raiz}/tabela.json`, JSON.stringify({ tarefa: "LUTA_POC, LP5, a grade", fase: g.fase, bases: g.bases, tam: g.tam, grupos: g.grupos, segundos: (Date.now() - t0) / 1000, tabela }, null, 1) + "\n");
const ids = Object.keys(tabela[0].metas);
const md = [`# A grade ${raiz.split(/[\\/]/).slice(-2).join("/")} (${g.fase}; ${g.bases} base(s); ${((Date.now() - t0) / 1000).toFixed(0)} s)`, "",
  `| candidato | passam | ${ids.join(" | ")} |`, `|---|---|${ids.map(() => "---").join("|")}|`,
  ...tabela.map(x => `| ${x.nome} | ${x.passam.length} | ${ids.map(i => `${x.metas[i].passa ? "**ok** " : ""}${x.metas[i].curto.replace(/\|/g, "/")}`).join(" | ")} |`), ""].join("\n");
writeFileSync(`${raiz}/tabela.md`, md);
console.log(md);
