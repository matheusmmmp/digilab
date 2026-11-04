/* o HUD da tela Pet (src/hudPet.ts, 2026-11-04): o chamado de fome so aparece abaixo de FOME_FALA; o emoji, abaixo de FOME_EMOTE */
import { describe, expect, test } from "vitest";
import { FOME_EMOTE, FOME_FALA, chamadosVisiveis, fomeNoEmote } from "../src/hudPet.ts";
import type { Motor } from "../motor/index.ts";

const pet = (fome: number, abertos: string[]) => ({ e: { fome }, chamadosAbertos: () => abertos }) as unknown as Motor;

describe("a fome no HUD", () => {
  test("o chamado de fome so aparece abaixo de FOME_FALA; os outros chamados passam", () => {
    expect(chamadosVisiveis(pet(.76, ["fome", "carinho"]))).toEqual(["carinho"]);
    expect(chamadosVisiveis(pet(FOME_FALA - .01, ["fome", "carinho"]))).toEqual(["fome", "carinho"]);
  });
  test("o emoji da carne abaixo de FOME_EMOTE", () => {
    expect(fomeNoEmote(pet(FOME_EMOTE - .01, []))).toBe(true);
    expect(fomeNoEmote(pet(FOME_EMOTE, []))).toBe(false);
  });
});
