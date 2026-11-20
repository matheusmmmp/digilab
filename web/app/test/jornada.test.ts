/* jornada do jogador: o ovo do brasao escolhido sai da semente (motor e save sem mudanca) */
import { expect, test } from "vitest";
import { ESPECIES, Motor } from "../motor/index.ts";
import { especieDaSemente, marcos, sementeDoBrasao } from "../src/jornada.ts";

test("semente do brasao da o ovo daquela especie", () => {
  for (const esp of ESPECIES) {
    const s = sementeDoBrasao(esp);
    expect(especieDaSemente(s)).toBe(esp);
    expect(new Motor(s).especie).toBe(esp);
  }
});

test("marcos: ovo, estagios, o Mega, as seis arenas e a Liga dos Lideres", () => {
  const x = marcos(new Motor(7));
  expect(x).toHaveLength(12);
  expect(x[0].feito).toBe(true);
  expect(x.slice(1).every(v => !v.feito)).toBe(true);
  expect(x.map(v => v.rotulo)).toContain("Virou Mega");
  /* a jornada termina na Liga dos Lideres (docs/DESIGN_FRONTEIRA.md), nao no Piedmon */
  expect(x.map(v => v.rotulo).slice(-2)).toEqual(["Venceu Montanha Espiral", "Venceu a Liga dos Líderes"]);
});
