/* O ceu do estilo Digital sem a pintura de anime (docs/TAREFA_V3_UX_TELA_PET.md, secao 25; 2026-11-08): so vista. Confere os numeros que o
   Matheus pediu ("muito saturada [...] mais opaca"; "mais pixelada"), sem DOM */
import { describe, expect, test } from "vitest";
import { CEU_SEM_PINTURA, DIGITAL } from "../src/telas/pet/ilha/constantes.ts";

const rgb = (h: string) => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const saturacao = (h: string) => { const c = rgb(h), mx = Math.max(...c), mn = Math.min(...c); return mx === 0 ? 0 : (mx - mn) / mx; };

describe("o ceu sem pintura", () => {
  test("o padrao e o pixel, em faixas, e a nevoa tem a cor do horizonte", () => {
    expect(CEU_SEM_PINTURA.modo).toBe("pixel");
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
  test("fraca, menos saturada que a de antes e so na faixa de baixo", () => {
    expect(DIGITAL.grade.alfa).toBeLessThanOrEqual(0.2);
    expect(saturacao(DIGITAL.grade.cor)).toBeLessThan(saturacao("#b8faff"));
    expect(DIGITAL.grade.desde).toBeGreaterThan(0);
  });
});
