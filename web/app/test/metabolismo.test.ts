/* O metabolismo energetico em TS (docs/TAREFA_V2_METABOLISMO.md, etapa 4; o G-PAR da secao 5): motor/corpo.ts reproduz, inteiro a
   inteiro, as secoes `metabolismo`, `metabolismo_gasto` e `metabolismo_v11` do gabarito do corpo (tests/gabaritos/corpo_quimica_python.json,
   de experiments/exportar_gabarito_corpo.py), lido do proprio lugar: a config, o grafo, a grade de casos (com o resto e as contas), as
   grades com a conversao 2/3 e com o gasto das atividades x 1/2 e x 2, e as sequencias longas (o sha256 de q, da janela, do resto e das
   contas depois de cada operacao). O corpo do ponto do v11 (o gasto 4/5, basal 300/150, e o ponto (2, 1) do adendo 4) e o da config_v11
   do gabarito do cerebro A.

   E os equivalentes TS dos gates do Python (tests/test_metabolismo.py) onde o gabarito permite: o G-GRAFO (as tabelas feitas para falhar),
   o G-MEC-M (a conta de cada peca), o G-CONS-M (as contas fecham a cada operacao) e o G-HOJE-M em malha aberta (as vidas de hoje do
   gabarito, rejogadas com o metabolismo: com o combustivel acima de C/4, os quimicos de antes dao o mesmo sha256 do Python; com a falta, so
   o cansaco difere, a partir do tick dela). O G-HOJE-M em malha fechada (as vidas com o cerebro) precisa do Motor com o corpo por tick, que
   e da etapa 4 do W-PORTE. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CCO, CCO_V11, CMU, type ConfigCorpo } from "../motor/constantes.ts";
import {
  CCO_CORPO_V11, CCO_DRIVES, CCO_METABOLISMO, CONTAS_METABOLISMO, Corpo, GrafoInvalido, checarGrafo, configCorpo, emissor,
  gastoDaAtividade, grafoDoCorpo, leitura, quimico, quimicosDe, taxasDe, type ContaMetabolismo, type GrafoCorpo, type Reacao,
} from "../motor/corpo.ts";
import { receptoresNovos } from "../motor/lobos.ts";
import { sha256 } from "../motor/mundo.ts";
import type { AcaoPet } from "../motor/tipos.ts";

type Rec = Record<string, unknown>;
type Op = (string | number)[];
type Contas = Record<ContaMetabolismo, number>;
interface CasoM {
  q: number[]; janela: string[]; resto: number; op: Op; q_depois: number[]; janela_depois: string[]; resto_depois: number; contas: Contas;
  receptores?: number[];
}
interface Sequencia {
  ops: Op[]; sha256: string; q_final: number[]; janela_final: string[]; resto_final: number; contas_final: Contas; receptores_final?: number[];
}
interface VidaAberta {
  dono: string; semente: number; q_inicial: number[]; tick_inicial: number; ticks: string; eventos: [number, string, string][];
  q_final: number[]; sha256: string;
}
type Tabela = { quimicos: unknown[][]; reacoes: unknown[][]; emissores: Rec[] };
const G = JSON.parse(readFileSync(new URL("../../../tests/gabaritos/corpo_quimica_python.json", import.meta.url), "utf8")) as {
  config: Rec; mundo: { nutricao_fruta: number; efeito_podre: number };
  vida: { quimicos: string[]; vidas: VidaAberta[] };
  etapa6: { quimicos: string[]; sequencia: { ops: Op[]; sha256: string } };
  metabolismo: { quimicos: string[]; config: Rec; config_fracao: { conversao_num: number; conversao_den: number };
    grafo: { chaves: string; com_mundo: boolean; tabela: Tabela; relato: Rec }[]; casos: CasoM[]; casos_fracao: CasoM[]; sequencia: Sequencia };
  metabolismo_gasto: Record<string, { gasto_atividades_num: number; gasto_atividades_den: number; pet: Rec; dono_brincar: Rec; casos: CasoM[] }>;
  metabolismo_v11: { quimicos: string[]; config: Rec; receptores: string[]; taxas_pet: Rec; taxas_dono_brincar: Rec;
    grafo: { tabela: Tabela; relato: Rec }; casos: CasoM[]; sequencia: Sequencia };
};
const L = JSON.parse(readFileSync(new URL("./gabaritos/lobos_python.json", import.meta.url), "utf8")) as {
  config_v11: { corpo: Rec; receptores: string[] };
};

const C = CCO.escala;
const MUNDO = { nutricao_fruta: G.mundo.nutricao_fruta, efeito_podre: G.mundo.efeito_podre };
const MIN = configCorpo({ ligada: true, digestao: true, metabolismo: true });
const FRACAO = configCorpo({ ...CCO_METABOLISMO, ...G.metabolismo.config_fracao });
const F = MIN.falta_limiar, M = MIN.mobilizar_limiar, A = MIN.armazenar_limiar;
const NASCER = { tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 };

const hex = (bytes: number[]): string => bytes.map((b) => b.toString(16).padStart(2, "0")).join("");
const qDe = (c: Corpo): number[] => c.quimicos.map((n) => c.q[n]);
const contas = (c: Corpo): Contas => c.contas_metabolismo as Contas;
/** json.dumps(..., sort_keys=True, separators=(",", ":")) das contas: as chaves em ordem */
const contasOrdenadas = (c: Corpo): Contas => Object.fromEntries(Object.entries(contas(c)).sort(([a], [b]) => (a < b ? -1 : 1))) as Contas;
function corpoDe(q: number[], cc: ConfigCorpo, comMundo: boolean, janela: string[] = [], resto = 0): Corpo {
  const c = new Corpo(Object.fromEntries(quimicosDe(cc, comMundo).map((n, i) => [n, q[i]])), { cc, comMundo });
  c.janela_tedio = [...janela];
  c.resto_combustivel = resto;
  return c;
}
/** um corpo do nascimento, com alguns quimicos trocados (o _corpo do tests/test_metabolismo.py) */
function corpo(cc: ConfigCorpo, q: Record<string, number> = {}, comMundo = false): Corpo {
  const c = Corpo.deEstado(NASCER, { cc, comMundo });
  Object.assign(c.q, q);
  return c;
}
const passo = (c: Corpo, dormindo = false): void => c.passo({ tick: 600, dormindo, sujeira: 0 });

