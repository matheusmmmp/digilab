/* A vista do mundo dos pets v12 (src/telas/pet/vistaMundo.ts; docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2): a janela da camera presa no
   mapa, os lugares nomeados do caminho acessivel (MV-4) dentro do mapa e aceitos pelo motor, a regiao com o artigo e o seguidor (a
   interpolacao) que vai ate a posicao do motor sem nunca escrever nele */
import { describe, expect, test } from "vitest";
import { CMU_MVP, Motor } from "../motor/index.ts";
import { JANELA_CELULAS, Seguidor, dentroDoMapa, janelaEm, lugaresNomeados, naRegiao } from "../src/telas/pet/vistaMundo.ts";

const cm = CMU_MVP, W = cm.celulas_x * cm.sub, H = cm.celulas_y * cm.sub;

describe("a vista do mundo", () => {
  test("a janela tem 16 x 12 celulas e fica presa no mapa", () => {
    for (const c of [[0, 0], [W - 1, H - 1], [W / 2, H / 2], [10, H - 1], [W - 1, 5]] as const) {
      const j = janelaEm(cm, c);
      expect([j.w, j.h]).toEqual([JANELA_CELULAS[0] * cm.sub, JANELA_CELULAS[1] * cm.sub]);
      expect(j.x0).toBeGreaterThanOrEqual(0); expect(j.y0).toBeGreaterThanOrEqual(0);
      expect(j.x0 + j.w).toBeLessThanOrEqual(W); expect(j.y0 + j.h).toBeLessThanOrEqual(H);
    }
    expect(janelaEm(cm, [0, 0])).toMatchObject({ x0: 0, y0: 0 });
    expect(janelaEm(cm, [W - 1, H - 1])).toMatchObject({ x0: W - 16 * cm.sub, y0: H - 12 * cm.sub });
  });
  test("dentro do mapa: so subunidades inteiras de 0 a W-1 e de 0 a H-1", () => {
    expect(dentroDoMapa(cm, 0, 0)).toBe(true);
    expect(dentroDoMapa(cm, W - 1, H - 1)).toBe(true);
    for (const [x, y] of [[-1, 0], [0, -1], [W, 0], [0, H], [1.5, 2], [Number.NaN, 0]]) expect(dentroDoMapa(cm, x, y)).toBe(false);
  });
  test("os lugares nomeados: o comedouro do mapa, perto (2 celulas a leste) e longe (20 para o lado com mais espaco), dentro do mapa", () => {
    const comedouro: [number, number] = [168, 248];
    const oeste = lugaresNomeados({ pet: [100, 200], comedouro, cm });
    expect(oeste.comedouro).toEqual(comedouro);
    expect(oeste.perto).toEqual([100 + cm.perto_max_celulas * cm.sub, 200]);
    expect(oeste.longe).toEqual([100 + cm.longe_min_celulas * cm.sub, 200]);
    const leste = lugaresNomeados({ pet: [W - 100, 200], comedouro, cm });
    expect(leste.longe).toEqual([W - 100 - cm.longe_min_celulas * cm.sub, 200]);
    /* na borda: o deslocar do motor prende no mapa */
    const borda = lugaresNomeados({ pet: [W - 1, H - 1], comedouro, cm });
    for (const p of Object.values(borda)) expect(dentroDoMapa(cm, p[0], p[1])).toBe(true);
  });
  test("num pet v12 de verdade os tres lugares sao aceitos pelo motor e entram no registro como o evento dc", () => {
    const m = new Motor(6503, 12);
    m.avancar(120);
    const lugares = lugaresNomeados(m.mundo!);
    for (const [x, y] of Object.values(lugares)) m.deixarComida("racao", x, y);
    expect(m.log.filter(e => e[1] === "dc").map(e => e[2])).toEqual(Object.values(lugares).map(([x, y]) => ({ tipo: "racao", x, y })));
    /* o motor falha alto fora do mapa: a tela confere antes (dentroDoMapa) */
    expect(() => m.deixarComida("racao", W, 0)).toThrow();
  });
  test("a regiao com o artigo: na casa, no jardim, no campo, na mata", () => {
    expect(cm.layout.regioes.map(([, c0]) => naRegiao(cm, c0 * cm.sub))).toEqual(["na casa", "no jardim", "no campo", "na mata"]);
  });
  test("o seguidor: salta na primeira vez e quando a distancia passa de 8 celulas; senao vai ate o alvo sem passar dele", () => {
    const s = new Seguidor();
    expect(s.seguir([100, 100], 0, cm)).toEqual([100, 100]);
    const a = s.seguir([132, 100], 120, cm);
    expect(a[0]).toBeGreaterThan(100); expect(a[0]).toBeLessThan(132);
    for (let i = 0; i < 60; i++) s.seguir([132, 100], 120, cm);
    expect(s.pos).toEqual([132, 100]);
    expect(s.seguir([132 + 9 * cm.sub, 100], 120, cm)).toEqual([132 + 9 * cm.sub, 100]);
    /* sem tempo (o relogio parado), fica onde esta ate um alvo perto */
    expect(s.seguir([132 + 9 * cm.sub + 16, 100], 0, cm)).toEqual([132 + 9 * cm.sub, 100]);
  });
});
