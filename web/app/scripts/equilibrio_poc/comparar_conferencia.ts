/* LUTA_POC, LP5-4 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.4 e secao 7): a tabela de todas as metas, na calibracao e na conferencia, com o
   candidato final. Le os dois resumo.json e grava, ao lado do da conferencia, o comparacao.json e o comparacao.md. Nenhum numero muda por
   causa dela: a meta que reprova fica como esta, com o valor da calibracao ao lado.
   uso (em web/app): node scripts/equilibrio_poc/comparar_conferencia.ts --calibracao lp5_3 --candidato lp5_3 [--conferencia lp5_4|lp6_3] */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { argumento } from "./comum.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type J = any;
const faseCal = argumento("calibracao"), nome = argumento("candidato"), faseConf = argumento("conferencia", "lp5_4");
if (faseConf !== "lp5_4" && faseConf !== "lp6_3") throw new Error(`comparar: a conferencia e a da LP5-4 ou a da LP6-3, nao ${faseConf}`);
const dirMed = (s: string) => fileURLToPath(new URL(`../medicoes/equilibrio_poc/${s}/`, import.meta.url));
const ler = (arq: string): J => JSON.parse(readFileSync(arq, "utf-8"));
const cal = ler(dirMed(faseCal) + "calibracao/resumo.json"), conf = ler(dirMed(faseConf) + "conferencia/resumo.json");
for (const [r, faixa] of [[cal, "calibracao"], [conf, "conferencia"]] as const) {
  if (r.candidato?.nome !== nome) throw new Error(`comparar: o resumo da ${faixa} e do candidato ${r.candidato?.nome}, nao do ${nome}`);
  if (r.faixa !== faixa) throw new Error(`comparar: o resumo esperado da ${faixa} e da ${r.faixa}`);
  if (r.parcial) throw new Error(`comparar: o resumo da ${faixa} e parcial`);
}
/* os numeros do candidato sao os mesmos nas duas faixas */
if (JSON.stringify(cal.candidato) !== JSON.stringify(conf.candidato)) throw new Error("comparar: o candidato da conferencia nao e o da calibracao");
const porId = (r: J) => Object.fromEntries((r.metas as J[]).map(m => [m.id, m]));
const mc = porId(cal), mf = porId(conf);
const ids = Object.keys(mc);
if (ids.join() !== Object.keys(mf).join()) throw new Error("comparar: as metas da calibracao e da conferencia nao sao as mesmas");
const curto = (v: unknown) => JSON.stringify(v).replace(/"/g, "").slice(0, 160);
const linhas = ids.map(id => ({ id, meta: mc[id].meta, criterio: mc[id].criterio, calibracao: mc[id].passa, conferencia: mf[id].passa, valores_calibracao: mc[id].valores, valores_conferencia: mf[id].valores }));
const mudou = linhas.filter(l => l.calibracao !== l.conferencia).map(l => l.id);
const saida = {
  tarefa: faseConf === "lp5_4" ? "LUTA_POC, LP5-4, a conferencia" : "LUTA_POC, LP6-3, a conferencia", candidato: nome,
  commit_calibracao: cal.commit, commit_conferencia: conf.commit,
  passam_calibracao: cal.passam, passam_conferencia: conf.passam, mudaram: mudou, metas: linhas,
};
const dir = dirMed(faseConf) + "conferencia/";
writeFileSync(dir + "comparacao.json", JSON.stringify(saida, null, 1) + "\n");
const sim = (b: boolean) => b ? "sim" : "**nao**";
writeFileSync(dir + "comparacao.md", [
  `# A conferencia do ${nome} (${faseConf === "lp5_4" ? "LP5-4" : "LP6-3"})`, "",
  `A calibracao no commit \`${cal.commit}\` (${cal.passam.length} de ${ids.length}); a conferencia no \`${conf.commit}\` (${conf.passam.length} de ${ids.length}).`,
  `Mudaram de lado: ${mudou.length ? mudou.join(", ") : "nenhuma"}.`, "",
  "| # | a meta | calibracao | conferencia | os valores na calibracao | os valores na conferencia |", "|---|---|---|---|---|---|",
  ...linhas.map(l => `| ${l.id} | ${l.meta} | ${sim(l.calibracao)} | ${sim(l.conferencia)} | ${curto(l.valores_calibracao)} | ${curto(l.valores_conferencia)} |`), "",
].join("\n"));
console.log(`comparar: ${conf.passam.length} de ${ids.length} na conferencia; mudaram ${mudou.join(", ") || "nenhuma"}`);
