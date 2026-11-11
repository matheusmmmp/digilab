/* MITOLOGIA, E1 (docs/TAREFA_V3_MITOLOGIA.md, secao 10): os sinais dos cinco deuses, o termometro do Myotismon, a pedra do macaco, as
   pegadas, o dia raro e o enigma, como funcao pura do pet refeito do log. Registros sinteticos e uma vida de verdade com replay. */
import { describe, expect, test } from "vitest";
import { CD, CMU_MVP, TICK_INICIAL, TPD } from "../motor/constantes.ts";
import { NPC } from "../motor/bots.ts";
import {
  CMIT_E1, ENIGMA, FALA_DIA_RARO, FALA_PEDRA, FALA_PEGADAS, diaDeVida, myotismonJaApareceu, myotismonNoTick, pedraAchadaDe, pedraEm, pegadasDe, sinaisDe,
  sinaisNoTick, tickDoDiaRaro, type FontesE1,
} from "../motor/lendas_e1.ts";
import { Motor } from "../motor/motor.ts";
import { centroDaCelula } from "../motor/mundo.ts";
import { hashSemente } from "../motor/rng.ts";

const GAZIMON = "npc_tier1_brutamontes", total = NPC[GAZIMON]!.total;
const NOITE = 23 * 60, DIA = 12 * 60;
const vazio = (x: Partial<FontesE1> = {}, mundo: Record<string, unknown> = {}): FontesE1 =>
  ({ forcaLutas: [], log: [], feitosCuidado: [], ...x, mundo: { decisoes: [], ...mundo } as FontesE1["mundo"] });

describe("MITOLOGIA E1: os sinais dos cinco deuses", () => {
  test("Coragem: vencer um lider que nao e mais fraco que o pet; um por dia", () => {
    const s = sinaisDe(vazio({ forcaLutas: [
      { tick: 10, rival: GAZIMON, forcaPet: total, resultado: "vitoria" },             // igual: conta
      { tick: 20, rival: GAZIMON, forcaPet: total, resultado: "vitoria" },             // mesmo dia: nao
      { tick: TPD + 5, rival: GAZIMON, forcaPet: total + 1, resultado: "vitoria" },    // pet mais forte: nao
      { tick: TPD + 6, rival: GAZIMON, forcaPet: 10, resultado: "derrota" },           // derrota: nao
    ] }));
    expect(s.filter(x => x.deus === "coragem").map(x => x.tick)).toEqual([10]);
  });
  test("Amizade: 3 dias seguidos com 3 carinhos e 2 brincadeiras do dono; um dia que falha recomeca a conta", () => {
    const bom = (d: number) => [[d * TPD + 1, "d", "acariciar"], [d * TPD + 2, "d", "brincar"], [d * TPD + 3, "d", "acariciar"],
                                [d * TPD + 4, "d", "acariciar"], [d * TPD + 5, "d", "brincar"]];
    const log = [...bom(0), ...bom(1), ...bom(3), ...bom(4), ...bom(5), [6 * TPD + 1, "d", "acariciar"], ...bom(7), ...bom(8), ...bom(9)];
    expect(sinaisDe(vazio({ log })).filter(x => x.deus === "amizade").map(x => x.tick)).toEqual([5 * TPD + 5, 9 * TPD + 5]);
  });
  test("Conhecimento: 6 exploracoes num dia", () => {
    const decisoes = [...[1, 2, 3, 4, 5].map(t => ({ tick: t, acao: "explorar" })), { tick: 6, acao: "comer" }, { tick: 7, acao: "explorar" },
                      ...[1, 2, 3, 4, 5].map(t => ({ tick: TPD + t, acao: "explorar" }))];
    expect(sinaisDe(vazio({}, { decisoes })).filter(x => x.deus === "conhecimento").map(x => x.tick)).toEqual([7]);
  });
  test("Sinceridade: 3 chamados atendidos num dia (as pausas nao contam)", () => {
    const feitosCuidado = [{ tick: 1, tipo: "chamado" }, { tick: 2, tipo: "pausa" }, { tick: 3, tipo: "chamado" }, { tick: 4, tipo: "chamado" }];
    expect(sinaisDe(vazio({ feitosCuidado })).filter(x => x.deus === "sinceridade").map(x => x.tick)).toEqual([4]);
  });
  test("Diversao: a brincadeira variada da E0; cada sinal vale um dia", () => {
    const decisoes = [{ tick: 100, acao: "brincar" }, { tick: 101, acao: "explorar" }, { tick: 102, acao: "brincar", brincou_com_bola: true }];
    const s = sinaisDe(vazio({}, { decisoes }));
    expect(s).toEqual([{ deus: "diversao", tick: 102, dia: 0 }]);
    expect(sinaisNoTick(s, 101)).toEqual([]);
    expect(sinaisNoTick(s, 102 + TPD - 1)).toEqual(["diversao"]);
    expect(sinaisNoTick(s, 102 + TPD)).toEqual([]);
  });
});

