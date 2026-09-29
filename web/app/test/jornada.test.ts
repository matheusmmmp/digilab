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

test("marcos: ovo, estagios e as tres ilhas", () => {
  const m = new Motor(7);
  const x = marcos(m);
  expect(x).toHaveLength(7);
  expect(x[0].feito).toBe(true);
  expect(x.slice(1).every(v => !v.feito)).toBe(true);
});
