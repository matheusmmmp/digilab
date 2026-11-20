/* CORPO C3, a ponte com teto em TS (docs/PLANO_ANALISE_V3_CORPO_C3.md, secoes 2 e 7; D-C3-1 e D-C3-2): com a D ligada e a
   ConfigTetoFomeCorpo, a fome so sobe pela falta de combustivel ate o teto. motor/corpo.ts reproduz, inteiro a inteiro, o gabarito do
   Python (tests/gabaritos/corpo_teto_python.json, de experiments/exportar_gabarito_corpo_teto.py): o DTL (teto no limiar da privacao)
   e o DTB (teto em C/2) nos corpos v11 (sem e com o mundo) e etapa6_mundo; a grade (q, janela, resto, contas, ticks_teto, receptores)
   e a sequencia longa com o sha256. Sem o teto (o padrao), o corpo e o da D de hoje: o corpo_acoplamento.test.ts confere. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CMU, type ConfigCorpo } from "../motor/constantes.ts";
import {
  CCO_CORPO_V11, CCO_METABOLISMO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_TETO_FOME_BAIXO, CONFIG_TETO_FOME_CORPO, CONFIG_TETO_FOME_LIMIAR,
  Corpo, conferirConfigTetoFome, type ConfigTetoFomeCorpo, type ContaMetabolismo,
} from "../motor/corpo.ts";
import { sha256 } from "../motor/mundo.ts";
import type { AcaoPet } from "../motor/tipos.ts";

type Rec = Record<string, unknown>;
type Op = (string | number)[];
type Contas = Record<ContaMetabolismo, number>;
interface Caso {
  q: number[]; janela: string[]; resto: number; op: Op; q_depois: number[]; janela_depois: string[]; resto_depois: number; contas: Contas;
  ticks_teto: number; receptores: number[];
}
interface Secao {
  config: Rec; com_mundo: boolean; quimicos: string[]; receptores: string[]; teto: number; casos: Caso[];
  sequencia: { ops: Op[]; sha256: string; q_final: number[]; janela_final: string[]; resto_final: number; contas_final: Contas;
    ticks_teto_final: number; receptores_final: number[] };
}
const G = JSON.parse(readFileSync(new URL("../../../tests/gabaritos/corpo_teto_python.json", import.meta.url), "utf8")) as {
  versao: number; acoplamento_d: Rec; tetos: Record<string, number>; corpos: Record<string, Secao>;
};
const CA = CONFIG_ACOPLAMENTO_CORPO_LIGADA;
const CORPOS: Record<string, ConfigCorpo> = { v11: CCO_CORPO_V11, v11_mundo: CCO_CORPO_V11, etapa6_mundo: CCO_METABOLISMO };
const TETOS: Record<string, ConfigTetoFomeCorpo> = { DTL: CONFIG_TETO_FOME_LIMIAR, DTB: CONFIG_TETO_FOME_BAIXO };
const MUNDO = { nutricao_fruta: CMU.nutricao_fruta, efeito_podre: CMU.efeito_podre };
const NASCER = { tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 };

const hex = (bytes: number[]): string => bytes.map((b) => b.toString(16).padStart(2, "0")).join("");
const qDe = (c: Corpo): number[] => c.quimicos.map((n) => c.q[n]);
const contas = (c: Corpo): Contas => c.contas_metabolismo as Contas;
const contasOrdenadas = (c: Corpo): Contas => Object.fromEntries(Object.entries(contas(c)).sort(([a], [b]) => (a < b ? -1 : 1))) as Contas;

/** as operacoes do exportador do corpo (_aplicar e _aplicar_e6), com os mesmos argumentos */
function aplicar(c: Corpo, op: Op): void {
  const [tipo, a, b, d] = op;
  switch (tipo) {
    case "passo": c.passo({ tick: d as number, dormindo: Boolean(a), sujeira: b as number }); break;
    case "dono": c.acaoDono(a as string); break;
    case "pet": c.acaoPet(a as AcaoPet); break;
    case "fruta": c.estimuloFruta(a as number, b as number); break;
    case "pet_mundo": c.acaoPet(a as AcaoPet, true); break;
    case "andar": c.estimuloAndar(a as number, b as number); break;
    case "consumo": c.estimuloConsumoMundo(a as string, b as string, MUNDO, d as number); break;
    case "atividade": c.atividade(a as string); break;
    case "novidade": c.estimuloNovidade(a as number); break;
    default: throw new Error(`operacao desconhecida: ${JSON.stringify(op)}`);
  }
}

