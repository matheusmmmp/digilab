/* A vista da ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA3; src/telas/pet/ilha/grade.ts, o modo `comAgua`):
     - a terra da vista e a terra do motor, celula a celula: nao ha terra na tela onde o pet nao pisa, nem agua onde ele pisa;
     - a moldura e so mar; a ilha e plana (sem penhasco, plato nem mata);
     - os lugares, os enfeites, os caminhos e a decoracao ficam em terra; o cais, na beira do mar;
     - as pontes da vista sao as do mapa do motor;
     - a ilha de hoje (o layout sem agua) nao muda: os testes dela (ilha_grade, ilha_planta, ilha_enfeites, ilha_lugares) seguem como estao. */
import { describe, expect, test } from "vitest";
import { AGUA_ILHA, CMU_MVP, CMU_MVP_AGUA, PONTE, celulasSecas } from "../motor/index.ts";
import { ILHA_AGUA, PLANTA_ILHA, PLANTA_ILHA_AGUA } from "../src/telas/pet/ilha/constantes.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { MODELOS } from "../src/telas/pet/ilha/modelos.ts";
import { celulasDoCorrimao } from "../src/telas/pet/ilha/ponteConta.ts";

const CM = CMU_MVP_AGUA, W = CM.celulas_x, H = CM.celulas_y, secas = celulasSecas(CM)!;
const seca = (x: number, z: number): boolean => x >= 0 && z >= 0 && x < W && z < H && secas[Math.floor(z) * W + Math.floor(x)];

