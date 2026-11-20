/* O Motor do jogo dentro do Grupo (docs/TAREFA_V3_COOPERACAO.md, etapa CO4b; motor/grupo_jogo.ts):
   - dois Motors inteiros (v26, CO4c) na ilha com agua, o tempo andando pelo grupo, um tick por vez na vez sorteada;
   - o mundo e um so: a racao que o dono deixa por um pet pode ser comida pelo outro, e as comidas, a bola e as quedas sao as mesmas;
   - cada pet tem a percepcao do outro, os contatos e os chamados dele;
   - o G-REPLAY-2 no motor: o registro do grupo refeito da a mesma assinatura, e um evento desconhecido, fora do tick ou de um pet de fora falha
     alto;
   - o avancar de um pet do grupo anda o grupo inteiro (CO4c), e a acao do dono com o tempo dentro entra no registro na ordem certa;
   - a v26 so existe no grupo, e o grupo so tem a v26; o pet sozinho de hoje nao muda (o G-HOJE segue nos testes de cada versao). */
import { describe, expect, test } from "vitest";
import { TICK_INICIAL, TPD } from "../motor/constantes.ts";
import { GrupoDoJogo, Motor, derivarSemente, sementeDoSegundoJogo, type EventoGrupoJogo } from "../motor/index.ts";

const VERSAO = 26;

/** o dono de roteiro: a cada passo de 15 ticks, a racao a um pet (alternando), o carinho no outro de vez em quando e a limpeza */
function viver(semente: number, passos: number): GrupoDoJogo {
  const g = new GrupoDoJogo(semente, VERSAO);
  for (let k = 0; k < passos; k++) {
    g.avancar(15);
    const quem = Math.floor(k / 8) % 2 === 0 ? "A" : "B", outro = quem === "A" ? "B" : "A";
    if (k % 8 === 0) g.agir(quem, m => m.observar("alimentar"));
    if (k % 12 === 5) g.agir(outro, m => m.observar("acariciar"));
    if (k % 20 === 9) g.agir(quem, m => m.observar("limpar"));
  }
  return g;
}

