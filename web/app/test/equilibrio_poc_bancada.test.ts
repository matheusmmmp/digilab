/* LUTA_POC, LP5-0 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.3): a bancada do equilibrio refaz o jogo de hoje. O CANDIDATO_V21 tem de dar os
   mesmos numeros que o motor (o statsLutaPoc do pet, o statsNpc, o statsRivalArena, o statsRivalForma e o da Fabrica), senao a medida da
   LP5-0 nao e o ponto de partida. E o treino tipico (D-LP5-2) sai com o total exato e dentro dos tetos. */
import { describe, expect, test } from "vitest";
import {
  CAMPANHA_V6, CMD, CTR, DUR_EVO, LIGA, Motor, STATS, TICK_INICIAL, TentativaFabrica, caraterCanonico, condicaoDe, formaLiga, rivaisArena,
  statsDoPet, statsNpc, statsRivalArena, statsRivalForma, type Stats,
} from "../motor/index.ts";
import {
  CANDIDATO_V21, ESTAGIOS_LUTA, TETO, TIPICO, npc, petDoEstagio, pontosNoTotal, rivalCanonico, rivalDaForma, statsLuta,
} from "../scripts/equilibrio_poc/comum.ts";
import { basesDa } from "../scripts/equilibrio_poc/faixas.ts";

const c = CANDIDATO_V21;

describe("o candidato v21 refaz os numeros do jogo", () => {
  test("o pet: o statsLutaPoc do Motor, sem e com treino", () => {
    for (const s of [11, 21, 23, 101, 202]) {
      const m = new Motor(s);
      m.liberar(CMD.mega);
      m.avancar(DUR_EVO.bebe + 30);
      const conf = () => expect(statsLuta(c, statsDoPet(m.forma, m.carater(), m.pontosDeLuta()), m.forma.est, condicaoDe(m.e.saude))).toEqual(m.statsLutaPoc());
      conf();
      m.treino.pontos = { vigor: 2, folego: 1, recuperacao: 1, forca: 2, mira: 1, guarda: 1.5 } as Stats;
      conf();
      m.avancar(TICK_INICIAL + DUR_EVO.bebe + DUR_EVO.crianca + 15 - m.e.tick);
      expect(m.estagioAtual).toBe("adolescente");
      conf();
    }
  });
  test("os 10 NPCs da campanha v6", () => {
    expect(CAMPANHA_V6).toHaveLength(10);
    for (const x of CAMPANHA_V6) expect(npc(c, x.k)).toEqual(statsNpc(x.k));
  });
  test("os rivais da Arena de cada estagio", () => {
    for (const e of ESTAGIOS_LUTA) for (const k of rivaisArena(e)) expect(rivalCanonico(c, k)).toEqual(statsRivalArena(k));
  });
  test("os Megas da Liga e da Fabrica", () => {
    LIGA.forEach((x, k) => expect(rivalDaForma(c, formaLiga(k), caraterCanonico(x.adulta))).toEqual(statsRivalForma(formaLiga(k), caraterCanonico(x.adulta))));
    const t = new TentativaFabrica(1, 0);
    for (const f of t.alugueis) expect(rivalDaForma(c, f, caraterCanonico(f.adulta!))).toEqual(t.statsPoc(f));
  });
});

describe("o treino tipico (D-LP5-2) e os pets", () => {
  test("o total sai exato, cada stat dentro do teto, e a curva sobe", () => {
    for (const esp of ["brasa", "cirro", "ferrugem", "limo"] as const) {
      let antes: Stats | null = null;
      for (let n = 0; n <= TETO.mega; n += 2) {
        const p = pontosNoTotal(esp, n), tot = STATS.reduce((a, k) => a + p[k], 0);
        expect(tot).toBeCloseTo(n, 9);
        for (const k of STATS) { expect(p[k]).toBeGreaterThanOrEqual(0); expect(p[k]).toBeLessThanOrEqual(CTR.tetoStat + 1e-9); if (antes) expect(p[k]).toBeGreaterThanOrEqual(antes[k] - 1e-9); }
        antes = p;
      }
      expect(() => pontosNoTotal(esp, TETO.mega + 1)).toThrow(/nao chega/);
    }
    expect(TIPICO).toEqual({ crianca: 8, adolescente: 22, adulto: 36, mega: 40 });
    expect(TETO).toEqual({ crianca: 10, adolescente: 22, adulto: 36, mega: 40 });
  });
  test("o pet da base: uma forma do estagio, a mesma a cada chamada", () => {
    for (const e of ESTAGIOS_LUTA) {
      const p = petDoEstagio(86101, 3, e);
      expect(rivaisArena(e)).toContain(p.chave);
      expect(petDoEstagio(86101, 3, e)).toEqual(p);
    }
  });
  test("as faixas: as 5 bases, e um nome fora falha alto", () => {
    expect(basesDa("calibracao")).toEqual([86101, 86202, 86303, 86404, 86505]);
    expect(basesDa("conferencia")).toEqual([87101, 87202, 87303, 87404, 87505]);
    expect(() => basesDa("calibracao2")).toThrow(/faixa desconhecida/);
  });
});
