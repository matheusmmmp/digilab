/* Medalhas do Tamer no motor (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 4 e 5; pets v6 em diante, hoje o v13): a trava da evolucao
   (1/3/5 medalhas), o evento "u" no registro do pet (o pet pronto espera e evolui no tick em que o "u" chega), o replay
   com "u". */
import { createHash } from "node:crypto";
import { afterEach, describe, expect, test } from "vitest";
import { ACOES_DONO_JOGO_V11, CAT, CD, CMD, CMG, DUR_EVO, MEDALHAS, TICK_INICIAL, TPD, VERSAO_PET } from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";
import { criarDono, type VisaoDono } from "../motor/donos.ts";
import { Motor } from "../motor/motor.ts";
import { criarRng, hashSemente } from "../motor/rng.ts";
import type { EventoRegistro } from "../motor/tipos.ts";

const escalaAntes = ESCALA.ligada;
afterEach(() => ligarEscala(escalaAntes));
const sha = (s: string): string => createHash("sha256").update(s).digest("hex");
const FIM_ROOKIE = DUR_EVO.bebe + DUR_EVO.crianca;

/** vida com o dono simulado: cuida, trata lesao, luta na Campina no Rookie, faz as lutas de treino e treina.
    `medalhas(m, p)`: quando o Tamer "ganha" medalhas nesta vida (so v6) */
function vida(tipo: "atencioso" | "aleatorio", semente: number, dias: number, medalhas?: (m: Motor, p: number) => void): Motor {
  const m = new Motor(semente, 13), dono = criarDono(tipo), r = criarRng(hashSemente("dono", semente, tipo));
  const passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, r).filter(a => ACOES_DONO_JOGO_V11.includes(a));
    if (m.lesionadoDesde !== null && acoes.length) acoes[0] = "tratar_lesao";
    for (const a of acoes) { m.observar(a); gasto++; }
    if (m.estagioAtual === "crianca" && p % 7 === 0) m.lutar("npc_tier1_brutamontes", hashSemente("camp", semente, p));
    if ((m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) || (m.estagioAtual === "adulto" && m.lutas.lutas < 12))
      m.lutar("aleatorio", hashSemente("sparring", semente, p));
    if (m.estagioAtual !== "bebe" && p % 5 === 0 && m.treino.podeTocar(m.e.tick)) { try { m.treinar("corrida"); } catch { /* dormindo */ } }
    medalhas?.(m, p);
  }
  return m;
}

describe("a versao dos ovos novos", () => {
  test("ovos novos sao v13 (v6 + confianca + combate equilibrado + vinculo B + o cerebro A e o corpo + o mundo fisico + a luta em tempo real)", () => { expect(VERSAO_PET).toBe(14); expect(new Motor(1).versao).toBe(14); });
});

describe("a trava (pet v13)", () => {
  test("a mesma vida no v6, sem medalha, fica no Rookie pronta para evoluir", () => {
    ligarEscala(true);
    const m = vida("atencioso", 5202, 3);
    expect(m.estagioAtual).toBe("crianca");
    expect(m.esperandoMedalha()).toEqual({ tem: 0, precisa: CMD.adolescente, ok: false });
    const r = m.requisitosEvolucao()!;
    expect(r.alvo).toBe("adolescente"); expect(r.tempo).toBe(true); expect(r.pronto).toBe(false);
  });
  test("Rookie -> Champion: espera a 1a medalha e evolui no tick do evento u", () => {
    const m = new Motor(77, 13);
    m.avancar(FIM_ROOKIE + 120);
    expect(m.estagioAtual).toBe("crianca");
    const t = m.e.tick;
    m.liberar(1);
    expect(m.log[m.log.length - 1]).toEqual([t, "u", { n: 1 }]);
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.evolucoes[m.evolucoes.length - 1].tick).toBe(t);
    expect(t).toBeGreaterThan(TICK_INICIAL + FIM_ROOKIE);   /* esperou: evoluiu depois do fim do Rookie, so no u */
    expect(m.esperandoMedalha()).toBeNull();
  });
  test("medalha antes da hora: o Rookie evolui no tempo de sempre", () => {
    const m = new Motor(78, 13);
    m.avancar(30); m.liberar(1);
    m.avancar(FIM_ROOKIE + 30);
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.evolucoes[m.evolucoes.length - 1].tick).toBe(TICK_INICIAL + FIM_ROOKIE);   /* no tempo de sempre, sem esperar */
  });
  test("Champion -> Ultimate: pede 3 medalhas; com 1 e 2 espera", () => {
    const m = new Motor(79, 13);
    m.liberar(1);
    m.avancar(FIM_ROOKIE + 15);
    expect(m.estagioAtual).toBe("adolescente");
    m.sparring = CAT.sparring;
    m.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 };
    m.avancar(DUR_EVO.adolescente);
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.esperandoMedalha()).toEqual({ tem: 1, precisa: CMD.adulto, ok: false });
    m.liberar(2);
    expect(m.estagioAtual).toBe("adolescente");
    m.liberar(3);
    expect(m.estagioAtual).toBe("adulto");
    expect(m.evolucoes[m.evolucoes.length - 1].tick).toBe(m.e.tick);
  });
  test("o Champion dura o tempo inteiro mesmo quando o Rookie esperou a medalha (tempo desde a evolucao anterior)", () => {
    const m = new Motor(80, 13);
    m.avancar(FIM_ROOKIE + 600);
    expect(m.estagioAtual).toBe("crianca");
    m.liberar(1);
    const t1 = m.e.tick;
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.tickLimiteEstagio()).toBe(t1 + m.dur.adolescente);
    m.sparring = CAT.sparring;
    m.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 };
    m.liberar(3);
    m.avancar(m.dur.adolescente - 15);
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.requisitosEvolucao()!.falta).toBe(15);
    m.avancar(15);
    expect(m.estagioAtual).toBe("adulto");
  });
  test("Ultimate -> Mega: pede 5 medalhas; requisitosMega mostra tem e precisa", () => {
    const m = new Motor(80, 13);
    m.liberar(3);
    m.avancar(FIM_ROOKIE + 15);
    m.sparring = CAT.sparring;
    m.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 };
    m.avancar(DUR_EVO.adolescente);
    expect(m.estagioAtual).toBe("adulto");
    m.avancar(CMG.durRapida + 10);
    /* lutas e vinculo postos a mao (so para testar a regra): o vinculo anda com o tempo, entao vem logo antes do passo */
    m.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 }; m.vinc.valor = .9;
    m.avancar(1);
    expect(m.estagioAtual).toBe("adulto");
    const r = m.requisitosMega()!;
    expect(r.tempo && r.lutas && r.taxa && r.vinculo).toBe(true);
    expect(r.medalhas).toEqual({ tem: 3, precisa: CMD.mega, ok: false });
    expect(m.podeMega()).toBe(false);
    expect(m.esperandoMedalha()).toEqual({ tem: 3, precisa: 5, ok: false });
    m.liberar(5);
    expect(m.estagioAtual).toBe("mega");
    expect(m.requisitosEvolucao()).toBeNull();
  });
  test("liberacao invalida falha alto", () => {
    const m = new Motor(81, 13);
    m.liberar(2);
    expect(() => m.liberar(2)).toThrow(/liberação inválida/);
    expect(() => m.liberar(1)).toThrow(/liberação inválida/);
    expect(() => m.liberar(MEDALHAS.length + 1)).toThrow(/liberação inválida/);
    expect(() => m.liberar(2.5)).toThrow(/liberação inválida/);
    expect(m.log.filter(e => e[1] === "u")).toHaveLength(1);
  });
});

