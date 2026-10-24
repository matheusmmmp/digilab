/* O G-PAR da etapa 1 do MVP (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, secao 4): o laco do pet com o mundo em TS (motor/motor_corpo_mundo.ts)
   contra o gabarito do Python gravado na etapa 0 (test/gabaritos/mvp_mundo_python.json, experiments/exportar_gabarito_mvp_mundo.py),
   decisao a decisao e bit a bit no Node: a percepcao, os candidatos, o ocorrido (com os vistos novos), o Estado antes e depois do mundo,
   a percepcao depois e o corpo antes e depois (os quimicos, os receptores, com a curiosidade, e os estimulos: o pet, o andar, a comida, a
   novidade e a atividade). No fim, o log, o resumo do mundo, o corpo, o Estado e os proximos sorteios de cada fluxo.

   As tres vidas do cerebro A rodam o braco do v11 de verdade (bracoV11), sem as chaves do mundo e com o alvo padrao do motor (MV-2). A
   vida do instinto do mundo (que o TS nao tem) rejoga as acoes gravadas: o laco, o mundo e o corpo sao os do TS. O laco roda no modo
   `paridade`, que aceita o elogio e a bronca dos donos sinteticos do gabarito (o jogo nao os tem). O gabarito nao muda: o sha256 dele
   esta pinado no G2 (test/mvp_etapa0.test.ts). */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { type BracoConsequencia } from "../motor/lobos.ts";
import { MotorCorpoMundo, type OcorridoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo, type PoliticaCorpo } from "../motor/motor_corpo.ts";
import { type PercepcaoMundo } from "../motor/mundo.ts";
import { bracoV11 } from "../motor/pet_v11.ts";
import type { AcaoPet } from "../motor/tipos.ts";

type Rec = Record<string, unknown>;
interface Vida {
  nome: string; cerebro: "a_v11" | "instinto"; dono: string; lugar: string; semente: number; dias: number; log: EventoCorpo[]; traco: Rec[];
  resumo: Rec; corpo_fim: Rec; estado_fim: Rec; proximos: Record<string, { random: number[]; randrange16: number[] }>; decisoes: number;
}
const G = JSON.parse(readFileSync(new URL("./gabaritos/mvp_mundo_python.json", import.meta.url), "utf8")) as {
  versao: number; config: { corpo: Rec; braco: string; dias: number; intervalo_decisao_ticks: number }; vidas: Vida[];
};
const json = (v: unknown): unknown => JSON.parse(JSON.stringify(v));

const percepcao = (p: PercepcaoMundo): Rec => ({ x: p.x, y: p.y, regiao: p.regiao, vistos: p.vistos.map((v) => [...v]), cheiro: p.cheiro,
  direcao_cheiro: p.direcao_cheiro, alvo_pendente: p.alvo_pendente });
const estadoMundo = (e: { fome: number; energia: number; humor: number; sujeira: number }): Rec =>
  ({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira });

/** o MotorMundoCorpoGravado do exportador, do lado do TS: grava o traco do mundo e o corpo em cada decisao; nao muda nada da vida */
class LacoGravado extends MotorCorpoMundo {
  readonly traco: Rec[] = [];
  private op: Rec | null = null;
  private corpoAgora(): Rec { return { q: { ...this.corpo.q }, receptores: { ...this.corpo.receptores() } }; }

  protected override antesDaDecisao(): PercepcaoMundo {
    const p = super.antesDaDecisao();
    this.op = { op: "decisao", tick: this.estado.tick, fome_antes: this.estado.fome, percepcao: percepcao(p), corpo_antes: this.corpoAgora() };
    return p;
  }

