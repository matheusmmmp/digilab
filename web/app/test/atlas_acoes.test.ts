// As acoes novas no atlas de clipes (docs/TAREFA_V3_SPRITES_ACOES.md, secao 3.4; missao M2): o Comer e o Comer_objeto entram pelo juntarClipes,
// que falha alto quando o objeto nao casa com o clipe dele, quando vem sem ele e quando uma forma tem a acao e outra nao. Atlas sintetico de
// arte propria, versionado (so numeros, sem PNG da Bandai).
import { expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CLIPES_ACOES, juntarClipes, type AtlasClipes, type AtlasUp } from "../src/atlas.ts";

const acoes = JSON.parse(readFileSync(new URL("./atlas_acoes_sintetico.json", import.meta.url), "utf8")) as AtlasClipes;
const base: AtlasUp = { atlas: "a.png", ms_por_quadro: 120, sprites: {}, pecas: {} };
const copia = (): AtlasClipes => structuredClone(acoes);

test("as acoes do atlas: Comer, Comer_objeto e as quatro do lote 1", () => {
  expect([...CLIPES_ACOES]).toEqual(["Comer", "Comer_objeto", "Feliz", "Sacudir", "Chamar", "Emburrar"]);
});

test("passa: todas as formas com o Comer e o objeto casando; NPCs e bots sem as acoes", () => {
  const j = juntarClipes(base, acoes);
  expect(j.sprites.forma_a.clipes?.Comer?.loop).toBe(true);
  expect(j.sprites.forma_a.clipes?.Comer_objeto?.ms).toEqual([133, 100, 67]);
  expect(j.sprites.forma_b.clipes?.Comer_objeto?.quadros.length).toBe(2);
  expect(j.sprites.npc_sintetico.clipes?.Comer).toBeUndefined();
  expect(j.sprites.bot_sintetico.clipes?.Comer).toBeUndefined();
});

test("passa: nenhuma forma com as acoes (o atlas de hoje)", () => {
  const c = copia();
  for (const s of Object.values(c.sprites)) { delete s.clipes.Comer; delete s.clipes.Comer_objeto; }
  expect(() => juntarClipes(base, c)).not.toThrow();
});

test("passa: o Comer sem objeto em todas as formas", () => {
  const c = copia();
  for (const s of Object.values(c.sprites)) delete s.clipes.Comer_objeto;
  expect(juntarClipes(base, c).sprites.forma_a.clipes?.Comer?.ms).toEqual([133, 100, 67]);
});

test("falha alto: o objeto com ms diferentes do clipe dele", () => {
  const c = copia(); c.sprites.forma_a.clipes.Comer_objeto!.ms[1] = 101;
  expect(() => juntarClipes(base, c)).toThrow(/Comer_objeto de forma_a nao casa com o clipe dele em quadros e ms/);
});

test("falha alto: o objeto com outro numero de quadros", () => {
  const c = copia(), o = c.sprites.forma_b.clipes.Comer_objeto!;
  o.quadros.push([0, 0, 0, 0, 0, 0]); o.ms.push(150);
  expect(() => juntarClipes(base, c)).toThrow(/Comer_objeto de forma_b nao casa/);
});

test("falha alto: o objeto sem o clipe base", () => {
  const c = copia(); delete c.sprites.forma_a.clipes.Comer; delete c.sprites.forma_b.clipes.Comer;
  expect(() => juntarClipes(base, c)).toThrow(/Comer_objeto de forma_a sem o clipe Comer/);
});

test("falha alto: a acao numa forma e nao em outra", () => {
  const c = copia(); delete c.sprites.forma_b.clipes.Comer; delete c.sprites.forma_b.clipes.Comer_objeto;
  expect(() => juntarClipes(base, c)).toThrow(/a acao Comer existe em 1 formas e falta em 1: forma_b/);
  const o = copia(); delete o.sprites.forma_a.clipes.Comer_objeto;
  expect(() => juntarClipes(base, o)).toThrow(/a acao Comer_objeto existe em 1 formas e falta em 1: forma_a/);
});

test("falha alto: o clipe novo com duracao que nao casa com os quadros (a regra de sempre vale para ele)", () => {
  const c = copia(); c.sprites.forma_a.clipes.Comer!.ms = [133, 100];
  expect(() => juntarClipes(base, c)).toThrow(/clipe Comer de forma_a sem quadros ou com duracao invalida/);
});
