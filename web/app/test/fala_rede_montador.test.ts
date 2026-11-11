/* DC4a da CONVERSA_PET (docs/PLANO_ANALISE_V3_CONVERSA_DC4.md, secao 10, item 1): a paridade do espelho Python do montador do pedido da voz
   (experiments/montador_voz_rede.py) com o da pagina (src/falaRede.ts, conceitosDaVoz). O gabarito (test/gabaritos/fala_rede_montador.json.gz,
   experiments/exportar_gabarito_fala_rede.py) traz, por decisao de vidas curtas do LAB+F, o dec-v2 do Python, o conteudo da fala e o pedido que o
   Python montou; aqui o mesmo dec-v2 e o mesmo conteudo passam pelo conceitosDaVoz (com um motor que so devolve os dois) e o pedido tem de ser
   o mesmo. Mais os casos feitos a mao do alvo fora do catalogo. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { conceitosDaVoz, VERSAO_DEC_FALA } from "../src/falaRede.ts";
import type { Motor } from "../motor/index.ts";

interface Caso { origem: string; dec_v2: Record<string, unknown>; conteudo: string | null; pedido: Record<string, unknown> }
const gab = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/fala_rede_montador.json.gz", import.meta.url))).toString("utf8")) as {
  versao: number; classes_alvo: string[]; versao_dec_fala: string; casos: Caso[];
};

/** um motor que so responde as duas leituras que o montador faz */
const motorDe = (c: Caso): Motor => ({ conceitosDec: () => c.dec_v2, conteudoDaFala: () => c.conteudo }) as unknown as Motor;

describe("DC4a: o montador do pedido da voz, Python = pagina", () => {
  test("as constantes e o tamanho do gabarito", () => {
    expect(gab.versao).toBe(1);
    expect(gab.versao_dec_fala).toBe(VERSAO_DEC_FALA);
    expect(gab.casos.filter(c => c.origem === "a_mao").length).toBe(4);
    expect(gab.casos.length).toBeGreaterThan(500);
    for (const p of ["fome", "higiene", "solidao"]) expect(gab.casos.some(c => c.origem !== "a_mao" && c.conteudo === p), p).toBe(true);
  });
  test("cada decisao: o conceitosDaVoz da pagina sai igual ao do Python", () => {
    let n = 0;
    for (const c of gab.casos) {
      expect(conceitosDaVoz(motorDe(c)), `${c.origem} k=${String(c.dec_v2["k"])}`).toEqual(c.pedido);
      n++;
    }
    expect(n).toBe(gab.casos.length);
  });
  test("sem decisao do modular, nada (null nos dois lados)", () => {
    expect(conceitosDaVoz({ conceitosDec: () => null, conteudoDaFala: () => null } as unknown as Motor)).toBeNull();
  });
});
