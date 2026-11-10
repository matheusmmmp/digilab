// O laboratorio na tela (src/lab.ts, src/jogo.ts, src/importar.ts; docs/TAREFA_V3_LAB_MODULAR.md, LM5b):
//   - o pet de teste (v16) tem espaco proprio do save e nunca toca o save do pet de hoje nem os guardados;
//   - Abrir mostra o pet de teste sem trocar o pet ativo (LM5-7); o pet de hoje volta como estava;
//   - Descartar apaga so o save do pet de teste (LM5-8);
//   - o arquivo v16 abre, exporta e nunca vira pet ativo nem guardado.
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { Motor, VERSAO_PET, VERSAO_PET_LAB, petDeTeste } from "../motor/index.ts";
import { CHAVE, textoSave, type Armazenamento } from "../src/save.ts";
import { CHAVE_GUARDADOS } from "../src/pets.ts";
import { CHAVE_LAB, CHAVE_LAB_LIGADO, chocarOvoLab, descartarPetLab, labLigado, lerPetLab, ligarLab } from "../src/lab.ts";
import { abrirLab, iniciarJogo, jogoAtual, motorReal, mudarMotor, sairDoLab, trocarMotor } from "../src/jogo.ts";
import { ficarComArquivo, importarSemConflito, lerArquivo, nomeArquivo } from "../src/importar.ts";

let dados: Record<string, string>;
const armaz = (): Armazenamento => ({ getItem: k => (k in dados ? dados[k]! : null), setItem(k, v) { dados[k] = v; } });
beforeEach(() => {
  dados = {};
  vi.stubGlobal("localStorage", { getItem: (k: string) => (k in dados ? dados[k]! : null), setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; } });
});
afterEach(() => { vi.unstubAllGlobals(); });

/** o jogo com um pet de hoje que ja viveu um pouco, e os guardados de sempre */
function jogoDeHoje(): { texto: string; guardados: string } {
  const hoje = new Motor(555); hoje.avancar(300); hoje.observar("alimentar");
  dados[CHAVE] = textoSave(hoje);
  dados[CHAVE_GUARDADOS] = JSON.stringify([JSON.parse(textoSave(new Motor(777)))]);
  iniciarJogo(armaz());
  return { texto: dados[CHAVE]!, guardados: dados[CHAVE_GUARDADOS]! };
}

