// A vida de demonstração do WORLD-POC-02 (docs/TAREFA_V2_WORLD_POC_02.md, o Gate B), só descritiva: a semente 101, 3.000 ticks, com o
// corpo ligado e o cérebro de teste. Grava artifacts_v2_world_poc/poc02_laco.json com:
//   - quantas decisões de cada Intenção e como cada uma terminou;
//   - as chamadas ao corpo, por tipo;
//   - a primeira decisão que fecha a cadeia da comida e a primeira da bola (o registro inteiro: a Observação, a Intenção, a ação
//     executada, o resultado físico, os receptores antes e depois e a consequência por drive);
//   - os receptores no fim (o achado da higiene: ela cai pelo corpo, e o POC não tem como limpar).
//
//   npm run poc:medir02
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { LIMIARES_CORPO } from "./mundo3d/cerebro.ts";
import { Simulacao } from "./mundo3d/simulacao.ts";

const SEMENTE = 101, TICKS = 3000, S = 1024;
const SAIDA = fileURLToPath(new URL("../../../artifacts_v2_world_poc/", import.meta.url));

const s = new Simulacao(SEMENTE, undefined, { corpo: true });
s.avancar(TICKS);
const r = s.registros;
const intencoes = {};
for (const x of r) {
  const k = `${x.intencao.tipo}:${x.executada.parou_por}`;
  intencoes[k] = (intencoes[k] ?? 0) + 1;
}
const chamadas = {};
for (const c of s.chamadasCorpo) chamadas[c.t] = (chamadas[c.t] ?? 0) + 1;
const comida = r.find(x => S - x.corpo_antes.fome >= LIMIARES_CORPO.fome && x.intencao.tipo === "consumir"
  && x.executada.parou_por === "chegou" && x.fisico.comeu > 0 && x.consequencia.fome > 0);
const bola = r.find(x => x.corpo_antes.tedio >= LIMIARES_CORPO.tedio && x.intencao.tipo === "empurrar" && x.fisico.empurroes > 0
  && x.consequencia.tedio > 0);
if (!comida || !bola) throw new Error("a vida de demonstracao nao fecha as duas cadeias");

const saida = {
  semente: SEMENTE, ticks: TICKS, decisoes_fechadas: r.length, hash: s.hash(),
  intencoes, chamadas_corpo: chamadas,
  decisoes_que_comeram: r.filter(x => x.fisico.comeu > 0).length,
  decisoes_com_empurrao: r.filter(x => x.fisico.empurroes > 0).length,
  cadeia_comida: comida, cadeia_bola: bola,
  receptores_no_comeco: r[0].corpo_antes, receptores_no_fim: r.at(-1).corpo_depois,
};
mkdirSync(SAIDA, { recursive: true });
writeFileSync(join(SAIDA, "poc02_laco.json"), JSON.stringify(saida, null, 1) + "\n");
console.log(JSON.stringify({ ...saida, cadeia_comida: `decisao ${comida.n}`, cadeia_bola: `decisao ${bola.n}` }, null, 1));
