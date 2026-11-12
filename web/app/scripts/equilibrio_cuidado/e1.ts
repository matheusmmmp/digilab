/* EQUILIBRIO_CUIDADO, E1: a calibracao (docs/PLANO_V3_EQUILIBRIO_CUIDADO.md, secao 3; as metas APROVADAS da secao 6 do plano de analise).
   A bancada do E0 (e0.ts) com as chaves do E1 ligadas: as mesmas 30 vidas (2 versoes x 3 donos x 5 sementes da calibracao 93101...93505),
   uma rodada por valor tentado. Cada rodada grava as 30 vidas, o resumo.json e o tabelas.md em
   scripts/medicoes/equilibrio_cuidado_e1/<rodada>/, e a grade.md junta a conta das metas de todas as rodadas ja rodadas, na ordem da GRADE.

     node scripts/equilibrio_cuidado/e1.ts --rodada <nome>     # uma rodada
     node scripts/equilibrio_cuidado/e1.ts --bloco <A|B|B4|C|E|F>   # as rodadas de um bloco, na ordem
     node scripts/equilibrio_cuidado/e1.ts --grade              # so refaz a grade.md com as rodadas ja gravadas

   A validacao (94101...94505) nao e tocada: a vida falha alto fora da faixa de calibracao (e0.ts). Um processo so. */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import { AJUSTE_E1_DESLIGADO, AJUSTE_E1_PROPOSTO, type AjusteEquilibrioE1 } from "../../motor/equilibrio_e1.ts";
import { CONFIG_EQUILIBRIO_CUIDADO } from "../../motor/digibrain/constantes.ts";
import { BITS, BITS_V2, type TabelaBits } from "../../src/bits.ts";
import { DONOS, SEMENTES_E0, VERSOES, vida, type OpcoesVida } from "./e0.ts";
import { resumir } from "./e0_resumo.ts";

export const PASTA_E1 = fileURLToPath(new URL("../medicoes/equilibrio_cuidado_e1/", import.meta.url));

const aj = (x: Partial<Omit<AjusteEquilibrioE1, "cerebro">> & { cerebro?: Partial<AjusteEquilibrioE1["cerebro"]> } = {}): AjusteEquilibrioE1 =>
  ({ ...AJUSTE_E1_DESLIGADO, ...x, cerebro: { ...CONFIG_EQUILIBRIO_CUIDADO, ...(x.cerebro ?? {}) } });
const bits = (x: Partial<TabelaBits>): TabelaBits => ({ ...BITS, ...x });

