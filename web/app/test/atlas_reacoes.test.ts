// As reacoes de rosto no atlas de clipes (docs/TAREFA_V3_SPRITES_REACOES.md, R-rosto-jogo): ao contrario das acoes de CLIPES_ACOES, elas existem so nos
// Digimon do estagio crianca. A regra do juntarClipes e por forma: ou as 7, ou nenhuma; uma forma com so parte delas e erro, e uma forma sem elas
// ao lado de uma que tem NAO e. Atlas sintetico de arte propria (so numeros, sem PNG da Bandai).
import { expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CLIPES_REACOES, juntarClipes, type AtlasClipes, type AtlasUp } from "../src/atlas.ts";

const base: AtlasUp = { atlas: "a.png", ms_por_quadro: 120, sprites: {}, pecas: {} };
const sintetico = JSON.parse(readFileSync(new URL("./atlas_acoes_sintetico.json", import.meta.url), "utf8")) as AtlasClipes;
const comReacoes = (): AtlasClipes => {
  const c = structuredClone(sintetico);
  for (const r of CLIPES_REACOES) c.sprites.forma_a.clipes[r] = { quadros: [[0, 0, 4, 4, 1, 6]], ms: [1000], loop: true };
  return c;
};

test("as reacoes de rosto: as 7 do estagio crianca", () => {
  expect([...CLIPES_REACOES]).toEqual(["Triste", "Cansado", "Carinho", "Medo", "Envergonhado", "Recusa", "Doente"]);
});

test("passa: as 7 reacoes numa forma e nenhuma na outra (opcional por forma)", () => {
  const j = juntarClipes(base, comReacoes());
  expect(j.sprites.forma_a.clipes?.Triste?.ms).toEqual([1000]);
  expect(j.sprites.forma_b.clipes?.Triste).toBeUndefined();
});

test("passa: nenhuma forma com as reacoes (o atlas de antes)", () => {
  expect(() => juntarClipes(base, sintetico)).not.toThrow();
});

test("falha alto: uma forma com so parte das reacoes", () => {
  const c = comReacoes(); delete c.sprites.forma_a.clipes.Doente; delete c.sprites.forma_a.clipes.Medo;
  expect(() => juntarClipes(base, c)).toThrow(/forma_a tem so parte das reacoes de rosto, faltam Medo, Doente/);
});

test("falha alto: a reacao com duracao que nao casa com os quadros (a regra de sempre vale para ela)", () => {
  const c = comReacoes(); c.sprites.forma_a.clipes.Triste!.ms = [1000, 1000];
  expect(() => juntarClipes(base, c)).toThrow(/clipe Triste de forma_a sem quadros ou com duracao invalida/);
});
