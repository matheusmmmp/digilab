/* O corpo em TS (docs/TAREFA_V2_CORPO_DRIVES.md, etapa 7; o G-PAR da secao 12): motor/corpo.ts reproduz, inteiro a inteiro, o gabarito
   do corpo do Python (tests/gabaritos/corpo_quimica_python.json, de experiments/exportar_gabarito_corpo.py), lido do proprio lugar,
   sem copia. Confere a config e as taxas, as contas inteiras (div_arred, meia-vida), o grafo (a tabela e o relato das checagens, em
   cada combinacao de sub-chaves) e as checagens que falham alto, o corpo que nasce de um Estado, a grade de casos de cada etapa (a
   quimica, a digestao, a digestao lenta, a Vida, os estimulos do mundo fisico, os drives novos e os gestos), as vidas de hoje em malha
   aberta (com o sha256 de q depois de cada operacao) e a sequencia longa da etapa 6 (o sha256 de q e da janela do tedio). */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CCO, CMU, DUR_CLASSICA, type ConfigCorpo } from "../motor/constantes.ts";
import {
  CCO_DRIVES, CCO_LIGADA, Corpo, DURACOES_PESQUISA, GrafoInvalido, checarGrafo, ciclosDoGrafo, configCorpo, emissor, grafoDoCorpo,
  kMeiaVida, leitura, limiaresEstagio, passoMeiaVida, quimico, quimicosDe, taxasDe, ticksDeEstagio, type DuracoesEstagio,
  type GrafoCorpo,
} from "../motor/corpo.ts";
import { divArred, sha256 } from "../motor/mundo.ts";
import type { AcaoPet } from "../motor/tipos.ts";

type Rec = Record<string, unknown>;
type Op = (string | number)[];
interface Caso {
  q: number[]; op: Op; q_depois: number[]; privacao: boolean; receptores: number[];
  digerido?: number; digerido_no_tick?: number; descartado?: number;
}
interface CasoE6 { q: number[]; janela: string[]; op: Op; q_depois: number[]; janela_depois: string[]; receptores: number[] }
interface VidaAberta {
  dono: string; semente: number; q_inicial: number[]; tick_inicial: number; ticks: string; eventos: [number, string, string][];
  pontos: [number, number[]][]; q_final: number[]; sha256: string; digerido_total?: number; descartado_total?: number;
  estagios?: [number, string][];
}
const G = JSON.parse(readFileSync(new URL("../../../tests/gabaritos/corpo_quimica_python.json", import.meta.url), "utf8")) as {
  versao: number; quimicos: string[]; escala: number; escala_receptor: number; bits_meia_vida: number; taxas: Rec; casos: Caso[];
  meia_vida: number[][]; div_arred: number[][]; vidas: VidaAberta[];
  digestao: { quimicos: string[]; taxa_digestao: number; casos: Caso[]; vidas: VidaAberta[] };
  digestao_lenta: { quimicos: string[]; taxa_digestao: number; casos: Caso[] };
  vida: { quimicos: string[]; vida_decaimento: number; ticks_de_estagio: Record<string, number[]>; limiares: Record<string, number[]>;
    casos: { duracao: string; vida: number; estagio: string; vida_depois: number; estagio_depois: string }[]; vidas: VidaAberta[] };
  mundo: { custo_andar_por_subunidade: number; nutricao_fruta: number; efeito_podre: number; casos: Caso[];
    digestao: { quimicos: string[]; casos: Caso[] } };
  etapa6: { quimicos: string[]; config: Rec; receptores: string[]; casos: CasoE6[];
    sequencia: { ops: Op[]; sha256: string; q_final: number[]; janela_final: string[] } };
  config: Rec;
  grafo: { chaves: string; com_mundo: boolean; config: Partial<ConfigCorpo>; tabela: { quimicos: unknown[][]; reacoes: unknown[][]; emissores: Rec[] }; relato: Rec }[];
  de_estado: { chaves: string; com_mundo: boolean; config: Partial<ConfigCorpo>; estado: { tick: number; fome: number; higiene: number;
    energia: number; humor: number; saude: number }; quimicos: string[]; q: number[]; receptores: Rec; drives: Rec; para_dict: Rec }[];
  etapa6_mundo: { quimicos: string[]; casos: (CasoE6 & { privacao: boolean; drives: Rec; digerido: number; digerido_no_tick: number; descartado: number })[] };
};

