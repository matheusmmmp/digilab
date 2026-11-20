/* A planta A na grade da ilha (src/telas/pet/ilha/grade.ts e constantes.ts, PLANTA_ILHA; docs/pranchas/ux-ilha-planta-a/, PA-1 a PA-5
   aprovadas em 2026-11-08) e o fim da ilha (FIM_ILHA). PL-1: a praca e os caminhos de terra, que so pintam a grama da area.
   PL-2: nenhum lugar sobre o caminho. PL-3: a decoracao que cai no caminho some da vista. PL-4: a moldura em bosques e vaos. PL-5: os
   degraus a leste do rio. Os pontos sao PROPOSTO, SEM FONTE. */
import { describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { FIM_ILHA, PLANTA_ILHA } from "../src/telas/pet/ilha/constantes.ts";
import { ALTURA_NIVEL, NIVEL_AGUA, RIO, ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { MODELOS } from "../src/telas/pet/ilha/modelos.ts";

const P = PLANTA_ILHA;
const distLinha = (x: number, z: number, l: readonly (readonly [number, number])[]) => {
  let d = Infinity;
  for (let k = 1; k < l.length; k++) {
    const [ax, az] = l[k - 1], [bx, bz] = l[k], dx = bx - ax, dz = bz - az, q = dx * dx + dz * dz;
    const t = q === 0 ? 0 : Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / q));
    d = Math.min(d, Math.hypot(ax + t * dx - x, az + t * dz - z));
  }
  return d;
};

