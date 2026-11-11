// O protótipo P0 do gosto visual (docs/futuro/gosto_visual_pet.md, seção 14; src/gostoVisual/). Sem DOM (vitest em node).
// Cobre: a chave desligada por padrão e o app sem nada do protótipo; os sentidos (visão e som) a partir de pixels e amostras; o inato
// determinístico pela semente; a habituação (o interesse se gasta e volta); a exposição e o carinho deslocando o alvo; o estado guardado
// sem quadro nem áudio e o erro alto num estado estranho; o protótipo fora do motor e do log.
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test } from "vitest";
import { GOSTO_VISUAL_LIGADO, gostoVisualLigado } from "../src/gostoVisual/chave.ts";
import { GostoVisual, PetAssistindo } from "../src/gostoVisual/GostoVisual.tsx";
import { analisarQuadro, vetorDoSom } from "../src/gostoVisual/sentidos.ts";
import {
  COMPONENTES, alvo, doTexto, valores, estadoInicial, gostaMaisDe, inatoDaSemente, paraTexto, passo, tempoJunto, type EstadoGosto, type Sentido,
} from "../src/gostoVisual/gosto.ts";

const quadro = (w: number, h: number, f: (x: number, y: number) => [number, number, number]): Uint8ClampedArray => {
  const px = new Uint8ClampedArray(w * h * 4);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const [r, g, b] = f(x, y); px.set([r, g, b, 255], 4 * (y * w + x)); }
  return px;
};
const visto = (cor: number, brilho: number, movimento: number, complexidade: number): Sentido => ({ visao: { cor, brilho, movimento, complexidade }, som: null });
const rodar = (semente: number, s: Sentido, n: number, carinho = false): EstadoGosto => {
  const ina = inatoDaSemente(semente);
  let e = estadoInicial();
  for (let i = 0; i < n; i++) e = passo(ina, e, s, carinho).estado;
  return e;
};

describe("a chave", () => {
  test("desligada por padrão: sem o parâmetro, ou com outro valor, não liga", () => {
    expect(GOSTO_VISUAL_LIGADO).toBe(false);
    expect(gostoVisualLigado("")).toBe(false);
    expect(gostoVisualLigado("?gosto_visual=0")).toBe(false);
    expect(gostoVisualLigado("?luta_poc=1")).toBe(false);
    expect(gostoVisualLigado("?gosto_visual=1")).toBe(true);
  });
  test("desligada, o componente não renderiza nada (o app de hoje)", () => {
    expect(renderToStaticMarkup(h(GostoVisual))).toBe("");
  });
  test("o App só ganha a montagem do componente, e fora dele só o cantinho da TV na ilha (atrás da mesma chave) importa o protótipo", () => {
    const raiz = join(import.meta.dirname, "..", "src"), quem: string[] = [];
    const andar = (d: string): void => { for (const n of readdirSync(d, { withFileTypes: true })) {
      const p = join(d, n.name);
      if (n.isDirectory()) { if (n.name !== "gostoVisual") andar(p); }
      else if (/\.(ts|tsx)$/.test(n.name) && readFileSync(p, "utf8").includes("gostoVisual/")) quem.push(n.name);
    } };
    andar(raiz);
    /* o cantinho da TV (ilha/cantinhoTv.ts e cantinhoTvConta.ts; test/gosto_visual_tv.test.ts confere a chave dele) lê a chave e o estado da TV */
    expect(quem.sort()).toEqual(["App.tsx", "cantinhoTv.ts", "cantinhoTvConta.ts"]);
  });
  test("o protótipo fica fora do motor, do log e do save: não importa mudarMotor, aplicarEvento nem o save", () => {
    const dir = join(import.meta.dirname, "..", "src", "gostoVisual");
    for (const n of readdirSync(dir)) {
      const t = readFileSync(join(dir, n), "utf8");
      expect(t, n).not.toMatch(/mudarMotor|aplicarEvento|trocarMotor|from "\.\.\/save\.ts"/);
    }
  });
});

