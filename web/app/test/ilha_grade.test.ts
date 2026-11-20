/* A grade da ilha (src/telas/pet/ilha/grade.ts; docs/TAREFA_V3_HABITAT_ILHA_3D.md, secao 5, regra 5 e H2): mesma entrada, mesma ilha;
   a area andavel e o mapa do motor, plana e livre (so decoracao baixa e as arvores do layout la dentro); a borda do mapa casa com o pe
   do penhasco (norte e oeste), com o rio (leste) e com a areia (sul); a moldura tem pelo menos 8 celulas de cada lado. */
import { describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { MOLDURA, ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { ALTURA_BAIXA, MODELOS } from "../src/telas/pet/ilha/modelos.ts";

describe("a grade da ilha", () => {
  test("mesmo layout, mesma ilha; outro layout, outra decoracao", () => {
    const a = ilhaDe(CMU_MVP), b = ilhaDe(CMU_MVP), c = ilhaDe(CMU);
    expect(JSON.stringify([a.celulas, a.objetos])).toBe(JSON.stringify([b.celulas, b.objetos]));
    expect(JSON.stringify(a.objetos)).not.toBe(JSON.stringify(c.objetos));
  });

  for (const cm of [CMU_MVP, CMU]) test(`a area andavel e plana e livre (layout ${cm.layout.nome})`, () => {
    const ilha = ilhaDe(cm), W = cm.celulas_x, H = cm.celulas_y;
    expect([ilha.area.w, ilha.area.h]).toEqual([W, H]);
    for (let z = 0; z < H; z++) for (let x = 0; x < W; x++) {
      const c = ilha.cel(x, z)!;
      expect(c.nivel, `${x},${z}`).toBe(0);
      expect(["grama", "caminho"], `${x},${z}`).toContain(c.tipo);
      expect(c.cantos, `${x},${z}`).toEqual([0, 0, 0, 0]);
    }
    const dentro = ilha.objetos.filter(o => ilha.naArea(Math.floor(o.x), Math.floor(o.z)));
    for (const o of dentro) {
      if (o.doMotor) continue;
      expect(MODELOS[o.modelo].baixo, `${o.modelo} em ${o.x},${o.z}`).toBe(true);
      expect(MODELOS[o.modelo].altura * o.escala, `${o.modelo} em ${o.x},${o.z}`).toBeLessThanOrEqual(ALTURA_BAIXA * 1.2);
    }
    /* as arvores do layout, uma por arvore do motor, no centro da celula dela */
    const doMotor = ilha.objetos.filter(o => o.doMotor).map(o => [o.doMotor, o.x - 0.5, o.z - 0.5]);
    expect(doMotor).toEqual(cm.layout.arvores.map(([id, x, y]) => [id, x, y]));
    /* nada alto rente a area por fora: a copa nao cobre o pet na borda */
    for (const o of ilha.objetos) if (!o.doMotor && !MODELOS[o.modelo].baixo) expect(ilha.distanciaDaArea(o.x, o.z), o.modelo).toBeGreaterThanOrEqual(1.5);
  });

  test("a borda do mapa: o pe do penhasco ao norte e a oeste, o rio a leste e a areia ao sul", () => {
    const ilha = ilhaDe(CMU_MVP), W = CMU_MVP.celulas_x, H = CMU_MVP.celulas_y;
    for (let x = 0; x < W; x++) {
      expect(ilha.cel(x, -1)!.nivel, `norte ${x}`).toBeGreaterThanOrEqual(1);
      expect(ilha.cel(x, H)!.tipo, `sul ${x}`).toBe("areia");
    }
    for (let z = 0; z < H; z++) {
      expect(ilha.cel(-1, z)!.nivel, `oeste ${z}`).toBeGreaterThanOrEqual(1);
      expect(ilha.cel(W, z)!.tipo, `leste ${z}`).toBe("agua");
    }
    for (const lado of Object.values(MOLDURA)) expect(lado).toBeGreaterThanOrEqual(8);
    expect([ilha.x0, ilha.z0, ilha.larg, ilha.prof]).toEqual([-MOLDURA.oeste, -MOLDURA.norte, W + MOLDURA.oeste + MOLDURA.leste, H + MOLDURA.norte + MOLDURA.sul]);
  });

  test("a moldura tem a cachoeira (o rio desce do plato), a lagoa no plato e o mar ao sul", () => {
    const ilha = ilhaDe(CMU_MVP);
    let cachoeira = false, lagoa = false, mar = false;
    for (let z = ilha.z0; z < ilha.z0 + ilha.prof; z++) for (let x = ilha.x0; x < ilha.x0 + ilha.larg; x++) {
      const c = ilha.cel(x, z)!, sul = ilha.cel(x, z + 1);
      if (c.tipo === "agua" && c.nivel === 1 && sul?.tipo === "agua" && sul.nivel === 0) cachoeira = true;
      if (c.tipo === "agua" && c.nivel === 1 && x < 0) lagoa = true;
      if (c.tipo === "agua" && c.nivel === -1) mar = true;
    }
    expect([cachoeira, lagoa, mar]).toEqual([true, true, true]);
  });
});
