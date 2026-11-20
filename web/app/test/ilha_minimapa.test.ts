/* O fundo do minimapa (src/telas/pet/ilha/minimapa.ts, L1 de "Lugares da ilha"): a grade da ilha vista de cima, um pixel por celula, nas
   cores da paleta do estilo e na agua do shader; o relevo escurece; uma regiao sem cor falha alto. */
import { describe, expect, test } from "vitest";
import { CMU } from "../motor/index.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { AGUA_MAPA, ESCURECE_NIVEL, pixelsDoMapa } from "../src/telas/pet/ilha/minimapa.ts";
import type { PaletaTerreno } from "../src/telas/pet/ilha/cena.ts";

const P: PaletaTerreno = {
  grama: { casa: [0x9cdb72], jardim: [0x8fd16a], campo: [0xa9d870], mata: [0x74b957], moldura: [0x8fd16a] },
  caminho: [0xd9c08c], areia: [0xf3e2b0], fundo: [0xc9b07a], borda: 0x6fb84e, estrato: [0xe9c79a], estratoAreia: [0xe8d39f], margem: [0xa88a5c],
};

describe("o fundo do minimapa", () => {
  const ilha = ilhaDe(CMU), px = pixelsDoMapa(ilha, P);
  const em = (x: number, z: number) => { const i = ((z - ilha.z0) * ilha.larg + (x - ilha.x0)) * 4; return [px[i], px[i + 1], px[i + 2], px[i + 3]]; };

  test("uma celula por pixel, opaco", () => {
    expect(px.length).toBe(ilha.larg * ilha.prof * 4);
    for (let i = 3; i < px.length; i += 4) expect(px[i]).toBe(255);
  });

  test("a casa (dentro da area, nivel 0) tem a grama da casa; a agua, a cor do shader", () => {
    const c = ilha.celulas[(20 - ilha.z0) * ilha.larg + (2 - ilha.x0)];
    expect(c.regiao).toBe("casa");
    if (c.tipo === "grama") expect(em(2, 20)).toEqual([0x9c, 0xdb, 0x72, 255]);
    const iAgua = ilha.celulas.findIndex(k => k.tipo === "agua" && k.nivel <= 0);
    expect(iAgua).toBeGreaterThanOrEqual(0);
    expect([...px.slice(iAgua * 4, iAgua * 4 + 3)]).toEqual([...AGUA_MAPA]);
  });

  test("o planalto escurece pelo nivel", () => {
    const i = ilha.celulas.findIndex(k => k.tipo === "grama" && k.nivel === 1 && k.regiao === "moldura");
    expect(i).toBeGreaterThanOrEqual(0);
    expect(px[i * 4]).toBe(Math.round(0x8f * (1 - ESCURECE_NIVEL)));
  });

  test("uma regiao sem cor na paleta falha alto", () => {
    expect(() => pixelsDoMapa(ilha, { ...P, grama: { casa: [0x9cdb72] } })).toThrow(/regiao sem cor/);
  });
});
