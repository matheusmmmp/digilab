// O enjoo do protótipo P0 do gosto visual (2026-11-11, o pedido do Matheus: "Era pra ele ficar enjoado de uma mesma imagem"; as escolhas
// D-GV-ENJOO-1 a 6 em docs/registro/2026-11.md). Sem DOM (vitest em node). Cobre: a imagem parada por 30 min termina em "enjoou", sem voltar
// a olhar; a cena nova devolve o interesse; voltar à primeira logo depois não devolve; o desenjoo lento (horas); a exposição em U invertido;
// o "adorando" com o interesse alto; a memória de tamanho fixo e a troca determinística; o estado guardado, a migração da versão 1 e o erro
// alto numa memória estragada. Todos os números são PROPOSTOS, SEM FONTE.
import { describe, expect, test } from "vitest";
import {
  INTERESSE_ADORANDO, PROTOTIPOS, RAIO_GENERALIZACAO, distancia, doTexto, estadoInicial, inatoDaSemente, paraTexto, passo,
  type EstadoGosto, type Inato, type Leitura, type Sentido,
} from "../src/gostoVisual/gosto.ts";

const SEMENTE = 101, MEIA_HORA = 1800;
const limitar = (x: number): number => (x < 0 ? 0 : x > 1 ? 1 : x);
const visto = (cor: number, brilho: number, movimento: number, complexidade: number): Sentido => ({ visao: { cor, brilho, movimento, complexidade }, som: null });
/* a cena A e a cena B: o ótimo do pet com dois componentes levados 0,32 para o meio (a cor e o movimento em A, o brilho e o detalhe em
   B; o ótimo fica em [0,15; 0,85], então nada é cortado); as duas agradam, e a distância entre elas passa do raio da generalização (o
   teste confere) */
const cenas = (ina: Inato): { A: Sentido; B: Sentido } => {
  const o = ina.otimo, d = 0.32, meio = (x: number): number => (x > 0.5 ? x - d : x + d);
  return { A: visto(meio(o.cor), o.brilho, meio(o.movimento), o.complexidade), B: visto(o.cor, meio(o.brilho), o.movimento, meio(o.complexidade)) };
};
const assistir = (ina: Inato, e0: EstadoGosto, s: Sentido, n: number): { estado: EstadoGosto; leituras: Leitura[] } => {
  let e = e0; const leituras: Leitura[] = [];
  for (let i = 0; i < n; i++) { const r = passo(ina, e, s, false); e = r.estado; leituras.push(r.leitura); }
  return { estado: e, leituras };
};

describe("o enjoo da imagem parada", () => {
  const ina = inatoDaSemente(SEMENTE), { A, B } = cenas(ina);
  const meiaHora = assistir(ina, estadoInicial(), A, MEIA_HORA);

  test("as cenas do teste: A e B ficam além do raio da generalização uma da outra, e A agrada de cara", () => {
    expect(distancia(B.visao, { vetor: A.visao, enjoo: 0 })).toBeGreaterThanOrEqual(RAIO_GENERALIZACAO);
    expect(meiaHora.leituras[0]!.olhando).toBe(true);
  });
  test("30 min da mesma imagem: o pet olha, enjoa, para e não volta a olhar enquanto ela não muda", () => {
    const ls = meiaHora.leituras, parou = ls.findIndex(l => !l.olhando);
    expect(parou).toBeGreaterThan(0);
    expect(ls.slice(parou).every(l => !l.olhando)).toBe(true);
    expect(ls[parou]!.reacao).toBe("enjoou");
    const fim = ls.at(-1)!;
    expect(fim.olhando).toBe(false);
    expect(fim.reacao).toBe("enjoou");
    expect(fim.interesse).toBeLessThan(0.1);
  });
  test("a cena nova devolve o interesse: o pet volta a olhar logo", () => {
    const b = assistir(ina, meiaHora.estado, B, 60).leituras;
    expect(b[0]!.novidade).toBeGreaterThanOrEqual(RAIO_GENERALIZACAO);
    expect(b[0]!.interesse).toBeGreaterThan(0.95);
    expect(b[0]!.reacao).not.toBe("enjoou");
    expect(b.slice(0, 10).some(l => l.olhando)).toBe(true);
  });
  test("voltar à primeira imagem logo depois não desenjoa", () => {
    const depoisDeB = assistir(ina, meiaHora.estado, B, 60).estado;
    const volta = assistir(ina, depoisDeB, A, 30).leituras;
    expect(volta[0]!.interesse).toBeLessThan(0.1);
    expect(volta.every(l => !l.olhando)).toBe(true);
    expect(volta.at(-1)!.reacao).toBe("enjoou");
  });
  test("o desenjoo é lento: depois de 4 h vendo outra coisa, o interesse na primeira imagem volta quase todo", () => {
    const depois = assistir(ina, meiaHora.estado, B, 4 * 3600).estado;
    const r = passo(ina, depois, A, false).leitura;
    expect(r.interesse).toBeGreaterThan(0.8);
    expect(r.olhando).toBe(true);
  });
  test("o 'adorando' pede o interesse alto: olhando com o agrado alto e o interesse gasto é só 'olhando'", () => {
    const ls = meiaHora.leituras;
    expect(ls.some(l => l.olhando && l.agrado > 0.7 && l.interesse <= INTERESSE_ADORANDO)).toBe(true);
    for (const l of ls) if (l.reacao === "adorando") expect(l.interesse).toBeGreaterThan(INTERESSE_ADORANDO);
    expect(ls.filter(l => l.olhando && l.interesse <= INTERESSE_ADORANDO).every(l => l.reacao === "olhando")).toBe(true);
  });
});

