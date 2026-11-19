/* MMO8 (docs/PLANO_V3_MMO.md, secoes 8 e 9; MMO-15 a MMO-19): o evento "reset" no registro do Tamer (versao 11, atras da chave
   RESET_LIGADO), os Bits do reset (um por semana de relogio), o nivel do reset, os pontos do Digimon e o Respeito na conta pura
   (src/ranking/pontos.ts). Os pets Ultimate e Mega sao de teste: a evolucao e posta a mao no registro das evolucoes (chegar la pelo motor
   leva dias de vida simulada), como no teste da MMO2. */
import { describe, expect, test } from "vitest";
import { GrupoDoJogo, MEDALHAS, Motor, VERSAO_GRUPO } from "../motor/index.ts";
import { hashAte } from "../src/ranking/pedido.ts";
import {
  BONUS_RESET, PONTOS_MINIMOS_RESET, TAMER_LENDARIO, estagioMaximo, nivelDoReset, nivelPeloRespeito, pontosDoDigimon, respeito,
  respeitoDoReset, respeitoLocal, semanaDe, tituloDoRespeito, type LutaRanqueada,
} from "../src/ranking/pontos.ts";
import { aplicarReset, eventoDoReset, petDoBonus, previaDoReset } from "../src/reset.ts";
import { petsDoAposentado } from "../src/heranca.ts";
import {
  CHAVE_TAMER, RESET_LIGADO, Tamer, VERSAO_TAMER, VERSAO_TAMER_RESET, gravarTamer, lerTamer, pagarReset, versaoTamerDe, type EventoTamer, type ResetPet,
} from "../src/tamer.ts";

const armaz = (dados: Record<string, string> = {}) => ({ dados, getItem: (k: string) => dados[k] ?? null, setItem: (k: string, v: string) => { dados[k] = v; } });
/** segunda-feira, 16/11/2026, 12:00 em Brasilia */
const SEG = Date.UTC(2026, 10, 16, 15);
const DIA = 86_400_000;
const H64 = "a".repeat(64);

/** um pet de teste que chegou ao estagio dado (as evolucoes postas a mao) e, se pedido, venceu a Liga */
function petAte(semente: number, est: "crianca" | "adolescente" | "adulto" | "mega", liga = false): Motor {
  const m = new Motor(semente), ordem = ["crianca", "adolescente", "adulto", "mega"] as const;
  ordem.slice(0, ordem.indexOf(est) + 1).forEach((e, i) => m.evolucoes.push({ tick: 1000 * (i + 1), estagio: e, forma: { ...m.forma } }));
  if (liga) m.liga.titulos = 1;
  return m;
}
const reset = (x: Partial<ResetPet> = {}): Omit<ResetPet, "quando"> =>
  ({ pet: 7, hash: H64, eventos: 10, est: "adulto", forma: "WarGrowlmon", nivel: 1, tick: 5000, por: "reset", ...x });

describe("MMO8: a chave e a versao do registro do Tamer", () => {
  test("a chave esta ligada: o registro grava a 11; com ela desligada, a 10 sem o reset e a 11 com ele", () => {
    expect(RESET_LIGADO).toBe(true);
    expect(VERSAO_TAMER).toBe(10);
    expect(versaoTamerDe([])).toBe(VERSAO_TAMER_RESET);
    expect(versaoTamerDe([], false)).toBe(10);
    const t = new Tamer();
    t.resetar(reset(), SEG);
    expect(versaoTamerDe(t.log, false)).toBe(11);
  });
  test("gravar e ler: a versao 11, o mesmo reset", () => {
    const t = new Tamer(), a = armaz();
    aplicarReset(t, reset(), SEG);
    gravarTamer(a, t);
    const d = JSON.parse(a.dados[CHAVE_TAMER]);
    expect(d.versao).toBe(11);
    const l = lerTamer(a);
    expect(l.resets).toEqual(t.resets);
    expect(l.resetDe(7)).toEqual({ ...reset(), quando: SEG });
    expect(l.bits).toBe(BONUS_RESET[1].bits);
  });
  test("um registro de antes da 11 com o reset, ou com os Bits do reset, falha alto", () => {
    const r: EventoTamer = ["reset", { ...reset(), quando: SEG }];
    expect(() => lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 10, log: [r] }) }))).toThrow(/versão 11/);
    const b: EventoTamer = ["bits", { id: "reset:7", pet: 7, valor: 150, origem: "reset", tick: 5000, quando: SEG }];
    expect(() => lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 10, log: [b] }) }))).toThrow(/versão 11/);
    expect(lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 11, log: [r, b] }) })).bits).toBe(150);
  });
  test("falha alto: o reset repetido, o nivel desconhecido, sem hash, sem estagio, por onde desconhecido", () => {
    const t = new Tamer();
    t.resetar(reset(), SEG);
    expect(() => t.resetar(reset(), SEG)).toThrow(/repetido/);
    expect(() => new Tamer().resetar(reset({ nivel: 4 as never }))).toThrow(/nível/);
    expect(() => new Tamer().resetar(reset({ hash: "xyz" }))).toThrow(/hash/);
    expect(() => new Tamer().resetar(reset({ est: "ovo" as never }))).toThrow(/estágio/);
    expect(() => new Tamer().resetar(reset({ por: "outro" as never }))).toThrow(/desconhecido/);
  });
});

