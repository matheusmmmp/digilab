/* LUTA_POC, LP5-0 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.3): a bancada do equilibrio refaz o jogo de hoje. O CANDIDATO_V21 tem de dar os
   mesmos numeros que o motor (o statsLutaPoc do pet, o statsNpc, o statsRivalArena, o statsRivalForma e o da Fabrica), senao a medida da
   LP5-0 nao e o ponto de partida. E o treino tipico (D-LP5-2) sai com o total exato e dentro dos tetos. */
import { describe, expect, test } from "vitest";
import {
  CAMPANHA_V6, CMD, CTR, DUR_EVO, LIGA, Motor, STATS, TICK_INICIAL, TentativaFabrica, caraterCanonico, condicaoDe, formaLiga, rivaisArena,
  statsDoPet, statsNpc, statsRivalArena, statsRivalForma, TIRO_POC_V21, lutarNucleoPoc, sorteiosPoc, type Stats,
} from "../motor/index.ts";
import {
  CANDIDATO_V21, ESTAGIOS_LUTA, TETO, TIPICO, npc, petDoEstagio, pontosNoTotal, rivalCanonico, rivalDaForma, statsLuta,
} from "../scripts/equilibrio_poc/comum.ts";
import { basesDa } from "../scripts/equilibrio_poc/faixas.ts";
import { limitesNpc, passaNpc } from "../scripts/equilibrio_poc/criterios.ts";
import { candidatoDe, LP5_1_ESQ, LP5_1_R2, LP5_2 } from "../scripts/equilibrio_poc/candidatos.ts";
import { motorDoCandidato } from "../scripts/equilibrio_poc/bancada.ts";

const c = CANDIDATO_V21;

describe("o candidato v21 refaz os numeros do jogo", () => {
  test("o pet: o statsLutaPoc do Motor, sem e com treino", () => {
    for (const s of [11, 21, 23, 101, 202]) {
      const m = new Motor(s);
      m.liberar(CMD.mega);
      m.avancar(DUR_EVO.bebe + 30);
      const conf = () => expect(statsLuta(c, statsDoPet(m.forma, m.carater(), m.pontosDeLuta()), m.forma.est, condicaoDe(m.e.saude))).toEqual(m.statsLutaPoc());
      conf();
      m.treino.pontos = { vigor: 2, folego: 1, recuperacao: 1, forca: 2, mira: 1, guarda: 1.5 } as Stats;
      conf();
      m.avancar(TICK_INICIAL + DUR_EVO.bebe + DUR_EVO.crianca + 15 - m.e.tick);
      expect(m.estagioAtual).toBe("adolescente");
      conf();
    }
  });
  test("os 10 NPCs da campanha v6", () => {
    expect(CAMPANHA_V6).toHaveLength(10);
    for (const x of CAMPANHA_V6) expect(npc(c, x.k)).toEqual(statsNpc(x.k));
  });
  test("os rivais da Arena de cada estagio", () => {
    for (const e of ESTAGIOS_LUTA) for (const k of rivaisArena(e)) expect(rivalCanonico(c, k)).toEqual(statsRivalArena(k));
  });
  test("os Megas da Liga e da Fabrica", () => {
    LIGA.forEach((x, k) => expect(rivalDaForma(c, formaLiga(k), caraterCanonico(x.adulta))).toEqual(statsRivalForma(formaLiga(k), caraterCanonico(x.adulta))));
    const t = new TentativaFabrica(1, 0);
    for (const f of t.alugueis) expect(rivalDaForma(c, f, caraterCanonico(f.adulta!))).toEqual(t.statsPoc(f));
  });
});