describe("os sentidos", () => {
  test("um quadro cinza liso: sem cor, sem borda, sem movimento; o brilho é a luminância", () => {
    const { vetor, lum } = analisarQuadro(quadro(8, 4, () => [128, 128, 128]), 8, 4, null);
    expect(vetor.cor).toBe(0);
    expect(vetor.complexidade).toBe(0);
    expect(vetor.movimento).toBe(0);
    expect(vetor.brilho).toBeCloseTo(128 / 255, 5);
    const segundo = analisarQuadro(quadro(8, 4, () => [255, 255, 255]), 8, 4, lum).vetor;
    expect(segundo.movimento).toBe(1); /* a diferença de 0,5 vezes o ganho 4 passa de 1 e é limitada */
  });
  test("um xadrez vermelho e preto: cor e complexidade no máximo", () => {
    const v = analisarQuadro(quadro(8, 8, (x, y) => ((x + y) % 2 ? [255, 0, 0] : [0, 0, 0])), 8, 8, null).vetor;
    expect(v.complexidade).toBe(1);
    expect(v.cor).toBeCloseTo(0.5, 5); /* metade vermelho puro, metade preto (saturação 0) */
  });
  test("um quadro com o tamanho errado falha alto", () => {
    expect(() => analisarQuadro(new Uint8ClampedArray(10), 8, 4, null)).toThrow(/bytes/);
  });
  test("o som: o volume do RMS, a variação entre janelas e o timbre do centróide", () => {
    const grave = new Uint8Array(512); grave[4] = 255;
    const agudo = new Uint8Array(512); agudo[200] = 255;
    const a = vetorDoSom([0.1, 0.1, 0.1], grave), b = vetorDoSom([0.02, 0.2, 0.02], agudo);
    expect(a.volume).toBeCloseTo(0.4, 5);
    expect(a.variacao).toBeCloseTo(0, 6);
    expect(b.variacao).toBeGreaterThan(0.5);
    expect(b.timbre).toBeGreaterThan(a.timbre);
    expect(vetorDoSom([0], new Uint8Array(512)).timbre).toBe(0);
    expect(() => vetorDoSom([], grave)).toThrow(/janela/);
  });
});

