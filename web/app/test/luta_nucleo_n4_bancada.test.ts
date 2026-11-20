// A N4 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 8): a bancada leva as chaves da N3 do candidato para a luta (comum.ts
// lutar) e para a vida do Motor (o nucleoLutaPoc, so a bancada o poe). Desligadas, a luta e a de antes; ligadas, a mesma luta do nucleo com
// a chave na entrada. Nenhuma versao de pet as liga (D-N-7).
import { describe, expect, test } from "vitest";
import { Motor, VERSAO_V23, lutarNucleoPoc, sorteiosPoc } from "../motor/index.ts";
import { extrasLp6, lutar, nucleoDe, rivalCanonico } from "../scripts/equilibrio_poc/comum.ts";
import { CANDIDATOS, LP5_3, LP6_3_U120, N4, candidatoDe } from "../scripts/equilibrio_poc/candidatos.ts";
import { motorDoCandidato } from "../scripts/equilibrio_poc/bancada.ts";

const A = { forma: "brasa_crianca_sereno", stats: rivalCanonico(LP5_3, "brasa_crianca_sereno") };
const B = { forma: "brasa_crianca_arisco", stats: rivalCanonico(LP5_3, "brasa_crianca_arisco") };

describe("as chaves da N3 no candidato da bancada", () => {
  test("os candidatos de antes tem as 4 desligadas", () => {
    for (const k of ["v21", "lp5_3", "lp6_3_u120"]) { expect(nucleoDe(CANDIDATOS[k])).toBeUndefined(); expect(extrasLp6(CANDIDATOS[k]).nucleo).toBeUndefined(); }
  });
  test("os candidatos da N4 levam so as chaves deles", () => {
    expect(nucleoDe(N4.n4_atr115)).toEqual({ forcaAtr: 1.15 });
    expect(nucleoDe(N4.n4_morto)).toEqual({ tiroDoMorto: true });
    expect(nucleoDe(N4.n4_pulo)).toEqual({ puloMax: 75 });
    expect(nucleoDe(N4.n4_borda)).toEqual({ bordaRingue: .9 });
    expect(nucleoDe(N4.n4_juntas_v29)).toEqual({ forcaAtr: 1.15, tiroDoMorto: true, puloMax: 75, bordaRingue: .9 });
    /* fora das chaves, o n4 e o lp5_3 (e o n4_juntas_v29, o lp6_3_u120) */
    const { nome: _a, nucleo: _b, ...resto } = N4.n4_atr115, { nome: _c, nucleo: _d, ...base } = LP5_3;
    expect(resto).toEqual(base);
    const { nome: _e, nucleo: _f, ...r29 } = N4.n4_juntas_v29, { nome: _g, nucleo: _h, ...b29 } = LP6_3_U120;
    expect(r29).toEqual(b29);
  });
  test("a luta da bancada leva a chave como o nucleo", () => {
    const tiro = { ...LP5_3.tiro }, s = 101;
    const r = lutar("campo", s, A, B, tiro, undefined, extrasLp6(N4.n4_atr100));
    const n = lutarNucleoPoc({ cena: "campo", semente: s, a: A, b: B, tiro, forcaAtr: 1 }, sorteiosPoc(s));
    expect(r).toEqual({ vencedor: n.vencedor, fim: n.fim, relogio: n.relogio, vidaA: n.vidaA });
  });
  test("fora da faixa, o candidato falha alto", () => {
    expect(() => candidatoDe({ nome: "x", nucleo: { forcaAtr: .5 } })).toThrow(/vantagem do atributo/);
    expect(() => candidatoDe({ nome: "x", nucleo: { puloMax: 5 } })).toThrow(/teto do pulo/);
    expect(() => candidatoDe({ nome: "x", nucleo: { bordaRingue: 2 } })).toThrow(/borda do Ringue/);
    expect(() => candidatoDe({ nome: "x", nucleo: { tiroDoMorto: 2 } })).toThrow(/tiroDoMorto/);
  });
  test("a vida do Motor: so a bancada poe as chaves; o Motor do jogo fica sem elas", () => {
    expect(new Motor(11, VERSAO_V23).nucleoLutaPoc).toBeNull();
    expect(motorDoCandidato(LP5_3, 11).nucleoLutaPoc).toBeNull();
    expect(motorDoCandidato(N4.n4_juntas_v23, 11).nucleoLutaPoc).toEqual({ forcaAtr: 1.15, tiroDoMorto: true, puloMax: 75, bordaRingue: .9 });
  });
});
