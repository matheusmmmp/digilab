/* PE3 da ponte da luta (docs/TAREFA_V3_PONTE_LUTA.md, 3.5 e 3.7): o espelho TS da dor no corpo (PE1) e da luta como episodio no M-MEM (PE2).
   Desde a LP4 da LUTA_POC, na luta da POC dos pets v21 (o pet de teste v16 nao luta mais).
     - G1: a vida com a marca "pl" (v21 modular, v21 A e v21 com um "cb" no meio), com luta, refaz bit a bit no replay;
     - a dor da luta e exata (div_arred(p x C, S), p a vida perdida em S, cortada em [0, S]) e vale com qualquer cerebro (PL-9);
     - o episodio `luta` so existe com o modular ativo: o A ativo nao guarda nada para o modular parado (3.7);
     - sem a marca, nada muda; a marca so vale nos pets com o cerebro trocavel (a v21) e no pet de teste, uma vez, no comeco; a marca com eps
       (a PE4: o epsilon da luta por turnos pelo g_exp, que saiu com ela) ainda e lida e fica na assinatura;
     - o G-PAR do corpo e do M-MEM contra o Python esta em digibrain_modular_vida.test.ts. */
import { describe, expect, test } from "vitest";
import { Motor, VERSAO_PET_LAB, petDeTeste, type EventoRegistro } from "../motor/index.ts";
import { ligarProduto } from "../src/produto.ts";
import { divArred } from "../motor/mundo.ts";
import type { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { SEMENTES, VARIANTES, nascer, refazer, sha256, viverComLutas } from "./ponte_luta_pe0.ts";

/** as dores de cada resumo de uma vida: o motor refeito com um espiao no estimulo da luta */
function espiar(m: Motor): { v: number; antes: number; depois: number }[] {
  const laco = m.v11!.laco as MotorCorpoMundo, out: { v: number; antes: number; depois: number }[] = [];
  const original = laco.corpo.estimuloLuta.bind(laco.corpo);
  laco.corpo.estimuloLuta = (v: number) => { const antes = laco.corpo.q["dor"]!; original(v); out.push({ v, antes, depois: laco.corpo.q["dor"]! }); };
  return out;
}

describe("PE3: a vida com a marca da ponte da luta", () => {
  for (const v of VARIANTES) for (const s of SEMENTES) {
    test(`${v} @${s}: luta com a marca e o replay sai bit a bit (G1)`, () => {
      const vida = viverComLutas(v, s, 2, true);
      expect(vida.log.some(e => e[1] === "pl")).toBe(true);
      expect(vida.lutas.length).toBeGreaterThan(5);
      const r = refazer(vida);
      expect(r.lutas).toEqual(vida.lutas.map(l => ({ evento: l.evento, confianca: l.confianca, modular: l.modular })));
      expect(sha256(r.m.assinatura())).toBe(vida.assinatura);
      expect(r.m.ponteLuta).toBe(true);
      expect(Motor.reproduzir(s, vida.log, vida.versao).assinatura(), "pelo caminho publico do replay").toBe(r.m.assinatura());
    });
  }

  test("a dor de cada luta e exata e vale com qualquer cerebro; o episodio luta so com o modular ativo", () => {
    let comDor = 0, episodiosModular = 0;
    for (const v of VARIANTES) for (const s of SEMENTES) {
      const vida = viverComLutas(v, s, 2, true);
      const m = new Motor(s);
      const dores = espiar(m);
      for (const ev of vida.log) m.aplicarEvento(ev);
      const laco = m.v11!.laco as MotorCorpoMundo, C = laco.corpo.C, S = laco.corpo.S;
      expect(dores.length, `${v}@${s}: um estimulo por luta da serie`).toBe(vida.lutas.reduce((n, l) => n + l.lutas.length, 0));
      for (const d of dores) {
        expect(d.v).toBeGreaterThanOrEqual(0);
        expect(d.depois).toBe(Math.min(C, d.antes + divArred(Math.min(d.v, S) * C, S)));      // a dor sobe exatamente, cortada no teto do corpo
        if (d.v > 0) comDor++;
      }
      const eps = m.lab ? m.lab.mem.guardados().filter(e => e.origem === "luta") : [];
      if (v === "v21_a") expect(m.lab, "o modular nao decide").toBeNull();
      episodiosModular += eps.length;
      eps.forEach(e => { expect(e.outro).toBe(e.classe); expect(e.acao[0]).toBe("lutar"); });
    }
    expect(comDor, "alguma luta tirou vida").toBeGreaterThan(0);
    expect(episodiosModular, "o modular guardou lutas").toBeGreaterThan(0);
  });

  test("com o A ativo o modular parado nao recebe a luta; ao voltar, continua dali (3.7)", () => {
    const vida = viverComLutas("v21_cb", 101, 2, true);
    const m = new Motor(101), entregues: number[] = [];
    const vistos = new WeakSet<object>();
    let doModular = 0, doA = 0;
    for (const ev of vida.log) {
      if (ev[1] === "l" && m.lab && !vistos.has(m.lab)) {            // um espiao no gancho do modular, uma vez
        const lab = m.lab, original = lab.receberLuta.bind(lab);
        lab.receberLuta = (...a: Parameters<typeof original>) => { entregues.push(m.e.tick); original(...a); };
        vistos.add(lab);
      }
      const antes = entregues.length, serieAntes = m.lutas.lutas;
      const ativo = m.cerebroAtual;
      m.aplicarEvento(ev);
      if (ev[1] === "l") {
        const n = m.lutas.lutas - serieAntes;                          // as lutas da serie
        if (ativo === "modular") doModular += n; else doA += n;
        expect(entregues.length - antes, `${ativo}: o modular recebe uma por luta da serie, o A nenhuma`).toBe(ativo === "modular" ? n : 0);
      }
    }
    expect(doA, "houve luta com o A ativo").toBeGreaterThan(0);
    expect(doModular, "houve luta com o modular ativo").toBeGreaterThan(0);
    expect(entregues.length).toBe(doModular);
    expect(m.lab!.mem.guardados().filter(e => e.origem === "luta").length).toBeLessThanOrEqual(doModular);
  });

  test("a marca: uma vez, no comeco; sem ela a luta passa ao lado do corpo", () => {
    const m = nascer("v21_modular", 101, true);
    expect(() => m.ligarPonteLuta()).toThrow(/uma vez/);
    const tarde = nascer("v21_modular", 202);
    tarde.avancar(30);
    expect(() => tarde.ligarPonteLuta()).toThrow(/comeco|começo/);
    expect(() => new Motor(101).aplicarEvento([480, "pl", { luta: false }] as unknown as EventoRegistro)).toThrow(/inválida/);
    expect(() => new Motor(101).aplicarEvento([480, "pl", { luta: true, x: 1 }] as unknown as EventoRegistro)).toThrow(/inválida/);
    const sem = nascer("v21_modular", 303);
    expect(sem.ponteLuta).toBe(false);
    expect(m.ponteLuta).toBe(true);
    expect(m.assinatura()).not.toBe(nascer("v21_modular", 101).assinatura());
    expect(VERSAO_PET_LAB).toBe(16);
  });

  test("a marca com eps (a PE4): so com eps verdadeiro e uma vez; o ovo do jogo a grava, e ela fica na assinatura", () => {
    expect(() => new Motor(101).aplicarEvento([480, "pl", { luta: true, eps: false }] as unknown as EventoRegistro)).toThrow(/inválida/);
    expect(() => new Motor(101).aplicarEvento([480, "pl", { eps: true }] as unknown as EventoRegistro)).toThrow(/inválida/);
    const m = nascer("v21_modular", 101, "eps");
    expect(() => m.ligarPonteLuta(true)).toThrow(/uma vez/);
    expect(m.epsLuta).toBe(true);
    expect(m.assinatura()).not.toBe(nascer("v21_modular", 101, true).assinatura());
    expect(petDeTeste(101).epsLuta).toBe(false);
    expect(ligarProduto(new Motor(101)).log.find(ev => ev[1] === "pl")?.[2]).toEqual({ luta: true, eps: true });
  });

  test("o corpo e o modular sem a chave levantam erro (G2: a vida de hoje nao os usa)", () => {
    const m = nascer("v21_modular", 101);
    const laco = m.v11!.laco as MotorCorpoMundo;
    expect(() => laco.corpo.estimuloLuta(300)).toThrow(/ConfigLutaCorpo/);
    expect(() => laco.aplicarResumoLuta("muralha", -1, 300)).toThrow(/ConfigLutaCorpo/);
    expect(() => m.lab!.receberLuta("muralha", -1, 300, 480)).toThrow(/luta_memoria/);
  });
});
