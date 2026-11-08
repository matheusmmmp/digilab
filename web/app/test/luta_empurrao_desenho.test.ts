// O desenho do empurrao (docs/TAREFA_V3_LUTA_EMPURRAO.md, etapa 5): so vista, a partir do estado e dos eventos do motor. Confere que o
// tranco so visual da E1 nao soma ao empurrao do motor, que a queda usa o Stun desde o passo em que caiu, que o arco da queda e a poeira
// sao os mesmos para o mesmo passo e que desenhar nao muda a luta v18.
import { describe, expect, test } from "vitest";
import { CV21E_TR18, criarLutaTR, lutadorBot, passoTR, perfilNeutro, Cd, Rg, type Lutador } from "../motor/index.ts";
import { clipeDoLado } from "../src/telas/lutar/palcoTR/desenhoTR.ts";
import { aplicarEventosTR, empurraoDoPasso, poeiraDoPasso, puloDaQueda, visualNovoTR, MOVIMENTO } from "../src/telas/lutar/palcoTR/efeitosTR.ts";

const R = CV21E_TR18;
const cheio = () => ({ ...perfilNeutro(), guts0: 1000, gutsMax: 1000, regen: 1000 });
const lista = (regras: ReturnType<typeof Rg>[], final = "carregar"): Lutador =>
  ({ nome: "teste", estilo: { nome: "teste", gambits: { regras, final }, eps: 0 }, cond: cheio() });
const pesado = () => lista([Rg(Cd("distancia_eh", 0), "preparar_pesado"), Rg(Cd("sempre"), "avancar")]);

describe("o desenho do empurrao", () => {
  test("o acerto que o motor empurrou nao ganha o tranco so visual da E1; o golpe rapido continua com ele", () => {
    /* os trancos de cada acerto, dois passos depois dele: [empurrado pelo motor, tranco visual] */
    const trancos = (A: Lutador): [boolean, number][] => {
      const Lt = criarLutaTR(A, lista([], "carregar"), 1, { R, eventos: true }), v = visualNovoTR(), out: [boolean, number][] = [];
      let lidos = 0;
      while (!passoTR(Lt)) {
        aplicarEventosTR(v, Lt, Lt.eventos!.slice(lidos)); lidos = Lt.eventos!.length;
        for (const i of v.impactos) if (Lt.S.passo === i.t0 + 2) out.push([!!i.motor, empurraoDoPasso(v, i.t0 + 2, i.lado)]);
      }
      return out;
    };
    const doPesado = trancos(pesado()), doRapido = trancos(lista([Rg(Cd("distancia_eh", 0), "golpe_rapido"), Rg(Cd("sempre"), "avancar")]));
    expect(doPesado.length).toBeGreaterThan(0);
    for (const [motor, tranco] of doPesado) { expect(motor).toBe(true); expect(tranco).toBe(0); }
    expect(doRapido.length).toBeGreaterThan(0);
    for (const [motor, tranco] of doRapido) { expect(motor).toBe(false); expect(tranco).toBeGreaterThan(0); }
  });
  test("a queda: o Stun desde o passo em que caiu, ate levantar", () => {
    const Lt = criarLutaTR(pesado(), lista([], "carregar"), 1, { R, eventos: true }), S = Lt.S;
    while (S.L[1].quedaDe < 0) passoTR(Lt);
    const t0 = S.L[1].quedaDe;
    expect(clipeDoLado(S.L[1], t0, null)).toEqual({ clipe: "Stun", t: 0 });
    expect(clipeDoLado(S.L[1], t0 + 10, null)).toEqual({ clipe: "Stun", t: 160 });
    expect(clipeDoLado(S.L[1], S.L[1].atordoadoAte, null).clipe).not.toBe("Stun");
  });
  test("o arco da queda sobe e volta ao chao no fim do deslize; fora dela, 0", () => {
    expect(puloDaQueda(100, -1, 111)).toBe(0);
    expect(puloDaQueda(100, 100, 111)).toBe(0);
    expect(puloDaQueda(105, 100, 110)).toBe(MOVIMENTO.pulo);
    expect(puloDaQueda(110, 100, 110)).toBe(0); expect(puloDaQueda(99, 100, 110)).toBe(0);
  });
  test("a poeira e a mesma para a mesma idade, em pixels inteiros, e some antes do comeco", () => {
    for (let k = 0; k < 20; k++) expect(poeiraDoPasso(k)).toEqual(poeiraDoPasso(k));
    expect(poeiraDoPasso(-1)).toEqual([]);
    for (const p of poeiraDoPasso(5)) { expect(Number.isInteger(p.dx) && Number.isInteger(p.dy) && Number.isInteger(p.tam)).toBe(true); expect(p.tam).toBeGreaterThan(0); }
  });
  test("desenhar nao muda a luta v18: com e sem os efeitos, o mesmo estado", () => {
    const A = lutadorBot("tita", R), B = lutadorBot("duelista", R);
    const sem = criarLutaTR(A, B, 303, { R, eventos: true }), com = criarLutaTR(A, B, 303, { R, eventos: true }), v = visualNovoTR();
    let lidos = 0;
    for (;;) {
      const f1 = passoTR(sem), f2 = passoTR(com);
      aplicarEventosTR(v, com, com.eventos!.slice(lidos)); lidos = com.eventos!.length;
      expect(com.S.L.map(l => [l.x, l.hp, l.atordoadoAte])).toEqual(sem.S.L.map(l => [l.x, l.hp, l.atordoadoAte]));
      if (f1 || f2) { expect(f2).toEqual(f1); break; }
    }
    expect(com.eventos!.some(e => e.tipo === "empurrao")).toBe(true);
  });
});
