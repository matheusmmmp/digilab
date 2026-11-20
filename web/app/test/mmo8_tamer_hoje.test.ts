/* MMO8: com a chave do reset desligada, os registros do Tamer de hoje saem byte a byte iguais ao gabarito gravado antes do evento "reset"
   (test/gabaritos/mmo8_tamer_hoje.json, por test/gerar_gabarito_mmo8.ts). Com a chave ligada (desde as telas, 2026-11-19), a unica
   diferenca e a versao gravada, 11 no lugar da 10: os eventos e o estado lido sao os mesmos. */
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { RESET_LIGADO } from "../src/tamer.ts";
import { jogarHoje, type CasoTamer } from "./mmo8_tamer_hoje.ts";

const gab = JSON.parse(readFileSync(new URL("./gabaritos/mmo8_tamer_hoje.json", import.meta.url), "utf8")) as { versao: number; casos: CasoTamer[] };

describe("MMO8: os registros do Tamer de hoje saem iguais ao gabarito gravado antes do reset", () => {
  test("a forma do gabarito", () => {
    expect(gab.versao).toBe(1);
    expect(gab.casos.map(c => c.nome)).toEqual(["vazio", "tres_medalhas", "liga_e_recorde", "bits", "marco_10", "registro_9"]);
    expect(gab.casos.every(c => c.lido.versao === 10)).toBe(true);
  });
  const agora = jogarHoje(false), ligada = jogarHoje(true);
  for (const c of gab.casos) {
    test(`o caso ${c.nome}, com a chave desligada: o texto gravado e o estado lido, byte a byte`, () => {
      expect(agora.find(x => x.nome === c.nome)).toEqual(c);
    });
    test(`o caso ${c.nome}, com a chave ligada: so a versao muda (10 para 11)`, () => {
      expect(c.texto.startsWith('{"versao":10,')).toBe(true);
      expect(ligada.find(x => x.nome === c.nome)).toEqual({ ...c, texto: '{"versao":11,' + c.texto.slice('{"versao":10,'.length), lido: { ...c.lido, versao: 11 } });
    });
  }
  test("a chave do reset esta ligada no jogo", () => { expect(RESET_LIGADO).toBe(true); });
});
