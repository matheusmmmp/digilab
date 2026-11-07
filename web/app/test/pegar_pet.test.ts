// Pegar o pet (docs/TAREFA_V3_PEGAR_PET.md, P2): o gesto na tela (PegarPet.tsx com o ToquePet.tsx no mesmo alvo) e as contas do pet na mao
// (ilha/mao.ts). Sem DOM (vitest em node): o alvo e um EventTarget com o retangulo, e a vista do mundo e uma falsa, que poe o chao no
// ponto do cliente (1 px = 1 subunidade). O jogo e o do app (iniciarJogo), com um pet v19 no save.
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import { Motor, VERSAO_V19 } from "../motor/index.ts";
import { CHAVE, textoSave, type Armazenamento } from "../src/save.ts";
import { iniciarJogo, jogoAtual } from "../src/jogo.ts";
import { CENA } from "../src/telas/pet/cenaEstado.ts";
import { arrastoPega, ligarPegarPet, podePegar } from "../src/telas/pet/PegarPet.tsx";
import { LIMIAR_ARRASTO } from "../src/telas/pet/PorRacao.tsx";
import { ligarToquePet } from "../src/telas/pet/ToquePet.tsx";
import { MAO, Pendulo, alturaDepoisDeSoltar, soltarAcabou, tremorAgora } from "../src/telas/pet/ilha/mao.ts";

const armaz = (dados: Record<string, string> = {}): Armazenamento => ({ getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } });

/** um pet v19 acordado (ou dormindo) no mundo */
function petV19(dormindo: boolean): Motor {
  const m = new Motor(4242, VERSAO_V19);
  m.avancar(120);
  for (let i = 0; i < 2000 && m.e.dormindo !== dormindo; i++) m.avancar(5);
  if (m.e.dormindo !== dormindo) throw new Error("o teste nao achou o pet " + (dormindo ? "dormindo" : "acordado"));
  return m;
}

/** a cena falsa: o sprite do pet em (100..140, 100..160) da cena, que comeca em (0, 0); o pe dele em (120, 160) */
function cenaFalsa(): void {
  CENA.ret = { x: 100, y: 100, w: 40, h: 60 };
  CENA.mundo = {
    paraMundo: (x, y) => [Math.round(x), Math.round(y)],
    paraTela: () => [120, 160],
    get pet() { const p = jogoAtual().motor.mundo!.pet; return [p[0], p[1]] as [number, number]; },
    pousoEm: (x, y) => (y < 0 ? null : [Math.round(x), Math.round(y)]),
  };
}
const alvo = () => Object.assign(new EventTarget(), { getBoundingClientRect: () => ({ left: 0, top: 0 }), setPointerCapture: () => {} });
const ev = (tipo: string, x: number, y: number, id = 1) =>
  Object.assign(new Event(tipo, { cancelable: true }), { pointerId: id, clientX: x, clientY: y, button: 0, pointerType: "mouse" });

let desligar: (() => void)[] = [];
/** liga o toque e o gesto no alvo, nessa ordem (a do Habitat.tsx) */
function ligar() {
  const el = alvo();
  desligar = [ligarToquePet(el), ligarPegarPet(el)];
  return el;
}
const eventos = (tipo: string) => jogoAtual().motor.log.filter(e => e[1] === tipo);

beforeEach(() => { CENA.coberto = false; CENA.bolaNaMao = false; CENA.petNaMao = false; CENA.maoPet = null; });
afterEach(() => { for (const d of desligar) d(); desligar = []; CENA.ret = null; CENA.mundo = null; });

