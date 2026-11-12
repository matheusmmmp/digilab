// As chaves da N3 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 4; D-N-5, "As 4 (Recommended)", Matheus, 2026-11-12):
// cada uma desligada sem o campo na entrada (o gabarito test/luta_nucleo_n3_gabarito.test.ts confere as lutas de antes), a regra de cada
// uma ligada e o replay bit a bit com ela.
import { describe, expect, test } from "vitest";
import { OPCOES_PADRAO, configLuta, criarLuta, rodarAteOFim, sorteiosPorFluxo, type EntradaLuta, type Evento } from "../motor/arena/index.ts";
import { LUTA_V23 } from "../motor/luta_poc.ts";
import { resumoLutaLp6 } from "./arena_lp6_lutas.ts";
import { entradaDaTabela } from "./luta_nucleo_n3_lutas.ts";

/** os eventos de uma luta inteira */
function eventos(e: EntradaLuta): Evento[] {
  const L = criarLuta(configLuta(e), sorteiosPorFluxo(e.semente)), ev: Evento[] = [];
  rodarAteOFim(L, x => { ev.push(...x); });
  return ev;
}
/* o Agumon (Vaccine) contra o Guilmon (Virus): o Vaccine tem a vantagem */
const AGU_GUI = entradaDaTabela(LUTA_V23, "campo", "brasa_crianca_sereno", "brasa_crianca_arisco", 101);

describe("a chave forcaAtr (a vantagem do atributo na entrada)", () => {
  test("sem ela, a forca e a do OPCOES_PADRAO; com 1,5, a luta e a mesma", () => {
    expect(configLuta(AGU_GUI).forca).toBe(OPCOES_PADRAO.forca);
    expect(resumoLutaLp6({ ...AGU_GUI, forcaAtr: OPCOES_PADRAO.forca })).toEqual(resumoLutaLp6(AGU_GUI));
  });
  test("com 1, o triangulo nao pesa: todo dano sai com mult 1", () => {
    const ev = eventos({ ...AGU_GUI, forcaAtr: 1 }).filter(x => x.tipo === "dano");
    expect(ev.length).toBeGreaterThan(0);
    for (const x of ev) if (x.tipo === "dano") expect(x.mult).toBe(1);
    const de = eventos(AGU_GUI).filter(x => x.tipo === "dano").map(x => x.tipo === "dano" ? x.mult : 0);
    expect(de).toContain(1.5);
  });
  test("o valor entra no mult do dano (1,25 e 1/1,25)", () => {
    const ms = new Set(eventos({ ...AGU_GUI, forcaAtr: 1.25 }).flatMap(x => x.tipo === "dano" ? [x.mult] : []));
    for (const m of ms) expect([1.25, 1 / 1.25]).toContain(m);
  });
  test("fora da faixa falha alto", () => {
    for (const x of [0.99, 3.01, Number.NaN, Infinity]) expect(() => configLuta({ ...AGU_GUI, forcaAtr: x })).toThrow(/vantagem do atributo invalida/);
  });
  test("o replay bit a bit com ela ligada", () => {
    const e = { ...AGU_GUI, forcaAtr: 1.15 };
    expect(resumoLutaLp6(e)).toEqual(resumoLutaLp6(e));
  });
});
