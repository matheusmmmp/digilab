/* O G-PAR da etapa 1 do MVP (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, secao 4): o laco do pet com o mundo em TS (motor/motor_corpo_mundo.ts)
   contra os gabaritos do Python, o mesmo cenario nos dois lados (o mundo, o dono e o cerebro), decisao a decisao e bit a bit no Node:
     - o do produto (test/gabaritos/mvp_produto_python.json, experiments/exportar_gabarito_mvp_produto.py): o mundo do pet v12, sem
       arvores, so a racao do jogador (CMU_MVP; a opcao 1 do Matheus de 2026-10-24), gravado num commit proprio antes deste codigo;
     - o da etapa 0 (test/gabaritos/mvp_mundo_python.json, experiments/exportar_gabarito_mvp_mundo.py): o mundo da pesquisa (CMU, o
       layout padrao), o G-PAR do laco de pesquisa.
   Em cada decisao: a percepcao, os candidatos, o ocorrido (com os vistos novos), o Estado antes e depois do mundo,
   a percepcao depois e o corpo antes e depois (os quimicos, os receptores, com a curiosidade, e os estimulos: o pet, o andar, a comida, a
   novidade e a atividade). No fim, o log, o resumo do mundo, o corpo, o Estado e os proximos sorteios de cada fluxo.

   As tres vidas do cerebro A rodam o braco do v11 de verdade (bracoV11), sem as chaves do mundo e com o alvo padrao do motor (MV-2). A
   vida do instinto do mundo (que o TS nao tem) rejoga as acoes gravadas: o laco, o mundo e o corpo sao os do TS. O laco roda no modo
   `paridade`, que aceita o elogio e a bronca dos donos sinteticos do gabarito (o jogo nao os tem). Nenhum campo e mascarado. Os
   gabaritos nao mudam: o sha256 do da etapa 0 esta pinado no G2 (test/mvp_etapa0.test.ts), e o do produto, aqui. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { CMU, CMU_MVP, type ConfigMundo } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy } from "../motor/motor_corpo.ts";
import type { AcaoPet } from "../motor/tipos.ts";
import { json, ler, viver, type Rec, type Vida } from "./laco_gravado.ts";

/* (o nome, o arquivo, o mundo do laco, o sha256 pinado do produto; o da etapa 0 fica no G2) */
const CENARIOS: { nome: string; rel: string; cm: ConfigMundo; sha: string | null }[] = [
  { nome: "o produto (sem arvores)", rel: "./gabaritos/mvp_produto_python.json", cm: CMU_MVP,
    sha: "47f7af2c8e0cb98677f2e90680aed9607a742579be92819989c45065a4670956" },
  { nome: "a pesquisa (o layout padrao)", rel: "./gabaritos/mvp_mundo_python.json", cm: CMU, sha: null },
];

for (const cen of CENARIOS) {
  const { texto, g: G } = ler(cen.rel);
  const viverAqui = (v: Vida) => viver(v, cen.cm);
describe(`G-PAR do MVP, ${cen.nome}: o laco do pet com o mundo em TS = o Python, decisao a decisao`, () => {
  test("o gabarito: quatro vidas de 3 dias, o braco e o corpo do v11, o mesmo mundo do laco", () => {
    expect([G.versao, G.config.braco, G.config.dias, G.vidas.length]).toEqual([1, "P1-c-tapa", 3, 4]);
    expect(Object.fromEntries(Object.keys(G.config.corpo).map((k) => [k, (CCO_CORPO_V11 as unknown as Rec)[k]]))).toEqual(G.config.corpo);
    /* o do produto traz o mundo (a ConfigMundo do Python, campo a campo); o da etapa 0 e o CMU, o padrao do exportador dele */
    if (cen.sha !== null) {
      expect(createHash("sha256").update(texto).digest("hex")).toBe(cen.sha);
      expect(json(cen.cm)).toEqual(G.config.mundo);
      expect(cen.cm.layout.arvores).toEqual([]);
    } else expect(G.config.mundo).toBeUndefined();
  });

  for (const vida of G.vidas) {
    test(`${vida.nome} (semente ${vida.semente}): cada decisao, o corpo, o log e o mundo no fim`, () => {
      const { m } = viverAqui(vida);
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
    const decisoes = G.vidas.flatMap((v) => viverAqui(v).m.traco.filter((o) => o.op === "decisao")) as
      { ocorrido: { comeu: { tipo: string } | null; deslocamento: number } | null; corpo_depois: { estimulos: (string | number)[][]; receptores: Rec } }[];
    const estimulos = new Set(decisoes.flatMap((o) => o.corpo_depois.estimulos.map((s) => s[0])));
    expect([...estimulos].sort()).toEqual(["andar", "atividade", "comida", "novidade", "pet"]);
    expect(decisoes.filter((o) => o.ocorrido?.comeu?.tipo === "racao").length).toBeGreaterThanOrEqual(20);
    expect(decisoes.filter((o) => (o.ocorrido?.deslocamento ?? 0) > 0).length).toBeGreaterThanOrEqual(50);
    expect(decisoes.every((o) => "curiosidade" in o.corpo_depois.receptores)).toBe(true);
    /* no mundo do produto, so a racao do jogador: nenhuma fruta */
    if (cen.sha !== null) expect(decisoes.every((o) => !o.ocorrido?.comeu || o.ocorrido.comeu.tipo === "racao")).toBe(true);
  });
});
}

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
