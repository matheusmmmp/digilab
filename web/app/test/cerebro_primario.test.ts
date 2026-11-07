/* O cerebro primario (docs/TAREFA_V3_CEREBRO_PRIMARIO.md; pedido do Matheus de 2026-11-04): a v17, o v15 com o cerebro trocavel.
     - sem "cb", a v17 e a v15 (a mesma assinatura, evento a evento), e a promocao de um pet v15 vivo confere isso;
     - o ovo novo nasce com o modular por padrao (o "cb" logo depois das chaves do produto), ou com o A, pela preferencia;
     - a troca no meio da vida: o cerebro que sai fica parado com o que aprendeu, o que entra decide; o replay refaz tudo bit a bit;
     - o que nao vale falha alto: o mesmo cerebro, um pet que nao e v17, um "cb" malformado no registro;
     - no app: a troca no pet ativo grava o registro (o v15 vira v17), e a preferencia dos ovos novos fica fora do save. */
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { TICK_INICIAL, TPD, VERSAO_PET, VERSAO_PET_LAB } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import type { AcaoDono, EventoRegistro } from "../motor/tipos.ts";
import { CHAVE_CEREBRO, cerebroDosOvos, escolherCerebroDosOvos } from "../src/cerebro.ts";
import { iniciarJogo, jogoAtual, novoPet, trocarCerebroDoPet } from "../src/jogo.ts";
import { ligarProduto } from "../src/produto.ts";
import { CHAVE, textoSave, type Armazenamento } from "../src/save.ts";

/** o dono do jogo com o mundo (o mesmo do pet_lab.test.ts): racao perto quando ha fome, limpa, carinho e um tapa de vez em quando */
function viver(m: Motor, dias: number): void {
  const passos = Math.round(dias * TPD / 30);
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e, mu = m.mundo!;
    if (e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
    if (e.sujeira >= 2) m.observar("limpar");
    if (p % 5 === 0) m.observar("acariciar");
    if (p % 11 === 10) m.observar("tapa" as AcaoDono);
  }
}
const copia = (log: readonly EventoRegistro[]) => JSON.parse(JSON.stringify(log)) as EventoRegistro[];

let dados: Record<string, string> = {};
beforeEach(() => {
  dados = {};
  vi.stubGlobal("localStorage", { getItem: (k: string) => (k in dados ? dados[k]! : null), setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; } });
});
afterEach(() => { vi.unstubAllGlobals(); });