describe("a planta A na grade da ilha", () => {
  for (const cm of [CMU_MVP, CMU]) {
    const ilha = ilhaDe(cm), lugar = (n: string) => ilha.lugares.find(l => l.nome === n)!;

    test(`PL-1: a praca em (31, 16) e os caminhos praca -> lar, portao, barraca e cais (layout ${cm.layout.nome})`, () => {
      expect([P.praca.x, P.praca.z]).toEqual([31, 16]);
      expect(ilha.cel(31, 16)!.tipo).toBe("caminho");
      /* quatro caminhos, todos saindo da praca; o do lar acaba no comedouro do layout */
      expect(ilha.caminhos).toHaveLength(4);
      expect(ilha.caminhos[0][0]).toEqual([cm.layout.comedouro[0] + 0.5, cm.layout.comedouro[1] + 0.5]);
      for (const l of ilha.caminhos) expect(l.some(p => p[0] === P.praca.x && p[1] === P.praca.z)).toBe(true);
      /* o do portao e reto e vai ao norte */
      expect(P.caminhos.portao.every(p => p[0] === P.praca.x)).toBe(true);
      /* o caminho so pinta a grama da area andavel: fora dela nada e caminho */
      for (const c of ilha.celulas) if (c.tipo === "caminho") expect(c.nivel).toBe(0);
      for (let z = ilha.z0; z < ilha.z0 + ilha.prof; z++) for (let x = ilha.x0; x < ilha.x0 + ilha.larg; x++)
        if (!ilha.naArea(x, z)) expect(ilha.cel(x, z)!.tipo, `${x},${z}`).not.toBe("caminho");
      /* cada caminho chega perto do lugar dele: a celula do ultimo ponto na area, ou a vizinha, e caminho */
      for (const l of ilha.caminhos) {
        const meio = l[Math.floor(l.length / 2)];
        if (ilha.naArea(Math.floor(meio[0]), Math.floor(meio[1]))) expect(ilha.cel(Math.floor(meio[0]), Math.floor(meio[1]))!.tipo).toBe("caminho");
      }
    });

    test(`PL-2: nenhum lugar sobre o caminho (layout ${cm.layout.nome})`, () => {
      for (const n of ["portao", "barraca"] as const) {
        const l = lugar(n), r = P.lugares[n].base;
        for (let z = Math.floor(l.z - r); z <= Math.ceil(l.z + r); z++) for (let x = Math.floor(l.x - r); x <= Math.ceil(l.x + r); x++)
          if (Math.hypot(x + 0.5 - l.x, z + 0.5 - l.z) < r && ilha.cel(x, z)) expect(ilha.cel(x, z)!.tipo, `${n} em ${x},${z}`).not.toBe("caminho");
      }
      /* o saco fica fora do caminho, longe de qualquer caminho */
      const [sx, sz] = P.lugares.saco;
      expect(ilha.cel(Math.floor(sx), Math.floor(sz))!.tipo).toBe("grama");
      for (const l of ilha.caminhos) expect(distLinha(sx, sz, l)).toBeGreaterThan(P.raioCaminho + 1);
      /* o cais fica na beira do mar, onde o caminho do cais acaba */
      expect(Math.abs(lugar("cais").x - P.caminhos.cais[P.caminhos.cais.length - 1][0])).toBeLessThanOrEqual(1);
    });

    test(`PL-3: a decoracao do caminho some da vista, e a lista de objetos nao muda (layout ${cm.layout.nome})`, () => {
      ilha.objetos.forEach((o, i) => {
        if (o.doMotor !== null) return;
        if (ilha.cel(Math.floor(o.x), Math.floor(o.z))!.tipo === "caminho") expect(ilha.escondidos.has(i), `${o.modelo} em ${o.x},${o.z}`).toBe(true);
      });
      for (const o of ilha.extras) expect(ilha.naArea(Math.floor(o.x), Math.floor(o.z)), `${o.modelo} em ${o.x},${o.z}`).toBe(false);
    });

    test(`PL-4: a moldura em bosques e vaos (layout ${cm.layout.nome})`, () => {
      const naElipse = (x: number, z: number, e: readonly number[], f = 1) => ((x - e[0]) / (e[2] * f)) ** 2 + ((z - e[1]) / (e[3] * f)) ** 2 <= 1;
      const leste = (x: number) => x >= ilha.rioX + RIO.largura;
      const arvore = (m: string) => m === "pinheiro" || m === "arvore_redonda";
      /* as arvores da moldura que ficam a vista: num bosque ou na mata a leste do rio, nunca num vao */
      ilha.objetos.forEach((o, i) => {
        if (o.doMotor !== null || ilha.escondidos.has(i) || !arvore(o.modelo) || ilha.naArea(Math.floor(o.x), Math.floor(o.z))) return;
        expect(P.vaos.some(v => naElipse(o.x, o.z, v)), `${o.modelo} em ${o.x},${o.z}`).toBe(false);
        expect(leste(o.x) || P.bosques.some(b => naElipse(o.x, o.z, b)), `${o.modelo} em ${o.x},${o.z}`).toBe(true);
      });
      /* cada bosque ganha arvores; nada alto rente a area */
      for (const b of P.bosques) expect(ilha.extras.some(o => arvore(o.modelo) && naElipse(o.x, o.z, b)), `bosque em ${b[0]},${b[1]}`).toBe(true);
      for (const o of ilha.extras) if (arvore(o.modelo)) {
        expect(ilha.distanciaDaArea(o.x, o.z)).toBeGreaterThanOrEqual(1.5);
        expect(P.vaos.some(v => naElipse(o.x, o.z, v))).toBe(false);
        expect(MODELOS[o.modelo].baixo).toBe(false);
      }
    });

    test(`PL-5: a leste do rio, a mata sobe em degraus ate o morro (layout ${cm.layout.nome})`, () => {
      const x0 = ilha.rioX + RIO.largura, ultima = ilha.x0 + ilha.larg - 1;
      for (let z = 0; z < ilha.area.h; z++) {
        const c = ilha.cel(ultima, z)!;
        expect(c.nivel, `borda leste em ${z}`).toBe(FIM_ILHA.degraus.length);
        expect(c.cantos).toEqual([c.nivel * ALTURA_NIVEL, c.nivel * ALTURA_NIVEL, c.nivel * ALTURA_NIVEL, c.nivel * ALTURA_NIVEL]);
        /* o nivel nunca desce para o leste */
        for (let x = x0 + 1; x <= ultima; x++) expect(ilha.cel(x, z)!.nivel, `${x},${z}`).toBeGreaterThanOrEqual(ilha.cel(x - 1, z)!.nivel);
      }
      /* a area andavel continua plana (o teste da grade confere o resto) */
      expect(ilha.cel(ilha.area.w - 1, 10)!.nivel).toBe(0);
    });
  }
});
