/* LUTA_POC, LP6-3 (docs/PLANO_LP6_SEGUNDO_GOLPE.md, secao 5; o adendo da LP6-3 no docs/PLANO_EQUILIBRIO_LUTA_POC.md): as chaves da LP6-1 na
   bancada. Desligadas, nada entra na luta (a de sempre); ligadas, a luta da bancada e a do nucleo com as mesmas entradas; o Motor da
   bancada as recebe pelas entradas opcionais; e a regra do ritmo do apoio refaz a tabela do git. */
import { describe, expect, test } from "vitest";
import { CMD, DUR_EVO, FORMAS_ARENA, Motor, VERSAO_V22, VERSAO_V23, lutarNucleoPoc, sorteiosPoc } from "../motor/index.ts";
import { APOIO_LP6, APOIO_TABELA, ARENA_POR_ESTAGIO_LP6 } from "../motor/arena/index.ts";
import { CANDIDATO_V21, extrasLp6, lutar, refazerApoio, rivalCanonico, tabelaDoRitmo } from "../scripts/equilibrio_poc/comum.ts";
import { candidatoDe, LP5_3, LP6_0 } from "../scripts/equilibrio_poc/candidatos.ts";
import { motorDoCandidato } from "../scripts/equilibrio_poc/bancada.ts";

describe("as chaves da LP6 na bancada (LP6-3)", () => {
  test("desligadas no v21 e no lp5_3: nada entra; o lp6_0 e o lp5_3 com as duas ligadas e os numeros da LP6-1", () => {
    expect(extrasLp6(CANDIDATO_V21)).toEqual({});
    expect(extrasLp6(LP5_3)).toEqual({});
    const { apoio, arena, nome, ...resto } = LP6_0, { apoio: a3, arena: r3, nome: n3, ...resto3 } = LP5_3;
    expect([nome, n3]).toEqual(["lp6_0", "lp5_3"]);
    expect(resto).toEqual(resto3);
    expect(a3.ligado).toBe(0); expect(r3.ligada).toBe(0);
    expect(apoio).toEqual({ ligado: 1, ...APOIO_LP6, ritmo: APOIO_TABELA.ritmo, desde: 0, recua: 0 });
    expect(arena).toEqual({ ligada: 1, ...ARENA_POR_ESTAGIO_LP6 });
    expect(extrasLp6(LP6_0)).toEqual({ apoio: { ...APOIO_LP6 }, arenaPorEstagio: { ...ARENA_POR_ESTAGIO_LP6 } });
  });
  test("a regra do ritmo refaz a tabela do git no 0,6; outro ritmo so com o apoio ligado; fora da faixa falha alto", () => {
    expect(refazerApoio(FORMAS_ARENA, APOIO_TABELA.ritmo)).toEqual(FORMAS_ARENA);
    expect(tabelaDoRitmo(APOIO_TABELA.ritmo)).toBeUndefined();
    const t = tabelaDoRitmo(.8)!, f = t.brasa_crianca_sereno!;
    expect(f.msApoio).toBe(Math.round(f.msGolpe * .8));
    expect(f.apoio!.t).toBeCloseTo(f.golpe.t * .8, 12);
    expect(tabelaDoRitmo(.8)).toBe(t);
    expect(() => candidatoDe({ nome: "teste", apoio: { ritmo: .8 } })).toThrow();
    expect(() => candidatoDe({ nome: "teste", apoio: { ligado: 1, dano: 0 } })).toThrow();
    expect(() => candidatoDe({ nome: "teste", arena: { ligada: 1, Ultimate: 1.4, Mega: 1.2 } })).toThrow();
    expect(() => candidatoDe({ nome: "teste", arena: { ligada: 2 } })).toThrow();
    expect(extrasLp6(candidatoDe({ nome: "teste", apoio: { ligado: 1, ritmo: .8 } })).tabela).toBe(t);
  });
  test("a luta da bancada com as chaves e a do nucleo com as mesmas entradas, e o apoio muda a luta do atirador colado", () => {
    const A = { forma: "brasa_adulto_furioso", stats: rivalCanonico(LP6_0, "brasa_adulto_furioso") };
    const B = { forma: "ferrugem_adulto_furioso", stats: rivalCanonico(LP6_0, "ferrugem_adulto_furioso") };
    const x = extrasLp6(LP6_0);
    let difere = 0;
    for (const s of [1, 2, 3, 4, 5, 6]) {
      const r = lutarNucleoPoc({ cena: "campo", semente: s, a: A, b: B, apoio: x.apoio!, arenaPorEstagio: x.arenaPorEstagio! }, sorteiosPoc(s));
      const b = lutar("campo", s, A, B, undefined, undefined, x);
      expect([b.vencedor, b.relogio, b.vidaA]).toEqual([r.vencedor, r.relogio, r.vidaA]);
      const sem = lutar("campo", s, A, B);
      if (sem.relogio !== b.relogio || sem.vidaA !== b.vidaA) difere++;
    }
    expect(difere).toBeGreaterThan(0);
  });
  test("o Motor da bancada: as entradas da LP6 so com as chaves ligadas; o v23 do jogo nao as tem", () => {
    const sem = motorDoCandidato(LP5_3, 101), com = motorDoCandidato(LP6_0, 101), jogo = new Motor(101, VERSAO_V23);
    expect([sem.apoioLutaPoc, sem.arenaLutaPoc, sem.formasLutaPoc]).toEqual([null, null, null]);
    expect([jogo.apoioLutaPoc, jogo.arenaLutaPoc, jogo.formasLutaPoc]).toEqual([null, null, null]);
    expect(com.apoioLutaPoc).toEqual(APOIO_LP6);
    expect(com.arenaLutaPoc).toEqual(ARENA_POR_ESTAGIO_LP6);
    expect(com.formasLutaPoc).toBeNull();
    expect(com.versao).toBe(VERSAO_V22);
    /* a mesma vida, a luta com o apoio pela entrada do Motor */
    let difere = 0;
    for (const s of [101, 202, 303]) {
      const a = motorDoCandidato(LP5_3, s), b = motorDoCandidato(LP6_0, s);
      for (const m of [a, b]) { m.liberar(CMD.mega); m.avancar(DUR_EVO.bebe + 30); }
      for (const rv of a.rivaisArenaPoc()) {
        const ra = a.lutarPoc(rv, s * 7, "campo"), rb = b.lutarPoc(rv, s * 7, "campo");
        if (JSON.stringify(ra.serie) !== JSON.stringify(rb.serie)) difere++;
      }
    }
    expect(difere).toBeGreaterThan(0);
  });
  test("o apoio pelo estagio e o recuo na bancada (D-LP6-3-7): o desde vira o estagio, o recua vira a chave; so com o apoio ligado", () => {
    const c = candidatoDe({ nome: "teste", apoio: { ligado: 1, desde: 3, recua: 1 } });
    expect(extrasLp6(c).apoio).toEqual({ ...APOIO_LP6, desde: "Ultimate", recua: true });
    expect(extrasLp6(candidatoDe({ nome: "teste", apoio: { ligado: 1, desde: 4 } })).apoio).toEqual({ ...APOIO_LP6, desde: "Mega" });
    expect(() => extrasLp6(candidatoDe({ nome: "teste", apoio: { ligado: 1, desde: 5 } }))).toThrow();
    expect(() => candidatoDe({ nome: "teste", apoio: { desde: 3 } })).toThrow();
    expect(() => candidatoDe({ nome: "teste", apoio: { ligado: 1, recua: 2 } })).toThrow();
  });
});
