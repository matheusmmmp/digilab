// O enquadre do pet no cartao da evolucao (Revelacao.tsx, PetGrande). O defeito de 2026-11-11: com a chave CLIPES_UP a caixa do sprite passou
// a ser a comum a todos os clipes, o canvas do PetGrande seguiu sendo essa caixa e o corpo parado ficou fora do meio do anel e da plataforma
// (o Koromon 19,5 px da caixa para a direita, o Gallantmon 36 para a esquerda, antes da escala). O canvas agora e a caixa do Idle.
import { expect, test } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { caixaIdle, enquadrarIdle, juntarClipes, type AtlasClipes, type AtlasUp, type SpriteUp } from "../src/atlas.ts";

const ler = (caminho: string): string => readFileSync(new URL(caminho, import.meta.url), "utf8");
/* o corpo parado no canto de baixo e a direita de uma caixa bem maior (o golpe estica a caixa para a esquerda e para cima) */
const FORA_DO_MEIO: SpriteUp = { caixa: [113, 92], quadros: [[0, 0, 42, 37, 55, 41], [50, 0, 40, 39, 56, 39], [0, 0, 0, 0, 0, 0]] };

/** onde cada quadro desenhavel cai no canvas, como o desenharSprite faz: [esquerda, topo, direita, base] */
function quadrosNoCanvas(s: SpriteUp, e: { esc: number; x: number; y: number }): [number, number, number, number][] {
  return s.quadros.filter(q => q[2] > 0).map(q => [e.x + q[4] * e.esc, e.y + q[5] * e.esc, e.x + (q[4] + q[2]) * e.esc, e.y + (q[5] + q[3]) * e.esc]);
}
function conferir(s: SpriteUp, alvo: [number, number], maxEscala: number, rotulo: string): void {
  const e = enquadrarIdle(s, alvo, maxEscala), qs = quadrosNoCanvas(s, e);
  expect(Number.isInteger(e.esc) && e.esc >= 1 && e.esc <= maxEscala, rotulo + ": escala inteira").toBe(true);
  /* a caixa do Idle fica a 1 px (de sprite) de cada borda do canvas: o meio do corpo no meio, o pe na base */
  expect(Math.min(...qs.map(q => q[0])), rotulo + ": esquerda").toBe(e.esc);
  expect(Math.max(...qs.map(q => q[2])), rotulo + ": direita").toBe(e.w - e.esc);
  expect(Math.min(...qs.map(q => q[1])), rotulo + ": topo").toBe(e.esc);
  expect(Math.max(...qs.map(q => q[3])), rotulo + ": pe na base").toBe(e.h - e.esc);
  if (e.esc > 1) expect(e.w <= alvo[0] && e.h <= alvo[1], rotulo + ": cabe no alvo").toBe(true);
}

test("caixaIdle: o retangulo que os quadros do Idle ocupam juntos, sem o quadro vazio", () => {
  expect(caixaIdle(FORA_DO_MEIO)).toEqual([55, 39, 42, 39]);
  expect(caixaIdle({ caixa: [8, 6], quadros: [[0, 0, 0, 0, 0, 0]] })).toEqual([0, 0, 8, 6]);
});

test("enquadrarIdle: o corpo fora do meio da caixa fica no meio do canvas e com o pe na base", () => {
  const e = enquadrarIdle(FORA_DO_MEIO, [340, 300], 6);
  expect(e).toEqual({ esc: 6, w: 264, h: 246, x: -324, y: -228 });
  conferir(FORA_DO_MEIO, [340, 300], 6, "desktop");
  conferir(FORA_DO_MEIO, [250, 220], 6, "celular");
  conferir(FORA_DO_MEIO, [56, 56], 2, "mini");
  /* o defeito: pela caixa do sprite a escala caia para 2 e o meio do corpo ficava 19,5 px de sprite a direita do meio do canvas */
  const [cx, , cw] = caixaIdle(FORA_DO_MEIO);
  expect(cx + cw / 2 - FORA_DO_MEIO.caixa[0] / 2).toBe(19.5);
});

test("o PetGrande enquadra pela caixa do Idle, nunca pela caixa do sprite", () => {
  const fonte = ler("../src/componentes/Revelacao.tsx"), pet = fonte.slice(fonte.indexOf("export function PetGrande"), fonte.indexOf("function Mini"));
  expect(pet).toContain("enquadrarIdle(sp, alvo, maxEscala)");
  expect(pet).not.toContain("sp.caixa");
});

test("o brilho atras do anel entra como mascara pela luminancia, nunca como imagem (a peca tem fundo preto opaco)", () => {
  const fonte = ler("../src/componentes/Revelacao.tsx"), css = ler("../src/estilo/evolucao.css");
  expect(fonte).not.toMatch(/<Deco nome="UI_Fx_Glow_Circle_01"/);
  const regra = css.match(/\.evm-glow\{[^}]*\}/)?.[0] ?? "";
  expect(regra).toContain("mask:var(--evm-glow)");
  expect(regra).toContain("mask-mode:luminance");
  expect(regra).toContain("display:none");
  expect(css).toContain("@supports (mask-mode:luminance){ .evm-glow{display:block} }");
});

test("o pe do pet segue o meio da plataforma pelas mesmas variaveis dela, sem margem solta", () => {
  const css = ler("../src/estilo/evolucao.css");
  expect(css).toContain(".evm-pet{position:relative;z-index:1;margin-bottom:calc(var(--evm-plat-base) + var(--evm-plat-alt) / 2);");
  expect(css.match(/\.evm-plataforma\{[^}]*\}/)?.[0]).toContain("bottom:var(--evm-plat-base);width:260px;height:var(--evm-plat-alt)");
  /* a partir de 900 px a plataforma cresce pela variavel, nunca por uma altura a parte */
  expect(css).not.toMatch(/\.evm-plataforma\{[^}]*height:\d/);
});

/* o atlas de verdade (fora do git): todas as formas, nos tres alvos da tela. Pula com aviso sem o Assets (CI, outra maquina) */
const ASSETS = new URL("../../../../Assets/", import.meta.url);
const CLIPES = new URL("digilab_atlas_up_clipes.json", ASSETS), BASE = new URL("digilab_atlas_up.json", ASSETS);
const tem = existsSync(CLIPES) && existsSync(BASE);
if (!tem) console.warn("evolucao_enquadre: sem o Assets, teste do atlas real pulado");

test.skipIf(!tem)("no atlas real, toda forma fica no meio e com o pe na base, do In-Training ao Mega", () => {
  const j = juntarClipes(JSON.parse(readFileSync(BASE, "utf8")) as AtlasUp, JSON.parse(readFileSync(CLIPES, "utf8")) as AtlasClipes);
  const formas = Object.keys(j.sprites).filter(k => j.sprites[k].clipes && !k.startsWith("npc_") && !k.startsWith("bot_"));
  expect(formas.length).toBe(60);
  let fora = 0;
  for (const k of formas) {
    const s = j.sprites[k], [cx, , cw] = caixaIdle(s);
    for (const [alvo, max] of [[[340, 300], 6], [[250, 220], 6], [[56, 56], 2]] as [[number, number], number][]) conferir(s, alvo, max, k);
    if (Math.abs(cx + cw / 2 - s.caixa[0] / 2) >= 2) fora++;
  }
  /* a prova de que a caixa do sprite nao serve de enquadre: na maioria das formas o corpo esta a 2 px ou mais do meio dela */
  expect(fora).toBeGreaterThan(30);
});
