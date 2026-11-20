/* MMO6: a Fabrica do dia, com as sementes vindas de fora (motor/fabrica.ts, TentativaFabrica.doDia) e a conta pura do desafio
   (src/ranking/desafio.ts). A Fabrica de sempre fica no gabarito (mmo6_fabrica_hoje.test.ts). */
import { describe, expect, test } from "vitest";
import { TentativaFabrica, VERSAO_FABRICA_POC, alugueisFabrica, formaRivalFabrica, sementeFabrica, sementeLutaFabrica } from "../motor/index.ts";
import {
  JOGADORES_PARA_O_PERCENTUAL, RegistroMalformado, TOP_DO_DIA, compararDesafio, lerRegistroDesafio, refazerDesafio, selosDoDia,
} from "../src/ranking/desafio.ts";
import { jogarHoje } from "./mmo6_fabrica_hoje.ts";

const DIA = 2_901_234_567;
const lutasDe = (n: number, k: number) => Array.from({ length: k }, (_, i) => sementeLutaFabrica(sementeFabrica(n), i));

describe("MMO6: a Fabrica do dia no motor", () => {
  test("com as sementes de dentro passadas de fora, a tentativa e a mesma da Fabrica de sempre", () => {
    for (const n of [1, 2, 3, 15, 24]) {
      const hoje = jogarHoje(n, n % 3, n % 4);
      const t = TentativaFabrica.doDia(n % 3, sementeFabrica(n), lutasDe(n, hoje.lutas.length), VERSAO_FABRICA_POC);
      for (const l of hoje.lutas) {
        const x = t.lutar(t.proxima()!.s);
        expect([x.k, x.s, x.venceu, x.vidaFim]).toEqual([l.k, l.s, l.venceu, l.vidaFim]);
        if (x.venceu && hoje.ritmo > 0 && x.k % hoje.ritmo === 0) t.trocar();
      }
      expect([t.vitorias, t.series, t.acabou]).toEqual([hoje.vitorias, hoje.series, hoje.acabou]);
    }
  });
  test("os alugados e os rivais saem da semente do dia; as sementes das lutas, de fora", () => {
    const t = TentativaFabrica.doDia(1, DIA);
    expect(t.ehDoDia).toBe(true);
    expect(new TentativaFabrica(1, 0).ehDoDia).toBe(false);
    expect(t.alugueis).toEqual(alugueisFabrica(DIA));
    expect(t.proximoRival()).toEqual({ k: 0, serie: 1, naSerie: 1, rival: formaRivalFabrica(DIA, 0) });
    expect(t.sementesRecebidas).toBe(0);
    expect(() => t.proxima()).toThrow(/ainda não veio do servidor/);
    t.receberSemente(0, 77);
    expect(t.proxima()).toMatchObject({ k: 0, s: 77 });
    expect(() => t.lutar(78)).toThrow(/tem a semente 77/);
  });
  test("as sementes chegam em ordem e sao inteiros sem sinal de 32 bits", () => {
    const t = TentativaFabrica.doDia(0, DIA);
    expect(() => t.receberSemente(1, 5)).toThrow(/fora de ordem/);
    expect(() => t.receberSemente(0, -1)).toThrow(/inválida/);
    expect(() => t.receberSemente(0, 2 ** 32)).toThrow(/inválida/);
    expect(() => TentativaFabrica.doDia(0, 1.5)).toThrow(/semente do dia/);
    expect(() => new TentativaFabrica(1, 0).receberSemente(0, 1)).toThrow(/Fábrica de sempre/);
    expect(() => new TentativaFabrica(1, 0).sementesRecebidas).toThrow(/Fábrica de sempre/);
  });
});

describe("MMO6: a conta do desafio", () => {
  test("a forma do registro", () => {
    const ok = { v: VERSAO_FABRICA_POC, escolha: 2, lutas: [1, 2], trocas: [0] };
    expect(lerRegistroDesafio(ok)).toEqual(ok);
    for (const ruim of [null, [], { ...ok, vitorias: 3 }, { ...ok, escolha: 3 }, { ...ok, lutas: [-1] }, { ...ok, lutas: [2 ** 32] },
      { ...ok, trocas: [1, 1] }, { ...ok, trocas: [2, 1] }, { ...ok, v: "21" }, { v: 21, escolha: 0, lutas: [] }])
      expect(() => lerRegistroDesafio(ruim), JSON.stringify(ruim)).toThrow(RegistroMalformado);
  });
  test("refaz pelo motor e falha alto no registro impossivel", () => {
    const n = 15, hoje = jogarHoje(n, n % 3, 0);
    const r = refazerDesafio(sementeFabrica(n), { v: VERSAO_FABRICA_POC, escolha: n % 3, lutas: lutasDe(n, hoje.lutas.length), trocas: [] });
    expect(r.resultado).toMatchObject({ vitorias: hoje.vitorias, series: hoje.series, lutas: hoje.lutas.length, acabou: hoje.acabou });
    expect(r.resultado.vitorias > 0 ? r.resultado.vidaUltimaVitoria > 0 : r.resultado.vidaUltimaVitoria === 0).toBe(true);
    const base = { v: VERSAO_FABRICA_POC, escolha: n % 3, lutas: lutasDe(n, hoje.lutas.length), trocas: [] as number[] };
    expect(() => refazerDesafio(sementeFabrica(n), { ...base, v: 13 })).toThrow(/versão/);
    expect(() => refazerDesafio(sementeFabrica(n), { ...base, lutas: lutasDe(n, hoje.lutas.length + 1) })).toThrow(/já acabou/);
    expect(() => refazerDesafio(sementeFabrica(n), { ...base, trocas: [hoje.lutas.length] })).toThrow(/troca depois da luta/);
  });
  test("o desempate e o selo", () => {
    const l = (vitorias: number, vidaUltimaVitoria: number, terminouEm: number) => ({ vitorias, vidaUltimaVitoria, terminouEm });
    expect([l(1, 9, 0), l(3, 1, 9), l(3, 5, 9), l(3, 5, 2)].sort(compararDesafio)).toEqual([l(3, 5, 2), l(3, 5, 9), l(3, 1, 9), l(1, 9, 0)]);
    expect(TOP_DO_DIA).toBe(10);
    expect(selosDoDia(4)).toBe(4);
    expect(selosDoDia(500)).toBe(10);
    expect(selosDoDia(JOGADORES_PARA_O_PERCENTUAL)).toBe(10);
    expect(selosDoDia(2_345)).toBe(24);
  });
});