/** as operacoes do exportador (_aplicar e _aplicar_e6), com os mesmos argumentos */
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

/** G-CONS-M: o combustivel e a reserva sao o que entrou menos o que saiu, desde o comeco (`comb0`, `res0`) */
function fecha(c: Corpo, comb0: number, res0: number, resto0 = 0, digerido0 = 0): void {
  const k = contas(c), cc = c.cc;
  expect(c.q.combustivel).toBe(comb0 + k.convertido - k.descartado_teto + k.mobilizado - k.gasto_basal - k.gasto_atividade - k.armazenado);
  expect(c.q.reserva).toBe(res0 + k.armazenado - k.mobilizado);
  expect(k.convertido * cc.conversao_den + c.resto_combustivel).toBe(resto0 + (c.digerido_total - digerido0) * cc.conversao_num);
  expect(c.resto_combustivel >= 0 && c.resto_combustivel < cc.conversao_den).toBe(true);
  expect(Object.values(k).every((v) => v >= 0)).toBe(true);
}

function conferirCasos(casos: CasoM[], cc: ConfigCorpo, comMundo: boolean, receptores?: string[]): void {
  for (const caso of casos) {
    const c = corpoDe(caso.q, cc, comMundo, caso.janela, caso.resto);
    aplicar(c, caso.op);
    const visto: Rec = { q: caso.q, janela: caso.janela, resto: caso.resto, op: caso.op, q_depois: qDe(c), janela_depois: c.janela_tedio,
      resto_depois: c.resto_combustivel, contas: contas(c) };
    if (receptores) { const rec = c.receptores(); visto.receptores = receptores.map((r) => rec[r]); }
    expect(visto, JSON.stringify(caso.op)).toEqual(caso);
    /* G-CONS-M em cada caso: as contas partem de zero no corpo montado */
    const a = corpoDe(caso.q, cc, comMundo);
    fecha(c, a.q.combustivel, a.q.reserva, caso.resto, 0);
  }
}

function conferirSequencia(s: Sequencia, cc: ConfigCorpo, comMundo: boolean, receptores?: string[]): void {
  const c = Corpo.deEstado(NASCER, { cc, comMundo });
  const marcas: string[] = [];
  for (const op of s.ops) {
    aplicar(c, op);
    marcas.push(JSON.stringify([qDe(c), c.janela_tedio, c.resto_combustivel, contasOrdenadas(c)]));
    fecha(c, cc.combustivel_inicial, cc.reserva_inicial);
  }
  expect([qDe(c), c.janela_tedio, c.resto_combustivel, contas(c)]).toEqual([s.q_final, s.janela_final, s.resto_final, s.contas_final]);
  if (receptores) { const rec = c.receptores(); expect(receptores.map((r) => rec[r])).toEqual(s.receptores_final); }
  expect(hex(sha256(marcas.join("")))).toBe(s.sha256);
}

/** a tabela no formato do gabarito do metabolismo (_tabela_m: as reacoes inteiras) */
const tabela = (g: GrafoCorpo): unknown => ({
  quimicos: g.quimicos.map((q) => [q.nome, q.teto, q.descarte, q.receptor, q.leitura, q.meia_vida, q.k_meia_vida]),
  reacoes: g.reacoes.map((r) => [r.nome, r.consome, r.produz, r.taxa, r.fracoes ?? [], r.le ?? null, r.lado ?? null, r.limiar ?? 0]),
  emissores: g.emissores.map((e) => ({ nome: e.nome, gatilho: e.gatilho, fase: e.fase, efeitos: e.efeitos,
    le: e.le.map((le) => [le.quimico, le.num, le.den, le.sinal]), limiar: e.limiar, divisor: e.divisor, variavel: e.variavel })),
});

