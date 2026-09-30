// Escala de stats no motor TS (TAREFA_PLANILHA_PROGRESSAO, Parte C; espelho de tests/test_escala.py). A chave
// desligada nao muda a luta; com ela ligada, a mesma escala multiplicada nos dois lados da a mesma luta (na web a
// razao E_A/E_B e float: os fatores do teste sao potencias de 2, exatas; o Python confere 2, 10 e 37 com fracoes).
import { afterEach, test } from "vitest";
import assert from "node:assert/strict";
import * as M from "../motor/index.ts";

afterEach(() => M.ligarEscala(false));

const pet = (est, pontos = 0) => {
  const f = est === "crianca" ? { esp: "brasa", est, ramo: "sereno" }
    : est === "adolescente" ? { esp: "brasa", est, ramo: "sereno", linha: "brigao" }
      : { esp: "brasa", est, ramo: "sereno", linha: "brigao", adulta: "duelista" };
  const tr = pontos ? Object.fromEntries(M.STATS.map(k => [k, pontos / 6])) : null;
  return { nome: "pet", estilo: M.estiloBot("agressivo"), cond: M.perfilDe(f, null, 1, tr, true) };
};
const escalado = (L, k) => ({ ...L, cond: { ...L.cond, escala: L.cond.escala * k } });
const luta = r => JSON.stringify(r.turnos.map(t => [t.a, t.b, t.dano, t.depois.L.map(l => l.hp)]).concat([r.pontosA, r.fim]));

test("escala desligada: o NPC e o pet da campanha sao os de sempre", () => {
  assert.equal(M.ESCALA.ligada, false);
  const npc = M.lutadorBot("npc_tier1_brutamontes");
  assert.equal(npc.cond.escala, undefined);
  assert.equal(pet("crianca", 8).cond.escala, undefined);
});

test("escala ligada: mesmo fator nos dois lados = mesma luta", () => {
  M.ligarEscala(true);
  const npc = M.lutadorBot("npc_tier1_brutamontes");
  assert.equal(npc.cond.escala, 200 * 1.1);
  for (const [a, b] of [[pet("crianca", 8), npc], [pet("adulto"), pet("adolescente", 22)]]) {
    for (const s of [4101, 4202, 4303]) {
      const base = luta(M.jogarV2(a, b, s));
      for (const k of [2, 8, 64]) assert.equal(luta(M.jogarV2(escalado(a, k), escalado(b, k), s)), base);
    }
  }
});

test("escala ligada: o treino sobe a escala (beta) e a vida exibida cresce do bebe ao adulto", () => {
  M.ligarEscala(true);
  assert.equal(M.escalaDe("crianca", 8), 200 * (1 + 0.03 * 8));
  const vb = M.vidaExibida(M.perfilDe({ esp: "brasa", est: "bebe" }, null));
  const va = M.vidaExibida(pet("adulto").cond);
  assert.ok(vb > 40 && vb < 60, `bebê ${vb}`);
  assert.ok(va > 1300 && va < 1700, `adulto ${va}`);
});

/* escala dos pets v6 (CESC_V6, 2026-09-30): so o pet v6 (pela versao) e o NPC nas lutas V21D (pelas regras) usam a escala
   propria; a CESC (pets v1-v5) nao muda */
test("escala v6: o pet v6 e o NPC da luta V21D usam a CESC_V6; os v1-v5, a CESC", () => {
  M.ligarEscala(true);
  const { CESC, CESC_V6, CV21D, VERSAO_ESCALA_V6 } = M;
  assert.equal(VERSAO_ESCALA_V6, 6);
  for (const est of ["crianca", "adolescente", "adulto"]) {
    assert.equal(M.escalaDe(est, 22), CESC.vida[est] * (1 + CESC.beta * 22));
    assert.equal(M.escalaDe(est, 22, 5), CESC.vida[est] * (1 + CESC.beta * 22));
    assert.equal(M.escalaDe(est, 22, 6), CESC_V6.vida[est] * (1 + CESC_V6.beta * 22));
  }
  assert.equal(M.escalaDe("mega", 40), M.CMG.vida * (1 + CESC.beta * 40));
  assert.equal(M.escalaDe("mega", 40, 6), CESC_V6.vida.mega * (1 + CESC_V6.beta * 40));
  const f = { esp: "brasa", est: "adolescente", ramo: "sereno", linha: "brigao" }, tr = Object.fromEntries(M.STATS.map(k => [k, 22 / 6]));
  assert.equal(M.perfilDe(f, null, 1, tr, true).escala, M.escalaDe("adolescente", 22));
  assert.equal(M.perfilDe(f, null, 1, tr, true, 6).escala, M.escalaDe("adolescente", 22, 6));
  /* o NPC: fora da V21D a escala de sempre; com as regras dos pets v6, a vida da CESC_V6 */
  assert.equal(M.lutadorBot("npc_tier2_porteiro").cond.escala, CESC.vida.adolescente * CESC.fatorNpc.npc_tier2_porteiro);
  const dev6 = M.lutadorBot("npc_tier2_porteiro", CV21D).cond.escala;
  assert.equal(dev6, CESC_V6.vida.adolescente * (CESC_V6.fatorNpc.npc_tier2_porteiro ?? CESC.fatorNpc.npc_tier2_porteiro));
  /* a exibicao segue a versao */
  const pa = M.perfilDe(f, null);
  assert.equal(M.vidaExibida(pa, "adolescente", 0, 6) / M.vidaExibida(pa, "adolescente", 0), CESC_V6.vida.adolescente / CESC.vida.adolescente);
});
