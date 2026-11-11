// O desenho do scan do DigiBrain (D1 e D1e da UX_TELA_PET; src/componentes/ScanDigiBrain.tsx). Sem DOM (vitest em node): renderToStaticMarkup.
// Cobre: a rede viva (uma ilustracao: deterministica pela semente do pet, dentro do quadro, sem texto nem nos do motor), quantos impulsos
// correm (o que o desenho le da decisao), as marcas de parada e de decisao nova, a faixa de baixo (a onda e o estado atual, que saem do
// motor), os numeros do movimento e o contraste nas duas peles.
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { Motor } from "../motor/index.ts";
import { REGRAS_LOBOS } from "../motor/index.ts";
import {
  FaixaEstado, GIRO_CICLO_S, GIRO_GRAUS, IMPULSOS_MIN, IMPULSOS_POR_ENTRADA, N_IMPULSOS, PULSO_MS, RedeVivaDesenho, TOM_REGRA, VARREDURA_MS,
  impulsosDaDecisao, picosDaDecisao, pontosDaOnda, redeViva,
} from "../src/componentes/ScanDigiBrain.tsx";

/* o pet v11 do e2e do DigiBrain (e2e/jogo.spec.ts) */
const LOG: [number, string, unknown][] = [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]];
const m = Motor.reproduzir(4242, LOG as never, 21), db = m.digibrain()!;
const montar = (o: { movel?: boolean; correndo?: boolean; surto?: boolean; acesas?: typeof db.mapa.acesas } = {}): string =>
  renderToStaticMarkup(h(RedeVivaDesenho, { semente: 4242, n: (o.acesas === undefined ? db.mapa.acesas : o.acesas)?.n ?? null,
    pesaram: (o.acesas === undefined ? db.mapa.acesas : o.acesas)?.arestas.length ?? 0, tom: TOM_REGRA[db.decisao!.regra],
    movel: o.movel ?? false, correndo: o.correndo ?? true, surto: o.surto ?? false }));
const contar = (s: string, re: RegExp): number => (s.match(re) ?? []).length;
const grupo = (s: string, classe: string): string => s.match(new RegExp(`<g class="${classe}"[^>]*>(.*?)</g>`))![1]!;

