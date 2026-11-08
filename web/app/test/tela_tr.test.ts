// O tempo de tela da bancada da fase 1 (a D-R3-6 da rodada 3; scripts/equilibrio_tr/tela_tr.ts): os numeros do palco lidos de src/luta.ts e
// a conta de uma serie da Cidadela. So a bancada usa isto; o jogo e a luta nao mudam.
import { describe, expect, test } from "vitest";
import { ARENA_POR_ID, CV21E_TR, FORMAS_AD, PASSO_TR_MS, RELOGIO_V14, jogarArena, lutadorBot, type RegrasLuta } from "../motor/index.ts";
import { PALCO, telaDaSerie } from "../scripts/equilibrio_tr/tela_tr.ts";

describe("o tempo de tela da bancada (D-R3-6)", () => {
  test("os numeros do palco sao os de src/luta.ts", () => {
    expect(PALCO).toEqual({ quadroMs: 48, passosQuadro: 3, pausaFim: 900, pausaFimKo: 1800, pausaSerie: 1500 });
  });
  test("a serie leva mais tempo na tela que na luta, e a conta se repete", () => {
    const R: RegrasLuta = { ...CV21E_TR, relogio: RELOGIO_V14 }, cid = ARENA_POR_ID.cidadela;
    const serie = jogarArena(lutadorBot(FORMAS_AD[0], R), lutadorBot(cid.lider, R, cid), 101, R, cid.lutas ?? 1, 1);
    const luta = serie.reduce((a, x) => a + x.tr!.passos * PASSO_TR_MS, 0), tela = telaDaSerie(serie);
    /* na velocidade de sempre, um quadro de 48 ms mostra 3 passos de 16 ms: a tela nunca e mais rapida que a luta */
    expect(tela).toBeGreaterThan(luta);
    expect(telaDaSerie(serie)).toBe(tela);
  });
});
