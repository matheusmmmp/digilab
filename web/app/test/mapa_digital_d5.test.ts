/* O cel shading do estilo Digital (docs/TAREFA_V3_MAPA_DIGITAL.md, D5): o chao pintado, os tufos, as flores em manchas e o contorno.
   - D5-G1: o terreno do Digital marca a grama de cima (aPinta 1, so nas celulas de grama, de frente para cima, na primeira cor da regiao:
     sem o xadrez) e a pedra do barranco (aPinta 2); o da Ilha nao marca nada (o chao da Ilha nao muda).
   - D5-G2: os tufos so nascem em celula de grama, na altura da tabela, sempre iguais, e nao escrevem a profundidade (o contorno nao os pega).
   - D5-G3: as flores sao sempre as mesmas (rng propria) e nao escrevem a profundidade.
   - D5-G4: so o estilo Digital pede o contorno.
   Sem DOM (vitest em node): a cena.ts pinta texturas num canvas ao carregar, entao o teste poe um document falso antes de importa-la. */
import * as THREE from "three";
import { beforeAll, describe, expect, test } from "vitest";
import { CMU_MVP } from "../motor/index.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";

/* um canvas que aceita tudo e nao desenha nada (so para a cena.ts carregar em node) */
function canvasFalso(): unknown {
  /* cada metodo devolve outro objeto que aceita tudo (o gradiente do createRadialGradient, por exemplo) */
  const tudo: unknown = new Proxy(function () {}, { get: () => tudo, apply: () => tudo, set: () => true });
  const ctx: unknown = new Proxy({}, { get: (_a, k) => (k === "getImageData" ? () => ({ data: new Uint8ClampedArray(4) }) : () => tudo), set: () => true });
  return { width: 0, height: 0, getContext: () => ctx, style: {} };
}
type Cena = typeof import("../src/telas/pet/ilha/cena.ts");
type Estilos = typeof import("../src/telas/pet/ilha/estilos.ts");
let cena: Cena, estilos: Estilos;
beforeAll(async () => {
  /* o estilo Digital pede o ceu pintado (TextureLoader): uma imagem que nunca carrega */
  const imagem = () => ({ style: {}, addEventListener() {}, removeEventListener() {}, setAttribute() {} });
  (globalThis as { document?: unknown }).document ??= { createElement: () => canvasFalso(), createElementNS: () => imagem() };
  cena = await import("../src/telas/pet/ilha/cena.ts");
  estilos = await import("../src/telas/pet/ilha/estilos.ts");
});

describe("o cel shading do Digital (D5)", () => {
  const ilha = ilhaDe(CMU_MVP);

  test("D5-G1: a grama e a pedra pintadas so no Digital, sem o xadrez", () => {
    const t = cena.terreno(ilha, cena.PALETA_DIGITAL), g = t.geometry;
    const pin = g.getAttribute("aPinta"), pos = g.getAttribute("position"), nor = g.getAttribute("normal"), col = g.getAttribute("color");
    let grama = 0, pedra = 0;
    for (let v = 0; v < pin.count; v++) {
      const p = pin.getX(v);
      if (p === 1) {
        grama++;
        expect(nor.getY(v)).toBeGreaterThan(0.9);
      } else if (p === 2) {
        pedra++;
        expect(Math.abs(nor.getY(v))).toBeLessThan(0.1);
      } else expect(p).toBe(0);
    }
    /* cada celula de grama da um quadrado em cima (6 vertices); a cor dele e a primeira da regiao */
    let celulas = 0;
    for (let j = 0; j < ilha.prof; j++) for (let i = 0; i < ilha.larg; i++) if (ilha.cel(ilha.x0 + i, ilha.z0 + j)!.tipo === "grama") celulas++;
    expect(grama).toBe(celulas * 6);
    expect(pedra).toBeGreaterThan(0);
    /* a cor do vertice e a do THREE.Color (no espaco linear), como o terreno a grava */
    const primeiras = Object.values(cena.PALETA_DIGITAL.grama).map(c => new THREE.Color(c[0]));
    for (let v = 0; v < pin.count; v += 3) if (pin.getX(v) === 1) {
      const k = new THREE.Color(col.getX(v), col.getY(v), col.getZ(v));
      expect(primeiras.some(p => Math.abs(p.r - k.r) + Math.abs(p.g - k.g) + Math.abs(p.b - k.b) < 1e-6), k.getHexString()).toBe(true);
    }
    expect(pos.count).toBe(pin.count);
    const ilhaPin = cena.terreno(ilha).geometry.getAttribute("aPinta");
    for (let v = 0; v < ilhaPin.count; v++) expect(ilhaPin.getX(v)).toBe(0);
  });

  test("D5-G2: os tufos so na grama, na altura da tabela, sempre iguais e fora do contorno", () => {
    const a = cena.tufos(ilha), b = cena.tufos(ilha), pa = a.geometry.getAttribute("position");
    expect(Array.from(pa.array as Float32Array)).toEqual(Array.from(b.geometry.getAttribute("position").array as Float32Array));
    expect(pa.count % 3).toBe(0);
    expect(pa.count).toBeGreaterThan(0);
    for (let v = 0; v < pa.count; v += 3) {
      /* a base da folha (os dois primeiros vertices) fica numa celula de grama; a ponta, acima do chao */
      const bx = (pa.getX(v) + pa.getX(v + 1)) / 2, bz = (pa.getZ(v) + pa.getZ(v + 1)) / 2;
      expect(ilha.cel(Math.floor(bx), Math.floor(bz))?.tipo).toBe("grama");
      const h = pa.getY(v + 2) - pa.getY(v);
      expect(h).toBeGreaterThan(0.1); expect(h).toBeLessThan(0.3);
    }
    expect((a.material as { depthWrite: boolean }).depthWrite).toBe(false);
  });

  test("D5-G3: as flores sempre iguais e fora do contorno", () => {
    const a = cena.flores(ilha), b = cena.flores(ilha);
    expect(Array.from(a.geometry.getAttribute("position").array as Float32Array)).toEqual(Array.from(b.geometry.getAttribute("position").array as Float32Array));
    expect((a.material as { depthWrite: boolean }).depthWrite).toBe(false);
  });

  test("D5-G4: so o Digital pede o contorno", () => {
    expect(estilos.estiloDe("digital", "http://x/").contorno).toBeDefined();
    for (const m of ["ilha", "voxel", "floresta", "cassette"] as const) expect(estilos.estiloDe(m, "http://x/").contorno, m).toBeUndefined();
  });
});