describe("a config do teto da fome", () => {
  test("o padrao, o DTL e o DTB sao os do Python", () => {
    expect(G.versao).toBe(1);
    expect(CA).toEqual(G.acoplamento_d);
    expect(CONFIG_TETO_FOME_CORPO.teto).toBeNull();
    expect(CONFIG_TETO_FOME_LIMIAR.teto).toBe(G.tetos.DTL);
    expect(CONFIG_TETO_FOME_BAIXO.teto).toBe(G.tetos.DTB);
  });
  test("falha alto como no Python", () => {
    expect(() => conferirConfigTetoFome({ teto: 0 })).toThrow(/teto/);
    expect(() => conferirConfigTetoFome({ teto: -5 })).toThrow(/teto/);
    expect(() => conferirConfigTetoFome({ teto: 2.5 })).toThrow(/teto/);
    expect(conferirConfigTetoFome({ teto: null }).teto).toBeNull();
    // o teto exige a D
    expect(() => Corpo.deEstado(NASCER, { cc: CCO_METABOLISMO, tetoFome: CONFIG_TETO_FOME_LIMIAR })).toThrow(/exige a D/);
    // o teto nao passa de C
    expect(() => Corpo.deEstado(NASCER, { cc: CCO_METABOLISMO, acoplamento: CA, tetoFome: { teto: CCO_METABOLISMO.escala + 1 } }))
      .toThrow(/passa de C/);
    // o teto igual a C vale
    expect(() => Corpo.deEstado(NASCER, { cc: CCO_METABOLISMO, acoplamento: CA, tetoFome: { teto: CCO_METABOLISMO.escala } })).not.toThrow();
  });
  test("sem o teto, o corpo e o da D de hoje (ticksTeto fica em 0)", () => {
    const a = Corpo.deEstado(NASCER, { cc: CCO_METABOLISMO, acoplamento: CA });
    const b = Corpo.deEstado(NASCER, { cc: CCO_METABOLISMO, acoplamento: CA, tetoFome: CONFIG_TETO_FOME_CORPO });
    for (let t = 0; t < 200; t++) { a.passo({ tick: t, dormindo: false, sujeira: 0 }); b.passo({ tick: t, dormindo: false, sujeira: 0 }); }
    expect(qDe(b)).toEqual(qDe(a));
    expect(a.ticksTeto).toBe(0);
    expect(b.ticksTeto).toBe(0);
  });
});

describe("G-PAR: a ponte com teto = o gabarito do Python, bit a bit no Node", () => {
  expect(Object.keys(G.corpos).sort()).toEqual(
    Object.keys(TETOS).flatMap((b) => Object.keys(CORPOS).map((n) => `${b}_${n}`)).sort());
  for (const [chave, s] of Object.entries(G.corpos)) {
    const [braco, ...resto] = chave.split("_");
    const nome = resto.join("_");
    const cc = CORPOS[nome];
    const opcoes = { cc, comMundo: s.com_mundo, acoplamento: CA, tetoFome: TETOS[braco] };
    test(`${chave}: a config e o teto`, () => {
      expect(cc).toEqual(s.config);
      expect(TETOS[braco].teto).toBe(s.teto);
    });
    test(`${chave}: a grade, cada operacao com o estado, o resto, as contas, o ticks_teto e os receptores depois`, () => {
      for (const caso of s.casos) {
        const c = new Corpo(Object.fromEntries(s.quimicos.map((n, i) => [n, caso.q[i]])), opcoes);
        c.janela_tedio = [...caso.janela];
        c.resto_combustivel = caso.resto;
        aplicar(c, caso.op);
        const rec = c.receptores();
        expect({ q: caso.q, janela: caso.janela, resto: caso.resto, op: caso.op, q_depois: qDe(c), janela_depois: c.janela_tedio,
          resto_depois: c.resto_combustivel, contas: contas(c), ticks_teto: c.ticksTeto, receptores: s.receptores.map((r) => rec[r]) },
        JSON.stringify(caso.op)).toEqual(caso);
      }
    });
    test(`${chave}: a sequencia longa, 3000 operacoes do nascimento, com o sha256`, () => {
      const c = Corpo.deEstado(NASCER, opcoes);
      const marcas: string[] = [];
      for (const op of s.sequencia.ops) {
        aplicar(c, op);
        marcas.push(JSON.stringify([qDe(c), c.janela_tedio, c.resto_combustivel, contasOrdenadas(c)]));
      }
      const rec = c.receptores();
      expect([qDe(c), c.janela_tedio, c.resto_combustivel, contas(c), c.ticksTeto, s.receptores.map((r) => rec[r])])
        .toEqual([s.sequencia.q_final, s.sequencia.janela_final, s.sequencia.resto_final, s.sequencia.contas_final,
          s.sequencia.ticks_teto_final, s.sequencia.receptores_final]);
      expect(hex(sha256(marcas.join("")))).toBe(s.sequencia.sha256);
    });
  }
});
