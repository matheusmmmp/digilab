/* O gabarito das lutas em tempo real de hoje (docs/TAREFA_V3_LUTA_EMPURRAO.md, etapa 2): as lutas das regras v13 e v14 saem iguais ao
   gabarito gravado antes do empurrao novo (test/gabaritos/luta_tr_hoje.json.gz, por test/luta_tr_hoje.ts --gravar), o estado passo a
   passo inclusive. Nunca regravar este gabarito para fazer um teste passar: se ele quebrar, a luta de hoje mudou. */
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { describe, expect, test } from "vitest";
import { NPCS, SEMENTES, assinatura, todas, type LutaGravada } from "./luta_tr_hoje.ts";

const gab = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/luta_tr_hoje.json.gz", import.meta.url))).toString("utf8")) as
  { sementes: number[]; npcs: string[]; lutas: LutaGravada[]; assinatura: string };

describe("as lutas em tempo real de hoje (v13 e v14) nao mudam", () => {
  test("o gabarito e o do gerador de hoje (as sementes, os NPCs e a assinatura)", () => {
    expect(gab.sementes).toEqual([...SEMENTES]); expect(gab.npcs).toEqual([...NPCS]);
    expect(assinatura(gab.lutas)).toBe(gab.assinatura);
  });
  test("cada luta sai igual, passo a passo", () => {
    const agora = todas();
    expect(agora.length).toBe(gab.lutas.length);
    for (let i = 0; i < agora.length; i++) expect(agora[i], `${gab.lutas[i].regras} ${gab.lutas[i].a} x ${gab.lutas[i].b} @${gab.lutas[i].semente}`).toEqual(gab.lutas[i]);
  }, 120_000);
});
