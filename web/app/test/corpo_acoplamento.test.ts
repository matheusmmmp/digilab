/* CORPO_ACOPLAMENTO, a opcao D em TS (docs/TAREFA_V3_CORPO_ACOPLAMENTO.md, etapa 2; D-CA-2, D-CA-5 e D-CA-7): com a ConfigAcoplamentoCorpo
   ligada, a falta de combustivel sobe a fome, e nao o cansaco. motor/corpo.ts reproduz, inteiro a inteiro, o gabarito do Python
   (tests/gabaritos/corpo_acoplamento_python.json, de experiments/exportar_gabarito_corpo_acoplamento.py): a config, a tabela do grafo e o
   relato, a grade de casos (o estado, o resto, as contas e os receptores) e a sequencia longa, nos corpos do v11 (sem e com o mundo) e da
   etapa 6 com o metabolismo. Desligada (o padrao), o corpo e o de hoje: o metabolismo.test.ts e o corpo.test.ts conferem. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CMU, type ConfigCorpo } from "../motor/constantes.ts";
import {
  CCO_CORPO_V11, CCO_METABOLISMO, CONFIG_ACOPLAMENTO_CORPO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, Corpo, checarGrafo, configCorpo,
  conferirConfigAcoplamento, grafoDoCorpo, quimicosDe, taxasDe, type ConfigAcoplamentoCorpo, type ContaMetabolismo, type GrafoCorpo,
} from "../motor/corpo.ts";
import { sha256 } from "../motor/mundo.ts";
import type { AcaoPet } from "../motor/tipos.ts";

type Rec = Record<string, unknown>;
type Op = (string | number)[];
type Contas = Record<ContaMetabolismo, number>;
interface Caso {
  q: number[]; janela: string[]; resto: number; op: Op; q_depois: number[]; janela_depois: string[]; resto_depois: number; contas: Contas;
  receptores: number[];
}
interface Secao {
  config: Rec; com_mundo: boolean; quimicos: string[]; receptores: string[]; grafo: { tabela: unknown; relato: Rec }; casos: Caso[];
  sequencia: { ops: Op[]; sha256: string; q_final: number[]; janela_final: string[]; resto_final: number; contas_final: Contas;
    receptores_final: number[] };
}
const G = JSON.parse(readFileSync(new URL("../../../tests/gabaritos/corpo_acoplamento_python.json", import.meta.url), "utf8")) as {
  versao: number; acoplamento: ConfigAcoplamentoCorpo; padrao: ConfigAcoplamentoCorpo; corpos: Record<string, Secao>;
};
const CA = CONFIG_ACOPLAMENTO_CORPO_LIGADA;
const CORPOS: Record<string, ConfigCorpo> = { v11: CCO_CORPO_V11, v11_mundo: CCO_CORPO_V11, etapa6_mundo: CCO_METABOLISMO };
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

/** a tabela no formato do gabarito do metabolismo (_tabela_m: as reacoes inteiras) */
const tabela = (g: GrafoCorpo): unknown => ({
  quimicos: g.quimicos.map((q) => [q.nome, q.teto, q.descarte, q.receptor, q.leitura, q.meia_vida, q.k_meia_vida]),
  reacoes: g.reacoes.map((r) => [r.nome, r.consome, r.produz, r.taxa, r.fracoes ?? [], r.le ?? null, r.lado ?? null, r.limiar ?? 0]),
  emissores: g.emissores.map((e) => ({ nome: e.nome, gatilho: e.gatilho, fase: e.fase, efeitos: e.efeitos,
    le: e.le.map((le) => [le.quimico, le.num, le.den, le.sinal]), limiar: e.limiar, divisor: e.divisor, variavel: e.variavel })),
});