describe("a rede viva (D1e): uma ilustracao, nao o mapa dos pesos", () => {
  test("o pet do e2e tem decisao e arestas acesas", () => {
    expect(db.decisao).not.toBeNull();
    expect(db.mapa.acesas).not.toBeNull();
  });
  test("a mesma semente da a mesma rede; outra semente, outra rede", () => {
    expect(redeViva(4242)).toEqual(redeViva(4242));
    expect(redeViva(4243).fios).not.toEqual(redeViva(4242).fios);
  });
  test("a rede cabe no quadro: nenhum ponto nem fio fora do viewBox 880 x 552, e o meio do anel fica vazio", () => {
    for (const semente of [1, 4242, 99999]) {
      const rede = redeViva(semente);
      expect(rede.pontos.length).toBe(150);
      expect(rede.impulsos.length).toBe(N_IMPULSOS);
      expect(rede.fios.length).toBeGreaterThan(500); expect(rede.fios.length).toBeLessThan(600);
      for (const p of rede.pontos) {
        expect(p.x).toBeGreaterThan(0); expect(p.x).toBeLessThan(880); expect(p.y).toBeGreaterThan(0); expect(p.y).toBeLessThan(552);
        expect(Math.hypot(p.x - 440, p.y - 276)).toBeGreaterThan(80);
      }
      const nums = [...rede.fios, ...rede.impulsos].flatMap(d => [...d.matchAll(/(-?[0-9.]+) (-?[0-9.]+)/g)].map(c => [Number(c[1]), Number(c[2])]));
      expect(nums.length).toBeGreaterThan(1000);
      for (const [x, y] of nums) { expect(x).toBeGreaterThan(0); expect(x).toBeLessThan(880); expect(y).toBeGreaterThan(0); expect(y).toBeLessThan(552); }
    }
  });
  test("quantos impulsos correm sai da decisao: o minimo, mais dois por entrada que pesou, ate o teto", () => {
    const ac = db.mapa.acesas!;
    expect(impulsosDaDecisao(0)).toBe(IMPULSOS_MIN);
    expect(impulsosDaDecisao(ac.arestas.length)).toBe(Math.min(N_IMPULSOS, IMPULSOS_MIN + IMPULSOS_POR_ENTRADA * ac.arestas.length));
    expect(impulsosDaDecisao(40)).toBe(N_IMPULSOS);
    expect(() => impulsosDaDecisao(-1)).toThrow(/pesaram/);
  });
  for (const movel of [false, true]) {
    test(`o SVG (${movel ? "390" : "1920"} px): os fios, os pontos e os impulsos da rede, sem texto e sem os nos do motor`, () => {
      const s = montar({ movel }), ac = db.mapa.acesas!, rede = redeViva(4242);
      expect(s).toContain('viewBox="0 0 880 552"');
      expect(s).toContain(`data-n="${ac.n}"`);
      expect(s).toContain(`data-impulsos="${impulsosDaDecisao(ac.arestas.length)}"`);
      expect(s).toContain(`data-tom="${TOM_REGRA[db.decisao!.regra]}"`);
      expect(contar(grupo(s, "rv-fios"), /<path /g)).toBe(rede.fios.length);
      expect(contar(grupo(s, "rv-impulsos"), /<path /g)).toBe(impulsosDaDecisao(ac.arestas.length));
      expect(contar(grupo(s, "rv-pontos"), /<circle /g)).toBe(rede.pontos.length);
      expect(s).toContain('role="img"');
      expect(s).toContain("os pesos de verdade estão no mapa em texto");
      expect(s).not.toMatch(/<text|data-entrada|data-regra|data-acao|mp-pesos|mp-acesas|mp-no|mp-silhueta/);
    });
  }
  test("as marcas: parada com o tempo parado, surto numa decisao nova; sem decisao, o minimo de impulsos", () => {
    expect(montar()).not.toMatch(/rv--parada|rv--surto/);
    expect(montar({ correndo: false })).toContain("rv--parada");
    expect(montar({ surto: true })).toContain("rv--surto");
    const sem = montar({ acesas: null });
    expect(sem).toContain('data-n=""');
    expect(contar(grupo(sem, "rv-impulsos"), /<path /g)).toBe(IMPULSOS_MIN);
  });
  test("o custo de montar o SVG (mediana de 30 montagens, impressa)", () => {
    for (let i = 0; i < 5; i++) montar();   // aquece
    const t: number[] = [];
    for (let i = 0; i < 30; i++) { const a = performance.now(); montar(); t.push(performance.now() - a); }
    t.sort((a, b) => a - b);
    console.log(`RedeVivaDesenho: ${redeViva(4242).fios.length} fios; mediana ${t[15]!.toFixed(2)} ms, max ${t[29]!.toFixed(2)} ms (renderToStaticMarkup, node)`);
    expect(t[15]!).toBeLessThan(200);   // so um teto frouxo: acima disso algo quebrou
  });
  test("com \"reduzir movimento\" nada anima: toda animacao da rede fica dentro do no-preference", () => {
    const css = readFileSync(new URL("../src/estilo/scan_digibrain.css", import.meta.url), "utf8");
    const fora = css.replace(/@media \(prefers-reduced-motion:no-preference\)\{[\s\S]*?\n\}/g, "");
    expect(fora).not.toMatch(/animation:\s*rv-/);
    expect(css).toMatch(/animation:\s*rv-impulso/);
  });
});