/** uma rodada da grade: o bloco, o que ela tenta e as chaves */
export interface Rodada { nome: string; bloco: string; tenta: string; opcoes: OpcoesVida }
/** a grade do E1, na ordem em que foi rodada (a calibracao mostra a grade, nao so o vencedor) */
export const GRADE: readonly Rodada[] = [
  { nome: "base", bloco: "-", tenta: "nenhuma chave (confere o E0 byte a byte)", opcoes: {} },
  /* A: o bebe come com a fome dele (EQ-7), o peso da entrada `bebe` no inato do comer */
  ...[256, 512, 768, 1024].map(w => ({ nome: `A_bebe_w${w}`, bloco: "A", tenta: `comer_bebe, w_comer_bebe = ${w}`,
    opcoes: { ajuste: aj({ cerebro: { comer_bebe: true, w_comer_bebe: w } }) } })),
  /* B: a fome que acorda; o urgencia_lambda dos inatos (a fome urgente: o sono, o convite, o passeio) e o lambda_acordar do sono */
  ...[576, 640, 768].map(u => ({ nome: `B_urg${u}`, bloco: "B", tenta: `urgencia_lambda = ${u}`, opcoes: { ajuste: aj({ urgencia_lambda: u }) } })),
  { nome: "B_urg896", bloco: "B", tenta: "urgencia_lambda = 896", opcoes: { ajuste: aj({ urgencia_lambda: 896 }) } },
  ...[870, 1000].map(l => ({ nome: `B_acordar${l}`, bloco: "B", tenta: `lambda_acordar = ${l}`, opcoes: { ajuste: aj({ lambda_acordar: l }) } })),
  /* B4: o brincar do Rookie do atento, o vies do brincar no W0 (hoje -256) e o w_bola_do_dono (hoje 4 096) */
  ...[-128, 0, 128].map(v => ({ nome: `B4_vies${v}`, bloco: "B4", tenta: `vies do brincar = ${v}`, opcoes: { ajuste: aj({ vies_brincar: v }) } })),
  { nome: "B4_bola2048", bloco: "B4", tenta: "w_bola_do_dono = 2 048", opcoes: { ajuste: aj({ w_bola_do_dono: 2048 }) } },
  /* C: a guarda da fome urgente no brincar (EQ-7) */
  { nome: "C_guarda", bloco: "C", tenta: "guarda_fome_brincar", opcoes: { ajuste: aj({ cerebro: { guarda_fome_brincar: true } }) } },
  /* E: os Bits (so do jogo): o cuidado na hora certa e o teto do dia */
  ...([[2, 20], [3, 20], [3, 30], [4, 30], [4, 40]] as const).map(([c, t]) => ({ nome: `E_cuidado${c}_teto${t}`, bloco: "E",
    tenta: `Bits: cuidado = ${c}, teto do dia = ${t}`, opcoes: { bits: bits({ cuidado: c, tetoCuidadoDia: t }) } })),
  ...([[5, 40, 50], [4, 40, 60], [5, 40, 60]] as const).map(([c, t, e]) => ({ nome: `E_cuidado${c}_teto${t}_evo${e}`, bloco: "E",
    tenta: `Bits: cuidado = ${c}, teto do dia = ${t}, evolucao para o Rookie = ${e}`,
    opcoes: { bits: bits({ cuidado: c, tetoCuidadoDia: t, evolucao: { ...BITS.evolucao, crianca: e } }) } })),
  /* F: tudo junto; o F1 e o F2 diferem so na fome urgente */
  ...([768, 640] as const).map((u, i) => ({ nome: `F${i + 1}_todas_urg${u}`, bloco: "F",
    tenta: `bebe w 512, urgencia_lambda ${u}, vies do brincar 0, guarda; Bits cuidado 5, teto 40, Rookie 60`,
    opcoes: { ajuste: aj({ cerebro: { comer_bebe: true, guarda_fome_brincar: true, w_comer_bebe: 512 }, urgencia_lambda: u, vies_brincar: 0 }),
      bits: bits({ cuidado: 5, tetoCuidadoDia: 40, evolucao: { ...BITS.evolucao, crianca: 60 } }) } })),
  ...([[768, 640], [512, 576], [512, 704]] as const).map(([w, u], i) => ({ nome: `F${i + 3}_todas_bebe${w}_urg${u}`, bloco: "F",
    tenta: `bebe w ${w}, urgencia_lambda ${u}, vies do brincar 0, guarda; Bits cuidado 5, teto 40, Rookie 60`,
    opcoes: { ajuste: aj({ cerebro: { comer_bebe: true, guarda_fome_brincar: true, w_comer_bebe: w }, urgencia_lambda: u, vies_brincar: 0 }),
      bits: bits({ cuidado: 5, tetoCuidadoDia: 40, evolucao: { ...BITS.evolucao, crianca: 60 } }) } })),
  /* o escolhido: o F2, pelas constantes (AJUSTE_E1_PROPOSTO e BITS_V2); as 30 vidas tem de sair as do F2, byte a byte */
  { nome: "E1_escolhido", bloco: "F", tenta: "o F2 pelas constantes AJUSTE_E1_PROPOSTO e BITS_V2", opcoes: { ajuste: AJUSTE_E1_PROPOSTO, bits: BITS_V2 } },
];

