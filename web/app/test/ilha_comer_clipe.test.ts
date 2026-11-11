// O clipe Comer na ilha (docs/TAREFA_V3_SPRITES_ACOES.md, M3; SA-4 e SA-5): as regras do cenaAcao.ts (escolherComer) e o corte alargado
// (ilha/corte.ts). So vista, sem DOM (vitest em node). O atlas e o sintetico de arte propria da M2 (test/atlas_acoes_sintetico.json).
//   - a linha "comer (acao do pet)" da tabela 3.2: o Comer em laco enquanto a acao dura, no minimo um ciclo;
//   - a linha "comeu a racao": a entrada nova em mundo.consumos toca o Comer uma vez, virado para a comida; acima de 1 h/s sai;
//   - o gesto de hoje e o clipe nunca juntos, e sem o clipe (sem o atlas ou num sprite sem o Comer) a queda explicita para o gesto;
//   - a reacao do dono ocupa um ciclo por cima do Comer e depois ele volta;
//   - o corte do Comer (com o Comer_objeto) e o do Attack_1 tem o mesmo centro e o mesmo pe do corte do sprite.
import { beforeEach, describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CENA_ACAO, SEM_GESTO, comerAgora, comidaPerto, emoteAgora, escolherComer, esquecerCoco, esquecerComer, esquecerReacao, gestoAgora, gestoDaReacao,
  mostrarReacao, type EntradaComer, type Reacao } from "../src/telas/pet/cenaAcao.ts";
import { alargarCorte, unirCaixas, type Corte } from "../src/telas/pet/ilha/corte.ts";
import { juntarClipes, type AtlasClipes, type AtlasUp, type Quadro } from "../src/atlas.ts";

const atlas = juntarClipes({ atlas: "a.png", ms_por_quadro: 120, sprites: {}, pecas: {} },
  JSON.parse(readFileSync(new URL("./atlas_acoes_sintetico.json", import.meta.url), "utf8")) as AtlasClipes);
const soma = (ms: number[]) => ms.reduce((a, b) => a + b, 0);
/** o ciclo do Comer do sprite sintetico forma_a: 133 + 100 + 67 = 300 ms */
const CICLO = soma(atlas.sprites.forma_a.clipes!.Comer!.ms);

const base: EntradaComer = { chave: "1", acao: "ocioso", consumos: 0, alvo: null, ciclo: CICLO, velocidade: 10, andando: false, pausa: false, donoDesde: null, comidaPerto: true };
const em = (t: number, e: Partial<EntradaComer> = {}) => escolherComer({ ...base, ...e }, t);
const cena = (acao: string) => ({ acao, sujeira: 0, chave: "1" });
const relaxou = (desde: number): Reacao => ({ desde, tipo: "relaxou", carinho: 1, medo: 0 });
beforeEach(() => { esquecerComer(); esquecerReacao(); esquecerCoco(); });

describe("o Comer em laco: a acao comer do pet", () => {
  test("com o clipe, a acao comer toca o Comer em laco desde o primeiro quadro; o ocioso nao", () => {
    expect(em(0).tocou).toBeNull();
    const a = em(16, { acao: "comer" });
    expect(a).toMatchObject({ tocou: "clipe", desde: 16, momento: false });
    for (let t = 16; t < 16 + 5 * CICLO; t += 16) expect(em(t, { acao: "comer" })).toMatchObject({ tocou: "clipe", desde: 16 });
    expect(comerAgora().tocou).toBe("clipe");
  });
  test("o minimo e um ciclo inteiro, mesmo que a acao troque logo (6 h/s: a acao dura ~40 ms)", () => {
    em(0, { acao: "comer", velocidade: 360 });
    for (let t = 40; t < CICLO; t += 20) expect(em(t, { acao: "ocioso", velocidade: 360 }).tocou, `t=${t}`).toBe("clipe");
    expect(em(CICLO, { acao: "ocioso", velocidade: 360 }).tocou).toBeNull();
  });
  test("a acao troca no meio de um ciclo: o clipe vai ate o fim dele, sem cortar a mordida", () => {
    em(0, { acao: "comer" });
    em(1.5 * CICLO, { acao: "comer" });
    expect(em(1.6 * CICLO, { acao: "explorar" }).tocou).toBe("clipe");
    expect(em(2 * CICLO - 1, { acao: "explorar" }).tocou).toBe("clipe");
    expect(em(2 * CICLO, { acao: "explorar" }).tocou).toBeNull();
  });
  test("andando, o laco cede ao Run; na Pausa, nada", () => {
    expect(em(0, { acao: "comer", andando: true }).tocou).toBeNull();
    expect(em(10, { acao: "comer" }).tocou).toBe("clipe");
    expect(em(20, { acao: "comer", andando: true }).tocou).toBeNull();
    expect(em(30, { acao: "comer", pausa: true }).tocou).toBeNull();
  });
  test("a troca de pet esquece o comer", () => {
    em(0, { acao: "comer" });
    expect(em(10, { acao: "ocioso", chave: "2" }).tocou).toBeNull();
  });
  test("falha alto: um ciclo que nao e positivo", () => {
    expect(() => em(0, { acao: "comer", ciclo: 0 })).toThrow(/ciclo/);
    expect(() => em(0, { acao: "comer", ciclo: Number.NaN })).toThrow(/ciclo/);
  });
});

