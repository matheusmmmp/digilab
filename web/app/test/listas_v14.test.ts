/* As listas candidatas da rodada de equilibrio do tempo real (fase 2; bots.LISTAS_V14, PROPOSTO): cada uma e uma lista que a forma pode
   ter (as condicoes do estagio, so a tecnica da propria linha, o numero de regras do estagio), as sombrias nao leem o oponente, e
   nenhuma luta dos pets v13 muda (a lista dos bots de hoje e a mesma); a fase 3 semeia o pet com elas (GambitsPet.semear com a lista de
   partida). */
import { describe, expect, test } from "vitest";
import {
  APRENDIZADO_V14, CESC_V9, RELOGIO_V14, comCarta, jogarTR, FATOR_INSTALACAO, FATOR_LIDER_V9, FATOR_LIGA_V9, FATOR_RIVAL_FABRICA_V9, FATOR_SALAO_V9, FATORES_V14,
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
  test("os fatores candidatos (fase 4) tem as chaves das tabelas de hoje, e as de hoje ficam (os pets v13)", () => {
    expect(Object.keys(FATORES_V14.lider).sort()).toEqual(Object.keys(FATOR_LIDER_V9).sort());
    expect(Object.keys(FATORES_V14.npc).sort()).toEqual(Object.keys(CESC_V9.fatorNpc).sort());
    expect(Object.keys(FATORES_V14.liga).sort()).toEqual(Object.keys(FATOR_LIGA_V9).sort());
    expect(Object.keys(FATORES_V14.salao).sort()).toEqual(Object.keys(FATOR_SALAO_V9).sort());
    expect([FATOR_LIDER_V9.torre, CESC_V9.fatorNpc.npc_tier2_sentinela, FATOR_LIGA_V9.campina, FATOR_SALAO_V9.adolescente, FATOR_INSTALACAO, FATOR_RIVAL_FABRICA_V9])
      .toEqual([1.5, 1.53, .4, 1, 1, .6]);
  });
  test("DR2-5: o aprendizado proprio do tempo real so muda a ordem com o prior, e sem ele (null) a ordem e so pela nota", () => {
    expect(APRENDIZADO_V14).not.toBeNull();
    const f = formaDe("sentinela"), g = LISTAS_V14.sentinela, ultima = chaveRegra(g.regras[g.regras.length - 2]);
    for (const prior of [0, 1]) {
      const gp = new GambitsPet();
      gp.chipsNoFim = true; gp.aprendizadoTR = { alfa: .2, prior }; gp.semear(f, "sentinela", CV21E_TR, g);
      /* a penultima sobe pela nota: so o prior grande a segura no lugar */
      gp.notas[ultima] += .5; gp.ordenar();
      expect(gp.ativas.indexOf(ultima) === 0, String(prior)).toBe(prior === 0);
    }
    const hoje = new GambitsPet();
    hoje.chipsNoFim = true; hoje.semear(f, "sentinela", CV21E_TR, g); hoje.notas[ultima] += .5; hoje.ordenar();
    expect(hoje.ativas[0]).toBe(ultima);
  });
  test("DR2-4: a carta candidata pode passar o guts do maximo (gutsTeto) e dar ao pet um ritmo proprio; sem elas, a carta de hoje", () => {
    const R = { ...CV21E_TR, relogio: RELOGIO_V14 }, A = lutadorBot("duelista", R), B = lutadorBot("tita", R);
    const max = A.cond.gutsMax, folego = comCarta(A, { guts: 2 * max, gutsTeto: 1.5 });
    expect(folego.cond.guts0).toBe(1.5 * max);
    expect(comCarta(A, { guts: 2 * max }).cond.guts0).toBe(max);
    expect(() => comCarta(A, { ritmo: 1.5 })).toThrow(/inteiro/);
    const n = (L: typeof A) => jogarTR(L, B, 7, { R }).acoes.filter(a => a.lado === 0).length;
    expect(n(comCarta(A, { foco: true, ritmo: 4 }))).toBeGreaterThan(n(comCarta(A, { foco: true })));
    expect(comCarta(A, { foco: true }).cond.ritmoCarta).toBeUndefined();
  });
});
