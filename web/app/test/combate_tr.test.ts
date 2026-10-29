// A luta em tempo real (docs/ESPEC_COMBATE_TR.md; COMBATE-TR, etapa R1): a chave, o determinismo por semente no Node, as RNG de politica
// separadas, as mecanicas do DigiLab em tempo (o parry, a interrupcao do preparo, a esquiva, o Guts, o limite, a carta de Cura, a escala)
// e o saldo das acoes que o aprendizado vai ler (R2).
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import {
  CTR_TR, CV, CV21, CV21E, Cd, FORMAS_AD, Rg, T_TR, criarLutaTR, estiloBot, jogarTR, ligarCombateTR, lutadorBot, passoTR, perfilNeutro,
  sementePoliticaTR, type Lutador, type ResultadoLutaTR,
} from "../motor/index.ts";

const lista = (regras: ReturnType<typeof Rg>[], final = "defender", eps = 0): Lutador =>
  ({ nome: "teste", estilo: { nome: "teste", gambits: { regras, final }, eps }, cond: perfilNeutro() });
const resumo = (r: ResultadoLutaTR) => ({ pontosA: r.pontosA, fim: r.fim, passos: r.passos, hp: r.E.L.map(l => l.hp), acoes: r.acoes });

beforeEach(() => ligarCombateTR(true));
afterEach(() => ligarCombateTR(false));

describe("a chave", () => {
  test("desligada, a luta em tempo real falha alto", () => {
    ligarCombateTR(false);
    expect(() => jogarTR(lutadorBot("duelista", CV21E), lutadorBot("tita", CV21E), 1)).toThrow(/COMBATE_TR/);
  });
});

describe("o determinismo", () => {
  test("a mesma semente da a mesma luta, ate o ultimo float, nas 8 formas adultas", () => {
    for (const a of FORMAS_AD) for (const b of FORMAS_AD) {
      const A = lutadorBot(a, CV21E), B = lutadorBot(b, CV21E);
      expect(resumo(jogarTR(A, B, 4242, { R: CV21E }))).toEqual(resumo(jogarTR(A, B, 4242, { R: CV21E })));
    }
  });
  test("a semente muda a luta (o epsilon dos dois lados)", () => {
    const A = lutadorBot("duelista", CV21E), B = lutadorBot("vigia", CV21E);
    const marcas = new Set([101, 202, 303, 404, 505].map(s => JSON.stringify(resumo(jogarTR(A, B, s, { R: CV21E })))));
    expect(marcas.size).toBeGreaterThan(1);
  });
  test("sem epsilon, a semente nao muda nada: so a politica sorteia", () => {
    const A = { ...lutadorBot("espelho", CV21E) }, B = { ...lutadorBot("sentinela", CV21E) };
    A.estilo = { ...A.estilo, eps: 0 }; B.estilo = { ...B.estilo, eps: 0 };
    const r0 = JSON.stringify(resumo(jogarTR(A, B, 101, { R: CV21E })));
    for (const s of [202, 303, 404]) expect(JSON.stringify(resumo(jogarTR(A, B, s, { R: CV21E })))).toBe(r0);
  });
  test("a RNG de politica e uma por lado: o epsilon de um lado nao mexe na sequencia do outro", () => {
    expect(sementePoliticaTR(7, 0)).not.toBe(sementePoliticaTR(7, 1));
    /* o lado A explora igual contra dois rivais que nunca sorteiam e decidem a mesma coisa por motivos diferentes */
    const A = lista([], "carregar", .5);
    const B1 = lista([Rg(Cd("sempre"), "defender")]), B2 = lista([], "defender");
    const a1 = jogarTR(A, B1, 77).acoes.filter(x => x.lado === 0).map(x => [x.nome, x.inicio]);
    const a2 = jogarTR(A, B2, 77).acoes.filter(x => x.lado === 0).map(x => [x.nome, x.inicio]);
    expect(a1).toEqual(a2);
  });
});

