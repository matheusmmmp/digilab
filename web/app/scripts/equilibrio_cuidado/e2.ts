/* EQUILIBRIO_CUIDADO, E2: a validacao unica (docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md, secao 9, o adendo 1, registrado antes). A bancada
   do E0 (e0.ts) no modo de validacao, com a F2 do E1 e as chaves ligadas (o AJUSTE_E1_PROPOSTO e a BITS_V2, como a rodada E1_escolhido), nas
   30 vidas: 2 versoes (os ovos de hoje antes do E3: a v35 e a v37, o NUMERO_VERSAO de e0.ts) x 3 donos x as 5 sementes da validacao (94101...94505). Roda UMA vez: recusa
   rodar se a pasta ja tem vidas. Grava as vidas, o resumo.json, o tabelas.md, o rodada.json e o comparacao.md (cada linha de meta no E0, no E1
   da calibracao e no E2) em scripts/medicoes/equilibrio_cuidado_e2/.

     node scripts/equilibrio_cuidado/e2.ts            # a validacao (uma vez)
     node scripts/equilibrio_cuidado/e2.ts --tabela   # so refaz o comparacao.md com as vidas ja gravadas

   Um processo so. */
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import { AJUSTE_E1_PROPOSTO } from "../../motor/equilibrio_e1.ts";
import { VERSAO_V35 } from "../../motor/index.ts";
import { BITS_V2 } from "../../src/bits.ts";
import { DONOS, VERSOES, vida, type OpcoesVida } from "./e0.ts";
import { resumir } from "./e0_resumo.ts";

export const PASTA_E2 = fileURLToPath(new URL("../medicoes/equilibrio_cuidado_e2/", import.meta.url));
/** as 5 sementes da validacao (o adendo 1): as bases da faixa 94101...94505 */
export const SEMENTES_E2 = [94101, 94202, 94303, 94404, 94505] as const;
/** a configuracao validada: a F2 com as chaves ligadas, no modo de validacao */
export const OPCOES_E2: OpcoesVida = { ajuste: AJUSTE_E1_PROPOSTO, bits: BITS_V2, validacao: true };

const vidasGravadas = (pasta: string): string[] =>
  existsSync(pasta) ? readdirSync(pasta).filter(f => /^(pet|grupo)_(atento|medio|relapso)_\d+\.json$/.test(f)) : [];

/** a validacao: as 30 vidas, uma vez. Falha alto se a pasta ja tem alguma vida */
export function validar(pasta: string = PASTA_E2): void {
  const ja = vidasGravadas(pasta);
  if (ja.length) throw new Error(`a validacao roda uma vez so: ${pasta} ja tem ${ja.length} vidas`);
  mkdirSync(pasta, { recursive: true });
  for (const versao of VERSOES) for (const dono of DONOS) for (const s of SEMENTES_E2) {
    const t0 = Date.now(), v = vida(versao, dono, s, 3, false, OPCOES_E2);
    writeFileSync(`${pasta}${versao}_${dono}_${s}.json`, JSON.stringify(v, null, 1) + "\n");
    console.log(`${versao} ${dono} ${s}: ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  }
  writeFileSync(`${pasta}rodada.json`, JSON.stringify({ nome: "E2_validacao", sementes: SEMENTES_E2, opcoes: OPCOES_E2 }, null, 1) + "\n");
  resumir(pasta, "o E2, a validacao unica (adendo 1): a F2 com as chaves ligadas; media [min; max] das 5 sementes da validacao", SEMENTES_E2);
}

interface MetaGravada { id: string; medida: string; meta: string; dono: string; hoje: string; passa: boolean | null }
const lerMetas = (f: string): MetaGravada[] => (JSON.parse(readFileSync(f, "utf8")) as { metas: MetaGravada[] }).metas;
/** a versao de uma linha de meta, pelo numero no comeco do `hoje` (o pet e sempre a v35; o grupo mudou de v36 para v37) */
const versaoDe = (m: MetaGravada): "pet" | "grupo" => m.hoje.startsWith(`v${VERSAO_V35}:`) ? "pet" : "grupo";
const chave = (m: MetaGravada): string => `${m.id}|${m.dono}|${versaoDe(m)}`;
const sn = (b: boolean | null | undefined): string => b === undefined ? "—" : b === null ? "sem dado" : b ? "passa" : "**não passa**";

/** o comparacao.md: cada linha de meta no E0, no E1 (a rodada E1_escolhido, na calibracao) e no E2, e a conta */
export function comparar(pasta: string = PASTA_E2): string {
  const e0 = lerMetas(fileURLToPath(new URL("../medicoes/equilibrio_cuidado_e0/resumo.json", import.meta.url)));
  const e1 = lerMetas(fileURLToPath(new URL("../medicoes/equilibrio_cuidado_e1/E1_escolhido/resumo.json", import.meta.url)));
  const e2 = lerMetas(`${pasta}resumo.json`);
  const m0 = new Map(e0.map(m => [chave(m), m])), m1 = new Map(e1.map(m => [chave(m), m]));
  if (m0.size !== e2.length || m1.size !== e2.length) throw new Error(`as linhas de meta nao batem: E0 ${m0.size}, E1 ${m1.size}, E2 ${e2.length}`);
  const conta = (ms: MetaGravada[]) => ({ falham: ms.filter(m => m.passa === false).length, semDado: ms.filter(m => m.passa === null).length });
  const c0 = conta(e0), c1 = conta(e1), c2 = conta(e2);
  const linhas = ["# A validacao unica (E2) ao lado do E0 e do E1 (gerada por scripts/equilibrio_cuidado/e2.ts)", "",
    `Linhas de meta: ${e2.length}. Nao passam: E0 ${c0.falham}, E1 (calibracao, E1_escolhido) ${c1.falham}, E2 (validacao) ${c2.falham}. ` +
    `Sem dado: E0 ${c0.semDado}, E1 ${c1.semDado}, E2 ${c2.semDado}.`, "",
    "| id | dono | versão | meta | E0 | passa no E0? | E1 (calibração) | passa no E1? | E2 (validação) | passa no E2? |",
    "|---|---|---|---|---|---|---|---|---|---|"];
  for (const m of e2) {
    const a = m0.get(chave(m))!, b = m1.get(chave(m))!;
    linhas.push(`| ${m.id} | ${m.dono} | ${versaoDe(m)} | ${m.meta} | ${a.hoje} | ${sn(a.passa)} | ${b.hoje} | ${sn(b.passa)} | ${m.hoje} | ${sn(m.passa)} |`);
  }
  const texto = linhas.join("\n") + "\n";
  writeFileSync(`${pasta}comparacao.md`, texto);
  return texto;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  if (!process.argv.includes("--tabela")) validar();
  console.log(comparar());
}
