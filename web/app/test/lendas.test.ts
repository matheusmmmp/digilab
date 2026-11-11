/* MITOLOGIA, E0 (docs/TAREFA_V3_MITOLOGIA.md): as lendas como funcao pura do pet refeito do log. Confere a regra da hybris e a da
   brincadeira variada em registros sinteticos, a voz do oraculo, e numa vida de verdade (um Rookie que luta na Campina) que o
   forcaLutas e as lendas saem iguais do replay do log, e que o forcaLutas fica fora da assinatura. */
import { describe, expect, test } from "vitest";
import { CD, TPD } from "../motor/constantes.ts";
import { NPC } from "../motor/bots.ts";
import {
  CMIT, LENDA_CONTADA, LENDA_DO_MACACO, detalheNoTick, falaDoOraculo, hybrisDe, lendas, variadaDe, type FontesLenda,
} from "../motor/lendas.ts";
import { Motor } from "../motor/motor.ts";
import { hashSemente } from "../motor/rng.ts";

const GAZIMON = "npc_tier1_brutamontes";
const total = NPC[GAZIMON]!.total;
const luta = (tick: number, forcaPet: number, resultado = "derrota", rival = GAZIMON) => ({ tick, rival, forcaPet, resultado });
const decisao = (tick: number, acao: string, bola = false) => ({ tick, acao, brincou_com_bola: bola });
const fontes = (dec: Record<string, unknown>[], log: unknown[][] = []): FontesLenda => ({ forcaLutas: [], log, mundo: { decisoes: dec } });

describe("MITOLOGIA E0: a hybris", () => {
  test("so a derrota para um lider muito acima da forca do pet; a parte conta as hybris anteriores", () => {
    const limite = total / CMIT.razaoHybris;
    const h = hybrisDe([
      luta(10, Math.floor(limite)),                  // derrota bem abaixo: hybris (parte 0)
      luta(TPD + 20, Math.ceil(limite) + 1),         // derrota sem a distancia: nao
      luta(TPD + 30, 10, "vitoria"),                 // vitoria: nao
      luta(TPD + 40, 10, "empate"),                  // empate: nao
      luta(TPD + 50, 10, "derrota", "brasa_crianca_x"),   // nao e lider da Campanha: nao
      luta(TPD + 60, 10),                            // hybris (parte 1)
    ]);
    expect(h.map(e => [e.tick, e.parte, e.forcaRival])).toEqual([[10, 0, total], [TPD + 60, 1, total]]);
  });
  test("no maximo uma hybris por dia de jogo", () => {
    expect(hybrisDe([luta(10, 10), luta(20, 10), luta(TPD - 1, 10), luta(TPD, 10)]).map(e => e.tick)).toEqual([10, TPD]);
  });
  test("forca do pet nao positiva falha alto", () => {
    expect(() => hybrisDe([luta(1, 0)])).toThrow();
  });
  test("o oraculo conta a lenda em pedacos, na ordem, e fecha quando acaba", () => {
    const h = hybrisDe(Array.from({ length: LENDA_DO_MACACO.length + 2 }, (_, i) => luta(i * TPD, 1)));
    expect(h.map(falaDoOraculo)).toEqual([...LENDA_DO_MACACO, LENDA_CONTADA, LENDA_CONTADA]);
  });
  test("a fala nao nomeia a obra nem o heroi", () => {
    for (const t of [...LENDA_DO_MACACO, LENDA_CONTADA]) expect(t).not.toMatch(/wukong|goku|jornada ao oeste|journey|sun /i);
  });
});

