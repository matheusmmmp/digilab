/* EQUILIBRIO_CUIDADO, E2 (docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md, secao 9): o modo de validacao da bancada. So ele aceita as 94xxx, e
   ele recusa as sementes da calibracao e as de teste; a validacao recusa rodar de novo numa pasta com vidas. Nao roda nenhuma vida da
   validacao (o e2.ts roda uma vez). */
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { AJUSTE_E1_PROPOSTO } from "../motor/equilibrio_e1.ts";
import { BITS_V2 } from "../src/bits.ts";
import { vida } from "../scripts/equilibrio_cuidado/e0.ts";
import { OPCOES_E2, SEMENTES_E2, validar } from "../scripts/equilibrio_cuidado/e2.ts";

describe("o modo de validacao da bancada (E2)", () => {
  test("as sementes sao as cinco da faixa de validacao, e a configuracao e a F2", () => {
    expect([...SEMENTES_E2]).toEqual([94101, 94202, 94303, 94404, 94505]);
    expect(OPCOES_E2).toEqual({ ajuste: AJUSTE_E1_PROPOSTO, bits: BITS_V2, validacao: true });
  });
  test("fora do modo de validacao, as 94xxx falham alto; no modo, a calibracao e o teste falham alto", () => {
    expect(() => vida("pet", "atento", 94101, 1, false, { ajuste: AJUSTE_E1_PROPOSTO })).toThrow(/calibracao/);
    expect(() => vida("pet", "atento", 93101, 1, false, OPCOES_E2)).toThrow(/validacao/);
    expect(() => vida("pet", "atento", 94506, 1, false, OPCOES_E2)).toThrow(/validacao/);
    expect(() => vida("pet", "atento", 101, 1, true, OPCOES_E2)).toThrow(/teste/);
  });
  test("a validacao roda uma vez so: a pasta com vidas falha alto antes de qualquer vida", () => {
    const d = mkdtempSync(join(tmpdir(), "e2-")) + "/";
    try {
      mkdirSync(d, { recursive: true });
      writeFileSync(`${d}pet_atento_94101.json`, "{}\n");
      expect(() => validar(d)).toThrow(/uma vez so/);
    } finally { rmSync(d, { recursive: true, force: true }); }
  });
});
