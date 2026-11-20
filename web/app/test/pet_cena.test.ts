// A cena de cada acao do pet e a reacao ao toque (so vista; src/telas/pet/cenaAcao.ts e ToquePet.tsx). Sem DOM (vitest em node).
//   - cada acao do ACOES_PET tem a cena que o motor registrou (o ocioso e o dormir nao inventam gesto novo);
//   - o cocô aparece quando a sujeira do motor SOBE;
//   - a reacao ao toque sai do corpo (solidao, estresse, susto), e o toque e o MESMO evento "d" do botao Carinho;
//   - a vista nao muda a vida: o replay e a assinatura do pet com o toque sao os de um pet com o botao.
import { beforeEach, describe, expect, test } from "vitest";
import { ACOES_PET, Motor } from "../motor/index.ts";
import { S } from "../src/grades.ts";
import { CENA_ACAO, EMOTE_ATLAS, EMOTE_DA_ACAO, EMOTE_GRADE, SEM_GESTO, emoteAgora, esquecerCoco, esquecerReacao, gestoAgora, gestoDaAcao, gestoDaReacao, mostrarReacao,
  reacaoAtual, reacaoDoCorpo, vigiarCoco, type LeituraCorpo } from "../src/telas/pet/cenaAcao.ts";
import { TOQUE, lerCorpo, noSprite } from "../src/telas/pet/ToquePet.tsx";

const C = 450000;
const corpo = (extra: Partial<LeituraCorpo> = {}): LeituraCorpo => ({ solidao: 200000, estresse: 100000, susto: 0, C, medo: 1, ...extra });
beforeEach(() => { esquecerCoco(); esquecerReacao(); });

describe("a cena de cada acao", () => {
  test("toda acao do ACOES_PET esta no mapa dos emotes, e so as de verbo tem emote", () => {
    expect(Object.keys(EMOTE_DA_ACAO).sort()).toEqual([...ACOES_PET].sort());
    expect(EMOTE_DA_ACAO.ocioso).toBeNull();
    expect(EMOTE_DA_ACAO.dormir).toBeNull();
    for (const a of ["comer", "brincar", "chamar_atencao", "explorar", "emburrar"]) expect(EMOTE_DA_ACAO[a], a).toBeTruthy();
  });
  test("todo emote da cena se desenha: no atlas (ou na grade), e sem atlas pela grade", () => {
    const icones = new Set([...Object.values(EMOTE_DA_ACAO), "coracao", "gota"].filter((x): x is string => !!x));
    for (const i of icones) expect(i in EMOTE_ATLAS || i in S, i).toBe(true);
    for (const i of icones) expect(S[EMOTE_GRADE[i] ?? i], "grade de reserva de " + i).toBeTruthy();
  });
  test("cada acao de verbo mexe o corpo de um jeito proprio, e o ocioso e o dormir ficam sem gesto", () => {
    const amostra = (a: string) => Array.from({ length: 400 }, (_, i) => gestoDaAcao(a, i * 17));
    expect(amostra("ocioso").every(g => g === SEM_GESTO)).toBe(true);
    expect(amostra("dormir").every(g => g === SEM_GESTO)).toBe(true);
    expect(Math.max(...amostra("brincar").map(g => g.alto))).toBeGreaterThan(CENA_ACAO.brincarAlto * 0.9);
    expect(Math.max(...amostra("chamar_atencao").map(g => g.alto))).toBeGreaterThan(0);
    expect(Math.min(...amostra("comer").map(g => g.estica))).toBeLessThan(1 - CENA_ACAO.comerEstica * 0.5);
    expect(Math.max(...amostra("explorar").map(g => g.frente))).toBeGreaterThan(1);
    expect(Math.min(...amostra("explorar").map(g => g.frente))).toBeLessThan(-1);
    expect(amostra("emburrar").every(g => g.estica < 1)).toBe(true);
    for (const a of ACOES_PET) for (const g of amostra(a)) { expect(g.alto).toBeGreaterThanOrEqual(0); expect(g.estica).toBeGreaterThan(0); expect(g.estica).toBeLessThanOrEqual(1); }
  });
  test("com o pet andando ou com movimento reduzido, o gesto da acao nao entra", () => {
    const e = { acao: "brincar", sujeira: 0, chave: "1" };
    expect(gestoAgora(e, 280, false, true).alto).toBeGreaterThan(0);
    expect(gestoAgora(e, 280, false, false)).toBe(SEM_GESTO);
    expect(gestoAgora(e, 280, true, true)).toBe(SEM_GESTO);
    /* em Pausa a vida nao anda (como o Seguidor), mas a reacao a uma mao do dono vale */
    expect(gestoAgora(e, 280, false, true, true)).toBe(SEM_GESTO);
    mostrarReacao(reacaoDoCorpo(corpo(), corpo({ solidao: 1 }), 0));
    expect(gestoAgora(e, 280, false, true, true).alto).toBeGreaterThan(0);
  });
  test("o emote da cena e o da acao que o motor registrou; sem verbo, nenhum", () => {
    for (const a of ACOES_PET) expect(emoteAgora({ acao: a, sujeira: 0, chave: "1" }, 0), a).toBe(EMOTE_DA_ACAO[a]);
  });
});

