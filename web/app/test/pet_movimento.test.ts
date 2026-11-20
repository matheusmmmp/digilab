// O pet se mexendo entre as decisoes (so vista; o motor nao muda). Sem DOM (vitest em node).
//   - o Seguidor: em `ocioso` nunca passa do raio do ponto do motor e volta a ele; ao andar chega antes da proxima decisao; em Pausa e
//     com movimento reduzido fica parado; dormindo fica como era;
import { describe, expect, test } from "vitest";
import { CMU_MVP } from "../motor/index.ts";
import { ACOES_NO_LUGAR, INTERVALO_DECISAO_MIN, RAIO_NO_LUGAR, Seguidor, duracaoCaminhadaMs, type Movimento } from "../src/telas/pet/vistaMundo.ts";

const cm = CMU_MVP;
const mov = (extra: Partial<Movimento> = {}): Movimento => ({ velJogo: 10, acao: "ocioso", dorme: false, reduzido: false, ...extra });
const FRAME = 16;

describe("o seguidor do pet na vista", () => {
  test("em ocioso, brincar e chamar_atencao nunca passa do raio do ponto do motor, e se mexe de verdade", () => {
    for (const acao of ACOES_NO_LUGAR) {
      const s = new Seguidor(7), alvo: [number, number] = [500, 240];
      s.seguir(alvo, 0, cm, mov({ acao }));
      let maior = 0, mexeu = 0, voltou = 0;
      for (let t = 0; t < 60_000; t += FRAME) {
        const p = s.seguir(alvo, FRAME, cm, mov({ acao })), d = Math.hypot(p[0] - alvo[0], p[1] - alvo[1]);
        maior = Math.max(maior, d);
        if (d > 0.5) mexeu++;
        if (d < 0.05) voltou++;
      }
      expect(maior, acao).toBeLessThanOrEqual(RAIO_NO_LUGAR + 1e-9);
      expect(mexeu, acao + " se mexe").toBeGreaterThan(100);
      expect(voltou, acao + " volta ao ponto").toBeGreaterThan(20);
    }
  });
  test("ao andar chega a posicao do motor antes da proxima decisao, em velocidade constante", () => {
    for (const velJogo of [1, 10, 60]) {
      const intervaloMs = (INTERVALO_DECISAO_MIN / velJogo) * 1000, s = new Seguidor();
      s.seguir([400, 200], 0, cm, mov({ velJogo, acao: "explorar" }));
      const alvo: [number, number] = [400 + 60, 200 + 20];
      let t = 0, chegou = -1, ant = 0;
      while (t < intervaloMs && chegou < 0) {
        t += FRAME;
        const p = s.seguir(alvo, FRAME, cm, mov({ velJogo, acao: "explorar" })), d = Math.hypot(alvo[0] - p[0], alvo[1] - p[1]);
        if (d < 0.05) chegou = t;
        if (chegou < 0) { expect(s.caminhando).toBe(true); expect(d).toBeLessThan(ant || Infinity); ant = d; }
      }
      expect(chegou, `a ${velJogo} min/s`).toBeGreaterThan(0);
      expect(chegou).toBeLessThanOrEqual(Math.min(intervaloMs, duracaoCaminhadaMs(velJogo)) + FRAME);
      expect(s.caminhando).toBe(false);
    }
    /* a 10 min/s a caminhada ocupa o intervalo (~1,35 s de 1,5 s), nao os ~250 ms de antes */
    expect(duracaoCaminhadaMs(10)).toBeGreaterThan(1000);
  });
  test("em Pausa nada se mexe, nem andando nem no lugar", () => {
    const s = new Seguidor(), alvo: [number, number] = [300, 100];
    s.seguir([250, 100], 0, cm, mov({ acao: "explorar" }));
    const antes = [...s.seguir(alvo, FRAME, cm, mov({ velJogo: 10, acao: "explorar" }))];
    for (let i = 0; i < 100; i++) expect(s.seguir(alvo, FRAME, cm, mov({ velJogo: 0, acao: "explorar" }))).toEqual(antes);
    const p = new Seguidor(3); p.seguir(alvo, 0, cm, mov({ velJogo: 0 }));
    for (let i = 0; i < 500; i++) expect(p.seguir(alvo, FRAME, cm, mov({ velJogo: 0 }))).toEqual(alvo);
  });
  test("com movimento reduzido o ocioso fica parado no ponto, e o andar e o suave de antes", () => {
    const s = new Seguidor(3), alvo: [number, number] = [300, 100];
    s.seguir(alvo, 0, cm, mov({ reduzido: true }));
    for (let i = 0; i < 2000; i++) expect(s.seguir(alvo, FRAME, cm, mov({ reduzido: true }))).toEqual(alvo);
    const novo: [number, number] = [340, 100];
    let p = s.seguir(novo, FRAME, cm, mov({ reduzido: true, acao: "explorar" }));
    expect(p[0]).toBeGreaterThan(300);
    for (let i = 0; i < 400; i++) p = s.seguir(novo, FRAME, cm, mov({ reduzido: true, acao: "explorar" }));
    expect(p).toEqual(novo);
  });
  test("dormindo fica parado no ponto; sem `mov` e o suave de antes; longe demais salta", () => {
    const s = new Seguidor(3), alvo: [number, number] = [300, 100];
    s.seguir(alvo, 0, cm, mov({ dorme: true, acao: "dormir" }));
    for (let i = 0; i < 2000; i++) expect(s.seguir(alvo, FRAME, cm, mov({ dorme: true, acao: "ocioso" }))).toEqual(alvo);
    const v = new Seguidor(); v.seguir([100, 100], 0, cm);
    const p = v.seguir([140, 100], 250, cm);
    expect(p[0]).toBeGreaterThan(120); expect(p[0]).toBeLessThan(140);
    expect(v.seguir([100 + 8 * cm.sub + 500, 100], 16, cm, mov())).toEqual([100 + 8 * cm.sub + 500, 100]);
  });
});
