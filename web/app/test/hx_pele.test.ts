/* M1 do layout habitat: a pele XCOM (tokens --hx-*, hud.css e componentes hx). Sem DOM (vitest em node): renderToStaticMarkup
   e leitura do CSS. Os tokens sao conferidos em contraste 4,5:1 (texto) e 3:1 (bordas) pelo proprio teste. */
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { CTR } from "../motor/constantes.ts";
import { AbasHx, BotaoContinuar, BotaoHx, ChipHx, LinhaHx, MedidorHx, PainelHx, indiceAbaPorTecla } from "../src/componentes/hx/index.ts";

const tokens = readFileSync(new URL("../src/estilo/tokens.css", import.meta.url), "utf8");
const hud = readFileSync(new URL("../src/estilo/hud.css", import.meta.url), "utf8");
const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");

const lum = (hex: string) => {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((x) => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
};
const contraste = (a: string, b: string) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
const token = (nome: string) => { const m = tokens.match(new RegExp(`--${nome}:(#[0-9A-Fa-f]{6})`)); if (!m) throw new Error(`token ${nome}`); return m[1]; };

describe("tokens --hx-*", () => {
  it("valem em qualquer tema: ficam so no :root, sem variante por tema", () => {
    const bloco = tokens.slice(tokens.indexOf("Pele XCOM dos menus"));
    expect(bloco).not.toContain("data-tema");
    expect(bloco).not.toContain("prefers-color-scheme");
  });
  it("todo texto passa 4,5:1 contra o pior fundo dos menus, e as bordas 3:1", () => {
    const fundos = [token("hx-chao"), token("hx-miolo"), token("hx-miolo-2"), "#0E1E16"];
    for (const t of ["hx-texto", "hx-texto-2", "hx-sec", "hx-rotulo", "hx-btn-ink", "hx-alerta", "hx-perigo", "hx-ok", "hx-necessidade", "hx-aprendido", "hx-sombrio"]) {
      for (const f of fundos) expect(contraste(token(t), f), `${t} sobre ${f}`).toBeGreaterThanOrEqual(4.5);
    }
    expect(contraste(token("hx-escolhido-ink"), token("hx-escolhido"))).toBeGreaterThanOrEqual(4.5);
    expect(contraste(token("hx-escolhido-ink"), token("hx-necessidade"))).toBeGreaterThanOrEqual(4.5);
    for (const f of fundos) expect(contraste(token("hx-borda-topo"), f)).toBeGreaterThanOrEqual(3);
    expect(contraste(token("hx-btn-borda"), "#0E1E16")).toBeGreaterThanOrEqual(3);
  });
});

/* T1 do tema dos menus: a pele Sci-fi (vidro; docs/TAREFA_V2_TEMA_MENUS.md §3 e §6), refeita em 2026-10-31 mais translucida. O contraste e
   medido no pior caso do habitat (a ilha 3D): a grama de dia, o pixel mais claro das capturas da H5 (o desfoque so tira a media), com o
   reflexo azul claro de 10 % por cima (o comeco do --hx-reflexo). O render e conferido em e2e_capturas/conferencia_pele.spec.ts. */
const vidroCss = readFileSync(new URL("../src/estilo/pele-vidro.css", import.meta.url), "utf8");
const main = readFileSync(new URL("../src/main.tsx", import.meta.url), "utf8");
const blocoVidro = (() => { const i = tokens.indexOf(':root[data-pele="vidro"]{'); if (i < 0) throw new Error("sem o bloco do vidro"); return tokens.slice(i, tokens.indexOf("}", i)); })();
const tokenVidro = (nome: string) => { const m = blocoVidro.match(new RegExp(`--${nome}:([^;]+);`)); return m ? m[1].trim() : token(nome); };
type Rgb = [number, number, number];
const rgb = (v: string): [Rgb, number] => {
  const h = v.match(/^#([0-9A-Fa-f]{6})$/); if (h) return [[1, 3, 5].map((i) => parseInt(v.slice(i, i + 2), 16)) as Rgb, 1];
  const m = v.match(/^rgba\((\d+),(\d+),(\d+),([\d.]+)\)$/); if (!m) throw new Error(`cor ${v}`);
  return [[+m[1], +m[2], +m[3]], +m[4]];
};
const sobre = (cor: string, fundo: Rgb): Rgb => { const [c, a] = rgb(cor); return c.map((x, i) => x * a + fundo[i] * (1 - a)) as Rgb; };
const hex = (c: Rgb) => "#" + c.map((x) => Math.round(x).toString(16).padStart(2, "0")).join("");

describe("pele Sci-fi (vidro)", () => {
  const grama: Rgb = [161, 225, 113];
  const pior = sobre("rgba(170,225,255,.10)", sobre(tokenVidro("hx-miolo-2"), grama));
  it("todo texto passa 4,5:1 sobre o vidro com o habitat mais claro atras; bordas e foco 3:1", () => {
    for (const t of ["hx-texto", "hx-texto-2", "hx-sec", "hx-rotulo", "hx-num", "hx-alerta", "hx-perigo", "hx-ok", "hx-aprendido", "hx-foco", "hx-sombrio"]) {
      expect(contraste(tokenVidro(t).replace(/^var\(--hx-texto\)$/, token("hx-texto")), hex(pior)), t).toBeGreaterThanOrEqual(4.5);
    }
    const escolhido = sobre("rgba(58,168,255,.40)", pior), botao = sobre(tokenVidro("hx-btn-bg"), pior);
    expect(tokenVidro("hx-escolhido")).toContain("rgba(58,168,255,.40)");
    expect(contraste(tokenVidro("hx-escolhido-ink"), hex(escolhido))).toBeGreaterThanOrEqual(4.5);
    expect(contraste(tokenVidro("hx-btn-ink"), hex(botao))).toBeGreaterThanOrEqual(4.5);
    expect(contraste(hex(sobre(tokenVidro("hx-borda"), pior)), hex(pior))).toBeGreaterThanOrEqual(3);
    expect(contraste(tokenVidro("hx-escolhido-borda"), hex(pior))).toBeGreaterThanOrEqual(3);
    expect(contraste("#0A1316", token("hx-necessidade"))).toBeGreaterThanOrEqual(4.5);
    expect(vidroCss).toContain(".hx-chip--necessidade{ color:#0A1316 }");
  });
  it("sem variante por tema; transparencia reduzida deixa o vidro opaco, sem desfoque", () => {
    expect(blocoVidro).not.toContain("data-tema");
    const reduz = tokens.slice(tokens.indexOf("@media (prefers-reduced-transparency: reduce)"));
    expect(reduz).toMatch(/--hx-vidro:none/);
    expect(reduz).toMatch(/--hx-reflexo:none/);
    for (const t of ["hx-chao", "hx-miolo", "hx-miolo-2", "hx-btn-bg"]) expect(reduz).toMatch(new RegExp(`--${t}:#[0-9A-Fa-f]{6};`));
  });
  it("o Militar e fosco e reto: sem vidro, sem chanfro, sem brilho, a HUD quase opaca", () => {
    for (const [t, v] of [["hx-vidro", "none"], ["hx-reflexo", "none"], ["hx-sombra", "none"], ["hx-chanfro", "0px"], ["hx-luz", "transparent"],
      ["hx-escolhido-borda", "#C5CFB0"], ["hx-titulo-tam", "18px"], ["hx-medidor-alt", "12px"], ["hud-desfoque", "none"], ["hud-ch", "0px"],
      ["hud-brilho", "none"], ["hud-fundo-1", "rgba(30,33,36,.97)"]]) expect(tokens).toContain(`--${t}:${v};`);
    /* o pior fundo da HUD: a caixa de alfa .97 sobre branco puro */
    const hud = hex(sobre("rgba(30,33,36,.97)", [255, 255, 255]));
    for (const t of ["hx-texto", "hx-texto-2", "hx-sec", "hx-rotulo", "hx-btn-ink", "hx-alerta", "hx-perigo", "hx-foco", "hx-sombrio"]) {
      expect(contraste(token(t), hud), t).toBeGreaterThanOrEqual(4.5);
    }
  });
  it("o vidro e translucido de verdade (o cenario passa) e a HUD segue a pele", () => {
    for (const t of ["hx-miolo-2", "hx-miolo"]) expect(rgb(tokenVidro(t))[1]).toBeLessThanOrEqual(0.86);
    expect(tokenVidro("hud-fundo-1")).toBe("var(--hx-miolo-2)");
    expect(tokenVidro("hud-desfoque")).toBe("var(--hx-vidro)");
  });
  it("pele-vidro.css: toda regra sob :root[data-pele=\"vidro\"], sem animacao, importada por ultimo; Barlow e Rajdhani no index.html", () => {
    const semComentario = vidroCss.replace(/\/\*[\s\S]*?\*\//g, "");
    const seletores = [...semComentario.matchAll(/(?:^|[}{])\s*([^{}@]+?)\s*\{/g)].map((m) => m[1]);
    expect(seletores.length).toBeGreaterThan(20);
    /* as virgulas de fora dos parenteses (as de dentro de :is() e :has() nao separam regras) */
    const partes = (sel: string) => { const r: string[] = []; let d = 0, ini = 0;
      [...sel].forEach((c, i) => { if (c === "(") d++; else if (c === ")") d--; else if (c === "," && d === 0) { r.push(sel.slice(ini, i)); ini = i + 1; } });
      return [...r, sel.slice(ini)]; };
    for (const sel of seletores) for (const parte of partes(sel)) expect(parte.trim(), sel).toMatch(/^:root\[data-pele="vidro"\]/);
    expect(semComentario).not.toMatch(/animation|transition/);
    const imports = [...main.matchAll(/^import "\.\/estilo\/([^"]+)";/gm)].map((m) => m[1]);
    expect(imports.at(-1)).toBe("pele-vidro.css");
    expect(main).toMatch(/iniciarTema\(\);\niniciarPele\(\);/);
    expect(html).toContain("family=Barlow:wght@400;600;700");
    expect(html).toContain("family=Rajdhani:wght@700");
  });
});

/* B3 (docs/TAREFA_V3_LUTA_LAYOUT.md, teste 4): as caixas da luta (plaquinhas, relogio, etiqueta e contexto, cartao da regra, dock) ficam sobre o
   mapa do UP do lugar, a tela inteira. O pior fundo e o pixel mais claro dos mapas depois do desfoque (a media local de 24 px, medida em
   Assets/arena_up/mapas, que fica fora do repositorio): no alto (as plaquinhas, o relogio, o contexto e o cartao da regra no desktop) o ceu
   claro da praia e o fundo do ringue; embaixo (o dock e a faixa da regra no celular) o piso da praia e o do ringue, os mais claros. O degrade
   escuro do alto e do pe (luta_hud.css) so ajuda. Nenhum token novo: o CSS da luta nao declara --hx-* nem --hud-*. */
describe("caixas da luta nas duas peles", () => {
  const lutaCss = readFileSync(new URL("../src/estilo/luta_hud.css", import.meta.url), "utf8");
  /* ceu da praia (cenasTR.ts) e praia_piso.jpg, sob o degrade preto de luta_hud.css (.45 no topo, 0 em 22 %; 0 em 70 %, .55 no pe): as caixas do
     alto ficam de 1 % a 26 % da altura (alfa >= .2 mesmo no pior ponto) e o dock e a faixa da regra de 90 % a 99 % (alfa >= .35) */
  const escurecer = (c: Rgb, a: number): Rgb => c.map(x => x * (1 - a)) as Rgb;
  const ALTO = escurecer([217, 240, 247], .2), PE = escurecer([255, 252, 244], .35);
  const vidroSobre = (fundo: Rgb) => sobre("rgba(170,225,255,.10)", sobre(tokenVidro("hx-miolo-2"), fundo));
  const tVidro = (t: string) => tokenVidro(t).replace(/^var\(--hx-texto\)$/, token("hx-texto"));
  it("Vidro, no alto: todo texto das caixas passa 4,5:1 sobre o vidro com o mapa mais claro atras; no cartao da regra tambem", () => {
    const pior = vidroSobre(ALTO), regra = sobre(tokenVidro("hx-miolo-2"), pior);
    for (const t of ["hx-texto", "hx-texto-2", "hx-sec", "hx-rotulo", "hx-num", "hx-aprendido", "hx-perigo", "hx-ok", "hx-alerta", "hx-sombrio"]) {
      expect(contraste(tVidro(t), hex(pior)), `alto ${t}`).toBeGreaterThanOrEqual(4.5);
    }
    for (const t of ["hx-texto", "hx-aprendido", "hx-sec", "hx-rotulo"]) expect(contraste(tVidro(t), hex(regra)), `regra ${t}`).toBeGreaterThanOrEqual(4.5);
  });
  it("Vidro, no pe: o dock e a faixa da regra (texto, aprendido, perigo do Desistir, o escolhido) sobre o piso mais claro", () => {
    const pior = vidroSobre(PE), regra = sobre(tokenVidro("hx-miolo-2"), pior);
    for (const t of ["hx-texto", "hx-texto-2", "hx-perigo"]) expect(contraste(tVidro(t), hex(pior)), `pe ${t}`).toBeGreaterThanOrEqual(4.5);
    for (const t of ["hx-texto", "hx-aprendido"]) expect(contraste(tVidro(t), hex(regra)), `faixa ${t}`).toBeGreaterThanOrEqual(4.5);
    expect(contraste(tokenVidro("hx-escolhido-ink"), hex(sobre("rgba(58,168,255,.40)", pior)))).toBeGreaterThanOrEqual(4.5);
  });
  it("Militar: a caixa quase opaca sobre o mapa mais claro; texto 4,5:1, o cartao da regra e o escolhido do dock tambem", () => {
    for (const fundo of [ALTO, PE]) {
      const caixa = hex(sobre("rgba(30,33,36,.97)", fundo));
      for (const t of ["hx-texto", "hx-texto-2", "hx-sec", "hx-rotulo", "hx-aprendido", "hx-perigo", "hx-ok", "hx-alerta", "hx-sombrio"]) expect(contraste(token(t), caixa), `militar ${t}`).toBeGreaterThanOrEqual(4.5);
    }
    for (const t of ["hx-texto", "hx-aprendido", "hx-sec"]) expect(contraste(token(t), token("hx-miolo-2")), `regra ${t}`).toBeGreaterThanOrEqual(4.5);
    expect(contraste(token("hx-escolhido-ink"), token("hx-escolhido"))).toBeGreaterThanOrEqual(4.5);
  });
  it("luta_hud.css so usa tokens que ja existem, sem animacao, e e importado pela tela da luta", () => {
    const semComentario = lutaCss.replace(/\/\*[\s\S]*?\*\//g, "");
    expect(semComentario).not.toMatch(/--hx-[a-z-]+\s*:|--hud-[a-z-]+\s*:/);
    expect(semComentario).not.toMatch(/animation|transition|@keyframes/);
    for (const [, nome] of semComentario.matchAll(/var\((--(?:hx|hud)-[a-z0-9-]+)/g)) expect(tokens, nome).toContain(nome + ":");
    /* desde a LP4 da LUTA_POC a tela da luta e a da POC (a TelaLuta do combate por turnos saiu) */
    expect(readFileSync(new URL("../src/telas/lutar/palcoPoc/TelaLutaPoc.tsx", import.meta.url), "utf8")).toContain('import "../../../estilo/luta_hud.css"');
  });
});

describe("hud.css e fonte", () => {
  it("respeita prefers-reduced-motion (transicao so em no-preference) e define foco", () => {
    expect(hud).toMatch(/@media \(prefers-reduced-motion: no-preference\)\{[^@]*transition/);
    expect(hud.split("@media")[0]).not.toContain("transition");
    expect(hud).toContain(":focus-visible");
  });
  it("Saira Condensed 400-700 carregada no index.html e usada so via --hx-f", () => {
    expect(html).toContain("family=Saira+Condensed:wght@400;500;600;700");
    expect(tokens).toContain('--hx-f:"Saira Condensed"');
    expect(hud).not.toContain("Saira");
  });
});

describe("PainelHx", () => {
  it("titulo em <h2> ligado a <section>, sem × quando nao ha onFechar", () => {
    const s = renderToStaticMarkup(h(PainelHx, { titulo: "Estado atual" }, "conteudo"));
    expect(s).toMatch(/<section class="hx-painel" aria-labelledby="([^"]+)"><header class="hx-painel__cab"><h2 id="\1" class="hx-painel__titulo">Estado atual<\/h2><\/header>/);
    expect(s).not.toContain("hx-quad");
  });
  it("com onFechar tem o botao quadrado com nome acessivel", () => {
    const s = renderToStaticMarkup(h(PainelHx, { titulo: "Crescer", onFechar: () => {} }));
    expect(s).toContain('<button type="button" class="hx-quad" aria-label="Fechar"><span aria-hidden="true">×</span></button>');
  });
});

describe("AbasHx", () => {
  const abas = [{ id: "a", rotulo: "Treinar" }, { id: "b", rotulo: "Evolução" }, { id: "c", rotulo: "Itens" }];
  it("tablist com a aba escolhida selecionada e a unica na ordem de Tab", () => {
    const s = renderToStaticMarkup(h(AbasHx, { abas, ativa: "b", onMudar: () => {}, rotulo: "Crescer" }));
    expect(s).toContain('role="tablist" aria-label="Crescer"');
    expect(s.match(/role="tab"/g)).toHaveLength(3);
    expect(s).toMatch(/id="hx-aba-b"[^>]*aria-selected="true" tabindex="0"/);
    expect(s.match(/tabindex="-1"/g)).toHaveLength(2);
  });
  it("teclado: setas circulares, Home e End; outra tecla nao navega", () => {
    expect(indiceAbaPorTecla("ArrowRight", 2, 3)).toBe(0);
    expect(indiceAbaPorTecla("ArrowLeft", 0, 3)).toBe(2);
    expect(indiceAbaPorTecla("Home", 2, 3)).toBe(0);
    expect(indiceAbaPorTecla("End", 0, 3)).toBe(2);
    expect(indiceAbaPorTecla("a", 0, 3)).toBeNull();
    expect(indiceAbaPorTecla("ArrowRight", 0, 0)).toBeNull();
  });
});

describe("LinhaHx, botoes e chip", () => {
  it("LinhaHx: <div> sem clique, <button aria-pressed> com clique", () => {
    expect(renderToStaticMarkup(h(LinhaHx, { secundario: "3" }, "Fruta"))).toBe('<div class="hx-linha">Fruta<span class="hx-linha__sec">3</span></div>');
    const b = renderToStaticMarkup(h(LinhaHx, { onClick: () => {}, escolhida: true }, "Fruta"));
    expect(b).toBe('<button type="button" class="hx-linha" aria-pressed="true">Fruta</button>');
  });
  it("BotaoHx e BotaoContinuar sao <button type=button>; o principal diz Continuar por padrao", () => {
    expect(renderToStaticMarkup(h(BotaoHx, { tom: "perigo" }, "Desistir"))).toBe('<button type="button" class="hx-btn hx-btn--perigo">Desistir</button>');
    expect(renderToStaticMarkup(h(BotaoContinuar))).toBe('<button type="button" class="hx-continuar">Continuar</button>');
  });
  it("ChipHx: o tom vira classe, o neutro nao", () => {
    expect(renderToStaticMarkup(h(ChipHx, { tom: "aprendido" }, "Aprendido"))).toBe('<span class="hx-chip hx-chip--aprendido">Aprendido</span>');
    expect(renderToStaticMarkup(h(ChipHx, null, "x"))).toBe('<span class="hx-chip">x</span>');
  });
});

describe("MedidorHx", () => {
  it("role=meter com valor, limites e texto equivalente; a largura segue a razao", () => {
    const s = renderToStaticMarkup(h(MedidorHx, { valor: 30, max: 120, rotulo: "Fome", tom: "alerta" }));
    expect(s).toContain('role="meter" aria-label="Fome" aria-valuemin="0" aria-valuemax="120" aria-valuenow="30" aria-valuetext="30 de 120"');
    expect(s).toContain("hx-medidor--alerta");
    expect(s).toContain("width:25%");
  });
  it("valor fora da faixa e preso nos limites; max invalido levanta erro", () => {
    expect(renderToStaticMarkup(h(MedidorHx, { valor: 500, max: 100, rotulo: "x" }))).toContain('aria-valuenow="100"');
    expect(renderToStaticMarkup(h(MedidorHx, { valor: -4, max: 100, rotulo: "x" }))).toContain('aria-valuenow="0"');
    expect(() => renderToStaticMarkup(h(MedidorHx, { valor: 1, max: 0, rotulo: "x" }))).toThrow();
  });
  it("em porcento o texto e N% (o HUD da tela Pet) e o max tem de ser 100", () => {
    const s = renderToStaticMarkup(h(MedidorHx, { valor: 42, max: 100, rotulo: "comida", porcento: true }));
    expect(s).toContain('aria-valuetext="42%"');
    /* o "%" vai num span proprio (uma pele pode esconde-lo); o texto lido continua "42%" */
    expect(s).toContain('>42<span class="hx-medidor__pct">%</span><');
    expect(() => renderToStaticMarkup(h(MedidorHx, { valor: 2, max: 5, rotulo: "x", porcento: true }))).toThrow();
  });
});

/* M1 do mobile minimo (pet_movel.css): os circulos de acao e o icone do agora, no celular, levam um fundo proprio quase opaco (--hx-miolo por baixo) e
   nao usam desfoque. O icone passa de 3:1 sobre o pior pixel da cena (a grama clara e o branco puro) nas duas peles. */
describe("o celular (mobile minimo): acoes e icone do agora", () => {
  const movelCss = readFileSync(new URL("../src/estilo/pet_movel.css", import.meta.url), "utf8");
  const clara = [[161, 225, 113], [255, 255, 255]] as Rgb[];
  const acaoVidro = (f: Rgb) => sobre(tokenVidro("hx-btn-bg"), sobre(tokenVidro("hx-miolo"), f));
  it("Vidro: o icone da acao e o do agora (--hx-btn-ink, --hx-texto) passam 3:1 sobre o pior pixel", () => {
    for (const f of clara) {
      expect(contraste(tokenVidro("hx-btn-ink"), hex(acaoVidro(f))), `acao ${f}`).toBeGreaterThanOrEqual(3);
      const agora = sobre(tokenVidro("hud-fundo-1").replace("var(--hx-miolo-2)", tokenVidro("hx-miolo-2")), sobre(tokenVidro("hx-miolo"), f));
      expect(contraste(token("hx-texto"), hex(agora)), `agora ${f}`).toBeGreaterThanOrEqual(3);
    }
  });
  it("Militar: o mesmo, com o --hx-btn-bg quase opaco sobre o --hx-miolo", () => {
    for (const f of clara) {
      expect(contraste(token("hx-btn-ink"), hex(sobre("rgba(14,30,22,.92)", sobre(token("hx-miolo"), f))))).toBeGreaterThanOrEqual(3);
      expect(contraste(token("hx-texto"), hex(sobre("rgba(30,33,36,.97)", sobre(token("hx-miolo"), f))))).toBeGreaterThanOrEqual(3);
    }
  });
  it("o CSS poe o --hx-miolo por baixo do --hx-btn-bg, tira o desfoque dos circulos e do agora, e o anel de foco leva o halo escuro", () => {
    expect(movelCss).toMatch(/background:linear-gradient\(var\(--hx-btn-bg\), var\(--hx-btn-bg\)\), linear-gradient\(var\(--hx-miolo\), var\(--hx-miolo\)\)/);
    expect(movelCss).toMatch(/\.mm-acao, \.mm-extra, \.mm-mais \.racao-bt\)\{[^}]*backdrop-filter:none/);
    expect(movelCss).toMatch(/\.mm-agora\{[^}]*backdrop-filter:none/);
    expect(movelCss).toMatch(/:root\[data-pele\] body \.mm-bt:focus-visible\{[^}]*box-shadow:0 0 0 5px var\(--hx-miolo\) !important/);
  });
});

/* os itens trancados do nivel do Tamer (nivel.css; trilho, coluna do celular, minimapa e pecas): apagados por cor de token (--hx-sec), borda tracejada e cadeado, sem opacity no
   conjunto. O texto passa 4,5:1 e o icone 3:1 nas duas peles (o vidro no pior caso, a grama de dia atras) */
describe("itens trancados do nivel do Tamer", () => {
  const nivelCss = readFileSync(new URL("../src/estilo/nivel.css", import.meta.url), "utf8");
  const bloco = (sel: string) => { const i = nivelCss.indexOf(sel); if (i < 0) throw new Error("sem " + sel); return nivelCss.slice(i, nivelCss.indexOf("}", i)); };
  it("o apagado e cor de token, sem opacity, com a borda tracejada", () => {
    for (const sel of [".hx-nav__bt--trancado{", ":root[data-pele] body .mm-coluna .mm-bt--trancado{", ".minimapa-ic.minimapa-marca--trancado{", ".fechado-trancado{"]) {
      const b = bloco(sel);
      expect(b, sel).toContain("color:var(--hx-sec)");
      expect(b, sel).toMatch(/dashed/);
      expect(b, sel).not.toContain("opacity");
    }
  });
  it("Militar: o --hx-sec passa 4,5:1 (texto) e 3:1 (icone) sobre os fundos dos menus", () => {
    for (const f of [token("hx-chao"), token("hx-miolo"), token("hx-miolo-2"), "#0E1E16"]) {
      expect(contraste(token("hx-sec"), f), f).toBeGreaterThanOrEqual(4.5);
      expect(contraste(token("hx-sec"), f), f).toBeGreaterThanOrEqual(3);
    }
    expect(contraste(token("hx-texto-2"), token("hx-miolo"))).toBeGreaterThanOrEqual(4.5);   // o "Nv N" do minimapa
  });
  it("Vidro: o --hx-sec passa 4,5:1 e 3:1 no pior caso do habitat", () => {
    const pior = sobre("rgba(170,225,255,.10)", sobre(tokenVidro("hx-miolo-2"), [161, 225, 113]));
    expect(contraste(tokenVidro("hx-sec"), hex(pior))).toBeGreaterThanOrEqual(4.5);
    expect(contraste(tokenVidro("hx-sec"), hex(pior))).toBeGreaterThanOrEqual(3);
  });
});

/* As peles de rua (docs/PLANO_UX_PELES_RUA.md, 2026-11-20): a pele Estencil, os tokens e a forma do desenho aprovado. A pele e opaca: o
   pior fundo e a propria tinta, sem o habitat por tras. As cores de sentido sao as do :root (o Militar), sem mudanca. */
describe("pele Estencil (os tokens e a forma)", () => {
  const estencilCss = readFileSync(new URL("../src/estilo/pele-estencil.css", import.meta.url), "utf8");
  const mainTsx = readFileSync(new URL("../src/main.tsx", import.meta.url), "utf8");
  const bloco = (() => { const i = tokens.indexOf(':root[data-pele="estencil"]{'); if (i < 0) throw new Error("sem o bloco da estencil"); return tokens.slice(i, tokens.indexOf("}", i)); })();
  const tk = (nome: string) => { const m = bloco.match(new RegExp(`--${nome}:(#[0-9A-Fa-f]{6})`)); if (!m) throw new Error(`token ${nome} da estencil`); return m[1]; };
  const fundos = () => [tk("hx-chao"), tk("hx-miolo"), tk("hx-miolo-2")];

  it("todo texto passa 4,5:1 sobre a tinta, a tinta clara e o chao; o contorno e o foco passam 3:1", () => {
    for (const t of ["hx-texto", "hx-texto-2", "hx-sec", "hx-rotulo"]) for (const f of fundos()) expect(contraste(tk(t), f), `${t} sobre ${f}`).toBeGreaterThanOrEqual(4.5);
    for (const f of fundos()) {
      expect(contraste(tk("hx-borda"), f)).toBeGreaterThanOrEqual(3);
      expect(contraste(tk("hx-borda-topo"), f)).toBeGreaterThanOrEqual(3);
      expect(contraste(tk("hx-foco"), f)).toBeGreaterThanOrEqual(3);
    }
  });
  it("as cores de sentido do :root continuam legiveis sobre a tinta, e nao sao redefinidas", () => {
    for (const t of ["hx-alerta", "hx-perigo", "hx-ok", "hx-necessidade", "hx-aprendido", "hx-sombrio"]) {
      expect(bloco, t).not.toContain(`--${t}:`);
      for (const f of fundos()) expect(contraste(token(t), f), `${t} sobre ${f}`).toBeGreaterThanOrEqual(4.5);
    }
  });
  it("a acao e tinta sobre o vermelhao, o escolhido e tinta sobre o osso, e a necessidade leva a tinta: todos 4,5:1", () => {
    expect(contraste(tk("hx-btn-ink"), tk("hx-btn-bg"))).toBeGreaterThanOrEqual(4.5);
    expect(contraste(tk("hx-btn-ink"), tk("hx-btn-bg-hover"))).toBeGreaterThanOrEqual(4.5);
    expect(contraste(tk("hx-escolhido-ink"), tk("hx-escolhido"))).toBeGreaterThanOrEqual(4.5);
    expect(contraste(tk("hx-escolhido-ink"), token("hx-necessidade"))).toBeGreaterThanOrEqual(4.5);
    /* o vermelhao como letra sobre a tinta (a etiqueta "ativo" do pele-estencil.css) */
    expect(contraste(tk("hx-btn-bg"), tk("hx-miolo"))).toBeGreaterThanOrEqual(4.5);
    expect(contraste(tk("hx-btn-borda"), tk("hx-miolo"))).toBeGreaterThanOrEqual(3);
  });
  it("opaca, sem vidro e sem variante por tema; os cantos cortados saem do chanfro da HUD", () => {
    expect(bloco).not.toContain("data-tema");
    expect(bloco).toMatch(/--hud-desfoque:none/);
    expect(bloco).toMatch(/--hud-fundo-1:#17191F; --hud-fundo-2:#17191F/);
    expect(bloco).toMatch(/--hud-ch:14px; --hud-ch-p:9px/);
    expect(bloco).not.toMatch(/blur\(|rgba\([^)]*\)\s*;\s*--hx-miolo/);
    /* o bloco vem depois do vidro e nao muda o padrao */
    expect(tokens.indexOf(':root[data-pele="estencil"]{')).toBeGreaterThan(tokens.indexOf(':root[data-pele="vidro"]{'));
  });
  it("pele-estencil.css: toda regra sob :root[data-pele=\"estencil\"], sem animacao, importada antes do vidro (que segue por ultimo)", () => {
    const semComentario = estencilCss.replace(/\/\*[\s\S]*?\*\//g, "");
    const seletores = [...semComentario.matchAll(/(?:^|[}{])\s*([^{}@]+?)\s*\{/g)].map((m) => m[1]);
    expect(seletores.length).toBeGreaterThanOrEqual(150);
    /* parte a lista de seletores nas virgulas de fora dos parenteses (ha :is() com :not() dentro) */
    const partes = (sel: string): string[] => {
      const out: string[] = []; let fundo = 0, ini = 0;
      for (let i = 0; i < sel.length; i++) {
        if (sel[i] === "(") fundo++; else if (sel[i] === ")") fundo--;
        else if (sel[i] === "," && fundo === 0) { out.push(sel.slice(ini, i)); ini = i + 1; }
      }
      return [...out, sel.slice(ini)];
    };
    for (const sel of seletores) for (const parte of partes(sel)) expect(parte.trim(), sel).toMatch(/^:root\[data-pele="estencil"\]/);
    expect(semComentario).not.toMatch(/animation|transition/);
    expect(semComentario).not.toMatch(/#[0-9A-Fa-f]{3,8}\b/);
    const imports = [...mainTsx.matchAll(/^import "\.\/estilo\/([^"]+)";/gm)].map((m) => m[1]);
    expect(imports.at(-1)).toBe("pele-vidro.css");
    expect(imports.at(-2)).toBe("pele-estencil.css");
    /* o texto da acao fora do botao: os dois lugares do jogo que o usam sobre fundo escuro estao cobertos */
    expect(semComentario).toContain(".dl-tag--ativo{ color:var(--hx-btn-bg) }");
    expect(semComentario).toContain(".res-faixa--vit{ background-color:var(--hx-btn-bg); color:var(--hx-btn-ink) }");
  });
  it("a letra vazada: Saira Stencil One carregada no index.html e usada so pelo token --hx-f-tit", () => {
    expect(html).toContain("family=Saira+Stencil+One");
    expect(bloco).toContain('--hx-f-tit:"Saira Stencil One", "Saira Condensed"');
    expect(estencilCss).not.toContain("Saira");
    expect(estencilCss).toContain("var(--hx-f-tit)");
    /* a sombra dura e os segmentos das barras tambem sao tokens da pele */
    expect(bloco).toMatch(/--hx-sombra-cor:#000000/);
    expect(bloco).toMatch(/--hx-mascara:repeating-linear-gradient\(90deg, #000 0 9px, transparent 9px 12px\)/);
  });
  it("a caixa do desenho: o contorno no ::before, o miolo no ::after e a sombra dura na peca; nada de fora alem dos tracos embutidos", () => {
    const s = estencilCss.replace(/\/\*[\s\S]*?\*\//g, "");
    expect(s).toMatch(/\.topo-bits\)::before,[^{]*\{[^}]*background:var\(--hx-borda\);\s*clip-path:polygon\(/);
    expect(s).toMatch(/\.topo-bits\)::after,[^{]*\{[^}]*background:var\(--hx-miolo\);\s*clip-path:polygon\(/);
    expect(s).toMatch(/filter:drop-shadow\(5px 5px 0 var\(--hx-sombra-cor\)\)/);
    /* o indice das janelas e a ordem delas na pilha (um contador), e o aviso muda de cor quando o pet pede algo */
    expect(s).toContain("counter(es-janela, decimal-leading-zero)");
    expect(s).toContain(".pet-prioridade[data-pede]::after{ background:var(--hx-necessidade) }");
    /* nenhum arquivo de fora: so os tracos embutidos (svg em data:) */
    expect(s).not.toMatch(/url\((?!"data:image\/svg\+xml,)/);
    expect(s).not.toMatch(/https?:\/\/(?!www\.w3\.org\/2000\/svg)/);
  });
  it("os icones em traco: cada acao e cada exercicio da lista existe no jogo, e as telas poem o gancho que a pele le", () => {
    const telaPet = readFileSync(new URL("../src/telas/pet/TelaPet.tsx", import.meta.url), "utf8");
    const telaTreinar = readFileSync(new URL("../src/telas/crescer/TelaTreinar.tsx", import.meta.url), "utf8");
    const acoes = [...new Set([...estencilCss.matchAll(/\[data-acao="([a-z_]+)"\]\{ --es-ic:url\("data:image\/svg\+xml,/g)].map((m) => m[1]))];
    const exs = [...new Set([...estencilCss.matchAll(/\[data-ex="([a-z_]+)"\]\{ --es-ic:url\("data:image\/svg\+xml,/g)].map((m) => m[1]))];
    const dock = telaPet.match(/const ORDEM_DOCK: AcaoDono\[\] = \[([^\]]+)\]/);
    if (!dock) throw new Error("sem a ORDEM_DOCK na TelaPet");
    expect(acoes.sort()).toEqual(dock[1].split(",").map((x) => x.trim().replace(/"/g, "")).sort());
    expect(exs.sort()).toEqual(Object.keys(CTR.exercicios).sort());
    expect(telaPet).toContain("className={`hx-btn dock-bt ${cls}`} data-acao={a}");
    expect(telaPet).toContain('className="pet-prioridade" data-pede={r.emote || r.acao ? "" : undefined} data-acao={r.acao ?? undefined}');
    expect(telaTreinar).toContain('data-ex={ex} disabled={des}');
    /* a linha do dono no Registro e o "%" das necessidades (que a pele esconde) tambem sao ganchos */
    expect(readFileSync(new URL("../src/telas/diario/TelaRegistro.tsx", import.meta.url), "utf8")).toContain("data-tipo={TIPO_REG[h.quem][0]}");
    expect(readFileSync(new URL("../src/componentes/hx/MedidorHx.tsx", import.meta.url), "utf8")).toContain('<span className="hx-medidor__pct">%</span>');
    expect(estencilCss).toContain('.rg2-linha[data-tipo="voce"]');
    expect(estencilCss).toContain(".hx-medidor__pct{ display:none }");
  });
});