const RECEPTORES_HOJE = ["fome", "higiene", "energia", "humor", "saude"];
const CC_DIGESTAO = configCorpo({ ligada: true, digestao: true });
const CC_LENTA = configCorpo({ ligada: true, digestao: true, taxa_digestao: 1000 });
const CC_VIDA = configCorpo({ ligada: true, digestao: true, vida: true });
const DURACOES: Record<string, DuracoesEstagio> = { pesquisa: DURACOES_PESQUISA, canonica: DUR_CLASSICA as unknown as DuracoesEstagio };
/** a ConfigMundo que o gabarito usou (a CONFIG_MUNDO_LIGADA do Python): a nutricao da fruta e o efeito da podre */
const MUNDO = { nutricao_fruta: G.mundo.nutricao_fruta, efeito_podre: G.mundo.efeito_podre };

const hex = (bytes: number[]): string => bytes.map((b) => b.toString(16).padStart(2, "0")).join("");
const qDe = (c: Corpo): number[] => c.quimicos.map((n) => c.q[n]);
const corpoDe = (q: number[], cc: ConfigCorpo, comMundo = false): Corpo =>
  new Corpo(Object.fromEntries(quimicosDe(cc, comMundo).map((n, i) => [n, q[i]])), { cc, comMundo });

/** as operacoes do exportador (_aplicar e _aplicar_e6), com os mesmos argumentos */
function aplicar(c: Corpo, op: Op): void {
  const [tipo, a, b, d] = op;
  switch (tipo) {
    case "passo": c.passo({ tick: d as number, dormindo: Boolean(a), sujeira: b as number }); break;
    case "dono": c.acaoDono(a as string); break;
    case "pet": c.acaoPet(a as AcaoPet); break;
    case "bola": c.estimuloBola(a as number); break;
    case "fruta": c.estimuloFruta(a as number, b as number); break;
    case "pet_mundo": c.acaoPet(a as AcaoPet, true); break;
    case "andar": c.estimuloAndar(a as number, b as number); break;
    case "consumo": c.estimuloConsumoMundo(a as string, b as string, MUNDO, d as number); break;
    case "atividade": c.atividade(a as string); break;
    case "novidade": c.estimuloNovidade(a as number); break;
    default: throw new Error(`operacao desconhecida: ${JSON.stringify(op)}`);
  }
}

function conferirCasos(casos: Caso[], cc: ConfigCorpo): void {
  for (const caso of casos) {
    const c = corpoDe(caso.q, cc);
    aplicar(c, caso.op);
    const rec = c.receptores();
    const visto: Rec = { q: caso.q, op: caso.op, q_depois: qDe(c), privacao: c.emPrivacao(), receptores: RECEPTORES_HOJE.map((r) => rec[r]) };
    if (cc.digestao) Object.assign(visto, { digerido: c.digerido_total, digerido_no_tick: c.digerido_no_tick, descartado: c.descartado_total });
    expect(visto, JSON.stringify(caso.op)).toEqual(caso);
  }
}

/** vida_malha_aberta do exportador: os eventos antes do tick em que acontecem (na ordem do log), o tick com o sono e a sujeira do
 *  caractere, e a marca de q depois de cada operacao no sha256 */
function rejogar(v: VidaAberta, cc: ConfigCorpo): void {
  const c = corpoDe(v.q_inicial, cc);
  const marcas: string[] = [];
  const marca = (): void => { marcas.push(qDe(c).join(",") + ";"); };
  const pontos: [number, number[]][] = [];
  const estagios: [number, string][] = cc.vida ? [[0, c.estagio()]] : [];
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
    if (cc.vida && c.estagio() !== estagios[estagios.length - 1][1]) estagios.push([t + 1, c.estagio()]);
    if ((t + 1) % 60 === 0) pontos.push([t + 1, qDe(c)]);
  }
  eventosAte(v.ticks.length);
  expect(k).toBe(v.eventos.length);
  expect(pontos).toEqual(v.pontos);
  expect(qDe(c)).toEqual(v.q_final);
  expect(hex(sha256(marcas.join("")))).toBe(v.sha256);
  if (cc.digestao) expect([c.digerido_total, c.descartado_total]).toEqual([v.digerido_total, v.descartado_total]);
  if (cc.vida) expect(estagios).toEqual(v.estagios);
}

const ccDoGabarito = (sub: Partial<ConfigCorpo>): ConfigCorpo => configCorpo(sub);