describe("o comeu a racao: a entrada nova em mundo.consumos", () => {
  test("toca o Comer uma vez, virado para a comida, e acaba (a acao ja nao e comer)", () => {
    em(0, { consumos: 3 });                                     // a primeira olhada nao conta
    expect(em(10, { consumos: 3 }).tocou).toBeNull();
    const a = em(20, { consumos: 4, alvo: [5, 7] });
    expect(a).toMatchObject({ tocou: "clipe", momento: true, desde: 20, alvo: [5, 7] });
    expect(em(20 + CICLO - 1, { consumos: 4 }).tocou).toBe("clipe");
    expect(em(20 + CICLO, { consumos: 4 }).tocou).toBeNull();
  });
  test("cede so ao golpe, nao ao passo: andando, o pet para de andar e come", () => {
    em(0);
    expect(em(10, { consumos: 1, andando: true, alvo: [1, 1] })).toMatchObject({ tocou: "clipe", momento: true });
  });
  test("se a acao segue comer, o laco continua do fim do momento, sem pulo", () => {
    em(0, { acao: "comer" });
    em(10, { acao: "comer", consumos: 1, alvo: [2, 2] });
    expect(em(10 + CICLO, { acao: "comer", consumos: 1 })).toMatchObject({ tocou: "clipe", momento: false, desde: 10 + CICLO });
  });
  test("acima de 1 h/s o comeu a racao sai; a 1 h/s fica", () => {
    em(0);
    expect(em(10, { consumos: 1, velocidade: 360 }).tocou).toBeNull();
    expect(em(20, { consumos: 2, velocidade: CENA_ACAO.momentoVelMax }).tocou).toBe("clipe");
  });
  test("o momento nao interrompe a reacao do dono: espera ela acabar ate momentoEsperaMs, e depois sai", () => {
    em(0);
    mostrarReacao(relaxou(100));
    expect(em(110, { consumos: 1 })).toMatchObject({ tocou: null, reacao: true });
    expect(em(100 + CICLO, { consumos: 1 })).toMatchObject({ tocou: "clipe", momento: true, desde: 100 + CICLO });
    esquecerComer(); esquecerReacao();
    em(0);
    em(10, { consumos: 1, donoDesde: 10, ciclo: 2 * CENA_ACAO.momentoEsperaMs });
    expect(em(10 + 2 * CENA_ACAO.momentoEsperaMs, { consumos: 1, donoDesde: 10, ciclo: 2 * CENA_ACAO.momentoEsperaMs }).tocou).toBeNull();
  });
});

