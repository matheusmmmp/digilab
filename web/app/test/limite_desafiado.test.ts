// Regra do limite de turnos (decisao do Matheus, 2026-09-30, so no jogo): a luta que chega ao limite sem KO e de quem foi
// desafiado. Nas lutas do motor do pet v13 o pet (lado A) sempre desafia: no limite (80 s em tempo real), derrota do pet.
// A regra deriva da versao do pet (nada novo no registro). As funcoes por turnos (fimV2, jogarArena com CV21D) seguem testadas.
import { describe, expect, test } from "vitest";
import { CV, CV21D, CV21E_TR, desafiadoDaVersao, estadoV2, fimV2, hashSemente, jogarArena, jogarLuta, perfilNeutro } from "../motor/index.ts";
import { Motor } from "../motor/motor.ts";

describe("limite de turnos: vence quem foi desafiado (pet v13)", () => {
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
    expect(desafiadoDaVersao(13)).toBe(1);
  });
  test("luta de pet v13 que chega ao limite (80 s) e derrota do pet", () => {
    const m = new Motor(31);
    m.avancar(60);                                               /* bebe: luta ao acaso e chega ao limite com a tartaruga */
    const { A, B } = m.lutadores("tartaruga"), R = m.regras;
    expect(R).toBe(CV21E_TR);
    let achou = false;
    for (let k = 0; k < 400 && !achou; k++) {
      const s = hashSemente("limite", 13, k), livre = jogarLuta(A, B, s, R);
      if (livre.fim !== "limite" || livre.pontosA !== 1) continue;
      achou = true;                                              /* no limite com o pet na frente pela fracao de vida */
      const doMotor = m.montarLuta("tartaruga", s).serie[0];
      expect(doMotor.tr!.acoes).toEqual(livre.tr!.acoes);       /* a regra so muda quem fica com a luta */
      expect(doMotor.fim).toBe("limite");
      expect(doMotor.pontosA).toBe(0);
      expect(doMotor).toEqual(jogarArena(A, B, s, R, 1, 1)[0]);
    }
    expect(achou).toBe(true);
  });
  test("na serie da Cidadela, a luta que chega ao limite quebra a serie", () => {
    const m = new Motor(31);
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