describe("config e taxas", () => {
  test("a ConfigCorpo e a do Python, campo a campo, e o gabarito e a versao 5", () => {
    expect(G.versao).toBe(5);
    expect(CCO).toEqual(G.config);
    for (const [k, v] of Object.entries(G.etapa6.config)) expect(CCO_DRIVES[k as keyof ConfigCorpo], k).toBe(v);
    expect([CCO.escala, CCO.escala_receptor, CCO.bits_meia_vida]).toEqual([G.escala, G.escala_receptor, G.bits_meia_vida]);
    expect([CC_DIGESTAO.taxa_digestao, CC_LENTA.taxa_digestao, CC_VIDA.vida_decaimento])
      .toEqual([G.digestao.taxa_digestao, G.digestao_lenta.taxa_digestao, G.vida.vida_decaimento]);
    expect([CMU.custo_energia_por_subunidade, CMU.nutricao_fruta, CMU.efeito_podre])
      .toEqual([G.mundo.custo_andar_por_subunidade, G.mundo.nutricao_fruta, G.mundo.efeito_podre]);
  });
  test("as sub-chaves exigem a anterior e os numeros sao inteiros positivos (falha alto, como no __post_init__)", () => {
    expect(() => configCorpo({ digestao: true })).toThrow(/exige ConfigCorpo.ligada/);
    expect(() => configCorpo({ ligada: true, digestao: true, drives_novos: true })).toThrow(/exige ConfigCorpo.vida/);
    expect(() => configCorpo({ ligada: true, tedio_sobe: 0 })).toThrow(/inteiro positivo/);
    expect(() => configCorpo({ ligada: true, janela_tedio: 2.5 })).toThrow(/inteiro positivo/);
    expect(() => configCorpo({ ligada: true, medo_da_mao: 2 })).toThrow(/medo_da_mao/);
    expect(() => new Corpo({}, { cc: CCO })).toThrow(/desligada/);
  });
  test("as taxas de hoje na escala C sao as do Python (os numeros de config.Config, pelo espelho C)", () => {
    expect(JSON.parse(JSON.stringify(taxasDe(CCO_LIGADA)))).toEqual(G.taxas);
  });
  test("os quimicos de cada combinacao de sub-chaves", () => {
    expect(quimicosDe(CCO_LIGADA)).toEqual(G.quimicos);
    expect(quimicosDe(CC_DIGESTAO)).toEqual(G.digestao.quimicos);
    expect(quimicosDe(CC_LENTA)).toEqual(G.digestao_lenta.quimicos);
    expect(quimicosDe(CC_VIDA)).toEqual(G.vida.quimicos);
    expect(quimicosDe(CCO_DRIVES, true)).toEqual(G.etapa6.quimicos);
    expect(quimicosDe(CCO_DRIVES, true)).toEqual(G.etapa6_mundo.quimicos);
  });
  test("os ticks de estagio e os limiares da Vida nas duas duracoes", () => {
    for (const [nome, d] of Object.entries(DURACOES)) {
      expect(ticksDeEstagio(d), nome).toEqual(G.vida.ticks_de_estagio[nome]);
      expect(limiaresEstagio(CC_VIDA, d), nome).toEqual(G.vida.limiares[nome]);
    }
    expect(() => limiaresEstagio(configCorpo({ ligada: true, digestao: true, vida: true, vida_decaimento: 500 }))).toThrow(/Vida acaba/);
  });
});

describe("as contas inteiras", () => {
  test("div_arred: meio longe do zero, sem -0", () => {
    for (const [n, d, r] of G.div_arred) expect(divArred(n, d), `${n}/${d}`).toBe(r);
  });
  test("o passo da meia-vida, com o minimo de 1", () => {
    for (const [q, k, r] of G.meia_vida) expect(passoMeiaVida(q, k, G.bits_meia_vida), `${q}, ${k}`).toBe(r);
  });
  test("as constantes da meia-vida derivam de h (so conferencia; o tick nunca as deriva)", () => {
    expect([kMeiaVida(30), kMeiaVida(60), kMeiaVida(1440)]).toEqual([CCO.k_meia_vida_susto, CCO.k_meia_vida_dor, CCO.k_meia_vida_estresse]);
  });
});

