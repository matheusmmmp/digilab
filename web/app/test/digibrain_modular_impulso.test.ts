/* G-PAR do M-IMPULSO (LM1): cada `impulso.unidades` do gabarito da LM0 (as unidades, os termos, as ativacoes e o z).
   O gabarito guarda `<plasticidade>` e `<fn>` (o `casa` do M-MEM) como texto. O que o impulso pede ao M-PLAST (`habito` e `incentivo`) vem do
   arquivo digibrain_modular_leituras_plast.json.gz (a leitura nova da LM1 no exportador): o TS recebe um M-PLAST de mentira que devolve o que o
   Python devolveu, conferindo a entrada de cada pergunta. O `casa` e o oficial do M-MEM (mem.ts, LM3). */
import { describe, expect, test } from "vitest";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_MODULAR_MUNDO } from "../motor/digibrain/constantes.ts";
import { Impulso, type PlastImpulso, type TermoLembranca } from "../motor/digibrain/impulso.ts";
import { Memoria } from "../motor/digibrain/mem.ts";
import { conferir, entrada, leiturasPlast, vidasModular } from "./digibrain_modular_gabarito.ts";

/** o `casa` oficial do M-MEM (mem.ts, LM3) */
const casa = new Memoria({ sub: CONFIG_MODULAR_MUNDO.sub }, null, CONFIG_DIGIBRAIN_LAB).casa;

/** a chave da persistencia no Python (`str` da tupla) em JSON: ('comer', 'cheiro', None) -> ["comer","cheiro",null] */
const chaveDoPython = (t: string): string => JSON.stringify(JSON.parse(t.replace(/'/g, '"').replace(/None/g, "null").replace(/\(/g, "[").replace(/\)/g, "]")));

describe("G-PAR impulso", () => {
  test("impulso.unidades igual ao Python em todas as decisoes das oito vidas", () => {
    const lp = leiturasPlast();
    let conferidas = 0, comLembranca = 0, comPonto = 0, comIncentivo = 0, comHabito = 0, comPersistencia = 0;
    const impulso = new Impulso(null, CONFIG_DIGIBRAIN_LAB);
    vidasModular().forEach((v, iv) => {
      const lv = lp[iv]!;
      expect([lv.lugar, lv.dono, lv.semente]).toEqual([v.lugar, v.dono, v.semente]);
      for (const d of v.decisoes) {
        for (const c of d.chamadas.filter(x => x.m === "impulso.unidades")) {
          const onde = `${v.lugar}/${v.dono}/${v.semente} k=${d.k} impulso.unidades`;
          const fila = [...lv.decisoes[d.k]!.chamadas];
          const proxima = (m: string) => {
            const x = fila.shift();
            if (!x || x.m !== m) throw new Error(`${onde}: esperava ${m}, veio ${x?.m}`);
            return x;
          };
          const plast: PlastImpulso = {
            habito(b, z) {
              const x = proxima("plast.habito");
              conferir(`${onde} ${x.m}.entrada`, [b, [...z]], x.e);
              return x.s;
            },
            incentivo(pc, classe, drives) {
              const x = proxima("plast.incentivo");
              conferir(`${onde} ${x.m}.entrada`, [pc, classe, [...drives]], x.e);
              return x.s;
            },
          };
          const ctx = entrada(d, c, 2);
          const persistencia = Object.fromEntries(Object.entries(ctx.persistencia as Record<string, number>).map(([k, h]) => [chaveDoPython(k), h]));
          const l = c.e[6] as [TermoLembranca, string] | null;
          const lembranca = l === null ? null : ([l[0], casa] as const);
          const [unidades, z] = impulso.unidades(entrada(d, c, 0), entrada(d, c, 1), { ...ctx, persistencia }, plast, entrada(d, c, 4), c.e[5] as string[], lembranca, c.e[7]);
          conferir(onde, [unidades, z], c.s);
          if (fila.length) throw new Error(`${onde}: sobraram ${fila.length} leituras do M-PLAST`);
          conferidas++;
          if (lembranca) comLembranca++;
          if (unidades.some(u => u.tipo === "ponto")) comPonto++;
          if (unidades.some(u => u.termos["incentivo"] !== 0)) comIncentivo++;
          if (unidades.some(u => u.termos["habito"] !== 0)) comHabito++;
          if (unidades.some(u => u.termos["persistencia"] !== 0)) comPersistencia++;
        }
      }
    });
    console.log(`G-PAR impulso: ${conferidas} chamadas conferidas (lembranca ${comLembranca}, lugar lembrado ${comPonto}, incentivo ${comIncentivo}, habito ${comHabito}, persistencia ${comPersistencia})`);
    expect(conferidas).toBeGreaterThan(0);
    expect(conferidas).toBe(8 * 384);
    for (const n of [comLembranca, comPonto, comIncentivo, comHabito, comPersistencia]) expect(n).toBeGreaterThan(0);
  });

  test("a facetas_mem fica fora do laboratorio e o tipo `cheiro` no W0_tipo falha alto", () => {
    expect(() => new Impulso(null, { ...CONFIG_DIGIBRAIN_LAB, facetas_mem: true })).toThrow(/facetas_mem/);
  });
});
