// O mapa do scan do DigiBrain (D1 da UX_TELA_PET; src/componentes/ScanDigiBrain.tsx). Sem DOM (vitest em node): renderToStaticMarkup.
// Cobre: cada ponto e um no do motor e cada fio uma aresta de Motor.digibrain().mapa (as contagens que o e2e le), o destaque da decisao, o
// pulso so quando pedido (e um por aresta acesa), a falha alta (no fora do mapa, mapa e decisao de passos diferentes), a 390 e a 1920, e o
// tempo de montar o SVG com os ~80 fios (impresso, nao assertado: a maquina muda).
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test } from "vitest";
import { Motor } from "../motor/index.ts";
import { GIRO_CICLO_S, GIRO_GRAUS, MapaScan, PULSO_MS, VARREDURA_MS, cobrirCena } from "../src/componentes/ScanDigiBrain.tsx";
import { CENA } from "../src/telas/pet/cenaEstado.ts";

/* o pet v11 do e2e do DigiBrain (e2e/jogo.spec.ts) */
const LOG: [number, string, unknown][] = [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]];
const m = Motor.reproduzir(4242, LOG as never, 13), db = m.digibrain()!;
const montar = (movel: boolean, movendo: boolean, mapa = db.mapa, decisao = db.decisao): string =>
  renderToStaticMarkup(h(MapaScan, { mapa, decisao, movel, movendo }));
const contar = (s: string, re: RegExp): number => (s.match(re) ?? []).length;

