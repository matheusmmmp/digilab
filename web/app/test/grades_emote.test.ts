/* A gota sobre a cabeca do pet (docs/TAREFA_V3_UX_TELA_PET.md, secao 21): a grade em lagrima e o contorno de adesivo no lugar da caixa
   branca. So vista. */
import { describe, expect, it } from "vitest";
import { S, contornoGrade } from "../src/grades.ts";

/** um contexto falso que guarda os pixels pintados pelo fillRect (cada fillRect em unidades inteiras da grade) */
function ctxFalso(): { ctx: CanvasRenderingContext2D; pintados: Set<string>; cores: Set<string> } {
  const pintados = new Set<string>(), cores = new Set<string>();
  const ctx = {
    fillStyle: "",
    fillRect(x: number, y: number, w: number, h: number) {
      cores.add(String(this.fillStyle));
      for (let i = 0; i < w; i++) for (let j = 0; j < h; j++) pintados.add(`${x + i},${y + j}`);
    },
  };
  return { ctx: ctx as unknown as CanvasRenderingContext2D, pintados, cores };
}

describe("a gota em lagrima", () => {
  it("tem a ponta em cima e o bojo embaixo, mais largo que a ponta", () => {
    const g = S.gota, largura = (l: string) => l.replace(/^\.+|\.+$/g, "").length;
    expect(g.length).toBe(8);
    expect(largura(g[0])).toBe(1);
    const maior = Math.max(...g.map(largura));
    expect(maior).toBe(7);
    /* a linha mais larga fica na metade de baixo */
    expect(g.findIndex(l => largura(l) === maior)).toBeGreaterThanOrEqual(g.length / 2);
    /* tem o brilho */
    expect(g.join("")).toContain("w");
  });
});

describe("a marca de raiva", () => {
  it("e quadrada, simetrica nos dois eixos e vazia no centro", () => {
    const g = S.raiva, n = g.length;
    expect(g.every(l => l.length === n)).toBe(true);
    g.forEach((l, y) => {
      expect(l).toBe([...l].reverse().join(""));
      expect(l).toBe(g[n - 1 - y]);
    });
    expect(g[(n - 1) / 2][(n - 1) / 2]).toBe(".");
  });
});

describe("o contorno de adesivo", () => {
  it("segue o desenho: os cantos da caixa ficam vazios, em volta de cada pixel fica pintado", () => {
    const { ctx, pintados, cores } = ctxFalso();
    contornoGrade(ctx, S.gota, 10, 20);
    expect([...cores]).toEqual(["#FFFFFF"]);
    /* o canto de cima a esquerda da caixa antiga (x0-1, y0-1) nao e pintado: a ponta da gota fica no meio */
    expect(pintados.has("9,19")).toBe(false);
    expect(pintados.has("10,20")).toBe(false);
    /* acima da ponta (x 3 da grade) fica o contorno */
    expect(pintados.has("13,19")).toBe(true);
    /* todo pixel do desenho fica coberto pelo contorno */
    S.gota.forEach((l, y) => [...l].forEach((ch, x) => { if (ch !== ".") expect(pintados.has(`${10 + x},${20 + y}`)).toBe(true); }));
  });
});
