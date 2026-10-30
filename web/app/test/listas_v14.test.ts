/* As listas candidatas da rodada de equilibrio do tempo real (fase 2; bots.LISTAS_V14, PROPOSTO): cada uma e uma lista que a forma pode
   ter (as condicoes do estagio, so a tecnica da propria linha, o numero de regras do estagio), as sombrias nao leem o oponente, e
   nenhuma luta dos pets v13 muda (a lista dos bots de hoje e a mesma). */
import { describe, expect, test } from "vitest";
import {
  BOTS_V21, CRIANCA_V21, ADOL_V21, CV21, CV21E_TR, FORMAS_AD, LINHA_DA_FORMA, LISTAS_V14, RIVAL_ESPECIE, SOMBRIA, gambitsAdulto, lutadorBot,
  permitida, sementeDe, type Forma, type FormaAdultaNormal,
} from "../motor/index.ts";

/** a forma de cada chave das listas candidatas */
function formaDe(k: string): Forma {
  if (k in CRIANCA_V21) return { esp: "brasa", est: "crianca", ramo: k as Forma["ramo"] };
  if (k in ADOL_V21) return { esp: "brasa", est: "adolescente", linha: k as Forma["linha"] };
  if (k in BOTS_V21) return { esp: RIVAL_ESPECIE[k as FormaAdultaNormal], est: "adulto", linha: LINHA_DA_FORMA[k as FormaAdultaNormal], adulta: k as FormaAdultaNormal };
  const s = SOMBRIA[k];
  if (!s) throw new Error("chave desconhecida nas listas candidatas: " + k);
  return { esp: "brasa", est: "adulto", linha: s.linha, adulta: k as Forma["adulta"] };
}

describe("as listas candidatas da v14 (fase 2)", () => {
  test("cada lista cabe na forma dela", () => {
    expect(Object.keys(LISTAS_V14).length).toBeGreaterThan(0);
    for (const [k, g] of Object.entries(LISTAS_V14)) {
      const f = formaDe(k), est = f.est as keyof typeof CV21.maxRegras;
      expect(g.regras.length, k).toBeLessThanOrEqual(CV21.maxRegras[est]);
      for (const r of g.regras) expect(permitida(r, f), `${k}: ${JSON.stringify(r)}`).toBe(true);
    }
  });
  test("as sombrias nao leem o oponente", () => {
    for (const [k, g] of Object.entries(LISTAS_V14)) if (SOMBRIA[k])
      for (const r of g.regras) expect(r.se.some(c => c.n.startsWith("oponente_")), k).toBe(false);
  });
  test("os pets v13 e os bots de hoje ficam com as listas de hoje", () => {
    for (const f of FORMAS_AD) expect(lutadorBot(f, CV21E_TR).estilo.gambits).toEqual(gambitsAdulto(f, CV21E_TR));
    for (const k of Object.keys(LISTAS_V14)) expect(sementeDe(formaDe(k), CV21E_TR)).not.toEqual(LISTAS_V14[k]);
  });
});
