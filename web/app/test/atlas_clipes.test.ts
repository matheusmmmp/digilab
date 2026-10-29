// Clipes do UP no atlas (TAREFA_V2_UP_ATLAS): o quadro certo para um tempo dado e a juncao com o atlas atual, com um JSON sintetico
// versionado (sem PNG da Bandai).
import { expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { juntarClipes, quadroDoClipe, type AtlasClipes, type AtlasUp } from "../src/atlas.ts";

const clipes = JSON.parse(readFileSync(new URL("./atlas_clipes_sintetico.json", import.meta.url), "utf8")) as AtlasClipes;
const base: AtlasUp = { atlas: "a.png", ms_por_quadro: 120, sprites: { forma_a: { caixa: [1, 1], quadros: [[0, 0, 1, 1, 0, 0]] }, oraculo: { caixa: [2, 2], quadros: [[0, 0, 1, 1, 0, 0]] } }, pecas: {} };

test("quadroDoClipe: pela soma das duracoes, repetindo no loop", () => {
  const ms = clipes.sprites.forma_a.clipes.Idle!.ms;           /* 100, 50, 200 = 350 */
  const q = (t: number) => quadroDoClipe(ms, true, t);
  expect([0, 99, 100, 149, 150, 349].map(q)).toEqual([0, 0, 1, 1, 2, 2]);
  expect([350, 449, 450, 699, 700].map(q)).toEqual([0, 0, 1, 2, 0]);
});

test("quadroDoClipe: sem loop segura o ultimo quadro", () => {
  const ms = clipes.sprites.forma_a.clipes.Die!.ms;            /* 300, 100 */
  expect([0, 299, 300, 399, 400, 99999].map(t => quadroDoClipe(ms, false, t))).toEqual([0, 0, 1, 1, 1, 1]);
});

test("juntarClipes: troca o sprite do atlas de clipes, o Idle vira `quadros`, o resto fica", () => {
  const j = juntarClipes(base, clipes);
  expect(j.sprites.forma_a.caixa).toEqual([20, 10]);
  expect(j.sprites.forma_a.quadros).toBe(clipes.sprites.forma_a.clipes.Idle!.quadros);
  expect(j.sprites.forma_a.clipes?.Die?.loop).toBe(false);
  expect(j.sprites.oraculo).toBe(base.sprites.oraculo);
  expect(base.sprites.forma_a.clipes).toBeUndefined();         /* o atlas atual nao e alterado */
});

test("juntarClipes: falha alto sem Idle ou com duracao que nao casa", () => {
  const semIdle = structuredClone(clipes); delete semIdle.sprites.forma_a.clipes.Idle;
  expect(() => juntarClipes(base, semIdle)).toThrow(/sem Idle/);
  const ruim = structuredClone(clipes); ruim.sprites.forma_a.clipes.Die!.ms = [300];
  expect(() => juntarClipes(base, ruim)).toThrow(/duracao invalida/);
  const zero = structuredClone(clipes); zero.sprites.forma_a.clipes.Idle!.ms[0] = 0;
  expect(() => juntarClipes(base, zero)).toThrow(/duracao invalida/);
});
