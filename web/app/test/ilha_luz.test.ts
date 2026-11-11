/* A hierarquia de luz da ilha (a regra 1 de "guiar o olhar sem texto"; docs/pranchas/ux-ilha-luz/, docs/TAREFA_V3_UX_TELA_PET.md secoes 27
   e 28): LZ-1 a LZ-5 aprovadas em 2026-11-09, a B por padrao. Confere que a B liga sem parametro e que `?luz=0` desliga, que os focos cobrem
   o lar, a praca, os lugares abertos e os caminhos e cabem no shader, sem o cais trancado, e que as propostas vao da mais forte a mais leve.
   Os numeros sao PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { LUZ_MAX, LUZ_PROPOSTA, listaDeFocos, propostaDe, recebeLuz } from "../src/telas/pet/ilha/luzConta.ts";
import { LUZ_HIERARQUIA, PLANTA_ILHA } from "../src/telas/pet/ilha/constantes.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { LUGAR_ABERTO } from "../src/telas/pet/lugaresIlha.ts";

describe("a hierarquia de luz (LZ-1 a LZ-5)", () => {
  test("a B liga sem parametro, ?luz=0 desliga; so os materiais de cor do mundo recebem o termo (nao os aditivos, as sombras nem as linhas)", () => {
    expect(LUZ_PROPOSTA).toBe("b");
    expect(propostaDe(null)).toBe("b");
    expect(propostaDe("0")).toBeNull();
    expect(propostaDe("a")).toBe("a");
    expect(() => propostaDe("x")).toThrow();
    const toon = new THREE.MeshToonMaterial();
    expect(recebeLuz(toon)).toBe(true);
    expect(recebeLuz(toon, null)).toBe(false);
    expect(recebeLuz(new THREE.MeshBasicMaterial({ blending: THREE.AdditiveBlending }), "b")).toBe(false);
    expect(recebeLuz(new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false }), "b")).toBe(false);
    expect(recebeLuz(new THREE.LineBasicMaterial(), "b")).toBe(false);
  });

  for (const cm of [CMU_MVP, CMU]) test(`os focos cobrem o lar, a praca, os lugares e os caminhos e cabem no shader (${cm.layout.nome})`, () => {
    const ilha = ilhaDe(cm), f = listaDeFocos(ilha), perto = (x: number, z: number) => f.some(([fx, fz, r]) => Math.hypot(fx - x, fz - z) < r);
    expect(f.length).toBeLessThanOrEqual(LUZ_MAX);
    expect(perto(cm.layout.ninho[0] + 0.5, cm.layout.ninho[1] + 0.5)).toBe(true);
    expect(perto(PLANTA_ILHA.praca.x, PLANTA_ILHA.praca.z)).toBe(true);
    for (const l of ilha.lugares) if (LUGAR_ABERTO[l.nome]) expect(perto(l.x, l.z), l.nome).toBe(true);
    /* o cais trancado nao acende (LZ-2): nenhum foco de lugar nele; com ele aberto, entra um foco a mais */
    const cais = ilha.lugares.find(l => l.nome === "cais");
    expect(cais).toBeDefined();
    expect(f.some(([fx, fz]) => fx === cais!.x && fz === cais!.z)).toBe(false);
    expect(listaDeFocos(ilha, { ...LUGAR_ABERTO, cais: true }).length).toBe(f.length + 1);
    /* todo ponto dos caminhos fica dentro de algum foco: o caminho e uma faixa clara continua */
    for (const c of ilha.caminhos) for (let k = 1; k < c.length; k++) for (let t = 0; t <= 1; t += 0.05) {
      const x = c[k - 1][0] + (c[k][0] - c[k - 1][0]) * t, z = c[k - 1][1] + (c[k][1] - c[k - 1][1]) * t;
      expect(perto(x, z), `caminho em (${x.toFixed(1)}, ${z.toFixed(1)})`).toBe(true);
    }
  });

  test("as propostas vao da forte (A) a so quente (C); o chao pesa menos, para a grama nao ficar cinza", () => {
    const { a, b, c } = LUZ_HIERARQUIA.propostas;
    expect(a.escuro).toBeLessThan(b.escuro);
    expect(b.escuro).toBeLessThan(c.escuro);
    expect(a.dessat).toBeGreaterThan(b.dessat);
    expect(c.escuro).toBe(1);
    expect(c.dessat).toBe(0);
    for (const p of [a, b, c]) expect(p.quente).toBeGreaterThan(0);
    expect(LUZ_HIERARQUIA.pesoChao).toBeGreaterThan(0);
    expect(LUZ_HIERARQUIA.pesoChao).toBeLessThan(1);
  });
});
