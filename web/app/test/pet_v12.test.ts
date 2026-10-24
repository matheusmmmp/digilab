/* Os pets v12 no Motor (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 1; MV-1): o v11 com o mundo fisico. O laco e o do G-PAR
   (test/mvp_mundo.test.ts); aqui, o que o jogo grava e refaz:
     - G1: a vida do v12 se refaz do registro, bit a bit (a assinatura, com o mundo, a cada evento e no fim; pelo replay e pelo save);
     - G-EVENTO: o "dc" invalido falha alto (fora do mapa, nao inteiro, tipo que nao e racao, malformado, num pet anterior ao v12) e o
       evento desconhecido tambem;
     - o laco jogavel: o dono deixa a racao, o pet a ve, anda ate ela e come por iniciativa propria, e a fome cai pelo corpo (o mesmo efeito
       do alimentar de hoje, MV-9); o botao Alimentar poe a racao no comedouro (a reserva temporaria);
     - o carinho e o tapa ficam fora do mundo (MV-7) e o v12 nao tem elogio nem bronca, como o v11. */
import { describe, expect, test } from "vitest";
import { TPD, VERSAO_PET } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import type { AcaoDono, EventoRegistro } from "../motor/tipos.ts";

/** o dono do jogo com o mundo: cuida pelo botao (o Alimentar poe a racao no comedouro) ou deixa a racao perto do pet, faz carinho e
 *  um tapa de vez em quando */
function viverV12(m: Motor, dias: number, perto: boolean): void {
  const passos = Math.round(dias * TPD / 30);
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e, mu = m.mundo!;
    if (e.fome < .6 && p % 2 === 0) {
      if (perto) m.deixarComida("racao", Math.min(1023, mu.pet[0] + 24), mu.pet[1]);
      else m.observar("alimentar");
    }
    if (e.sujeira >= 2) m.observar("limpar");
    if (p % 5 === 0) m.observar("acariciar");
    if (p % 11 === 10) m.observar("tapa" as AcaoDono);
  }
}