describe("a v17: o cerebro trocavel", () => {
  test("sem \"cb\", a v17 e a v15: a mesma assinatura depois de cada evento", () => {
    const m15 = new Motor(101, 15);
    viver(m15, 1.5);
    const r15 = new Motor(101, 15), r17 = new Motor(101, 17);
    m15.log.forEach((ev, i) => { r15.aplicarEvento(ev); r17.aplicarEvento(ev); expect(r17.assinatura(), `evento ${i}`).toBe(r15.assinatura()); });
    expect(r17.cerebroAtual).toBe("a");
    expect(r17.lab).toBeNull();
  });

  test("a promocao: um pet v15 vivo vira v17 com o mesmo registro e a mesma vida; os outros nao", () => {
    const m = ligarProduto(new Motor(202, 15));
    expect(m.log.map(ev => ev[1])).toEqual(["p"]);         // o v15 nao ganha o "cb" do ovo
    viver(m, 1);
    const p = Motor.promoverV17(m);
    expect(p.versao).toBe(17); expect(m.versao).toBe(15);
    expect(p.assinatura()).toBe(m.assinatura());
    expect(p.log).toEqual(m.log);
    expect(() => Motor.promoverV17(new Motor(202, 14))).toThrow(/v15/);
    expect(() => Motor.promoverV17(p)).toThrow(/v15/);
  });

  test("o ovo novo nasce com o modular por padrao, e com o A pela preferencia; o replay le o cerebro do registro", () => {
    expect(VERSAO_PET).toBe(19);
    expect(CHAVE_CEREBRO).toBe(CHAVE + "-cerebro");
    expect(cerebroDosOvos()).toBe("modular");
    const m = ligarProduto(new Motor(303));
    expect(m.log[1]).toEqual([TICK_INICIAL, "cb", { cerebro: "modular" }]);
    expect(m.cerebroAtual).toBe("modular"); expect(m.lab).not.toBeNull();
    escolherCerebroDosOvos("a");
    expect(dados[CHAVE_CEREBRO]).toBe("a");
    const a = ligarProduto(new Motor(303));
    expect(a.log[1]).toEqual([TICK_INICIAL, "cb", { cerebro: "a" }]);
    expect(a.cerebroAtual).toBe("a"); expect(a.lab).toBeNull();
    viver(m, 2); viver(a, 2);
    expect(m.lab!.motivos.length).toBe(2 * TPD / 15);              // toda decisao foi do modular
    expect(m.assinatura()).not.toBe(a.assinatura());
    for (const x of [m, a]) {
      const r = Motor.reproduzir(303, copia(x.log), 17);
      expect(r.assinatura()).toBe(x.assinatura());
      expect(r.cerebroAtual).toBe(x.cerebroAtual);
    }
  });

  test("a troca no meio da vida: o que sai fica parado, o que entra decide, e o replay refaz evento a evento", () => {
    const m = Motor.promoverV17(ligarProduto(new Motor(404, 15)));
    viver(m, 1);
    const aAntes = JSON.stringify(m.cerebro!.estadoInterno());
    m.trocarCerebro("modular");
    expect(m.cerebroAtual).toBe("modular");
    viver(m, 1);
    expect(JSON.stringify(m.cerebro!.estadoInterno())).toBe(aAntes);   // o A nao aprendeu nada enquanto o modular decidia
    const mod = m.lab!, kAntes = mod.k;
    expect(kAntes).toBe(TPD / 15);
    m.trocarCerebro("a");
    expect(m.lab).toBeNull();
    viver(m, .5);
    expect(mod.k).toBe(kAntes);                                         // o modular parado
    expect(JSON.stringify(m.cerebro!.estadoInterno())).not.toBe(aAntes);
    m.trocarCerebro("modular");
    viver(m, .5);
    expect(m.lab).toBe(mod);                                            // o mesmo modular, com o que aprendeu
    expect(mod.k).toBe(kAntes + TPD / 30);
    const r = new Motor(404, 17), log = copia(m.log);
    for (const ev of log) r.aplicarEvento(ev);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(JSON.stringify(r.lab!.estadoInterno())).toBe(JSON.stringify(m.lab!.estadoInterno()));
    expect(log.filter(ev => ev[1] === "cb").map(ev => (ev[2] as { cerebro: string }).cerebro)).toEqual(["modular", "a", "modular"]);
  });

  test("o que nao vale falha alto", () => {
    const m = ligarProduto(new Motor(505));
    expect(() => m.trocarCerebro("modular")).toThrow(/já decide/);
    expect(() => new Motor(505, 15).trocarCerebro("modular")).toThrow(/v17/);
    expect(() => new Motor(505, VERSAO_PET_LAB).trocarCerebro("a")).toThrow(/v17/);
    expect(() => new Motor(505, 17).aplicarEvento([TICK_INICIAL, "cb", { cerebro: "b" }] as unknown as EventoRegistro)).toThrow(/inválida/);
    expect(() => new Motor(505, 17).aplicarEvento([TICK_INICIAL, "cb", { cerebro: "a", x: 1 }] as unknown as EventoRegistro)).toThrow(/inválida/);
    expect(() => new Motor(505, 15).aplicarEvento([TICK_INICIAL, "cb", { cerebro: "modular" }])).toThrow(/v17/);
    /* o mesmo cerebro no meio da vida, no registro */
    const v = new Motor(505, 17); v.avancar(60);
    expect(() => v.aplicarEvento([v.e.tick, "cb", { cerebro: "a" }])).toThrow(/já decide/);
  });
});

describe("no app", () => {
  const armaz = (d: Record<string, string> = {}): Armazenamento & { d: Record<string, string> } =>
    ({ d, getItem: k => (k in d ? d[k]! : null), setItem(k, v) { d[k] = v; } });

  test("a troca no pet ativo: o v15 do save passa a v17, com o \"cb\" no registro gravado; a mesma troca de novo falha", () => {
    const antigo = ligarProduto(new Motor(606, 15)); viver(antigo, .5);
    const a = armaz({ [CHAVE]: textoSave(antigo) });
    iniciarJogo(a);
    expect(jogoAtual().motor.versao).toBe(15);
    expect(() => trocarCerebroDoPet("a")).toThrow(/já decide/);
    expect(jogoAtual().motor.versao).toBe(15);                          // a troca recusada nao promove
    trocarCerebroDoPet("modular");
    const s = JSON.parse(a.d[CHAVE]!) as { versao: number; log: EventoRegistro[] };
    expect(s.versao).toBe(17);
    expect(s.log.slice(0, -1)).toEqual(JSON.parse(JSON.stringify(antigo.log)));
    expect(s.log.at(-1)).toEqual([antigo.e.tick, "cb", { cerebro: "modular" }]);
    expect(Motor.reproduzir(606, s.log, 17).assinatura()).toBe(jogoAtual().motor.assinatura());
    expect(dados[CHAVE_CEREBRO]).toBeUndefined();                       // a troca do pet nao mexe na preferencia dos ovos
  });

  test("os pets v13 e v14 nao trocam; o ovo novo segue a preferencia", () => {
    const a = armaz({ [CHAVE]: textoSave(new Motor(707, 14)) });
    iniciarJogo(a);
    expect(() => trocarCerebroDoPet("modular")).toThrow(/versão 14/);
    escolherCerebroDosOvos("a");
    novoPet();
    expect(jogoAtual().motor.versao).toBe(19);
    expect(jogoAtual().motor.cerebroAtual).toBe("a");
    expect((JSON.parse(a.d[CHAVE]!) as { log: EventoRegistro[] }).log[1]).toEqual([TICK_INICIAL, "cb", { cerebro: "a" }]);
  });
});
