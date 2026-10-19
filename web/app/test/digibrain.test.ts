/* A leitura do painel DigiBrain (motor/digibrain.ts; docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 5) contra o Python
   (test/gabaritos/painel_digibrain_python.json, de experiments/exportar_gabarito_painel_digibrain.py), bit a bit no Node:
     - a leitura de cada decisao das vidas L0 e v11 do gabarito dos lobos (as barras, as chances, a sonda "quem decidiu" e a percepcao);
     - o "o que aprendeu" de cada desvio da secao `vontade`;
   e no Motor: o painel so existe nos v11 (PW-7), le a ultima decisao do cerebro e nao muda a vida. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { leituraAprendido, leituraDecisao, type LeituraDecisao } from "../motor/digibrain.ts";
import { tabelaPrior, type MotivoLobos } from "../motor/lobos.ts";
import { Motor } from "../motor/motor.ts";
import type { AcaoPet } from "../motor/tipos.ts";

interface VidaLobos { dono: string; semente: number; motivos: MotivoLobos[]; pesos_prior?: Record<string, Record<string, number[]>> }
const L = JSON.parse(readFileSync(new URL("./gabaritos/lobos_python.json", import.meta.url), "utf8")) as {
  l0: VidaLobos[]; v11: VidaLobos[];
  vontade: { vidas: { dono: string; decisoes: { desvio: Record<string, number> }[]; grade: { desvio: Record<string, number> }[] }[] };
};
type Aprendido = { acao: string; desvio: number }[];
const P = JSON.parse(readFileSync(new URL("./gabaritos/painel_digibrain_python.json", import.meta.url), "utf8")) as {
  S: number; receptores: string[];
  l0: { dono: string; decisoes: LeituraDecisao[] }[]; v11: { dono: string; decisoes: LeituraDecisao[] }[];
  aprendido: { dono: string; decisoes: Aprendido[]; grade: Aprendido[] }[];
};

/** as chaves em ordem, como o gabarito (sort_keys), para o toStrictEqual comparar tambem a ordem dos objetos */
function ordenar(v: unknown): unknown {
  if (Array.isArray(v)) return v.map(ordenar);
  if (v !== null && typeof v === "object") return Object.fromEntries(Object.keys(v).sort().map(k => [k, ordenar((v as Record<string, unknown>)[k])]));
  return v;
}

describe("a leitura do painel DigiBrain, contra o Python", () => {
  for (const secao of ["l0", "v11"] as const) {
    test(`as decisoes das vidas ${secao}: bit a bit`, () => {
      const prior0 = tabelaPrior(P.S);
      let n = 0, mudou = 0, corpo = 0;
      L[secao].forEach((vida, i) => {
        expect(P[secao][i].dono).toBe(vida.dono);
        const rec = secao === "v11" ? P.receptores : [];
        vida.motivos.forEach((m, k) => {
          const prior = vida.pesos_prior ?? prior0;
          const d = leituraDecisao(m, (prior as Record<string, Record<string, number[]>>)[m.regra][m.acao], P.S, rec);
          expect(ordenar(d)).toStrictEqual(ordenar(P[secao][i].decisoes[k]));
          n++; if (d.quem_decidiu.mudou) mudou++; if (d.barras.corpo !== 0) corpo++;
        });
      });
      expect(n).toBe(L[secao].length * 288);
      if (secao === "v11") { expect(mudou).toBeGreaterThan(0); expect(corpo).toBeGreaterThan(0); }
    });
  }

  test("o que aprendeu: por decisao e na grade, bit a bit", () => {
    L.vontade.vidas.forEach((v, i) => {
      expect(P.aprendido[i].dono).toBe(v.dono);
      v.decisoes.forEach((d, k) => expect(ordenar(leituraAprendido(d.desvio as Partial<Record<AcaoPet, number>>))).toStrictEqual(ordenar(P.aprendido[i].decisoes[k])));
      v.grade.forEach((d, k) => expect(ordenar(leituraAprendido(d.desvio as Partial<Record<AcaoPet, number>>))).toStrictEqual(ordenar(P.aprendido[i].grade[k])));
    });
  });

  test("falha alto: a decisao do motivo que nao e o aprendido mais o corpo, a linha do prior errada, a acao fora dos candidatos", () => {
    const m = L.v11[0].motivos.find(x => x.u !== null && x.regra === "tempo_livre")!, linha = L.v11[0].pesos_prior![m.regra][m.acao];
    expect(() => leituraDecisao(m, linha, P.S, P.receptores)).not.toThrow();
    const errado = structuredClone(m);
    errado.contribuicoes.decisao[m.acao] = errado.contribuicoes.decisao[m.acao]! + 1e-9;
    expect(() => leituraDecisao(errado, linha, P.S, P.receptores)).toThrow(/decisao do motivo/);
    expect(() => leituraDecisao(m, linha.slice(1), P.S, P.receptores)).toThrow(/linha do prior/);
    expect(() => leituraDecisao(m, linha, P.S, P.receptores.slice(1))).toThrow(/receptores/);
    expect(() => leituraDecisao({ ...m, acao: "dormir" }, linha, P.S, P.receptores)).toThrow(/fora dos candidatos/);
    expect(() => leituraAprendido({ voar: 1 } as unknown as Partial<Record<AcaoPet, number>>)).toThrow(/ACOES_PET_HOJE/);
  });
});

describe("o painel no Motor", () => {
  test("so nos v11 (PW-7); antes da primeira decisao, so o que aprendeu (nada, no recem-nascido)", () => {
    expect(new Motor(4242, 10).digibrain()).toBeNull();
    const m = new Motor(4242);
    expect(m.versao).toBe(11);
    const p = m.digibrain()!;
    expect(p.decisao).toBeNull();
    expect(p.aprendido).toEqual([]);
  });

  test("le a ultima decisao do cerebro e o desvio de agora, sem mudar a vida", () => {
    const a = new Motor(4242), b = new Motor(4242);
    for (let h = 0; h < 30; h++) {
      a.avancar(60); b.avancar(60);
      if (h % 4 === 0) { a.observar("acariciar"); b.observar("acariciar"); }
      if (h % 7 === 6) { a.observar("tapa"); b.observar("tapa"); }
      const p = a.digibrain()!, c = a.cerebro!, ult = c.ultimoMotivo!;
      expect(p.decisao).toStrictEqual(leituraDecisao(ult, c.prior[ult.regra][ult.acao], c.escala, c.receptoresNovos));
      expect(p.decisao!.acao).toBe(a.acao);
      expect(p.aprendido).toStrictEqual(leituraAprendido(c.desvioAprendido(a.observacaoAgora())));
    }
    expect(a.assinatura()).toBe(b.assinatura());
    expect(a.digibrain()!.aprendido.length).toBeGreaterThan(0);
  });
});