describe("a reacao do dono por cima do Comer (SA-5)", () => {
  test("o toque ocupa um ciclo do Comer, com o gesto da reacao; depois o Comer volta do comeco", () => {
    em(0, { acao: "comer" });
    mostrarReacao(relaxou(500));
    for (let t = 500; t < 500 + CICLO; t += 25) {
      const c = em(t, { acao: "comer" });
      expect(c, `t=${t}`).toMatchObject({ tocou: null, reacao: true });
      expect(gestoAgora(cena("comer"), t, false, true, false, false)).toEqual(gestoDaReacao(relaxou(500), t));
    }
    expect(em(500 + CICLO, { acao: "comer" })).toMatchObject({ tocou: "clipe", desde: 500 + CICLO });
  });
  test("o flash de uma acao do dono tambem ocupa um ciclo; a segunda acao recomeca a reacao", () => {
    em(0, { acao: "comer" });
    expect(em(400, { acao: "comer", donoDesde: 400 }).reacao).toBe(true);
    expect(em(400 + CICLO - 1, { acao: "comer", donoDesde: 400 + CICLO / 2 }).reacao).toBe(true);
    expect(em(400 + 1.5 * CICLO - 1, { acao: "comer", donoDesde: 400 + CICLO / 2 }).reacao).toBe(true);
    expect(em(400 + 1.5 * CICLO, { acao: "comer", donoDesde: 400 + CICLO / 2 }).tocou).toBe("clipe");
  });
  test("o minimo de um ciclo vale tambem depois da reacao: o toque logo no comeco, e a acao ja trocou", () => {
    em(0, { acao: "comer" });
    mostrarReacao(relaxou(50));
    em(60, { acao: "ocioso" });
    const volta = 50 + CICLO;
    for (let t = volta; t < volta + CICLO; t += 25) expect(em(t, { acao: "ocioso" }).tocou, `t=${t}`).toBe("clipe");
    expect(em(volta + CICLO, { acao: "ocioso" }).tocou).toBeNull();
  });
  test("quem ja cumpriu o ciclo e trocou de acao nao volta a comer depois da reacao", () => {
    em(0, { acao: "comer" });
    em(2 * CICLO + 10, { acao: "comer" });
    mostrarReacao(relaxou(2 * CICLO + 20));
    em(2 * CICLO + 30, { acao: "ocioso" });
    expect(em(3 * CICLO + 20, { acao: "ocioso" }).tocou).toBeNull();
  });
});

describe("o gesto e o clipe nunca juntos; a queda sem o clipe", () => {
  test("com o clipe no corpo, nenhum gesto, nenhuma carne sobre a cabeca; sem ele, o gesto e a carne de hoje", () => {
    for (let t = 0; t < 4 * CICLO; t += 7) {
      const c = em(t, { acao: "comer" }), clipe = c.tocou === "clipe";
      expect(clipe).toBe(true);
      expect(gestoAgora(cena("comer"), t, false, true, false, clipe)).toBe(SEM_GESTO);
      expect(emoteAgora(cena("comer"), t, clipe)).toBeNull();
    }
    expect(gestoAgora(cena("comer"), 210, false, true, false, false)).not.toEqual(SEM_GESTO);
    expect(emoteAgora(cena("comer"), 210, false)).toBe("carne");
  });
  test("sem o atlas (ou num sprite sem o Comer): ciclo null, a queda explicita para o gesto, e o momento nao toca", () => {
    em(0, { ciclo: null });
    for (let t = 10; t < 3 * CICLO; t += 10) {
      const c = em(t, { acao: "comer", ciclo: null, consumos: 1 });
      expect(c.tocou).toBe("gesto");
      expect(gestoAgora(cena("comer"), t + 105, false, true, false, false).estica).toBeLessThan(1);
    }
    expect(em(1000, { acao: "ocioso", ciclo: null, consumos: 2 }).tocou).toBeNull();
    expect(em(1010, { acao: "comer", ciclo: null, andando: true }).tocou).toBeNull();
  });
  test("o sprite sintetico sem o Comer (o NPC) da ciclo null pelo atlas", () => {
    expect(atlas.sprites.npc_sintetico.clipes?.Comer).toBeUndefined();
    expect(soma(atlas.sprites.forma_b.clipes!.Comer!.ms)).toBe(300);
  });
});

