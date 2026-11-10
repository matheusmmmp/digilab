/* A ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA2): o espelho do tests/test_ilha_agua.py do Python.
     - a agua do layout (celulasSecas, solidosDaAgua), a tabela pelo nome e o que falha alto;
     - nada cai na agua: a comida e a bola postas na agua, a bola que rola (tick a tick), o pet solto na agua;
     - o G-PAR do laco: o TS refaz o gabarito do Python (test/gabaritos/ilha_agua_python.json, experiments/exportar_gabarito_ilha_agua.py)
       decisao a decisao e bit a bit no Node, pelo laco gravado do MVP (test/laco_gravado.ts), no mundo do produto com a agua, com o
       controlador do contrato; e confere do lado do TS que nada ficou na agua e que o pet cruzou o rio pisando na ponte.
   A chave fica desligada no jogo (a IA4 liga): os pets de hoje rodam o CMU_MVP, sem agua. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { AGUA_DOCE, AGUA_ILHA, AGUA_MAR, AGUA_POR_LAYOUT, CMU_MVP, CMU_MVP_AGUA, PONTE, TERRA } from "../motor/constantes.ts";
import { CONFIG_CONTRATO, CONFIG_CONTRATO_AGUA, bloqueioEm, grade } from "../motor/contrato.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { estadoNascimentoPy } from "../motor/motor_corpo.ts";
import { Mundo, celulasSecas, deslocar, distancia, divArred, solidosDaAgua } from "../motor/mundo.ts";
import { LacoGravado, cerebroDa, json, ler, type Rec, type Vida } from "./laco_gravado.ts";

const { texto, g: G } = ler("./gabaritos/ilha_agua_python.json");
const SHA = "3e19d644de1009dfad2db72a8c4b45415c66131a45539fcc66172bfc36fe1f5f";
interface Pedido { tick: number; pedido: [number, number]; ficou: [number, number] }
type VidaAgua = Vida & {
  pedidos: { comida: (Pedido & { id: number })[]; levar: Pedido[]; ponte: { tick: number; pet: [number, number]; racao: [number, number] }[];
             dormindo_em: number[] };
  conferido: { cruzou_pela_ponte: number; rolagens: number; rolagens_paradas_na_margem: number; posicoes_do_pet: number;
               tirados_da_agua: { comida: number; levar: number } };
};
const VIDAS = G.vidas as VidaAgua[];
const CM = CMU_MVP_AGUA, NX = CM.celulas_x, NY = CM.celulas_y, SUB = CM.sub;
const mundo = (semente = 101): Mundo => new Mundo({ semente, cfg: CM, contrato: CONFIG_CONTRATO_AGUA });

describe("a agua do layout", () => {
  test("o mapa e o do Python, pelo nome do layout; o mundo de hoje nao tem agua", () => {
    expect(AGUA_ILHA).toEqual((G.config as unknown as { agua: string[] }).agua);
    expect(Object.keys(AGUA_POR_LAYOUT)).toEqual(["mvp_agua"]);
    expect(celulasSecas(CMU_MVP)).toBeNull();
    expect(solidosDaAgua(CMU_MVP)).toEqual([]);
    expect(json({ ...CM, layout: { ...CM.layout, nome: "mvp" } })).toEqual(json(CMU_MVP));
    const m = new Mundo({ semente: 101, cfg: CMU_MVP });
    expect(m.secas).toBeNull();
    expect([m.seca(5, 5), m.emTerra(5, 5), m.ateAMargem(0, 0, 900, 400), m.rolagemSeca(0, 0, 900, 400)]).toEqual([true, [5, 5], [900, 400], [900, 400]]);
    expect(new Set(AGUA_ILHA.join(""))).toEqual(new Set([AGUA_MAR, AGUA_DOCE, TERRA, PONTE]));
    expect(new Set(AGUA_ILHA[0] + AGUA_ILHA[NY - 1] + AGUA_ILHA.map(l => l[0] + l[NX - 1]).join(""))).toEqual(new Set([AGUA_MAR]));
  });

  test("os solidos cobrem a agua e so a agua, e a grade do contrato e a das celulas secas", () => {
    const secas = celulasSecas(CM)!, solidos = solidosDaAgua(CM);
    expect(solidos.every(s => s.categoria === "obstaculo" && s.colide && !s.alto)).toBe(true);
    let area = 0;
    for (const s of solidos) area += (s.x1 - s.x0) * (s.y1 - s.y0);
    expect(area).toBe((NX * NY - secas.filter(Boolean).length) * SUB * SUB);
    for (let cy = 0; cy < NY; cy++) for (let cx = 0; cx < NX; cx++) {
      const x = cx * SUB + SUB / 2, y = cy * SUB + SUB / 2;
      const dentro = solidos.filter(s => x >= s.x0 && x < s.x1 && y >= s.y0 && y < s.y1).length;
      expect(dentro, `${cx}, ${cy}`).toBe(secas[cy * NX + cx] ? 0 : 1);
    }
    expect([...grade(NX, NY, SUB, CONFIG_CONTRATO_AGUA.r_pet, solidos)]).toEqual([...secas]);
  });

  test("a agua exige o controlador do contrato", () => {
    expect(() => new Mundo({ semente: 101, cfg: CM })).toThrow(/controlador/);
    expect(() => new Mundo({ semente: 101, cfg: CM, contrato: { ...CONFIG_CONTRATO, sensores: true } })).toThrow(/controlador/);
    expect(mundo().pet).toEqual([4 * SUB + SUB / 2, 15 * SUB + SUB / 2]);
  });
});

describe("nada cai na agua", () => {
  test("a comida e a bola postas na agua vao para a terra mais perto; fora do mapa continua falhando alto", () => {
    const m = mundo();
    expect(m.seca(670, 250)).toBe(false);
    const [x, y] = m.emTerra(670, 250);
    expect([m.seca(x, y), x % SUB, y % SUB]).toEqual([true, SUB / 2, SUB / 2]);
    expect(m.emTerra(300, 240)).toEqual([300, 240]);
    m.deixarComida(10, "racao", 670, 250);
    const c = [...m.comidas.values()].at(-1)!;
    expect([c.x, c.y]).toEqual([x, y]);
    m.deixarBola(20, 205, 368);
    expect(m.seca(...m.bolaEm(20))).toBe(true);
    expect(m.bolaEm(20)).toEqual(m.emTerra(205, 368));
    expect(() => m.deixarComida(30, "racao", -1, 5)).toThrow();
  });

  test("a bola para na margem e nao entra na agua no meio da rolagem", () => {
    const m = mundo();
    expect(m.ateAMargem(560, 250, 600, 250)).toEqual([600, 250]);
    expect(m.ateAMargem(560, 250, 900, 250)).toEqual([41 * SUB - 1, 250]);
    /* os casos em que so o ateAMargem deixava a bola entrar 1 subunidade na agua (a conta do bolaEm arredonda pela distancia) */
    for (const [x, y] of [[601, 76], [867, 114], [86, 136], [291, 50], [662, 153]]) {
      let encurtou = 0;
      for (let d = 0; d < 16; d++) for (let c = 1; c <= 24; c++) {
        const alvo = deslocar(x, y, d, c * SUB, CM), para = m.rolagemSeca(x, y, ...alvo), margem = m.ateAMargem(x, y, ...alvo);
        /* todo ponto por onde a bola passa, tick a tick (a conta do bolaEm) */
        const dist = distancia(para[0] - x, para[1] - y);
        for (let j = 1; j < Math.ceil(dist / CM.atrito); j++)
          expect(m.seca(x + divArred((para[0] - x) * CM.atrito * j, dist), y + divArred((para[1] - y) * CM.atrito * j, dist)), `${x}, ${y}, ${d}, ${c}, ${j}`).toBe(true);
        if (para[0] !== margem[0] || para[1] !== margem[1]) encurtou++;
        expect(m.seca(...para), `${x}, ${y}, ${d}, ${c}`).toBe(true);
      }
      expect(encurtou, `${x}, ${y}`).toBeGreaterThan(0);
    }
    /* as rolagens de verdade ficam em terra, tick a tick */
    for (const s of [101, 202, 303]) {
      const w = mundo(s);
      w.deixarBola(0, 640, 250);
      for (let t = 1; t < 60; t++) {
        w.rolarBola(t * 100);
        for (let k = 0; k < 100; k++) expect(w.seca(...w.bolaEm(t * 100 + k)), `${s}, ${t}, ${k}`).toBe(true);
      }
    }
  });

  test("o pet solto na agua, ou rente a ela, cai em terra sem invadir a margem", () => {
    const m = mundo(), r = CONFIG_CONTRATO_AGUA.r_pet, solidos = solidosDaAgua(CM);
    for (const [x, y] of [[690, 300], [5, 5], [-40, 120], [1500, 50], [210, 372], [670, 250], [300, 200]]) {
      m.levarPet(10, x, y);
      expect(bloqueioEm(m.pet[0], m.pet[1], r, solidos), `${x}, ${y}`).toBeNull();
    }
    expect(m.pet).toEqual([300, 200]);
    expect([m.seca(653, 250), m.seca(656, 250)]).toEqual([true, false]);
    m.levarPet(20, 653, 250);
    expect(m.pet).toEqual([Math.floor(653 / SUB) * SUB + SUB / 2, Math.floor(250 / SUB) * SUB + SUB / 2]);
  });
});

