// A vista da bola do dono (docs/TAREFA_V3_BOLA_BRINCAR.md, BB-9; a etapa BB3): o arco do lance (src/telas/pet/ilha/arcoBola.ts) e a vigia do
// lance, do chute e da recusa (src/telas/pet/momentos.ts, vigiarBola). So vista, sem DOM: o motor ja decidiu, e nada daqui volta a ele.
import { afterEach, beforeEach, expect, test } from "vitest";
import { ARCO_BOLA, CHUTE_BOLA, bateEm, novoArco, origemDoArco, passoDoChute, pontoDoArco, pontoDoChute, type ChuteBola } from "../src/telas/pet/ilha/arcoBola.ts";
import { MOMENTOS, chuteNaJanela, bolaVista, esquecerMomentos, vigiarBola, type EntradaBola } from "../src/telas/pet/momentos.ts";
import { escolherReacao, esquecerReacaoRosto } from "../src/telas/pet/reacao.ts";
import { ouvirSom, type InstanteSom } from "../src/somEventos.ts";

let sons: InstanteSom[] = [];
let largar: () => void = () => {};
beforeEach(() => { esquecerMomentos(); esquecerReacaoRosto(); sons = []; largar = ouvirSom(i => sons.push(i)); });
afterEach(() => largar());

const BASE: EntradaBola = { chave: "p", lances: [], rolagens: [], tickMundo: 100, janela: 30, energia: 0.8, dormindo: false, convidado: true };
const em = (o: Partial<EntradaBola> = {}): EntradaBola => ({ ...BASE, ...o });
const efeitos = () => sons.flatMap(s => (s.tipo === "efeito" ? [s.efeito] : s.tipo === "voz" ? ["voz:" + s.humor] : []));
const rosto = (t: number) => escolherReacao({ chave: "p", humor: 0.7, energia: 0.8, saude: 1, lesionado: false, dormindo: false }, t)?.reacao ?? null;
const LANCE = { tick: 100, para: [40, 60] as const };

test("o arco sai do lado da camera, a `recuo` celulas do ponto do lance", () => {
  expect(origemDoArco([10, 10], [10, 30])).toEqual([10, 10 + ARCO_BOLA.recuo]);
  const [x, z] = origemDoArco([0, 0], [30, 40]);
  expect(Math.hypot(x, z)).toBeCloseTo(ARCO_BOLA.recuo, 12);
  expect(x / z).toBeCloseTo(30 / 40, 12);
  /* a camera mais perto que o recuo: sai do chao sob ela */
  expect(origemDoArco([0, 0], [1, 2])).toEqual([1, 2]);
  expect(() => origemDoArco([0, NaN], [1, 2])).toThrow();
  expect(() => origemDoArco([0, 0], [1, 2], -1)).toThrow();
});

test("o arco comeca na mao, sobe acima da reta e cai no chao no ponto do lance", () => {
  const a = novoArco(1000, [10, 10], [10, 30]);
  expect(a.de).toEqual([10, 15]);
  const p0 = pontoDoArco(a, 1000), meio = pontoDoArco(a, 1000 + a.ms / 2), fim = pontoDoArco(a, 1000 + a.ms);
  expect(p0).toEqual({ x: 10, z: 15, y: ARCO_BOLA.alturaMao, acabou: false });
  expect(meio.y).toBeCloseTo(ARCO_BOLA.alturaMao / 2 + ARCO_BOLA.altura, 12);
  expect(meio.y).toBeGreaterThan(p0.y);
  expect(meio.z).toBeCloseTo(12.5, 12);
  expect(fim).toEqual({ x: 10, z: 10, y: 0, acabou: true });
  /* antes de comecar, na mao; depois do fim, parada no chao */
  expect(pontoDoArco(a, 900).y).toBe(ARCO_BOLA.alturaMao);
  expect(pontoDoArco(a, 99999)).toEqual(fim);
  expect(() => novoArco(0, [0, 0], [1, 1], 0)).toThrow();
});

test("o chute vale na janela do convite: do tick do lance ate antes de tick + janela", () => {
  expect(chuteNaJanela(100, 100, 30)).toBe(true);
  expect(chuteNaJanela(100, 129, 30)).toBe(true);
  expect(chuteNaJanela(100, 130, 30)).toBe(false);
  expect(chuteNaJanela(100, 99, 30)).toBe(false);
});

test("a primeira olhada e a troca de pet nao contam", () => {
  expect(vigiarBola(em({ lances: [LANCE], rolagens: [101] }), 0)).toEqual({ lance: null, chutou: false, recusa: null });
  expect(vigiarBola(em({ chave: "q", lances: [LANCE, LANCE], rolagens: [101, 102] }), 10)).toEqual({ lance: null, chutou: false, recusa: null });
  expect(efeitos()).toEqual([]);
  expect(bolaVista()).toEqual({ lances: 0, chutes: 0, recusas: 0 });
});

test("o lance e o chute na janela: o som do lance, a batida e a voz contente, sem recusa", () => {
  vigiarBola(em(), 0);
  const s1 = vigiarBola(em({ lances: [LANCE] }), 10);
  expect(s1.lance).toEqual(LANCE);
  expect(efeitos()).toEqual(["cuidado_toque"]);
  const s2 = vigiarBola(em({ lances: [LANCE], rolagens: [104], tickMundo: 104 }), 20);
  expect(s2).toEqual({ lance: null, chutou: true, recusa: null });
  expect(efeitos()).toEqual(["cuidado_toque", "treino_alvo", "voz:contente"]);
  expect(vigiarBola(em({ lances: [LANCE], rolagens: [104], tickMundo: 200 }), 30).recusa).toBeNull();
  expect(bolaVista()).toEqual({ lances: 1, chutes: 1, recusas: 0 });
  /* idempotente no mesmo estado */
  expect(vigiarBola(em({ lances: [LANCE], rolagens: [104], tickMundo: 200 }), 40)).toEqual({ lance: null, chutou: false, recusa: null });
});

