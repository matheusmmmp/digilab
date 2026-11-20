/* A ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG2): o espelho do tests/test_ilha_grande.py do Python.
     - o mundo de 128 x 60 celulas: o mapa do Python, as regioes dobradas, a arvore e o marco como celulas fechadas, os solidos;
     - o que o dono poe em cima da arvore ou do marco vai para a terra; a posicao dos eventos vale ate o tamanho do mapa de cada mundo;
     - o G-PAR do laco: o TS refaz o gabarito do Python (test/gabaritos/ilha_grande_python.json, experiments/exportar_gabarito_ilha_grande.py)
       decisao a decisao e bit a bit no Node, pelo laco gravado do MVP (test/laco_gravado.ts), com o controlador do contrato; e confere do
       lado do TS que nada ficou em celula fechada e que o pet pisou na ponte.
   Nenhum pet do jogo roda este mundo ainda (a IG4 liga). */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { AGUA_DOCE, AGUA_ILHA_GRANDE, AGUA_MAR, AGUA_POR_LAYOUT, ARVORE_FECHADA, CMU_GRANDE, CMU_MVP, CMU_MVP_AGUA, MARCO_FECHADO, PONTE, TERRA } from "../motor/constantes.ts";
import { CONFIG_CONTRATO_AGUA, bloqueioEm, grade } from "../motor/contrato.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { estadoNascimentoPy } from "../motor/motor_corpo.ts";
import { MAPA_PADRAO, Mundo, celulasSecas, eventoDeixarBola, eventoDeixarComida, regiaoDe, solidosDaAgua, tamanhoDoMapa } from "../motor/mundo.ts";
import { LacoGravado, cerebroDa, json, ler, type Rec, type Vida } from "./laco_gravado.ts";

const { texto, g: G } = ler("./gabaritos/ilha_grande_python.json");
const SHA = "1bd222b3c2f762b635e31eaaa1548e48e5a890c5ad40a971639ddc935a3d7ab3";
type VidaGrande = Vida & {
  conferido: { cruzou_pela_ponte: number; rolagens: number; posicoes_do_pet: number; tirados_da_agua: { comida: number; levar: number };
               tirados_da_arvore_e_do_marco: Record<"arvore" | "marco", { comida: number; levar: number }> };
};
const VIDAS = G.vidas as VidaGrande[];
const CM = CMU_GRANDE, NX = CM.celulas_x, NY = CM.celulas_y, SUB = CM.sub;
const mundo = (semente = 101): Mundo => new Mundo({ semente, cfg: CM, contrato: CONFIG_CONTRATO_AGUA });
const centro = (cx: number, cy: number): [number, number] => [cx * SUB + SUB / 2, cy * SUB + SUB / 2];
const NA_ARVORE = centro(30, 14), NO_MARCO = centro(31, 21);

