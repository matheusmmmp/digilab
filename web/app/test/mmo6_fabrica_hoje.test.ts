/* MMO6: a Fabrica de hoje sai byte a byte igual ao gabarito gravado antes das sementes vindas de fora (test/gabaritos/mmo6_fabrica_hoje.json,
   por test/gerar_gabarito_mmo6.ts). Sem a chave (sem as sementes de fora), nada muda: os alugados, os rivais, as sementes e cada luta. */
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { LUTAS_MAX, TENTATIVAS_HOJE, jogarHoje, type TentativaHoje } from "./mmo6_fabrica_hoje.ts";

const gab = JSON.parse(readFileSync(new URL("./gabaritos/mmo6_fabrica_hoje.json", import.meta.url), "utf8")) as
  { versao: number; lutasMax: number; tentativas: number[][]; vidas: TentativaHoje[] };

describe("MMO6: a Fabrica de hoje sai igual ao gabarito gravado antes da mudanca", () => {
  test("a forma do gabarito", () => {
    expect(gab.versao).toBe(1);
    expect(gab.lutasMax).toBe(LUTAS_MAX);
    expect(gab.tentativas).toEqual(TENTATIVAS_HOJE.map(x => [...x]));
    expect(gab.vidas.map(v => [v.n, v.escolha, v.ritmo])).toEqual(gab.tentativas);
    /* o gabarito cobre a vitoria, a derrota e a troca */
    const lutas = gab.vidas.flatMap(v => v.lutas);
    expect(lutas.some(l => l.venceu)).toBe(true);
    expect(lutas.some(l => !l.venceu)).toBe(true);
    expect(lutas.some(l => l.trocou)).toBe(true);
  });
  for (const [n, e, r] of TENTATIVAS_HOJE) {
    test(`a tentativa ${n} (alugado ${e}, troca a cada ${r}): as sementes, os alugados, os rivais e cada luta`, () => {
      expect(jogarHoje(n, e, r)).toEqual(gab.vidas.find(v => v.n === n));
    });
  }
});
