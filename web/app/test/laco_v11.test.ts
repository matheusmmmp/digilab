/* O gate do laco (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 4): as quatro vidas da secao v11 do gabarito do Python
   (test/gabaritos/lobos_python.json) rodam pelo laco do corpo em TS (motor/motor_corpo.ts), evento a evento do log, e nao so pelos
   ganchos gravados como no G-PAR-L1 (test/lobos_v11.test.ts). Bit a bit no Node:
     - os ganchos que o laco faz ao cerebro sao os que o motor do Python fez, na ordem e com o que levaram (a observacao com os receptores
       do corpo, a transicao, o ocorrido do corpo, a acao do dono e o tick, o antes e o depois do carinho);
     - cada motivo, e no fim os pesos, os pesos do corpo, o aprendizado, a memoria e emocao e os canais;
     - o estado do motor no fim (test/gabaritos/lobos_laco_python.json, do mesmo exportador): os drives, a sujeira, o sono, os cuidados, a
       acao atual e o corpo inteiro (a quimica, a digestao, o estagio, a janela do tedio e o metabolismo), e as acoes do pet com o tick.
   A sujeira sai da rng do ambiente do Python (o RandomPy do mundo.ts, o Mersenne Twister do CPython); o sorteio do cerebro, da rng da
   politica, as duas como no engine.Motor. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CCO_CORPO_V11, configCorpo } from "../motor/corpo.ts";
import { type BracoConsequencia, type MotivoLobos, type ObservacaoLobos } from "../motor/lobos.ts";
import { bracoV11 } from "../motor/pet_v11.ts";
import { MotorCorpo, type EventoCorpo, type PoliticaCorpo } from "../motor/motor_corpo.ts";

type Gancho = unknown[];
interface VidaV11 {
  dono: string; semente: number; log: EventoCorpo[]; motivos: MotivoLobos[]; pesos: unknown; pesos_prior: unknown; pesos_corpo: unknown;
  aprendizado: unknown; corpo: unknown; memoria_emocao: unknown; canais: unknown; ganchos: Gancho[];
}
interface LacoV11 { dono: string; semente: number; estado: Record<string, unknown>; acoes_pet: [number, string][] }
const ler = (nome: string) => JSON.parse(readFileSync(new URL(`./gabaritos/${nome}`, import.meta.url), "utf8"));
const G = ler("lobos_python.json") as { config_v11: { corpo: Record<string, unknown>; receptores: string[] }; v11: VidaV11[] };
const L = ler("lobos_laco_python.json") as { versao: number; braco: string; dias: number; v11: LacoV11[] };
const RECEPTORES = G.config_v11.receptores;

/** [Estado.vetor, ticks_desde_cuidado, receptores na ordem do gabarito]; um receptor a mais ou a menos falha alto */
function obs(o: ObservacaoLobos): unknown[] {
  const corpo = o.corpo as Record<string, number>;
  if (Object.keys(corpo).sort().join() !== [...RECEPTORES].sort().join()) throw new Error(`receptores fora do v11: ${Object.keys(corpo)}`);
  return [[...o.v], o.tdc, RECEPTORES.map((r) => corpo[r])];
}

/** o _Gravador do exportador, do lado do TS: grava cada chamada do laco ao cerebro, no formato do gabarito, e repassa */
function gravador(braco: BracoConsequencia): { politica: PoliticaCorpo; ganchos: Gancho[] } {
  const ganchos: Gancho[] = [];
  const politica: PoliticaCorpo = {
    agir(o, rng) { ganchos.push(["agir", ...obs(o)]); return braco.agir(o, rng); },
    observar(t) { ganchos.push(["observar", t.acao, ...obs(t.observacao), ...obs(t.observacaoSeguinte)]); braco.observar(t); },
    consequenciaCorpo(acao, ocorrido, depois) {
      ganchos.push(["consequencia_corpo", acao, { acao: ocorrido.acao, estimulos: ocorrido.estimulos.map((e) => [...e]) }, ...obs(depois)]);
      braco.consequenciaCorpo(acao, ocorrido, depois);
    },
    receberAcaoDono(acao, tick) { ganchos.push(["dono", acao, tick]); braco.receberAcaoDono(acao, tick); },
    mudancaNoCorpo(antes, depois) { ganchos.push(["carinho", ...obs(antes), ...obs(depois)]); braco.mudancaNoCorpo(antes, depois); },
  };
  return { politica, ganchos };
}

function viver(vida: VidaV11, semente = vida.semente, log: EventoCorpo[] = vida.log) {
  const braco = bracoV11();
  const g = gravador(braco);
  const motor = new MotorCorpo(g.politica, semente);
  for (const e of log) motor.aplicarEvento(e);
  return { motor, braco, ganchos: g.ganchos };
}

