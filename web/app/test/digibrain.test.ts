/* A leitura do painel DigiBrain (motor/digibrain.ts; docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 5) contra o Python
   (test/gabaritos/painel_digibrain_python.json, de experiments/exportar_gabarito_painel_digibrain.py), bit a bit no Node:
     - a leitura de cada decisao das vidas L0 e v11 do gabarito dos lobos (as barras, as chances, a sonda "quem decidiu" e a percepcao);
     - o "o que aprendeu" de cada desvio da secao `vontade`;
     - o mapa dos pesos (test/gabaritos/mapa_digibrain_python.json): as arestas do prior e dos pesos do fim das vidas v11 e as acesas
       em cada decisao;
   e no Motor: o painel so existe nos v11 (PW-7), le a ultima decisao do cerebro e nao muda a vida. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { leituraAprendido, leituraDecisao, mapaDecisao, mapaPesos, type ArestaMapa, type LeituraDecisao, type MapaDecisao } from "../motor/digibrain.ts";
import { tabelaPrior, type MotivoLobos } from "../motor/lobos.ts";
import { Motor } from "../motor/motor.ts";
import type { AcaoPet } from "../motor/tipos.ts";
import { estadoSelo } from "../src/seloDigiBrain.ts";

type Tab = Record<string, Record<string, number[]>>;
interface VidaLobos { dono: string; semente: number; motivos: MotivoLobos[]; pesos_prior?: Tab; pesos?: Tab; pesos_corpo?: Tab }
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

const M = JSON.parse(readFileSync(new URL("./gabaritos/mapa_digibrain_python.json", import.meta.url), "utf8")) as {
  S: number; teto: number; receptores: string[]; l0: ArestaMapa[];
  pesos: { dono: string; arestas: ArestaMapa[] }[]; v11: { dono: string; decisoes: MapaDecisao[] }[];
};
const zeros = (t: Tab): Tab => Object.fromEntries(Object.entries(t).map(([r, a]) => [r, Object.fromEntries(Object.entries(a).map(([k, v]) => [k, v.map(() => 0)]))]));

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

describe("o mapa dos pesos, contra o Python", () => {
  test("as arestas: o prior do L0 e os pesos do fim das vidas v11, bit a bit", () => {
    const prior0 = tabelaPrior(M.S);
    expect(ordenar(mapaPesos(prior0, prior0, {}, {}, M.S, M.teto, []))).toStrictEqual(ordenar(M.l0));
    let aprendidas = 0;
    L.v11.forEach((v, i) => {
      expect(M.pesos[i].dono).toBe(v.dono);
      const a = mapaPesos(v.pesos_prior!, v.pesos!, zeros(v.pesos_corpo!), v.pesos_corpo!, M.S, M.teto, M.receptores);
      expect(ordenar(a)).toStrictEqual(ordenar(M.pesos[i].arestas));
      aprendidas += a.filter(x => x.aprendido !== 0).length;
      expect(a.some(x => M.receptores.includes(x.entrada))).toBe(true);
    });
    expect(aprendidas).toBeGreaterThan(0);
  });

  test("as acesas de cada decisao das vidas v11, bit a bit; o termo da acao escolhida e o da percepcao", () => {
    L.v11.forEach((v, i) => {
      v.motivos.forEach((m, k) => {
        const linha = v.pesos_prior![m.regra][m.acao], d = mapaDecisao(m, linha, M.S, M.receptores);
        expect(ordenar(d)).toStrictEqual(ordenar(M.v11[i].decisoes[k]));
        const termo = new Map(d.arestas.map(x => [x.entrada, x.termo]));
        for (const p of leituraDecisao(m, linha, M.S, M.receptores).percepcao) expect(termo.get(p.entrada)).toBe(p.termo);
        expect(Math.max(...d.arestas.map(x => x.forca))).toBe(1);
      });
    });
  });

  test("falha alto: regra fora do mapa, linha curta, peso alem do teto", () => {
    const p0 = tabelaPrior(M.S) as unknown as Tab;
    expect(() => mapaPesos({ ...p0, bola_no_cenario: p0.tempo_livre }, { ...p0, bola_no_cenario: p0.tempo_livre }, {}, {}, M.S, M.teto, [])).toThrow(/fora do mapa/);
    const curto = structuredClone(p0); curto.tempo_livre.brincar = curto.tempo_livre.brincar.slice(1);
    expect(() => mapaPesos(p0, curto, {}, {}, M.S, M.teto, [])).toThrow(/esperados/);
    const alem = structuredClone(p0); alem.tempo_livre.brincar[1] = M.teto + 1;
    expect(() => mapaPesos(p0, alem, {}, {}, M.S, M.teto, [])).toThrow(/teto/);
    const m = L.v11[0].motivos[0];
    expect(() => mapaDecisao(m, [1], M.S, M.receptores)).toThrow(/linha do prior/);
  });
});

describe("o painel no Motor", () => {
  test("so nos v11 (PW-7); antes da primeira decisao, so o que aprendeu (nada, no recem-nascido)", () => {
    const m = new Motor(4242);
    expect(m.versao).toBe(13);                                      /* os v12 (o v11 com o mundo) e os v13 (a luta em tempo real) tambem */
    const p = m.digibrain()!;
    expect(p.decisao).toBeNull();
    expect(p.aprendido).toEqual([]);
    expect(p.mapa.acesas).toBeNull();
    expect(p.mapa.arestas.every(x => x.aprendido === 0)).toBe(true);           /* o recem-nascido: so o prior */
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
      expect(p.mapa.acesas).toStrictEqual(mapaDecisao(ult, c.prior[ult.regra][ult.acao], c.escala, c.receptoresNovos));
      expect(p.mapa.acesas!.acao).toBe(a.acao);
      expect(p.mapa.arestas).toStrictEqual(mapaPesos(c.prior, c.pesos, c.priorCorpo, c.pesosCorpo, c.escala, c.cfg.aprendiz!.teto, c.receptoresNovos));
    }
    expect(a.assinatura()).toBe(b.assinatura());
    expect(a.digibrain()!.aprendido.length).toBeGreaterThan(0);
  });
});

describe("o selo do painel", () => {
  const vivo = { replay: false, velocidade: 10, nascendo: 0, erroSave: false, lutaSegura: false, morto: false };
  test("ao vivo so com o tempo andando; replay num replay; senao pausado", () => {
    expect(estadoSelo(vivo)).toBe("vivo");
    expect(estadoSelo({ ...vivo, replay: true })).toBe("replay");
    expect(estadoSelo({ ...vivo, replay: true, velocidade: 0 })).toBe("replay");
    for (const mudanca of [{ velocidade: 0 }, { nascendo: 3 }, { erroSave: true }, { lutaSegura: true }, { morto: true }]) {
      expect(estadoSelo({ ...vivo, ...mudanca })).toBe("pausado");
    }
  });
});