// ================================================================== G-PAR
describe("G-PAR: o metabolismo = o gabarito do Python, bit a bit no Node", () => {
  test("a config: os campos do metabolismo, a conversao 2/3, os fatores do gasto e os quimicos", () => {
    for (const [k, v] of Object.entries(G.metabolismo.config)) expect(CCO_METABOLISMO[k as keyof ConfigCorpo], k).toBe(v);
    for (const [k, v] of Object.entries(G.config)) expect(CCO[k as keyof ConfigCorpo], k).toBe(v);
    expect([FRACAO.conversao_num, FRACAO.conversao_den]).toEqual([2, 3]);
    expect(Object.keys(G.metabolismo_gasto)).toEqual(["dobro", "metade"]);
    expect(quimicosDe(CCO_METABOLISMO, true)).toEqual(G.metabolismo.quimicos);
    expect(quimicosDe(CCO_METABOLISMO, true).slice(-2)).toEqual(["combustivel", "reserva"]);
    expect(quimicosDe(CCO_METABOLISMO, true).slice(0, -2)).toEqual(quimicosDe(CCO_DRIVES, true));
  });

  test("o grafo: a tabela (com as reacoes inteiras) e o relato em cada combinacao que o TS tem, com e sem o mundo", () => {
    const chaves: Record<string, ConfigCorpo> = { minimo: MIN, etapa6: CCO_METABOLISMO, fracao: FRACAO };
    /* o banheiro (a vontade e o conforto) ainda nao tem quimica em TS (a etapa 4 do banheiro): as duas tabelas dele ficam de fora */
    expect(G.metabolismo.grafo.map((x) => x.chaves)).toEqual(["minimo", "minimo", "etapa6", "etapa6", "banheiro", "banheiro", "fracao", "fracao"]);
    for (const item of G.metabolismo.grafo.filter((x) => x.chaves !== "banheiro")) {
      const cc = chaves[item.chaves];
      const g = grafoDoCorpo(cc, taxasDe(cc), item.com_mundo);
      const nome = `${item.chaves}/${item.com_mundo}`;
      expect(tabela(g), nome).toEqual(item.tabela);
      expect(checarGrafo(g), nome).toEqual(item.relato);
    }
  });

  test("a grade: cada operacao, com o estado, a janela, o resto e as contas depois", () => conferirCasos(G.metabolismo.casos, CCO_METABOLISMO, true));
  test("a grade com a conversao 2/3 (o resto mordendo)", () => conferirCasos(G.metabolismo.casos_fracao, FRACAO, true));
  test("a grade com o gasto das atividades x 1/2 e x 2, e as taxas das atividades em cada um", () => {
    for (const [nome, x] of Object.entries(G.metabolismo_gasto)) {
      const cc = configCorpo({ ...CCO_METABOLISMO, gasto_atividades_num: x.gasto_atividades_num, gasto_atividades_den: x.gasto_atividades_den });
      const t = taxasDe(cc);
      expect(t.pet, nome).toEqual(x.pet);
      expect(t.dono.brincar, nome).toEqual(x.dono_brincar);
      conferirCasos(x.casos, cc, true);
    }
  });
  test("a sequencia longa: 3000 operacoes num corpo so, do nascimento, com o sha256 de q, da janela, do resto e das contas", () => {
    conferirSequencia(G.metabolismo.sequencia, CCO_METABOLISMO, true);
  });
});