test("a janela passa sem chute: o rosto da recusa por recusaBolaMs, com o resmungo", () => {
  vigiarBola(em(), 0);
  vigiarBola(em({ lances: [LANCE] }), 10);
  expect(vigiarBola(em({ lances: [LANCE], tickMundo: 129 }), 20).recusa).toBeNull();
  expect(vigiarBola(em({ lances: [LANCE], tickMundo: 130 }), 1000).recusa).toBe("Recusa");
  expect(rosto(1000)).toBe("Recusa");
  expect(rosto(1000 + MOMENTOS.recusaBolaMs)).toBeNull();
  expect(efeitos()).toEqual(["cuidado_toque", "voz:resmungo"]);
  /* uma vez so */
  expect(vigiarBola(em({ lances: [LANCE], tickMundo: 200 }), 1100).recusa).toBeNull();
  expect(bolaVista()).toEqual({ lances: 1, chutes: 0, recusas: 1 });
});

test("um chute fora da janela nao desfaz a recusa; a energia baixa mostra Cansado com o bocejo", () => {
  vigiarBola(em({ energia: 0.1 }), 0);
  vigiarBola(em({ energia: 0.1, lances: [LANCE] }), 10);
  const s = vigiarBola(em({ energia: 0.1, lances: [LANCE], rolagens: [140], tickMundo: 140 }), 500);
  expect(s.chutou).toBe(true);
  expect(s.recusa).toBe("Cansado");
  expect(efeitos()).toContain("voz:bocejo");
});

test("sem convite (o cerebro A, BB-6) ou dormindo (o reflexo do sono), nenhuma recusa no rosto", () => {
  vigiarBola(em({ convidado: false }), 0);
  vigiarBola(em({ convidado: false, lances: [LANCE] }), 10);
  expect(vigiarBola(em({ convidado: false, lances: [LANCE], tickMundo: 300 }), 20).recusa).toBeNull();
  esquecerMomentos();
  vigiarBola(em({ dormindo: true }), 0);
  vigiarBola(em({ dormindo: true, lances: [LANCE] }), 10);
  expect(vigiarBola(em({ dormindo: true, lances: [LANCE], tickMundo: 300 }), 20).recusa).toBeNull();
  expect(rosto(20)).toBeNull();
});

test("o pet de antes da v30 (sem o lance) so tem o chute; a entrada invalida falha alto", () => {
  vigiarBola(em({ lances: null }), 0);
  expect(vigiarBola(em({ lances: null, rolagens: [101] }), 10)).toEqual({ lance: null, chutou: true, recusa: null });
  expect(() => vigiarBola(em({ janela: 0 }), 0)).toThrow();
  expect(() => vigiarBola(em({ energia: NaN }), 0)).toThrow();
});

test("o chute: o pet para encostado na bola, do lado de onde vem; ja perto, fica", () => {
  expect(pontoDoChute([0, 0], [3, 4])).toEqual([0.6 * CHUTE_BOLA.encosto, 0.8 * CHUTE_BOLA.encosto].map(v => v) as [number, number]);
  expect(pontoDoChute([0, 0], [0.3, 0])).toEqual([0.3, 0]);
});

test("o chute: corre ate a bola, da o golpe nela, volta ao motor; a bola so rola quando o braco chega", () => {
  const c: ChuteBola = { desde: 1000, bola: [10, 10], partida: [10, 13], alvo: [10, 6], golpeMs: 450 };
  const motor: [number, number] = [10, 11], ponto = pontoDoChute(c.bola, c.partida);
  const { corridaMs, voltaMs } = CHUTE_BOLA;
  expect(passoDoChute(c, 1000, motor, false)).toEqual({ cel: [10, 13], golpe: null, andando: true, acabou: false });
  expect(passoDoChute(c, 1000 + corridaMs, motor, false)).toEqual({ cel: ponto, golpe: { desde: 1000 + corridaMs, alvo: [10, 6] }, andando: false, acabou: false });
  const volta = passoDoChute(c, 1000 + corridaMs + 450 + voltaMs / 2, motor, false);
  expect([volta.golpe, volta.andando, volta.acabou]).toEqual([null, true, false]);
  expect(passoDoChute(c, 1000 + corridaMs + 450 + voltaMs, motor, false)).toEqual({ cel: motor, golpe: null, andando: false, acabou: true });
  expect(bateEm(c, false)).toBe(1000 + corridaMs + 450 * CHUTE_BOLA.bateFracao);
  /* movimento reduzido: so o golpe, no lugar do motor, e a bola sai logo */
  expect(passoDoChute(c, 1100, motor, true)).toEqual({ cel: motor, golpe: { desde: 1000, alvo: [10, 6] }, andando: false, acabou: false });
  expect(passoDoChute(c, 1450, motor, true).acabou).toBe(true);
  expect(bateEm(c, true)).toBe(1000 + 450 * CHUTE_BOLA.bateFracao);
});