describe("replay com o evento u", () => {
  test("vida v6 com medalhas no meio: o replay da a mesma assinatura; sem os u, outra", () => {
    ligarEscala(true);
    const dadas = new Set<number>();
    const dar = (m: Motor, n: number) => { if (!dadas.has(n)) { dadas.add(n); m.liberar(n); } };
    /* semente 5404 (era 5202): sem os u o pet fica mais tempo no Rookie e luta mais com o Gazimon; com a escala dos pets v6 e a
       regra do limite do desafiado ele perde mais, e em varias sementes a linha do tempo sem os u morre de lesao sem tratar (o
       dono do registro nao a via). A assinatura diferente e o que o teste pede; a morte tambem conta como outra linha do tempo */
    const m = vida("atencioso", 5404, 3, (mm, p) => {
      if (p === 40) dar(mm, 1);                                  /* no In-Training: nada muda na hora */
      if (mm.esperandoMedalha()) dar(mm, mm.esperandoMedalha()!.precisa);
    });
    expect(m.log.filter(e => e[1] === "u").length).toBeGreaterThanOrEqual(1);
    const r = Motor.reproduzir(m.semente, m.log, 13);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.medalhas).toBe(m.medalhas);
    expect(r.estagioAtual).toBe(m.estagioAtual);
    const semU = m.log.filter(e => e[1] !== "u");
    let outra: string;
    try { outra = Motor.reproduzir(m.semente, semU, 13).assinatura(); } catch (err) { outra = "morreu: " + String(err); }
    expect(outra).not.toBe(m.assinatura());
  });
  test("a assinatura dos v6 inclui as medalhas (um u no In-Training ja muda)", () => {
    const a = new Motor(90, 13), b = new Motor(90, 13);
    a.avancar(30); b.avancar(30); b.liberar(1);
    a.avancar(30); b.avancar(30);
    expect(a.estagioAtual).toBe(b.estagioAtual);
    expect(a.assinatura()).not.toBe(b.assinatura());
  });
  test("u fora de ordem e evento desconhecido: o replay falha alto", () => {
    const u: EventoRegistro = [TICK_INICIAL, "u", { n: 1 }];
    expect(() => Motor.reproduzir(1, [u, [TICK_INICIAL, "u", { n: 1 }]], 13)).toThrow(/liberação inválida/);
    expect(() => Motor.reproduzir(1, [[TICK_INICIAL, "x", 1] as unknown as EventoRegistro], 13)).toThrow(/desconhecido/);
    const m = Motor.reproduzir(1, [u], 13);
    expect(m.medalhas).toBe(1);
  });
  test("o filho da heranca nasce na versao atual (v7) e recebe as medalhas depois da origem", () => {
    const p = new Motor(91, 13), q = new Motor(92, 13);
    for (const x of [p, q]) {
      x.liberar(3); x.avancar(FIM_ROOKIE + 15); x.sparring = CAT.sparring;
      x.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 }; x.avancar(DUR_EVO.adolescente);
      expect(x.estagioAtual).toBe("adulto");
    }
    const f = Motor.cruzar(p, q, 93, 94, "t");
    expect(f.versao).toBe(VERSAO_PET);
    f.liberar(3);
    expect(f.log.map(e => e[1])).toEqual(["o", "u"]);
    expect(Motor.reproduzir(93, f.log, f.versao).assinatura()).toBe(f.assinatura());
  });
});