describe("o corpo do ponto do v11 (o gasto 4/5, basal 300/150, e o ponto (2, 1) do adendo 4)", () => {
  test("o CCO_V11 completado e a ConfigCorpo das vidas do v11, campo a campo, nos dois gabaritos", () => {
    expect(CCO_CORPO_V11).toEqual(G.metabolismo_v11.config);
    expect(CCO_CORPO_V11).toEqual(L.config_v11.corpo);
    expect([CCO_CORPO_V11.gasto_basal_acordado, CCO_CORPO_V11.gasto_basal_dormindo, CCO_CORPO_V11.gasto_atividades_num,
      CCO_CORPO_V11.gasto_atividades_den]).toEqual([300, 150, 4, 5]);
    /* o ponto (m_sobe, m_reduz) = (2, 1): as subidas x 2, o divisor do estresse / 2, as reducoes como estao */
    expect([CCO_CORPO_V11.tedio_sobe, CCO_CORPO_V11.solidao_sobe, CCO_CORPO_V11.estresse_divisor]).toEqual([2 * CCO.tedio_sobe,
      2 * CCO.solidao_sobe, CCO.estresse_divisor / 2]);
    expect([CCO_CORPO_V11.tedio_brincar, CCO_CORPO_V11.carinho_solidao]).toEqual([CCO.tedio_brincar, CCO.carinho_solidao]);
    /* o que o CCO_V11 troca e so o que difere do padrao */
    for (const [k, v] of Object.entries(CCO_V11)) expect(v, k).not.toBe(CCO[k as keyof ConfigCorpo]);
    expect(Object.keys(CCO_CORPO_V11).filter((k) => CCO_CORPO_V11[k as keyof ConfigCorpo] !== CCO[k as keyof ConfigCorpo]).sort())
      .toEqual(Object.keys(CCO_V11).sort());
  });
  test("os quimicos, os receptores do v11 e as taxas das atividades com o gasto 4/5", () => {
    expect(quimicosDe(CCO_CORPO_V11)).toEqual(G.metabolismo_v11.quimicos);
    expect(G.metabolismo_v11.receptores).toEqual(L.config_v11.receptores);
    const c = Corpo.deEstado(NASCER, { cc: CCO_CORPO_V11 });
    expect(Object.keys(c.receptores())).toEqual(L.config_v11.receptores);
    expect(["fome", "higiene", "energia", "humor", "saude", ...receptoresNovos(CCO_CORPO_V11)]).toEqual(L.config_v11.receptores);
    const t = taxasDe(CCO_CORPO_V11);
    expect(t.pet).toEqual(G.metabolismo_v11.taxas_pet);
    expect(t.dono.brincar).toEqual(G.metabolismo_v11.taxas_dono_brincar);
    expect([t.pet.brincar.combustivel, t.pet.explorar.combustivel, t.dono.brincar.combustivel]).toEqual([-7200, -5400, -28800]);
  });
  test("o grafo do v11: a tabela e o relato", () => {
    const g = grafoDoCorpo(CCO_CORPO_V11, taxasDe(CCO_CORPO_V11));
    expect(tabela(g)).toEqual(G.metabolismo_v11.grafo.tabela);
    expect(checarGrafo(g)).toEqual(G.metabolismo_v11.grafo.relato);
  });
  test("a grade do v11: o estado, o resto, as contas e os receptores do v11 depois de cada operacao", () => {
    conferirCasos(G.metabolismo_v11.casos, CCO_CORPO_V11, false, G.metabolismo_v11.receptores);
  });
  test("a sequencia longa do v11, do nascimento: o sha256 e os receptores no fim", () => {
    conferirSequencia(G.metabolismo_v11.sequencia, CCO_CORPO_V11, false, G.metabolismo_v11.receptores);
  });
  test("controle negativo: o basal de 375 (o padrao) no lugar do 300 do v11 e pego", () => {
    expect(() => conferirSequencia(G.metabolismo_v11.sequencia, configCorpo({ ...CCO_CORPO_V11, gasto_basal_acordado: 375 }), false)).toThrow();
    expect(() => conferirSequencia(G.metabolismo_v11.sequencia, configCorpo({ ...CCO_CORPO_V11, gasto_atividades_num: 1,
      gasto_atividades_den: 1 }), false)).toThrow();
  });
});

