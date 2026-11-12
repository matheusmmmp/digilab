/* O G-PAR-CO7 (docs/ESPEC_V3_COOPERACAO_CO7.md, secao 6): as contas da CO7 do motor/digibrain/dever.ts repetem as do Python
   (digilab/digibrain/dever.py), decisao a decisao, bit a bit no Node, contra o gabarito de experiments/exportar_gabarito_co7_par.py
   (co7_python.json.gz): em cada decisao do modular das seis vidas com a CO7 ligada, a percepcao social em posicoes absolutas, a situacao
   (as comidas proibidas, a privacao, o escudo, o delta e a unica), os pesos depois do escudo e da universalizacao e a culpa e a inveja,
   com as mesmas entradas. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CCOOP } from "../motor/constantes.ts";
import { CONFIG_COOPERACAO, CONFIG_COOPERACAO_CO6, CONFIG_COOPERACAO_CO7, Cooperacao } from "../motor/cooperacao.ts";
import { ajustarDever, culpaInveja, situacaoDever, socialDever, type SensDever, type SituacaoDever } from "../motor/digibrain/dever.ts";

type Rec = Record<string, unknown>;
type Chamada =
  | { f: "social"; ps: Rec | null; pos: [number, number]; antes: Record<string, [number, number]>; r: number; out: unknown }
  | { f: "situacao"; sens: SensDever; urgencias: Record<string, number>; out: unknown }
  | { f: "ajustar"; chaves: unknown[][]; w: number[]; sit: SituacaoDever; out: unknown }
  | { f: "culpa_inveja"; sens: SensDever; out: [number, number] };
interface Vida { semente: number; cerebro_b: string; lugar: string; chamadas: Chamada[]; escolhas: Record<string, [string, unknown[], Rec | null][]> }
const G = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/co7_python.json.gz", import.meta.url))).toString("utf8")) as { vidas: Vida[] };
const comoJson = (v: unknown): unknown => JSON.parse(JSON.stringify(v));
const S = CCOOP.escala;

describe("a config da CO7", () => {
  test("o CCOOP da CO7 e a ConfigCooperacao do Python, e a chave desligada", () => {
    const py = (JSON.parse(readFileSync(new URL("./gabaritos/constantes_python.json", import.meta.url), "utf8")) as Record<string, Rec>).ConfigCooperacao!;
    expect([CCOOP.limiarEscudo, CCOOP.rEscudoCelulas, CCOOP.pisoPrivacaoS, CCOOP.wUniv, CCOOP.limiarHumor, CCOOP.wCulpa, CCOOP.wInveja, CCOOP.janelaInveja])
      .toEqual([py.limiar_escudo, py.r_escudo_celulas, py.piso_privacao_s, py.w_univ, py.limiar_humor, py.w_culpa, py.w_inveja, py.janela_inveja]);
    expect(py.co7).toBe(false);
    expect([CONFIG_COOPERACAO.co7, CONFIG_COOPERACAO_CO6.co7, CONFIG_COOPERACAO_CO7.co7]).toEqual([false, false, true]);
    expect(() => new Cooperacao({ ...CONFIG_COOPERACAO_CO6, co6: false, co7: true })).toThrow(/co7 so liga/);
  });
});

describe("o G-PAR-CO7", () => {
  test("o gabarito tem as seis vidas, com o escudo valendo, a universalizacao que reprova e a que aprova, a culpa e a inveja", () => {
    expect(G.vidas.length).toBe(6);
    const ds = G.vidas.flatMap(v => Object.values(v.escolhas).flat().map(e => e[2]).filter((d): d is Rec => d !== null));
    expect(ds.filter(d => d.escudo && (d.proibidas as unknown[]).length).length).toBeGreaterThan(0);
    expect(ds.some(d => (d.reprovadas as unknown[]).length > 0)).toBe(true);
    expect(ds.some(d => (d.aprovadas as number) > 0)).toBe(true);
    expect(ds.some(d => (d.culpa as number) > 0) && ds.some(d => (d.inveja as number) > 0)).toBe(true);
  });

  for (const v of G.vidas) {
    test(`vida ${v.semente} (${v.cerebro_b}, ${v.lugar}): cada conta, com as entradas do Python`, () => {
      const cfg = CONFIG_COOPERACAO_CO7;
      for (const [n, c] of v.chamadas.entries()) {
        const onde = `${v.semente}/${v.cerebro_b}/${v.lugar}, chamada ${n} (${c.f})`;
        if (c.f === "social") {
          const ps = c.ps === null ? null : { outros: c.ps.outros as never, onde_comeu: c.ps.onde_comeu as never, peso_dever: c.ps.peso_dever as number };
          expect(comoJson(socialDever(ps, c.pos, c.antes, c.r)), onde).toEqual(c.out);
        } else if (c.f === "situacao") {
          expect(comoJson(situacaoDever(c.sens, c.urgencias, cfg, S)), onde).toEqual(c.out);
        } else if (c.f === "ajustar") {
          expect(comoJson(ajustarDever(c.chaves, c.w, c.sit)), onde).toEqual(c.out);
        } else {
          expect(culpaInveja(c.sens, cfg), onde).toEqual(c.out);
        }
      }
    });
  }
});
