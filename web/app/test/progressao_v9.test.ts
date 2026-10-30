/* Progressao dos pets v9 (rodada de equilibrio geral, fase 2; docs/EQUILIBRIO_GERAL.md, metas M-B1...M-B3): a escala dos pets v9
   (CESC_V9), os fatores dos lideres (arenas.FATOR_LIDER_V9) e dos desafiantes (CESC_V9.fatorNpc) valem nas lutas dos pets v9 em diante.
   A CESC_V6 (pets v6-v8) saiu na COMBATE-TR R3: a vida e o beta dela, que a CESC_V9 repete, ficam fixos aqui como prova de que os numeros
   nao mudaram; as escalas de antes dos v9 falham alto. */
import { afterAll, beforeAll, describe, expect, test } from "vitest";
import {
  ARENAS, ARENAS_V9, CESC_V9, CV21E, CV21E_TR, FATOR_LIDER_V9, FATOR_LIGA_V9, LIGA, LUGARES_V6, NPC, VERSAO_ARENAS_V9, VERSAO_ESCALA_V9,
  arenaDaLuta, escalaDaVersao, escalaDe, lutadorBot, lutadorLiga, perfilDe,
} from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";
import { Motor } from "../motor/motor.ts";

/* os numeros da escala dos pets v6-v8 antes da fase 2 (a vida e o beta seguem na CESC_V9; nao podem mudar) */
const V6_VIDA = { bebe: 50, crianca: 200, adolescente: 700, adulto: 2500, mega: 23000 }, V6_BETA = .045;
const V6_FATOR_NPC = { npc_tier2_sentinela: 1.5, npc_tier2_porteiro: 1.1, npc_v5_puppetmon: 2.5, npc_v5_machinedramon: 2.2 };
/* o fator do lider na luta de arena dos v6-v8: o da arena ou, sem ele, o do NPC */
const V6_FATOR_LIDER: Record<string, number> = { campina: 1.3, torre: 1.6, floresta: 1.5, cidadela: .9, lago: 1.5, espiral: 1.6 };
const DESAFIANTES = Object.keys(V6_FATOR_NPC);

describe("progressao dos pets v9: escala e fatores separados por versao", () => {
  const antes = ESCALA.ligada;
  beforeAll(() => ligarEscala(true));
  afterAll(() => ligarEscala(antes));

  test("os numeros da escala nao mudaram (a vida e o beta da CESC_V6 que saiu)", () => {
    expect(CESC_V9.vida).toEqual(V6_VIDA); expect(CESC_V9.beta).toBe(V6_BETA);
    for (const a of ARENAS) expect(a.fator ?? NPC[a.lider]!.fator).toBe(V6_FATOR_LIDER[a.id]);
  });

  test("a escala da versao: CESC_V9 do v9 em diante; antes disso falha alto", () => {
    expect(VERSAO_ESCALA_V9).toBe(9);
    for (const v of [0, 1, 5, 6, 8]) expect(() => escalaDaVersao(v)).toThrow(/não existe mais/);
    expect(escalaDaVersao(9)).toBe(CESC_V9); expect(escalaDaVersao(13)).toBe(CESC_V9);
    for (const est of ["crianca", "adolescente", "adulto", "mega"] as const) {
      expect(escalaDe(est, 22, 13)).toBe(V6_VIDA[est] * (1 + V6_BETA * 22));
      expect(escalaDe(est, 22, 9)).toBe(CESC_V9.vida[est] * (1 + CESC_V9.beta * 22));
    }
    const f = { esp: "brasa", est: "adolescente", ramo: "sereno", linha: "brigao" } as const;
    expect(perfilDe(f, null, 1, null, true, 13).escala).toBe(V6_VIDA.adolescente);
    expect(perfilDe(f, null, 1, null, true, 9).escala).toBe(CESC_V9.vida.adolescente);
    expect(() => perfilDe(f, null, 1, null, true, 5)).toThrow(/não existe mais/);
  });

  test("os desafiantes: o fator dos v9 nas lutas V21E (pets v9 em diante)", () => {
    expect(Object.keys(CESC_V9.fatorNpc).sort()).toEqual([...DESAFIANTES].sort());
    for (const k of DESAFIANTES) {
      const est = NPC[k]!.est;
      expect(lutadorBot(k, CV21E_TR).cond.escala).toBe(CESC_V9.vida[est] * CESC_V9.fatorNpc[k]);
      expect(lutadorBot(k, CV21E).cond.escala).toBe(CESC_V9.vida[est] * CESC_V9.fatorNpc[k]);
    }
    /* pelo motor do pet: o v13 luta com o fator dos v9 */
    for (const k of DESAFIANTES) {
      const est = NPC[k]!.est;
      expect(new Motor(3).lutadores(k).B.cond.escala).toBe(CESC_V9.vida[est] * CESC_V9.fatorNpc[k]);
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
      expect(new Motor(3).lutadores(a.lider).B.cond.escala).toBeCloseTo(CESC_V9.vida[est] * FATOR_LIDER_V9[a.id], 9);
    });
  });

  test("a Liga: a vida do Mega, a mesma dos v6; o fator dos v9 (fase 3)", () => {
    expect(CESC_V9.vida.mega).toBe(V6_VIDA.mega);
    LIGA.forEach((x, i) => {
      expect(lutadorLiga(i, CV21E).cond.escala).toBeCloseTo(V6_VIDA.mega * FATOR_LIGA_V9[x.arena], 9);
      expect(lutadorLiga(i, CV21E_TR, 1).cond.escala).toBe(V6_VIDA.mega);
    });
  });
});