describe("o gesto de pegar o pet", () => {
  test("o arrasto de mais de 6 px a partir do pet o pega, e soltar grava o levar pet no ponto do chao", () => {
    iniciarJogo(armaz({ [CHAVE]: textoSave(petV19(false)) }));
    cenaFalsa();
    const el = ligar(), d0 = eventos("d").length;
    el.dispatchEvent(ev("pointerdown", 120, 130));
    el.dispatchEvent(ev("pointermove", 120 + LIMIAR_ARRASTO, 130));
    expect(CENA.petNaMao, "6 px ainda nao pega (PP-5: mais de 6)").toBe(false);
    el.dispatchEvent(ev("pointermove", 128, 133));
    expect(CENA.petNaMao).toBe(true);
    /* o pe fica a mesma distancia do ponteiro de quando ele foi pego (o pe em (120, 160), o ponteiro em (120, 130)) */
    expect(CENA.maoPet).toEqual({ x: 128, y: 163 });
    el.dispatchEvent(ev("pointermove", 150, 140));
    el.dispatchEvent(ev("pointerup", 150, 140));
    expect(CENA.petNaMao).toBe(false);
    expect(CENA.maoPet).toBeNull();
    const lp = eventos("lp");
    expect(lp).toHaveLength(1);
    expect(lp[0][2]).toEqual({ x: 150, y: 170 });
    expect(eventos("d").length, "o arrasto nao vira carinho").toBe(d0);
  });

  test("um arrasto curto (entre 6 e 10 px) pega o pet e nao vira carinho, mesmo dentro da folga do toque", () => {
    iniciarJogo(armaz({ [CHAVE]: textoSave(petV19(false)) }));
    cenaFalsa();
    const el = ligar(), d0 = eventos("d").length;
    el.dispatchEvent(ev("pointerdown", 120, 130));
    el.dispatchEvent(ev("pointermove", 128, 130));
    el.dispatchEvent(ev("pointerup", 128, 130));
    expect(eventos("d").length).toBe(d0);
    expect(eventos("lp")).toHaveLength(1);
  });

  test("o toque curto no pet continua sendo carinho e nao pega o pet", () => {
    iniciarJogo(armaz({ [CHAVE]: textoSave(petV19(false)) }));
    cenaFalsa();
    const el = ligar(), d0 = eventos("d").length;
    el.dispatchEvent(ev("pointerdown", 120, 130));
    el.dispatchEvent(ev("pointermove", 122, 131));
    expect(CENA.petNaMao).toBe(false);
    el.dispatchEvent(ev("pointerup", 122, 131));
    expect(eventos("d").map(e => e[2]).slice(d0)).toEqual(["acariciar"]);
    expect(eventos("lp")).toHaveLength(0);
  });

  test("o pet dormindo nao e pego (PP-2): o arrasto nao comeca e nada se grava", () => {
    iniciarJogo(armaz({ [CHAVE]: textoSave(petV19(true)) }));
    cenaFalsa();
    const el = ligar(), log0 = jogoAtual().motor.log.length;
    el.dispatchEvent(ev("pointerdown", 120, 130));
    el.dispatchEvent(ev("pointermove", 160, 150));
    expect(CENA.petNaMao).toBe(false);
    el.dispatchEvent(ev("pointerup", 160, 150));
    expect(eventos("lp")).toHaveLength(0);
    expect(jogoAtual().motor.log.length).toBe(log0);
  });

  test("fora do sprite, com painel por cima ou com a bola na mao, o arrasto nao pega o pet", () => {
    iniciarJogo(armaz({ [CHAVE]: textoSave(petV19(false)) }));
    cenaFalsa();
    const el = ligar();
    const arrastar = (x: number, y: number) => {
      el.dispatchEvent(ev("pointerdown", x, y)); el.dispatchEvent(ev("pointermove", x + 30, y + 10));
      const pegou = CENA.petNaMao; el.dispatchEvent(ev("pointerup", x + 30, y + 10)); return pegou;
    };
    expect(arrastar(20, 20)).toBe(false);
    CENA.coberto = true; expect(arrastar(120, 130)).toBe(false); CENA.coberto = false;
    CENA.bolaNaMao = true; expect(arrastar(120, 130)).toBe(false); CENA.bolaNaMao = false;
    expect(eventos("lp")).toHaveLength(0);
    expect(arrastar(120, 130)).toBe(true);
    expect(eventos("lp")).toHaveLength(1);
  });

  test("o pointercancel larga o pet sem gravar; fora do chao vale o ultimo ponto do chao", () => {
    iniciarJogo(armaz({ [CHAVE]: textoSave(petV19(false)) }));
    cenaFalsa();
    const el = ligar();
    el.dispatchEvent(ev("pointerdown", 120, 130)); el.dispatchEvent(ev("pointermove", 140, 130));
    el.dispatchEvent(new Event("pointercancel"));
    expect(CENA.petNaMao).toBe(false);
    expect(eventos("lp")).toHaveLength(0);
    /* o pe passa por (130, 150) no chao e o dedo sobe ao "ceu" da cena falsa (y < 0): cai no ultimo ponto do chao */
    el.dispatchEvent(ev("pointerdown", 120, 130)); el.dispatchEvent(ev("pointermove", 130, 120));
    el.dispatchEvent(ev("pointermove", 130, -100)); el.dispatchEvent(ev("pointerup", 130, -100));
    expect(eventos("lp").map(e => e[2])).toEqual([{ x: 130, y: 150 }]);
  });

  test("podePegar: so v19 em diante, vivo, fora do ovo, acordado, sem painel, sem bola e com a ilha (pousoEm)", () => {
    const m = petV19(false), ok = { coberto: false, bolaNaMao: false, pousoEm: true };
    expect(podePegar(m, 0, ok)).toBe(true);
    expect(podePegar(m, 1, ok)).toBe(false);
    expect(podePegar(m, 0, { ...ok, coberto: true })).toBe(false);
    expect(podePegar(m, 0, { ...ok, bolaNaMao: true })).toBe(false);
    expect(podePegar(m, 0, { ...ok, pousoEm: false }), "a reserva do mundo nao pega").toBe(false);
    expect(podePegar(petV19(true), 0, ok)).toBe(false);
    const v18 = new Motor(4242, 18); v18.avancar(120);
    expect(podePegar(v18, 0, ok)).toBe(false);
    expect(arrastoPega(LIMIAR_ARRASTO, 0)).toBe(false);
    expect(arrastoPega(LIMIAR_ARRASTO + 0.5, 0)).toBe(true);
  });

  test("PP-1: pegar e soltar so muda a posicao (o resto da assinatura do motor fica igual)", () => {
    const m = petV19(false), antes = m.assinatura(), estado = JSON.stringify(m.e);
    m.levarPet(10, 10);
    expect(JSON.stringify(m.e)).toBe(estado);
    expect(m.assinatura()).not.toBe(antes);
  });
});

