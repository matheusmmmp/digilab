/* Quem tapa o pet (src/telas/pet/ilha/tapar.ts; docs/TAREFA_V3_MOITA_NINHO.md): com a camera de sempre (CAMERA_DESLOC, atras e acima do
   pet), a arvore entre a camera e o pet tapa; a de lado, a de tras e a baixa longe da linha nao tapam; o arbusto colado na frente do pet tapa.
   E a opacidade anda para o alvo, e chega na hora com "reduzir movimento". */
import { describe, expect, test } from "vitest";
import { CAMERA_DESLOC, TAPAR_PET } from "../src/telas/pet/ilha/constantes.ts";
import { opacidadeAgora, quemTapa, type Ponto, type Tapavel } from "../src/telas/pet/ilha/tapar.ts";

const pe: Ponto = [10, 0, 10];
const camera: Ponto = [pe[0] + CAMERA_DESLOC[0], CAMERA_DESLOC[1], pe[2] + CAMERA_DESLOC[2]];
const tapa = (lista: Tapavel[]) => quemTapa(camera, pe, lista, TAPAR_PET.alturaPet, TAPAR_PET.raio, TAPAR_PET.amostras);
const arvore = (x: number, z: number): Tapavel => ({ x, z, y0: 0, topo: 6, raio: 1.5 });

describe("quem tapa o pet", () => {
  test("a arvore entre a camera e o pet tapa", () => {
    expect(tapa([arvore(10, 13)])).toEqual([0]);
  });
  test("a arvore de lado, longe da linha, nao tapa", () => {
    expect(tapa([arvore(16, 13)])).toEqual([]);
  });
  test("a arvore atras do pet nao tapa", () => {
    expect(tapa([arvore(10, 7)])).toEqual([]);
  });
  test("o arbusto baixo colado na frente do pet tapa; o mesmo arbusto perto da camera fica abaixo da linha", () => {
    const arbusto = (z: number): Tapavel => ({ x: 10, z, y0: 0, topo: 1, raio: 0.7 });
    expect(tapa([arbusto(11)])).toEqual([0]);
    expect(tapa([arbusto(20)])).toEqual([]);
  });
  test("a lista volta pelos indices, na ordem", () => {
    expect(tapa([arvore(16, 13), arvore(10, 13), arvore(10, 7), arvore(10.5, 16)])).toEqual([1, 3]);
  });
  test("a base dobrada abaixo da linha: a copa alta perto da camera tapa pelo topo", () => {
    expect(tapa([{ x: 10, z: 22, y0: -2, topo: 8, raio: 1.5 }])).toEqual([0]);
    expect(tapa([{ x: 10, z: 22, y0: -2, topo: 2, raio: 1.5 }])).toEqual([]);
  });
});

describe("a opacidade", () => {
  test("anda para o alvo e chega nele", () => {
    let op = 1;
    for (let i = 0; i < 100; i++) op = opacidadeAgora(op, TAPAR_PET.opacidade, 16, TAPAR_PET.tauMs, false);
    expect(op).toBe(TAPAR_PET.opacidade);
    expect(opacidadeAgora(1, 0.3, 16, 120, false)).toBeGreaterThan(0.3);
    expect(opacidadeAgora(1, 0.3, 16, 120, false)).toBeLessThan(1);
  });
  test("com reduzir movimento, na hora", () => {
    expect(opacidadeAgora(1, TAPAR_PET.opacidade, 16, TAPAR_PET.tauMs, true)).toBe(TAPAR_PET.opacidade);
    expect(opacidadeAgora(0.3, 1, 1, TAPAR_PET.tauMs, true)).toBe(1);
  });
});
