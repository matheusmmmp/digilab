/* A tela Pet mais limpa (docs/TAREFA_V3_UX_TELA_PET.md, secao 23, 2026-11-08): o pet anda ate o lugar no ritmo dele, as faixas ficam 5 s, o minimapa
   menor. So vista */
import { describe, expect, test } from "vitest";
import { PET_VIAGEM_CEL_MS, PET_VIAGEM_MAX_MS, duracaoPetViagem } from "../src/telas/pet/ilha/constantes.ts";
import { AVISO_MS, NOTIFICA_MS } from "../src/hudPet.ts";
import { MINIMAPA_PX } from "../src/telas/pet/minimapaGeo.ts";
import { VIAGEM_MS } from "../src/viagem.ts";

describe("o pet anda ate o lugar", () => {
  test("na velocidade dele: o dobro da distancia, o dobro do tempo, e mais devagar que a camera", () => {
    expect(duracaoPetViagem(7, false)).toBeCloseTo(7 / PET_VIAGEM_CEL_MS, 9);
    expect(duracaoPetViagem(10, false)).toBeCloseTo(2 * duracaoPetViagem(5, false), 9);
    expect(duracaoPetViagem(10, false)).toBeGreaterThan(VIAGEM_MS);
  });
  test("nunca passa do teto, e com reduzir movimento chega na hora", () => {
    expect(duracaoPetViagem(1000, false)).toBe(PET_VIAGEM_MAX_MS);
    expect(duracaoPetViagem(10, true)).toBe(0);
    expect(duracaoPetViagem(0, false)).toBe(0);
  });
});

describe("as faixas e o minimapa", () => {
  test("a faixa do resumo e a linha do agora ficam 5 s; o balao da fala segue com o tempo dele", () => {
    expect(NOTIFICA_MS).toBe(5000);
    expect(AVISO_MS).toBe(15_000);
  });
  test("o minimapa menor que o de antes (232 px)", () => {
    expect(MINIMAPA_PX).toBeLessThan(232);
  });
});
