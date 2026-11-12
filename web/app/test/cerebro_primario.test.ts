/* O cerebro primario (docs/TAREFA_V3_CEREBRO_PRIMARIO.md; pedido do Matheus de 2026-11-04): a v17, o v15 com o cerebro trocavel, que a v21
   herda. Desde a LP4 da LUTA_POC so a v21 abre: a comparacao com a v15 e a promocao de um pet v15 sairam com as versoes antigas.
     - sem "cb", a v21 decide com o A;
     - o ovo novo nasce com o modular por padrao (o "cb" logo depois das chaves do produto), ou com o A, pela preferencia;
     - a troca no meio da vida: o cerebro que sai fica parado com o que aprendeu, o que entra decide; o replay refaz tudo bit a bit;
     - o que nao vale falha alto: o mesmo cerebro, o pet de teste, um "cb" malformado no registro;
     - no app: a troca no pet ativo grava o registro, e a preferencia dos ovos novos fica fora do save. */
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

describe("o cerebro trocavel (a v17, na v21)", () => {
  test("sem \"cb\", a v21 decide com o A, e o replay refaz a vida", () => {
    const m = new Motor(101, 21);
    viver(m, 1.5);
    expect(m.cerebroAtual).toBe("a");
    expect(m.lab).toBeNull();
    expect(Motor.reproduzir(101, copia(m.log), 21).assinatura()).toBe(m.assinatura());
  });

  test("o ovo novo nasce com o modular por padrao, e com o A pela preferencia; o replay le o cerebro do registro", () => {
    expect(VERSAO_PET).toBe(30);   // a v30 desde a BB2 (a v27 com o lance do dono)
    expect(CHAVE_CEREBRO).toBe(CHAVE + "-cerebro");
    expect(cerebroDosOvos()).toBe("modular");
    const m = ligarProduto(new Motor(303, 21));
    expect(m.log[1]).toEqual([TICK_INICIAL, "cb", { cerebro: "modular" }]);
    expect(m.cerebroAtual).toBe("modular"); expect(m.lab).not.toBeNull();
    escolherCerebroDosOvos("a");
    expect(dados[CHAVE_CEREBRO]).toBe("a");
    const a = ligarProduto(new Motor(303, 21));
    expect(a.log[1]).toEqual([TICK_INICIAL, "cb", { cerebro: "a" }]);
    expect(a.cerebroAtual).toBe("a"); expect(a.lab).toBeNull();
    viver(m, 2); viver(a, 2);
    expect(m.lab!.motivos.length).toBe(2 * TPD / 15);              // toda decisao foi do modular
    expect(m.assinatura()).not.toBe(a.assinatura());
    for (const x of [m, a]) {
      const r = Motor.reproduzir(303, copia(x.log), 21);
      expect(r.assinatura()).toBe(x.assinatura());
      expect(r.cerebroAtual).toBe(x.cerebroAtual);
    }
  });

  test("a troca no meio da vida: o que sai fica parado, o que entra decide, e o replay refaz evento a evento", () => {
    const m = new Motor(404, 21);
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
    const r = new Motor(404, 21), log = copia(m.log);
    for (const ev of log) r.aplicarEvento(ev);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(JSON.stringify(r.lab!.estadoInterno())).toBe(JSON.stringify(m.lab!.estadoInterno()));
    expect(log.filter(ev => ev[1] === "cb").map(ev => (ev[2] as { cerebro: string }).cerebro)).toEqual(["modular", "a", "modular"]);
  });

  test("o que nao vale falha alto", () => {
    const m = ligarProduto(new Motor(505, 21));
    expect(() => m.trocarCerebro("modular")).toThrow(/já decide/);
    expect(() => new Motor(505, VERSAO_PET_LAB).trocarCerebro("a")).toThrow(/v17/);
    expect(() => new Motor(505, 21).aplicarEvento([TICK_INICIAL, "cb", { cerebro: "b" }] as unknown as EventoRegistro)).toThrow(/inválida/);
    expect(() => new Motor(505, 21).aplicarEvento([TICK_INICIAL, "cb", { cerebro: "a", x: 1 }] as unknown as EventoRegistro)).toThrow(/inválida/);
    expect(() => new Motor(505, VERSAO_PET_LAB).aplicarEvento([TICK_INICIAL, "cb", { cerebro: "modular" }])).toThrow(/v17/);
    /* o mesmo cerebro no meio da vida, no registro */
    const v = new Motor(505, 21); v.avancar(60);
    expect(() => v.aplicarEvento([v.e.tick, "cb", { cerebro: "a" }])).toThrow(/já decide/);
  });
});

describe("no app", () => {
  const armaz = (d: Record<string, string> = {}): Armazenamento & { d: Record<string, string> } =>
    ({ d, getItem: k => (k in d ? d[k]! : null), setItem(k, v) { d[k] = v; } });

  test("a troca no pet ativo: o \"cb\" no registro gravado; a mesma troca de novo falha", () => {
    escolherCerebroDosOvos("a");
    const antigo = ligarProduto(new Motor(606, 21)); viver(antigo, .5);
    delete dados[CHAVE_CEREBRO];
    const a = armaz({ [CHAVE]: textoSave(antigo) });
    iniciarJogo(a);
    expect(jogoAtual().motor.versao).toBe(21);
    expect(() => trocarCerebroDoPet("a")).toThrow(/já decide/);
    trocarCerebroDoPet("modular");
    const s = JSON.parse(a.d[CHAVE]!) as { versao: number; log: EventoRegistro[] };
    expect(s.versao).toBe(21);
    expect(s.log.slice(0, -3)).toEqual(JSON.parse(JSON.stringify(antigo.log)));
    expect(s.log.at(-3)).toEqual([antigo.e.tick, "mi", { ilha: "grande" }]);          // o pet v21 passou para a ilha grande ao abrir (ILHA_AGUA, IG4)
    expect(s.log.at(-2)).toEqual([antigo.e.tick, "ma", { alcance: 2048 }]);           // e ganhou a memoria de 128 celulas (ILHA_AGUA, IG6)
    expect(s.log.at(-1)).toEqual([antigo.e.tick, "cb", { cerebro: "modular" }]);
    expect(Motor.reproduzir(606, s.log, 21).assinatura()).toBe(jogoAtual().motor.assinatura());
    expect(dados[CHAVE_CEREBRO]).toBeUndefined();                       // a troca do pet nao mexe na preferencia dos ovos
  });

  test("o ovo novo segue a preferencia", () => {
    const a = armaz({ [CHAVE]: textoSave(new Motor(707, 21)) });
    iniciarJogo(a);
    escolherCerebroDosOvos("a");
    novoPet();
    expect(jogoAtual().motor.versao).toBe(VERSAO_PET);
    expect(jogoAtual().motor.cerebroAtual).toBe("a");
    expect((JSON.parse(a.d[CHAVE]!) as { log: EventoRegistro[] }).log[1]).toEqual([TICK_INICIAL, "cb", { cerebro: "a" }]);
  });
});
