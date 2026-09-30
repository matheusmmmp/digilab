/* Medalhas do Tamer no motor (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 4 e 5; pets v6, so no jogo): a trava da evolucao
   (1/3/5 medalhas), o evento "u" no registro do pet (o pet pronto espera e evolui no tick em que o "u" chega), o replay
   com "u" e os pets v1-v5 intactos (gabaritos de paridade nos outros testes; aqui, vidas v4 e v5 com a assinatura de
   antes da mudanca). */
import { createHash } from "node:crypto";
import { afterEach, describe, expect, test } from "vitest";
import { CAT, CD, CMD, CMG, DUR_EVO, MEDALHAS, TICK_INICIAL, TPD, VERSAO_PET } from "../motor/index.ts";
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
function vida(versao: number, tipo: "atencioso" | "aleatorio", semente: number, dias: number, medalhas?: (m: Motor, p: number) => void): Motor {
  const m = new Motor(semente, versao), dono = criarDono(tipo), r = criarRng(hashSemente("dono", semente, tipo));
  const passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, r);
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

describe("pets v1-v5 nao mudam", () => {
  /* sha256 da assinatura destas vidas no motor de ANTES das medalhas (origin/main em 2026-09-29, escala ligada) */
  const ANTES: [number, "atencioso" | "aleatorio", number, string, string][] = [
    [4, "atencioso", 5101, "adulto", "0270ea2fb6bd458b3c1b17d3f1e23d2c21f7014e760dca868f377bb40c99f519"],
    [5, "atencioso", 5202, "mega", "d6cfe0a92bdff2261cb404dc6f71a804fa9b43286d988c8a3a76a0b5c668bb06"],
    [5, "aleatorio", 5303, "mega", "782ec604330b4c5a494b531dc090948521826902659dce632142bf3b02e18a9e"],
  ];
  for (const [versao, tipo, s, est, h] of ANTES) test(`v${versao} ${tipo} @${s}: mesma assinatura de antes, sem trava`, () => {
    ligarEscala(true);
    const m = vida(versao, tipo, s, 3);
    expect(m.estagioAtual).toBe(est);
    expect(sha(m.assinatura())).toBe(h);
    expect(m.requisitoMedalhas("adolescente")).toBeNull();
    expect(m.requisitosEvolucao()?.medalhas ?? null).toBeNull();
    expect(() => m.liberar(1)).toThrow(/v6/);
  });
  test("ovos novos sao v6", () => { expect(VERSAO_PET).toBe(6); expect(new Motor(1).versao).toBe(6); });
});