describe("o gate do laco: as vidas do v11 pelo laco do corpo em TS = o Python, bit a bit", () => {
  test("os dois gabaritos sao das mesmas vidas", () => {
    expect([L.versao, L.braco, L.dias]).toEqual([1, "P1-c-tapa", 3]);
    expect(L.v11.map((v) => [v.dono, v.semente])).toEqual(G.v11.map((v) => [v.dono, v.semente]));
    /* o corpo do laco e o do ponto do v11, chave a chave */
    expect(Object.fromEntries(Object.keys(G.config_v11.corpo).map((k) => [k, (CCO_CORPO_V11 as unknown as Record<string, unknown>)[k]])))
      .toEqual(G.config_v11.corpo);
  });

  G.v11.forEach((vida, i) => {
    test(`${vida.dono} ${vida.semente}: os ganchos, os motivos, o cerebro no fim e o motor no fim`, () => {
      const { motor, braco, ganchos } = viver(vida);
      expect(motor.log).toStrictEqual(vida.log);
      expect(ganchos.length).toBe(vida.ganchos.length);
      for (let k = 0; k < ganchos.length; k++) expect(ganchos[k], `gancho ${k}`).toStrictEqual(vida.ganchos[k]);
      expect(braco.cerebro.motivos).toStrictEqual(vida.motivos);
      const interno = braco.cerebro.estadoInterno();
      expect(interno.pesos).toStrictEqual(vida.pesos);
      expect(interno.pesos_prior).toStrictEqual(vida.pesos_prior);
      expect(interno.pesos_corpo).toStrictEqual(vida.pesos_corpo);
      expect(interno.aprendizado).toStrictEqual(vida.aprendizado);
      expect(interno.memoria_emocao).toStrictEqual(vida.memoria_emocao);
      expect(interno.canais).toStrictEqual(vida.canais);
      expect(interno.corpo).toStrictEqual(vida.corpo);
      const fim = L.v11[i];
      expect(motor.estadoDict()).toStrictEqual(fim.estado);
      expect(motor.acoesPet).toStrictEqual(fim.acoes_pet);
      expect([motor.consequencias, motor.mudancas]).toEqual([vida.motivos.length, vida.log.filter((e) => e.valor === "acariciar").length]);
    });
  });

  test("a sujeira e o sono saem da rng do ambiente: as vidas sujam, dormem e alimentam com sorteio", () => {
    const sujas = L.v11.filter((v) => (v.estado.sujeira as number) > 0).length;
    const dormiu = L.v11.every((v) => v.acoes_pet.some(([, a]) => a === "dormir"));
    expect(sujas).toBeGreaterThan(0);
    expect(dormiu).toBe(true);
    expect(G.v11.every((v) => v.log.some((e) => e.valor === "alimentar"))).toBe(true);
  });

  test("o mesmo log duas vezes da a mesma vida (determinismo)", () => {
    const a = viver(G.v11[2]), b = viver(G.v11[2]);
    expect(b.ganchos).toStrictEqual(a.ganchos);
    expect(b.motor.estadoDict()).toStrictEqual(a.motor.estadoDict());
  });

  test("controles negativos: outra semente do motor e um evento trocado sao pegos", () => {
    const vida = G.v11[0];
    const outra = viver(vida, vida.semente + 1);
    expect(outra.ganchos).not.toStrictEqual(vida.ganchos);
    const k = vida.log.findIndex((e) => e.valor === "limpar");
    const log = vida.log.map((e, j) => (j === k ? { ...e, valor: "alimentar" } : e));
    expect(viver(vida, vida.semente, log).motor.estadoDict()).not.toStrictEqual(L.v11[0].estado);
  });

  test("falha alto: o elogio e a bronca no v11, um evento fora do tick e o banheiro no corpo", () => {
    const mk = () => new MotorCorpo(gravador(bracoV11()).politica, 101);
    expect(() => mk().observar("elogiar")).toThrow(/elogio/);
    expect(() => mk().observar("repreender")).toThrow(/elogio/);
    expect(() => mk().aplicarEvento({ tick: 5, tipo: "avanco", valor: 15 })).toThrow(/tick/);
    expect(() => mk().aplicarEvento({ tick: 0, tipo: "nada" as "avanco", valor: 1 })).toThrow(/desconhecido/);
    expect(() => configCorpo({ ...CCO_CORPO_V11, banheiro: true })).toThrow(/banheiro/);
    expect(() => new MotorCorpo(gravador(bracoV11()).politica, 101, configCorpo({ ligada: true }))).toThrow(/drives novos/);
  });
});
