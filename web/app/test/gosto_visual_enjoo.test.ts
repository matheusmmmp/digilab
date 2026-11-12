// O enjoo do protótipo P0 do gosto visual (2026-11-11, o pedido do Matheus: "Era pra ele ficar enjoado de uma mesma imagem"; as escolhas
// D-GV-ENJOO-1 a 6 em docs/registro/2026-11.md). Sem DOM (vitest em node). Cobre: a imagem parada por 30 min termina em "enjoou", sem voltar
// a olhar; a cena nova devolve o interesse; voltar à primeira logo depois não devolve; o desenjoo lento (horas); a exposição em U invertido;
// o "adorando" com o interesse alto; a memória de tamanho fixo e a troca determinística; o estado guardado, a migração da versão 1 e o erro
// alto numa memória estragada. E sem o enjoo migrante (D-GV-MIGRANTE-1 a 3, 2026-11-12): quadros distintos mas próximos nascem com o
// interesse alto, a volta ao primeiro não o acha desenjoado por arrasto, e o corte de cena não gasta protótipo. Todos os números são
// PROPOSTOS, SEM FONTE.
import { describe, expect, test } from "vitest";
import {
  INTERESSE_ADORANDO, PROTOTIPOS, RAIO_GENERALIZACAO, SALTO_CORTE, distancia, doTexto, estadoInicial, inatoDaSemente, paraTexto, passo,
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

describe("sem o enjoo migrante (D-GV-MIGRANTE-1 a 3)", () => {
  const ina = inatoDaSemente(SEMENTE);
  /* sete quadros parados: o meio e seis com um componente 0,25 para um lado; ficam a 0,0625 do meio e a 0,125 uns dos outros, todos
     dentro do raio de antes (0,15), como os quadros reais */
  const base = visto(0.5, 0.5, 0, 0.5).visao;
  const quadros: Sentido[] = [{ visao: base, som: null }];
  for (const k of ["cor", "brilho", "complexidade"] as const) for (const d of [-0.25, 0.25]) quadros.push({ visao: { ...base, [k]: base[k] + d }, som: null });
  /* o segundo do corte: o quadro novo com o pico de movimento, como o vetor da visão mede a troca de quadro */
  const pico = (s: Sentido): Sentido => ({ visao: { ...s.visao, movimento: 0.9 }, som: null });
  /* o primeiro por 10 min e os outros por 30 s cada, cada troca com o segundo do corte; devolve a leitura do 1º segundo depois do corte */
  const sequencia = (): { estado: EstadoGosto; primeiros: Leitura[]; nosCortes: Leitura[] } => {
    let e = assistir(ina, estadoInicial(), quadros[0]!, 600).estado;
    const primeiros: Leitura[] = [], nosCortes: Leitura[] = [];
    for (const q of quadros.slice(1)) {
      const c = passo(ina, e, pico(q), false); nosCortes.push(c.leitura);
      const r = assistir(ina, c.estado, q, 29); primeiros.push(r.leituras[0]!); e = r.estado;
    }
    return { estado: e, primeiros, nosCortes };
  };
  test("os sete quadros são distintos, mas ficam a menos de 0,15 uns dos outros e além do raio da generalização", () => {
    for (let i = 0; i < quadros.length; i++) for (let j = i + 1; j < quadros.length; j++) {
      const d = distancia(quadros[i]!.visao, { vetor: quadros[j]!.visao, enjoo: 0 });
      expect(d).toBeLessThan(0.15);
      expect(d).toBeGreaterThanOrEqual(RAIO_GENERALIZACAO);
    }
  });
  test("cada quadro novo começa com o interesse alto: não nasce enjoado do quadro de antes", () => {
    const { primeiros, nosCortes } = sequencia();
    expect(assistir(ina, estadoInicial(), quadros[0]!, 600).leituras.at(-1)!.interesse).toBeLessThan(0.3);
    for (const l of [...primeiros, ...nosCortes]) expect(l.interesse).toBeGreaterThan(0.9);
  });
  test("a volta ao primeiro quadro depois dos outros não o acha desenjoado por arrasto", () => {
    const { estado } = sequencia();
    expect(estado.memoria.some(p => JSON.stringify(p.vetor) === JSON.stringify(quadros[0]!.visao))).toBe(true);
    const c = passo(ina, estado, pico(quadros[0]!), false), volta = assistir(ina, c.estado, quadros[0]!, 30).leituras;
    expect(volta[0]!.interesse).toBeLessThan(0.3);
    expect(volta.every(l => l.interesse < 0.3)).toBe(true);
  });
  test("o protótipo fica parado no vetor em que nasceu", () => {
    const e = assistir(ina, assistir(ina, estadoInicial(), quadros[0]!, 60).estado, { visao: { ...base, cor: 0.51 }, som: null }, 60).estado;
    expect(e.memoria.map(p => p.vetor)).toEqual([quadros[0]!.visao]);
  });
  test("o corte de cena não gasta um protótipo com o vetor de passagem, nem com a memória cheia", () => {
    const A = quadros[0]!, B = quadros[1]!;
    expect(0.9 - 0).toBeGreaterThan(SALTO_CORTE);
    const e = assistir(ina, passo(ina, assistir(ina, estadoInicial(), A, 60).estado, pico(B), false).estado, B, 60).estado;
    expect(e.memoria.map(p => p.vetor)).toEqual([A.visao, B.visao]);
    let cheia = assistir(ina, estadoInicial(), quadros[0]!, 30).estado;
    for (const q of quadros.slice(1, PROTOTIPOS)) cheia = assistir(ina, cheia, q, 30).estado;
    expect(cheia.memoria).toHaveLength(PROTOTIPOS);
    const depois = passo(ina, cheia, pico(quadros[6]!), false).estado;
    expect(depois.memoria).toEqual(cheia.memoria.map(p => ({ vetor: p.vetor, enjoo: p.enjoo * Math.exp(-1 / 7200) })));
  });
});
