/* G-PAR do M-SENS (LM1): cada `sens.codificar` do gabarito da LM0, em ordem por vida (o M-SENS tem estado: a habituacao), igual ao Python. */
import { expect, test } from "vitest";
import { CONFIG_MODULAR_MUNDO } from "../motor/digibrain/constantes.ts";
import { Sens } from "../motor/digibrain/sens.ts";
import { conferir, vidasModular } from "./digibrain_modular_gabarito.ts";

test("G-PAR sens.codificar: a saida do TS e a do Python, em todas as decisoes das oito vidas", () => {
  let conferidas = 0;
  for (const v of vidasModular()) {
    const sens = new Sens(CONFIG_MODULAR_MUNDO, CONFIG_MODULAR_MUNDO);
    for (const d of v.decisoes) {
      for (const c of d.chamadas.filter(x => x.m === "sens.codificar")) {
        conferir(`${v.lugar}/${v.dono}/${v.semente} k=${d.k} sens.codificar`, sens.codificar(c.e[0] as never), c.s);
        conferidas++;
      }
    }
  }
  console.log(`G-PAR sens: ${conferidas} chamadas conferidas`);
  expect(conferidas).toBeGreaterThan(0);
  expect(conferidas).toBe(8 * 384);
});

test("o M-SENS falha alto num receptor fora do prototipo e num tipo desconhecido", () => {
  const sens = new Sens(CONFIG_MODULAR_MUNDO, CONFIG_MODULAR_MUNDO);
  const obs = (corpo: Record<string, number | null>, vistos: never[] = []) => ({
    corpo: { fome: 800, higiene: 800, energia: 800, humor: 800, saude: 1024, tedio: 0, curiosidade: 0, solidao: 0, estresse: 0, dor: 0, susto: 0, ...corpo },
    mundo: { x: 0, y: 0, regiao: 0, direcao_cheiro: 0, vistos }, vetor_estado: [0, 0, 0, 0, 0, 0, 0, 0], ticks_desde_cuidado: 0 });
  expect(() => sens.codificar(obs({ paladar_doce: 10 }))).toThrow(/fora do prototipo/);
  expect(() => sens.codificar(obs({}, [[1, "pedra", 0, 0, 1]] as never))).toThrow(/desconhecido/);
});
