// O gabarito da LP6-1 (docs/PLANO_LP6_SEGUNDO_GOLPE.md): com as chaves do golpe de apoio e da arena por estagio desligadas, a luta do
// nucleo sai byte a byte igual a de antes da LP6 (a v21 e a v23). O gabarito foi gravado por scripts/arena_gabarito_lp6.ts num commit
// proprio, antes da mudanca; cada luta e o sha256 dos eventos e do estado final.
import { expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { lutasDoGabaritoLp6, resumoLutaLp6 } from "./arena_lp6_lutas.ts";

const gab = JSON.parse(readFileSync(new URL("./gabaritos/arena_lp6_v23.json", import.meta.url), "utf8")) as { lutas: { id: string; sha: string }[] };

test("as chaves da LP6 desligadas: as 384 lutas da v21 e da v23 saem byte a byte iguais ao gabarito de antes da LP6", () => {
  const lutas = lutasDoGabaritoLp6();
  expect(lutas.map(l => l.id)).toEqual(gab.lutas.map(l => l.id));
  expect(lutas.length).toBe(384);
  for (let i = 0; i < lutas.length; i++) {
    const r = resumoLutaLp6(lutas[i].entrada);
    expect({ id: lutas[i].id, ...r }, lutas[i].id).toEqual(gab.lutas[i]);
  }
});