/** a tabela no formato do gabarito */
const tabela = (g: GrafoCorpo): unknown => ({
  quimicos: g.quimicos.map((q) => [q.nome, q.teto, q.descarte, q.receptor, q.leitura, q.meia_vida, q.k_meia_vida]),
  reacoes: g.reacoes.map((r) => [r.nome, r.consome, r.produz, r.taxa]),
  emissores: g.emissores.map((e) => ({ nome: e.nome, gatilho: e.gatilho, fase: e.fase, efeitos: e.efeitos,
    le: e.le.map((le) => [le.quimico, le.num, le.den, le.sinal]), limiar: e.limiar, divisor: e.divisor, variavel: e.variavel })),
});

describe("o grafo (secao 18)", () => {
  test("a tabela unica e o relato das checagens sao os do Python em toda combinacao de sub-chaves, com e sem o mundo", () => {
    expect(G.grafo.length).toBe(12);
    for (const item of G.grafo) {
      const cc = ccDoGabarito(item.config);
      const g = grafoDoCorpo(cc, taxasDe(cc), item.com_mundo);
      const nome = `${item.chaves}/${item.com_mundo}`;
      expect(tabela(g), nome).toEqual(item.tabela);
      expect(checarGrafo(g), nome).toEqual(item.relato);
    }
  });
  test("o Corpo carrega a tabela e a confere; um emissor tirado da tabela some do tick", () => {
    const corpo = Corpo.deEstado({ tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 }, { cc: CCO_DRIVES, comMundo: true });
    expect(corpo.relato_grafo.pares_meia_vida_mesma_ordem).toEqual([["dor", "susto"]]);
    const est = { tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 };
    const a = Corpo.deEstado(est), b = Corpo.deEstado(est);
    b.grafo = { ...b.grafo, emissores: b.grafo.emissores.filter((e) => e.nome !== "tristeza_tick") };
    a.passo({ tick: 0, dormindo: false, sujeira: 0 });
    b.passo({ tick: 0, dormindo: false, sujeira: 0 });
    expect(a.q.tristeza).toBe(b.q.tristeza + a.t.tristeza_por_tick);
    expect(a.q.fome).toBe(b.q.fome);
  });

  const C = CCO.escala;
  const q = (nome: string, extra: Parameters<typeof quimico>[3] = {}, teto = C, descarte = true) => quimico(nome, teto, descarte, extra);
  const g = (quimicos: GrafoCorpo["quimicos"], reacoes: GrafoCorpo["reacoes"], emissores: GrafoCorpo["emissores"]): GrafoCorpo =>
    ({ quimicos, reacoes, emissores });
  const laco = (ab: [number, number], ba: [number, number]): GrafoCorpo => g([q("a"), q("b")], [], [
    emissor("a_faz_b", "limiar", 2, [["b", 1]], { le: [leitura("a", ...ab)], limiar: 0, divisor: 2, variavel: true }),
    emissor("b_faz_a", "limiar", 2, [["a", 1]], { le: [leitura("b", ...ba)], limiar: 0, divisor: 2, variavel: true }),
    emissor("tira_a", "estimulo", 0, [["a", -1]]), emissor("tira_b", "estimulo", 0, [["b", -1]])]);

  test("cada checagem falha alto (as tabelas do tests/test_corpo_grafo.py)", () => {
    const falha = (gr: GrafoCorpo, re: RegExp): void => {
      expect(() => checarGrafo(gr)).toThrow(GrafoInvalido);
      expect(() => checarGrafo(gr)).toThrow(re);
    };
    falha(g([q("a")], [{ nome: "r", consome: ["a"], produz: ["b"], taxa: 10 }], []), /nao fechado/);
    falha(g([q("a")], [], [emissor("e", "limiar", 2, [["a", 1]], { le: [leitura("x", 1, 2)], divisor: 2, variavel: true })]), /nao fechado/);
    falha(g([q("a", {}, C, false)], [], [emissor("sobe", "tick", 1, [["a", 5]])]), /sem sumidouro/);
    checarGrafo(g([q("a", { meia_vida: 30, k_meia_vida: 1497 }, C, false)], [], [emissor("sobe", "tick", 1, [["a", 5]])]));
    falha(g([q("a", {}, 0, false), q("b")], [{ nome: "r", consome: ["a", "b"], produz: [], taxa: 10 }],
      [emissor("sobe_b", "tick", 1, [["b", 1]])]), /automantido/);
    checarGrafo(g([q("a"), q("b")], [{ nome: "r", consome: ["a", "b"], produz: [], taxa: 10 }], [emissor("sobe_b", "tick", 1, [["b", 1]])]));
    falha(laco([1, 1], [1, 1]), /ganho >= 1/);
    falha(laco([3, 2], [2, 3]), /ganho >= 1/);
    expect(checarGrafo(laco([1, 2], [3, 4])).lacos).toEqual([{ ciclo: ["a", "b"], ganho: [3, 8] }]);
    falha(g([q("a"), q("b")], [], [
      emissor("b_corta_tira_a", "estimulo", 0, [["a", -10]], { le: [leitura("b", 1, 1, -1)] }),
      emissor("a_faz_b", "limiar", 2, [["b", 1]], { le: [leitura("a", 1, 1)], divisor: 2, variavel: true }),
      emissor("tira_b", "estimulo", 0, [["b", -1]])]), /ganho >= 1/);
    falha(g([q("a"), q("a")], [], []), /repetido/);
    falha(g([q("a", { meia_vida: 30 })], [], []), /meia-vida e k/);
    falha(g([q("a")], [], [emissor("e", "lua_cheia", 1, [["a", 1]])]), /gatilho/);
    falha(g([q("a")], [], [emissor("e", "tick", 1, [["a", 0]])]), /efeitos/);
    falha(g([q("a")], [], [emissor("e", "estimulo", 1, [["a", -1]])]), /fase/);
  });
  test("o grafo de hoje nao tem laco (os ciclos do grafo receptor -> emissor)", () => {
    const gr = grafoDoCorpo(CCO_DRIVES, taxasDe(CCO_DRIVES), true);
    expect(checarGrafo(gr).lacos).toEqual([]);
    expect(ciclosDoGrafo(new Map([["a|b", [1, 2]], ["b|c", [1, 2]], ["c|a", [1, 2]], ["b|a", [1, 2]]]))).toEqual([["a", "b"], ["a", "b", "c"]]);
  });
});

