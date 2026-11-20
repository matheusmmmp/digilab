// O gabarito da N3 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 4): com as chaves forcaAtr, tiroDoMorto, puloMax e
// bordaRingue desligadas, as lutas das 3 tabelas que as versoes vivas usam saem byte a byte iguais ao gabarito gravado antes das chaves
// (scripts/arena_gabarito_n3.ts, num commit proprio); e cada versao viva segue na tabela de antes.
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { VERSOES_PET } from "../motor/constantes.ts";
import { tabelaLuta } from "../motor/luta_poc.ts";
import { resumoLutaLp6 } from "./arena_lp6_lutas.ts";
import { lutasDoGabaritoN3 } from "./luta_nucleo_n3_lutas.ts";

const gab = JSON.parse(readFileSync(new URL("./gabaritos/luta_nucleo_n3.json", import.meta.url), "utf8")) as { versoes: Record<string, number>; lutas: { id: string; sha: string }[] };

describe("o gabarito da N3, com as chaves desligadas", () => {
  test("cada versao viva luta pela mesma tabela de antes (a v21, a v23 ou a v29)", () => {
    expect(Object.fromEntries(VERSOES_PET.map(v => [String(v), tabelaLuta(v).versao]))).toEqual(gab.versoes);
  });
  test("as 576 lutas das tabelas v21, v23 e v29 saem byte a byte iguais", () => {
    const lutas = lutasDoGabaritoN3();
    expect(lutas.map(l => l.id)).toEqual(gab.lutas.map(l => l.id));
    expect(lutas.length).toBe(576);
    for (let i = 0; i < lutas.length; i++) expect({ id: lutas[i].id, ...resumoLutaLp6(lutas[i].entrada) }, lutas[i].id).toEqual(gab.lutas[i]);
  });
});
