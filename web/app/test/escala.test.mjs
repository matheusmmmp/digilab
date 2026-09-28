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