describe("o pet v12 no Motor", () => {
  test("o ovo novo e v12: o laco com o mundo, o corpo com a curiosidade e o cerebro A do v11", () => {
    expect(VERSAO_PET).toBe(12);
    const m = new Motor(4242);
    expect(m.versao).toBe(12);
    expect(m.v11!.laco).toBeInstanceOf(MotorCorpoMundo);
    expect(m.mundo).not.toBeNull();
    expect(m.cerebro).not.toBeNull();
    expect("curiosidade" in m.observacaoAgora().corpo!).toBe(true);
    expect(new Motor(4242, 11).mundo).toBeNull();
    expect("curiosidade" in new Motor(4242, 11).observacaoAgora().corpo!).toBe(false);
    for (const a of ["elogiar", "repreender", "petisco", "levar_ao_banheiro"] as AcaoDono[]) expect(() => m.observar(a)).toThrow(/v11/);
  });

  test("o botao Alimentar poe a racao no comedouro (o evento \"dc\"), e a fome nao sobe na hora: so quando o pet come", () => {
    const m = new Motor(101);
    m.avancar(30);
    const fome = m.e.fome, [x, y] = m.mundo!.comedouro;
    m.observar("alimentar");
    expect(m.log[m.log.length - 1]).toEqual([m.e.tick, "dc", { tipo: "racao", x, y }]);
    expect(m.e.fome).toBe(fome);
    expect(m.e.ultimoCuidado).toBe(m.e.tick);
    /* o id segue o das frutas que ja cairam: o relogio do mundo e o do pet, que nasce no tick 480 (o mundo anda desde o 0) */
    expect(m.mundo!.deixadas).toEqual([{ tick: m.e.tick, id: expect.any(Number), tipo: "racao", x, y, pet: [...m.mundo!.pet] }]);
    expect(m.mundo!.comidas.get(m.mundo!.deixadas[0].id as number)).toMatchObject({ tipo: "racao", x, y, origem: "dono" });
  });

  for (const [semente, perto] of [[101, true], [202, false], [303, true]] as const) {
    test(`v12 @${semente} (${perto ? "a racao perto do pet" : "o botao Alimentar"}): o pet ve, anda, come, a fome cai, e o G1 bit a bit`, () => {
      const m = new Motor(semente);
      viverV12(m, 4, perto);
      const mu = m.mundo!;
      /* o laco: a racao do dono vista, andada e comida por iniciativa do pet, e o corpo com o efeito do alimentar */
      const doDono = mu.consumos.filter((c) => c.origem === "dono" && c.situacao === "madura");
      expect(doDono.length).toBeGreaterThan(0);
      expect(doDono.every((c) => (c.fome_depois as number) > (c.fome_antes as number))).toBe(true);
      expect(mu.decisoes.some((d) => (d.deslocamento as number) > 0)).toBe(true);
      expect(mu.decisoes.some((d) => d.comeu !== null)).toBe(true);
      /* G1: o replay do registro, evento a evento, e pelo caminho publico e pelo save (o JSON do registro) */
      const r = new Motor(semente, 12);
      for (const ev of m.log) r.aplicarEvento(ev);
      expect(r.assinatura()).toBe(m.assinatura());
      const log = JSON.parse(JSON.stringify(m.log)) as EventoRegistro[];
      expect(Motor.reproduzir(semente, log, 12).assinatura()).toBe(m.assinatura());
      expect(JSON.stringify(Motor.reproduzir(semente, log, 12).mundo!.resumo())).toBe(JSON.stringify(mu.resumo()));
    });
  }

  test("G1: o replay incremental passa pelos mesmos estados (a assinatura com o mundo depois de cada evento)", () => {
    const m = new Motor(404), passos: string[] = [];
    viverV12(m, 2, true);
    const r = new Motor(404, 12);
    for (const ev of m.log) { r.aplicarEvento(ev); passos.push(r.assinatura()); }
    const s = new Motor(404, 12);
    m.log.forEach((ev, i) => { s.aplicarEvento(ev); expect(s.assinatura(), `evento ${i}`).toBe(passos[i]); });
    expect(passos[passos.length - 1]).toBe(m.assinatura());
  });

  test("G-EVENTO: o deixar_comida invalido falha alto antes do registro", () => {
    const m = new Motor(505);
    m.avancar(30);
    const n = m.log.length, antes = m.assinatura();
    expect(() => m.deixarComida("a", 100, 100)).toThrow(/MV-3/);
    expect(() => m.deixarComida("pizza", 100, 100)).toThrow(/MV-3/);
    expect(() => m.deixarComida("racao", 1024, 100)).toThrow(/fora do mapa/);
    expect(() => m.deixarComida("racao", 100, 480)).toThrow(/fora do mapa/);
    expect(() => m.deixarComida("racao", -1, 100)).toThrow(/fora do mapa/);
    expect(() => m.deixarComida("racao", 10.5, 100)).toThrow(/nao inteira/);
    expect(() => m.deixarComida("racao", Number.NaN, 100)).toThrow(/nao inteira/);
    expect(m.log.length).toBe(n);
    expect(m.assinatura()).toBe(antes);
    expect(() => new Motor(505, 11).deixarComida("racao", 100, 100)).toThrow(/v12/);
  });

  test("G-EVENTO: o \"dc\" malformado ou fora do v12 no registro falha alto, e o evento desconhecido tambem", () => {
    const t = 480;
    const ruins: unknown[] = [
      [t, "dc", { tipo: "a", x: 100, y: 100 }], [t, "dc", { tipo: "racao", x: 100 }], [t, "dc", { tipo: "racao", x: 100, y: 100, z: 1 }],
      [t, "dc", { tipo: "racao", x: "100", y: 100 }], [t, "dc", { tipo: "racao", x: 2000, y: 100 }], [t, "dc", null], [t, "dc", "racao|1|2"],
    ];
    for (const ev of ruins) expect(() => Motor.reproduzir(1, [ev as EventoRegistro], 12), JSON.stringify(ev)).toThrow();
    expect(() => Motor.reproduzir(1, [[t, "dc", { tipo: "racao", x: 100, y: 100 }]], 11)).toThrow(/v12/);
    expect(() => Motor.reproduzir(1, [[t, "zz", 1] as unknown as EventoRegistro], 12)).toThrow(/desconhecido/);
    expect(Motor.reproduzir(1, [[t, "dc", { tipo: "racao", x: 100, y: 100 }]], 12).mundo!.comidas.size).toBe(1);
  });

  test("MV-7: o carinho e o tapa ficam fora do mundo (sem posicao do dono): o mundo nao muda, so o corpo e o cerebro", () => {
    const m = new Motor(606);
    m.avancar(60);
    const mundo = JSON.stringify(m.mundo!.resumo());
    m.observar("acariciar");
    m.observar("tapa" as AcaoDono);
    expect(JSON.stringify(m.mundo!.resumo())).toBe(mundo);
    expect(m.log.slice(-2)).toEqual([[m.e.tick, "d", "acariciar"], [m.e.tick, "d", "tapa"]]);
  });
});