describe("a trava (pets v6)", () => {
  test("a mesma vida no v6, sem medalha, fica no Rookie pronta para evoluir", () => {
    ligarEscala(true);
    const m = vida(6, "atencioso", 5202, 3);
    expect(m.estagioAtual).toBe("crianca");
    expect(m.esperandoMedalha()).toEqual({ tem: 0, precisa: CMD.adolescente, ok: false });
    const r = m.requisitosEvolucao()!;
    expect(r.alvo).toBe("adolescente"); expect(r.tempo).toBe(true); expect(r.pronto).toBe(false);
  });
  test("Rookie -> Champion: espera a 1a medalha e evolui no tick do evento u", () => {
    const v5 = new Motor(77, 5), m = new Motor(77, 6);
    v5.avancar(FIM_ROOKIE + 120); m.avancar(FIM_ROOKIE + 120);
    expect(v5.estagioAtual).toBe("adolescente");
    expect(m.estagioAtual).toBe("crianca");
    const t = m.e.tick;
    m.liberar(1);
    expect(m.log[m.log.length - 1]).toEqual([t, "u", { n: 1 }]);
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.evolucoes[m.evolucoes.length - 1].tick).toBe(t);
    expect(v5.evolucoes[v5.evolucoes.length - 1].tick).toBeLessThan(t);   /* o v5 evoluiu antes, sem esperar */
    expect(m.esperandoMedalha()).toBeNull();
  });
  test("medalha antes da hora: o Rookie evolui no tempo de sempre", () => {
    const v5 = new Motor(78, 5), m = new Motor(78, 6);
    m.avancar(30); m.liberar(1);
    v5.avancar(FIM_ROOKIE + 60); m.avancar(FIM_ROOKIE + 30);
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.evolucoes.map(x => x.tick)).toEqual(v5.evolucoes.map(x => x.tick));
  });
  test("Champion -> Ultimate: pede 3 medalhas; com 1 e 2 espera", () => {
    const m = new Motor(79, 6);
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
    const m = new Motor(80, 6), v5 = new Motor(80, 5);
    m.avancar(FIM_ROOKIE + 600); v5.avancar(FIM_ROOKIE + 600);
    expect(m.estagioAtual).toBe("crianca");
    m.liberar(1);
    const t1 = m.e.tick;
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.tickLimiteEstagio()).toBe(t1 + m.dur.adolescente);
    expect(v5.tickLimiteEstagio()).toBe(TICK_INICIAL + DUR_EVO.bebe + DUR_EVO.crianca + DUR_EVO.adolescente);   /* v5: desde o nascimento */
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
    const m = new Motor(80, 6);
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
    const m = new Motor(81, 6);
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
    const m = vida(6, "atencioso", 5202, 3, (mm, p) => {
      if (p === 40) dar(mm, 1);                                  /* no In-Training: nada muda na hora */
      if (mm.esperandoMedalha()) dar(mm, mm.esperandoMedalha()!.precisa);
    });
    expect(m.log.filter(e => e[1] === "u").length).toBeGreaterThanOrEqual(1);
    const r = Motor.reproduzir(m.semente, m.log, 6);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.medalhas).toBe(m.medalhas);
    expect(r.estagioAtual).toBe(m.estagioAtual);
    const semU = m.log.filter(e => e[1] !== "u");
    expect(() => Motor.reproduzir(m.semente, semU, 6).assinatura()).not.toThrow();
    expect(Motor.reproduzir(m.semente, semU, 6).assinatura()).not.toBe(m.assinatura());
  });
  test("a assinatura dos v6 inclui as medalhas (um u no In-Training ja muda)", () => {
    const a = new Motor(90, 6), b = new Motor(90, 6);
    a.avancar(30); b.avancar(30); b.liberar(1);
    a.avancar(30); b.avancar(30);
    expect(a.estagioAtual).toBe(b.estagioAtual);
    expect(a.assinatura()).not.toBe(b.assinatura());
  });
  test("u em pet v5, u fora de ordem e evento desconhecido: o replay falha alto", () => {
    const u: EventoRegistro = [TICK_INICIAL, "u", { n: 1 }];
    expect(() => Motor.reproduzir(1, [u], 5)).toThrow(/v6/);
    expect(() => Motor.reproduzir(1, [u, [TICK_INICIAL, "u", { n: 1 }]], 6)).toThrow(/liberação inválida/);
    expect(() => Motor.reproduzir(1, [[TICK_INICIAL, "x", 1] as unknown as EventoRegistro], 6)).toThrow(/desconhecido/);
    const m = Motor.reproduzir(1, [u], 6);
    expect(m.medalhas).toBe(1);
  });
  test("o filho da heranca e v6 e recebe as medalhas depois da origem", () => {
    const p = new Motor(91, 6), q = new Motor(92, 6);
    for (const x of [p, q]) {
      x.liberar(3); x.avancar(FIM_ROOKIE + 15); x.sparring = CAT.sparring;
      x.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 }; x.avancar(DUR_EVO.adolescente);
      expect(x.estagioAtual).toBe("adulto");
    }
    const f = Motor.cruzar(p, q, 93, 94, "t");
    expect(f.versao).toBe(6);
    f.liberar(3);
    expect(f.log.map(e => e[1])).toEqual(["o", "u"]);
    expect(Motor.reproduzir(93, f.log, 6).assinatura()).toBe(f.assinatura());
  });
});