describe("MMO8: os Bits do reset (MMO-18 e MMO-19)", () => {
  test("sem bonus (antes do Ultimate) nao paga; o nivel 1 paga 150, o 2 400, o 3 800", () => {
    for (const nivel of [0, 1, 2, 3] as const) {
      const t = new Tamer(), r = t.resetar(reset({ nivel }), SEG), g = pagarReset(t, r, SEG);
      expect(g?.valor ?? 0).toBe(BONUS_RESET[nivel].bits);
      if (g) expect(g).toMatchObject({ id: "reset:7", pet: 7, origem: "reset" });
    }
  });
  test("um reset pago por semana de relogio: o segundo na mesma semana nao paga, o da semana seguinte paga", () => {
    const t = new Tamer();
    expect(aplicarReset(t, reset({ pet: 1 }), SEG).bits?.valor).toBe(150);
    expect(aplicarReset(t, reset({ pet: 2, nivel: 3 }), SEG + 4 * DIA).bits).toBeNull();     // sexta da mesma semana
    expect(t.resetDe(2)).not.toBeNull();                                                    // o reset entra igual
    expect(semanaDe(SEG + 7 * DIA)).not.toBe(semanaDe(SEG));
    expect(aplicarReset(t, reset({ pet: 3, nivel: 2 }), SEG + 7 * DIA).bits?.valor).toBe(400);
    expect(t.bits).toBe(550);
  });
  test("o reset sem bonus nao gasta a vez da semana", () => {
    const t = new Tamer();
    expect(aplicarReset(t, reset({ pet: 1, nivel: 0 }), SEG).bits).toBeNull();
    expect(aplicarReset(t, reset({ pet: 2 }), SEG + DIA).bits?.valor).toBe(150);
  });
  test("a previa: o nivel, o bonus e a semana ja paga", () => {
    const t = new Tamer();
    expect(previaDoReset(petAte(9, "adulto"), t, SEG)).toEqual({ nivel: 1, respeito: 300, bits: 150, bitsDaSemanaPagos: false });
    aplicarReset(t, reset({ pet: 1 }), SEG);
    expect(previaDoReset(petAte(9, "mega"), t, SEG + DIA)).toEqual({ nivel: 2, respeito: 600, bits: 0, bitsDaSemanaPagos: true });
  });
});

describe("MMO8: o nivel do reset, refeito do pet", () => {
  test("antes do Ultimate 0; o Ultimate 1; o Mega 2; o Mega com o titulo da Liga 3", () => {
    expect(nivelDoReset(new Motor(9))).toBe(0);
    expect(estagioMaximo(new Motor(9))).toBe("bebe");
    expect(nivelDoReset(petAte(9, "adolescente"))).toBe(0);
    expect(nivelDoReset(petAte(9, "adulto"))).toBe(1);
    expect(nivelDoReset(petAte(9, "adulto", true))).toBe(1);   // a Liga sem o Mega nao sobe o nivel
    expect(nivelDoReset(petAte(9, "mega"))).toBe(2);
    expect(nivelDoReset(petAte(9, "mega", true))).toBe(3);
  });
  test("o evento do reset: a semente, o hash do registro inteiro (o mesmo do pedido da semente), os eventos e o nivel", async () => {
    const m = petAte(11, "adulto");
    m.avancar(5);
    const x = await eventoDoReset(m, "reset");
    expect(x).toMatchObject({ pet: 11, eventos: m.log.length, nivel: 1, tick: m.e.tick, por: "reset", est: m.estagioAtual });
    expect(x.hash).toBe(await hashAte(m.log, m.log.length));
    expect(x.hash).toMatch(/^[0-9a-f]{64}$/);
  });
});

