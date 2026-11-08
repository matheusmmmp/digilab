/* O ceu do estilo Digital sem a pintura de anime (docs/TAREFA_V3_UX_TELA_PET.md, secao 25; 2026-11-08): so vista. Confere os numeros que o
   Matheus pediu ("muito saturada [...] mais opaca"; "mais pixelada"), sem DOM */
import { describe, expect, test } from "vitest";
import { CEU_SEM_PINTURA, DIGITAL } from "../src/telas/pet/ilha/constantes.ts";

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

describe("a grade digital mais discreta", () => {
  test("visivel no ceu todo, mais fraca que a de antes (0,5) e mais fraca no alto", () => {
    expect(DIGITAL.grade.alfa).toBeGreaterThan(0.2);
    expect(DIGITAL.grade.alfa).toBeLessThan(0.5);
    expect(saturacao(DIGITAL.grade.cor)).toBeLessThan(saturacao("#b8faff"));
    expect(DIGITAL.grade.topo).toBeGreaterThan(0);
    expect(DIGITAL.grade.topo).toBeLessThan(1);
  });
});