// ================================================================== a chave e o grafo
describe("a sub-chave e o grafo (G-GRAFO)", () => {
  test("a sub-chave exige a digestao e os numeros sao conferidos (falha alto, como no __post_init__)", () => {
    expect(CCO.metabolismo).toBe(false);
    expect(() => configCorpo({ ligada: true, metabolismo: true })).toThrow(/metabolismo exige ConfigCorpo.digestao/);
    expect(() => configCorpo({ ligada: true, digestao: true, metabolismo: 1 as unknown as boolean })).toThrow(/bool/);
    expect(() => configCorpo({ ...MIN, falta_limiar: M })).toThrow(/falta_limiar < mobilizar_limiar/);
    expect(() => configCorpo({ ...MIN, armazenar_limiar: C })).toThrow(/armazenar_limiar < C/);
    expect(() => configCorpo({ ...MIN, gasto_basal_dormindo: 0 })).toThrow(/inteiro positivo/);
    expect(() => configCorpo({ ...MIN, gasto_atividades_den: 2.5 })).toThrow(/inteiro positivo/);
    expect(() => configCorpo({ ...MIN, reserva_inicial: C + 1 })).toThrow(/\[0, C\]/);
    expect([MIN.combustivel_inicial, MIN.reserva_inicial, F, M, A]).toEqual([C / 2, C / 4, C / 4, C / 2, 3 * C / 4]);
    expect([MIN.gasto_basal_acordado, taxasDe(MIN).fome_por_tick, MIN.gasto_basal_dormindo]).toEqual([375, 375, 187]);
    expect([MIN.falta_cansaco, taxasDe(MIN).cansaco_acordado]).toEqual([500, 500]);
    /* o fator que arredonda o gasto a zero falha alto (a atividade deixaria de custar combustivel) */
    expect(() => gastoDaAtividade(configCorpo({ ...MIN, gasto_atividades_num: 1, gasto_atividades_den: 100000 }), 9000)).toThrow(/zera/);
    expect(() => taxasDe(configCorpo({ ...MIN, gasto_atividades_num: 1, gasto_atividades_den: 100000 }))).toThrow(/zera/);
  });

  test("os quimicos novos sem receptor e o nascimento; desligado, nada muda", () => {
    for (const [cc, mundo] of [[MIN, false], [CCO_METABOLISMO, false], [CCO_METABOLISMO, true], [CCO_CORPO_V11, false]] as [ConfigCorpo, boolean][]) {
      const c = Corpo.deEstado({ ...NASCER, tick: 5000 }, { cc, comMundo: mundo });
      const sem = Corpo.deEstado({ ...NASCER, tick: 5000 }, { cc: configCorpo({ ...cc, metabolismo: false }), comMundo: mundo });
      expect(c.quimicos.slice(-2)).toEqual(["combustivel", "reserva"]);
      expect(c.quimicos.slice(0, -2)).toEqual(sem.quimicos);
      expect([c.q.combustivel, c.q.reserva]).toEqual([cc.combustivel_inicial, cc.reserva_inicial]);
      expect(c.grafo.quimicos.filter((q) => METAB.includes(q.nome)).map((q) => q.receptor)).toEqual([null, null]);
      /* G-RECEPTOR-M: o cerebro recebe os mesmos receptores */
      expect(c.receptores()).toEqual(sem.receptores());
      expect(c.paraDict().metabolismo).toEqual({ resto_combustivel: 0, contas: Object.fromEntries(CONTAS_METABOLISMO.map((k) => [k, 0])) });
      expect(sem.paraDict().metabolismo).toBeUndefined();
      expect(sem.contas_metabolismo).toBeNull();
    }
  });

  test("as checagens passam em toda combinacao; as retroalimentacoes sao negativas (nenhum laco novo)", () => {
    for (const cc of [MIN, configCorpo({ ...MIN, vida: true }), configCorpo({ ...MIN, vida: true, drives_novos: true }), CCO_METABOLISMO,
      configCorpo({ ...CCO_METABOLISMO, medo_da_mao: 0 }), FRACAO, CCO_CORPO_V11]) {
      for (const mundo of [false, true]) {
        const g = grafoDoCorpo(cc, taxasDe(cc), mundo);
        const rel = checarGrafo(g);
        const ccSem = configCorpo({ ...cc, metabolismo: false });
        const sem = checarGrafo(grafoDoCorpo(ccSem, taxasDe(ccSem), mundo));
        expect(rel.lacos).toEqual(sem.lacos);
        expect(rel.so_pelo_teto).toEqual(sem.so_pelo_teto);
        expect(new Set(rel.sumidouros.combustivel)).toEqual(new Set(["reacao:armazenamento", "emissor:gasto_basal_acordado",
          "emissor:gasto_basal_dormindo", "emissor:dono:brincar", "emissor:pet:brincar", "emissor:pet:explorar", "emissor:andar", "teto"]));
        expect(rel.fontes.combustivel).toEqual(["reacao:digestao", "reacao:mobilizacao"]);
        expect([rel.sumidouros.reserva, rel.fontes.reserva]).toEqual([["reacao:mobilizacao", "teto"], ["reacao:armazenamento"]]);
        const falta = g.emissores.find((e) => e.nome === "falta_combustivel")!;
        expect([falta.gatilho, falta.fase, falta.limiar, falta.efeitos]).toEqual(["abaixo", 2, cc.falta_limiar, [["cansaco", cc.falta_cansaco]]]);
        /* G-RECEPTOR-M: nenhum emissor novo sobe o cansaco fora da falta */
        const sobeCansaco = (gr: GrafoCorpo): string[] => gr.emissores.filter((e) => e.efeitos.some(([q, d]) => q === "cansaco" && d > 0)).map((e) => e.nome);
        expect(new Set(sobeCansaco(g))).toEqual(new Set([...sobeCansaco(grafoDoCorpo(ccSem, taxasDe(ccSem), mundo)), "falta_combustivel"]));
      }
    }
  });

  test("as tabelas feitas para falhar falham alto: o combustivel sem gasto e a reserva sem armazenamento", () => {
    const g = grafoDoCorpo(CCO_METABOLISMO, taxasDe(CCO_METABOLISMO), true);
    checarGrafo(g);
    const semComb = (manter: string[] = []): GrafoCorpo => ({ ...g, emissores: g.emissores.flatMap((e) => {
      if (manter.includes(e.nome) || !e.efeitos.some(([q]) => q === "combustivel")) return [e];
      const ef = e.efeitos.filter(([q]) => q !== "combustivel");
      return ef.length ? [{ ...e, efeitos: ef }] : [];
    }) });
    expect(() => checarGrafo(semComb())).toThrow(/so saem pelo teto/);
    expect(() => checarGrafo({ ...g, reacoes: g.reacoes.filter((r) => r.nome !== "armazenamento") })).toThrow(/transferencia consome sem fonte/);
    checarGrafo(semComb(["gasto_basal_acordado", "gasto_basal_dormindo"]));       // so o basal ja basta como gasto de verdade
  });

  test("a forma das pecas novas (as tabelas do tests/test_metabolismo.py)", () => {
    const q = [quimico("a", 10), quimico("b", 10)];
    const gasto = emissor("gasta_a", "tick", 1, [["a", -1]]), sobe = emissor("sobe_a", "tick", 1, [["a", 1]]);
    const gastaB = emissor("gasta_b", "tick", 1, [["b", -1]]);
    const ok: Reacao = { nome: "t", consome: ["a"], produz: ["b"], taxa: 5, le: "a", lado: "acima", limiar: 3 };
    const volta: Reacao = { nome: "v", consome: ["b"], produz: ["a"], taxa: 5, le: "a", lado: "abaixo", limiar: 2 };
    const gr = (reacoes: Reacao[], emissores = [gasto, sobe]): GrafoCorpo => ({ quimicos: q, reacoes, emissores });
    checarGrafo(gr([ok, volta]));
    for (const ruim of [{ ...ok, consome: ["a", "b"] }, { ...ok, lado: "dentro" }, { ...ok, le: null }, { ...ok, produz: ["a"] },
      { ...ok, fracoes: [["b", 1, 2]] as [string, number, number][] }, { ...ok, limiar: -1 },
      { nome: "x", consome: ["a"], produz: ["b"], taxa: 5, limiar: 3 }]) {
      expect(() => checarGrafo(gr([ruim, volta])), JSON.stringify(ruim)).toThrow(GrafoInvalido);
    }
    expect(() => checarGrafo(gr([{ ...ok, le: "z" }, volta]))).toThrow(/fora da tabela/);
    expect(() => checarGrafo(gr([{ nome: "d", consome: ["a"], produz: ["b"], taxa: 5, fracoes: [["a", 1, 2]] }]))).toThrow(/fracao/);
    const abaixo = emissor("falta", "abaixo", 2, [["b", 1]], { le: [leitura("a", 1, 1, -1)], limiar: 3 });
    checarGrafo(gr([], [gasto, sobe, abaixo, gastaB]));
    for (const ruim of [{ ...abaixo, le: [leitura("a", 1, 1)] }, { ...abaixo, fase: 1 }, { ...abaixo, divisor: 2 }]) {
      expect(() => checarGrafo(gr([], [gasto, sobe, ruim, gastaB]))).toThrow(/abaixo/);
    }
    /* a transferencia "acima" que alimenta um quimico que volta ao lido por um emissor fecha um laco de ganho 1: falha alto */
    const laco = emissor("b_faz_a", "limiar", 2, [["a", 1]], { le: [leitura("b", 1, 2)], limiar: 0, divisor: 2 });
    checarGrafo(gr([ok], [gasto, sobe, laco, gastaB]));
    expect(() => checarGrafo(gr([ok], [gasto, sobe, { ...laco, le: [leitura("b", 1, 1)] }, gastaB]))).toThrow(/ganho >= 1/);
  });
});
const METAB = ["combustivel", "reserva"];

