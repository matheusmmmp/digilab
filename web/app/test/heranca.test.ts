/* nova geracao: geracao do filho e previa (especie e faixa do temperamento) */
import { expect, test } from "vitest";
import { CAT, CHE, DUR_EVO, Motor, TICK_INICIAL } from "../motor/index.ts";
import { geracao, previa } from "../src/heranca.ts";

/** um adulto v13: as medalhas das evolucoes, e o Champion com as lutas de treino e as vitorias que a passagem pede (postas a mao) */
const adulto = (s: number) => {
  const m = new Motor(s);
  m.liberar(5);
  m.avancar(DUR_EVO.bebe + DUR_EVO.crianca + 15);
  expect(m.estagioAtual).toBe("adolescente");
  m.sparring = CAT.sparring; m.lutas = { ...m.lutas, lutas: CAT.sparring, vitorias: CAT.sparring };
  m.avancar(DUR_EVO.adolescente);
  expect(m.estagioAtual).toBe("adulto");
  return m;
};

test("geracao: sem origem 1; filho = 1 + a maior dos pais", () => {
  const p = adulto(601), q = adulto(602);
  expect(geracao(p)).toBe(1);
  const f = Motor.cruzar(p, q, 700, 1, "t", [geracao(p), geracao(q)]);
  expect(geracao(f)).toBe(2);
  const g = Motor.cruzar(p, q, 701, 2, "t", [2, 1]);
  expect(geracao(g)).toBe(3);
  expect(f.e.tick).toBe(TICK_INICIAL);
});

test("previa: especies dos pais e faixa = media +- 2 sigma", () => {
  const p = adulto(603), q = adulto(604), pv = previa(p, q);
  expect(pv.especies).toEqual(p.especie === q.especie ? [p.especie] : [p.especie, q.especie]);
  for (const x of pv.eixos) {
    expect(x.media).toBeCloseTo((p.temp[x.e] + q.temp[x.e]) / 2);
    expect(x.faixa[1] - x.faixa[0]).toBeLessThanOrEqual(4 * CHE.sigma + 1e-12);
  }
});
