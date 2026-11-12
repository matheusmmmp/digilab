/* MMO2 (docs/PLANO_V3_MMO.md, secao 12; MMO-13 e P-5 opcao T): o marco 10 do nivel do Tamer, o primeiro Mega, e o evento "nivel" no
   registro do Tamer (versao 10, que le as de antes). O pet Mega e de teste: a evolucao a Mega e posta a mao no registro das evolucoes
   (chegar ao Mega pelo motor leva dias de vida simulada); a conta do marco so le essa lista. */
import { describe, expect, test } from "vitest";
import { Motor, nomeForma } from "../motor/index.ts";
import { CHAVE_TAMER, MARCO_MEGA, Tamer, conferirMarcoMega, evolucaoMega, gravarTamer, lerTamer, marcoConfere, type EventoTamer } from "../src/tamer.ts";
import { ULTIMO_MARCO, cartoesPendentes, lerEstado, marcosDoPet, marcosDoTamer, marcosFeitos, sincronizar } from "../src/nivel.ts";

const armaz = (dados: Record<string, string> = {}) => ({
  dados, getItem: (k: string) => dados[k] ?? null, setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; },
});
/** um pet de teste com a evolucao a Mega no tick dado */
function petMega(semente: number, tick: number): Motor {
  const m = new Motor(semente);
  m.evolucoes.push({ tick, estagio: "mega", forma: { ...m.forma } });
  return m;
}

describe("MMO2: o marco 10, o primeiro Mega", () => {
  test("o ultimo marco e o 10; o pet sem Mega nao o tem, o pet Mega tem", () => {
    expect(ULTIMO_MARCO).toBe(10);
    expect(marcosDoPet(new Motor(7))).not.toContain(MARCO_MEGA);
    expect(marcosDoPet(petMega(7, 9000))).toContain(MARCO_MEGA);
  });
  test("o marco vai para o registro uma vez, com o pet e o tick da evolucao; o Tamer passa a ter o marco mesmo sem o pet", () => {
    const t = new Tamer(), sem = new Motor(6), mega = petMega(7, 9000);
    expect(conferirMarcoMega(t, [sem])).toBeNull();
    const x = conferirMarcoMega(t, [sem, mega], 1234)!;
    expect(x).toEqual({ n: 10, quando: 1234, pet: 7, forma: nomeForma(mega.forma), tick: 9000 });
    expect(conferirMarcoMega(t, [petMega(8, 100)])).toBeNull();     // o primeiro fica
    expect(marcosDoTamer(t)).toContain(MARCO_MEGA);
    expect(marcosFeitos([], t)).toEqual([MARCO_MEGA]);
  });
  test("a conferencia do servidor: o pet refeito tem a Mega no tick do marco", () => {
    const t = new Tamer(), mega = petMega(7, 9000), x = conferirMarcoMega(t, [mega])!;
    expect(marcoConfere(x, mega)).toBe(true);
    expect(marcoConfere({ ...x, tick: 9001 }, mega)).toBe(false);
    expect(marcoConfere({ ...x, pet: 8 }, mega)).toBe(false);
    expect(marcoConfere(x, new Motor(7))).toBe(false);
    expect(evolucaoMega(new Motor(7))).toBeNull();
  });
  test("gravar e ler: versao 10, o mesmo estado", () => {
    const t = new Tamer(), a = armaz();
    conferirMarcoMega(t, [petMega(7, 9000)], 55);
    gravarTamer(a, t);
    expect(JSON.parse(a.dados[CHAVE_TAMER]).versao).toBe(10);
    expect(lerTamer(a).marco(MARCO_MEGA)).toEqual(t.marco(MARCO_MEGA));
  });
  test("o registro 9 de antes abre (e grava como 10); com o evento \"nivel\" ele falha alto", () => {
    const med: EventoTamer = ["medalha", { id: "campina", n: 1, quando: 1, pet: 1, forma: "Agumon", tick: 480 }];
    const a = armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 9, log: [med] }) });
    const t = lerTamer(a);
    expect(t.n).toBe(1);
    gravarTamer(a, t);
    expect(JSON.parse(a.dados[CHAVE_TAMER])).toEqual({ versao: 10, log: [med] });
    const nv: EventoTamer = ["nivel", { n: 10, quando: 2, pet: 7, forma: "Agumon", tick: 9000 }];
    expect(() => lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 9, log: [med, nv] }) }))).toThrow(/versão 10/);
  });
  test("falha alto: o marco que nao vai ao registro, o repetido e o sem campos", () => {
    const nv = (x: object): EventoTamer => ["nivel", { n: 10, quando: 2, pet: 7, forma: "Agumon", tick: 9000, ...x }] as EventoTamer;
    expect(() => Tamer.reproduzir([nv({ n: 9 })])).toThrow(/não vai ao registro/);
    expect(() => Tamer.reproduzir([nv({}), nv({ pet: 8 })])).toThrow(/repetido/);
    expect(() => Tamer.reproduzir([nv({ tick: undefined })])).toThrow(/sem tick/);
    expect(() => Tamer.reproduzir([nv({ forma: "" })])).toThrow(/sem a forma/);
  });
  test("a vista: o estado aceita o 10 e nao o 11; o 10 conta no nivel e nao pede cartao (espera a prancha)", () => {
    expect(lerEstado(JSON.stringify({ marcos: [1, 10], cartoes: [1] }))!.marcos).toEqual([1, 10]);
    expect(() => lerEstado(JSON.stringify({ marcos: [11], cartoes: [] }))).toThrow();
    const r = sincronizar({ marcos: [1, 2, 3], cartoes: [1, 2, 3] }, [1, 2, 3, 10], true);
    expect(r.novos).toEqual([10]);
    expect(r.estado.marcos.length).toBe(4);
    expect(cartoesPendentes(r.estado)).toEqual([]);
  });
});