describe("o pet na mao: o pendulo, o tremor, a queda e o quique", () => {
  test("o pendulo balanca dentro de um limite, fica para tras do lado em que a mao anda e para com movimento reduzido", () => {
    const p = new Pendulo();
    let max = 0;
    for (let t = 0; t <= 5000; t += 16) max = Math.max(max, Math.abs(p.passo(16, 200, t, false)));
    expect(max).toBeGreaterThan(MAO.amplitude * 0.5);
    expect(max).toBeLessThan(MAO.amplitude * 2.5);
    /* a mao anda para a direita: o pe fica para tras (angulo negativo) em media */
    const q = new Pendulo();
    let soma = 0, n = 0;
    for (let t = 0; t <= 600; t += 16) { soma += q.passo(16, t * 0.4, t, false); n++; }
    expect(soma / n).toBeLessThan(0);
    const r = new Pendulo();
    for (let t = 0; t <= 1000; t += 16) expect(r.passo(16, t, t, true)).toBe(0);
    expect(() => r.passo(16, NaN, 0, false)).toThrow();
  });
  test("o tremor e de 1 texel e some com movimento reduzido", () => {
    const vistos = new Set<number>();
    for (let t = 0; t < 1000; t += 10) vistos.add(tremorAgora(t, false));
    expect([...vistos].sort()).toEqual([-1, 0, 1].map(v => v * MAO.tremorTexels).sort());
    expect(tremorAgora(123, true)).toBe(0);
  });
  test("ao soltar: cai da altura da mao, quica uma vez e para; com movimento reduzido, no chao na hora", () => {
    expect(alturaDepoisDeSoltar(0, false)).toBe(MAO.alturaTexels);
    expect(alturaDepoisDeSoltar(MAO.quedaMs, false)).toBeCloseTo(0, 9);
    expect(alturaDepoisDeSoltar(MAO.quedaMs + MAO.quiqueMs / 2, false)).toBeCloseTo(MAO.quiqueTexels, 9);
    expect(alturaDepoisDeSoltar(MAO.quedaMs + MAO.quiqueMs, false)).toBe(0);
    expect(soltarAcabou(MAO.quedaMs + MAO.quiqueMs, false)).toBe(true);
    expect(soltarAcabou(10, false)).toBe(false);
    expect(alturaDepoisDeSoltar(10, true)).toBe(0);
    expect(soltarAcabou(0, true)).toBe(true);
  });
});
