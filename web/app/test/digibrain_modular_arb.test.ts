/* G-PAR do M-ARB (LM2): `arb.reflexo` e `arb.escolher` do gabarito da LM0 (os pesos, o sorteio, o reflexo do sono, as sondas "quem decidiu" com a
   `sem_lembranca`). A rng de politica do motor e `random.Random(semente + 1_000_003)` (digilab/engine.py); o TS a refaz com o `RandomPy` do jogo e
   confere, a cada `escolher`, o sha256 do estado dela antes e depois contra `rng_antes` e `rng_depois` do gabarito. */
import { describe, expect, test } from "vitest";
import { Arbitragem } from "../motor/digibrain/arb.ts";
import { CONFIG_DIGIBRAIN_LAB } from "../motor/digibrain/constantes.ts";
import { RandomPy } from "../motor/mundo.ts";
import { assinar, conferir, entrada, sha16, textoCanonico, vidasModular } from "./digibrain_modular_gabarito.ts";

/** o sha256 do `getstate()` do Python: (3, as 624 palavras e o indice, None) */
const estadoRng = (r: RandomPy): string => {
  const x = r as unknown as { mt: Uint32Array; i: number };
  return sha16(textoCanonico([3, [...Array.from(x.mt), x.i], null]));
};

describe("G-PAR arb", () => {
  test("reflexo e escolher iguais ao Python (e a rng antes e depois) em todas as decisoes das oito vidas", () => {
    const n = { reflexo: 0, escolher: 0, sorteios: 0, reflexos: 0, semU: 0, lembrancaDecidiu: 0, aprendidoDecidiu: 0, nada: 0 };
    for (const v of vidasModular()) {
      const arb = new Arbitragem(null, CONFIG_DIGIBRAIN_LAB.memoria_autobio, CONFIG_DIGIBRAIN_LAB.facetas_mem);
      const rng = new RandomPy(v.semente + 1_000_003);
      for (const d of v.decisoes) {
        for (const c of d.chamadas) {
          if (!c.m.startsWith("arb.")) continue;
          const onde = `${v.lugar}/${v.dono}/${v.semente} k=${d.k} ${c.m}`;
          if (c.m === "arb.reflexo") {
            conferir(onde, arb.reflexo(entrada(d, c, 0)), c.s);
            n.reflexo++;
          } else if (c.m === "arb.escolher") {
            const antes = estadoRng(rng);
            conferir(`${onde} rng antes`, [antes], c.rng_antes);
            conferir(`${onde} rng (entrada)`, "rng:" + antes, c.e[3]);
            const s = arb.escolher(entrada(d, c, 0), entrada(d, c, 1), entrada(d, c, 2), rng, entrada(d, c, 4), entrada(d, c, 5));
            conferir(onde, s, c.s);
            conferir(`${onde} rng depois`, [estadoRng(rng)], c.rng_depois);
            n.escolher++;
            if (s.u !== null) n.sorteios++; else n.semU++;
            if (s.reflexo) n.reflexos++;
            if (s.nada_a_fazer) n.nada++;
            if (s.sondas["lembranca_decidiu"]) n.lembrancaDecidiu++;
            if (s.sondas["aprendido_decidiu"]) n.aprendidoDecidiu++;
          } else {
            throw new Error(`${onde}: chamada nao conferida`);
          }
        }
        conferir(`${v.lugar}/${v.dono}/${v.semente} k=${d.k} assinatura do arb`, assinar(arb.estadoInterno()), d.assinatura["arb"]);
      }
    }
    console.log(`G-PAR arb: ${n.reflexo + n.escolher} chamadas conferidas (reflexo ${n.reflexo}, escolher ${n.escolher}: sorteios ${n.sorteios}, sem sorteio ${n.semU}, `
      + `reflexos ${n.reflexos}, nada a fazer ${n.nada}, lembranca_decidiu ${n.lembrancaDecidiu}, aprendido_decidiu ${n.aprendidoDecidiu})`);
    expect(n.reflexo + n.escolher).toBeGreaterThan(0);
    expect(n.reflexo).toBe(8 * 384);
    expect(n.escolher).toBe(8 * 384);
    for (const x of [n.sorteios, n.semU, n.reflexos, n.aprendidoDecidiu]) expect(x).toBeGreaterThan(0);
  });

  test("a facetas_mem e a escolha segurada ficam fora do laboratorio", () => {
    expect(() => new Arbitragem(null, true, true)).toThrow(/facetas_mem/);
    const arb = new Arbitragem(null, true, false);
    expect(() => arb.escolher([], { g_exp: 0 }, { leitura: {} }, new RandomPy(1), false, ["comer", null, null])).toThrow(/segurada/);
  });
});
