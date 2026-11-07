/* Os lugares da ilha (L3 de "Lugares da ilha"): os pontos, o giro, a altura, o estado e o caminho do modelo de cada um. Pura: sem three e sem DOM. */
import { describe, expect, it } from "vitest";
import { CMU, LAYOUT_MUNDO_AFASTADO } from "../motor/index.ts";
import { centroDaCelula } from "../motor/mundo.ts";
import { BARRACA_DESDE_NINHO, LUGARES, ORDEM_LUGARES, lugarDoDestino, pontoDoLugar, type BaseDoMundo } from "../src/telas/pet/ilha/lugares.ts";
import { SACO_DESDE_NINHO } from "../src/telas/pet/ilha/constantes.ts";

const baseDe = (cm: typeof CMU): BaseDoMundo => {
  const [nx, ny] = centroDaCelula(cm.layout.ninho, cm), [cx, cy] = centroDaCelula(cm.layout.comedouro, cm);
  return { ninho: [nx / cm.sub, ny / cm.sub], comedouro: [cx / cm.sub, cy / cm.sub], area: { w: cm.celulas_x, h: cm.celulas_y } };
};

describe("lugares da ilha", () => {
  const base = baseDe(CMU);
  it("sao tres, na ordem saco, portao, barraca, todos abertos e sem modelo", () => {
    expect(ORDEM_LUGARES).toEqual(["saco", "portao", "barraca"]);
    for (const id of ORDEM_LUGARES) {
      const l = LUGARES[id];
      expect(l.id).toBe(id);
      expect(l.estado, id).toBe("aberto");
      expect(l.modelo, id).toBeNull();
      expect(l.luz, id).toBeNull();
      expect(l.cadeado, id).toBeNull();
      expect(l.nome.length).toBeGreaterThan(0);
    }
  });
  it("o saco fica onde ficava desde a L2: a [3, -4] do ninho", () => {
    const [nx, nz] = base.ninho;
    expect(pontoDoLugar("saco", base)).toEqual([nx + SACO_DESDE_NINHO[0], nz + SACO_DESDE_NINHO[1]]);
    expect(pontoDoLugar("saco", base)).toEqual([7.5, 11.5]);
  });
  it("o portao fica no fim do caminho de terra, a leste do comedouro, dentro da area andavel", () => {
    const [x, z] = pontoDoLugar("portao", base);
    expect(x).toBeGreaterThan(base.comedouro[0]);
    expect(x).toBeLessThan(16);                     // ainda na casa (o caminho de terra so existe nela)
    expect(z).toBeGreaterThanOrEqual(0); expect(z).toBeLessThan(base.area.h);
    expect([x, z]).toEqual([15.5, 17]);
  });
  it("a barraca fica a oeste do ninho, rente ao barranco, dentro da area andavel", () => {
    const [x, z] = pontoDoLugar("barraca", base);
    expect(x).toBeLessThan(base.ninho[0]);
    expect(x).toBeGreaterThanOrEqual(1.2);
    expect(x).toBeLessThan(4);
    expect([x, z]).toEqual([base.ninho[0] + BARRACA_DESDE_NINHO[0], base.ninho[1] + BARRACA_DESDE_NINHO[1]]);
  });
  it("as alturas alvo sao as do ITENS_3D: 5 para o portao e 4 para a barraca", () => {
    expect(LUGARES.portao.altura).toBe(5);
    expect(LUGARES.barraca.altura).toBe(4);
  });
  it("nenhum ponto sai da area andavel em outro layout (o afastado), e os tres ficam distantes entre si", () => {
    const cm = { ...CMU, layout: LAYOUT_MUNDO_AFASTADO }, b = baseDe(cm);
    const pts = ORDEM_LUGARES.map(id => pontoDoLugar(id, b));
    for (const [x, z] of pts) { expect(x).toBeGreaterThanOrEqual(0); expect(x).toBeLessThan(cm.celulas_x); expect(z).toBeGreaterThanOrEqual(0); expect(z).toBeLessThan(cm.celulas_y); }
    for (let i = 0; i < 3; i++) for (let j = i + 1; j < 3; j++) expect(Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])).toBeGreaterThan(3);
  });
  it("cada menu da ilha acha o seu lugar", () => {
    expect(lugarDoDestino("crescer")).toBe("saco");
    expect(lugarDoDestino("lutar")).toBe("portao");
    expect(lugarDoDestino("diario")).toBe("barraca");
    expect(lugarDoDestino("conversar")).toBeNull();
    expect(lugarDoDestino("pet")).toBeNull();
  });
});

describe("o pet nos lugares grandes", () => {
  it("fica na frente do lugar, do lado da camera, alem do raio da base, e a esquerda na tela", async () => {
    const { pontoDoPet, PET_MARGEM, PET_LADO } = await import("../src/telas/pet/ilha/lugares.ts");
    const frente: [number, number] = [0, -1], direita: [number, number] = [1, 0], ponto: [number, number] = [10, 10];   // a camera olha para o norte
    for (const id of ["portao", "barraca"] as const) {
      const [x, z] = pontoDoPet(ponto, LUGARES[id].raio, frente, direita);
      expect(z - ponto[1], id).toBeCloseTo(LUGARES[id].raio + PET_MARGEM, 6);     // do lado da camera (ao sul do lugar)
      expect(x - ponto[0], id).toBeCloseTo(-PET_LADO, 6);                          // a esquerda dele na tela
      expect(Math.hypot(x - ponto[0], z - ponto[1]), id).toBeGreaterThan(LUGARES[id].raio);
    }
  });
});