describe("o cocô: a sujeira do motor sobe", () => {
  test("so quando a sujeira sobe do mesmo pet; a primeira olhada, a troca de pet e a limpeza nao contam", () => {
    const e = (sujeira: number, chave = "1") => ({ acao: "ocioso", sujeira, chave });
    expect(emoteAgora(e(2), 0)).toBeNull();                       /* a primeira olhada */
    expect(emoteAgora(e(2), 100)).toBeNull();
    expect(emoteAgora(e(0), 200)).toBeNull();                     /* limpou */
    expect(emoteAgora(e(3, "2"), 300)).toBeNull();                /* outro pet */
    expect(emoteAgora(e(4, "2"), 400)).toBe("gota");              /* subiu */
    expect(gestoAgora(e(4, "2"), 450, false, true).estica).toBe(CENA_ACAO.cocoEstica);
    expect(emoteAgora(e(4, "2"), 400 + CENA_ACAO.cocoMs + 1)).toBeNull();   /* passou */
    vigiarCoco("2", 5, 5000);
    expect(emoteAgora(e(5, "2"), 5001)).toBe("gota");
  });
});

describe("a reacao ao toque sai do corpo", () => {
  test("relaxou: a solidao e o estresse cairam; o carinho e inteiro sem susto e a reacao nao tem recuo", () => {
    const r = reacaoDoCorpo(corpo(), corpo({ solidao: 190000, estresse: 95000 }), 1000);
    expect(r.tipo).toBe("relaxou");
    expect(r.carinho).toBe(1);
    expect(r.medo).toBe(0);
  });
  test("com susto, o medo da mao tira parte do carinho: (C - medo q_susto) / C", () => {
    const r = reacaoDoCorpo(corpo({ susto: C / 3 }), corpo({ solidao: 195000, estresse: 98000, susto: C / 3 }), 0);
    expect(r.carinho).toBeCloseTo(2 / 3, 12);
    expect(r.medo).toBeCloseTo(1 / 3, 12);
    /* sem a sub-chave gestos o medo e 0: o carinho vem inteiro, mesmo com susto */
    expect(reacaoDoCorpo(corpo({ susto: C / 3, medo: 0 }), corpo({ susto: C / 3, medo: 0, solidao: 1 }), 0).carinho).toBe(1);
  });
  test("calmo: nada a aliviar (solidao e estresse ja em zero)", () => {
    expect(reacaoDoCorpo(corpo({ solidao: 0, estresse: 0 }), corpo({ solidao: 0, estresse: 0 }), 0).tipo).toBe("calmo");
  });
  test("falha alto: leitura sem numero ou de escalas diferentes", () => {
    expect(() => reacaoDoCorpo(corpo({ solidao: NaN }), corpo(), 0)).toThrow(/sem solidao/);
    expect(() => reacaoDoCorpo(corpo(), corpo({ C: 1 }), 0)).toThrow(/escalas/);
  });
  test("o gesto e o emote da reacao: pula quando relaxa, recua com medo, e acaba depois de reacaoMs", () => {
    const e = { acao: "explorar", sujeira: 0, chave: "1" };
    mostrarReacao(reacaoDoCorpo(corpo(), corpo({ solidao: 1 }), 1000));
    expect(gestoDaReacao(reacaoAtual(1300)!, 1300).alto).toBeGreaterThan(0);
    expect(gestoDaReacao(reacaoAtual(1300)!, 1300).frente + 0).toBe(0);
    expect(emoteAgora(e, 1300)).toBe("coracao");                                  /* a reacao vale sobre a acao */
    expect(reacaoAtual(1000 + CENA_ACAO.reacaoMs + 1)).toBeNull();
    expect(emoteAgora(e, 1000 + CENA_ACAO.reacaoMs + 1)).toBe("surpreso");
    mostrarReacao(reacaoDoCorpo(corpo({ susto: C / 2 }), corpo({ susto: C / 2, solidao: 1 }), 5000));
    expect(gestoDaReacao(reacaoAtual(5250)!, 5250).frente).toBeLessThan(0);
    expect(emoteAgora({ ...e, acao: "ocioso" }, 5250)).toBe("gota");
    expect(gestoAgora(e, 5250, true, true)).toBe(SEM_GESTO);                      /* movimento reduzido */
  });
});