/** as 30 vidas de uma rodada, gravadas na pasta dela, e o resumo */
export function rodar(r: Rodada): void {
  const pasta = `${PASTA_E1}${r.nome}/`;
  mkdirSync(pasta, { recursive: true });
  for (const versao of VERSOES) for (const dono of DONOS) for (const s of SEMENTES_E0) {
    const v = vida(versao, dono, s, 3, false, r.opcoes);
    writeFileSync(`${pasta}${versao}_${dono}_${s}.json`, JSON.stringify(v, null, 1) + "\n");
  }
  writeFileSync(`${pasta}rodada.json`, JSON.stringify({ nome: r.nome, bloco: r.bloco, tenta: r.tenta, opcoes: r.opcoes }, null, 1) + "\n");
  resumir(pasta, `o E1, rodada ${r.nome} (${r.tenta}): media [min; max] das 5 sementes da calibracao`);
}

interface MetaGravada { id: string; dono: string; hoje: string; passa: boolean | null }
/** a grade.md: por rodada ja gravada, as metas que nao passam (id, dono, versao) e o valor de cada meta que o E0 reprovou */
export function grade(): string {
  const ler = (nome: string): MetaGravada[] | null => {
    const f = `${PASTA_E1}${nome}/resumo.json`;
    return existsSync(f) ? (JSON.parse(readFileSync(f, "utf8")) as { metas: MetaGravada[] }).metas : null;
  };
  const e0 = (JSON.parse(readFileSync(fileURLToPath(new URL("../medicoes/equilibrio_cuidado_e0/resumo.json", import.meta.url)), "utf8")) as { metas: MetaGravada[] }).metas;
  const chave = (m: MetaGravada) => `${m.id} ${m.dono} ${m.hoje.slice(0, 3)}`;
  const falhas0 = e0.filter(m => m.passa === false).map(chave);
  const linhas = ["# A grade do E1 (gerada por scripts/equilibrio_cuidado/e1.ts --grade)", "",
    `As metas que o E0 reprovou: ${falhas0.join("; ")}.`, "",
    "| rodada | bloco | o que tenta | metas que nao passam | passam agora (das do E0) | passavam no E0 e caem |", "|---|---|---|---|---|---|"];
  for (const r of GRADE) {
    const ms = ler(r.nome);
    if (ms === null) continue;
    const falhas = ms.filter(m => m.passa === false).map(chave);
    const consertou = falhas0.filter(f => !falhas.includes(f)), quebrou = falhas.filter(f => !falhas0.includes(f));
    linhas.push(`| ${r.nome} | ${r.bloco} | ${r.tenta} | ${falhas.length} | ${consertou.join("; ") || "—"} | ${quebrou.join("; ") || "—"} |`);
  }
  linhas.push("", "## O valor de cada meta reprovada no E0, por rodada", "");
  const ids = [...new Set(e0.filter(m => m.passa === false).map(chave))];
  for (const id of ids) {
    linhas.push(`### ${id}`, "", `- E0: ${e0.find(m => chave(m) === id)!.hoje}`);
    for (const r of GRADE) {
      const ms = ler(r.nome);
      const m = ms?.find(x => chave(x) === id);
      if (m) linhas.push(`- ${r.nome}: ${m.hoje} (${m.passa === null ? "sem dado" : m.passa ? "passa" : "não passa"})`);
    }
    linhas.push("");
  }
  const texto = linhas.join("\n") + "\n";
  writeFileSync(`${PASTA_E1}grade.md`, texto);
  return texto;
}

function argumento(nome: string): string | null {
  const i = process.argv.indexOf(`--${nome}`);
  if (i < 0) return null;
  const v = process.argv[i + 1];
  if (v === undefined || v.startsWith("--")) throw new Error(`--${nome} sem valor`);
  return v;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const nome = argumento("rodada"), bloco = argumento("bloco");
  const rodadas = nome !== null ? GRADE.filter(r => r.nome === nome) : bloco !== null ? GRADE.filter(r => r.bloco === bloco) : [];
  if ((nome !== null || bloco !== null) && !rodadas.length) throw new Error(`nenhuma rodada: ${nome ?? bloco}`);
  if (nome === null && bloco === null && !process.argv.includes("--grade")) throw new Error("use --rodada, --bloco ou --grade");
  for (const r of rodadas) {
    const t0 = Date.now();
    rodar(r);
    console.log(`${r.nome}: ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  }
  console.log(grade());
}
