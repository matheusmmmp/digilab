// CONTA, CN0 (docs/PLANO_V3_CONTA.md, secao 10): o script da medida do save (scripts/medir_cn0_save.ts) e o tempo entre fechar e abrir.
// O script: uma vida curta de cada perfil sai com o save que reabre, os bytes crescem com os dias e o comprimido e menor que o cru.
// O tempo: o laco do tempo.ts com o relogio falso. Fechar num aparelho e abrir noutro, horas depois, devolve o pet no mesmo tick (o save
// nao tem hora de parede); com a aba aberta, um passo depois de um sono do PC anda no maximo 1 h real na velocidade escolhida.
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { PERFIS, bytes, conferirReplay, tempoFechado, viver } from "../scripts/medir_cn0_save.ts";
import { CHAVE, type Armazenamento } from "../src/save.ts";
import { TICK_INICIAL } from "../motor/index.ts";
import { gravarPendente, iniciarJogo, jogoAtual, mudarMotor } from "../src/jogo.ts";
import { VEL_1X, escolherVelocidade, iniciarTempo } from "../src/tempo.ts";

const armaz = (dados: Record<string, string> = {}): Armazenamento & { dados: Record<string, string> } =>
  ({ dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } });

describe("CN0: a medida do save", () => {
  test("bytes: o comprimido de um texto repetitivo e menor que o cru", () => {
    const b = bytes(JSON.stringify(Array.from({ length: 200 }, (_, i) => [480 + i, "t", 15])));
    expect(b.gzip).toBeLessThan(b.cru);
    expect(b.brotli).toBeLessThan(b.cru);
  });
  for (const grupo of [false, true]) test(`uma vida curta de cada perfil (${grupo ? "grupo" : "um pet"}): o save reabre e cresce`, () => {
    for (const p of PERFIS) {
      const v = viver(p, grupo, 0, 2);
      expect(v.dias.length).toBe(2);
      expect(conferirReplay(v.textoFinal)).toBe(true);
      expect(v.dias[1].eventos).toBeGreaterThan(v.dias[0].eventos - 1);
      expect(v.dias[1].save.cru).toBeGreaterThanOrEqual(v.dias[0].save.cru);
      expect(v.dias[1].eventosNovos).toBe(v.dias[1].eventos - v.dias[0].eventos);
      if (p.tvMinDia > 0) expect(v.st).toBeGreaterThan(0);
    }
  }, 120_000);
  test("o save nao tem hora de parede: reabrir o texto devolve o mesmo tick", () => {
    const v = viver(PERFIS[1], false, 0, 1), t = tempoFechado(v.textoFinal);
    expect(t.temHoraDeParede).toBe(false);
    expect(t.campos).toEqual(["semente", "log", "versao"]);
    expect(t.tickAoAbrir).toBe(t.tickAoFechar);
  });
});

describe("CN0: o tempo entre fechar num aparelho e abrir noutro (tempo.ts)", () => {
  /* o relogio do laco e o performance.now: aqui, um relogio na mao (agora, em ms), e o setInterval falso roda os passos de 100 ms */
  let agora = 0;
  beforeEach(() => { agora = 0; vi.useFakeTimers({ toFake: ["setInterval", "clearInterval"] }); vi.spyOn(performance, "now").mockImplementation(() => agora); });
  afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); escolherVelocidade(10); });
  const passos = (n: number, ms = 100): void => { for (let k = 0; k < n; k++) { agora += ms; vi.advanceTimersByTime(ms); } };

  test("fechado, o pet nao envelhece: 8 h depois, noutro aparelho, ele abre no tick em que fechou", () => {
    escolherVelocidade(10);                                        // a velocidade com que o jogo abre (10 min de jogo por segundo)
    const a = armaz();
    iniciarJogo(a);
    mudarMotor(m => m.observar("alimentar"));                      // grava o save
    let parar = iniciarTempo();
    passos(30);                                                    // 3 s com a aba aberta: 30 min de jogo
    parar(); gravarPendente();
    const tickAoFechar = jogoAtual().motor.e.tick, texto = a.dados[CHAVE];
    expect(tickAoFechar).toBeGreaterThan(TICK_INICIAL);
    agora += 8 * 3_600_000;                                        // 8 h com a aba fechada: o laco nao roda
    const b = armaz({ [CHAVE]: texto });                           // o outro aparelho: o mesmo texto noutro armazenamento
    iniciarJogo(b);
    expect(jogoAtual().motor.e.tick).toBe(tickAoFechar);
    parar = iniciarTempo();
    passos(1);                                                     // o primeiro passo depois de abrir: 0,1 s
    parar();
    expect(jogoAtual().motor.e.tick - tickAoFechar).toBeLessThanOrEqual(1);   // 0,1 s x 10 min/s = 1 min; nada das 8 h
  });
  test("aberto com o PC dormindo 8 h: o passo de depois anda 1 h real, nao 8 (a 1x, 60 min de jogo)", () => {
    const a = armaz();
    iniciarJogo(a);
    mudarMotor(m => m.observar("alimentar"));
    escolherVelocidade(VEL_1X);
    const parar = iniciarTempo(), antes = jogoAtual().motor.e.tick;
    agora += 8 * 3_600_000;                                        // o relogio pula 8 h sem nenhum passo no meio
    vi.advanceTimersByTime(100);                                   // o primeiro passo depois: dt = min(3600 s, 8 h)
    parar();
    expect(jogoAtual().motor.e.tick - antes).toBe(60);
  });
});