// ================================================================== G-MEC-M
describe("G-MEC-M: a conta exata de cada peca", () => {
  test("a conversao com o resto, a de 1/1 e o descarte no teto", () => {
    const cc = configCorpo({ ...MIN, conversao_num: 2, conversao_den: 3 });
    let c = corpo(cc, { fome: 1000, combustivel: 300000 });
    c.resto_combustivel = 2;
    c.acaoDono("alimentar");                                  // digere 1000 (a fome): 2 + 2000 = 2002 -> 667 e resto 1
    expect([c.digerido_tick, c.q.combustivel, c.resto_combustivel, contas(c).convertido]).toEqual([1000, 300000 + 667, 1, 667]);
    c = corpo(MIN, { fome: 90000, combustivel: 300000 });
    c.acaoPet("comer");
    expect([c.q.combustivel, c.q.fome]).toEqual([300000 + 22500, 90000 - 22500]);
    c = corpo(MIN, { fome: C, combustivel: C - 100 });
    c.acaoDono("alimentar");
    expect([c.q.combustivel, contas(c).descartado_teto]).toEqual([C, 202500 - 100]);
  });

  test("o gasto basal acordado e dormindo, e no fundo so sai o que havia", () => {
    for (const [dormindo, gasto] of [[false, 375], [true, 187]] as [boolean, number][]) {
      const c = corpo(MIN, { combustivel: 300000, reserva: 1000 });
      passo(c, dormindo);
      expect([c.q.combustivel, c.q.reserva, contas(c).gasto_basal]).toEqual([300000 - gasto, 1000, gasto]);
    }
    const c = corpo(MIN, { combustivel: 100, reserva: 0 });
    passo(c);
    expect([c.q.combustivel, contas(c).gasto_basal]).toEqual([0, 100]);
    /* o v11: 300 acordado e 150 dormindo */
    for (const [dormindo, gasto] of [[false, 300], [true, 150]] as [boolean, number][]) {
      const v = corpo(CCO_CORPO_V11, { combustivel: 300000, reserva: 1000 });
      passo(v, dormindo);
      expect(contas(v).gasto_basal).toBe(gasto);
    }
  });

  const atividades: Record<string, (c: Corpo) => void> = {
    pet_brincar: (c) => c.acaoPet("brincar"), pet_explorar: (c) => c.acaoPet("explorar"), dono_brincar: (c) => c.acaoDono("brincar"),
    andar: (c) => c.estimuloAndar(37, CMU.custo_energia_por_subunidade),
  };
  for (const [nome, faz] of Object.entries(atividades)) {
    test(`${nome}: tira do combustivel o que soma ao cansaco (1/1) e o fator dele (4/5 no v11); o cansaco de hoje nao muda`, () => {
      for (const cc of [MIN, configCorpo({ ...MIN, gasto_atividades_num: 4, gasto_atividades_den: 5 })]) {
        const c = corpo(cc, { combustivel: 300000, cansaco: 1000 });
        const sem = corpo(configCorpo({ ...cc, metabolismo: false }), { cansaco: 1000 });
        faz(c);
        faz(sem);
        const subiu = c.q.cansaco - 1000;
        expect(subiu).toBeGreaterThan(0);
        expect(300000 - c.q.combustivel).toBe(gastoDaAtividade(cc, subiu));
        expect(contas(c).gasto_atividade).toBe(300000 - c.q.combustivel);
        if (cc.gasto_atividades_den === 1) expect(300000 - c.q.combustivel).toBe(subiu);
        expect(Object.fromEntries(Object.entries(c.q).filter(([k]) => !METAB.includes(k)))).toEqual(sem.q);
      }
    });
  }
  test("a atividade com pouco combustivel: so sai o que havia", () => {
    const c = corpo(MIN, { combustivel: 10 });
    c.acaoPet("brincar");
    expect([c.q.combustivel, contas(c).gasto_atividade]).toEqual([0, 10]);
  });

  test("o armazenamento e a mobilizacao nos limiares (o basal sai antes)", () => {
    const casos: [[number, number], [number, number]][] = [
      [[A + 1000, 0], [A + 625 - 375, 375]],      // acima: ate a taxa
      [[A + 500, 0], [A, 125]],                   // acima: so ate o limiar
      [[A + 375, 0], [A, 0]],                     // o basal o leva ao limiar: nada vai
      [[A + 1000, C - 50], [A + 625 - 50, C]],    // a reserva cheia: so o que cabe
      [[M + 375, 1000], [M, 1000]],               // entre os limiares: nada anda
      [[M + 100, 1000], [M, 725]],                // abaixo: ate o limiar
      [[M - 100, 1000], [M - 100, 625]],          // abaixo: ate a taxa
      [[M - 100, 50], [M - 425, 0]],              // abaixo: so o que a reserva tem
    ];
    for (const [[comb, res], esperado] of casos) {
      const c = corpo(MIN, { combustivel: comb, reserva: res });
      passo(c);
      expect([c.q.combustivel, c.q.reserva], `${comb}, ${res}`).toEqual(esperado);
    }
    const c = corpo(MIN, { combustivel: M, reserva: 1000 });
    passo(c, true);
    expect([c.q.combustivel, c.q.reserva]).toEqual([M, 813]);
  });

  test("a falta sobe o cansaco so abaixo de C/4, depois da mobilizacao; o teto do cansaco", () => {
    const base = 1000;
    for (const [comb, res, falta] of [[F + 375, 0, false], [F + 374, 0, true], [F + 374, 1, false], [F, 375, false], [F - 1, 1000, true],
      [F - 1000, 375, true], [0, 0, true]] as [number, number, boolean][]) {
      const c = corpo(MIN, { combustivel: comb, reserva: res, cansaco: base });
      const sem = corpo(configCorpo({ ...MIN, metabolismo: false }), { cansaco: base });
      passo(c);
      passo(sem);
      expect(c.q.cansaco - sem.q.cansaco, `${comb}, ${res}`).toBe(falta ? 500 : 0);
      expect(Object.fromEntries(Object.entries(c.q).filter(([k]) => k !== "cansaco" && !METAB.includes(k))))
        .toEqual(Object.fromEntries(Object.entries(sem.q).filter(([k]) => k !== "cansaco")));
    }
    const c = corpo(MIN, { combustivel: 0, reserva: 0, cansaco: C - 100 });
    passo(c);
    expect(c.q.cansaco).toBe(C);
  });
});