describe("o corpo que nasce de um Estado", () => {
  test("q, receptores, drives e para_dict iguais em toda combinacao e nos tres Estados", () => {
    expect(G.de_estado.length).toBe(36);
    for (const item of G.de_estado) {
      const c = Corpo.deEstado(item.estado, { cc: ccDoGabarito(item.config), comMundo: item.com_mundo });
      const nome = `${item.chaves}/${item.com_mundo}/${item.estado.tick}`;
      expect(c.quimicos, nome).toEqual(item.quimicos);
      expect(qDe(c), nome).toEqual(item.q);
      expect(c.receptores(), nome).toEqual(item.receptores);
      expect(c.drives(), nome).toEqual(item.drives);
      expect(c.paraDict(), nome).toEqual(item.para_dict);
    }
  });
  test("um drive fora da grade de C falha alto", () => {
    expect(() => Corpo.deEstado({ tick: 0, fome: 0.1234567, higiene: 1, energia: 1, humor: 1, saude: 1 })).toThrow(/grade/);
  });
});

describe("a grade de casos", () => {
  test("a quimica base: cada operacao, o estado depois, a privacao e os receptores", () => conferirCasos(G.casos, CCO_LIGADA));
  test("o orgao 1, a digestao na taxa C", () => conferirCasos(G.digestao.casos, CC_DIGESTAO));
  test("a digestao lenta (a reacao com a taxa mordendo)", () => conferirCasos(G.digestao_lenta.casos, CC_LENTA));
  test("os estimulos do mundo fisico, sem e com a digestao", () => {
    conferirCasos(G.mundo.casos, CCO_LIGADA);
    conferirCasos(G.mundo.digestao.casos, CC_DIGESTAO);
  });
  test("o orgao 2, a Vida em volta de cada limiar de estagio, nas duas duracoes", () => {
    for (const caso of G.vida.casos) {
      const c = new Corpo({ fome: 90000, desconforto: 0, cansaco: 45000, tristeza: 135000, dano: 0, alimento: 0, vida: caso.vida },
        { cc: CC_VIDA, duracoes: DURACOES[caso.duracao] });
      const antes = c.estagio();
      c.passo({ tick: 600, dormindo: false, sujeira: 0 });
      expect({ duracao: caso.duracao, vida: caso.vida, estagio: antes, vida_depois: c.q.vida, estagio_depois: c.estagio() }).toEqual(caso);
    }
  });
  test("a etapa 6: os drives novos e os gestos (o tick acordado e dormindo, o dono, o carinho, o tapa, as atividades e a novidade)", () => {
    for (const caso of G.etapa6.casos) {
      const c = corpoDe(caso.q, CCO_DRIVES, true);
      c.janela_tedio = [...caso.janela];
      aplicar(c, caso.op);
      const rec = c.receptores();
      expect({ q: caso.q, janela: caso.janela, op: caso.op, q_depois: qDe(c), janela_depois: c.janela_tedio,
        receptores: G.etapa6.receptores.map((r) => rec[r]) }, JSON.stringify(caso.op)).toEqual(caso);
    }
  });
  test("o mundo fisico no corpo da etapa 6, com a digestao e os drives lidos", () => {
    for (const caso of G.etapa6_mundo.casos) {
      const c = corpoDe(caso.q, CCO_DRIVES, true);
      c.janela_tedio = [...caso.janela];
      aplicar(c, caso.op);
      const rec = c.receptores();
      expect({ q: caso.q, janela: caso.janela, op: caso.op, q_depois: qDe(c), janela_depois: c.janela_tedio,
        receptores: G.etapa6.receptores.map((r) => rec[r]), privacao: c.emPrivacao(), drives: c.drives(),
        digerido: c.digerido_total, digerido_no_tick: c.digerido_no_tick, descartado: c.descartado_total }, JSON.stringify(caso.op)).toEqual(caso);
    }
  });
});

