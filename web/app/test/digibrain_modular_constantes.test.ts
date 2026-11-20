/* As constantes do DigiBrain modular em TS (motor/digibrain/constantes.ts) contra o gabarito da LM0
   (test/gabaritos/digibrain_modular_constantes.json): cada folha igual, e a CONFIG_MODULAR_MUNDO contra o motor e o Python. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import { CMU } from "../motor/constantes.ts";
import { CARACTERISTICAS_DIGIBRAIN, COMPORTAMENTOS_DIGIBRAIN, CONFIG_DIGIBRAIN_LAB, CONFIG_MODULAR_MUNDO, INATOS_MODULAR, RECEPTORES_DIGIBRAIN, TICKS_POR_DIA } from "../motor/digibrain/constantes.ts";
import { constantesModular } from "./digibrain_modular_gabarito.ts";

const py = constantesModular();
const pyBase = JSON.parse(readFileSync(new URL("./gabaritos/constantes_python.json", import.meta.url), "utf8")) as { Config: Record<string, number> };

describe("constantes do DigiBrain modular", () => {
  test("a ConfigDigibrainInatos e igual ao gabarito, folha a folha", () => {
    assert.deepStrictEqual(JSON.parse(JSON.stringify(INATOS_MODULAR)), py["config_digibrain_inatos"]);
    expect(Object.keys(INATOS_MODULAR).length).toBe(Object.keys(py["config_digibrain_inatos"]).length);
  });
  test("a ConfigDigibrain do laboratorio e igual ao gabarito", () => {
    assert.deepStrictEqual(JSON.parse(JSON.stringify(CONFIG_DIGIBRAIN_LAB)), py["config_digibrain"]);
  });
  test("o Config e a ConfigMundo que o M-SENS le", () => {
    expect(CONFIG_MODULAR_MUNDO.intervalo_decisao_ticks).toBe(pyBase.Config!["intervalo_decisao_ticks"]);
    expect(CONFIG_MODULAR_MUNDO.inicio_noite_tick).toBe(pyBase.Config!["inicio_noite_tick"]);
    expect(CONFIG_MODULAR_MUNDO.fim_noite_tick).toBe(pyBase.Config!["fim_noite_tick"]);
    expect(CONFIG_MODULAR_MUNDO.sub).toBe(CMU.sub);
    expect(CONFIG_MODULAR_MUNDO.raio_visao_celulas).toBe(CMU.raio_visao_celulas);
    expect(CONFIG_MODULAR_MUNDO.max_vistos).toBe(CMU.max_vistos);
  });
  test("os receptores, os comportamentos e as caracteristicas na ordem do Python", () => {
    expect(RECEPTORES_DIGIBRAIN.length).toBe(11);
    expect(COMPORTAMENTOS_DIGIBRAIN).toEqual(["ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar"]);
    expect(CARACTERISTICAS_DIGIBRAIN.length).toBe(23);
    expect(CARACTERISTICAS_DIGIBRAIN.slice(12)).toEqual(["noite", "dormindo", "sem_cuidado", "comida_vista", "sem_comida", "bola_vista", "fome_sem_comida", "cuidado_humor", "F", "V", "E"]);
    expect(TICKS_POR_DIA).toBe(1440);
  });
});