describe("o treino tipico (D-LP5-2) e os pets", () => {
  test("o total sai exato, cada stat dentro do teto, e a curva sobe", () => {
    for (const esp of ["brasa", "cirro", "ferrugem", "limo"] as const) {
      let antes: Stats | null = null;
      for (let n = 0; n <= TETO.mega; n += 2) {
        const p = pontosNoTotal(esp, n), tot = STATS.reduce((a, k) => a + p[k], 0);
        expect(tot).toBeCloseTo(n, 9);
        for (const k of STATS) { expect(p[k]).toBeGreaterThanOrEqual(0); expect(p[k]).toBeLessThanOrEqual(CTR.tetoStat + 1e-9); if (antes) expect(p[k]).toBeGreaterThanOrEqual(antes[k] - 1e-9); }
        antes = p;
      }
      expect(() => pontosNoTotal(esp, TETO.mega + 1)).toThrow(/nao chega/);
    }
    expect(TIPICO).toEqual({ crianca: 8, adolescente: 22, adulto: 36, mega: 40 });
    expect(TETO).toEqual({ crianca: 10, adolescente: 22, adulto: 36, mega: 40 });
  });
  test("o pet da base: uma forma do estagio, a mesma a cada chamada", () => {
    for (const e of ESTAGIOS_LUTA) {
      const p = petDoEstagio(86101, 3, e);
      expect(rivaisArena(e)).toContain(p.chave);
      expect(petDoEstagio(86101, 3, e)).toEqual(p);
    }
  });
  test("as faixas: as 5 bases, e um nome fora falha alto", () => {
    expect(basesDa("calibracao")).toEqual([86101, 86202, 86303, 86404, 86505]);
    expect(basesDa("conferencia")).toEqual([87101, 87202, 87303, 87404, 87505]);
    expect(() => basesDa("calibracao2")).toThrow(/faixa desconhecida/);
  });
});

describe("os candidatos da rodada (LP5-1 a LP5-3)", () => {
  test("o candidatoDe troca so o que se pede e falha alto no resto", () => {
    const x = candidatoDe({ nome: "teste", pesoPonto: 10, gama: { vigor: .5 } });
    expect(x.pesoPonto).toBe(10);
    expect(x.gama.vigor).toBe(.5);
    expect(x.gama.forca).toBe(1);
    expect(x.mapa).toEqual(c.mapa);
    expect(c.pesoPonto).toBe(CTR.pesoPontoCombate);
    expect(() => candidatoDe({ nome: "teste", gama: { sorte: 1 } } as never)).toThrow();
    expect(() => candidatoDe({ nome: "teste", pesoPonto: 0 })).toThrow();
    expect(() => candidatoDe({ nome: "v21" })).toThrow();
  });
  test("o Motor remendado com os numeros do v21 luta igual ao Motor do jogo (a vida do P5)", () => {
    const copia = candidatoDe({ nome: "copia_v21" });
    for (const s of [11, 21, 23]) {
      const a = new Motor(s), b = motorDoCandidato(copia, s, true);
      for (const m of [a, b]) { m.liberar(CMD.mega); m.avancar(TICK_INICIAL + DUR_EVO.bebe + DUR_EVO.crianca + 15 - m.e.tick); m.treino.pontos = { vigor: 2, folego: 1, recuperacao: 1, forca: 2, mira: 1, guarda: 1.5 } as Stats; }
      expect(b.estagioAtual).toBe("adolescente");
      for (let k = 0; k < 3; k++) {
        const rv = a.rivaisArenaPoc()[k];
        expect(b.lutarPoc(rv, 1000 + k, "campo")).toEqual(a.lutarPoc(rv, 1000 + k, "campo"));
      }
      expect(b.sparring).toBe(a.sparring);
    }
  });
});

