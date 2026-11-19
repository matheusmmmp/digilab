/* CORPO, as chaves da ablacao em TS (docs/PLANO_ANALISE_V3_CORPO.md, secoes 2 e 7; D-CO-1): a opcao E (`ConfigDigestaoCorpo.inteira`, em
   motor/corpo.ts) e a C5 (`ConfigReflexoSuave`, em motor/digibrain/arb.ts) reproduzem, inteiro a inteiro, o gabarito do Python
   (tests/gabaritos/corpo_chaves_python.json, de experiments/exportar_gabarito_corpo_chaves.py). Desligadas (o padrao), a vida e a de hoje. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CMU, type ConfigCorpo } from "../motor/constantes.ts";
import {
  CCO_CORPO_V11, CCO_METABOLISMO, CONFIG_ACOPLAMENTO_CORPO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_DIGESTAO_CORPO,
  CONFIG_DIGESTAO_CORPO_INTEIRA, Corpo, conferirConfigDigestao, configCorpo, quimicosDe, type ConfigAcoplamentoCorpo, type ConfigDigestaoCorpo,
  type ContaMetabolismo,
} from "../motor/corpo.ts";
import { Arbitragem, CONFIG_REFLEXO_SUAVE, CONFIG_REFLEXO_SUAVE_LIGADO, conferirConfigReflexoSuave } from "../motor/digibrain/arb.ts";
import { INATOS_MODULAR } from "../motor/digibrain/constantes.ts";
import type { UnidadeImpulso } from "../motor/digibrain/impulso.ts";
import { sha256 } from "../motor/mundo.ts";
import type { AcaoPet } from "../motor/tipos.ts";

type Rec = Record<string, unknown>;
type Op = (string | number)[];
type Contas = Record<ContaMetabolismo, number>;
interface Caso {
  q: number[]; janela: string[]; resto: number; op: Op; q_depois: number[]; janela_depois: string[]; resto_depois: number; contas: Contas;
  descartado: number; receptores: number[];
}
interface Secao {
  config: Rec; com_mundo: boolean; quimicos: string[]; receptores: string[]; casos: Caso[];
  sequencia: { ops: Op[]; sha256: string; q_final: number[]; janela_final: string[]; resto_final: number; contas_final: Contas;
    descartado_final: number; receptores_final: number[] };
}
interface CasoC5 {
  unidades: { acao: string; a: number; chave: [string, number] }[]; g_exp: number; energia: number; us: number[]; reflexo: boolean;
  indice: number; u: number | null; pesos: number[]; suaves: number; sorteios: number; reflexos: number;
}
const G = JSON.parse(readFileSync(new URL("../../../tests/gabaritos/corpo_chaves_python.json", import.meta.url), "utf8")) as {
  versao: number; digestao: ConfigDigestaoCorpo; acoplamento_d: ConfigAcoplamentoCorpo; corpos: Record<string, Secao>;
  reflexo_suave: { peso: number; lambda_sono: number; casos: CasoC5[] };
};
const CORPOS: Record<string, ConfigCorpo> = { v11: CCO_CORPO_V11, v11_mundo: CCO_CORPO_V11, etapa6_mundo: CCO_METABOLISMO };
const MUNDO = { nutricao_fruta: CMU.nutricao_fruta, efeito_podre: CMU.efeito_podre };
const NASCER = { tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 };

const hex = (bytes: number[]): string => bytes.map((b) => b.toString(16).padStart(2, "0")).join("");
const qDe = (c: Corpo): number[] => c.quimicos.map((n) => c.q[n]);
const contas = (c: Corpo): Contas => c.contas_metabolismo as Contas;
const contasOrdenadas = (c: Corpo): Contas => Object.fromEntries(Object.entries(contas(c)).sort(([a], [b]) => (a < b ? -1 : 1))) as Contas;
const nomeDoCorpo = (nome: string): string => nome.slice(nome.indexOf("_") + 1);

/** as operacoes do exportador do corpo (as mesmas do corpo_acoplamento.test.ts) */
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

