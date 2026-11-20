/* LUTA_POC, LP3b: o efeito da regra da LP-8 nas cinco formas que passaram a atirar (Gabumon, Garurumon, MetalGarurumon, Angemon e Gargomon).
   Cada uma contra cada rival do mesmo nivel (o perfil canonico, statsRivalArena), nos 8 mapas, nas sementes 101 a 104, como lado azul e como
   lado vermelho, com a tabela da POC (sem o projetil) e com a do jogo (com ele). Saida: scripts/medicoes/lp3b_lp8.json. Medicao de
   engenharia (nao e resultado de pesquisa); o equilibrio e da LP5. Uso: npx tsx scripts/medir_lp3b.ts */
import { writeFileSync } from "node:fs";
import { FORMAS_ARENA, FORMAS_ARENA_POC, GOLPES_DA_POC, IDS_CENA, lutar, sorteiosPorFluxo, type TabelaFormas } from "../motor/arena/index.ts";
import { DIGIMON_DA_FORMA, rivaisArena, statsRivalArena, formaDaChave } from "../motor/index.ts";

const SEMENTES = [101, 102, 103, 104];
function medir(k: string, tabela: TabelaFormas) {
  const est = formaDaChave(k).est, rivais = rivaisArena(est).filter(r => r !== k);
  let lutas = 0, vitorias = 0, empates = 0, relogio = 0;
  for (const r of rivais) for (const cena of IDS_CENA) for (const s of SEMENTES) for (const azul of [true, false]) {
    const eu = { forma: k, stats: statsRivalArena(k) }, ele = { forma: r, stats: statsRivalArena(r) };
    const res = lutar({ cena, semente: s, a: azul ? eu : ele, b: azul ? ele : eu }, sorteiosPorFluxo(s), tabela);
    lutas++; relogio += res.relogio;
    if (res.vencedor === null) empates++; else if ((res.vencedor === "a") === azul) vitorias++;
  }
  return { lutas, vitorias: vitorias / lutas, empates: empates / lutas, relogioMedioS: relogio / lutas / 1000 };
}
const formas = Object.keys(GOLPES_DA_POC).map(k => ({ chave: k, digimon: DIGIMON_DA_FORMA[k][0], nivel: DIGIMON_DA_FORMA[k][1], poc: medir(k, FORMAS_ARENA_POC), jogo: medir(k, FORMAS_ARENA) }));
const saida = { fonte: "web/app/scripts/medir_lp3b.ts", sementes: SEMENTES, mapas: IDS_CENA, regra: "LP-8: projetil de velocidade 30 (Guide), PROPOSTO, SEM FONTE", formas };
writeFileSync(new URL("./medicoes/lp3b_lp8.json", import.meta.url), JSON.stringify(saida, null, 2) + "\n");
for (const f of formas) console.log(`${f.digimon.padEnd(15)} ${f.nivel.padEnd(9)} vitorias ${(100 * f.poc.vitorias).toFixed(1)}% -> ${(100 * f.jogo.vitorias).toFixed(1)}%  luta ${f.poc.relogioMedioS.toFixed(1)} s -> ${f.jogo.relogioMedioS.toFixed(1)} s  (${f.jogo.lutas} lutas)`);
