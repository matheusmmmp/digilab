/* O G-PAR da chave do produto `decidirNaComida` (docs/TAREFA_V2_PRODUTO_FOME.md, o conserto (b)): o laco do pet com o mundo em TS, com a
   chave, contra o Python com a ConfigDecisaoNaComida ligada (test/gabaritos/decisao_na_comida_python.json,
   experiments/exportar_gabarito_decisao_na_comida.py), decisao a decisao e bit a bit no Node, pelo laco gravado do G-PAR do MVP
   (test/laco_gravado.ts). O dono e um roteiro com a racao no meio do intervalo (o dono sintetico age no passo das decisoes, e ali a chave
   nao muda nada). Cada vida vem com a chave ligada e desligada; a desligada e a vida de hoje. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { C, CMU_MVP } from "../motor/constantes.ts";
import { json, ler, viver, type Rec, type Vida } from "./laco_gravado.ts";

const { texto, g: G } = ler("./gabaritos/decisao_na_comida_python.json");
const SHA = "30c6f9cf051e86ed5a81bd73d32bcf571d8ea8ecc3416dfcd147c8f037a34c48";
type VidaChave = Vida & { decisao_na_comida: boolean };
const VIDAS = G.vidas as VidaChave[];
const decisoesEm = (v: Vida) => v.traco.filter(o => o.op === "decisao").map(o => o.tick as number);
const racoesEm = (v: Vida) => v.traco.filter(o => o.op === "deixar_comida").map(o => o.tick as number);

describe("G-PAR da decisao na comida: o laco do TS com a chave = o Python, decisao a decisao", () => {
  test("o gabarito: duas sementes, cada uma com a chave ligada e desligada, no mundo do produto", () => {
    expect(createHash("sha256").update(texto).digest("hex")).toBe(SHA);
    expect(json(CMU_MVP)).toEqual(G.config.mundo);
    expect(VIDAS.map(v => [v.semente, v.decisao_na_comida])).toEqual([[101, true], [101, false], [202, true], [202, false]]);
  });

  for (const vida of VIDAS) {
    test(`${vida.nome}, chave ${vida.decisao_na_comida ? "ligada" : "desligada"}: cada decisao, o log, o mundo e o corpo no fim`, () => {
      const { m } = viver(vida, CMU_MVP, { decidirNaComida: vida.decisao_na_comida });
      expect(m.traco.length).toBe(vida.traco.length);
      for (let i = 0; i < vida.traco.length; i++) {
        const esperado = vida.traco[i] as Rec, obtido = m.traco[i];
        if (JSON.stringify(obtido) === JSON.stringify(esperado)) continue;
        for (const k of Object.keys(esperado)) expect(obtido[k], `traco[${i}] (${esperado.op} no tick ${esperado.tick}): ${k}`).toEqual(esperado[k]);
      }
      expect(m.log).toEqual(vida.log);
      expect(json(m.mundo.resumo())).toEqual(vida.resumo);
      expect({ q: { ...m.corpo.q }, receptores: m.corpo.receptores() }).toEqual(vida.corpo_fim);
      const e = m.estado;
      expect({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira, tick: e.tick }).toEqual(vida.estado_fim);
      expect(m.mundo.decisoes.length).toBe(vida.decisoes);
    });
  }

  test("ligada, cada racao no meio do intervalo traz uma decisao no mesmo tick, e a seguinte vem 15 ticks depois; desligada, nao", () => {
    for (const [lig, des] of [[VIDAS[0], VIDAS[1]], [VIDAS[2], VIDAS[3]]]) {
      const dl = decisoesEm(lig), dd = decisoesEm(des), racoes = racoesEm(lig);
      expect(racoes).toEqual(racoesEm(des));
      /* ligada: toda racao tem uma decisao no mesmo tick, e a seguinte vem um intervalo depois (salvo outra racao antes) */
      for (const t of racoes) {
        expect(dl).toContain(t);
        const i = dl.indexOf(t);
        if (i + 1 < dl.length && !racoes.some(r => r > t && r < dl[i + 1])) expect(dl[i + 1] - t).toBe(C.intervalo);
      }
      /* desligada: as decisoes so no passo de 15 (a racao no meio do intervalo espera) */
      expect(racoes.filter(t => !dd.includes(t)).length).toBeGreaterThan(5);
      expect(dd.every((t, i) => i === 0 || t - dd[i - 1] === C.intervalo)).toBe(true);
      expect(lig.decisoes).toBeGreaterThan(des.decisoes);
    }
  });
});