describe("as configs das duas chaves", () => {
  test("a E e a C5 sao as do Python, e desligadas por padrao", () => {
    expect(G.versao).toBe(1);
    expect(CONFIG_DIGESTAO_CORPO_INTEIRA).toEqual(G.digestao);
    expect(CONFIG_DIGESTAO_CORPO.inteira).toBe(false);
    expect(CONFIG_REFLEXO_SUAVE.ligada).toBe(false);
    expect(CONFIG_REFLEXO_SUAVE_LIGADO.ligada).toBe(true);
    expect(CONFIG_REFLEXO_SUAVE.peso).toBe(G.reflexo_suave.peso);
    expect(CONFIG_REFLEXO_SUAVE_LIGADO.peso).toBe(G.reflexo_suave.peso);
    expect(INATOS_MODULAR.lambda_sono).toBe(G.reflexo_suave.lambda_sono);
  });
  test("falham alto como no Python", () => {
    expect(() => conferirConfigDigestao({ inteira: 1 as unknown as boolean })).toThrow(/inteira/);
    expect(() => conferirConfigReflexoSuave({ ligada: 1 as unknown as boolean, peso: 1024 })).toThrow(/ligada/);
    expect(() => conferirConfigReflexoSuave({ ligada: true, peso: 0 })).toThrow(/peso/);
    expect(() => conferirConfigReflexoSuave({ ligada: true, peso: 2.5 })).toThrow(/peso/);
    expect(() => new Arbitragem(null, false, false, undefined, { ligada: true, peso: -1 })).toThrow(/peso/);
    const sem = configCorpo({ ligada: true, digestao: true });
    expect(() => Corpo.deEstado(NASCER, { cc: sem, digestao: CONFIG_DIGESTAO_CORPO_INTEIRA })).toThrow(/metabolismo/);
    expect(() => Corpo.deEstado(NASCER, { cc: CCO_CORPO_V11, digestao: { inteira: 1 as unknown as boolean } })).toThrow(/inteira/);
  });
});

describe("G-PAR: a opcao E (e a D com a E) = o gabarito do Python, bit a bit no Node", () => {
  expect(Object.keys(G.corpos).sort()).toEqual(Object.keys(CORPOS).flatMap((n) => [`E_${n}`, `DE_${n}`]).sort());
  for (const [nome, s] of Object.entries(G.corpos)) {
    const cc = CORPOS[nomeDoCorpo(nome)];
    const ca = nome.startsWith("DE_") ? CONFIG_ACOPLAMENTO_CORPO_LIGADA : CONFIG_ACOPLAMENTO_CORPO;
    const opcoes = { cc, comMundo: s.com_mundo, acoplamento: ca, digestao: CONFIG_DIGESTAO_CORPO_INTEIRA };
    test(`${nome}: a config e os quimicos`, () => {
      expect(cc).toEqual(s.config);
      expect(quimicosDe(cc, s.com_mundo)).toEqual(s.quimicos);
    });
    test(`${nome}: a grade, cada operacao com o estado, o resto, as contas, o descartado e os receptores depois`, () => {
      for (const caso of s.casos) {
        const c = new Corpo(Object.fromEntries(quimicosDe(cc, s.com_mundo).map((n, i) => [n, caso.q[i]])), opcoes);
        c.janela_tedio = [...caso.janela];
        c.resto_combustivel = caso.resto;
        aplicar(c, caso.op);
        const rec = c.receptores();
        expect({ q: caso.q, janela: caso.janela, resto: caso.resto, op: caso.op, q_depois: qDe(c), janela_depois: c.janela_tedio,
          resto_depois: c.resto_combustivel, contas: contas(c), descartado: c.descartado_total, receptores: s.receptores.map((r) => rec[r]) },
        JSON.stringify(caso.op)).toEqual(caso);
      }
    });
    test(`${nome}: a sequencia longa, 3000 operacoes do nascimento, com o sha256 e o descartado`, () => {
      const c = Corpo.deEstado(NASCER, opcoes);
      const marcas: string[] = [];
      for (const op of s.sequencia.ops) {
        aplicar(c, op);
        marcas.push(JSON.stringify([qDe(c), c.janela_tedio, c.resto_combustivel, contasOrdenadas(c)]));
      }
      const rec = c.receptores();
      expect([qDe(c), c.janela_tedio, c.resto_combustivel, contas(c), c.descartado_total, s.receptores.map((r) => rec[r])])
        .toEqual([s.sequencia.q_final, s.sequencia.janela_final, s.sequencia.resto_final, s.sequencia.contas_final,
          s.sequencia.descartado_final, s.sequencia.receptores_final]);
      expect(hex(sha256(marcas.join("")))).toBe(s.sequencia.sha256);
    });
  }
});

