// Regra do limite de turnos (decisao do Matheus, 2026-09-30, so no jogo): a luta que chega ao limite sem KO e de quem foi
// desafiado. Nas lutas do motor dos pets v6 o pet (lado A) sempre desafia: no limite, derrota do pet. Pets v1-v5: a fracao de
// vida decide, como sempre. A regra deriva da versao do pet (nada novo no registro).
import { describe, expect, test } from "vitest";
import { CV, CV21D, desafiadoDaVersao, estadoV2, fimV2, hashSemente, jogarArena, jogarV2, perfilNeutro } from "../motor/index.ts";
import { Motor } from "../motor/motor.ts";

describe("limite de turnos: vence quem foi desafiado (pets v6)", () => {
  test("fimV2: no limite, sem desafiado a fracao de vida; com desafiado, ele", () => {
    const E0 = estadoV2(perfilNeutro(), perfilNeutro());
    const E = { ...E0, turno: CV.tMax, L: [{ ...E0.L[0], hp: E0.L[0].hpMax }, { ...E0.L[1], hp: 1 }] };
    expect(fimV2(E)).toEqual([1, "limite"]);
    expect(fimV2(E, 1)).toEqual([0, "limite"]);
    expect(fimV2(E, 0)).toEqual([1, "limite"]);
    /* KO decide antes do limite, com ou sem desafiado */
    const ko = { ...E, L: [E.L[0], { ...E.L[1], hp: 0 }] };
    expect(fimV2(ko, 1)).toEqual([1, "ko"]);
    expect(desafiadoDaVersao(6)).toBe(1);
    for (const v of [1, 2, 3, 4, 5]) expect(desafiadoDaVersao(v)).toBeNull();
  });
  test("luta de pet v6 que chega ao limite e derrota do pet; a de pet v5, decidida pela fracao de vida como hoje", () => {
    for (const versao of [5, 6]) {
      const m = new Motor(31, versao);
      m.avancar(60);                                             /* bebe: luta ao acaso e chega ao limite com a tartaruga */
      const { A, B } = m.lutadores("tartaruga"), R = m.regras;
      let achou = false;
      for (let k = 0; k < 400 && !achou; k++) {
        const s = hashSemente("limite", versao, k), livre = jogarV2(A, B, s, R);
        if (livre.fim !== "limite" || livre.pontosA !== 1) continue;
        achou = true;                                            /* no limite com o pet na frente pela fracao de vida */
        const doMotor = m.montarLuta("tartaruga", s).serie[0];
        expect(doMotor.turnos).toEqual(livre.turnos);          /* a regra so muda quem fica com a luta */
        expect(doMotor.fim).toBe("limite");
        expect(doMotor.pontosA).toBe(versao >= 6 ? 0 : 1);
        expect(doMotor).toEqual(jogarArena(A, B, s, R, 1, versao >= 6 ? 1 : null)[0]);
      }
      expect(achou).toBe(true);
    }
  });
  test("na serie da Cidadela, a luta que chega ao limite quebra a serie", () => {
    const m = new Motor(31, 6);
    m.avancar(60);
    const { A, B } = m.lutadores("tartaruga");
    for (let k = 0; k < 400; k++) {
      const s = hashSemente("serie-limite", k), serie = jogarArena(A, B, s, CV21D, 3, 1);
      const i = serie.findIndex(r => r.fim === "limite");
      if (i < 0) continue;
      expect(serie).toHaveLength(i + 1);
      expect(serie[i].pontosA).toBe(0);
      return;
    }
    throw new Error("nenhuma serie chegou ao limite");
  });
});