describe("a faixa de baixo (D1e): a onda e o estado atual saem do motor", () => {
  const ent = ["vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "ticks_sem_cuidado", ...db.mapa.receptores];
  test("a onda: um pico por aresta acesa, para cima a favor e para baixo contra, da altura da forca", () => {
    const ac = db.mapa.acesas!, pts = pontosDaOnda(ent, picosDaDecisao(ac)).split(" ").map(p => p.split(",").map(Number));
    expect(pts.length).toBe(2 + 3 * ac.arestas.length);
    for (const x of ac.arestas) {
      const pico = pts.find(p => p[0] === 12 * ent.indexOf(x.entrada) + 6)!;
      expect(pico[1]).toBeCloseTo(20 - Math.sign(x.termo) * x.forca * 17, 1);
    }
    /* uma decisao montada: um termo a favor e um contra */
    const dois = pontosDaOnda(ent, picosDaDecisao({ ...ac, arestas: [{ entrada: "fome", termo: 0.5, forca: 1 }, { entrada: "humor", termo: -0.2, forca: 0.5 }] }));
    expect(dois).toBe("0,20 14,20 18,3 22,20 50,20 54,28.5 58,20 " + 12 * ent.length + ",20");
    expect(pontosDaOnda(ent, picosDaDecisao(null))).toBe(`0,20 ${12 * ent.length},20`);
    expect(() => pontosDaOnda(ent, [{ entrada: "inventada", altura: 1 }])).toThrow(/entrada fora do mapa: inventada/);
    expect(() => pontosDaOnda(ent, [{ entrada: "fome", altura: 1.5 }])).toThrow(/fora de -1 a 1/);
  });
  test("o estado atual e a regra da decisao, com o tom dela; sem decisao, diz isso", () => {
    const s = renderToStaticMarkup(h(FaixaEstado, { mapa: db.mapa, decisao: db.decisao })), d = db.decisao!;
    expect(s).toContain(`data-regra="${d.regra}"`);
    expect(s).toContain(`data-tom="${TOM_REGRA[d.regra]}"`);
    expect(s).toContain("estado atual");
    expect(s).toContain(`data-n="${d.n}"`);
    const sem = renderToStaticMarkup(h(FaixaEstado, { mapa: { ...db.mapa, acesas: null }, decisao: null }));
    expect(sem).toContain('data-tom="sem"');
    expect(sem).toContain("sem decisão");
    expect(Object.keys(TOM_REGRA).sort()).toEqual([...REGRAS_LOBOS].sort());
    /* a coluna das cinco barras da referencia nao entra, e nada promete mais do que o motor tem */
    expect(s).not.toMatch(/memória|impulsos|emoção|social|calmo/i);
  });
});

describe("os numeros do movimento sao os PROPOSTOS da D1-2", () => {
  test("varredura 1,2 s, pulso 0,8 s, giro de 8 graus num ciclo de 40 s", () => {
    expect([VARREDURA_MS, PULSO_MS, GIRO_GRAUS, GIRO_CICLO_S]).toEqual([1200, 800, 8, 40]);
  });
});

describe("o modal pequeno nao cobre a ilha (D1b-3)", () => {
  /* o ambiente dos testes e node (sem jsdom no projeto): o contrato e conferido na fonte */
  test("sem CENA.coberto, sem os cartoes nem a legenda do rodape", async () => {
    const { readFileSync } = await import("node:fs");
    const fonte = readFileSync(new URL("../src/componentes/ScanDigiBrain.tsx", import.meta.url), "utf8");
    expect(fonte).not.toMatch(/cenaEstado|CENA.coberto =|cobrirCena/);
    expect(fonte).not.toMatch(/db-barras|db-opcoes|db-ultimas|SeloEmocao|mp-nota/);
    const css = readFileSync(new URL("../src/estilo/scan_digibrain.css", import.meta.url), "utf8");
    expect(css).not.toMatch(/#[0-9a-fA-F]{3,8}/);
    expect(css.match(/\.scan::backdrop\{[^}]*\}/)![0]).not.toMatch(/backdrop-filter|blur/);
  });
});

/* o contraste do desenho (rev-a11y da D1b): o modal fica sobre a ilha, entao o pior fundo e o do habitat mais claro, como em hx_pele.test.ts
   (a grama de dia; no Militar, o branco puro). A pilha, de baixo para cima: o fundo, o veu do ::backdrop (o --hx-miolo a 28 %), a caixa
   (o --hud-fundo-1, o lado mais claro do gradiente) e a moldura do desenho (o --hx-miolo a 92 %, D1e). O contorno escuro dos rotulos (paint-order)
   so ajuda e nao entra na conta. Com "reduzir transparencia" os tokens ficam opacos e mais escuros, entao o caso translucido e o pior */
describe("o contraste do desenho sobre a ilha, nas duas peles", () => {
  const tokensCss = readFileSync(new URL("../src/estilo/tokens.css", import.meta.url), "utf8");
  type Rgb = [number, number, number];
  const bloco = (sel: string) => { const i = tokensCss.indexOf(sel); if (i < 0) throw new Error(`sem ${sel}`); return tokensCss.slice(i, tokensCss.indexOf("}", i)); };
  const raiz = tokensCss;
  const ler = (b: string, nome: string): string => {
    const m = b.match(new RegExp(`--${nome}:([^;]+);`)) ?? raiz.match(new RegExp(`--${nome}:([^;]+);`));
    if (!m) throw new Error(`token ${nome}`);
    const v = m[1]!.trim(), ref = v.match(/^var\(--([\w-]+)\)$/);
    return ref ? ler(b, ref[1]!) : v;
  };
  const rgba = (v: string): [Rgb, number] => {
    const h = v.match(/^#([0-9A-Fa-f]{6})$/); if (h) return [[1, 3, 5].map(i => parseInt(v.slice(i, i + 2), 16)) as Rgb, 1];
    const m = v.match(/^rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)$/); if (!m) throw new Error(`cor ${v}`);
    return [[+m[1]!, +m[2]!, +m[3]!], +m[4]!];
  };
  const sobre = (cor: string, fundo: Rgb, mult = 1): Rgb => { const [c, a0] = rgba(cor), a = a0 * mult; return c.map((x, i) => x * a + fundo[i]! * (1 - a)) as Rgb; };
  const lum = (c: Rgb) => { const l = c.map(x => x / 255).map(x => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4)); return 0.2126 * l[0]! + 0.7152 * l[1]! + 0.0722 * l[2]!; };
  const contraste = (a: Rgb, b: Rgb) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x! + 0.05) / (y! + 0.05); };
  const casos: [string, string, Rgb][] = [["vidro", ':root[data-pele="vidro"]{', [161, 225, 113]], ["militar", ":root{", [255, 255, 255]]];
  for (const [pele, sel, ilha] of casos) {
    test(`${pele}: os rotulos 4,5:1 e as formas do selo 3:1`, () => {
      const b = pele === "vidro" ? bloco(sel) : raiz, t = (n: string) => rgba(ler(b, n))[0];
      const veu = sobre(ler(b, "hx-miolo"), ilha, 0.28), caixa = sobre(ler(b, "hud-fundo-1"), veu), desenho = sobre(ler(b, "hx-miolo"), caixa, 0.92);
      /* os nos (--hx-sec), as regioes (--hx-rotulo), os receptores do corpo (--hx-ok), os acesos (--hx-texto) e a chance (--hx-num), no desenho */
      for (const n of ["hx-sec", "hx-rotulo", "hx-ok", "hx-texto", "hx-num"]) expect(contraste(t(n), desenho), `${pele} ${n} no desenho`).toBeGreaterThanOrEqual(4.5);
      /* o tom do estado atual (--hx-alerta, --hx-perigo; o ok, o neutro e o sem ja estao acima), no fundo da faixa, o mesmo do desenho */
      for (const n of ["hx-alerta", "hx-perigo"]) expect(contraste(t(n), desenho), `${pele} ${n} na faixa`).toBeGreaterThanOrEqual(4.5);
      /* o titulo e os icones do topo, na caixa */
      for (const n of ["hx-texto", "hx-texto-2"]) expect(contraste(t(n), caixa), `${pele} ${n} na caixa`).toBeGreaterThanOrEqual(4.5);
      /* o selo: o ponto (--hx-ok), as barras (--hx-sec) e o triangulo (--hx-rotulo), na caixa */
      for (const n of ["hx-ok", "hx-sec", "hx-rotulo"]) expect(contraste(t(n), caixa), `${pele} selo ${n}`).toBeGreaterThanOrEqual(3);
    });
  }
});
