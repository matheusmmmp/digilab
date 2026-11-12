/* O sono que segura no grupo de dois pets (docs/TAREFA_V3_SONO_SEGURA.md, a v28; D-SONO-7, "Sim, os dois", Matheus, 2026-11-11): o ovo do
   brasao choca o grupo v28 (VERSAO_GRUPO), a v26 com o sono que segura. A medida e a do test/sono_segura_medida.test.ts, nos dois pets do
   grupo: o DigiBrain modular, sementes 101 e 202, 4 dias de jogo, um tick por vez, com o mesmo roteiro do dono (alimentar com a fome abaixo de
   0,5 e limpar com a sujeira em 2 ou mais; PROPOSTOS, SEM FONTE). O grupo v26 segue com o sono de antes, e o replay refaz o grupo v28. */
import { describe, expect, test } from "vitest";
import { GrupoDoJogo } from "../motor/grupo_jogo.ts";
import { TPD, VERSAO_GRUPO, VERSAO_V26, VERSAO_V28, ehDoGrupo, nasceComSonoSegura } from "../motor/constantes.ts";

const SEMENTES = [101, 202];
const DIAS = 4;
const mediana = (xs: number[]): number => {
  if (!xs.length) return NaN;
  const o = [...xs].sort((a, b) => a - b), n = o.length;
  return n % 2 ? o[(n - 1) / 2]! : (o[n / 2 - 1]! + o[n / 2]!) / 2;
};

interface Medida { versao: number; semente: number; ident: string; fracao: number; cochilosDepoisDia1: number; eFim: number }
function medir(versao: number, semente: number): { linhas: Medida[]; g: GrupoDoJogo } {
  const g = new GrupoDoJogo(semente, versao);
  for (const i of g.ids) g.agir(i, m => m.trocarCerebro("modular"));
  const st = Object.fromEntries(g.ids.map(i => [i, { dormindo: 0, depois: 0, fim: [] as number[], antes: g.motor(i).e.dormindo, e: 0 }]));
  for (let t = 0; t < DIAS * TPD; t++) {
    for (const i of g.ids) {
      const m = g.motor(i);
      if (m.morte !== null) throw new Error(`o pet ${i} v${versao}/${semente} morreu no tick ${t}`);
      if (m.e.fome < .5) g.agir(i, x => x.observar("alimentar"));
      if (m.e.sujeira >= 2) g.agir(i, x => x.observar("limpar"));
      st[i]!.e = m.e.energia;
    }
    g.avancar(1);
    for (const i of g.ids) {
      const s = st[i]!, agora = g.motor(i).e.dormindo;
      if (agora) s.dormindo++;
      if (agora && !s.antes && t >= TPD) s.depois++;
      if (!agora && s.antes) s.fim.push(s.e);
      s.antes = agora;
    }
  }
  return { g, linhas: g.ids.map(i => ({ versao, semente, ident: i, fracao: st[i]!.dormindo / (DIAS * TPD), cochilosDepoisDia1: st[i]!.depois, eFim: mediana(st[i]!.fim) })) };
}

describe("o sono que segura no grupo de dois pets (v26 x v28)", () => {
  test("a v28 e o grupo com o sono que segura (o de hoje e a v29, a v28 com a luta da LP6); a v26 segue com o de antes", () => {
    expect(VERSAO_GRUPO).toBe(VERSAO_V28 + 1);   // a v29 desde a LP6-4 (test/lp6_4_v29.test.ts)
    expect([ehDoGrupo(VERSAO_V28), nasceComSonoSegura(VERSAO_V28), nasceComSonoSegura(VERSAO_V26)]).toEqual([true, true, false]);
  });
  test("a tabela: no grupo v28 os dois pets dormem em menos cochilos e acordam mais descansados", () => {
    const rodadas = [VERSAO_V26, VERSAO_V28].flatMap(v => SEMENTES.map(s => medir(v, s)));
    const linhas = rodadas.flatMap(r => r.linhas);
    console.log(["versao | semente | pet | % dormindo | cochilos depois do dia 1 | energia mediana ao acordar",
      ...linhas.map(l => `v${l.versao} | ${l.semente} | ${l.ident} | ${(100 * l.fracao).toFixed(1)} | ${l.cochilosDepoisDia1} | ${l.eFim.toFixed(2)}`)].join("\n"));
    for (const l of linhas.filter(x => x.versao === VERSAO_V28)) {
      const a = linhas.find(x => x.versao === VERSAO_V26 && x.semente === l.semente && x.ident === l.ident)!;
      expect(l.cochilosDepoisDia1, `${l.semente}/${l.ident}`).toBeLessThan(a.cochilosDepoisDia1);
      expect(l.eFim, `${l.semente}/${l.ident}`).toBeGreaterThan(.9);
    }
    const g = rodadas.find(r => r.g.versao === VERSAO_V28)!.g;
    expect(GrupoDoJogo.reproduzir(g.semente, VERSAO_V28, g.log).assinatura()).toBe(g.assinatura());
  }, 600_000);
});
