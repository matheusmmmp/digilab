/* A vista da ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA3; src/telas/pet/ilha/grade.ts, o modo `comAgua`):
     - a terra da vista e a terra do motor, celula a celula: nao ha terra na tela onde o pet nao pisa, nem agua onde ele pisa;
     - a moldura e so mar; a ilha e plana (sem penhasco, plato nem mata);
     - os lugares, os enfeites, os caminhos e a decoracao ficam em terra; o cais, na beira do mar;
     - as pontes da vista sao as do mapa do motor;
     - a ilha de hoje (o layout sem agua) nao muda: os testes dela (ilha_grade, ilha_planta, ilha_enfeites, ilha_lugares) seguem como estao. */
import { describe, expect, test } from "vitest";
import { AGUA_ILHA, CMU_MVP, CMU_MVP_AGUA, PONTE, celulasSecas } from "../motor/index.ts";
import { ILHA_AGUA, PLANTA_ILHA, PLANTA_ILHA_AGUA, PONTE_ILHA } from "../src/telas/pet/ilha/constantes.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { MODELOS } from "../src/telas/pet/ilha/modelos.ts";
import { listaDeFocos } from "../src/telas/pet/ilha/luzConta.ts";
import { caixasDaPonte, celulasDoCorrimao } from "../src/telas/pet/ilha/ponteConta.ts";
import { comprimento, naRota, rotaEmTerra, type Ponto } from "../src/telas/pet/ilha/rotaConta.ts";

const CM = CMU_MVP_AGUA, W = CM.celulas_x, H = CM.celulas_y, secas = celulasSecas(CM)!;
const seca = (x: number, z: number): boolean => x >= 0 && z >= 0 && x < W && z < H && secas[Math.floor(z) * W + Math.floor(x)];