describe("G-PAR: a C5, o reflexo suave = o gabarito do Python", () => {
  test("reflexo, indice, u, pesos e os contadores, caso a caso", () => {
    expect(G.reflexo_suave.casos.length).toBeGreaterThan(0);
    for (const k of G.reflexo_suave.casos) {
      const arb = new Arbitragem(null, false, false, undefined, CONFIG_REFLEXO_SUAVE_LIGADO);
      arb.sondas = {};                                  // como o exportador: sem as sondas
      const sens = { leitura: { energia: k.energia } };
      const reflexo = arb.reflexo(sens);
      let i = 0;
      const rng = { random: () => k.us[i++]! };
      const unidades = k.unidades.map((x) => ({ ...x })) as unknown as UnidadeImpulso[];
      const out = arb.escolher(unidades, { g_exp: k.g_exp, urgencias: { fome: 0 } }, sens, rng, reflexo);
      expect({ reflexo, indice: out.indice, u: out.u, pesos: out.pesos, suaves: arb.suaves, sorteios: arb.sorteios, reflexos: arb.reflexos },
        JSON.stringify(k)).toEqual({ reflexo: k.reflexo, indice: k.indice, u: k.u, pesos: k.pesos, suaves: k.suaves, sorteios: k.sorteios,
        reflexos: k.reflexos });
    }
  });
  test("as sondas tambem recebem o peso, sem contar", () => {
    const arb = new Arbitragem(null, false, false, undefined, CONFIG_REFLEXO_SUAVE_LIGADO);
    const k = G.reflexo_suave.casos.find((c) => c.energia < G.reflexo_suave.lambda_sono)!;
    const unidades = k.unidades.map((x) => ({ ...x, soma: x.a, termos: { incentivo: 0, habito: 0, memoria: 0, persistencia: 0 } })) as unknown as UnidadeImpulso[];
    const out = arb.escolher(unidades, { g_exp: k.g_exp, urgencias: { fome: 0 } }, { leitura: { energia: k.energia } }, { random: () => 0.5 }, false);
    expect(arb.suaves).toBe(1);
    expect(out.reflexo).toBe(false);
    expect(Object.keys(out.sondas).length).toBeGreaterThan(0);
  });
  test("a unidade dormir e obrigatoria, e a energia tambem", () => {
    const arb = new Arbitragem(null, false, false, undefined, CONFIG_REFLEXO_SUAVE_LIGADO);
    arb.sondas = {};
    const u = [{ acao: "ocioso", a: 0, chave: ["ocioso", 0] }] as unknown as UnidadeImpulso[];
    expect(() => arb.escolher(u, { g_exp: 0 }, { leitura: { energia: 0 } }, { random: () => 0 })).toThrow(/dormir/);
    expect(() => arb.reflexo({ leitura: {} })).toThrow(/energia/);
  });
});

describe("desligadas, as duas chaves sao a vida de hoje", () => {
  test("o corpo: padrao = explicito desligado", () => {
    for (const [nome, s] of Object.entries(G.corpos).filter(([n]) => n.startsWith("E_"))) {
      const cc = CORPOS[nomeDoCorpo(nome)];
      const a = Corpo.deEstado(NASCER, { cc, comMundo: s.com_mundo });
      const b = Corpo.deEstado(NASCER, { cc, comMundo: s.com_mundo, digestao: { inteira: false } });
      for (const op of s.sequencia.ops.slice(0, 1500)) {
        aplicar(a, op);
        aplicar(b, op);
        expect([qDe(b), b.resto_combustivel, b.descartado_total, b.contas_metabolismo]).toEqual([qDe(a), a.resto_combustivel, a.descartado_total, a.contas_metabolismo]);
      }
      expect(b.digestao.inteira).toBe(false);
    }
  });
  test("a E ligada difere: o excedente vira combustivel e nao entra no descartado_total", () => {
    const off = Corpo.deEstado(NASCER, { cc: CCO_METABOLISMO, comMundo: true });
    const on = Corpo.deEstado(NASCER, { cc: CCO_METABOLISMO, comMundo: true, digestao: CONFIG_DIGESTAO_CORPO_INTEIRA });
    for (const c of [off, on]) { c.q.fome = 0; c.q.combustivel = 0; c.q.alimento = 5000; c.acaoDono("alimentar"); }
    expect(off.descartado_total).toBeGreaterThan(0);
    expect(on.descartado_total).toBe(0);
    expect(on.q.alimento).toBe(0);
    expect(on.q.combustivel).toBeGreaterThanOrEqual(off.q.combustivel);
  });
  test("a arbitragem: sem a config = config desligada explicita, mesmas saidas e estadoInterno", () => {
    const energias = [0, G.reflexo_suave.lambda_sono - 1, G.reflexo_suave.lambda_sono, 90000];
    for (const k of G.reflexo_suave.casos.slice(0, 120)) {
      const a = new Arbitragem();
      const b = new Arbitragem(null, false, false, undefined, CONFIG_REFLEXO_SUAVE);
      a.sondas = {}; b.sondas = {};
      const sens = { leitura: { energia: energias[k.indice % energias.length]! } };
      const run = (arb: Arbitragem) => {
        let i = 0;
        const rng = { random: () => k.us[i++ % k.us.length]! };
        const unidades = k.unidades.map((x) => ({ ...x })) as unknown as UnidadeImpulso[];
        const r = arb.reflexo(sens);
        const o = arb.escolher(unidades, { g_exp: k.g_exp, urgencias: { fome: 0 } }, sens, rng, r);
        return [r, o.indice, o.u, o.pesos, arb.estadoInterno(), arb.suaves];
      };
      expect(run(b)).toEqual(run(a));
      expect(a.suaves).toBe(0);
      expect(Object.keys(a.estadoInterno())).toEqual(["sorteios", "reflexos", "nada_a_fazer"]);
    }
  });
});