describe("as vidas de hoje em malha aberta", () => {
  test("a quimica sozinha: 3 vidas, o sha256 de q depois de cada operacao", () => { for (const v of G.vidas) rejogar(v, CCO_LIGADA); });
  test("com a digestao", () => { for (const v of G.digestao.vidas) rejogar(v, CC_DIGESTAO); });
  test("com a digestao e a Vida (os ticks em que o estagio muda)", () => { for (const v of G.vida.vidas) rejogar(v, CC_VIDA); });
  test("o corpo do nascimento e o Estado de hoje", () => {
    const c = Corpo.deEstado({ tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 }, { cc: CC_VIDA });
    expect(qDe(c)).toEqual(G.vida.vidas[0].q_inicial);
  });
});

describe("a sequencia longa da etapa 6", () => {
  test("3000 operacoes num corpo so, do nascimento: o sha256 de q e da janela depois de cada uma", () => {
    const c = Corpo.deEstado({ tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 }, { cc: CCO_DRIVES, comMundo: true });
    const marcas: string[] = [];
    for (const op of G.etapa6.sequencia.ops) {
      aplicar(c, op);
      marcas.push(JSON.stringify([qDe(c), c.janela_tedio]));
    }
    expect(qDe(c)).toEqual(G.etapa6.sequencia.q_final);
    expect(c.janela_tedio).toEqual(G.etapa6.sequencia.janela_final);
    expect(hex(sha256(marcas.join("")))).toBe(G.etapa6.sequencia.sha256);
  });
  test("as falhas altas dos estimulos novos", () => {
    const sem = Corpo.deEstado({ tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 }, { cc: CC_VIDA });
    expect(() => sem.acaoDono("tapa")).toThrow(/gestos/);
    expect(() => sem.atividade("bola")).toThrow(/drives_novos/);
    expect(() => sem.estimuloNovidade(1)).toThrow(/curiosidade/);
    expect(() => sem.acaoDono("treinar_corrida")).toThrow(/sem estimulo/);
    const sem_mundo = Corpo.deEstado({ tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 }, { cc: CCO_DRIVES });
    expect(() => sem_mundo.estimuloNovidade(1)).toThrow(/curiosidade/);
    const c = Corpo.deEstado({ tick: 0, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1 }, { cc: CCO_DRIVES, comMundo: true });
    expect(() => c.atividade("dormir")).toThrow(/desconhecida/);
    expect(() => c.estimuloNovidade(-1)).toThrow(/inteiro/);
    expect(() => c.estimuloAndar(1.5, CMU.custo_energia_por_subunidade)).toThrow(/inteiro/);
    expect(() => c.estimuloAndar(3, 1 / 7)).toThrow(/grade/);
    expect(() => c.estimuloConsumoMundo("pedra", "madura", CMU)).toThrow(/desconhecida/);
    expect(() => c.estimuloConsumoMundo("a", "verde", CMU)).toThrow(/situacao/);
  });
});
