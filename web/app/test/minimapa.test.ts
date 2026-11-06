/* O minimapa (L1 de "Lugares da ilha"): so as contas puras de minimapaGeo.ts. */
import { describe, expect, test } from "vitest";
import {
  ESCALA_B, MINIMAPA_PX, PASSO_SETA, celulaParaPx, centroDaJanela, corComAlfa, corDoNumero, dentroDoCirculo, escalaA, janelaDe, limitarZoom,
  passoDaSeta, passoNoChao, pontasDoCone, pxParaCelula, pxPorCelula,
} from "../src/telas/pet/minimapaGeo.ts";

const AREA = { w: 64, h: 30 };
const perto = (a: number[], b: number[]) => a.forEach((x, i) => expect(x).toBeCloseTo(b[i], 9));

describe("a escala", () => {
  test("A cabe a area inteira no circulo (~3,3 px por celula) e B e 9", () => {
    expect(escalaA(AREA)).toBeCloseTo(232 / Math.hypot(64, 30), 12);
    expect(escalaA(AREA)).toBeGreaterThan(3.2); expect(escalaA(AREA)).toBeLessThan(3.4);
    expect(pxPorCelula(AREA, 0)).toBeCloseTo(escalaA(AREA), 12);
    expect(pxPorCelula(AREA, 1)).toBeCloseTo(ESCALA_B, 12);
  });
  test("o zoom e limitado entre as duas escalas", () => {
    expect(limitarZoom(-3)).toBe(0); expect(limitarZoom(7)).toBe(1); expect(limitarZoom(0.4)).toBe(0.4); expect(limitarZoom(NaN)).toBe(0);
    expect(pxPorCelula(AREA, 9)).toBeCloseTo(ESCALA_B, 12);
    expect(pxPorCelula(AREA, -9)).toBeCloseTo(escalaA(AREA), 12);
  });
  test("entre A e B a escala cresce sem saltos", () => {
    let ant = pxPorCelula(AREA, 0);
    for (let i = 1; i <= 10; i++) { const p = pxPorCelula(AREA, i / 10); expect(p).toBeGreaterThan(ant); ant = p; }
  });
});

describe("o centro da janela", () => {
  test("sem zoom e o meio da area; com o zoom todo e o ponto olhado; no meio, entre os dois", () => {
    perto(centroDaJanela(AREA, [10, 5], 0), [32, 15]);
    perto(centroDaJanela(AREA, [10, 5], 1), [10, 5]);
    perto(centroDaJanela(AREA, [10, 5], 0.5), [21, 10]);
    perto(centroDaJanela(AREA, [10, 5], 5), [10, 5]);
  });
});

describe("celula <-> px", () => {
  for (const z of [0, 0.37, 1]) {
    test(`ida e volta com o zoom ${z}`, () => {
      const j = janelaDe(AREA, [50, 8], z);
      for (const c of [[0, 0], [64, 30], [32, 15], [12.5, 22.25], [-5, 40]] as [number, number][]) perto(pxParaCelula(celulaParaPx(c, j), j), c);
      for (const p of [[0, 0], [116, 116], [231, 3]] as [number, number][]) perto(celulaParaPx(pxParaCelula(p, j), j), p);
    });
    test(`o centro da janela cai no meio do circulo com o zoom ${z}`, () => {
      const j = janelaDe(AREA, [50, 8], z);
      perto(celulaParaPx(j.centro, j), [MINIMAPA_PX / 2, MINIMAPA_PX / 2]);
    });
  }
  test("na escala A a area inteira cabe no circulo; na B, 9 px por celula", () => {
    const a = janelaDe(AREA, [0, 0], 0);
    for (const c of [[0, 0], [64, 0], [0, 30], [64, 30]] as [number, number][]) expect(dentroDoCirculo(celulaParaPx(c, a))).toBe(true);
    const b = janelaDe(AREA, [20, 10], 1);
    perto([celulaParaPx([21, 10], b)[0] - celulaParaPx([20, 10], b)[0]], [ESCALA_B]);
  });
  test("o circulo: o centro esta dentro e o canto nao", () => {
    expect(dentroDoCirculo([116, 116])).toBe(true); expect(dentroDoCirculo([0, 0])).toBe(false); expect(dentroDoCirculo([116, 2], 4)).toBe(false);
  });
});

describe("as setas no plano da vista", () => {
  test("cada seta vira [frente, lado] de PASSO_SETA celulas", () => {
    expect(PASSO_SETA).toBe(2);
    expect(passoDaSeta("ArrowUp")).toEqual([2, 0]); expect(passoDaSeta("ArrowDown")).toEqual([-2, 0]);
    expect(passoDaSeta("ArrowLeft")).toEqual([0, -2]); expect(passoDaSeta("ArrowRight")).toEqual([0, 2]);
    expect(passoDaSeta("KeyW")).toBeNull();
  });
  test("com a frente para o norte a direita e o leste; girada, o passo gira junto", () => {
    perto(passoNoChao(2, 0, [0, -1]), [0, -2]); perto(passoNoChao(0, 2, [0, -1]), [2, 0]);
    perto(passoNoChao(2, 0, [1, 0]), [2, 0]); perto(passoNoChao(0, 2, [1, 0]), [0, 2]);
    const h = Math.SQRT1_2; perto(passoNoChao(2, 0, [h, h]), [2 * h, 2 * h]);
  });
});

describe("o cone e as cores", () => {
  test("o cone abre meia abertura para cada lado da frente", () => {
    const [a, b] = pontasDoCone([10, 10], [0, -1], Math.PI / 2, 13);
    perto(a, [-3, 10]); perto(b, [23, 10]);
    const [c, d] = pontasDoCone([10, 10], [1, 0], 0, 5); perto(c, [15, 10]); perto(d, [15, 10]);
  });
  test("corComAlfa e corDoNumero", () => {
    expect(corComAlfa("#F4F1E4", 0.45)).toBe("rgba(244, 241, 228, 0.45)");
    expect(corComAlfa("#fff", 0.12)).toBe("rgba(255, 255, 255, 0.12)");
    expect(corComAlfa("rgba(19, 21, 24, 0.97)", 0.5)).toBe("rgba(19, 21, 24, 0.5)");
    expect(() => corComAlfa("azul", 1)).toThrow();
    expect(corDoNumero(0xff7fc0)).toBe("rgb(255, 127, 192)");
  });
});