describe("a grade da ilha com agua", () => {
  const ilha = ilhaDe(CM);

  test("mesma entrada, mesma ilha; a ilha de hoje nao tem o modo da agua", () => {
    const b = ilhaDe(CM);
    const tudo = (i: typeof ilha) => JSON.stringify([i.celulas, i.objetos, i.extras, i.enfeites, i.lugares, i.caminhos, [...i.escondidos], i.pontes]);
    expect(tudo(ilha)).toBe(tudo(b));
    /* o saco e a praca sao os mesmos nas duas plantas (lugares.ts le o saco da planta A) */
    expect([PLANTA_ILHA_AGUA.lugares.saco, PLANTA_ILHA_AGUA.praca]).toEqual([PLANTA_ILHA.lugares.saco, PLANTA_ILHA.praca]);
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
    /* ao norte da linha `sulDesde` a praia tem `praia` celulas; dali para o sul, `praiaSul` */
    const longe = (x: number, z: number, d: number) => { for (let dz = -d; dz <= d; dz++) for (let dx = -d; dx <= d; dx++) if (mar(x + dx, z + dz)) return false; return true; };
    let larga = 0;
    for (let z = 0; z < H; z++) for (let x = 0; x < W; x++) {
      const c = ilha.cel(x, z)!;
      if (c.tipo !== "areia") continue;
      if (z < ILHA_AGUA.sulDesde) expect(longe(x, z, ILHA_AGUA.praia), `${x},${z}`).toBe(false);
      else if (longe(x, z, ILHA_AGUA.praia)) larga++;
    }
    expect(larga).toBeGreaterThan(5);
  });

  test("as pontes da vista sao as do mapa do motor, pintadas como caminho", () => {
    const doMapa: [number, number][] = [];
    AGUA_ILHA.forEach((l, z) => [...l].forEach((ch, x) => { if (ch === PONTE) doMapa.push([x, z]); }));
    expect(ilha.pontes).toEqual(doMapa);
    expect(doMapa.length).toBe(8);
    for (const [x, z] of ilha.pontes) expect(ilha.cel(x, z)!.tipo).toBe("caminho");
    /* as duas pontes atravessam o rio de oeste a leste: a agua fica ao norte e ao sul, e o corrimao so nessas 8 beiras */
    const beiras = celulasDoCorrimao(ilha);
    expect(beiras.map(b => [b.x, b.z, b.dx, b.dz]).sort()).toEqual(
      [[42, 11, 0, -1], [43, 11, 0, -1], [42, 12, 0, 1], [43, 12, 0, 1], [43, 21, 0, -1], [44, 21, 0, -1], [43, 22, 0, 1], [44, 22, 0, 1]].sort());
  });

  test("as caixas da ponte: as tabuas atravessadas ao passo, sobrando so para a agua; o corrimao rente a agua; nada sobre a terra", () => {
    const caixas = caixasDaPonte(ilha), T = PONTE_ILHA.tabuado, C = PONTE_ILHA.corrimao;
    const naPonte = (x: number, z: number) => ilha.pontes.some(([px, pz]) => px === Math.floor(x) && pz === Math.floor(z));
    const tabuas = caixas.filter(c => c.peca === "tabua"), paus = caixas.filter(c => c.peca === "corrimao"), postes = caixas.filter(c => c.peca === "poste");
    expect([tabuas.length, paus.length, postes.length]).toEqual([8 * T.porCelula, 8, 12]);
    for (const c of caixas) {
      const [x0, y0, z0] = c.min, [x1, y1, z1] = c.max;
      expect(x1 > x0 && y1 > y0 && z1 > z0, JSON.stringify(c)).toBe(true);
      /* nenhuma caixa passa para a terra a oeste ou a leste; para o norte e o sul, so a sobra das tabuas sobre a agua */
      for (const [x, z] of [[x0 + 1e-6, z0 + 1e-6], [x1 - 1e-6, z0 + 1e-6], [x0 + 1e-6, z1 - 1e-6], [x1 - 1e-6, z1 - 1e-6]]) {
        const c0 = ilha.cel(Math.floor(x), Math.floor(z))!;
        expect(naPonte(x, z) || (c.peca === "tabua" && c0.tipo === "agua"), `${c.peca} em ${x},${z}`).toBe(true);
      }
      if (c.peca === "tabua") {
        /* quem atravessa anda em x: a tabua e estreita em x e comprida em z; baixa, porque o pet e a bola sao desenhados no chao */
        expect(x1 - x0).toBeLessThan(1 / T.porCelula);
        expect(z1 - z0).toBeGreaterThanOrEqual(1);
        expect(z1 - z0).toBeLessThanOrEqual(1 + T.sobra + 1e-9);
        expect(y1).toBeLessThanOrEqual(0.06);
        expect(y0).toBeGreaterThan(0);
      } else expect(y1).toBeCloseTo(T.altura + T.espessura + C.altura, 9);
    }
    /* a mesma tabua em duas celulas tem o mesmo tom */
    for (const a of tabuas) for (const b of tabuas) if (a.min[0] === b.min[0] && Math.abs(a.min[2] - b.min[2]) <= 1.2) expect(a.tom).toBe(b.tom);
    /* o corrimao fica a `recuo` da beira da agua, do lado de dentro da ponte */
    for (const c of paus) {
      const z = (c.min[2] + c.max[2]) / 2, borda = Math.round(z);
      expect(Math.abs(z - borda)).toBeCloseTo(C.recuo, 9);
      expect(ilha.cel(Math.floor(c.min[0]), z < borda ? borda : borda - 1)!.tipo).toBe("agua");
      expect(c.max[0] - c.min[0]).toBe(1);
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
    expect(ilha.cel(Math.floor(cais.x), Math.floor(cais.z))!.nivel).toBe(-1);                 // o cais da para o mar, nao para o rio
    expect(ilha.enfeites.map(e => e.nome).sort()).toEqual(["carro", "geladeira", "poste", "poste", "poste", "poste", "poste", "poste", "trilho"]);
    for (const e of ilha.enfeites) expect(seca(e.x, e.z), `${e.nome} em ${e.x},${e.z}`).toBe(true);
    expect(seca(...PLANTA_ILHA_AGUA.lugares.saco)).toBe(true);
    expect(seca(PLANTA_ILHA_AGUA.praca.x, PLANTA_ILHA_AGUA.praca.z)).toBe(true);
    ilha.objetos.forEach((o, i) => {
      expect(seca(o.x, o.z), `${o.modelo} em ${o.x},${o.z}`).toBe(true);
      /* nada alto que nao seja do motor (a regra 5 da ilha) */
      if (!o.doMotor && !ilha.escondidos.has(i)) expect(MODELOS[o.modelo].baixo, o.modelo).toBe(true);
    });
    for (const o of ilha.extras) {
      expect(seca(o.x, o.z), `${o.modelo} em ${o.x},${o.z}`).toBe(true);
      expect(MODELOS[o.modelo].baixo, o.modelo).toBe(true);
    }
    expect(ilha.extras.length).toBeGreaterThan(5);
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
    /* todos os caminhos da planta ficam em terra de ponta a ponta (o do cais para na praia) */
    ilha.caminhos.forEach((l, n) => {
      for (let k = 1; k < l.length; k++) for (let t = 0; t <= 100; t++) {
        const x = l[k - 1][0] + ((l[k][0] - l[k - 1][0]) * t) / 100, z = l[k - 1][1] + ((l[k][1] - l[k - 1][1]) * t) / 100;
        expect(seca(x, z), `caminho ${n} em ${x},${z}`).toBe(true);
      }
    });
    /* e nenhum foco de luz cai na agua */
    for (const [x, z] of listaDeFocos(ilha)) expect(seca(x, z), `foco em ${x},${z}`).toBe(true);
  });
});

describe("a rota do pet ate um lugar aberto (so vista; IA4)", () => {
  const ilha = ilhaDe(CM);
  test("sem agua no layout, a reta de sempre", () => {
    expect(rotaEmTerra(CMU_MVP, [4.5, 15.5], [48.5, 8.5])).toEqual([[4.5, 15.5], [48.5, 8.5]]);
  });

  test("na ilha com agua a rota fica em terra de ponta a ponta e passa por uma ponte para cruzar o rio", () => {
    const destinos: Ponto[] = [[ilha.lugares[1].x, ilha.lugares[1].z + 1.5], [PLANTA_ILHA_AGUA.lugares.saco[0] - 1.35, PLANTA_ILHA_AGUA.lugares.saco[1]], [ilha.lugares[0].x, ilha.lugares[0].z + 1.5]];
    for (const de of [[4.5, 15.5], [36.5, 16.5], [55.2, 20.7], [12.3, 26.1]] as Ponto[]) for (const para of destinos) {
      const rota = rotaEmTerra(CM, de, para);
      expect(rota[0]).toEqual(de);
      expect(rota.at(-1)).toEqual(para);
      let ponte = 0;
      for (let k = 0; k <= 400; k++) {
        const [x, z] = naRota(rota, k / 400);
        expect(seca(x, z), `de ${de} a ${para}, em ${x},${z}`).toBe(true);
        if (AGUA_ILHA[Math.floor(z)][Math.floor(x)] === PONTE) ponte++;
      }
      /* cruzar o rio (de um lado ao outro da coluna 43) so pela ponte */
      const cruza = (de[0] < 42) !== (para[0] < 42) && de[1] > 6;
      if (cruza) expect(ponte, `de ${de} a ${para}`).toBeGreaterThan(0);
      expect(comprimento(rota)).toBeGreaterThanOrEqual(Math.hypot(para[0] - de[0], para[1] - de[1]) - 1e-9);
      expect(naRota(rota, 0)).toEqual(de);
      expect(naRota(rota, 1)).toEqual(para);
    }
  });

  test("a ponta que cai na agua vale o centro da celula de terra mais perto", () => {
    const rota = rotaEmTerra(CM, [43.5, 8.5], [0.5, 0.5]);            // do rio ao mar
    for (const [x, z] of rota) expect(seca(x, z)).toBe(true);
    expect(rota[0]).not.toEqual([43.5, 8.5]);
    expect(rota[0].map(v => v % 1)).toEqual([0.5, 0.5]);
  });
});
