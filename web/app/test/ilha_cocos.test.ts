/* O coco 3D no chao da ilha (ilha/cocos.ts): um por unidade de sujeira, no lugar onde o pet estava quando ela subiu, parado quando o pet
   anda, saindo os mais antigos quando ela cai, e o pulinho ao surgir. */
import { describe, expect, test } from "vitest";
import { Cocos, escalaAoSurgir, lugarDoCoco } from "../src/telas/pet/ilha/cocos.ts";
import * as THREE from "three";
import { COCO } from "../src/telas/pet/ilha/constantes.ts";

describe("o coco no chao da ilha", () => {
  test("cai perto do pet, no anel, e dois seguidos nao caem no mesmo lugar", () => {
    const a = lugarDoCoco([10, 5], 0), b = lugarDoCoco([10, 5], 1);
    for (const [x, z] of [a, b]) {
      const d = Math.hypot(x - 10, z - 5);
      expect(d).toBeGreaterThanOrEqual(COCO.raio - 1e-9);
      expect(d).toBeLessThanOrEqual(COCO.raio + 2 * COCO.passo + 1e-9);
    }
    expect(Math.hypot(a[0] - b[0], a[1] - b[1])).toBeGreaterThan(0.5);
  });

  test("fica onde caiu quando o pet anda; sai o mais antigo quando a sujeira cai", () => {
    const c = new Cocos(() => new THREE.Group());
    c.sincronizar(1, [4, 4], 0, false);
    const primeiro = c.lugares[0];
    c.sincronizar(1, [20, 20], 100, false);
    expect(c.lugares).toEqual([primeiro]);
    c.sincronizar(2, [20, 20], 200, false);
    const segundo = c.lugares[1];
    expect(Math.hypot(segundo[0] - 20, segundo[1] - 20)).toBeLessThan(2);
    c.sincronizar(1, [20, 20], 300, false);
    expect(c.lugares).toEqual([segundo]);
    c.sincronizar(0, [20, 20], 400, false);
    expect(c.quantos).toBe(0);
    expect(c.raiz.children.length).toBe(0);
  });

  test("os que ja estavam ao abrir aparecem inteiros; o novo surge com o pulinho", () => {
    const c = new Cocos(() => new THREE.Group());
    c.sincronizar(3, [0, 0], 1000, false);
    expect(c.raiz.children.every(g => g.scale.x === 1)).toBe(true);
    c.sincronizar(4, [0, 0], 2000, false);
    expect(c.raiz.children[3].scale.x).toBe(0);
    expect(escalaAoSurgir(COCO.surgirMs)).toBe(1);
    expect(escalaAoSurgir(COCO.surgirMs * 0.7)).toBeGreaterThan(1);
  });

  test("sujeira invalida falha alto", () => {
    expect(() => new Cocos(() => new THREE.Group()).sincronizar(-1, [0, 0], 0, false)).toThrow();
    expect(() => new Cocos(() => new THREE.Group()).sincronizar(1.5, [0, 0], 0, false)).toThrow();
  });
});