  protected override consequenciaDoMundo(acao: AcaoPet): OcorridoMundo | null {
    const op = this.op!;
    Object.assign(op, { acao, estado: estadoMundo(this.estado), com_gancho: false });
    const ocorrido = super.consequenciaDoMundo(acao);
    const regs = this.mundo.decisoes;
    Object.assign(op, { regra: regs[regs.length - 1].regra, candidatos: this.mundo.ultimosCandidatos, ocorrido,
                        depois: estadoMundo(this.estado), percepcao_depois: percepcao(this.mundo.perceber(this.estado.tick)) });
    return ocorrido;
  }

  protected override consequencia(acao: AcaoPet): OcorridoMundo | null {
    const ocorrido = super.consequencia(acao);
    const op = this.op!;
    this.op = null;
    op.corpo_depois = { ...this.corpoAgora(), estimulos: this.estimulos.map((s) => [...s]) };
    this.traco.push(json(op) as Rec);                     // o retrato da decisao, sem referencias que o motor mude depois
    return ocorrido;
  }

  override comidaDoDono(tipo: string, x: number, y: number): void {
    this.traco.push({ op: "deixar_comida", tick: this.estado.tick, tipo, x, y });
    super.comidaDoDono(tipo, x, y);
  }
}

/** o cerebro da vida: o braco do v11 (as vidas do A) ou as acoes gravadas (a do instinto do mundo, que o TS nao tem) */
function cerebroDa(vida: Vida): { politica: PoliticaCorpo; regra: () => string | null; braco: BracoConsequencia | null } {
  if (vida.cerebro === "a_v11") {
    const braco = bracoV11();
    return {
      braco, regra: () => braco.cerebro.ultimaRegra,
      politica: {
        agir: (o, rng) => braco.agir(o, rng), observar: (t) => braco.observar(t),
        consequenciaCorpo: (a, oc, d) => braco.consequenciaCorpo(a, oc, d), receberAcaoDono: (a, t) => braco.receberAcaoDono(a, t),
        mudancaNoCorpo: (a, d) => braco.mudancaNoCorpo(a, d),
      },
    };
  }
  const gravadas = vida.traco.filter((o) => o.op === "decisao") as { acao: AcaoPet; regra: string | null }[];
  let k = 0, regra: string | null = null;
  return {
    braco: null, regra: () => regra,
    politica: {
      agir() { const d = gravadas[k++]; regra = d.regra; return d.acao; },
      observar() {}, consequenciaCorpo() {}, receberAcaoDono() {}, mudancaNoCorpo() {},
    },
  };
}

function viver(vida: Vida) {
  const c = cerebroDa(vida);
  const m = new LacoGravado(c.politica, vida.semente, CCO_CORPO_V11, estadoNascimentoPy(0), { regra: c.regra, paridade: true });
  for (const e of vida.log) m.aplicarEvento(e);
  return { m, braco: c.braco };
}

