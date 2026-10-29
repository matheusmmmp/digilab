// A luta em tempo real no Motor (COMBATE-TR, etapa R2; docs/ESPEC_COMBATE_TR.md, itens 3 e 4): os pets v13 lutam pelo nucleo combate_tr,
// tudo o que o resultado alimenta continua (o aprendizado pelo saldo de cada acao, os contadores, a lesao, a confianca, a historia), as
// series, a Liga e a Fabrica passam pelo mesmo nucleo, o replay refaz igual sem cache (D-2) e cabe no teto de custo; uma vida v13 sem luta
// e a vida v12 de hoje, bit a bit.
import { describe, expect, test } from "vitest";
import {
  CV21E_TR, DUR_EVO, LUTAS_SERIE_FABRICA, Motor, NOME_BOT, TentativaFabrica, VERSAO_FABRICA_TR, VERSAO_PET, hashSemente, jogarSerie,
  lutadorBot, lutadorPet, type EventoRegistro,
} from "../motor/index.ts";

/** um Rookie v13 que ja pode lutar (a medalha da evolucao conhecida, o In-Training passado) */
function rookie(semente: number): Motor {
  const m = new Motor(semente);
  m.liberar(1);
  m.avancar(DUR_EVO.bebe + 30);
  expect(m.estagioAtual).toBe("crianca");
  return m;
}
const luta = (m: Motor, rival = "aleatorio") => m.lutar(rival, hashSemente("teste-tr", m.semente, m.log.length));

describe("os pets v13 lutam em tempo real", () => {
  test("o ovo novo e v13, com as regras CV21E_TR; o Motor.lutar devolve a luta em tempo real", () => {
    expect(VERSAO_PET).toBe(13);
    const m = rookie(101);
    expect(m.versao).toBe(13); expect(m.regras).toBe(CV21E_TR);
    const r = luta(m);
    expect(r.res.tr).toBeDefined(); expect(r.res.turnos).toEqual([]);
    expect(r.res.tr!.passos).toBeGreaterThan(0);
    expect(r.res.pontosA).toBe(r.res.tr!.pontosA);
    /* o evento no registro e o "l" de sempre: so o rival e a semente */
    expect(m.log[m.log.length - 1]).toEqual([m.e.tick, "l", { r: "aleatorio", s: expect.any(Number) }]);
  });

  test("o aprendizado le o saldo de cada acao: as regras que dispararam mudam de nota, as outras nao", () => {
    const m = rookie(202), notas = { ...m.gp!.notas }, ativas = m.gp!.ativas.slice();
    const r = luta(m);
    expect(m.gp!.nLutas).toBe(1);
    const disparadas = new Set(r.res.tr!.acoes.filter(a => a.lado === 0 && typeof a.motivo === "number" && a.motivo < ativas.length)
      .map(a => ativas[a.motivo as number]));
    expect(disparadas.size).toBeGreaterThan(0);
    for (const k of ativas) {
      if (disparadas.has(k)) {
        /* a nota de antes, puxada para a media dos saldos da regra mais o bonus do resultado (GambitsPet.aprender) */
        const saldos = r.res.tr!.acoes.filter(a => a.lado === 0 && a.motivo === ativas.indexOf(k)).map(a => a.saldo);
        const media = saldos.reduce((s, x) => s + x, 0) / saldos.length, bonus = .1 * (r.res.pontosA - .5);
        /* a primeira luta contra o rival: a novidade (M1) e 1, e o passo e o GA.alfa de sempre */
        expect(m.gp!.notas[k]).toBeCloseTo(notas[k] + .2 * (media + bonus - notas[k]), 12);
        expect(m.gp!.disparos[k]).toBe(saldos.length);
      } else expect(m.gp!.notas[k]).toBe(notas[k]);
    }
  });

  test("os contadores, a lesao, a confianca, a vida5 e a historia contam a luta em tempo real", () => {
    const m = rookie(303);
    let v = 0, d = 0, e = 0, les = 0;
    for (let i = 0; i < 12 && !m.morte; i++) {
      const hist = m.historico.length, vida5 = m.vida5.lutas.length, r = luta(m);
      if (r.res.pontosA === 1) v++; else if (r.res.pontosA === 0) d++; else e++;
      if (r.lesao) les++;
      expect(m.vida5.lutas.length).toBe(vida5 + 1);
      expect(m.vida5.lutas.at(-1)).toMatchObject({ rival: "aleatorio", lesao: r.lesao });
      expect(m.historico.slice(hist).some(h => h.quem === "luta" && h.a.includes(NOME_BOT.aleatorio))).toBe(true);
    }
    expect(m.lutas).toMatchObject({ lutas: v + d + e, vitorias: v, derrotas: d, empates: e, lesoes: les });
    expect(m.conf!.assinatura()).not.toEqual(new Motor(303).conf!.assinatura());
  });

  test("o replay refaz a vida com lutas igual, bit a bit, sem cache (D-2)", () => {
    const m = rookie(404);
    for (let i = 0; i < 8; i++) luta(m, i % 2 ? "agressivo" : "aleatorio");
    const x = Motor.reproduzir(m.semente, m.log, m.versao);
    expect(x.assinatura()).toBe(m.assinatura());
    /* o montarLuta (a tela refaz as lutas do registro por ele) da a mesma luta */
    const k = m.log.findIndex(ev => ev[1] === "l"), ev = m.log[k] as EventoRegistro & [number, "l", { r: string; s: number }];
    const m0 = Motor.reproduzir(m.semente, m.log.slice(0, k), m.versao), a = m0.montarLuta(ev[2].r, ev[2].s).serie[0];
    const b = Motor.reproduzir(m.semente, m.log.slice(0, k), m.versao).montarLuta(ev[2].r, ev[2].s).serie[0];
    expect(JSON.stringify(a.tr!.acoes)).toBe(JSON.stringify(b.tr!.acoes));
  });

  test("o custo do replay: 1 000 lutas refeitas cabem no teto de 10 s no Node (espec, item 4)", () => {
    const m = rookie(505);
    for (let i = 0; i < 150 && !m.morte; i++) luta(m);
    const n = m.log.filter(ev => ev[1] === "l").length;
    expect(n).toBeGreaterThan(50);
    const t0 = performance.now();
    Motor.reproduzir(m.semente, m.log, m.versao);
    const msPorLuta = (performance.now() - t0) / n;
    /* o teto (PROPOSTO, SEM FONTE; espec D-2): 10 ms por luta, 10 s para 1 000 */
    expect(msPorLuta * 1000).toBeLessThan(10_000);
  });

  test("uma vida v13 sem luta e a vida v12, bit a bit (a luta em tempo real so muda as lutas)", () => {
    const viver = (m: Motor) => {
      for (let p = 0; p < 40; p++) {
        m.avancar(30);
        if (m.e.fome < .6) m.observar("alimentar");
        if (m.e.sujeira >= 2) m.observar("limpar");
        if (p % 5 === 0) m.observar("acariciar");
      }
      return m;
    };
    const a = viver(new Motor(606, 12)), b = viver(new Motor(606, 13));
    expect(b.log).toEqual(a.log);
    expect(b.assinatura()).toBe(a.assinatura());
  });
});