describe("o Motor do jogo dentro do Grupo", () => {
  const g = viver(101, 2 * TPD / 15);

  test("os dois pets nascem juntos, com as sementes do grupo, e andam no relogio do mundo", () => {
    const [a, b] = [g.motor("A"), g.motor("B")];
    expect(a.semente).toBe(101);
    expect(b.semente).toBe(sementeDoSegundoJogo(101));
    expect(b.semente).toBe(Number(derivarSemente("segundo-pet", 101) & 0xffffffffn));
    expect(Number.isInteger(b.semente) && b.semente >= 0 && b.semente <= 0xffffffff).toBe(true);
    expect(g.tick).toBe(TICK_INICIAL + 2 * TPD);
    expect([a.e.tick, b.e.tick]).toEqual([g.tick, g.tick]);
    expect(a.noGrupo && b.noGrupo).toBe(true);
  });

  test("o mundo e um so: a racao deixada por um pet alimenta os dois, e as comidas sao as mesmas", () => {
    const [a, b] = [g.motor("A").mundo!, g.motor("B").mundo!];
    expect(a.comum).toBe(b.comum);
    expect(a.comidas).toBe(b.comidas);
    const deixadasPorA = new Set(a.deixadas.map(d => d.id as number)), deixadasPorB = new Set(b.deixadas.map(d => d.id as number));
    expect(deixadasPorA.size > 0 && deixadasPorB.size > 0).toBe(true);
    const comeuDoOutro = b.consumos.some(c => deixadasPorA.has(c.id as number)) || a.consumos.some(c => deixadasPorB.has(c.id as number));
    expect(comeuDoOutro).toBe(true);
    expect(a.consumos.length > 0 && b.consumos.length > 0).toBe(true);
  });

  test("a vez sorteada, a percepcao do outro e o toque", () => {
    expect(g.grupo.ordens.length).toBeGreaterThan(0);
    expect(g.grupo.ordens.every(o => o.decidem.length === 2)).toBe(true);
    expect(g.grupo.contatos.length).toBeGreaterThan(0);
    const a = g.motor("A").mundo!;
    expect(a.decisoesNoGrupo).toBeGreaterThan(0);
    expect(Object.keys(a.aVista)).toEqual(["B"]);
  });

  test("cada pet tem os chamados dele", () => {
    const abertos = (m: Motor) => m.chamadosAbertos().length;
    expect(typeof abertos(g.motor("A"))).toBe("number");
    expect(g.motor("A").chamados).not.toBe(g.motor("B").chamados);
  });

  test("o G-REPLAY-2: o registro refeito da a mesma assinatura, e o determinismo", () => {
    const r = GrupoDoJogo.reproduzir(101, VERSAO, g.log);
    expect(r.assinatura()).toBe(g.assinatura());
    expect(viver(101, 2 * TPD / 15).assinatura()).toBe(g.assinatura());
    expect(viver(202, 2 * TPD / 15).assinatura()).not.toBe(g.assinatura());
    expect(g.log.some(e => e[3] === "A") && g.log.some(e => e[3] === "B") && g.log.some(e => e[3] === null)).toBe(true);
    /* o registro de cada pet e a projecao do do grupo (o avanco do grupo, e os eventos dele) */
    for (const i of g.ids) {
      const proj: unknown[] = [];
      for (const [t, tipo, valor, pet] of g.log) {
        if (pet !== null && pet !== i) continue;
        const u = proj[proj.length - 1] as [number, string, number] | undefined;
        if (pet === null && u && u[1] === "t" && u[0] + u[2] === t) u[2] += valor as number; else proj.push([t, tipo, valor]);
      }
      expect(JSON.parse(JSON.stringify(g.motor(i).log))).toEqual(JSON.parse(JSON.stringify(proj)));
    }
  });

  test("o G-REPLAY-2: o que o replay recusa", () => {
    const log = g.log.map(e => [...e] as EventoGrupoJogo);
    const i = log.findIndex(e => e[3] !== null);
    const com = (f: (l: EventoGrupoJogo[]) => void) => { const l = log.map(e => [...e] as EventoGrupoJogo); f(l); return l; };
    expect(() => GrupoDoJogo.reproduzir(101, VERSAO, com(l => { l[i] = [l[i][0], "zz", 1, l[i][3]]; }))).toThrow();
    expect(() => GrupoDoJogo.reproduzir(101, VERSAO, com(l => { l[i] = [l[i][0], l[i][1], l[i][2], "C"]; }))).toThrow(/fora do grupo/);
    expect(() => GrupoDoJogo.reproduzir(101, VERSAO, com(l => { l[i] = [l[i][0] + 1, l[i][1], l[i][2], l[i][3]]; }))).toThrow(/tick/);
    expect(() => GrupoDoJogo.reproduzir(101, VERSAO, com(l => { l[0] = [l[0][0], "d", "acariciar", null]; }))).toThrow(/sem pet/);
    expect(() => GrupoDoJogo.reproduzir(101, VERSAO, com(l => { l.splice(i, 0, [l[i][0], "t", 5, "A"]); }))).toThrow(/avanco com pet/);
  });

  test("o avancar de um pet anda o grupo, e a acao com o tempo dentro entra na ordem (o relogio do jogo pelo mudarMotor, CO4c)", () => {
    const h = new GrupoDoJogo(303, VERSAO), t0 = h.tick;
    h.motor("B").avancar(15);
    expect([h.tick, h.motor("A").e.tick, h.motor("B").e.tick]).toEqual([t0 + 15, t0 + 15, t0 + 15]);
    expect(h.log).toEqual([[t0, "t", 15, null]]);
    h.agir("A", m => { m.observar("acariciar"); m.avancar(15); m.observar("limpar"); });
    expect(h.log.map(e => [e[0] - t0, e[1], e[3]])).toEqual([[0, "t", null], [15, "d", "A"], [15, "t", null], [30, "d", "A"]]);
    expect(GrupoDoJogo.reproduzir(303, VERSAO, h.log).assinatura()).toBe(h.assinatura());
    expect(() => h.agir("A", () => h.agir("B", () => 0))).toThrow(/dentro de outra/);
    expect(() => g.grupo.acaoDono("A", "acariciar")).toThrow(/pelo Motor/);
  });

  test("a v26 so existe no grupo, e o grupo so tem a v26; o pet sozinho de hoje anda como sempre", () => {
    expect(() => new Motor(101, VERSAO)).toThrow(/so nasce no grupo/);
    expect(() => new GrupoDoJogo(101, 23)).toThrow(/v26/);
    const so = new Motor(101, 23);
    expect(so.noGrupo).toBe(false);
    so.avancar(30);
    expect(so.e.tick).toBe(TICK_INICIAL + 30);
  });
});
