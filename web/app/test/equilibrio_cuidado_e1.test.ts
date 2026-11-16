/* EQUILIBRIO_CUIDADO, E1 (docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E1.md): a bancada com as chaves. Sem chave, a vida do E0 byte a byte; com o
   ajuste e a BITS_V2, a vida roda, muda e continua determinista; a BITS de hoje nao muda; a grade tem as rodadas na ordem. Semente de teste
   (101...505), 1 dia; nao roda a grade (o e1.ts). */
import { describe, expect, test } from "vitest";
import { CONFIG_EQUILIBRIO_CUIDADO } from "../motor/digibrain/constantes.ts";
import { AJUSTE_E1_DESLIGADO, type AjusteEquilibrioE1 } from "../motor/equilibrio_e1.ts";
import { BITS, BITS_V2 } from "../src/bits.ts";
import { vida } from "../scripts/equilibrio_cuidado/e0.ts";
import { GRADE } from "../scripts/equilibrio_cuidado/e1.ts";

const LIGADO: AjusteEquilibrioE1 = {
  ...AJUSTE_E1_DESLIGADO, cerebro: { ...CONFIG_EQUILIBRIO_CUIDADO, guarda_fome_brincar: true, comer_bebe: true }, urgencia_lambda: 768, vies_brincar: 0,
};

describe("a bancada do E1", () => {
  test("sem chave (e com o ajuste desligado e a BITS), a vida do E0 byte a byte", () => {
    for (const versao of ["pet", "grupo"] as const) {
      const e0 = JSON.stringify(vida(versao, "atento", 101, 1, true));
      expect(JSON.stringify(vida(versao, "atento", 101, 1, true, {}))).toBe(e0);
      expect(JSON.stringify(vida(versao, "atento", 101, 1, true, { ajuste: AJUSTE_E1_DESLIGADO, bits: BITS }))).toBe(e0);
    }
  }, 120_000);
  test("com as chaves, a vida muda e segue determinista", () => {
    const a = vida("pet", "atento", 202, 1, true, { ajuste: LIGADO, bits: BITS_V2 }), b = vida("pet", "atento", 202, 1, true, { ajuste: LIGADO, bits: BITS_V2 });
    expect(JSON.stringify(a)).toBe(JSON.stringify(b));
    expect(JSON.stringify(a)).not.toBe(JSON.stringify(vida("pet", "atento", 202, 1, true)));
    expect(a.pets[0]!.morte).toBeNull();
  }, 120_000);
  test("a BITS de hoje nao muda; a BITS_V2 so muda o que o E1 propoe", () => {
    expect([BITS.cuidado, BITS.tetoCuidadoDia, BITS.chamado, BITS.evolucao.crianca, BITS.nivel]).toEqual([1, 20, 2, 50, 30]);
    const mudou = (Object.keys(BITS) as (keyof typeof BITS)[]).filter(k => JSON.stringify(BITS[k]) !== JSON.stringify(BITS_V2[k]));
    expect(mudou.sort()).toEqual(["cuidado", "evolucao", "tetoCuidadoDia"]);
    expect({ ...BITS_V2.evolucao, crianca: BITS.evolucao.crianca }).toEqual(BITS.evolucao);
  });
  test("a grade: a base primeiro, nomes unicos, e a validacao nunca entra", () => {
    expect(GRADE[0]!.nome).toBe("base");
    expect(new Set(GRADE.map(r => r.nome)).size).toBe(GRADE.length);
    expect(() => vida("pet", "atento", 94101, 1, false, { ajuste: LIGADO })).toThrow(/calibracao/);
  });
});
