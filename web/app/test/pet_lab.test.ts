/* O pet de teste do laboratorio (docs/TAREFA_V3_LAB_MODULAR.md, LM4; LAB-2 e LAB-3): a v16, a v14 com o DigiBrain modular no lugar do cerebro A.
     - a fabrica (motor/pet_lab.ts) e a unica porta da v16: o ovo padrao segue v14 e a lista das versoes que abrem nao muda;
     - o cerebro e o modular (o laco com a chave do laboratorio), o resto e o da v14 (o mundo do produto, as regras de luta do candidato v14);
     - G1: a vida da v16 se refaz do registro, bit a bit (a assinatura, com o estado do modular, a cada evento e no fim; pelo replay e pelo save);
     - o pet decide de verdade pelo modular (motivos por modulo), come a racao posta e lembra o lugar. */
import { describe, expect, test } from "vitest";
import { CMU_MVP, TPD, VERSAO_PET, VERSAO_PET_LAB, VERSOES_PET } from "../motor/constantes.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import { Motor } from "../motor/motor.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { petDeTeste, petDeTesteDoRegistro } from "../motor/pet_lab.ts";
import type { AcaoDono, EventoRegistro } from "../motor/tipos.ts";

/** o dono do jogo com o mundo: deixa a racao perto ou longe do pet quando ele tem fome, limpa, faz carinho e um tapa de vez em quando */
function viver(m: Motor, dias: number, longe: boolean): void {
  const passos = Math.round(dias * TPD / 30);
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e, mu = m.mundo!;
    if (e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + (longe ? 300 : 24))), mu.pet[1]);
    if (e.sujeira >= 2) m.observar("limpar");
    if (p % 5 === 0) m.observar("acariciar");
    if (p % 11 === 10) m.observar("tapa" as AcaoDono);
  }
}

describe("o pet de teste do laboratorio (v16)", () => {
  test("a fabrica e a unica porta: o ovo padrao segue o padrao (a v15 do PR #525) e as versoes que abrem nao incluem o pet de teste", () => {
    expect(VERSAO_PET).toBe(23);
    expect(VERSOES_PET).toEqual([21, 22, 23]);
    expect(VERSAO_PET_LAB).toBe(16);
    expect(new Motor(101, 21).versao).toBe(21);
    expect(new Motor(101, 21).lab).toBeNull();
    const p = petDeTeste(101);
    expect(p.versao).toBe(16);
    expect(p.lab).toBeInstanceOf(DigiBrain);
    expect(p.v11!.laco).toBeInstanceOf(MotorCorpoMundo);
    expect(p.mundo!.cm).toBe(CMU_MVP);
    expect(p.mundo!.bolaNoGolpe).toBe(false);     // a v14 com o modular: a bola de antes
    expect(() => new Motor(101, 20)).toThrow(/versão de pet desconhecida/);
  });

  /* PROPOSTA da LP4 da LUTA_POC: o pet de teste lutava pelo combate por turnos (as regras do candidato v14), que saiu; ele nao luta mais, e
     um registro dele com luta ("l"), regras ("g") ou carta ("k") nao abre */
  test("o pet de teste nao luta (desde a LP4): a luta e os eventos dela falham alto", () => {
    const m = petDeTeste(101);
    m.liberar(6);
    while (m.estagioAtual === "bebe") m.avancar(60);
    expect(m.porqueNaoLutaPoc(m.rivaisArenaPoc()[0], "campo")).toMatch(/pet de teste/);
    expect(() => m.lutarPoc(m.rivaisArenaPoc()[0], 1, "campo")).toThrow(/pet de teste/);
    for (const ev of [[m.e.tick, "l", { r: "aleatorio", s: 1 }], [m.e.tick, "g", { op: "travar", k: "x" }], [m.e.tick, "k", { id: "carta_foco" }]])
      expect(() => petDeTesteDoRegistro(101, [...JSON.parse(JSON.stringify(m.log)), ev] as EventoRegistro[])).toThrow();
  });

  for (const [semente, longe] of [[101, false], [202, true], [303, false]] as const) {
    test(`v16 @${semente} (${longe ? "a racao longe" : "a racao perto"}): decide pelo modular, come, e o G1 bit a bit (replay e save)`, () => {
      const m = petDeTeste(semente);
      viver(m, 4, longe);
      const motivos = m.lab!.motivos;
      expect(motivos.length).toBe(4 * TPD / 15);
      expect(motivos.every((x) => Array.isArray(x.unidades) && x.afeto && x.estado && x.sondas)).toBe(true);
      expect(m.mundo!.consumos.some((c) => c.origem === "dono" && c.situacao === "madura")).toBe(true);
      expect(new Set(motivos.map((x) => x.acao)).size).toBeGreaterThan(2);
      expect(motivos.some((x) => (x.consequencia?.p1 ?? null) !== null)).toBe(true);
      /* G1: o replay do registro, evento a evento, e pelo caminho publico e pelo save (o JSON do registro) */
      const r = new Motor(semente, VERSAO_PET_LAB);
      for (const ev of m.log) r.aplicarEvento(ev);
      expect(r.assinatura()).toBe(m.assinatura());
      expect(JSON.stringify(r.lab!.estadoInterno())).toBe(JSON.stringify(m.lab!.estadoInterno()));
      const log = JSON.parse(JSON.stringify(m.log)) as EventoRegistro[];
      const refeito = petDeTesteDoRegistro(semente, log);
      expect(refeito.assinatura()).toBe(m.assinatura());
      expect(JSON.stringify(refeito.lab!.estadoInterno())).toBe(JSON.stringify(m.lab!.estadoInterno()));
      expect(JSON.stringify(refeito.mundo!.resumo())).toBe(JSON.stringify(m.mundo!.resumo()));
    });
  }

  test("G1: o replay incremental passa pelos mesmos estados (a assinatura depois de cada evento)", () => {
    const m = petDeTeste(404), passos: string[] = [];
    viver(m, 2, true);
    const r = petDeTeste(404);
    for (const ev of m.log) { r.aplicarEvento(ev); passos.push(r.assinatura()); }
    const s = petDeTeste(404);
    m.log.forEach((ev, i) => { s.aplicarEvento(ev); expect(s.assinatura(), `evento ${i}`).toBe(passos[i]); });
    expect(passos[passos.length - 1]).toBe(m.assinatura());
  });

  test("o ovo padrao nao traz o laboratorio na assinatura, e o pet v16 traz", () => {
    const a = new Motor(101, 21);
    a.avancar(60);
    expect(a.assinatura()).not.toContain('"lab"');
    const b = petDeTeste(101);
    b.avancar(60);
    expect(b.assinatura()).toContain('"lab"');
  });
});