describe("o espaco do pet de teste", () => {
  test("a chave vem desligada; so um pet de teste por vez; o ovo nasce v16 no espaco proprio", () => {
    expect(labLigado()).toBe(false);
    ligarLab(true);
    expect(dados[CHAVE_LAB_LIGADO]).toBe("1");
    expect(labLigado()).toBe(true);
    expect(lerPetLab().tipo).toBe("vazio");
    const m = chocarOvoLab();
    expect(m.versao).toBe(VERSAO_PET_LAB);
    /* os chamados do bebe pelo corpo, como nos ovos do jogo, e nao pelo relogio (2026-11-04) */
    expect(m.produto).toEqual({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
    const l = lerPetLab();
    expect(l.tipo === "ok" && l.motor.assinatura()).toBe(m.assinatura());
    expect(() => chocarOvoLab()).toThrow(/já existe um pet de teste/);
    expect(dados[CHAVE]).toBeUndefined();
    expect(dados[CHAVE_GUARDADOS]).toBeUndefined();
  });
  test("o save do pet de teste que nao abre e erro visivel e nada e apagado ou sobrescrito", () => {
    dados[CHAVE_LAB] = JSON.stringify({ semente: 5, log: [], versao: 14 });
    const l = lerPetLab();
    expect(l.tipo).toBe("erro");
    expect(() => chocarOvoLab()).toThrow();
    expect(dados[CHAVE_LAB]).toBe(JSON.stringify({ semente: 5, log: [], versao: 14 }));
  });
  test("Descartar apaga so o save do pet de teste: o pet de hoje e os guardados ficam byte a byte", () => {
    const { texto, guardados } = jogoDeHoje();
    chocarOvoLab();
    expect(dados[CHAVE_LAB]).toBeDefined();
    descartarPetLab();
    expect(dados[CHAVE_LAB]).toBeUndefined();
    expect(lerPetLab().tipo).toBe("vazio");
    expect(dados[CHAVE]).toBe(texto);
    expect(dados[CHAVE_GUARDADOS]).toBe(guardados);
    expect(motorReal().semente).toBe(555);
  });
});

describe("Abrir (LM5-7): o pet de teste na tela sem trocar o pet ativo", () => {
  test("mudar o pet de teste grava em CHAVE-lab e nunca no save de hoje; sair devolve o pet de hoje", () => {
    const { texto, guardados } = jogoDeHoje();
    const lab = chocarOvoLab();
    abrirLab(lab);
    expect(jogoAtual().motor).toBe(lab);
    expect(jogoAtual().emLab!.semente).toBe(555);
    mudarMotor(m => { m.avancar(120); m.observar("acariciar"); });
    expect(dados[CHAVE]).toBe(texto);
    expect(dados[CHAVE_GUARDADOS]).toBe(guardados);
    const l = lerPetLab();
    expect(l.tipo === "ok" && l.motor.assinatura()).toBe(lab.assinatura());
    expect(l.tipo === "ok" && l.motor.log.length).toBe(lab.log.length);
    sairDoLab();
    expect(jogoAtual().emLab).toBeNull();
    expect(jogoAtual().motor.semente).toBe(555);
    expect(dados[CHAVE]).toBe(texto);
  });
  test("o pet de teste nao da medalha nem muda o registro do Tamer", () => {
    jogoDeHoje();
    const antes = dados[CHAVE + "-tamer"];
    abrirLab(chocarOvoLab());
    mudarMotor(m => m.avancar(60));
    expect(dados[CHAVE + "-tamer"]).toBe(antes);
  });
  test("trocar o pet (ovo novo, ativar guardado) com o pet de teste na tela age sobre o pet de hoje e deixa o save do teste", () => {
    jogoDeHoje();
    const lab = chocarOvoLab();
    abrirLab(lab);
    const salvo = dados[CHAVE_LAB];
    trocarMotor(new Motor(888), "novo");
    expect(jogoAtual().emLab).toBeNull();
    expect(jogoAtual().motor.semente).toBe(888);
    expect(dados[CHAVE_LAB]).toBe(salvo);
    expect(JSON.parse(dados[CHAVE]!).semente).toBe(888);
  });
  test("Descartar com o pet de teste aberto: volta ao pet de hoje e o save do teste some", () => {
    const { texto } = jogoDeHoje();
    abrirLab(chocarOvoLab());
    sairDoLab(); descartarPetLab();
    expect(lerPetLab().tipo).toBe("vazio");
    expect(jogoAtual().motor.semente).toBe(555);
    expect(dados[CHAVE]).toBe(texto);
  });
});

describe("importar e exportar o save v16", () => {
  test("o arquivo v16 abre com o replay, o nome e o texto sao os do pet de teste, e ele e marcado como de laboratorio", () => {
    const m = petDeTeste(31); m.avancar(200);
    const l = lerArquivo(textoSave(m), "x.digilab");
    expect(l.lab).toBe(true);
    expect(l.m.versao).toBe(VERSAO_PET_LAB);
    expect(l.m.assinatura()).toBe(m.assinatura());
    expect(nomeArquivo(m)).toMatch(/^[a-z0-9-]+-D1\.digilab$/);
    expect(JSON.parse(textoSave(m)).versao).toBe(VERSAO_PET_LAB);
  });
  test("um arquivo de hoje (a v21) nao e de laboratorio; uma versao que ainda nao existe segue sem abrir", () => {
    const m = new Motor(31); m.avancar(200);
    expect(m.versao).toBe(21);
    expect(lerArquivo(textoSave(m), "a").lab).toBe(false);
    expect(() => lerArquivo(JSON.stringify({ semente: 31, log: [], versao: 20 }), "a")).toThrow(/versão 20/);
  });
  test("o v16 importado vai para o Laboratorio, nunca para o pet ativo nem para os guardados; um por vez", () => {
    const { texto, guardados } = jogoDeHoje();
    const m = petDeTeste(31); m.avancar(200);
    const l = lerArquivo(textoSave(m), "t.digilab");
    expect(importarSemConflito(l)).toMatch(/Laboratório/);
    expect(dados[CHAVE]).toBe(texto);
    expect(dados[CHAVE_GUARDADOS]).toBe(guardados);
    const aqui = lerPetLab();
    expect(aqui.tipo === "ok" && aqui.motor.assinatura()).toBe(m.assinatura());
    expect(importarSemConflito(l)).toMatch(/já está/);
    const outro = petDeTeste(32);
    expect(() => importarSemConflito(lerArquivo(textoSave(outro), "o.digilab"))).toThrow(/já existe um pet de teste/);
    expect(() => ficarComArquivo(l)).toThrow(/não toma o lugar/);
    expect(motorReal().versao).toBe(VERSAO_PET);
    expect(motorReal().semente).toBe(555);
  });
});