describe("MMO8: os pontos do Digimon e o Respeito (a conta pura)", () => {
  const luta = (pontos: number): LutaRanqueada => ({ pontos } as LutaRanqueada);
  test("os pontos do Digimon sao a soma das lutas da vida", () => {
    expect(pontosDoDigimon([])).toBe(0);
    expect(pontosDoDigimon([luta(20), luta(10), luta(0), luta(5)])).toBe(35);
  });
  test("o Respeito do reset: o do nivel; o conferido pede 200 pontos do Digimon; o do jogo (null) conta inteiro", () => {
    expect(PONTOS_MINIMOS_RESET).toBe(200);
    expect(respeitoDoReset(1, 240)).toBe(300);
    expect(respeitoDoReset(1, 199.5)).toBe(0);
    expect(respeitoDoReset(3, 200)).toBe(1000);
    expect(respeitoDoReset(2, null)).toBe(600);
    expect(respeitoDoReset(0, 900)).toBe(0);
    expect(() => respeitoDoReset(5 as never, 0)).toThrow(/nível/);
  });
  test("o Respeito: 100 por lider, 500 a Liga, os resets, 100 por titulo da semana, 20 por selo", () => {
    expect(respeito({ lideres: 6, liga: true, resets: [{ nivel: 1, pontos: 240 }, { nivel: 2, pontos: 80 }], titulosSemana: 2, selos: 7 }))
      .toEqual({ total: 600 + 500 + 300 + 200 + 140, lideres: 600, liga: 500, resets: 300, titulos: 200, selos: 140 });
    expect(() => respeito({ lideres: -1, liga: false, resets: [], titulosSemana: 0, selos: 0 })).toThrow(/contagem/);
  });
  test("o Respeito do jogo: as medalhas, o titulo e os resets inteiros, sem titulos nem selos", () => {
    const t = new Tamer(), m = new Motor(101);
    MEDALHAS.slice(0, 3).forEach((md, i) => t.ganhar(md.id, m, SEG + i));
    t.resetar(reset({ nivel: 2 }), SEG);
    expect(respeitoLocal(t)).toMatchObject({ total: 300 + 600, lideres: 300, liga: 0, resets: 600 });
  });
  test("o nivel do Tamer: abaixo do 10, o dos marcos; do 10 em diante, mais um a cada 1 000 de Respeito", () => {
    expect(nivelPeloRespeito(7, 5000)).toBe(7);
    expect(nivelPeloRespeito(10, 999)).toBe(10);
    expect(nivelPeloRespeito(10, 2340)).toBe(12);
    expect(() => nivelPeloRespeito(10, -1)).toThrow();
  });
  test("o titulo de faixa: Tamer Lendario a partir de 10 000, e a conta nao para", () => {
    expect(TAMER_LENDARIO).toBe(10000);
    expect(tituloDoRespeito(9999)).toBeNull();
    expect(tituloDoRespeito(10000)).toBe("Tamer Lendário");
    expect(tituloDoRespeito(25000)).toBe("Tamer Lendário");
  });
});

describe("MMO8: o reset do par (Matheus, 2026-11-19, \"Bonus do mais alto\"; D-CONTA-179)", () => {
  const sobe = (m: Motor, est: "crianca" | "adolescente" | "adulto" | "mega") => {
    const ordem = ["crianca", "adolescente", "adulto", "mega"] as const;
    ordem.slice(0, ordem.indexOf(est) + 1).forEach((e, i) => m.evolucoes.push({ tick: 1000 * (i + 1), estagio: e, forma: { ...m.forma } }));
  };
  test("o bonus e o do pet de nivel mais alto; no empate, o primeiro do grupo", () => {
    const g = new GrupoDoJogo(303, VERSAO_GRUPO), [a, b] = g.ids;
    expect(petDoBonus(g)).toBe(g.motor(a!));
    sobe(g.motor(b!), "adulto");
    expect(petDoBonus(g)).toBe(g.motor(b!));
    sobe(g.motor(a!), "mega");
    expect(petDoBonus(g)).toBe(g.motor(a!));
  });
  test("o par aposentado em Geracoes volta pelos dois pets do grupo", () => {
    const g = new GrupoDoJogo(304, VERSAO_GRUPO);
    g.avancar(30);
    const pets = petsDoAposentado({ semente: g.semente, log: g.log as never, versao: g.versao, ger: 1, filho: 0, quando: SEG, grupo: true, foco: g.ids[0] });
    expect(pets.map(m => m.semente)).toEqual(g.ids.map(i => g.motor(i).semente));
    expect(pets.map(m => m.log.length)).toEqual(g.ids.map(i => g.motor(i).log.length));
  });
});