describe("o corte alargado: o mesmo centro e o mesmo pe", () => {
  /** a caixa de um quadro do atlas dentro da caixa do sprite (o retangulo do quadro; vazio = null), mais 1 da folga de quadroAtlas */
  const caixa = (q: Quadro): Corte | null => q[2] === 0 ? null : { x0: q[4] + 1, x1: q[4] + q[2], pe: q[5] + q[3] + 1 };
  test("em todo sprite sintetico, o Comer com o Comer_objeto cabe no corte e guarda o centro e o pe do Idle", () => {
    for (const [k, s] of Object.entries(atlas.sprites)) {
      const cl = s.clipes!, b = unirCaixas([...cl.Idle!.quadros, ...(cl.Run?.quadros ?? [])].map(caixa))!;
      if (!cl.Comer) continue;
      const caixas = cl.Comer.quadros.map((q, i) => unirCaixas([caixa(q), caixa(cl.Comer_objeto!.quadros[i])]));
      const c = alargarCorte(b, caixas);
      expect(c.x0 + c.x1, k).toBe(b.x0 + b.x1);
      expect(c.pe, k).toBe(b.pe);
      for (const x of caixas) if (x) { expect(c.x0).toBeLessThanOrEqual(x.x0); expect(c.x1).toBeGreaterThanOrEqual(x.x1); }
    }
  });
  test("qualquer conjunto de caixas: o centro em meios texels igual, o pe igual, tudo dentro (inclusive alem da borda do quadro)", () => {
    let r = 12345;
    const rnd = (n: number) => { r = (r * 1103515245 + 12345) % 2147483648; return r % n; };
    for (let caso = 0; caso < 500; caso++) {
      const x0 = rnd(30), b: Corte = { x0, x1: x0 + rnd(30), pe: 10 + rnd(20) };
      const caixas = Array.from({ length: 1 + rnd(6) }, () => { const a = rnd(70) - 10; return rnd(5) === 0 ? null : { x0: a, x1: a + rnd(25), pe: rnd(60) }; });
      const c = alargarCorte(b, caixas);
      expect(c.x0 + c.x1).toBe(b.x0 + b.x1);
      expect(c.pe).toBe(b.pe);
      expect(c.x0).toBeLessThanOrEqual(b.x0);
      expect(c.x1).toBeGreaterThanOrEqual(b.x1);
      for (const x of caixas) if (x) { expect(c.x0).toBeLessThanOrEqual(x.x0); expect(c.x1).toBeGreaterThanOrEqual(x.x1); }
    }
  });
  test("sem nada fora do corte, ele nao cresce", () => {
    const b: Corte = { x0: 3, x1: 12, pe: 20 };
    expect(alargarCorte(b, [{ x0: 4, x1: 10, pe: 25 }, null])).toEqual(b);
  });
});

/* CADEIA, etapa 2 (D3 do Matheus de 2026-11-11): a cena so mastiga com o que comer. O motor pode decidir "comer" sem comida a ate uma celula
   (o A, cujo alvo e o padrao do motor; o modular a caminho): o laco do Comer, o gesto e as migalhas nao tocam. O "comeu a racao" vem do consumo
   e toca igual */
describe("comer sem nada perto (D3)", () => {
  test("com o clipe: a acao comer sem comida perto nao toca o laco; o consumo toca o momento", () => {
    esquecerComer();
    em(0, { comidaPerto: false });
    expect(em(10, { acao: "comer", comidaPerto: false }).tocou).toBeNull();
    expect(em(500, { acao: "comer", comidaPerto: false }).tocou).toBeNull();
    const m = em(600, { acao: "comer", comidaPerto: false, consumos: 1 });
    expect(m.tocou).toBe("clipe");
    expect(m.momento).toBe(true);
  });
  test("sem o clipe: nem o gesto; com comida perto, o gesto de hoje", () => {
    esquecerComer();
    expect(em(0, { acao: "comer", ciclo: null, comidaPerto: false }).tocou).toBeNull();
    expect(em(10, { acao: "comer", ciclo: null, comidaPerto: true }).tocou).toBe("gesto");
  });
  test("o gesto da cena: sem comida perto, nenhuma mastigacao; sem o campo, a de hoje", () => {
    esquecerReacao(); esquecerCoco();
    expect(gestoAgora({ ...cena("comer"), comidaPerto: false }, 210, false, true)).toEqual(SEM_GESTO);
    expect(gestoAgora(cena("comer"), 210, false, true).estica).toBeLessThan(1);
  });
});

describe("comidaPerto: a comida a ate uma celula do pet", () => {
  const mundo = (comidas: [number, number][]) => ({ pet: [100, 100] as const, cm: { sub: 8 }, comidas: new Map(comidas.map(([x, y], i) => [i, { x, y }])) });
  test("ate uma celula sim; mais longe nao; sem mundo, sim", () => {
    expect(comidaPerto(mundo([[106, 104]]))).toBe(true);
    expect(comidaPerto(mundo([[120, 100]]))).toBe(false);
    expect(comidaPerto(mundo([]))).toBe(false);
    expect(comidaPerto(undefined)).toBe(true);
  });
});

