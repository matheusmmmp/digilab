/* Os lugares da ilha (L3 de "Lugares da ilha"): os pontos, a altura, o estado e o caminho do modelo de cada um. Pura: sem three e sem DOM.
   Desde a mescla com a LUGARES_3D (2026-11-07) o portao e a barraca ficam onde a grade da ilha os poe (grade.ts, porLugares; o LG-G2 de
   test/ilha_lugares.test.ts confere o lugar em si), com o modelo de LUGARES_MODELOS; aqui so se confere que a tabela le a grade. */
import { describe, expect, it } from "vitest";
import { CMU, LAYOUT_MUNDO_AFASTADO } from "../motor/index.ts";
import { centroDaCelula } from "../motor/mundo.ts";
import { LUGARES, ORDEM_LUGARES, chaoDoLugar, gradeDosLugares, lugarDoDestino, pontoDoLugar, type BaseDoMundo } from "../src/telas/pet/ilha/lugares.ts";
import { SACO_DESDE_NINHO } from "../src/telas/pet/ilha/constantes.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { LUGARES_LUZ, LUGARES_MODELOS } from "../src/telas/pet/ilha/modelos.ts";

const baseDe = (cm: typeof CMU): BaseDoMundo => {
  const [nx, ny] = centroDaCelula(cm.layout.ninho, cm), [cx, cy] = centroDaCelula(cm.layout.comedouro, cm);
  return { ninho: [nx / cm.sub, ny / cm.sub], comedouro: [cx / cm.sub, cy / cm.sub], area: { w: cm.celulas_x, h: cm.celulas_y }, grade: gradeDosLugares(ilhaDe(cm)) };
};

describe("lugares da ilha", () => {
  const base = baseDe(CMU);
  it("sao tres, na ordem saco, portao, barraca, todos abertos; o portao e a barraca com o modelo da LUGARES_3D, o saco com o desenho de itens.ts", () => {
    expect(ORDEM_LUGARES).toEqual(["saco", "portao", "barraca"]);
    for (const id of ORDEM_LUGARES) {
      const l = LUGARES[id];
      expect(l.id).toBe(id);
      expect(l.estado, id).toBe("aberto");
      expect(l.cadeado, id).toBeNull();
      expect(l.nome.length).toBeGreaterThan(0);
    }
    expect(LUGARES.saco.modelo).toBeNull();
    expect(LUGARES.saco.luz).toBeNull();
    expect(LUGARES.portao.modelo).toBe("lugares/" + LUGARES_MODELOS.portao.arquivos[0]);
    expect(LUGARES.barraca.modelo).toBe("lugares/" + LUGARES_MODELOS.barraca.arquivos[0]);
    expect(LUGARES.portao.luz).toBe("lugares/" + LUGARES_LUZ.portao);
    expect(LUGARES.barraca.luz).toBeNull();
  });
  it("o saco fica onde ficava desde a L2: a [3, -4] do ninho", () => {
    const [nx, nz] = base.ninho;
    expect(pontoDoLugar("saco", base)).toEqual([nx + SACO_DESDE_NINHO[0], nz + SACO_DESDE_NINHO[1]]);
    expect(pontoDoLugar("saco", base)).toEqual([7.5, 11.5]);
  });
  it("o portao e a barraca ficam onde a grade da ilha os poe (ao norte da area andavel), com a altura do chao de la", () => {
    const ilha = ilhaDe(CMU);
    for (const id of ["portao", "barraca"] as const) {
      const g = ilha.lugares.find(l => l.nome === id)!;
      expect(pontoDoLugar(id, base), id).toEqual([g.x, g.z]);
      expect(chaoDoLugar(id, base), id).toBe(g.y);
      expect(g.z, id).toBeLessThan(0);
    }
    expect(chaoDoLugar("saco", base)).toBe(0);
  });
  it("sem a grade, o ponto do portao e da barraca falha alto (o saco nao precisa dela)", () => {
    const { grade: _g, ...sem } = base;
    expect(() => pontoDoLugar("portao", sem)).toThrow(/grade/);
    expect(() => pontoDoLugar("barraca", sem)).toThrow(/grade/);
    expect(pontoDoLugar("saco", sem)).toEqual(pontoDoLugar("saco", base));
  });
  it("as alturas alvo sao as do ITENS_3D: 5 para o portao e 4 para a barraca", () => {
    expect(LUGARES.portao.altura).toBe(5);
    expect(LUGARES.barraca.altura).toBe(4);
  });
  it("em outro layout (o afastado) o saco fica na area andavel, e os tres ficam distantes entre si", () => {
    const cm = { ...CMU, layout: LAYOUT_MUNDO_AFASTADO }, b = baseDe(cm);
    const pts = ORDEM_LUGARES.map(id => pontoDoLugar(id, b));
    const [sx, sz] = pts[0];
    expect(sx).toBeGreaterThanOrEqual(0); expect(sx).toBeLessThan(cm.celulas_x); expect(sz).toBeGreaterThanOrEqual(0); expect(sz).toBeLessThan(cm.celulas_y);
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