describe("a config da opcao D", () => {
  test("a ligada e a padrao sao as do Python", () => {
    expect(G.versao).toBe(1);
    expect(CA).toEqual(G.acoplamento);
    expect(CONFIG_ACOPLAMENTO_CORPO).toEqual(G.padrao);
    expect(CONFIG_ACOPLAMENTO_CORPO.ligada).toBe(false);
  });
  test("falha alto como no Python", () => {
    expect(() => conferirConfigAcoplamento({ ligada: true, falta_fome: 0 })).toThrow(/falta_fome/);
    expect(() => conferirConfigAcoplamento({ ligada: true, falta_fome: 2.5 })).toThrow(/falta_fome/);
    expect(() => conferirConfigAcoplamento({ ligada: 1 as unknown as boolean, falta_fome: 500 })).toThrow(/ligada/);
    const sem = configCorpo({ ligada: true, digestao: true });
    expect(() => Corpo.deEstado(NASCER, { cc: sem, acoplamento: CA })).toThrow(/metabolismo/);
  });
  test("desligada, a ponte e a ME-1 de hoje; ligada, ela sobe a fome", () => {
    const efeito = (ca?: ConfigAcoplamentoCorpo) =>
      grafoDoCorpo(CCO_CORPO_V11, taxasDe(CCO_CORPO_V11), false, undefined, ca).emissores.find((e) => e.nome === "falta_combustivel")?.efeitos;
    expect(efeito()).toEqual([["cansaco", CCO_CORPO_V11.falta_cansaco]]);
    expect(efeito(CONFIG_ACOPLAMENTO_CORPO)).toEqual([["cansaco", CCO_CORPO_V11.falta_cansaco]]);
    expect(efeito(CA)).toEqual([["fome", CA.falta_fome]]);
  });
});

describe("G-PAR: a opcao D = o gabarito do Python, bit a bit no Node", () => {
  expect(Object.keys(G.corpos).sort()).toEqual(Object.keys(CORPOS).sort());
  for (const [nome, s] of Object.entries(G.corpos)) {
    const cc = CORPOS[nome];
    const opcoes = { cc, comMundo: s.com_mundo, acoplamento: CA };
    test(`${nome}: a config, os quimicos, a tabela do grafo e o relato`, () => {
      expect(cc).toEqual(s.config);
      expect(quimicosDe(cc, s.com_mundo)).toEqual(s.quimicos);
      const g = grafoDoCorpo(cc, taxasDe(cc), s.com_mundo, undefined, CA);
      expect(tabela(g)).toEqual(s.grafo.tabela);
      expect(checarGrafo(g)).toEqual(s.grafo.relato);
    });
    test(`${nome}: a grade, cada operacao com o estado, o resto, as contas e os receptores depois`, () => {
      for (const caso of s.casos) {
        const c = new Corpo(Object.fromEntries(quimicosDe(cc, s.com_mundo).map((n, i) => [n, caso.q[i]])), opcoes);
        c.janela_tedio = [...caso.janela];
        c.resto_combustivel = caso.resto;
        aplicar(c, caso.op);
        const rec = c.receptores();
        expect({ q: caso.q, janela: caso.janela, resto: caso.resto, op: caso.op, q_depois: qDe(c), janela_depois: c.janela_tedio,
          resto_depois: c.resto_combustivel, contas: contas(c), receptores: s.receptores.map((r) => rec[r]) }, JSON.stringify(caso.op))
          .toEqual(caso);
      }
    });
    test(`${nome}: a sequencia longa, 3000 operacoes do nascimento, com o sha256`, () => {
      const c = Corpo.deEstado(NASCER, opcoes);
      const marcas: string[] = [];
      for (const op of s.sequencia.ops) {
        aplicar(c, op);
        marcas.push(JSON.stringify([qDe(c), c.janela_tedio, c.resto_combustivel, contasOrdenadas(c)]));
      }
      const rec = c.receptores();
      expect([qDe(c), c.janela_tedio, c.resto_combustivel, contas(c), s.receptores.map((r) => rec[r])])
        .toEqual([s.sequencia.q_final, s.sequencia.janela_final, s.sequencia.resto_final, s.sequencia.contas_final, s.sequencia.receptores_final]);
      expect(hex(sha256(marcas.join("")))).toBe(s.sequencia.sha256);
    });
  }
});