describe("MITOLOGIA E0: a brincadeira variada", () => {
  test("tres atividades diferentes num dia dao um evento, no tick da terceira; a repeticao nao conta", () => {
    const v = variadaDe(fontes([decisao(5, "brincar", true), decisao(6, "brincar", true), decisao(7, "explorar"), decisao(9, "comer")],
                               [[8, "d", "brincar"]]));
    expect(v).toEqual([{ tipo: "variada", tick: 8, dia: 0, atividades: ["bola", "explorar", "dono_brinca"] }]);
  });
  test("a mesma atividade o dia inteiro nao da evento; brincar sem a bola e outra atividade", () => {
    expect(variadaDe(fontes([1, 2, 3, 4].map(t => decisao(t, "explorar"))))).toEqual([]);
    expect(variadaDe(fontes([decisao(1, "brincar"), decisao(2, "brincar", true), decisao(3, "explorar")])).length).toBe(1);
  });
  test("no maximo um por dia, e o dia novo comeca do zero", () => {
    const dia = (d: number) => [decisao(d * TPD + 1, "brincar"), decisao(d * TPD + 2, "explorar"), decisao(d * TPD + 3, "brincar", true),
                                decisao(d * TPD + 4, "brincar")];
    const v = variadaDe(fontes([...dia(0), decisao(TPD - 1, "explorar"), ...dia(2)]));
    expect(v.map(e => [e.dia, e.tick])).toEqual([[0, 3], [2, 2 * TPD + 3]]);
    /* duas atividades num dia e uma no seguinte nao somam */
    expect(variadaDe(fontes([decisao(TPD - 2, "brincar"), decisao(TPD - 1, "explorar"), decisao(TPD, "brincar", true)]))).toEqual([]);
  });
  test("a nuvem vale por um dia de jogo a partir do evento", () => {
    const ev = lendas(fontes([decisao(100, "brincar"), decisao(101, "explorar"), decisao(102, "brincar", true)]));
    expect(detalheNoTick(ev, 101)).toBeNull();
    expect(detalheNoTick(ev, 102)?.tick).toBe(102);
    expect(detalheNoTick(ev, 102 + CMIT.duracaoDetalhe - 1)?.tick).toBe(102);
    expect(detalheNoTick(ev, 102 + CMIT.duracaoDetalhe)).toBeNull();
  });
  test("sem o mundo (pets antigos) nao ha brincadeira variada, e uma decisao sem tick falha alto", () => {
    expect(variadaDe({ forcaLutas: [], log: [], mundo: null })).toEqual([]);
    expect(() => variadaDe(fontes([{ acao: "brincar" }]))).toThrow();
  });
});

/** um Rookie que luta contra o Gazimon na Campina a cada 7 passos e brinca */
function vida(semente: number, dias: number): Motor {
  const m = new Motor(semente);
  const passos = Math.round(dias * TPD / CD.passo);
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    if (m.e.fome < .6) m.observar("alimentar");
    if (m.e.sujeira >= 2) m.observar("limpar");
    if (p % 3 === 0) m.observar("brincar");
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    if (m.estagioAtual === "crianca" && p % 7 === 0 && !m.morte) m.lutarPoc(GAZIMON, hashSemente("camp", semente, p), "campo");
  }
  return m;
}

describe("MITOLOGIA E0: numa vida de verdade", () => {
  const m = vida(101, 1.2);
  const replay = Motor.reproduzir(101, JSON.parse(JSON.stringify(m.log)), m.versao);   // como o save carrega
  test("cada luta da POC tem a forca do pet, e o resultado e o do vida5", () => {
    expect(m.forcaLutas.length).toBeGreaterThan(0);
    expect(m.forcaLutas.map(l => [l.tick, l.rival, l.resultado])).toEqual(m.vida5.lutas.map(l => [l.tick, l.rival, l.resultado]));
    for (const l of m.forcaLutas) expect(l.forcaPet).toBeGreaterThan(0);
  });
  test("a vida da os dois eventos: o Rookie perde para o Gazimon muito acima dele, e brinca variado", () => {
    const ev = lendas(m);
    expect(ev.some(e => e.tipo === "hybris")).toBe(true);
    expect(ev.some(e => e.tipo === "variada")).toBe(true);
  });
  test("o replay do log da o mesmo forcaLutas e as mesmas lendas", () => {
    expect(replay.forcaLutas).toEqual(m.forcaLutas);
    expect(lendas(replay)).toEqual(lendas(m));
    expect(replay.assinatura()).toBe(m.assinatura());
  });
  test("o forcaLutas fica fora da assinatura", () => {
    const antes = m.assinatura();
    const salvo = m.forcaLutas.splice(0);
    expect(m.assinatura()).toBe(antes);
    m.forcaLutas.push(...salvo);
  });
});