describe("a exposição com saturação (o U invertido)", () => {
  test("numa cena fora do ótimo, o agrado sobe com a exposição, chega a um pico e cai com o tédio", () => {
    const ina = inatoDaSemente(SEMENTE), o = ina.otimo;
    const s = visto(limitar(o.cor + 0.2), limitar(o.brilho + 0.2), o.movimento, o.complexidade);
    const ag = assistir(ina, estadoInicial(), s, MEIA_HORA).leituras.map(l => l.agrado);
    const pico = Math.max(...ag), quando = ag.indexOf(pico);
    expect(pico).toBeGreaterThan(ag[0]!);
    expect(quando).toBeGreaterThan(0);
    expect(quando).toBeLessThan(MEIA_HORA - 1);
    expect(ag.at(-1)!).toBeLessThan(ag[0]!);
  });
});

describe("a memória do enjoo", () => {
  const ina = inatoDaSemente(SEMENTE);
  const seis = (): EstadoGosto => {
    let e = assistir(ina, estadoInicial(), visto(0, 0, 0, 0), 300).estado;
    for (const x of [0.2, 0.4, 0.6, 0.8, 1]) e = assistir(ina, e, visto(x, x, x, x), 5).estado;
    return e;
  };
  const novo = visto(0.5, 0, 1, 0.5);
  test("tem tamanho fixo, a troca é determinística e sai o protótipo de menor enjoo; o mais enjoado fica", () => {
    const antes = seis();
    expect(antes.memoria).toHaveLength(PROTOTIPOS);
    const menor = antes.memoria.reduce((j, p, i) => (p.enjoo < antes.memoria[j]!.enjoo ? i : j), 0);
    const e = assistir(ina, antes, novo, 5).estado;
    expect(assistir(ina, seis(), novo, 5).estado).toEqual(e);
    expect(e.memoria).toHaveLength(PROTOTIPOS);
    /* os de antes, sem o de menor enjoo, na mesma ordem; o novo no fim */
    expect(e.memoria.slice(0, -1).map(p => p.vetor)).toEqual(antes.memoria.filter((_, i) => i !== menor).map(p => p.vetor));
    expect(e.memoria.at(-1)!.vetor).toEqual(novo.visao);
    const enjoos = e.memoria.map(p => p.enjoo);
    expect(e.memoria[0]!.vetor).toEqual({ cor: 0, brilho: 0, movimento: 0, complexidade: 0 });
    expect(enjoos[0]).toBe(Math.max(...enjoos));
  });
  test("o estado guardado leva a memória, e o pet volta enjoado da mesma imagem", () => {
    const { A } = cenas(ina), e = assistir(ina, estadoInicial(), A, MEIA_HORA).estado, t = paraTexto(e);
    expect(Object.keys(JSON.parse(t))).toEqual(["v", "exposicao", "carinho", "memoria", "segundosJuntos", "carinhos"]);
    const d = doTexto(t);
    expect(d.memoria).toEqual(e.memoria);
    expect(passo(ina, d, A, false).leitura.olhando).toBe(false);
  });
  test("a versão 1 (de antes do enjoo) migra com a memória vazia; uma memória estragada falha alto", () => {
    const z = { cor: 0, brilho: 0, movimento: 0, complexidade: 0, volume: 0, variacao: 0, timbre: 0 };
    const v1 = doTexto(JSON.stringify({ v: 1, exposicao: z, carinho: z, segundosJuntos: 10, carinhos: 1 }));
    expect(v1.memoria).toEqual([]);
    expect(v1.segundosJuntos).toBe(10);
    const v2 = (memoria: unknown): string => JSON.stringify({ v: 2, exposicao: z, carinho: z, memoria, segundosJuntos: 0, carinhos: 0 });
    expect(() => doTexto(v2(undefined))).toThrow(/memória/);
    expect(() => doTexto(v2(Array.from({ length: PROTOTIPOS + 1 }, () => ({ vetor: { cor: 0 }, enjoo: 0 }))))).toThrow(/memória/);
    expect(() => doTexto(v2([{ vetor: { cor: 2 }, enjoo: 0 }]))).toThrow(/memoria\[0\]\.cor/);
    expect(() => doTexto(v2([{ vetor: { sabor: 0.5 }, enjoo: 0 }]))).toThrow(/memoria\[0\]\.sabor/);
    expect(() => doTexto(v2([{ vetor: { cor: 0.5 }, enjoo: 1.5 }]))).toThrow(/enjoo/);
    expect(() => doTexto(v2([{ vetor: {}, enjoo: 0 }]))).toThrow(/vazio/);
  });
});