describe("a distancia do tiro no nucleo (D-LP5-12)", () => {
  const A = { forma: "brasa_crianca_sereno", stats: statsRivalArena("brasa_crianca_sereno") };
  const B = { forma: "ferrugem_crianca_arisco", stats: statsRivalArena("ferrugem_crianca_arisco") };
  test("o tiro da POC na entrada da a mesma luta que a entrada sem ele", () => {
    for (const cena of ["campo", "praia", "caverna"] as const) for (const s of [1, 2, 3]) {
      const sem = lutarNucleoPoc({ cena, semente: s, a: A, b: B }, sorteiosPoc(s));
      expect(lutarNucleoPoc({ cena, semente: s, a: A, b: B, tiro: { ...TIRO_POC_V21 } }, sorteiosPoc(s))).toEqual(sem);
    }
  });
  test("o candidato v21 nao leva o tiro; um tiro fora da faixa falha alto", () => {
    expect(c.tiro).toEqual(TIRO_POC_V21);
    expect(() => candidatoDe({ nome: "teste", tiro: { distMin: 500 } })).toThrow();
    expect(() => candidatoDe({ nome: "teste", tiro: { recuo: 0 } })).toThrow();
    expect(candidatoDe({ nome: "teste", tiro: { distMin: 90, esperaMax: 800 } }).tiro.distMin).toBe(90);
  });
});

describe("a esquiva pela perspicacia e pela velocidade (D-LP5-14)", () => {
  const A = { forma: "cirro_crianca_sereno", stats: statsRivalArena("cirro_crianca_sereno") };
  const B = { forma: "brasa_crianca_arisco", stats: statsRivalArena("brasa_crianca_arisco") };
  const neutra = { kChance: 1, kReacao: 1, kDash: 1, chanceMax: .95, pertoChance: 0, pertoReacao: 200, contraMs: 0 };
  test("ligada com os lutadores neutros e sem o golpe de perto, da a luta da POC", () => {
    for (const cena of ["campo", "floresta", "ringue"] as const) for (const s of [4, 5, 6]) {
      const sem = lutarNucleoPoc({ cena, semente: s, a: A, b: B }, sorteiosPoc(s));
      expect(lutarNucleoPoc({ cena, semente: s, a: A, b: B, esquiva: neutra }, sorteiosPoc(s))).toEqual(sem);
    }
  });
  test("o candidato v21 nao liga a esquiva; a perspicacia so aparece ligada; fora da faixa falha alto", () => {
    expect(c.esquiva.ligada).toBe(0);
    expect(rivalCanonico(c, "cirro_crianca_sereno").perc).toBeUndefined();
    const x = candidatoDe({ nome: "teste", esquiva: { ligada: 1, pertoChance: .3 } });
    expect(rivalCanonico(x, "cirro_crianca_sereno").perc).toBeGreaterThan(rivalCanonico(x, "brasa_crianca_arisco").perc!);
    expect(() => candidatoDe({ nome: "teste", esquiva: { ligada: 1, chanceMax: 2 } })).toThrow();
  });
  test("o lp5_2 (D-LP5-17) e o lp5_1_esq com o Gazimon em 76,8, e so isso", () => {
    expect(LP5_2.npcTotal.npc_tier1_brutamontes).toBe(76.8);
    expect({ ...LP5_2, nome: "", npcTotal: { ...LP5_2.npcTotal, npc_tier1_brutamontes: 96 } }).toEqual({ ...LP5_1_ESQ, nome: "" });
  });
  test("o lp5_1_esq (D-LP5-16) e o lp5_1_r2 com a esquiva ligada, e so isso", () => {
    expect(LP5_1_ESQ.esquiva).toMatchObject({ ligada: 1, gamaMira: .6, gamaFolego: .6, kAtento: .5, pertoChance: 0 });
    expect({ ...LP5_1_ESQ, nome: "", esquiva: null }).toEqual({ ...LP5_1_R2, nome: "", esquiva: null });
  });
});

