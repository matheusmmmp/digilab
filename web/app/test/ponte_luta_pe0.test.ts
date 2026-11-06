/* PE0 da ponte da luta (docs/TAREFA_V3_PONTE_LUTA.md, 3.5): o pet de teste v16 e o v17 lutam? (o modular, o A e um "cb" entre duas lutas)
     - o pet nasce, chega a um estagio que luta, luta contra bots e uma serie (a Liga), e o replay do registro refaz as lutas bit a bit;
     - o gabarito das lutas de hoje (test/gabaritos/ponte_luta_pe0.json.gz, gravado por test/gerar_gabarito_pe0.ts): por luta, o ResultadoLuta
       resumido, a assinatura do GambitsPet, a da confianca e o estadoInterno do modular. As chaves da ponte (PE1 em diante) desligadas
       tem de dar estes mesmos bytes (G2). */
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { describe, expect, test } from "vitest";
import { Motor, VERSAO_PET_LAB } from "../motor/index.ts";
import { DIAS, SEMENTES, VARIANTES, gravar, refazer, sha256, viverComLutas, type Variante, type VidaGravada } from "./ponte_luta_pe0.ts";

const gab = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/ponte_luta_pe0.json.gz", import.meta.url))).toString("utf8")) as
  { versao: number; dias: number; sementes: number[]; variantes: string[]; vidas: VidaGravada[] };

describe("PE0: o v16 e o v17 lutam, e o replay refaz as lutas", () => {
  for (const v of VARIANTES) for (const s of SEMENTES) {
    test(`${v} @${s}: nasce, chega a um estagio que luta, luta (bot e serie) e o replay sai bit a bit`, () => {
      const vida = viverComLutas(v, s);
      expect(vida.versao).toBe(v === "v16" ? VERSAO_PET_LAB : 17);
      expect(vida.estagio, "o pet saiu do In-Training").not.toBe("bebe");
      expect(vida.lutas.length, "o pet lutou").toBeGreaterThan(5);
      expect(vida.lutas.some(l => l.rival !== "liga" && l.serie === 1), "contra um bot").toBe(true);
      expect(vida.lutas.some(l => l.rival === "liga"), "a serie (a Liga)").toBe(true);
      /* o cerebro que decidia na hora da luta */
      const cer = new Set(vida.lutas.map(l => l.cerebro));
      expect([...cer].sort()).toEqual(v === "v17_a" ? ["a"] : v === "v17_cb" ? ["a", "modular"] : ["modular"]);
      expect(vida.lutas.every(l => (l.modular !== null) === (l.cerebro === "modular")), "o estado do modular so quando ele decide").toBe(true);
      expect(vida.lutas.every(l => l.lutas.every(x => [0, .5, 1].includes(x.pontosA) && x.passos > 0)), "o resultado de cada luta").toBe(true);
      /* G1: o replay do registro, evento a evento: as tres assinaturas depois de cada luta e a do pet no fim */
      const r = refazer(vida);
      expect(r.lutas).toEqual(vida.lutas.map(l => ({ evento: l.evento, gambits: l.gambits, confianca: l.confianca, modular: l.modular })));
      expect(sha256(r.m.assinatura())).toBe(vida.assinatura);
      expect(Motor.reproduzir(s, vida.log, vida.versao).assinatura(), "pelo caminho publico do replay").toBe(r.m.assinatura());
    });
  }

  test("o replay refaz uma serie de mais de uma luta (a Liga com mais de uma vitoria)", () => {
    const longa = VARIANTES.flatMap(v => SEMENTES.map(s => viverComLutas(v, s))).filter(x => x.lutas.some(l => l.serie > 1));
    expect(longa.length).toBeGreaterThan(0);
  });

  test("o 'cb' entre duas lutas: a troca cai no registro entre as lutas e o A fica parado, o modular continua dali", () => {
    const vida = viverComLutas("v17_cb", 101);
    const cb = vida.log.map((e, i) => [e, i] as const).filter(([e]) => e[1] === "cb").map(([, i]) => i);
    expect(cb.length).toBe(3);                   // o do ovo, para o A e de volta ao modular
    expect(vida.lutas.slice(0, 3).map(l => l.cerebro)).toEqual(["modular", "a", "modular"]);
    expect(cb[1]).toBeGreaterThan(vida.lutas[0].evento);
    expect(cb[1]).toBeLessThan(vida.lutas[1].evento);
    expect(cb[2]).toBeGreaterThan(vida.lutas[1].evento);
    expect(cb[2]).toBeLessThan(vida.lutas[2].evento);
  });
});

describe("PE0: o gabarito das lutas de hoje", () => {
  test("a forma do gabarito: as 4 variantes x as 5 sementes, os mesmos dias", () => {
    expect(gab.versao).toBe(1);
    expect(gab.dias).toBe(DIAS);
    expect(gab.sementes).toEqual([...SEMENTES]);
    expect(gab.variantes).toEqual([...VARIANTES]);
    expect(gab.vidas.map(v => [v.variante, v.semente])).toEqual(VARIANTES.flatMap(v => SEMENTES.map(s => [v, s])));
  });
  for (const v of VARIANTES) for (const s of SEMENTES) {
    test(`${v} @${s}: a vida de hoje sai igual ao gabarito (G2), luta a luta`, () => {
      const g = gab.vidas.find(x => x.variante === (v as Variante) && x.semente === s)!;
      const h = gravar(viverComLutas(v, s));
      expect(h.lutas.length).toBe(g.lutas.length);
      h.lutas.forEach((l, i) => expect(l, `luta ${i}`).toEqual(g.lutas[i]));
      expect(h).toEqual(g);
    });
  }
});
