/* Os lugares da ilha (L3 de "Lugares da ilha"): os pontos, a altura, o estado e o caminho do modelo de cada um. Pura: sem three e sem DOM.
   Desde a mescla com a LUGARES_3D (2026-11-07) o portao e a barraca ficam onde a grade da ilha os poe (grade.ts, porLugares; o LG-G2 de
   test/ilha_lugares.test.ts confere o lugar em si), com o modelo de LUGARES_MODELOS; aqui so se confere que a tabela le a grade. */
import { describe, expect, it } from "vitest";
import { CMU, LAYOUT_MUNDO_AFASTADO } from "../motor/index.ts";
import { centroDaCelula } from "../motor/mundo.ts";
import { LUGARES, ORDEM_LUGARES, chaoDoLugar, gradeDosLugares, idaDoTreino, lugarDoDestino, pontoDoLugar, type BaseDoMundo } from "../src/telas/pet/ilha/lugares.ts";
import { PLANTA_ILHA, TREINO_MS, TREINO_VEL } from "../src/telas/pet/ilha/constantes.ts";
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
  it("o saco fica perto da praca, no ponto da planta A", () => {
    expect(pontoDoLugar("saco", base)).toEqual([PLANTA_ILHA.lugares.saco[0], PLANTA_ILHA.lugares.saco[1]]);
    expect(pontoDoLugar("saco", base)).toEqual([22, 9]);
    expect(Math.hypot(22 - PLANTA_ILHA.praca.x, 9 - PLANTA_ILHA.praca.z)).toBeLessThan(12);
  });
  it("a ida ao saco no treino dura a distancia sobre TREINO_VEL, com TREINO_MS.ida no minimo (PA-3)", () => {
    expect(idaDoTreino(0)).toBe(TREINO_MS.ida);
    expect(idaDoTreino(2)).toBe(TREINO_MS.ida);
    expect(idaDoTreino(19)).toBeCloseTo((19 / TREINO_VEL) * 1000, 9);
    expect(idaDoTreino(19)).toBeGreaterThan(2500);
  });
  it("o portao e a barraca ficam onde a grade da ilha os poe (o portao ao norte, a barraca a leste da praca), com a altura do chao de la", () => {
    const ilha = ilhaDe(CMU);
    for (const id of ["portao", "barraca"] as const) {
      const g = ilha.lugares.find(l => l.nome === id)!;
      expect(pontoDoLugar(id, base), id).toEqual([g.x, g.z]);
      expect(chaoDoLugar(id, base), id).toBe(g.y);
    }
    expect(ilha.lugares.find(l => l.nome === "portao")!.z).toBeLessThan(0);
    expect(ilha.lugares.find(l => l.nome === "barraca")!.x).toBeGreaterThan(PLANTA_ILHA.praca.x);
    expect(chaoDoLugar("saco", base)).toBe(0);
  });
  it("sem a grade, o ponto do portao e da barraca falha alto (o saco nao precisa dela)", () => {
    const { grade: _g, ...sem } = base;
    expect(() => pontoDoLugar("portao", sem)).toThrow(/grade/);
    expect(() => pontoDoLugar("barraca", sem)).toThrow(/grade/);
    expect(pontoDoLugar("saco", sem)).toEqual(pontoDoLugar("saco", base));
  });
  it("as alturas alvo: 5 para o portao (ITENS_3D) e 3,6 para a barraca refeita (D-LG-OB-4, o barranco atras dela)", () => {
    expect(LUGARES.portao.altura).toBe(5);
    expect(LUGARES.barraca.altura).toBe(3.6);
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