describe("as series, a Liga e a Fabrica passam pelo mesmo nucleo", () => {
  test("a serie sem cura (a Cidadela, a Liga): cada luta comeca com a vida e o guts do fim da anterior", () => {
    const m = rookie(707), A = lutadorPet(m, "Seu pet"), B = lutadorBot("aleatorio", CV21E_TR);
    const serie = jogarSerie(A, [B, B, B], 31, CV21E_TR);
    for (const r of serie) expect(r.tr).toBeDefined();
    for (let k = 1; k < serie.length; k++) {
      expect(serie[k].E0.L[0].hp).toBe(serie[k - 1].E.L[0].hp);
      expect(serie[k].E0.L[0].guts).toBe(serie[k - 1].E.L[0].guts);
    }
  });
  test("a tentativa da Fabrica dos v13 luta em tempo real e se refaz igual", () => {
    const t = new TentativaFabrica(1, 0, VERSAO_FABRICA_TR), u = new TentativaFabrica(1, 0, VERSAO_FABRICA_TR);
    expect(t.regra.R).toBe(CV21E_TR);
    for (let k = 0; k < LUTAS_SERIE_FABRICA && t.proxima(); k++) {
      const p = t.proxima()!;
      t.lutar(p.s); u.lutar(p.s);
      expect(t.lutas[k].res.tr).toBeDefined();
      if (!t.lutas[k].venceu) break;
    }
    expect(t.lutas.map(l => [l.venceu, l.vidaFim])).toEqual(u.lutas.map(l => [l.venceu, l.vidaFim]));
  });
});
