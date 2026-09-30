/* Progressao dos pets v9 (rodada de equilibrio geral, fase 2; docs/EQUILIBRIO_GERAL.md, metas M-B1...M-B3): a escala dos pets v9
   (CESC_V9), os fatores dos lideres (arenas.FATOR_LIDER_V9) e dos desafiantes (CESC_V9.fatorNpc) valem so nas lutas dos pets v9. Os
   pets v6-v8 seguem com a CESC_V6 e os fatores de ARENAS (os numeros abaixo sao os de antes da fase 2, fixos no teste), e os v1-v5 com a
   CESC e sem arena. */
import { afterAll, beforeAll, describe, expect, test } from "vitest";
import {
  ARENAS, ARENAS_V9, CESC, CESC_V6, CESC_V9, CV21D, CV21E, FATOR_LIDER_V9, FATOR_LIGA_V9, LIGA, LUGARES_V6, NPC, VERSAO_ARENAS_V9, VERSAO_ESCALA_V9,
  arenaDaLuta, escalaDaVersao, escalaDe, lutadorBot, lutadorLiga, perfilDe,
} from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";
import { Motor } from "../motor/motor.ts";

/* os numeros dos pets v6-v8 antes da fase 2 (nao podem mudar) */
const V6_VIDA = { bebe: 50, crianca: 200, adolescente: 700, adulto: 2500, mega: 23000 }, V6_BETA = .045;
const V6_FATOR_NPC = { npc_tier2_sentinela: 1.5, npc_tier2_porteiro: 1.1, npc_v5_puppetmon: 2.5, npc_v5_machinedramon: 2.2 };
/* o fator do lider na luta de arena dos v6-v8: o da arena ou, sem ele, o do NPC */
const V6_FATOR_LIDER: Record<string, number> = { campina: 1.3, torre: 1.6, floresta: 1.5, cidadela: .9, lago: 1.5, espiral: 1.6 };
const DESAFIANTES = Object.keys(V6_FATOR_NPC);

describe("progressao dos pets v9: escala e fatores separados por versao", () => {
  const antes = ESCALA.ligada;
  beforeAll(() => ligarEscala(true));
  afterAll(() => ligarEscala(antes));

  test("os numeros dos pets v6-v8 nao mudaram", () => {
    expect(CESC_V6).toEqual({ versaoPet: 6, vida: V6_VIDA, beta: V6_BETA, fatorNpc: V6_FATOR_NPC });
    for (const a of ARENAS) expect(a.fator ?? NPC[a.lider]!.fator).toBe(V6_FATOR_LIDER[a.id]);
  });

  test("a escala da versao: CESC nos v1-v5, CESC_V6 nos v6-v8, CESC_V9 so do v9 em diante", () => {
    expect(VERSAO_ESCALA_V9).toBe(9);
    expect(CESC_V9).not.toBe(CESC_V6);
    for (const v of [0, 1, 5]) expect(escalaDaVersao(v)).toBeNull();
    for (const v of [6, 7, 8]) expect(escalaDaVersao(v)).toBe(CESC_V6);
    expect(escalaDaVersao(9)).toBe(CESC_V9);
    for (const est of ["crianca", "adolescente", "adulto", "mega"] as const) {
      expect(escalaDe(est, 22, 8)).toBe(V6_VIDA[est] * (1 + V6_BETA * 22));
      expect(escalaDe(est, 22, 9)).toBe(CESC_V9.vida[est] * (1 + CESC_V9.beta * 22));
    }
    const f = { esp: "brasa", est: "adolescente", ramo: "sereno", linha: "brigao" } as const;
    expect(perfilDe(f, null, 1, null, true, 8).escala).toBe(V6_VIDA.adolescente);
    expect(perfilDe(f, null, 1, null, true, 9).escala).toBe(CESC_V9.vida.adolescente);
    expect(perfilDe(f, null, 1, null, true, 5).escala).toBe(CESC.vida.adolescente);
  });

  test("os desafiantes: o fator dos v9 so nas lutas V21E (pets v9), o dos v6 nas lutas V21D", () => {
    expect(Object.keys(CESC_V9.fatorNpc).sort()).toEqual([...DESAFIANTES].sort());
    for (const k of DESAFIANTES) {
      const est = NPC[k]!.est;
      expect(lutadorBot(k, CV21D).cond.escala).toBe(V6_VIDA[est] * V6_FATOR_NPC[k as keyof typeof V6_FATOR_NPC]);
      expect(lutadorBot(k, CV21E).cond.escala).toBe(CESC_V9.vida[est] * CESC_V9.fatorNpc[k]);
    }
    /* pelo motor do pet: o v8 luta com o fator dos v6, o v9 com o dos v9 */
    for (const k of DESAFIANTES) {
      const est = NPC[k]!.est;
      expect(new Motor(3, 8).lutadores(k).B.cond.escala).toBe(V6_VIDA[est] * V6_FATOR_NPC[k as keyof typeof V6_FATOR_NPC]);
      expect(new Motor(3, 9).lutadores(k).B.cond.escala).toBe(CESC_V9.vida[est] * CESC_V9.fatorNpc[k]);
    }
  });

  test("os lideres: a arena da luta de um pet v9 tem o fator dos v9; v6-v8 a de sempre; v1-v5 sem arena", () => {
    expect(VERSAO_ARENAS_V9).toBe(9);
    expect(Object.keys(FATOR_LIDER_V9).sort()).toEqual(ARENAS.map(a => a.id).sort());
    ARENAS.forEach((a, i) => {
      for (const v of [6, 7, 8]) expect(arenaDaLuta(a.lider, v)).toBe(a);
      for (const v of [1, 5]) expect(arenaDaLuta(a.lider, v)).toBeNull();
      const a9 = arenaDaLuta(a.lider, 9)!;
      expect(a9).toBe(ARENAS_V9[i]);
      expect(a9.fator).toBe(FATOR_LIDER_V9[a.id]);
      /* so o fator muda: a regra, a lista, a tecnica e as lutas sao as mesmas */
      expect({ ...a9, fator: undefined }).toEqual({ ...a, fator: undefined });
      const est = LUGARES_V6[a.lugar].est;
      expect(new Motor(3, 8).lutadores(a.lider).B.cond.escala).toBeCloseTo(V6_VIDA[est] * V6_FATOR_LIDER[a.id], 9);
      expect(new Motor(3, 9).lutadores(a.lider).B.cond.escala).toBeCloseTo(CESC_V9.vida[est] * FATOR_LIDER_V9[a.id], 9);
    });
  });

  test("a Liga: a vida do Mega da CESC_V6, a mesma dos v9; o fator dos v9 (fase 3) so nas lutas V21E", () => {
    expect(CESC_V9.vida.mega).toBe(V6_VIDA.mega);
    LIGA.forEach((x, i) => {
      expect(lutadorLiga(i, CV21E).cond.escala).toBeCloseTo(V6_VIDA.mega * FATOR_LIGA_V9[x.arena], 9);
      expect(lutadorLiga(i, CV21D).cond.escala).toBe(V6_VIDA.mega);
    });
  });
});
