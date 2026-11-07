/* DC3d da CONVERSA_PET: as vidas de hoje (v13 a v19 e o pet de teste v16), gravadas antes do porte da `fala_unidades`
   (test/gabaritos/dc3d_vidas_hoje.json, por test/gerar_gabarito_dc3d.ts), saem byte a byte: sem a marca da fala com conteudo, nada muda. */
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { Motor } from "../motor/index.ts";
import { DIAS_HOJE, SEMENTES_HOJE, VARIANTES_HOJE, gravarHoje, viverHoje, type VidaHoje } from "./dc3d_hoje.ts";

const gab = JSON.parse(readFileSync(new URL("./gabaritos/dc3d_vidas_hoje.json", import.meta.url), "utf8")) as
  { versao: number; dias: number; sementes: number[]; variantes: string[]; vidas: VidaHoje[] };

describe("DC3d: as vidas de hoje saem iguais ao gabarito gravado antes do porte", () => {
  test("a forma do gabarito: as 8 variantes x as 5 sementes", () => {
    expect(gab.versao).toBe(1);
    expect(gab.dias).toBe(DIAS_HOJE);
    expect(gab.sementes).toEqual([...SEMENTES_HOJE]);
    expect(gab.variantes).toEqual([...VARIANTES_HOJE]);
    expect(gab.vidas.map(v => [v.variante, v.semente])).toEqual(VARIANTES_HOJE.flatMap(v => SEMENTES_HOJE.map(s => [v, s])));
  });
  for (const v of VARIANTES_HOJE) for (const s of SEMENTES_HOJE) {
    test(`${v} @${s}: o registro, a assinatura, os motivos do modular e o dec-v2 da ultima decisao; o replay tambem`, () => {
      const g = gab.vidas.find(x => x.variante === v && x.semente === s)!;
      const { m, log } = viverHoje(v, s);
      expect(gravarHoje(v, s, m, log)).toEqual(g);
      const r = Motor.reproduzir(s, log, m.versao);
      expect(gravarHoje(v, s, r, log)).toEqual(g);
    });
  }
});
