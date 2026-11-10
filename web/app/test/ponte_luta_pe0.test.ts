/* PE0 da ponte da luta (docs/TAREFA_V3_PONTE_LUTA.md, 3.5), na luta da POC (LUTA_POC, LP4): os pets v21 lutam com o modular, com o A e com
   um "cb" entre duas lutas.
     - o pet nasce, chega a um estagio que luta, luta na Arena e numa serie (a Liga), e o replay do registro refaz as lutas bit a bit;
     - o "cb" entre duas lutas cai no registro entre elas.
   O gabarito das lutas do pet de teste v16 e da v17 no combate por turnos (test/gabaritos/ponte_luta_pe0.json.gz) saiu na LP4 com as versoes
   antigas (LP-6); as vidas v21 com luta tem o gabarito delas em test/luta_poc_pet.test.ts. */
import { describe, expect, test } from "vitest";
import { Motor, VERSAO_PET } from "../motor/index.ts";
import { SEMENTES, VARIANTES, refazer, sha256, viverComLutas } from "./ponte_luta_pe0.ts";

describe("PE0: os pets v21 lutam, e o replay refaz as lutas", () => {
  for (const v of VARIANTES) for (const s of SEMENTES) {
    test(`${v} @${s}: nasce, chega a um estagio que luta, luta (Arena e serie) e o replay sai bit a bit`, () => {
      const vida = viverComLutas(v, s);
      expect(vida.versao).toBe(VERSAO_PET);
      expect(vida.estagio, "o pet saiu do In-Training").not.toBe("bebe");
      expect(vida.lutas.length, "o pet lutou").toBeGreaterThan(5);
      expect(vida.lutas.some(l => l.rival !== "liga" && l.serie === 1), "na Arena").toBe(true);
      expect(vida.lutas.some(l => l.rival === "liga"), "a serie (a Liga)").toBe(true);
      /* o cerebro que decidia na hora da luta */
      const cer = new Set(vida.lutas.map(l => l.cerebro));
      expect([...cer].sort()).toEqual(v === "v21_a" ? ["a"] : v === "v21_cb" ? ["a", "modular"] : ["modular"]);
      expect(vida.lutas.every(l => (l.modular !== null) === (l.cerebro === "modular")), "o estado do modular so quando ele decide").toBe(true);
      expect(vida.lutas.every(l => l.lutas.every(x => [0, .5, 1].includes(x.pontosA) && x.passos > 0)), "o resultado de cada luta").toBe(true);
      /* G1: o replay do registro, evento a evento: as duas assinaturas depois de cada luta e a do pet no fim */
      const r = refazer(vida);
      expect(r.lutas).toEqual(vida.lutas.map(l => ({ evento: l.evento, confianca: l.confianca, modular: l.modular })));
      expect(sha256(r.m.assinatura())).toBe(vida.assinatura);
      expect(Motor.reproduzir(s, vida.log, vida.versao).assinatura(), "pelo caminho publico do replay").toBe(r.m.assinatura());
    });
  }

  test("a Liga e uma serie: com uma vitoria, a luta seguinte entra com a vida do fim da anterior", () => {
    const longa = VARIANTES.flatMap(v => SEMENTES.map(s => viverComLutas(v, s))).flatMap(x => x.lutas).filter(l => l.serie > 1);
    expect(longa.length).toBeGreaterThan(0);
    for (const l of longa) l.lutas.slice(1).forEach((x, i) => expect(x.hp0[0]).toBe(l.lutas[i].hp[0]));
  });

  test("o 'cb' entre duas lutas: a troca cai no registro entre as lutas", () => {
    const vida = viverComLutas("v21_cb", 101);
    const cb = vida.log.map((e, i) => [e, i] as const).filter(([e]) => e[1] === "cb").map(([, i]) => i);
    expect(cb.length).toBe(3);                   // o do ovo, para o A e de volta ao modular
    expect(vida.lutas.slice(0, 3).map(l => l.cerebro)).toEqual(["modular", "a", "modular"]);
    expect(cb[1]).toBeGreaterThan(vida.lutas[0].evento);
    expect(cb[1]).toBeLessThan(vida.lutas[1].evento);
    expect(cb[2]).toBeGreaterThan(vida.lutas[1].evento);
    expect(cb[2]).toBeLessThan(vida.lutas[2].evento);
  });
});
