/* As listas candidatas da rodada de equilibrio do tempo real (fase 2; bots.LISTAS_V14, PROPOSTO): cada uma e uma lista que a forma pode
   ter (as condicoes do estagio, so a tecnica da propria linha, o numero de regras do estagio), as sombrias nao leem o oponente, e
   nenhuma luta dos pets v13 muda (a lista dos bots de hoje e a mesma); a fase 3 semeia o pet com elas (GambitsPet.semear com a lista de
   partida). */
import { describe, expect, test } from "vitest";
import {
  BOTS_V21, CRIANCA_V21, ADOL_V21, CV21, CV21E_TR, GambitsPet, chaveRegra, regraDe, FORMAS_AD, LINHA_DA_FORMA, LISTAS_V14, RIVAL_ESPECIE, SOMBRIA, gambitsAdulto, lutadorBot,
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
  test("o pet pode semear a lista candidata (a bancada da fase 3), e as regras novas tem chave", () => {
    for (const [k, g] of Object.entries(LISTAS_V14)) {
      for (const r of g.regras) expect(regraDe(chaveRegra(r))).toEqual(r);
      const gp = new GambitsPet(), f = formaDe(k);
      gp.semear(f, k, CV21E_TR, g);
      expect(gp.estilo().gambits).toEqual({ regras: g.regras.slice(0, CV21.maxRegras[f.est as keyof typeof CV21.maxRegras]), final: g.final });
      const hoje = new GambitsPet();
      hoje.semear(f, k, CV21E_TR);
      expect(hoje.estilo().gambits).toEqual(sementeDe(f, CV21E_TR));
    }
  });
  test("DE-10: com reservaNoFim, a reserva (a ultima da lista de partida) fica no fim mesmo com a maior nota; sem ela, sobe", () => {
    for (const [k, g] of Object.entries(LISTAS_V14)) {
      const f = formaDe(k), cap = CV21.maxRegras[f.est as keyof typeof CV21.maxRegras];
      if (g.regras.length < 2 || g.regras.length > cap) continue;
      const res = chaveRegra(g.regras[g.regras.length - 1]);
      for (const fixa of [true, false]) {
        const gp = new GambitsPet();
        gp.chipsNoFim = true; gp.reservaNoFim = fixa; gp.semear(f, k, CV21E_TR, g);
        expect(gp.reserva, k).toBe(fixa ? res : null);
        gp.notas[res] = 1e9; gp.ordenar();
        expect(gp.ativas[fixa ? gp.ativas.length - 1 : 0], k).toBe(res);
        expect(gp.listaSozinho()[fixa ? gp.ativas.length - 1 : 0], k).toBe(res);
      }
    }
  });
});