describe("MITOLOGIA E1: o termometro do Myotismon", () => {
  test("a mesma acao do dono a exaustao no ultimo dia escurece; variar devolve a luz", () => {
    const repetido = Array.from({ length: 12 }, (_, i) => [100 + i, "d", "acariciar"]);
    expect(myotismonNoTick(vazio({ log: repetido }), 200)).toBe(true);
    expect(myotismonNoTick(vazio({ log: repetido }), 100 + TPD + 12)).toBe(false);      // a janela passou
    const variado = repetido.map((e, i) => (i % 3 ? e : [e[0], "d", "brincar"]));
    expect(myotismonNoTick(vazio({ log: variado }), 200)).toBe(false);
    expect(myotismonNoTick(vazio({ log: repetido.slice(0, 11) }), 200)).toBe(false);     // poucas acoes
  });
  test("o historico: o Myotismon ja apareceu se em algum momento a janela fechou a regra", () => {
    const repetido = Array.from({ length: 12 }, (_, i) => [100 + i * 60, "d", "acariciar"]);
    expect(myotismonJaApareceu(vazio({ log: repetido }), 99)).toBe(false);
    expect(myotismonJaApareceu(vazio({ log: repetido }), 100 + 11 * 60)).toBe(true);
    expect(myotismonJaApareceu(vazio({ log: repetido }), 5 * TPD)).toBe(true);           // continua aparecido depois
    const espalhado = Array.from({ length: 12 }, (_, i) => [100 + i * 200, "d", "acariciar"]);   // 12 em 2200 ticks: nunca 12 num dia
    expect(myotismonJaApareceu(vazio({ log: espalhado }), 5 * TPD)).toBe(false);
    const lutas = Array.from({ length: 6 }, (_, i) => ({ tick: 10 + i, rival: GAZIMON, forcaPet: 50, resultado: "derrota" }));
    expect(myotismonJaApareceu(vazio({ forcaLutas: lutas }), 100)).toBe(true);
  });
  test("ou 6 lutas contra o mesmo rival no ultimo dia", () => {
    const lutas = Array.from({ length: 6 }, (_, i) => ({ tick: 10 + i, rival: GAZIMON, forcaPet: 50, resultado: "derrota" }));
    expect(myotismonNoTick(vazio({ forcaLutas: lutas }), 20)).toBe(true);
    expect(myotismonNoTick(vazio({ forcaLutas: lutas.slice(1) }), 20)).toBe(false);
  });
});

describe("MITOLOGIA E1: a pedra, as pegadas e o dia raro", () => {
  const [px, py] = pedraEm();
  test("a pedra fica na mata", () => {
    expect([px, py]).toEqual(centroDaCelula(CMIT_E1.pedraCelula, CMU_MVP));
    expect(CMIT_E1.pedraCelula[0]).toBeGreaterThanOrEqual(48);
  });
  test("o pet acha a pedra de noite, perto dela, por decisao ou levado pelo dono; de dia ou longe nao", () => {
    expect(pedraAchadaDe(vazio({}, { decisoes: [{ tick: DIA, x: px, y: py }] }))).toBeNull();
    expect(pedraAchadaDe(vazio({}, { decisoes: [{ tick: NOITE, x: px + 3 * 16, y: py }] }))).toBeNull();
    expect(pedraAchadaDe(vazio({}, { decisoes: [{ tick: NOITE + TPD, x: px + 16, y: py }], levadas: [{ tick: NOITE, para: [px, py] }] }))).toBe(NOITE);
  });
  test("as pegadas aparecem na exploracao numero 60 da vida", () => {
    const decisoes = [...Array.from({ length: 59 }, (_, i) => ({ tick: i * 100, acao: "explorar" })), { tick: 5950, acao: "comer" },
                      { tick: 6000, acao: "explorar" }];
    expect(pegadasDe(vazio({}, { decisoes }))).toBe(6000);
    expect(pegadasDe(vazio({}, { decisoes: decisoes.slice(0, 59) }))).toBeNull();
  });
  test("o dia raro e o 81 de vida", () => {
    expect(diaDeVida(TICK_INICIAL)).toBe(1);
    expect(diaDeVida(tickDoDiaRaro())).toBe(81);
    expect(diaDeVida(tickDoDiaRaro() - 1)).toBe(80);
  });
  test("as falas nao nomeiam a obra; o enigma tem uma resposta certa", () => {
    for (const t of [FALA_PEDRA, FALA_PEGADAS, FALA_DIA_RARO, ENIGMA.pergunta, ENIGMA.acerto, ENIGMA.erro])
      expect(t).not.toMatch(/wukong|goku|jornada ao oeste|journey|sun /i);
    expect(ENIGMA.opcoes[ENIGMA.certa]).toBe("A nuvem");
  });
});

describe("MITOLOGIA E1: numa vida de verdade", () => {
  const m = new Motor(202);
  for (let p = 0; p < Math.round(2 * TPD / CD.passo); p++) {
    m.avancar(CD.passo);
    if (m.e.fome < .6) m.observar("alimentar");
    if (m.e.sujeira >= 2) m.observar("limpar");
    if (p % 3 === 0) m.observar("brincar");
    if (p % 4 === 0) m.observar("acariciar");
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    if (m.estagioAtual === "crianca" && p % 9 === 0 && !m.morte) m.lutarPoc(GAZIMON, hashSemente("camp", 202, p), "campo");
  }
  const r = Motor.reproduzir(202, JSON.parse(JSON.stringify(m.log)), m.versao);
  const f = (x: Motor): FontesE1 => x;
  test("o Motor cumpre as fontes, e o replay da os mesmos sinais, a mesma pedra, as mesmas pegadas e o mesmo Myotismon", () => {
    expect(sinaisDe(f(r))).toEqual(sinaisDe(f(m)));
    expect(pedraAchadaDe(f(r))).toBe(pedraAchadaDe(f(m)));
    expect(pegadasDe(f(r))).toBe(pegadasDe(f(m)));
    expect(myotismonNoTick(f(r), r.e.tick)).toBe(myotismonNoTick(f(m), m.e.tick));
  });
  test("o dono carinhoso dessa vida da o sinal da Amizade", () => {
    expect(sinaisDe(f(m)).some(s => s.deus === "amizade")).toBe(true);
  });
});