describe("a grade da ilha com agua", () => {
  const ilha = ilhaDe(CM);

  test("mesma entrada, mesma ilha; a ilha de hoje nao tem o modo da agua", () => {
    const b = ilhaDe(CM);
    expect(JSON.stringify([ilha.celulas, ilha.objetos, ilha.extras, ilha.enfeites, ilha.lugares])).toBe(JSON.stringify([b.celulas, b.objetos, b.extras, b.enfeites, b.lugares]));
    const hoje = ilhaDe(CMU_MVP);
    expect([ilha.comAgua, hoje.comAgua]).toEqual([true, false]);
    expect(hoje.planta).toBe(PLANTA_ILHA);
    expect(ilha.planta).toBe(PLANTA_ILHA_AGUA);
    expect(hoje.pontes).toEqual([]);
  });

  test("a terra da vista e a terra do motor, celula a celula; a moldura e so mar", () => {
    const M = ILHA_AGUA.moldura;
    expect([ilha.x0, ilha.z0, ilha.larg, ilha.prof]).toEqual([-M, -M, W + 2 * M, H + 2 * M]);
    let terra = 0;
    for (let z = ilha.z0; z < ilha.z0 + ilha.prof; z++) for (let x = ilha.x0; x < ilha.x0 + ilha.larg; x++) {
      const c = ilha.cel(x, z)!;
      expect(c.tipo !== "agua", `${x},${z}`).toBe(seca(x, z));
      if (c.tipo === "agua") continue;
      terra++;
      expect([c.nivel, ...c.cantos], `${x},${z}`).toEqual([0, 0, 0, 0, 0]);
    }
    expect(terra).toBe(secas.filter(Boolean).length);
    /* o mar e fundo (nivel -1), a agua doce fica no nivel do chao */
    expect(ilha.cel(0, 0)!.nivel).toBe(-1);
    expect([ilha.cel(43, 8)!.tipo, ilha.cel(43, 8)!.nivel]).toEqual(["agua", 0]);
  });

  test("a praia da a volta na ilha: toda terra rente ao mar e areia, e a areia nunca fica longe do mar", () => {
    const mar = (x: number, z: number) => ilha.cel(x, z)?.nivel === -1 || !ilha.cel(x, z);
    let areia = 0;
    for (let z = 0; z < H; z++) for (let x = 0; x < W; x++) {
      const c = ilha.cel(x, z)!;
      if (c.tipo === "agua" || AGUA_ILHA[z][x] === PONTE) continue;
      const rente = [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dz]) => mar(x + dx, z + dz));
      if (rente) expect(c.tipo, `${x},${z}`).toBe("areia");
      if (c.tipo !== "areia") continue;
      areia++;
      let perto = false;
      for (let dz = -ILHA_AGUA.praiaSul; dz <= ILHA_AGUA.praiaSul; dz++) for (let dx = -ILHA_AGUA.praiaSul; dx <= ILHA_AGUA.praiaSul; dx++) if (mar(x + dx, z + dz)) perto = true;
      expect(perto, `${x},${z}`).toBe(true);
    }
    expect(areia).toBeGreaterThan(100);
  });

  test("as pontes da vista sao as do mapa do motor, pintadas como caminho", () => {
    const doMapa: [number, number][] = [];
    AGUA_ILHA.forEach((l, z) => [...l].forEach((ch, x) => { if (ch === PONTE) doMapa.push([x, z]); }));
    expect(ilha.pontes).toEqual(doMapa);
    expect(doMapa.length).toBe(8);
    for (const [x, z] of ilha.pontes) expect(ilha.cel(x, z)!.tipo).toBe("caminho");
    /* o corrimao so nas beiras que dao para a agua: cada celula de ponte tem agua de um lado pelo menos em uma das pontes */
    const beiras = celulasDoCorrimao(ilha);
    expect(beiras.length).toBeGreaterThanOrEqual(6);
    for (const b of beiras) {
      expect(ilha.pontes.some(([x, z]) => x === b.x && z === b.z)).toBe(true);
      expect(ilha.cel(b.x + b.dx, b.z + b.dz)!.tipo).toBe("agua");
    }
  });

  test("os lugares, os enfeites e a decoracao ficam em terra; o cais, na beira do mar", () => {
    expect(ilha.lugares.map(l => l.nome)).toEqual(["portao", "barraca", "cais"]);
    for (const l of ilha.lugares) if (l.nome !== "cais") {
      expect(seca(l.x, l.z), l.nome).toBe(true);
      expect(l.y).toBe(0);
    }
    const cais = ilha.lugares[2];
    expect([seca(cais.x, cais.z - 1), seca(cais.x, cais.z)]).toEqual([true, false]);
    expect(ilha.cel(Math.floor(cais.x), Math.floor(cais.z) - 1)!.tipo).toBe("areia");
    expect(ilha.enfeites.map(e => e.nome).sort()).toEqual(["carro", "geladeira", "poste", "poste", "poste", "poste", "poste", "poste", "trilho"]);
    for (const e of ilha.enfeites) expect(seca(e.x, e.z), `${e.nome} em ${e.x},${e.z}`).toBe(true);
    expect(seca(...PLANTA_ILHA_AGUA.lugares.saco)).toBe(true);
    expect(seca(PLANTA_ILHA_AGUA.praca.x, PLANTA_ILHA_AGUA.praca.z)).toBe(true);
    ilha.objetos.forEach((o, i) => {
      expect(seca(o.x, o.z), `${o.modelo} em ${o.x},${o.z}`).toBe(true);
      /* nada alto que nao seja do motor (a regra 5 da ilha) */
      if (!o.doMotor && !ilha.escondidos.has(i)) expect(MODELOS[o.modelo].baixo, o.modelo).toBe(true);
    });
    for (const o of ilha.extras) expect(seca(o.x, o.z), `${o.modelo} em ${o.x},${o.z}`).toBe(true);
    expect(ilha.objetos.length).toBeGreaterThan(100);
  });

  test("os caminhos pintados ficam em terra, e o da barraca passa pela ponte do norte", () => {
    let caminho = 0;
    for (let z = 0; z < H; z++) for (let x = 0; x < W; x++) if (ilha.cel(x, z)!.tipo === "caminho") { caminho++; expect(seca(x, z)).toBe(true); }
    expect(caminho).toBeGreaterThan(80);
    const barraca = ilha.caminhos[2], naPonte = (x: number, z: number) => AGUA_ILHA[Math.floor(z)]?.[Math.floor(x)] === PONTE;
    let molhou = 0, ponte = 0;
    for (let k = 1; k < barraca.length; k++) for (let t = 0; t <= 100; t++) {
      const x = barraca[k - 1][0] + ((barraca[k][0] - barraca[k - 1][0]) * t) / 100, z = barraca[k - 1][1] + ((barraca[k][1] - barraca[k - 1][1]) * t) / 100;
      if (!seca(x, z)) molhou++;
      if (naPonte(x, z)) ponte++;
    }
    expect([molhou, ponte > 0]).toEqual([0, true]);
    /* todos os caminhos da planta ficam em terra de ponta a ponta (o do cais para na areia) */
    ilha.caminhos.forEach((l, n) => {
      for (let k = 1; k < l.length; k++) for (let t = 0; t <= 100; t++) {
        const x = l[k - 1][0] + ((l[k][0] - l[k - 1][0]) * t) / 100, z = l[k - 1][1] + ((l[k][1] - l[k - 1][1]) * t) / 100;
        if (z < H - 2) expect(seca(x, z), `caminho ${n} em ${x},${z}`).toBe(true);
      }
    });
  });
});
