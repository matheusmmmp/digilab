/* Os Bits, a moeda do jogo (docs/PLANO_V3_MOEDA.md, etapa MO1): a conta dos feitos (src/bits.ts), o evento "bits" do registro do Tamer
   (src/tamer.ts, versao 9) e o ciclo no estado do app (src/jogo.ts). O pet nao muda: os feitos sao derivados do replay e ficam fora da
   assinatura. */
import { describe, expect, test } from "vitest";
import { CTR, CUIDADO_NA_HORA, DUR_EVO, Motor, TICK_INICIAL, TPD, hashSemente } from "../motor/index.ts";
import { BITS, bitsDaMedalha, feitosDoPet } from "../src/bits.ts";
import { CHAVE, petExemplo, textoSave, type Armazenamento } from "../src/save.ts";
import { iniciarJogo, mudarMotor, pagarNivel, tamerAtual, trocarMotor } from "../src/jogo.ts";
import { CHAVE_TAMER, Tamer, conferirBits, conferirBitsDoNivel, gravarTamer, lerTamer, type EventoTamer } from "../src/tamer.ts";

const armaz = (dados: Record<string, string> = {}) => {
  const a: Armazenamento & { dados: Record<string, string>; removeItem(k: string): void } = {
    dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; }, removeItem(k) { delete dados[k]; },
  };
  return a;
};
const GAZIMON = "npc_tier1_brutamontes";
const FIM_ROOKIE = DUR_EVO.bebe + DUR_EVO.crianca;
/** o Rookie treinado (como no tamer.test.ts): na luta da POC um Rookie sem treino nao vence o Gazimon */
function rookieTreinado(semente: number, ate = FIM_ROOKIE - 30): Motor {
  const m = new Motor(semente);
  m.avancar(DUR_EVO.bebe + 30);
  while (m.e.tick - TICK_INICIAL < ate) {
    if (m.treino.podeTocar(m.e.tick) && m.treino.fadiga + CTR.fadigaSessao < CTR.limiarPausa && !m.e.dormindo) m.treinar("levantar_pedra");
    m.avancar(10);
  }
  return m;
}
/** luta contra o rival ate `n` vitorias (devolve as lutas jogadas) */
function vencer(m: Motor, k: string, n = 1): number {
  let v = 0;
  for (let i = 1; i <= 80; i++) {
    if (m.lutarPoc(k, hashSemente("bits", m.semente, m.log.length), "campo").venceu && ++v === n) return i;
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  }
  throw new Error(`nao venceu ${n} vezes em 80 lutas`);
}
/** um motor de mentira, so com o que a conta dos Bits le */
const falso = (x: Partial<Pick<Motor, "vida5" | "feitosCuidado" | "evolucoes" | "lugares">>): Motor =>
  ({ vida5: { lutas: [] }, feitosCuidado: [], evolucoes: [], lugares: [], ...x }) as unknown as Motor;