describe("o mundo de 128 x 60", () => {
  test("o mapa e o do Python, com a arvore e o marco fechados e o mar em toda a borda", () => {
    expect(AGUA_ILHA_GRANDE).toEqual((G.config as unknown as { agua: string[] }).agua);
    expect([NX, NY, SUB]).toEqual([128, 60, 16]);
    expect(tamanhoDoMapa(CM)).toEqual([2048, 960]);
    expect(tamanhoDoMapa(CMU_MVP_AGUA)).toEqual(MAPA_PADRAO);
    expect(Object.keys(AGUA_POR_LAYOUT)).toEqual(["mvp_agua", "grande"]);
    expect(new Set(AGUA_ILHA_GRANDE.join(""))).toEqual(new Set([AGUA_MAR, AGUA_DOCE, TERRA, PONTE, ARVORE_FECHADA, MARCO_FECHADO]));
    expect(new Set(AGUA_ILHA_GRANDE[0] + AGUA_ILHA_GRANDE[NY - 1] + AGUA_ILHA_GRANDE.map(l => l[0] + l[NX - 1]).join(""))).toEqual(new Set([AGUA_MAR]));
    expect(AGUA_ILHA_GRANDE[14][30]).toBe(ARVORE_FECHADA);
    expect(AGUA_ILHA_GRANDE[21][31]).toBe(MARCO_FECHADO);
    /* mais de tres vezes a terra livre do mundo de hoje */
    const livres = (cm: typeof CM): number => celulasSecas(cm)!.filter(Boolean).length;
    expect(livres(CM)).toBeGreaterThan(3 * livres(CMU_MVP_AGUA));
  });

  test("as regioes sao as de sempre com as faixas dobradas; o ninho, o comedouro e a bola ficam em terra, nas regioes de hoje", () => {
    const L = CM.layout, hoje = CMU_MVP.layout;
    expect(L.regioes.map(([n, x0, x1]) => [n, x0, x1 + 1])).toEqual(hoje.regioes.map(([n, x0, x1]) => [n, 2 * x0, 2 * (x1 + 1)]));
    expect(L.arvores).toEqual([]);
    for (const nome of ["ninho", "comedouro", "bola_inicio"] as const) {
      const [cx, cy] = L[nome];
      expect(AGUA_ILHA_GRANDE[cy][cx], nome).toBe(TERRA);
      expect(regiaoDe(cx * SUB, CM), nome).toBe(regiaoDe(hoje[nome][0] * CMU_MVP.sub, CMU_MVP));
    }
    expect(json({ ...CM, layout: { ...CM.layout, nome: "x" } })).not.toEqual(json({ ...CMU_MVP, layout: { ...CMU_MVP.layout, nome: "x" } }));
  });

  test("os solidos cobrem o que e fechado e so isso, sao os do Python, e a grade do contrato e a das celulas livres", () => {
    const secas = celulasSecas(CM)!, solidos = solidosDaAgua(CM);
    expect(solidos.every(s => s.categoria === "obstaculo" && s.colide && !s.alto)).toBe(true);
    for (let cy = 0; cy < NY; cy++) for (let cx = 0; cx < NX; cx++) {
      const [x, y] = centro(cx, cy);
      const dentro = solidos.filter(s => x >= s.x0 && x < s.x1 && y >= s.y0 && y < s.y1).length;
      expect(dentro, `${cx}, ${cy}`).toBe(secas[cy * NX + cx] ? 0 : 1);
      expect(secas[cy * NX + cx], `${cx}, ${cy}`).toBe(AGUA_ILHA_GRANDE[cy][cx] === TERRA || AGUA_ILHA_GRANDE[cy][cx] === PONTE);
    }
    expect([...grade(NX, NY, SUB, CONFIG_CONTRATO_AGUA.r_pet, solidos)]).toEqual([...secas]);
    expect(solidos.map(s => [s.x0, s.y0, s.x1, s.y1])).toEqual((G.config as unknown as { solidos_da_agua: number[][] }).solidos_da_agua);
  });

  test("o que o dono poe em cima da arvore ou do marco vai para a terra mais perto", () => {
    const m = mundo(), r = CONFIG_CONTRATO_AGUA.r_pet, solidos = solidosDaAgua(CM);
    expect(m.pet).toEqual(centro(20, 30));
    for (const ponto of [NA_ARVORE, NO_MARCO]) {
      expect(m.seca(...ponto)).toBe(false);
      m.deixarComida(10, "racao", ...ponto);
      const c = [...m.comidas.values()].at(-1)!;
      expect([c.x, c.y]).not.toEqual(ponto);
      expect(m.seca(c.x, c.y)).toBe(true);
      m.deixarBola(20, ...ponto);
      expect(m.seca(...m.bolaEm(20))).toBe(true);
      m.levarPet(30, ...ponto);
      expect(bloqueioEm(m.pet[0], m.pet[1], r, solidos)).toBeNull();
    }
  });

  test("a posicao do evento vale ate o tamanho do mapa de cada mundo", () => {
    const longe: [number, number] = [1800, 700];                     /* dentro da ilha grande, fora do mapa de 64 x 30 */
    const m = mundo();
    m.deixarComida(10, "racao", ...longe);
    m.deixarBola(20, ...longe);
    expect(() => m.deixarComida(30, "racao", 2048, 10)).toThrow(/fora do mapa/);
    expect(() => m.deixarBola(30, 10, 960)).toThrow(/fora do mapa/);
    const hoje = new Mundo({ semente: 101, cfg: CMU_MVP_AGUA, contrato: CONFIG_CONTRATO_AGUA }), antes = hoje.comidas.size;
    expect(() => hoje.deixarComida(10, "racao", ...longe)).toThrow(/fora do mapa/);
    expect(() => hoje.deixarBola(10, ...longe)).toThrow(/fora do mapa/);
    expect(hoje.comidas.size).toBe(antes);
    /* quem nao passa o mapa continua no de 64 x 30 */
    expect(() => eventoDeixarComida(0, "racao", ...longe)).toThrow(/fora do mapa/);
    expect(() => eventoDeixarBola(0, ...longe)).toThrow(/fora do mapa/);
    expect(eventoDeixarComida(0, "racao", ...longe, tamanhoDoMapa(CM)).valor).toBe("racao|1800|700");
    /* so os dois tamanhos existem, como no Python */
    for (const outro of [{ celulas_x: 96, celulas_y: 48 }, { sub: 32 }, { celulas_x: 128 }])
      expect(() => new Mundo({ semente: 101, cfg: { ...CMU_MVP, ...outro } }), JSON.stringify(outro)).toThrow(/64 x 30/);
  });
});

