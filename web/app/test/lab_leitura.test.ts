/* A leitura do painel do modular (motor/digibrain/leitura.ts, LM5b): numeros inteiros do motivo do pet de teste, sem conta na tela. */
import { describe, expect, test } from "vitest";
import { TPD } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import { petDeTeste } from "../motor/pet_lab.ts";

function viver(m: Motor, dias: number, longe: boolean): void {
  for (let p = 0; p < Math.round(dias * TPD / 30); p++) {
    m.avancar(30);
    const mu = m.mundo!;
    if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + (longe ? 300 : 24))), mu.pet[1]);
    if (m.e.sujeira >= 2) m.observar("limpar");
    if (p % 5 === 0) m.observar("acariciar");
  }
}

describe("leituraLab", () => {
  test("null no pet de hoje e antes da primeira decisao", () => {
    expect(new Motor(101).leituraLab()).toBeNull();
    expect(petDeTeste(101).leituraLab()).toBeNull();
  });
  test("cada decisao: barras nao nulas e ordenadas, chances somam ~1000, a escolhida sempre listada", () => {
    for (const [s, longe] of [[101, false], [202, true]] as const) {
      const m = petDeTeste(s);
      viver(m, 3, longe);
      let achouLembranca = false, achouIntencao = false, achouLugar = false;
      const k0 = m.lab!.motivos.length;
      for (let i = 0; i < 200; i++) {
        m.avancar(15);
        const l = m.leituraLab();
        if (l === null) continue;
        expect(l.k).toBe(m.lab!.motivos.length - 1);
        expect(l.barras.every(b => b.valor !== 0 && Math.abs(b.permil) <= 1000)).toBe(true);
        expect(l.barras.map(b => Math.abs(b.permil))).toEqual([...l.barras.map(b => Math.abs(b.permil))].sort((a, b) => b - a));
        expect(l.barras.length + l.zeradas.length).toBe(7);
        expect(l.chances.filter(c => c.escolhida).length).toBe(1);
        if (l.chances.length > 1) expect(Math.abs(l.chances.reduce((s2, c) => s2 + (c.permil ?? 0), 0) - 1000)).toBeLessThanOrEqual(l.chances.length);
        if (l.lembranca) achouLembranca = true;
        if (l.intencao) achouIntencao = true;
        if (l.alvo?.do_mem) achouLugar = true;
      }
      expect(m.lab!.motivos.length).toBeGreaterThan(k0);
      expect(achouIntencao).toBe(true);
      void achouLembranca; void achouLugar;
    }
  });
  test("a leitura nao muda o pet (a assinatura igual)", () => {
    const m = petDeTeste(303);
    viver(m, 2, false);
    const a = m.assinatura(), est = JSON.stringify(m.lab!.estadoInterno());
    m.leituraLab(); m.leituraLab();
    expect(m.assinatura()).toBe(a);
    expect(JSON.stringify(m.lab!.estadoInterno())).toBe(est);
  });
});