describe("a conta dos feitos (src/bits.ts)", () => {
  test("a vitoria paga pela faixa; a repeticao no mesmo dia paga a metade; o dia seguinte paga cheio; derrota e torneio nao pagam", () => {
    const L = (tick: number, rival: string, resultado: "vitoria" | "derrota" = "vitoria") => ({ tick, rival, resultado, lesao: false });
    const lugares = [{ rivais: [GAZIMON], est: "crianca" }, { rivais: ["npc_x"], est: "adolescente" }] as unknown as Motor["lugares"];
    const f = feitosDoPet(falso({
      lugares,
      vida5: { lutas: [L(10, GAZIMON), L(20, GAZIMON), L(30, GAZIMON), L(40, GAZIMON, "derrota"), L(50, "npc_x"), L(60 + TPD, GAZIMON), L(70, "liga"), L(80, "salao")] } as Motor["vida5"],
    }));
    expect(f.map(x => [x.id, x.valor])).toEqual([["luta:0", 10], ["luta:1", 5], ["luta:2", 2], ["luta:4", 25], ["luta:5", 10]]);
  });
  test("o chamado e o cuidado tem o teto do dia; a pausa fica fora dele", () => {
    const fc = [...Array.from({ length: 12 }, (_, i) => ({ tick: i, tipo: "chamado" as const })), { tick: 13, tipo: "cuidado" as const },
      { tick: 14, tipo: "pausa" as const }, { tick: TPD + 1, tipo: "cuidado" as const }];
    const f = feitosDoPet(falso({ feitosCuidado: fc }));
    const dia0 = f.filter(x => x.tick < TPD && x.origem !== "pausa").reduce((s, x) => s + x.valor, 0);
    expect(dia0).toBe(BITS.tetoCuidadoDia);
    expect(f.filter(x => x.origem === "pausa")).toEqual([{ id: "pausa:13", valor: BITS.pausa, origem: "pausa", tick: 14 }]);
    expect(f.find(x => x.tick === TPD + 1)?.valor).toBe(BITS.cuidado);
  });
  test("a evolucao paga pelo estagio a que chegou; a 1a medalha, 5x a faixa do lugar", () => {
    const f = feitosDoPet(falso({ evolucoes: [{ tick: 5, estagio: "crianca" }, { tick: 9, estagio: "adolescente" }] as Motor["evolucoes"] }));
    expect(f.map(x => [x.id, x.valor])).toEqual([["evolucao:crianca", 50], ["evolucao:adolescente", 100]]);
    expect(bitsDaMedalha("campina")).toBe(50);
    expect(() => bitsDaMedalha("lua")).toThrow(/desconhecida/);
  });
});

describe("os feitos no motor (Motor.feitosCuidado)", () => {
  test("o chamado do bebe atendido vira feito; o cuidado do Rookie so conta abaixo do limiar; o replay refaz igual e a assinatura nao muda", () => {
    const m = new Motor(21);
    for (let i = 0; i < 200 && m.estagioAtual === "bebe"; i++) {
      const ab = m.chamadosAbertos();
      if (ab.length) m.observar(ab[0] === "fome" ? "alimentar" : ab[0] === "higiene" ? "limpar" : "acariciar");
      m.avancar(5);
    }
    const chamados = m.feitosCuidado.filter(f => f.tipo === "chamado").length;
    expect(chamados).toBeGreaterThan(0);
    expect(m.estagioAtual).toBe("crianca");
    /* o Rookie com o corpo cheio: o cuidado nao conta */
    const antes = m.feitosCuidado.length;
    m.observar("limpar");
    expect(m.e.higiene).toBeGreaterThanOrEqual(CUIDADO_NA_HORA.higiene);
    expect(m.feitosCuidado.length).toBe(antes);
    /* deixado sem cuidado ate a fome cair abaixo do limiar: a comida conta */
    while (m.e.fome >= CUIDADO_NA_HORA.fome) m.avancar(20);
    m.observar("alimentar");
    expect(m.feitosCuidado[m.feitosCuidado.length - 1]).toEqual({ tick: m.e.tick, tipo: "cuidado" });
    const r = Motor.reproduzir(m.semente, m.log, m.versao);
    expect(r.feitosCuidado).toEqual(m.feitosCuidado);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(m.assinatura()).not.toContain("feitosCuidado");
  });
});