// ================================================================== G-CONS-M e G-HOJE-M
describe("G-CONS-M: as contas fecham a cada operacao", () => {
  test("uma sequencia longa com a conversao 2/3 e o teto mordendo (todas as contas andam)", () => {
    const cc = configCorpo({ ...CCO_METABOLISMO, conversao_num: 2, conversao_den: 3, combustivel_inicial: C - 5000 });
    const c = Corpo.deEstado(NASCER, { cc, comMundo: true });
    let x = 11;
    const rnd = (): number => { x = (Math.imul(x, 1103515245) + 12345) >>> 0; return x / 4294967296; };   // so para sortear as operacoes
    for (let tick = 0; tick < 6000; tick++) {
      const r = rnd();
      if (r < 0.75) c.passo({ tick, dormindo: rnd() < 0.3, sujeira: Math.floor(rnd() * 3) });
      else if (r < 0.85) c.acaoDono("alimentar");
      else if (r < 0.9) c.acaoPet((["brincar", "explorar", "comer"] as AcaoPet[])[Math.floor(rnd() * 3)]);
      else if (r < 0.95) c.estimuloAndar(Math.floor(rnd() * 200), CMU.custo_energia_por_subunidade);
      else c.acaoDono("brincar");
      fecha(c, cc.combustivel_inicial, cc.reserva_inicial);
    }
    expect(CONTAS_METABOLISMO.every((k) => contas(c)[k] > 0)).toBe(true);
  });
});

