/* A disposicao do mapa da Exploracao (src/telas/lutar/mapaLayout.ts; docs/TAREFA_V2_EXPLORACAO.md): para 3, 4 e 7 ilhas (os lugares dos
   pets v1-v4, v5 e v6 em diante com a Fronteira), no celular (360 a 899 px) e em caixas de desktop, nenhum cartao sobre outro, nenhum
   cartao sobre uma ilha que nao e a dele, nenhuma ilha sobre outra, o marcador sem cobrir cartao e tudo dentro da caixa */
import { describe, expect, test } from "vitest";
import { caixaCartao, caixaIlha, caixaMarcador, layoutCelular, layoutDesktop, type Caixa, type LayoutMapa } from "../src/telas/lutar/mapaLayout.ts";

const cruza = (a: Caixa, b: Caixa) => a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1;
const dentro = (a: Caixa, L: LayoutMapa) => a.x0 >= 0 && a.y0 >= 0 && a.x1 <= L.larg && a.y1 <= L.alt;

function conferir(L: LayoutMapa): void {
  const n = L.ilhas.length;
  expect(L.cartoes).toHaveLength(n);
  for (let i = 0; i < n; i++) {
    const c = caixaCartao(L, i), m = caixaMarcador(L, i);
    expect(dentro(c, L), `cartão ${i} dentro da caixa`).toBe(true);
    expect(dentro(m, L), `marcador na ilha ${i} dentro da caixa`).toBe(true);
    expect(c.x1 - c.x0, `cartão ${i} com 150 px ou mais`).toBeGreaterThanOrEqual(150);
    for (let j = 0; j < n; j++) {
      if (j === i) continue;
      expect(cruza(c, caixaIlha(L, j)), `cartão ${i} sobre a ilha ${j}`).toBe(false);
      expect(cruza(m, caixaCartao(L, j)), `marcador na ilha ${i} sobre o cartão ${j}`).toBe(false);
      if (j > i) {
        expect(cruza(c, caixaCartao(L, j)), `cartões ${i} e ${j}`).toBe(false);
        expect(cruza(caixaIlha(L, i), caixaIlha(L, j)), `ilhas ${i} e ${j}`).toBe(false);
      }
    }
  }
}

describe("o mapa da Exploração", () => {
  for (const n of [3, 4, 7]) {
    for (const larg of [360, 390, 430, 600, 899]) test(`celular: ${n} ilhas em ${larg} px`, () => {
      const L = layoutCelular(n, larg);
      conferir(L);
      /* a primeira ilha embaixo, a ultima no alto, em zigue-zague */
      expect(L.ilhas[0].cy).toBeGreaterThan(L.ilhas[n - 1].cy);
      expect(L.ilhas.every((p, i) => (i % 2 ? p.cx > larg / 2 : p.cx < larg / 2))).toBe(true);
    });
    for (const [larg, alt] of [[460, 600], [560, 620], [600, 662], [760, 760], [1000, 900]]) test(`desktop: ${n} ilhas em ${larg} x ${alt}`, () => {
      const L = layoutDesktop(n, larg, alt);
      conferir(L);
      expect(L.ilhas[0].cy).toBeGreaterThanOrEqual(L.ilhas[n - 1].cy);
      expect(L.tam).toBeGreaterThanOrEqual(80);
    });
  }
  test("desktop baixo: o mapa passa da altura da caixa (ela rola), com a ilha de 90 px", () => {
    const L = layoutDesktop(7, 600, 540);
    conferir(L);
    expect(L.tam).toBe(90);
    expect(L.alt).toBeGreaterThan(540);
  });
  test("caixa estreita demais ou mapa vazio falham alto", () => {
    expect(() => layoutDesktop(7, 300, 200)).toThrow(/não cabe/);
    expect(() => layoutCelular(0, 390)).toThrow(/sem ilha/);
    expect(() => layoutCelular(7, 200)).toThrow(/estreito/);
  });
});
