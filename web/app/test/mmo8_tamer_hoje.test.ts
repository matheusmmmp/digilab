/* MMO8: com a chave do reset desligada, os registros do Tamer de hoje saem byte a byte iguais ao gabarito gravado antes do evento "reset"
   (test/gabaritos/mmo8_tamer_hoje.json, por test/gerar_gabarito_mmo8.ts). */
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { jogarHoje, type CasoTamer } from "./mmo8_tamer_hoje.ts";

const gab = JSON.parse(readFileSync(new URL("./gabaritos/mmo8_tamer_hoje.json", import.meta.url), "utf8")) as { versao: number; casos: CasoTamer[] };

describe("MMO8: os registros do Tamer de hoje saem iguais ao gabarito gravado antes do reset", () => {
  test("a forma do gabarito", () => {
    expect(gab.versao).toBe(1);
    expect(gab.casos.map(c => c.nome)).toEqual(["vazio", "tres_medalhas", "liga_e_recorde", "bits", "marco_10", "registro_9"]);
    expect(gab.casos.every(c => c.lido.versao === 10)).toBe(true);
  });
  const agora = jogarHoje();
  for (const c of gab.casos) {
    test(`o caso ${c.nome}: o texto gravado e o estado lido`, () => {
      expect(agora.find(x => x.nome === c.nome)).toEqual(c);
    });
  }
});
