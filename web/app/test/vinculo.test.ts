/* Vinculo B, previsibilidade + desejo (docs/PLANO_ANALISE_V2_VINCULO.md, secao 2): motor/vinculo.ts reproduz o gabarito do Python
   (experiments/exportar_gabarito_vinculo.py) ate 1e-12, no modo de hoje (pets v2-v9) e no modo B (pets v10, `porSituacao`). Os
   pets v10 nunca abrem pedido e agrupam a coerencia por (acao, situacao); os v1-v9 nao mudam (gabaritos de paridade e os testes
   das versoes anteriores seguem iguais). */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CD, CVB, CVI, TPD, VERSAO_PET } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import { Vinculo, situacaoDe } from "../motor/vinculo.ts";
import { criarDono } from "../motor/donos.ts";
import { criarRng, hashSemente } from "../motor/rng.ts";
import type { AcaoDono, AcaoPet, Desejo } from "../motor/tipos.ts";

interface Op { op: string; tick: number; obs?: number[]; acao?: string; desejo?: { tipo: string; alvo: string; tick: number; intensidade: number } | null;
  acao_pet?: string | null; ref?: number; componente?: string; delta?: number; amostra?: number; peso?: number; teto?: number }
const G = JSON.parse(readFileSync(new URL("./gabaritos/vinculo_python.json", import.meta.url), "utf8")) as {
  config: { vinculo: Record<string, number>; situacao: { limiar_necessidade: number; limiar_energia: number; noite: number[]; ticks_por_dia: number } };
  ops: Op[]; hoje: Bloco; b: Bloco };
interface Bloco { valores: number[]; final: { valor: number; pedidos_pendentes: number[]; vontades_pendentes: [number, string][]; chaves_feedback: string[];
  n_amostras_por_componente: Record<string, number>; ultimo_ref_baixa: number | null; teto: number; situacao_atual: string | null } }
const TOL = 1e-12;

function aplicar(v: Vinculo, ops: Op[]): number[] {
  const valores: number[] = [];
  for (const o of ops) {
    if (o.op === "decisao") {
      const d = o.desejo ? { tick: o.desejo.tick, tipo: o.desejo.tipo as Desejo["tipo"], alvo: o.desejo.alvo, intensidade: o.desejo.intensidade } : null;
      v.decisao({ v: o.obs!, tdc: 0 }, o.acao as AcaoPet, o.tick, d);
    } else if (o.op === "dono") v.acaoDono(o.acao as AcaoDono, o.tick, (o.acao_pet ?? null) as AcaoPet | null, o.ref!);
    else if (o.op === "ajustar") v.ajustar(o.delta!, o.ref!);
    else if (o.op === "amostra") v._amostra(o.amostra!, o.peso!, null);
    else if (o.op === "limitar") v.limitar(o.teto!);
    else throw new Error("op desconhecida: " + o.op);
    valores.push(v.valor);
  }
  return valores;
}
function conferir(v: Vinculo, bloco: Bloco, valores: number[]): void {
  expect(valores.length).toBe(bloco.valores.length);
  for (let i = 0; i < valores.length; i++) expect(Math.abs(valores[i] - bloco.valores[i]), `valor na chamada ${i} (${G.ops[i].op})`).toBeLessThanOrEqual(TOL);
  expect(Math.abs(v.valor - bloco.final.valor)).toBeLessThanOrEqual(TOL);
  expect(v.pedidos).toEqual(bloco.final.pedidos_pendentes);
  expect(v.vontades).toEqual(bloco.final.vontades_pendentes);
  expect(Object.keys(v.feedbacks).sort()).toEqual(bloco.final.chaves_feedback);
  expect(v.ultRefBaixa).toBe(bloco.final.ultimo_ref_baixa);
  expect(v.teto).toBe(bloco.final.teto);
  expect(v.situacao).toBe(bloco.final.situacao_atual);
}

describe("vinculo B (pets v10) e paridade com o Python", () => {
  test("constantes = config do gabarito", () => {
    const c = G.config.vinculo;
    expect([CVI.inicial, CVI.alfa, CVI.pesoAtend, CVI.pesoCoer, CVI.pesoDesejo, CVI.janelaLat, CVI.janelaCoer, CVI.janelaDesejo])
      .toEqual([c.inicial, c.alfa, c.peso_atendimento, c.peso_coerencia, c.peso_desejo, c.janela_latencia_ticks, c.janela_coerencia_ticks, c.janela_desejo_ticks]);
    expect([CVB.limNec, CVB.limEnergia, TPD]).toEqual([G.config.situacao.limiar_necessidade, G.config.situacao.limiar_energia, G.config.situacao.ticks_por_dia]);
    expect(G.ops.length).toBeGreaterThan(1000);
  });

  test("paridade, modo de hoje: as mesmas chamadas, o mesmo valor ate 1e-12 (pets v2-v9)", () => {
    const v = new Vinculo();
    conferir(v, G.hoje, aplicar(v, G.ops));
    expect(G.hoje.final.n_amostras_por_componente.atendimento).toBeGreaterThan(0);
  });

  test("paridade, modo B: sem pedido, coerencia por (acao, situacao), o mesmo valor ate 1e-12 (pets v10)", () => {
    const v = new Vinculo(true);
    conferir(v, G.b, aplicar(v, G.ops));
    expect(G.b.final.n_amostras_por_componente.atendimento).toBeUndefined();
    expect(G.b.final.chaves_feedback.every(k => /\|[01]{3}$/.test(k))).toBe(true);
    expect(G.b.valores).not.toEqual(G.hoje.valores);
  });

  test("situacao: tres bits com os limiares do pet, a noite pela hora do vetor (arredondada)", () => {
    const obs = (fome = .9, hig = .9, en = .9, t = 600) => [fome, hig, en, .5, 1, 0, 0, t / TPD];
    expect(situacaoDe(obs())).toBe("000");
    expect(situacaoDe(obs(.49))).toBe("100");
    expect(situacaoDe(obs(.9, .2, .2))).toBe("110");
    expect(situacaoDe(obs(.9, .9, .9, 1320))).toBe("001");
    expect(situacaoDe(obs(.9, .9, .9, 419))).toBe("001");
    expect(situacaoDe(obs(.9, .9, .9, 420))).toBe("000");
    for (let t = 0; t < TPD; t++) expect(situacaoDe(obs(.9, .9, .9, t))[2]).toBe(t >= 1320 || t < 420 ? "1" : "0");
  });

  test("os ovos novos (v13) tem o vinculo B; a variante A (pets v1-v9) so existe no Vinculo, pela paridade com o Python", () => {
    expect(VERSAO_PET).toBe(15); expect(CVB.versaoPet).toBe(10);
    expect(new Motor(1).vinc.porSituacao).toBe(true); expect(new Motor(1).vinc.assinatura().length).toBe(8);
    expect(() => new Motor(1, 9)).toThrow(/versão/);
    expect(() => new Motor(1, 16)).toThrow();
  });

});
