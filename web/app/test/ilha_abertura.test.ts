/* A camera do primeiro dia (src/telas/pet/ilha/aberturaConta.ts e src/abertura.ts; a prancha em docs/pranchas/ux-ilha-abertura/, AB-1 a AB-5
   APROVADAS). O caminho inteiro na tela fica no e2e (e2e/abertura.spec.ts). */
import { afterEach, describe, expect, it, vi } from "vitest";
import { ABERTURAS, duracao, inclinar, propostaDe, quadroDaAbertura, quadroDaSaida, type Par, type Ponto } from "../src/telas/pet/ilha/aberturaConta.ts";
import { CHAVE_ABERTURA, PROPOSTA_ESCOLHIDA, aberturaPendente, marcarAberturaTocada, pedirAbertura } from "../src/abertura.ts";

const PONTOS: Record<Ponto, Par> = { pet: [10, 14], ninho: [9, 14], praca: [31, 16], portao: [31, 3], barraca: [45, 12], meio: [20.5, 15] };

describe("a camera do primeiro dia (prototipo)", () => {
  it("o parametro: sem ele nada, a|b|c, outro valor falha alto", () => {
    expect(propostaDe(null)).toBeNull();
    for (const p of ["a", "b", "c"] as const) expect(propostaDe(p)).toBe(p);
    expect(() => propostaDe("d")).toThrow(/a, b e c/);
  });
  it("toda proposta comeca no tempo 0, anda para a frente e acaba no pet, no zoom e na inclinacao de sempre", () => {
    for (const p of ["a", "b", "c"] as const) {
      const qs = ABERTURAS[p];
      expect(qs[0].t).toBe(0);
      for (let i = 1; i < qs.length; i++) expect(qs[i].t).toBeGreaterThan(qs[i - 1].t);
      const fim = qs[qs.length - 1];
      expect([fim.em, fim.zoom, fim.inclina]).toEqual(["pet", 1, 0]);
      const q = quadroDaAbertura(p, duracao(p), PONTOS);
      expect(q).toEqual({ foco: PONTOS.pet, zoom: 1, inclina: 0, acabou: true });
    }
  });
  it("entre os quadros-chave o caminho e continuo, e nos quadros-chave passa exatamente neles", () => {
    for (const p of ["a", "b", "c"] as const) {
      for (const k of ABERTURAS[p].slice(0, -1)) {
        const q = quadroDaAbertura(p, k.t, PONTOS);
        expect(q.foco).toEqual(PONTOS[k.em]); expect(q.zoom).toBeCloseTo(k.zoom, 12);
      }
      let ant = quadroDaAbertura(p, 0, PONTOS);
      for (let t = 10; t < duracao(p); t += 10) {
        const q = quadroDaAbertura(p, t, PONTOS);
        expect(Math.hypot(q.foco[0] - ant.foco[0], q.foco[1] - ant.foco[1])).toBeLessThan(0.5);
        expect(Math.abs(q.zoom - ant.zoom)).toBeLessThan(0.02);
        ant = q;
      }
    }
  });
  it("um tempo invalido falha alto", () => {
    expect(() => quadroDaAbertura("a", -1, PONTOS)).toThrow();
    expect(() => quadroDaAbertura("a", Number.NaN, PONTOS)).toThrow();
  });
  it("inclinar mantem a distancia e o lado, e sobe a camera", () => {
    const d: [number, number, number] = [0, 6, 8], r = Math.hypot(...d), n = inclinar(d, 0.3);
    expect(Math.hypot(...n)).toBeCloseTo(r, 9);
    expect(n[0]).toBeCloseTo(0, 12); expect(n[2]).toBeGreaterThan(0);
    expect(n[1]).toBeGreaterThan(d[1]);
    inclinar(d, 0).forEach((v, i) => expect(v).toBeCloseTo(d[i], 12));
  });
});

describe("a saida pelo toque (AB-3)", () => {
  const de = { foco: [20, 15] as Par, zoom: 1.9, inclina: 0.3, acabou: false };
  it("comeca no quadro em que parou e chega a camera de sempre, sem inclinacao, no fim", () => {
    expect(quadroDaSaida(de, 0, [10, 14], 1, 400)).toEqual(de);
    const meio = quadroDaSaida(de, 200, [10, 14], 1, 400);
    expect(meio.acabou).toBe(false);
    expect(meio.zoom).toBeCloseTo(1.45, 9);
    expect(meio.inclina).toBeCloseTo(0.15, 9);
    expect(quadroDaSaida(de, 400, [10, 14], 1, 400)).toEqual({ foco: [10, 14], zoom: 1, inclina: 0, acabou: true });
  });
  it("tempo ou duracao invalidos falham alto", () => {
    expect(() => quadroDaSaida(de, -1, [0, 0], 1, 400)).toThrow(/tempo invalido/);
    expect(() => quadroDaSaida(de, 0, [0, 0], 1, 0)).toThrow(/duracao invalida/);
  });
});

describe("o pedido da abertura (AB-2: uma vez por pet)", () => {
  afterEach(() => { vi.unstubAllGlobals(); });
  const guardar = () => {
    const g: Record<string, string> = {};
    vi.stubGlobal("localStorage", { getItem: (k: string) => g[k] ?? null, setItem: (k: string, v: string) => { g[k] = v; } });
    return g;
  };
  it("a proposta escolhida e a B (AB-1)", () => { expect(PROPOSTA_ESCOLHIDA).toBe("b"); });
  it("o ovo que choca pede; tocada, nao volta; outro pet nao herda o pedido", () => {
    const g = guardar();
    expect(aberturaPendente(7)).toBe(false);
    pedirAbertura(7);
    expect(aberturaPendente(7)).toBe(true);
    expect(aberturaPendente(8)).toBe(false);
    marcarAberturaTocada(7);
    expect(aberturaPendente(7)).toBe(false);
    expect(JSON.parse(g[CHAVE_ABERTURA])).toEqual({ semente: 7, tocada: true });
    pedirAbertura(8);
    expect(aberturaPendente(8)).toBe(true);
  });
  it("sem localStorage, ou com a chave estragada, nao toca", () => {
    const g = guardar();
    g[CHAVE_ABERTURA] = "{nao e json";
    expect(aberturaPendente(7)).toBe(false);
    g[CHAVE_ABERTURA] = JSON.stringify({ semente: "7", tocada: false });
    expect(aberturaPendente(7)).toBe(false);
    vi.stubGlobal("localStorage", { getItem: () => { throw new Error("bloqueado"); }, setItem: () => { throw new Error("bloqueado"); } });
    expect(() => pedirAbertura(7)).not.toThrow();
    expect(aberturaPendente(7)).toBe(false);
  });
});