describe("o mapa do scan: cada ponto e cada fio vem do motor", () => {
  test("o pet do e2e tem decisao, fios e arestas acesas", () => {
    expect(db.decisao).not.toBeNull();
    expect(db.mapa.acesas).not.toBeNull();
    expect(db.mapa.arestas.length).toBeGreaterThan(40);
  });
  for (const movel of [false, true]) {
    test(`as contagens do e2e (${movel ? "390" : "1920"} px)`, () => {
      const s = montar(movel, false), ac = db.mapa.acesas!, d = db.decisao!;
      expect(s).toContain(`data-n="${ac.n}"`);
      const pesos = s.match(/<g class="mp-pesos[^"]*">(.*?)<\/g>/)![1]!, acesas = s.match(/<g class="mp-acesas">(.*?)<\/g>/)![1]!;
      expect(contar(pesos, /<path /g)).toBe(db.mapa.arestas.length);
      expect(contar(acesas, /<path /g)).toBe(ac.arestas.length);
      expect(contar(s, /class="mp-no[^"]*mp-lit[^"]*" data-regra=/g)).toBe(1);
      expect(s).toContain(`data-regra="${ac.regra}"`);
      expect(contar(s, /class="mp-no[^"]*mp-esc[^"]*" data-acao="/g)).toBe(1);
      expect(contar(s, /class="mp-no[^"]*mp-cand/g)).toBe(d.chances.length);
      expect(contar(s, /class="mp-pct"/g)).toBe(d.chances.length);
      expect(contar(s, /class="mp-no[^"]*mp-lit[^"]*" data-entrada=/g)).toBe(d.percepcao.length);
      expect(contar(s, /class="mp-reg [^"]*mp-dest"/g)).toBe(1);
      expect(s).toContain(`class="mp-reg mp-reg--${ac.lobo_decisivo} mp-dest" data-lobo="${ac.lobo_decisivo}"`);
      /* um no por entrada, regra e acao */
      expect(contar(s, /data-entrada=/g)).toBe(10 + db.mapa.receptores.length);
      expect(contar(s, /data-regra=/g)).toBe(7);
      expect(contar(s, /data-acao=/g)).toBe(7);
      expect(s).toContain('role="img"');
      expect(s).toContain("Mapa dos pesos do pet");
    });
  }
  test("o pulso so com `movendo`, um por aresta acesa, e fora de .mp-pesos e .mp-acesas", () => {
    const sem = montar(false, false), com = montar(false, true), ac = db.mapa.acesas!;
    expect(sem).not.toContain("mp-pulso");
    expect(com).toContain("mp-pulso");
    expect(contar(com.match(/<g class="mp-pulso"[^>]*>(.*?)<\/g>/)![1]!, /<path /g)).toBe(ac.arestas.length);
    expect(contar(com.match(/<g class="mp-acesas">(.*?)<\/g>/)![1]!, /<path /g)).toBe(ac.arestas.length);
    expect(contar(com.match(/<g class="mp-pesos[^"]*">(.*?)<\/g>/)![1]!, /<path /g)).toBe(db.mapa.arestas.length);
  });
  test("sem decisao: nada aceso, sem pulso, sem destaque", () => {
    const s = montar(false, true, { ...db.mapa, acesas: null }, null);
    expect(s).toContain('data-n=""');
    expect(s).toContain("Ainda sem decisão");
    expect(s).not.toContain("mp-acesas");
    expect(s).not.toContain("mp-pulso");
    expect(s).not.toContain("mp-lit");
    expect(s).not.toContain("mp-dest");
  });
});

describe("o mapa do scan falha alto", () => {
  test("uma entrada fora do mapa", () => {
    const mapa = { ...db.mapa, arestas: [{ ...db.mapa.arestas[0]!, entrada: "inventada" }, ...db.mapa.arestas.slice(1)] };
    expect(() => montar(false, false, mapa)).toThrow(/entrada fora do mapa: inventada/);
  });
  test("o mapa e a leitura de decisoes diferentes", () => {
    expect(() => montar(false, false, db.mapa, { ...db.decisao!, n: db.decisao!.n + 1 })).toThrow(/decisoes diferentes/);
  });
  test("acesas sem decisao", () => {
    expect(() => montar(false, false, db.mapa, null)).toThrow(/fora de par/);
  });
});

describe("os numeros do movimento sao os PROPOSTOS da D1-2", () => {
  test("varredura 1,2 s, pulso 0,8 s, giro de 8 graus num ciclo de 40 s", () => {
    expect([VARREDURA_MS, PULSO_MS, GIRO_GRAUS, GIRO_CICLO_S]).toEqual([1200, 800, 8, 40]);
  });
});

describe("o custo de montar o SVG", () => {
  test("com ~80 fios (mediana de 30 montagens, impressa)", () => {
    /* uma vida mais longa do mesmo save (como o dados_digibrain.mts da prancha) ate o mapa ter 70 fios ou mais */
    const log = [...LOG]; let t0 = 900, grande = db;
    for (let k = 0; k < 400 && grande.mapa.arestas.length < 70; k++) {
      if (k % 5 === 0) log.push([t0, "d", "acariciar"]);
      log.push([t0, "t", 60]); t0 += 60;
      const g = Motor.reproduzir(4242, log as never, 13).digibrain();
      if (g?.decisao) grande = g;
    }
    const mapa = grande.mapa, decisao = grande.decisao;
    for (let i = 0; i < 5; i++) montar(false, true, mapa, decisao);   // aquece
    const t: number[] = [];
    for (let i = 0; i < 30; i++) { const a = performance.now(); montar(false, true, mapa, decisao); t.push(performance.now() - a); }
    t.sort((a, b) => a - b);
    console.log(`MapaScan: ${mapa.arestas.length} fios + ${mapa.acesas!.arestas.length} acesas + pulso; mediana ${t[15]!.toFixed(2)} ms, max ${t[29]!.toFixed(2)} ms (renderToStaticMarkup, node)`);
    expect(t[15]!).toBeLessThan(200);   // so um teto frouxo: acima disso algo quebrou
  });
});

describe("o scan cobre a ilha", () => {
  /* o ScanDigiBrain chama `useEffect(cobrirCena, [])`; o ambiente dos testes e node (sem jsdom no projeto), entao o par montar/desmontar e
     testado pela funcao que o efeito usa */
  test("montado, CENA.coberto fica true; desmontado, volta a false", () => {
    expect(CENA.coberto).toBe(false);
    const limpar = cobrirCena();
    expect(CENA.coberto).toBe(true);
    limpar();
    expect(CENA.coberto).toBe(false);
  });
  test("a ordem do DOM e a do celular: agora, mapa, lobos, percepcao, opcoes, aprendido, ultimas", async () => {
    const { readFileSync } = await import("node:fs");
    const fonte = readFileSync(new URL("../src/componentes/ScanDigiBrain.tsx", import.meta.url), "utf8");
    expect(fonte).toContain("{agora}{centro}{lobos}{perc}{opc}{apr}{ult}");
    expect(fonte).toContain("useEffect(cobrirCena, [])");
  });
});