describe("as mecanicas", () => {
  test("o golpe rapido contra a defesa: o dano reduzido no alvo e o parry no atacante", () => {
    const A = lista([Rg(Cd("distancia_eh", 0), "golpe_rapido"), Rg(Cd("sempre"), "avancar")]);
    const B = lista([], "defender");
    const r = jogarTR(A, B, 1, { eventos: true });
    const [pa, pb] = [r.E.L[0].p, r.E.L[1].p];
    const golpes = r.acoes.filter(x => x.lado === 0 && x.nome === "golpe_rapido").length;
    expect(golpes).toBeGreaterThan(0);
    const danosB = r.eventos!.filter(e => e.tipo === "dano" && e.lado === 1).map(e => (e as { valor: number }).valor);
    const danosA = r.eventos!.filter(e => e.tipo === "dano" && e.lado === 0).map(e => (e as { valor: number }).valor);
    /* antes da morte subita: 8 x mPerto x 0,3 x mGuarda no alvo e 5 no atacante */
    expect(danosB[0]).toBeCloseTo(CV.dano.golpe_rapido * pa.mPerto * CV.multDef * pb.mGuarda, 12);
    expect(danosA[0]).toBe(CV.parry);
  });
  test("o golpe rapido interrompe o preparo do pesado (e nao sob pele dura)", () => {
    const A = lista([Rg(Cd("distancia_eh", 0), "golpe_rapido"), Rg(Cd("sempre"), "avancar")], "carregar");
    const B = lista([Rg(Cd("distancia_eh", 0), "preparar_pesado")], "carregar");
    const r = jogarTR(A, B, 3, { eventos: true });
    expect(r.eventos!.some(e => e.tipo === "interrompe" && e.lado === 1)).toBe(true);
    const Bp = { ...B, cond: { ...B.cond, tecnica: "pele_dura" as const } };
    Bp.estilo = { ...Bp.estilo, gambits: { regras: [Rg(Cd("distancia_eh", 0), "pele_dura"), Rg(Cd("distancia_eh", 0), "preparar_pesado")], final: "carregar" } };
    /* com a pele dura ativa no preparo, o golpe nao interrompe ate a pele acabar */
    const r2 = jogarTR(A, Bp, 3, { eventos: true });
    const peles = r2.acoes.filter(x => x.lado === 1 && x.nome === "pele_dura").map(x => x.inicio);
    for (const e of r2.eventos!) if (e.tipo === "interrompe") expect(peles.some(p => e.t >= p && e.t < p + CV21.turnosPele * T_TR)).toBe(false);
  });
  test("a esquiva anula o disparo; o golpe rapido acerta quem esquiva", () => {
    const atirador = lista([Rg(Cd("sempre"), "disparo")], "carregar");
    const esquiva = lista([], "carregar");
    esquiva.estilo = { ...esquiva.estilo, gambits: { regras: [Rg(Cd("sempre"), "esquivar")], final: "carregar" } };
    /* Guts sobrando para o atirador disparar e para a esquiva nao parar */
    const cheio = { ...perfilNeutro(), guts0: 1000, gutsMax: 1000, regen: 1000 };
    const r = jogarTR({ ...atirador, cond: cheio }, { ...esquiva, cond: cheio }, 5, { eventos: true });
    expect(r.acoes.filter(x => x.lado === 0 && x.nome === "disparo").length).toBeGreaterThan(3);
    expect(r.eventos!.filter(e => e.tipo === "dano" && e.lado === 1)).toEqual([]);
  });
  test("o Guts volta regen por T, e o custo sai no comeco da acao", () => {
    const A = lista([], "carregar"), B = lista([], "carregar");
    const L = criarLutaTR(A, B, 9), g0 = L.S.L[0].guts;
    passoTR(L);   /* passo 0: decide carregar (custo 0) e regenera 1/T */
    expect(L.S.L[0].guts).toBeCloseTo(g0 + L.S.L[0].regen / T_TR, 12);
    for (let i = 1; i < T_TR; i++) passoTR(L);
    /* no fim do carregar, +25 */
    expect(L.S.L[0].guts).toBeCloseTo(Math.min(L.S.L[0].gutsMax, g0 + L.S.L[0].regen + CV.gutsCarregar), 9);
  });
  test("o limite: 40 T sem KO; o desafiado fica com a luta; sem desafiado, a fracao de vida decide", () => {
    const A = lista([], "defender"), B = lista([], "defender");
    const r = jogarTR(A, B, 1);
    expect(r.fim).toBe("limite"); expect(r.passos).toBe(CTR_TR.limite); expect(r.passos * 16).toBe(80_000); expect(r.pontosA).toBe(.5);
    expect(jogarTR(A, B, 1, { desafiado: 1 }).pontosA).toBe(0);
    expect(jogarTR(A, B, 1, { desafiado: 0 }).pontosA).toBe(1);
  });
  test("a carta de Cura cura uma vez, abaixo do limiar; o comeco com a vida dada (as lutas seguidas)", () => {
    const A = lista([], "defender"), B = lista([Rg(Cd("distancia_eh", 0), "golpe_rapido"), Rg(Cd("sempre"), "avancar")], "carregar");
    const r = jogarTR(A, B, 2, { ini: { hp: 60, guts: 10 }, curas: [{ abaixo: .5, fracao: .3 }, null], eventos: true });
    expect(r.E0.hp[0]).toBe(60); expect(r.E0.guts[0]).toBe(10);
    const curas = r.eventos!.filter(e => e.tipo === "cura");
    expect(curas.length).toBe(1); expect(curas[0]).toMatchObject({ lado: 0 });
    expect(() => jogarTR(A, B, 2, { ini: { hp: 0, guts: 10 } })).toThrow(/começo/);
  });
  test("a escala ligada num lado so falha alto; o oraculo nao luta em tempo real (D-6)", () => {
    const A = lista([], "defender"), B = lista([], "defender");
    expect(() => jogarTR({ ...A, cond: { ...A.cond, escala: 100 } }, B, 1)).toThrow(/escala/);
    expect(() => jogarTR({ ...A, estilo: estiloBot("oraculo") }, B, 1)).toThrow(/oráculo/);
  });
});

describe("o saldo das acoes (o que o aprendizado vai ler)", () => {
  test("a soma dos saldos de um lado e o dano causado menos o recebido, sobre a vida do comeco", () => {
    for (const [a, b] of [["duelista", "muralha"], ["furioso", "emboscador"], ["vigia", "tita"], ["espelho", "sentinela"]]) {
      const r = jogarTR(lutadorBot(a, CV21E), lutadorBot(b, CV21E), 31, { R: CV21E });
      const perda = [0, 1].map(l => r.E0.hp[l] - r.E.L[l].hp);
      for (const l of [0, 1]) {
        const soma = r.acoes.filter(x => x.lado === l).reduce((s, x) => s + x.saldo, 0);
        expect(soma * r.E0.hpMax[l]).toBeCloseTo(perda[1 - l] - perda[l], 6);
      }
    }
  });
  test("cada acao do pet tem o motivo: o indice da regra, a exploracao, o pesado automatico ou a final", () => {
    const r = jogarTR(lutadorBot("tita", CV21E), lutadorBot("furioso", CV21E), 12, { R: CV21E });
    const n = lutadorBot("tita", CV21E).estilo.gambits!.regras.length;
    for (const x of r.acoes) expect(typeof x.motivo === "number" ? x.motivo <= n : ["exploracao", "pesado_automatico"].includes(x.motivo)).toBe(true);
  });
});
