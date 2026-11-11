/* O ceu do estilo Digital sem a pintura de anime (docs/TAREFA_V3_UX_TELA_PET.md, secao 25; 2026-11-08): so vista. Confere os numeros que o
   Matheus pediu ("muito saturada [...] mais opaca"; "mais pixelada"), sem DOM */
import { describe, expect, test } from "vitest";
import { CEU_SEM_PINTURA, DIGITAL, LONGE, NUVENS_PINTADAS } from "../src/telas/pet/ilha/constantes.ts";
import { DESENHOS_DE_ANEL, aneisDoPortal } from "../src/telas/pet/ilha/digitalConta.ts";

const rgb = (h: string) => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const saturacao = (h: string) => { const c = rgb(h), mx = Math.max(...c), mn = Math.min(...c); return mx === 0 ? 0 : (mx - mn) / mx; };

describe("o ceu sem pintura", () => {
  test("o padrao volta a ser o pintado, com o azul suavizado um pouco (nao tanto); o pixel fica em faixas e a nevoa dele tem a cor do horizonte", () => {
    expect(CEU_SEM_PINTURA.modo).toBe("pintado");
    expect(CEU_SEM_PINTURA.pintura.saturacao).toBeGreaterThanOrEqual(0.7);
    expect(CEU_SEM_PINTURA.pintura.saturacao).toBeLessThan(1);
    expect(CEU_SEM_PINTURA.pintura.clarear).toBeLessThanOrEqual(0.1);
    expect(CEU_SEM_PINTURA.faixas).toBeGreaterThanOrEqual(6);
    expect(CEU_SEM_PINTURA.horizonte).toBe(parseInt(CEU_SEM_PINTURA.cores[2].slice(1), 16));
  });
  test("as cores ficam em tons medios: o topo menos saturado que o azul de antes, e o horizonte o mais claro", () => {
    expect(saturacao(CEU_SEM_PINTURA.cores[0])).toBeLessThan(saturacao("#3d8de8"));
    const brilho = (h: string) => rgb(h).reduce((a, b) => a + b, 0);
    expect(brilho(CEU_SEM_PINTURA.cores[2])).toBeGreaterThan(brilho(CEU_SEM_PINTURA.cores[1]));
    expect(brilho(CEU_SEM_PINTURA.cores[1])).toBeGreaterThan(brilho(CEU_SEM_PINTURA.cores[0]));
  });
});

describe("o portal no ceu, no lugar da grade pintada", () => {
  const P = DIGITAL.portal, aneis = aneisDoPortal();
  test("os aneis crescem de dentro para fora, cada um gira para um lado e o de dentro e o mais rapido", () => {
    expect(aneis.length).toBe(P.aneis);
    expect(aneis[0].raio).toBe(P.raio[0]);
    expect(aneis[aneis.length - 1].raio).toBe(P.raio[1]);
    for (let k = 1; k < aneis.length; k++) {
      expect(aneis[k].raio).toBeGreaterThan(aneis[k - 1].raio);
      expect(Math.sign(aneis[k].volta)).toBe(-Math.sign(aneis[k - 1].volta));
      expect(Math.abs(aneis[k].volta)).toBeGreaterThan(Math.abs(aneis[k - 1].volta));
    }
  });
  test("o de fora e a linha cheia (o arco grande), os outros alternam o desenho, e a conta e deterministica", () => {
    expect(aneis[aneis.length - 1].desenho).toBe("linha");
    for (const a of aneis) { expect(DESENHOS_DE_ANEL).toContain(a.desenho); expect(a.partes % 8).toBe(0); expect(a.fase >= 0 && a.fase < Math.PI * 2).toBe(true); }
    expect(new Set(aneis.slice(0, -1).map(a => a.desenho)).size).toBeGreaterThanOrEqual(3);
    expect(aneisDoPortal()).toEqual(aneis);
  });
  test("cabe na camera: o portal e os arcos ficam aquem do plano de longe, e o portal fica alem das nuvens", () => {
    expect(P.longe).toBeGreaterThan(NUVENS_PINTADAS.raio[1]);
    expect(P.longe + P.raio[1]).toBeLessThan(LONGE - 40);
    expect(P.arcos.raio + 3 * P.arcos.inclina.length).toBeLessThan(LONGE - 40);
    expect(P.altura + P.raio[1]).toBeGreaterThan(P.raio[1]);
  });
  test("mais forte de noite que de dia, sem estourar com o pulso", () => {
    expect(P.opacidade[1]).toBeGreaterThan(P.opacidade[0]);
    expect(P.opacidade[1] * (1 + P.pulso[0])).toBeLessThanOrEqual(1);
    /* fraco, como coisa longe (o primeiro desenho, com 0,62 de dia, ficou claro demais), mas sem sumir */
    expect(P.opacidade[0]).toBeLessThan(0.4);
    expect(P.opacidade[0] * (1 - P.pulso[0])).toBeGreaterThan(0.15);
  });
});

describe("as nuvens da pintura no mundo", () => {
  test("cada pedaco cabe na imagem do ceu (1376 x 768), as bordas esfumam e o anel gira devagar em volta da ilha", () => {
    for (const [x, y, w, h] of NUVENS_PINTADAS.pedacos) {
      expect(x >= 0 && y >= 0 && w > 0 && h > 0).toBe(true);
      expect(x + w).toBeLessThanOrEqual(1376); expect(y + h).toBeLessThanOrEqual(768);
    }
    expect(NUVENS_PINTADAS.esfumar).toBeGreaterThan(0); expect(NUVENS_PINTADAS.esfumar).toBeLessThan(0.5);
    expect(NUVENS_PINTADAS.volta).toBeGreaterThanOrEqual(300);
    expect(NUVENS_PINTADAS.n).toBeGreaterThanOrEqual(NUVENS_PINTADAS.pedacos.length);
    /* o Matheus escolheu as nuvens 3D de pouco poligono (2026-11-08: "3D de polígonos"), com a base em sombra e mais de uma bolha */
    expect(NUVENS_PINTADAS.desenho).toBe("3d");
    expect(NUVENS_PINTADAS.bolhas[0]).toBeGreaterThanOrEqual(3);
    expect(NUVENS_PINTADAS.faixa).toBeGreaterThan(0); expect(NUVENS_PINTADAS.faixa).toBeLessThan(0.5);
  });
});
