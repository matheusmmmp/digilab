/* A trava do "só ver" (CN3, UX-NV-5; src/jogo.ts): com o pet aberto em outro aparelho ou com a escolha da história pendente, o pet aparece
   e nenhuma ação entra no registro deste aparelho, nem o tempo; nada se grava. E a chave: sem VITE_DIGILAB_NUVEM, a nuvem não liga. */
import { describe, expect, test } from "vitest";
import { Motor } from "../motor/index.ts";
import { nuvemNoBuild } from "../src/conta/apiDoBuild.ts";
import { ligarProduto } from "../src/produto.ts";
import { CHAVE, type Armazenamento } from "../src/save.ts";
import { SoParaVer, acoesTravadas, focar, iniciarJogo, jogoAtual, mudarMotor, mudarTamer, recarregarDoArmazenamento, travarAcoes, trocarMotor } from "../src/jogo.ts";
import { nuvemLigada } from "../src/nuvem/cliente.ts";

function armaz(): Armazenamento & { gravacoes: string[]; dados: Record<string, string> } {
  const dados: Record<string, string> = {}, gravacoes: string[] = [];
  return { dados, gravacoes, getItem: k => (k in dados ? dados[k]! : null), setItem(k, v) { dados[k] = v; gravacoes.push(k); } };
}

describe("a trava do só ver (UX-NV-5)", () => {
  test("travado: a ação do dono e o tempo não entram no registro, nada se grava, e as ações explícitas falham alto", () => {
    const a = armaz();
    iniciarJogo(a);
    mudarMotor(m => m.observar("alimentar"));
    const antes = JSON.stringify(jogoAtual().motor.log), gravadas = a.gravacoes.length;
    travarAcoes(true);
    expect(acoesTravadas()).toBe(true);
    mudarMotor(m => m.observar("brincar"));
    mudarMotor(m => m.avancar(30), "adiado");
    expect(JSON.stringify(jogoAtual().motor.log)).toBe(antes);
    expect(a.gravacoes.length).toBe(gravadas);
    expect(() => trocarMotor(ligarProduto(new Motor(102, jogoAtual().motor.versao)), "novo")).toThrow(SoParaVer);
    expect(() => mudarTamer(() => 1)).toThrow(SoParaVer);
    expect(() => focar("A")).toThrow(SoParaVer);
    /* destravado, tudo volta a ser como sempre */
    travarAcoes(false);
    mudarMotor(m => m.observar("brincar"));
    expect(jogoAtual().motor.log.length).toBeGreaterThan(JSON.parse(antes).length);
    expect(a.gravacoes.length).toBeGreaterThan(gravadas);
  });
  test("o save que a nuvem grava no armazenamento é relido (o pet da nuvem na tela), sem gravar por cima", () => {
    const a = armaz();
    iniciarJogo(a);
    const outro = ligarProduto(new Motor(103, jogoAtual().motor.versao));
    outro.avancar(40); outro.observar("alimentar");
    a.dados[CHAVE] = JSON.stringify({ semente: outro.semente, log: outro.log, versao: outro.versao });
    travarAcoes(true);
    const n = a.gravacoes.length;
    recarregarDoArmazenamento();
    expect(jogoAtual().motor.semente).toBe(103);
    expect(jogoAtual().motor.log).toEqual(outro.log);
    expect(a.gravacoes.length).toBe(n);
    travarAcoes(false);
  });
  test("sem a chave no build, a nuvem não liga", () => {
    expect(nuvemNoBuild()).toBe(false);
    expect(nuvemLigada()).toBe(false);
  });
});