describe("o gosto", () => {
  test("o inato é determinístico pela semente e muda entre pets", () => {
    expect(inatoDaSemente(101)).toEqual(inatoDaSemente(101));
    expect(inatoDaSemente(101)).not.toEqual(inatoDaSemente(202));
    for (const k of COMPONENTES) { const o = inatoDaSemente(303).otimo[k]; expect(o).toBeGreaterThanOrEqual(0.15); expect(o).toBeLessThanOrEqual(0.85); }
  });
  test("a mesma sequência dá o mesmo estado (determinismo do protótipo)", () => {
    expect(rodar(101, visto(0.8, 0.5, 0.6, 0.4), 200)).toEqual(rodar(101, visto(0.8, 0.5, 0.6, 0.4), 200));
  });
  test("a habituação: olhando a mesma coisa, o interesse cai e o pet desvia; sem olhar, o interesse volta", () => {
    const ina = inatoDaSemente(101), s: Sentido = { visao: { cor: ina.otimo.cor, brilho: ina.otimo.brilho, movimento: ina.otimo.movimento, complexidade: ina.otimo.complexidade }, som: null };
    let e = estadoInicial(), olhou = false, desviou = false;
    for (let i = 0; i < 120; i++) { const r = passo(ina, e, s, false); e = r.estado; if (r.leitura.olhando) olhou = true; else if (olhou) desviou = true; }
    expect(olhou).toBe(true);
    expect(desviou).toBe(true);
    const cansado = e.interesse;
    expect(cansado).toBeLessThan(0.6);
    /* um quadro novo devolve interesse (a deshabituação) */
    const novo = passo(ina, e, visto(1 - s.visao.cor, 1 - s.visao.brilho, s.visao.movimento, s.visao.complexidade), false);
    expect(novo.leitura.novidade).toBeGreaterThan(0.1);
  });
  test("a exposição desloca o alvo devagar na direção do que o pet vê, e para no limite", () => {
    const ina = inatoDaSemente(202), e = rodar(202, visto(1, 1, 1, 1), 3000);
    for (const k of ["cor", "brilho", "movimento", "complexidade"] as const) {
      expect(alvo(ina, e, k)).toBeGreaterThan(ina.otimo[k]);
      expect(e.exposicao[k]).toBeLessThanOrEqual(0.25);
    }
    expect(e.carinho.cor).toBe(0);
    expect(e.exposicao.volume).toBe(0); /* sem som, o alvo do som não anda */
  });
  test("o carinho puxa o alvo para o que está passando, mais rápido que a exposição, e fica separado dela", () => {
    const ina = inatoDaSemente(303), s = visto(0, 0, 0, 0);
    const so = rodar(303, s, 5), com = rodar(303, s, 5, true);
    expect(com.carinhos).toBe(5);
    expect(alvo(ina, com, "cor")).toBeLessThan(alvo(ina, so, "cor"));
    expect(Math.abs(com.carinho.cor)).toBeGreaterThan(Math.abs(com.exposicao.cor));
  });
  test("o 'gosta mais de' em palavras: os dois componentes mais marcados", () => {
    const p = { cor: 0.95, brilho: 0.5, movimento: 0.9, complexidade: 0.55, volume: 0.5, variacao: 0.5, timbre: 0.5 };
    expect(gostaMaisDe(p)).toBe("cores vivas e muito movimento");
    expect(gostaMaisDe({ ...p, cor: 0.1 })).toBe("cores suaves e muito movimento");
  });
  test("o estado guardado: só o aprendido e o tempo; volta igual; um texto estranho falha alto", () => {
    const e = rodar(101, visto(0.3, 0.7, 0.2, 0.9), 50, true), t = paraTexto(e);
    expect(Object.keys(JSON.parse(t))).toEqual(["v", "exposicao", "carinho", "segundosJuntos", "carinhos"]);
    const d = doTexto(t);
    expect(d.exposicao).toEqual(e.exposicao);
    expect(d.carinho).toEqual(e.carinho);
    expect(d.segundosJuntos).toBe(50);
    expect(() => doTexto('{"v":2}')).toThrow(/versão/);
    expect(() => doTexto('{"v":1,"exposicao":{},"carinho":{},"segundosJuntos":0,"carinhos":0}')).toThrow(/exposicao/);
  });
  test("o tempo junto em palavras", () => {
    expect(tempoJunto(40)).toBe("40 s");
    expect(tempoJunto(750)).toBe("12 min 30 s");
    expect(tempoJunto(3900)).toBe("1 h 05 min");
  });
  test("o componente fora do jogo é estável: um componente fora de [0, 1] falha alto", () => {
    expect(() => passo(inatoDaSemente(101), estadoInicial(), visto(1.5, 0, 0, 0), false)).toThrow(/fora de/);
  });
});

describe("a TV do jogo", () => {
  test("os programas têm os sete componentes em [0, 1], e a sequência é a mesma para a mesma semente", async () => {
    const { PROGRAMAS, ligarTvDoJogo } = await import("../src/gostoVisual/tvDoJogo.ts");
    for (const p of PROGRAMAS) expect(() => valores(p.perfil)).not.toThrow();
    const colher = (sem: number): Promise<string[]> => new Promise(ok => {
      const r: string[] = [], tv = ligarTvDoJogo(sem, (s, nome) => { r.push(nome + JSON.stringify(s)); if (r.length === 3) { tv.parar(); ok(r); } }, 1);
    });
    expect(await colher(101)).toEqual(await colher(101));
  });
});

describe("a vista", () => {
  test("mostra a reação, o gosto de hoje e o de nascença separados, e o tempo junto", () => {
    const ina = inatoDaSemente(101), e = rodar(101, visto(0.5, 0.5, 0.5, 0.5), 30);
    const html = renderToStaticMarkup(h(PetAssistindo, {
      v: { sprite: null, leitura: { agrado: 0.9, interesse: 0.8, novidade: 0, vontade: 0.8, olhando: true, reacao: "adorando" }, sentido: visto(0.5, 0.5, 0.5, 0.5), inato: ina, estado: e, capturando: true, temSom: false, origem: "a sua tela" },
      acoes: null,
    }));
    expect(html).toContain("adorando");
    expect(html).toContain("Gosta mais de:");
    expect(html).toContain("De nascença:");
    expect(html).toContain("30 s");
    expect(html).toContain("Sem som");
    expect(html).toContain("Assistindo: a sua tela");
    expect(html).not.toContain(">ritmo<"); /* sem som, as barras do som não aparecem */
  });
});
