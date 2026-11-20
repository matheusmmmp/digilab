/* MITOLOGIA, E2 (docs/TAREFA_V3_MITOLOGIA.md, secao 12): Piedmon e a montanha, como funcao pura do pet refeito do log. */
import { describe, expect, test } from "vitest";
import { TPD } from "../motor/constantes.ts";
import { NPC } from "../motor/bots.ts";
import {
  FALA_MONTANHA_FECHADA, FALA_PIEDMON_ANTES, FALA_PIEDMON_DERROTA, FALA_VITORIA_SEM_QUEDA, ehPiedmon, montanhaDe,
} from "../motor/lendas_e2.ts";
import type { FontesLenda } from "../motor/lendas.ts";

const GAZIMON = "npc_tier1_brutamontes", PIEDMON = "npc_tier3_soberano", PIEDMON_MEGA = "npc_v5_piedmon";
const luta = (tick: number, rival: string, resultado: string, forcaPet = 50) => ({ tick, rival, forcaPet, resultado });
const fontes = (lutas: FontesLenda["forcaLutas"]): FontesLenda => ({ forcaLutas: lutas, log: [], mundo: null });

describe("MITOLOGIA E2: Piedmon e a montanha", () => {
  test("os dois Piedmon da Campanha sao reconhecidos pelo nome; os outros nao", () => {
    expect(ehPiedmon(PIEDMON)).toBe(true);
    expect(ehPiedmon(PIEDMON_MEGA)).toBe(true);
    expect(ehPiedmon(GAZIMON)).toBe(false);
    expect(NPC[PIEDMON]!.nome).toBe("Piedmon");
  });
  test("vencer o Piedmon depois de uma hybris fecha a lenda; a primeira derrota fica marcada", () => {
    const m = montanhaDe(fontes([
      luta(10, PIEDMON, "derrota", 100),                 // derrota sem a distancia da hybris
      luta(TPD + 1, GAZIMON, "derrota", 50),             // hybris: Gazimon 96 >= 1,3 x 50
      luta(2 * TPD, PIEDMON, "vitoria", 100),            // vitoria depois da hybris: fecha
      luta(3 * TPD, PIEDMON, "vitoria", 100),
    ]));
    expect(m).toEqual({ derrota: 10, fechada: 2 * TPD, semQueda: null });
  });
  test("vencer sem nunca ter caido nao fecha; a hybris depois e outra vitoria fecham", () => {
    expect(montanhaDe(fontes([luta(5, PIEDMON_MEGA, "vitoria", 120)]))).toEqual({ derrota: null, fechada: null, semQueda: 5 });
    expect(montanhaDe(fontes([luta(5, PIEDMON_MEGA, "vitoria", 120), luta(TPD, GAZIMON, "derrota", 50), luta(2 * TPD, PIEDMON_MEGA, "vitoria", 120)])))
      .toEqual({ derrota: null, fechada: 2 * TPD, semQueda: 5 });
  });
  test("a hybris no mesmo tick da vitoria nao conta como antes", () => {
    expect(montanhaDe(fontes([luta(7, GAZIMON, "derrota", 50), luta(7, PIEDMON, "vitoria", 120)])).fechada).toBeNull();
  });
  test("as falas nao nomeiam a obra", () => {
    for (const t of [FALA_PIEDMON_ANTES, FALA_PIEDMON_DERROTA, FALA_MONTANHA_FECHADA, FALA_VITORIA_SEM_QUEDA])
      expect(t).not.toMatch(/wukong|goku|jornada ao oeste|journey|sun /i);
  });
});
