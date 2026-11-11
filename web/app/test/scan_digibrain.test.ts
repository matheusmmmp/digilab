// O mapa do scan do DigiBrain (D1 da UX_TELA_PET; src/componentes/ScanDigiBrain.tsx). Sem DOM (vitest em node): renderToStaticMarkup.
// Cobre: cada ponto e um no do motor e cada fio uma aresta de Motor.digibrain().mapa (as contagens que o e2e le), o destaque da decisao, o
// pulso so quando pedido (e um por aresta acesa), a falha alta (no fora do mapa, mapa e decisao de passos diferentes), a 390 e a 1920, e o
// tempo de montar o SVG com os ~80 fios (impresso, nao assertado: a maquina muda).
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { Motor } from "../motor/index.ts";
import { REGRAS_LOBOS } from "../motor/index.ts";
import { FaixaEstado, GIRO_CICLO_S, GIRO_GRAUS, MapaScan, PULSO_MS, TOM_REGRA, VARREDURA_MS, pontosDaOnda } from "../src/componentes/ScanDigiBrain.tsx";

/* o pet v11 do e2e do DigiBrain (e2e/jogo.spec.ts) */
const LOG: [number, string, unknown][] = [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]];
const m = Motor.reproduzir(4242, LOG as never, 21), db = m.digibrain()!;
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
      /* as tres regioes com os nomes do dono (D1b-6), sem o "pesou mais" nem a regiao sem pesos da memoria */
      expect([...s.matchAll(/<text class="mp-reg" data-lobo="([^"]+)"[^>]*>([^<]+)<\/text>/g)].map(x => [x[1], x[2]]))
        .toEqual([["decisao", "ações"], ["impulsos", "regras"], ["percepcao", "percepção"]]);
      expect(s).not.toMatch(/mp-dest|pesou mais|memória e emoção/);
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
  test("o anel (D1d): o viewBox 880 x 552, as acoes a esquerda, as entradas a direita e as regras por dentro; sem a silhueta", () => {
    const s = montar(false, false);
    expect(s).toContain('viewBox="0 0 880 552"');
    expect(s).not.toMatch(/mp-silhueta|mp-divisas|db-malha/);
    /* o centro do ponto de cada no (o segundo circulo do grupo; o primeiro e o alvo do toque) */
    const centros = (attr: string): [number, number][] => [...s.matchAll(new RegExp(`${attr}="[^"]+"><circle class="mp-alvo" cx="([-0-9.]+)" cy="([-0-9.]+)"`, "g"))].map(m => [Number(m[1]), Number(m[2])]);
    const raio = ([x, y]: [number, number]): number => Math.hypot(x - 440, y - 276);
    const ac = centros("data-acao"), en = centros("data-entrada"), re = centros("data-regra");
    expect([ac.length, re.length, en.length]).toEqual([7, 7, 10 + db.mapa.receptores.length]);
    for (const p of ac) { expect(p[0]).toBeLessThan(440); expect(raio(p)).toBeCloseTo(212, 0); }
    for (const p of en) { expect(p[0]).toBeGreaterThan(440); expect(raio(p)).toBeCloseTo(212, 0); }
    for (const p of re) expect(raio(p)).toBeCloseTo(150, 0);
    /* todo fio fica dentro do quadro: nenhuma coordenada fora do viewBox */
    const nums = [...s.matchAll(/ d="([^"]+)"/g)].flatMap(m => [...m[1]!.matchAll(/(-?[\d.]+) (-?[\d.]+)/g)].map(c => [Number(c[1]), Number(c[2])]));
    expect(nums.length).toBeGreaterThan(200);
    for (const [x, y] of nums) { expect(x).toBeGreaterThanOrEqual(0); expect(x).toBeLessThanOrEqual(880); expect(y).toBeGreaterThanOrEqual(0); expect(y).toBeLessThanOrEqual(552); }
  });
});

describe("a faixa de baixo (D1d): a onda e o estado atual saem do motor", () => {
  const ent = ["vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "ticks_sem_cuidado", ...db.mapa.receptores];
  test("a onda: um pico por aresta acesa, para cima a favor e para baixo contra, da altura da forca", () => {
    const ac = db.mapa.acesas!, pts = pontosDaOnda(ent, ac).split(" ").map(p => p.split(",").map(Number));
    expect(pts.length).toBe(2 + 3 * ac.arestas.length);
    for (const x of ac.arestas) {
      const pico = pts.find(p => p[0] === 12 * ent.indexOf(x.entrada) + 6)!;
      expect(pico[1]).toBeCloseTo(20 - Math.sign(x.termo) * x.forca * 17, 1);
    }
    /* uma decisao montada: um termo a favor e um contra */
    const dois = pontosDaOnda(ent, { ...ac, arestas: [{ entrada: "fome", termo: 0.5, forca: 1 }, { entrada: "humor", termo: -0.2, forca: 0.5 }] });
    expect(dois).toBe("0,20 14,20 18,3 22,20 50,20 54,28.5 58,20 " + 12 * ent.length + ",20");
    expect(pontosDaOnda(ent, null)).toBe(`0,20 ${12 * ent.length},20`);
    expect(() => pontosDaOnda(ent, { ...ac, arestas: [{ entrada: "inventada", termo: 1, forca: 1 }] })).toThrow(/entrada fora do mapa: inventada/);
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
      const g = Motor.reproduzir(4242, log as never, 21).digibrain();
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
   (o --hud-fundo-1, o lado mais claro do gradiente) e a moldura do desenho (o --hx-miolo a 92 %, D1d). O contorno escuro dos rotulos (paint-order)
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