describe("o toque e o carinho do botao", () => {
  test("lerCorpo le o corpo do pet v17 e a reacao do toque bate com o que o motor fez no `acariciar`", () => {
    const m = new Motor(777);
    m.avancar(600);
    const antes = lerCorpo(m);
    expect(antes.C).toBe(C);
    m.observar("acariciar");
    const depois = lerCorpo(m), r = reacaoDoCorpo(antes, depois, 0);
    expect(depois.solidao + depois.estresse).toBeLessThanOrEqual(antes.solidao + antes.estresse);
    expect(r.tipo).toBe(depois.solidao + depois.estresse < antes.solidao + antes.estresse ? "relaxou" : "calmo");
    expect(r.carinho + r.medo).toBeCloseTo(1, 12);
  });
  test("o toque grava o mesmo evento do botao: dois pets ficam com a mesma assinatura e o mesmo registro", () => {
    const botao = new Motor(4242), toque = new Motor(4242);
    for (const m of [botao, toque]) m.avancar(300);
    botao.observar("acariciar");
    lerCorpo(toque); toque.observar("acariciar"); lerCorpo(toque);          /* o toque le o corpo antes e depois, sem escrever nele */
    for (const m of [botao, toque]) m.avancar(300);
    expect(toque.assinatura()).toBe(botao.assinatura());
    expect(JSON.stringify(toque.log)).toBe(JSON.stringify(botao.log));
    expect(toque.log.filter(ev => ev[1] === "d").map(ev => ev[2])).toEqual(["acariciar"]);
  });
  test("o toque cai no sprite com a folga do dedo, e fora dele nao", () => {
    const cena = { left: 100, top: 50 }, ret = { x: 200, y: 120, w: 60, h: 80 };
    expect(noSprite(100 + 230, 50 + 160, cena, ret)).toBe(true);
    expect(noSprite(100 + 200 - TOQUE.folga, 50 + 120, cena, ret)).toBe(true);
    expect(noSprite(100 + 200 - TOQUE.folga - 1, 50 + 120, cena, ret)).toBe(false);
    expect(noSprite(100 + 230, 50 + 160, cena, null)).toBe(false);
  });
});