describe("a divisao dos stats do NPC (D-LP5-18)", () => {
  test("sem divisao, o NPC divide igual; com divisao, o total fica e os pesos mudam os stats", () => {
    expect(c.npcDivisao).toEqual({});
    const k = "npc_tier2_carcereiro", w = { vigor: .6, folego: .6, recuperacao: .6, forca: .6, mira: 3, guarda: .6 };
    const x = candidatoDe({ nome: "teste", esquiva: { ligada: 1 }, npcDivisao: { [k]: w } }), igual = candidatoDe({ nome: "teste", esquiva: { ligada: 1 } });
    expect(npc(igual, k)).toEqual(npc(candidatoDe({ nome: "teste", esquiva: { ligada: 1 }, npcDivisao: { [k]: { vigor: 1, folego: 1, recuperacao: 1, forca: 1, mira: 1, guarda: 1 } } }), k));
    expect(npc(x, k).perc!).toBeGreaterThan(npc(igual, k).perc!);
    expect(npc(x, k).agil!).toBeLessThan(npc(igual, k).agil!);
    expect(npc(x, "npc_v5_piedmon")).toEqual(npc(igual, "npc_v5_piedmon"));
  });
  test("divisao sem os 6 stats, com peso nao positivo, que nao soma 6 ou de um NPC que nao existe falha alto", () => {
    const um = { vigor: 1, folego: 1, recuperacao: 1, forca: 1, mira: 1, guarda: 1 };
    expect(() => candidatoDe({ nome: "teste", npcDivisao: { npc_tier2_carcereiro: { ...um, guarda: 2 } } })).toThrow();
    expect(() => candidatoDe({ nome: "teste", npcDivisao: { npc_tier2_carcereiro: { ...um, guarda: 0, mira: 2 } } })).toThrow();
    expect(() => candidatoDe({ nome: "teste", npcDivisao: { npc_tier2_carcereiro: { vigor: 6 } as never } })).toThrow();
    expect(() => candidatoDe({ nome: "teste", npcDivisao: { npc_que_nao_ha: um } })).toThrow();
  });
});

describe("o fator dos rivais dos torneios (D-LP5-20)", () => {
  test("hoje o fator e 1 e nao muda o rival; abaixo de 1, os 6 stats vezes o fator; nao positivo falha alto", () => {
    expect(c.fatorRival).toEqual({ salao: 1, liga: 1, torre: 1, fabrica: 1 });
    const f = formaLiga(0), car = caraterCanonico(LIGA[0].adulta), x = candidatoDe({ nome: "teste", esquiva: { ligada: 1 } });
    expect(rivalDaForma(x, f, car, 0, 1)).toEqual(rivalDaForma(x, f, car));
    const meio = rivalDaForma(x, f, car, 0, .5), um = rivalDaForma(x, f, car);
    expect(meio.atk).toBeLessThan(um.atk);
    expect(meio.perc!).toBeLessThan(um.perc!);
    expect(() => rivalDaForma(x, f, car, 0, 0)).toThrow();
    expect(() => candidatoDe({ nome: "teste", fatorRival: { liga: 0 } })).toThrow();
  });
});

describe("o criterio do P1 a P3 (D-LP5-17)", () => {
  test("os limites saem do T1 do lp5_1_esq: o meio do caminho na escala logistica, com 0,10 de folga", () => {
    expect([limitesNpc("crianca", false), limitesNpc("adolescente", false), limitesNpc("adulto", false), limitesNpc("mega", false)])
      .toEqual([{ sem: .41, tip: .59 }, { sem: .35, tip: .65 }, { sem: .3, tip: .7 }, { sem: .27, tip: .73 }]);
    expect([limitesNpc("adolescente", true), limitesNpc("mega", true)]).toEqual([{ sem: .5, tip: .7 }, { sem: .42, tip: .78 }]);
  });
  test("passa so dentro dos dois limites; estagio sem T1 falha alto", () => {
    expect(passaNpc("crianca", false, .41, .59)).toBe(true);
    expect(passaNpc("crianca", false, .42, .9)).toBe(false);
    expect(passaNpc("crianca", false, .1, .58)).toBe(false);
    expect(() => limitesNpc("ovo", false)).toThrow();
  });
});