describe("G-PAR da agua: o laco do TS = o Python, decisao a decisao", () => {
  test("o gabarito: duas sementes no mundo do produto com a agua, com a travessia pela ponte e a bola parada na margem", () => {
    expect(createHash("sha256").update(texto).digest("hex")).toBe(SHA);
    expect(json(CM)).toEqual(G.config.mundo);
    expect(json(CONFIG_CONTRATO_AGUA)).toEqual((G.config as unknown as { contrato: Rec }).contrato);
    expect(VIDAS.map(v => v.semente)).toEqual([202, 505]);
    for (const v of VIDAS) {
      expect(v.conferido.cruzou_pela_ponte).toBeGreaterThan(0);
      expect(v.conferido.rolagens_paradas_na_margem).toBeGreaterThan(0);
      expect(v.conferido.tirados_da_agua.comida).toBeGreaterThan(0);
      expect(v.conferido.tirados_da_agua.levar).toBeGreaterThan(0);
    }
  });

  for (const vida of VIDAS) {
    test(`${vida.nome}: cada decisao, o log, o mundo e o corpo no fim; nada na agua`, () => {
      const c = cerebroDa(vida);
      const m = new LacoGravado(c.politica, vida.semente, CCO_CORPO_V11, estadoNascimentoPy(0),
                                { regra: c.regra, paridade: true, cfgMundo: CM, decidirNaComida: true, bolaNoGolpe: true,
                                  contrato: CONFIG_CONTRATO_AGUA });
      const t0 = performance.now();
      for (const e of vida.log) m.aplicarEvento(e);
      const ms = performance.now() - t0;
      expect(m.traco.length).toBe(vida.traco.length);
      for (let i = 0; i < vida.traco.length; i++) {
        const esperado = vida.traco[i] as Rec, obtido = m.traco[i];
        if (JSON.stringify(obtido) === JSON.stringify(esperado)) continue;
        for (const k of Object.keys(esperado)) expect(obtido[k], `traco[${i}] (${esperado.op} no tick ${esperado.tick}): ${k}`).toEqual(esperado[k]);
      }
      expect(m.log).toEqual(vida.log);
      expect(json(m.mundo.resumo())).toEqual(vida.resumo);
      expect({ q: { ...m.corpo.q }, receptores: m.corpo.receptores() }).toEqual(vida.corpo_fim);
      const e = m.estado;
      expect({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira, tick: e.tick }).toEqual(vida.estado_fim);

      /* os gates do lado do TS: nenhuma comida, nenhum ponto do pet e nenhuma rolagem na agua */
      const w = m.mundo, r = CONFIG_CONTRATO_AGUA.r_pet, solidos = solidosDaAgua(CM);
      for (const p of vida.pedidos.comida) expect(w.seca(...p.ficou), `comida ${p.id}`).toBe(true);
      for (const cm of w.comidas.values()) expect(w.seca(cm.x, cm.y)).toBe(true);
      let pontos = 0, naPonte = 0;
      for (const d of w.contratoDecisoes) for (const [x, y] of d.trajetoria ?? []) {
        pontos++;
        if (AGUA_ILHA[Math.floor(y / SUB)][Math.floor(x / SUB)] === PONTE) naPonte++;
        if (bloqueioEm(x, y, r, solidos) !== null) throw new Error(`o pet na agua: (${x}, ${y})`);
      }
      for (const l of w.levadas) { pontos++; expect(bloqueioEm(l.para[0], l.para[1], r, solidos)).toBeNull(); }
      expect(pontos).toBe(vida.conferido.posicoes_do_pet + vida.pedidos.ponte.length);
      expect(naPonte).toBeGreaterThan(0);
      expect(w.rolagens.length).toBe(vida.conferido.rolagens);
      for (const rol of w.rolagens) { expect(w.seca(...rol.de)).toBe(true); expect(w.seca(...rol.para)).toBe(true); }
      /* o custo do controlador (o A* a cada decisao com alvo): a vida de 2 dias inteira, com o corpo e o cerebro, em milissegundos */
      console.log(`${vida.nome}: ${vida.traco.length} passos do traco em ${ms.toFixed(0)} ms`);
    });
  }
});