/** rejoga uma vida de hoje em malha aberta (vida_malha_aberta do exportador) com estas chaves; devolve q depois de cada tick */
function rejogar(v: VidaAberta, cc: ConfigCorpo, q0: Record<string, number> = {}): { marcas: string[]; porTick: Record<string, number>[]; c: Corpo } {
  const nomes = G.vida.quimicos;
  const c = new Corpo({ ...Object.fromEntries(nomes.map((n, i) => [n, v.q_inicial[i]])),
    ...(cc.metabolismo ? { combustivel: cc.combustivel_inicial, reserva: cc.reserva_inicial } : {}), ...q0 }, { cc });
  const marcas: string[] = [];
  const marca = (): void => { marcas.push(nomes.map((n) => c.q[n]).join(",") + ";"); };
  const porTick: Record<string, number>[] = [];
  let k = 0;
  const eventosAte = (t: number): void => {
    for (; k < v.eventos.length && v.eventos[k][0] === t; k++) {
      const [, quem, acao] = v.eventos[k];
      if (quem === "pet") c.acaoPet(acao as AcaoPet);
      else if (quem === "dono") c.acaoDono(acao);
      else throw new Error(`evento desconhecido: ${quem}`);
      marca();
    }
  };
  for (let t = 0; t < v.ticks.length; t++) {
    eventosAte(t);
    const cod = v.ticks.charCodeAt(t) - 97;
    c.passo({ tick: v.tick_inicial + t, dormindo: cod >= 8, sujeira: cod % 8 });
    marca();
    porTick.push({ ...c.q });
    if (cc.metabolismo) fecha(c, (q0.combustivel ?? cc.combustivel_inicial), (q0.reserva ?? cc.reserva_inicial));
  }
  eventosAte(v.ticks.length);
  expect(k).toBe(v.eventos.length);
  return { marcas, porTick, c };
}
const CC_VIDA = configCorpo({ ligada: true, digestao: true, vida: true });
const CC_VIDA_M = configCorpo({ ...CC_VIDA, metabolismo: true });

describe("G-HOJE-M em malha aberta: as vidas de hoje do gabarito, com o metabolismo", () => {
  test("com o combustivel acima de C/4, os quimicos de antes sao os de sem o metabolismo, tick a tick, e dao o sha256 do Python", () => {
    expect(G.vida.vidas.length).toBe(3);
    let cheias = 0;
    for (const v of G.vida.vidas) {
      /* o corpo nasce cheio: o gate vale enquanto o combustivel fica acima de C/4 */
      const com = rejogar(v, CC_VIDA_M, { combustivel: C, reserva: C });
      const sem = rejogar(v, CC_VIDA);
      const t = com.porTick.findIndex((q) => q.combustivel < F);
      const ate = t < 0 ? com.porTick.length : t;
      expect(com.porTick.slice(0, ate).map((q) => Object.fromEntries(Object.entries(q).filter(([k]) => !METAB.includes(k)))))
        .toEqual(sem.porTick.slice(0, ate));
      expect(hex(sha256(sem.marcas.join("")))).toBe(v.sha256);
      if (t < 0) {
        cheias += 1;
        expect(hex(sha256(com.marcas.join("")))).toBe(v.sha256);
        expect(Object.values(contas(com.c)).filter((x) => x > 0).length).toBeGreaterThanOrEqual(3);
      }
    }
    /* a aleatorio 101 gasta o corpo cheio e entra em falta no dia 2; a relapso 303 e a atencioso 202 nunca */
    expect(cheias).toBe(2);
  });

  test("com a falta, so o cansaco difere, a partir do tick dela, e +500 (cortado em C)", () => {
    let vistas = 0;
    for (const v of G.vida.vidas) {
      const com = rejogar(v, CC_VIDA_M);
      const sem = rejogar(v, CC_VIDA);
      const t = com.porTick.findIndex((q) => q.combustivel < F);
      if (t < 0) continue;
      vistas += 1;
      const velhos = (q: Record<string, number>): Record<string, number> => Object.fromEntries(Object.entries(q).filter(([k]) => !METAB.includes(k)));
      expect(com.porTick.slice(0, t).map(velhos)).toEqual(sem.porTick.slice(0, t));
      const a = velhos(com.porTick[t]), b = sem.porTick[t];
      expect(a.cansaco).toBe(Math.min(C, b.cansaco + CC_VIDA_M.falta_cansaco));
      expect(a.cansaco).not.toBe(b.cansaco);
      expect({ ...a, cansaco: 0 }).toEqual({ ...b, cansaco: 0 });
    }
    expect(vistas).toBe(3);                                  // do nascimento (C/2 e C/4), as tres vidas entram em falta
  });

  test("a sequencia longa da etapa 6, com o metabolismo cheio: os quimicos de antes ate a falta sao os de sem ele", () => {
    const cheio = configCorpo({ ...CCO_METABOLISMO, combustivel_inicial: C, reserva_inicial: C });
    const com = Corpo.deEstado(NASCER, { cc: cheio, comMundo: true });
    const sem = Corpo.deEstado(NASCER, { cc: CCO_DRIVES, comMundo: true });
    let falta = -1;
    G.etapa6.sequencia.ops.forEach((op, i) => {
      aplicar(com, op);
      aplicar(sem, op);
      if (falta < 0 && com.q.combustivel < F) falta = i;
      if (falta < 0) expect(G.etapa6.quimicos.map((n) => com.q[n]), `op ${i}`).toEqual(qDe(sem));
      fecha(com, C, C);
    });
    /* nas operacoes sorteadas da etapa 6, o corpo cheio entra em falta na operacao 355 de 3000: o sha256 da sequencia inteira nao vale aqui */
    expect(falta).toBe(355);
  });
});
