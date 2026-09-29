// Estado do app (src/jogo.ts): uma so porta de mudanca, que grava o save; save que nao abre nunca e regravado;
// o tempo grava no maximo a cada 2 s e o pendente sai ao fechar a aba.
import { describe, expect, test } from "vitest";
import { CHAVE, textoSave, type Armazenamento } from "../src/save.ts";
import { VERSAO_PET } from "../motor/index.ts";
import { gravarPendente, iniciarJogo, jogoAtual, mudarMotor, novoPet } from "../src/jogo.ts";

const armaz = (dados: Record<string, string> = {}) => {
  let escritas = 0;
  const a: Armazenamento & { dados: Record<string, string>; escritas: () => number } = {
    dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; escritas++; }, escritas: () => escritas,
  };
  return a;
};

describe("jogo", () => {
  test("sem save: pet de exemplo, que so e gravado quando muda", () => {
    const a = armaz();
    iniciarJogo(a);
    expect(jogoAtual().origem).toBe("exemplo");
    expect(a.escritas()).toBe(0);
    mudarMotor(m => m.observar("alimentar"));
    expect(jogoAtual().origem).toBe("save");
    expect(a.dados[CHAVE]).toBe(textoSave(jogoAtual().motor));
  });
  test("save que nao abre: o app nao grava por cima, nem com o tempo nem com acao", () => {
    const bruto = '{"semente":1,"log":[[480,"x",1]]}', a = armaz({ [CHAVE]: bruto });
    iniciarJogo(a);
    expect(jogoAtual().erroSave).not.toBeNull();
    mudarMotor(m => m.avancar(30), "adiado");
    mudarMotor(m => m.observar("limpar"));
    gravarPendente();
    expect(a.dados[CHAVE]).toBe(bruto);
    expect(a.escritas()).toBe(0);
  });
  test("tempo grava no maximo a cada 2 s; acao do dono grava na hora; o pendente sai ao fechar", () => {
    const a = armaz();
    iniciarJogo(a);
    mudarMotor(m => m.avancar(1));                 /* primeira mudanca: grava */
    const n0 = a.escritas();
    mudarMotor(m => m.avancar(10), "adiado");
    mudarMotor(m => m.avancar(10), "adiado");
    expect(a.escritas()).toBe(n0);                 /* dentro de 2 s: nada */
    gravarPendente();
    expect(a.escritas()).toBe(n0 + 1);
    expect(a.dados[CHAVE]).toBe(textoSave(jogoAtual().motor));
    mudarMotor(m => m.observar("brincar"));
    expect(a.escritas()).toBe(n0 + 2);
    gravarPendente();                               /* nada pendente: nao grava de novo */
    expect(a.escritas()).toBe(n0 + 2);
  });
  test("ovo novo: troca o pet, grava e choca por 16 quadros", () => {
    const a = armaz();
    iniciarJogo(a);
    novoPet();
    const j = jogoAtual();
    expect(j.nascendo).toBe(16);
    expect(j.motor.log).toEqual([]);
    expect(JSON.parse(a.dados[CHAVE])).toEqual({ semente: j.motor.semente, log: [], versao: VERSAO_PET });
  });
});
