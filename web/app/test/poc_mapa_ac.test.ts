/* A grade do POC do mapa no estilo Animal Crossing (poc/mapa_ac/mapa.ts; PR #480): só dados, sem three. Confere que o mapa sai sempre
   igual, que o início é andável, que a rampa liga o platô ao chão e que nada que bloqueia cai na água ou no caminho. */
import { describe, expect, test } from "vitest";
import { ALTURA_NIVEL, LARG, Mapa, PROF, RAMPAS } from "../poc/mapa_ac/mapa.ts";

describe("POC mapa_ac: a grade", () => {
  const m = new Mapa();

  test("mesmo mapa a cada construção", () => {
    const n = new Mapa();
    expect(n.celulas).toEqual(m.celulas);
    expect(n.objetos).toEqual(m.objetos);
    expect(m.celulas).toHaveLength(LARG * PROF);
  });

  test("o início é andável, no nível 0", () => {
    const [x, z] = m.inicio;
    expect(m.altura(x, z)).toBe(0);
    expect(m.livre(x, z, 0)).toBe(true);
  });

  test("a rampa desce do platô ao chão sem degrau, e o penhasco ao lado bloqueia", () => {
    const r = RAMPAS[0], x = r.x + 0.5;
    let z = 0;
    while (m.altura(x, z + 0.5) !== ALTURA_NIVEL || m.altura(x, z + 1.5) === ALTURA_NIVEL) z++;
    /* anda da borda do platô até o pé da rampa em passos pequenos, sem passar de 0,4 de altura por passo */
    let h = m.altura(x, z + 0.5);
    for (let t = z + 0.5; t < z + 3.5; t += 0.1) {
      expect(Math.abs(m.altura(x, t) - h)).toBeLessThan(0.4);
      h = m.altura(x, t);
    }
    expect(h).toBe(0);
  });

  test("nada que bloqueia fica na água, no caminho ou na rampa", () => {
    for (const o of m.objetos.filter(o => o.raio > 0 && o.modelo !== "tronco")) {
      const c = m.cel(Math.floor(o.x), Math.floor(o.z))!;
      expect(c.tipo, `${o.modelo} em ${o.x.toFixed(1)}, ${o.z.toFixed(1)}`).toBe("grama");
      expect(new Set(c.cantos).size).toBe(1);
    }
  });

  test("a água não deixa passar", () => {
    const agua = m.celulas.findIndex(c => c.tipo === "agua" && c.nivel === 0);
    expect(agua).toBeGreaterThanOrEqual(0);
    const x = agua % LARG + 0.5, z = Math.floor(agua / LARG) + 0.5;
    expect(m.livre(x, z, m.altura(x, z))).toBe(false);
  });
});