describe("G-PAR do MVP: o laco do pet com o mundo em TS = o Python, decisao a decisao", () => {
  test("o gabarito e o da etapa 0: quatro vidas de 3 dias, o braco e o corpo do v11", () => {
    expect([G.versao, G.config.braco, G.config.dias, G.vidas.length]).toEqual([1, "P1-c-tapa", 3, 4]);
    expect(Object.fromEntries(Object.keys(G.config.corpo).map((k) => [k, (CCO_CORPO_V11 as unknown as Rec)[k]]))).toEqual(G.config.corpo);
  });

  for (const vida of G.vidas) {
    test(`${vida.nome} (semente ${vida.semente}): cada decisao, o corpo, o log e o mundo no fim`, () => {
      const { m } = viver(vida);
      expect(m.traco.length).toBe(vida.traco.length);
      for (let i = 0; i < vida.traco.length; i++) {
        const esperado = vida.traco[i], obtido = m.traco[i];
        if (JSON.stringify(obtido) === JSON.stringify(esperado)) continue;
        /* a primeira divergencia, campo a campo (a condicao de parada da etapa: reportar a primeira decisao divergente) */
        for (const k of Object.keys(esperado)) expect(obtido[k], `traco[${i}] (${esperado.op} no tick ${esperado.tick}): ${k}`).toEqual(esperado[k]);
        expect(obtido, `traco[${i}]`).toEqual(esperado);
      }
      expect(m.log).toEqual(vida.log);
      expect(json(m.mundo.resumo())).toEqual(vida.resumo);
      expect({ q: { ...m.corpo.q }, receptores: m.corpo.receptores() }).toEqual(vida.corpo_fim);
      const e = m.estado;
      expect({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira, tick: e.tick }).toEqual(vida.estado_fim);
      expect(m.mundo.decisoes.length).toBe(vida.decisoes);
      const mu = m.mundo;
      for (const [fluxo, r] of [["arvores", mu.rngArvores], ["bola", mu.rngBola], ["sujeira", mu.rngSujeira], ["alvo", mu.rngAlvo]] as const) {
        const prox = { random: [r.random(), r.random(), r.random()], randrange16: [r.randrange(1 << 16), r.randrange(1 << 16), r.randrange(1 << 16)] };
        expect(prox, `proximos de ${fluxo}`).toEqual(vida.proximos[fluxo]);
      }
    });
  }

  test("o laco cobre o que o MVP pede: comer a racao deixada, andar, e o corpo com a curiosidade, a novidade e a atividade", () => {
    const decisoes = G.vidas.flatMap((v) => viver(v).m.traco.filter((o) => o.op === "decisao")) as
      { ocorrido: { comeu: { tipo: string } | null; deslocamento: number } | null; corpo_depois: { estimulos: (string | number)[][]; receptores: Rec } }[];
    const estimulos = new Set(decisoes.flatMap((o) => o.corpo_depois.estimulos.map((s) => s[0])));
    expect([...estimulos].sort()).toEqual(["andar", "atividade", "comida", "novidade", "pet"]);
    expect(decisoes.filter((o) => o.ocorrido?.comeu?.tipo === "racao").length).toBeGreaterThanOrEqual(20);
    expect(decisoes.filter((o) => (o.ocorrido?.deslocamento ?? 0) > 0).length).toBeGreaterThanOrEqual(50);
    expect(decisoes.every((o) => "curiosidade" in o.corpo_depois.receptores)).toBe(true);
  });
});

describe("o laco com o mundo: o dono e os eventos", () => {
  const sem = { agir: () => "ocioso" as AcaoPet, observar() {}, consequenciaCorpo() {}, receberAcaoDono() {}, mudancaNoCorpo() {} };
  test("o alimentar sai (vira o deixar_comida); o elogio e a bronca so no modo paridade", () => {
    const m = new MotorCorpoMundo(sem, 101);
    expect(() => m.observar("alimentar")).toThrow(/deixar_comida/);
    expect(() => m.observar("elogiar")).toThrow(/fora do v11/);
    expect(() => m.observar("repreender")).toThrow(/fora do v11/);
    const p = new MotorCorpoMundo(sem, 101, CCO_CORPO_V11, estadoNascimentoPy(), { paridade: true });
    expect(() => p.observar("elogiar")).not.toThrow();
  });
  test("deixar_comida invalido falha alto antes do log: fora do mapa, nao inteiro, tipo desconhecido", () => {
    const m = new MotorCorpoMundo(sem, 101);
    expect(() => m.deixarComida("racao", 1024, 10)).toThrow(/fora do mapa/);
    expect(() => m.deixarComida("racao", 10, -1)).toThrow(/fora do mapa/);
    expect(() => m.deixarComida("racao", 1.5, 10)).toThrow(/nao inteira/);
    expect(() => m.deixarComida("pizza", 10, 10)).toThrow(/desconhecido/);
    expect(m.log).toEqual([]);
    expect(() => m.aplicarEvento({ tick: 0, tipo: "deixar_comida", valor: "racao|10" })).toThrow(/malformado/);
    expect(() => m.aplicarEvento({ tick: 0, tipo: "outro" as "avanco", valor: 1 })).toThrow(/desconhecido/);
  });
});
