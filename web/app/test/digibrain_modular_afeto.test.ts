/* G-PAR do M-AFETO (LM1): `afeto.ler`, `afeto.drives` e `afeto.consequencia` do gabarito da LM0, na ordem de cada vida (V e E guardam estado). */
import { expect, test } from "vitest";
import { Afeto } from "../motor/digibrain/afeto.ts";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_MODULAR_MUNDO } from "../motor/digibrain/constantes.ts";
import { conferir, entrada, vidasModular } from "./digibrain_modular_gabarito.ts";

test("G-PAR afeto: ler, drives e consequencia iguais ao Python, em todas as chamadas das oito vidas", () => {
  const n = { ler: 0, drives: 0, consequencia: 0 };
  for (const v of vidasModular()) {
    const afeto = new Afeto(CONFIG_MODULAR_MUNDO, CONFIG_DIGIBRAIN_LAB);
    for (const d of v.decisoes) {
      for (const c of d.chamadas) {
        const onde = `${v.lugar}/${v.dono}/${v.semente} k=${d.k} ${c.m}`;
        if (c.m === "afeto.ler") {
          conferir(onde, afeto.ler(entrada(d, c, 0)), c.s);
          n.ler++;
        } else if (c.m === "afeto.drives") {
          conferir(onde, afeto.drives(entrada(d, c, 0)), c.s);
          n.drives++;
        } else if (c.m === "afeto.consequencia") {
          conferir(onde, afeto.consequencia(entrada(d, c, 0), entrada(d, c, 1), entrada(d, c, 2)), c.s);
          n.consequencia++;
        }
      }
    }
  }
  console.log(`G-PAR afeto: ${n.ler} ler, ${n.drives} drives, ${n.consequencia} consequencia conferidas`);
  expect(n.ler).toBeGreaterThan(0);
  expect(n.drives).toBeGreaterThan(0);
  expect(n.consequencia).toBeGreaterThan(0);
});

test("a soma dos canais e o r (a soma telescopica), e a serie E da doadora so com o controle embaralhado", () => {
  const afeto = new Afeto(CONFIG_MODULAR_MUNDO, CONFIG_DIGIBRAIN_LAB);
  const corpo = (fome: number) => ({ fome, higiene: 900, energia: 900, humor: 900, saude: 1024, tedio: 0, curiosidade: 0, solidao: 0, estresse: 0, dor: 0, susto: 0 });
  const r = afeto.consequencia(corpo(500), corpo(900), ["fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto"]);
  expect(Object.values(r.canais).reduce((a, b) => a + b, 0)).toBe(r.r);
  expect(() => new Afeto(CONFIG_MODULAR_MUNDO, CONFIG_DIGIBRAIN_LAB, undefined, [1, 2])).toThrow(/embaralhado/);
});
