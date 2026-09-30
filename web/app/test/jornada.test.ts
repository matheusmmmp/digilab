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

test("marcos: ovo, estagios e as ilhas (pets v5: o Mega e a Montanha Espiral; v6: as seis arenas e a Liga dos Lideres)", () => {
  for (const [versao, n] of [[4, 7], [5, 9], [6, 12]] as const) {
    const x = marcos(new Motor(7, versao));
    expect(x).toHaveLength(n);
    expect(x[0].feito).toBe(true);
    expect(x.slice(1).every(v => !v.feito)).toBe(true);
  }
  expect(marcos(new Motor(7, 5)).map(v => v.rotulo)).toContain("Virou Mega");
  /* pets v6: a jornada termina na Liga dos Lideres (docs/DESIGN_FRONTEIRA.md), nao no Piedmon */
  expect(marcos(new Motor(7, 6)).map(v => v.rotulo).slice(-2)).toEqual(["Venceu Montanha Espiral", "Venceu a Liga dos Líderes"]);
  expect(marcos(new Motor(7, 5)).map(v => v.rotulo)).not.toContain("Venceu a Liga dos Líderes");
});
