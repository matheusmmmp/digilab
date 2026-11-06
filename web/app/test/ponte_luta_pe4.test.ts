/* PE4 da ponte da luta (docs/TAREFA_V3_PONTE_LUTA.md, 3.3, 3.5 e 3.7): o cerebro muda a luta por um parametro so, o epsilon, pelo g_exp.
     - a forma (D-PE4-1): so a marca { luta: true, eps: true } liga; um ovo com { luta: true } (os saves da PE3) segue com o epsilon de hoje;
     - T-PL-4: com g_exp = e0 o epsilon e o de hoje; o epsilon lido e o da ultima decisao do modular; o replay sai bit a bit, com o modular,
       com o A e com um "cb" no meio;
     - 3.7: com o A ativo, o epsilon e o de hoje; nenhuma decisao nova nem rng do modular na leitura. */
import { describe, expect, test } from "vitest";
import { Motor, estiloDoPet, petDeTeste, type EventoRegistro } from "../motor/index.ts";
import { SEMENTES, VARIANTES, nascer, refazer, sha256, viverComLutas } from "./ponte_luta_pe0.ts";

const E0 = 512;
type Mut = { afeto: { g_exp: number } };

describe("PE4: o epsilon da luta pelo g_exp", () => {
  for (const v of VARIANTES) for (const s of SEMENTES) {
    test(`${v} @${s}: a vida com a marca eps refaz bit a bit (T-PL-4)`, () => {
      const vida = viverComLutas(v, s, 2, "eps");
      expect(vida.log.find(e => e[1] === "pl")![2]).toEqual({ luta: true, eps: true });
      expect(vida.lutas.length).toBeGreaterThan(5);
      const r = refazer(vida);
      expect(r.lutas).toEqual(vida.lutas.map(l => ({ evento: l.evento, gambits: l.gambits, confianca: l.confianca, modular: l.modular })));
      expect(sha256(r.m.assinatura())).toBe(vida.assinatura);
      expect(r.m.epsLuta).toBe(true);
      expect(Motor.reproduzir(s, vida.log, vida.versao).assinatura()).toBe(r.m.assinatura());
    });
  }

  test("sem a marca eps ({ luta: true }) o epsilon e o de hoje, mesmo com o g_exp longe de e0", () => {
    for (const v of ["v16", "v17_modular"] as const) {
      const m = nascer(v, 101, true);
      m.avancar(60);
      expect(m.epsLuta).toBe(false);
      expect(m.fatorEpsLuta()).toBeNull();
    }
  });

  test("T-PL-4: g_exp = e0 deixa o epsilon de hoje; fora de e0 ele escala e corta em 1; o valor lido e o da ultima decisao", () => {
    for (const v of ["v16", "v17_modular"] as const) {
      const m = nascer(v, 202, "eps");
      m.avancar(300);
      const lab = m.lab!;
      const mot = lab.ultimoMotivo as unknown as Mut | null;
      expect(mot, `${v}: o modular ja decidiu`).not.toBeNull();
      const hoje = (): number => { m.epsLuta = false; const e = estiloDoPet(m).eps; m.epsLuta = true; return e; };
      const antes = lab.estadoInterno();
      const base = hoje();
      mot!.afeto.g_exp = E0;
      expect(estiloDoPet(m).eps).toBe(base);
      mot!.afeto.g_exp = 256;
      expect(estiloDoPet(m).eps).toBe(Math.min(1, base * .5));
      mot!.afeto.g_exp = 1024;
      expect(estiloDoPet(m).eps).toBe(Math.min(1, base * 2));
      expect(m.fatorEpsLuta()).toBe(2);
      expect(lab.estadoInterno(), "a leitura nao mexe no modular").toEqual(antes);
      m.avancar(60);                                    // uma decisao nova: o epsilon passa a ler a dela
      const nova = lab.ultimoMotivo as unknown as Mut;
      expect(m.fatorEpsLuta()).toBe(nova.afeto.g_exp / E0);
    }
  });

  test("3.7: com o A ativo o epsilon e o de hoje (o g_exp do modular parado nao vale)", () => {
    const m = nascer("v17_modular", 303, "eps");
    m.avancar(300);
    expect(m.fatorEpsLuta()).not.toBeNull();
    m.trocarCerebro("a");
    expect(m.cerebroAtual).toBe("a");
    expect(m.fatorEpsLuta()).toBeNull();
    const hoje = estiloDoPet(m).eps;
    m.epsLuta = false;
    expect(estiloDoPet(m).eps).toBe(hoje);
  });

  test("a marca: { luta, eps } so com eps verdadeiro e uma vez; o log do produto do jogo leva a marca eps", () => {
    expect(() => new Motor(101, 17).aplicarEvento([480, "pl", { luta: true, eps: false }] as unknown as EventoRegistro)).toThrow(/inválida/);
    expect(() => new Motor(101, 17).aplicarEvento([480, "pl", { eps: true }] as unknown as EventoRegistro)).toThrow(/inválida/);
    const m = nascer("v17_modular", 101, "eps");
    expect(() => m.ligarPonteLuta(true)).toThrow(/uma vez/);
    expect(petDeTeste(101).epsLuta).toBe(false);
  });
});