describe("G-PAR da ilha grande: o laco do TS = o Python, decisao a decisao", () => {
  test("o gabarito: duas sementes na ilha grande, com a travessia pela ponte e a racao e o pet tirados da arvore e do marco", () => {
    expect(createHash("sha256").update(texto).digest("hex")).toBe(SHA);
    expect(json(CM)).toEqual(G.config.mundo);
    expect(json(CONFIG_CONTRATO_AGUA)).toEqual((G.config as unknown as { contrato: Rec }).contrato);
    expect(VIDAS.map(v => v.semente)).toEqual([202, 505]);
    for (const v of VIDAS) {
      expect(v.conferido.cruzou_pela_ponte).toBeGreaterThan(0);
      for (const onde of ["arvore", "marco"] as const) for (const k of ["comida", "levar"] as const)
        expect(v.conferido.tirados_da_arvore_e_do_marco[onde][k], `${onde} ${k}`).toBeGreaterThan(0);
    }
  });

  for (const vida of VIDAS) {
    test(`${vida.nome}: cada decisao, o log, o mundo e o corpo no fim; nada em celula fechada`, () => {
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
      /* as decisoes e os proximos sorteios de cada fluxo de acaso (como no test/mvp_mundo.test.ts): nenhum fluxo andou a mais */
      expect(m.mundo.decisoes.length).toBe(vida.decisoes);
      for (const [fluxo, rg] of [["arvores", m.mundo.rngArvores], ["bola", m.mundo.rngBola], ["sujeira", m.mundo.rngSujeira], ["alvo", m.mundo.rngAlvo]] as const) {
        const prox = { random: [rg.random(), rg.random(), rg.random()], randrange16: [rg.randrange(1 << 16), rg.randrange(1 << 16), rg.randrange(1 << 16)] };
        expect(prox, `proximos de ${fluxo}`).toEqual(vida.proximos[fluxo]);
      }

      /* os gates do lado do TS: nenhuma comida e nenhum ponto do pet em celula fechada, e o pet pisou na ponte */
      const w = m.mundo, r = CONFIG_CONTRATO_AGUA.r_pet, solidos = solidosDaAgua(CM);
      for (const cm of w.comidas.values()) expect(w.seca(cm.x, cm.y)).toBe(true);
      let pontos = 0, naPonte = 0;
      for (const d of w.contratoDecisoes) for (const [x, y] of d.trajetoria ?? []) {
        pontos++;
        if (AGUA_ILHA_GRANDE[Math.floor(y / SUB)][Math.floor(x / SUB)] === PONTE) naPonte++;
        if (bloqueioEm(x, y, r, solidos) !== null) throw new Error(`o pet em celula fechada: (${x}, ${y})`);
      }
      for (const l of w.levadas) { pontos++; expect(bloqueioEm(l.para[0], l.para[1], r, solidos)).toBeNull(); }
      expect(pontos).toBe(vida.conferido.posicoes_do_pet);
      expect(naPonte).toBeGreaterThan(0);
      expect(w.rolagens.length).toBe(vida.conferido.rolagens);
      for (const rol of w.rolagens) { expect(w.seca(...rol.de)).toBe(true); expect(w.seca(...rol.para)).toBe(true); }
      /* o custo do controlador no mapa de 7 680 celulas: a vida de 2 dias inteira, com o corpo e o cerebro, em milissegundos */
      console.log(`${vida.nome}: ${vida.traco.length} passos do traco em ${ms.toFixed(0)} ms`);
    });
  }
});