describe("o evento \"bits\" no registro do Tamer (versao 9)", () => {
  test("pagar, gravar e reproduzir: o mesmo saldo; conferir de novo nao paga duas vezes", () => {
    const m = rookieTreinado(22);
    vencer(m, GAZIMON);
    const t = new Tamer(), a = armaz();
    const novos = conferirBits(t, m, 1000);
    expect(novos.length).toBeGreaterThan(0);
    expect(novos.some(g => g.origem === "luta" && g.valor === BITS.faixa.crianca)).toBe(true);
    expect(novos.some(g => g.origem === "evolucao" && g.id === "evolucao:crianca")).toBe(true);
    expect(conferirBits(t, m, 2000)).toEqual([]);
    gravarTamer(a, t);
    expect(JSON.parse(a.dados[CHAVE_TAMER]).versao).toBe(10);
    const r = lerTamer(a);
    expect(r.bits).toBe(t.bits);
    expect(r.bits).toBe(novos.reduce((s, g) => s + g.valor, 0));
    expect(conferirBits(r, m)).toEqual([]);
  });
  test("a 1a medalha paga uma vez por Tamer; o nivel paga cada nivel uma vez", () => {
    const t = new Tamer(), m = new Motor(5);
    t.ganhar("campina", m, 1);
    expect(conferirBits(t, m).filter(g => g.origem === "lider").map(g => g.valor)).toEqual([50]);
    expect(conferirBits(t, new Motor(6)).filter(g => g.origem === "lider")).toEqual([]);
    expect(conferirBitsDoNivel(t, 3).length).toBe(3);
    expect(conferirBitsDoNivel(t, 4).map(g => g.id)).toEqual(["nivel:4"]);
    expect(conferirBitsDoNivel(t, 4)).toEqual([]);
  });
  test("feito repetido, origem desconhecida, valor invalido e campo faltando falham alto", () => {
    const ok: EventoTamer = ["bits", { id: "luta:0", pet: 7, valor: 10, origem: "luta", tick: 500, quando: 1 }];
    expect(() => Tamer.reproduzir([ok, ok])).toThrow(/duas vezes/);
    expect(Tamer.reproduzir([ok, ["bits", { ...ok[1], pet: 8 }]]).bits).toBe(20);   /* o mesmo id em outro pet e outro feito */
    expect(() => Tamer.reproduzir([["bits", { ...ok[1], origem: "loteria" }] as unknown as EventoTamer])).toThrow(/origem desconhecida/);
    expect(() => Tamer.reproduzir([["bits", { ...ok[1], valor: 0 }]])).toThrow(/valor inválido/);
    expect(() => Tamer.reproduzir([["bits", { ...ok[1], valor: 2.5 }]])).toThrow(/valor inválido/);
    expect(() => Tamer.reproduzir([["bits", { ...ok[1], id: "" }]])).toThrow(/sem o id/);
    const { tick: _t, ...semTick } = ok[1];
    expect(() => Tamer.reproduzir([["bits", semTick] as unknown as EventoTamer])).toThrow(/sem tick/);
  });
  test("o registro 8 de antes abre (sem Bits) e passa a gravar a 9", () => {
    const a = armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 8, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 1, forma: "Agumon", tick: 480 }]] }) });
    const t = lerTamer(a);
    expect(t.n).toBe(1);
    expect(t.bits).toBe(0);
  });
});

describe("o ciclo no app (src/jogo.ts)", () => {
  test("a vitoria do pet do jogador vira Bits gravados no Tamer; o pet de exemplo nao paga", () => {
    const m = rookieTreinado(23), a = armaz({ [CHAVE]: textoSave(m) });
    iniciarJogo(a);
    const b0 = tamerAtual().bits;
    expect(b0).toBeGreaterThan(0);                    /* a evolucao para Rookie e os feitos de antes, pagos na abertura */
    mudarMotor(x => { vencer(x, GAZIMON); });
    expect(tamerAtual().bits).toBeGreaterThan(b0);
    expect(lerTamer(a).bits).toBe(tamerAtual().bits);
    pagarNivel(2);
    expect(lerTamer(a).bits).toBe(tamerAtual().bits);
    expect(tamerAtual().pago("nivel", "nivel:2", 0)).toBe(true);
    /* sem save: o pet de exemplo das boas-vindas */
    iniciarJogo(armaz());
    expect(tamerAtual().bits).toBe(0);
    /* o exemplo intocado com a origem "save" (depois de um descarte) tambem nao paga, mesmo com o historico de cuidado dele */
    const ex = petExemplo();
    expect(feitosDoPet(ex).length).toBeGreaterThan(0);
    trocarMotor(ex, "save");
    expect(tamerAtual().bits).toBe(0);
  });
});
