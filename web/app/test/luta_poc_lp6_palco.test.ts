/* LUTA_POC, LP6-2 (docs/PLANO_LP6_SEGUNDO_GOLPE.md, secoes 4 e 4a): o golpe de apoio e a elipse por estagio no palco, so desenho. Com as
   chaves da LP6-1 desligadas, o palco le a mesma elipse e o mesmo tempo de clipe de antes; ligadas, o apoio de perto reaproveita o Attack_1
   inteiro e mais rapido, com um avanco curto do corpo, o tiro fraco sai marcado, e a camera abre o nivel 0 para a elipse maior. Nada aqui
   muda a luta: o resultado e o do nucleo. */
import { describe, expect, test } from "vitest";
import {
  APOIO_LP6, APOIO_LP6_3, ARENA_POR_ESTAGIO_LP6, ARENA_POR_ESTAGIO_LP6_3, ELIPSE_POC, FORMAS_ARENA, LIMITE_POC_MS, LUTA_V23, configLutaPoc, criarLutaPoc, esquivaDaTabela, passoPoc,
  sorteiosPoc, statsRivalArena, type EntradaLutaPoc, type LutaPoc,
} from "../motor/index.ts";
import { lutar as lutarArena } from "../motor/arena/luta.ts";
import { aplicarEventosPoc, passosDoTiro, tempoDoAtaque, visualNovoPoc, type VooPoc } from "../src/telas/lutar/palcoPoc/visualPoc.ts";
import { APOIO_POC, BORDA_CORTADA, avancoDoApoio, caixaDoMundo, clipeDoLutador, esfumarBordas, geometriaPoc, ladosCortados } from "../src/telas/lutar/palcoPoc/desenhoPoc.ts";
import { ladoDesenho, lutaMontadaDoEndereco } from "../src/lutaPocTela.ts";

const T = LUTA_V23, ESQ = esquivaDaTabela(T)!;
const ent = (cena: EntradaLutaPoc["cena"], a: string, b: string, semente: number, ligadas: boolean): EntradaLutaPoc => ({
  cena, semente, a: { forma: a, stats: statsRivalArena(a, T) }, b: { forma: b, stats: statsRivalArena(b, T) }, tiro: T.tiro!, esquiva: ESQ,
  ...(ligadas ? { apoio: APOIO_LP6, arenaPorEstagio: ARENA_POR_ESTAGIO_LP6 } : {}),
});

/** as formas do jogo de um nivel: a primeira que atira e a primeira que bate de perto */
function par(nivel: string): [string, string] {
  const ks = Object.keys(FORMAS_ARENA).filter(k => FORMAS_ARENA[k].estagio === nivel && !k.startsWith("npc"));
  const atira = ks.find(k => FORMAS_ARENA[k].golpe.proj), perto = ks.find(k => !FORMAS_ARENA[k].golpe.proj);
  if (!atira || !perto) throw new Error(`teste: o nivel ${nivel} sem as duas formas`);
  return [atira, perto];
}
const NIVEIS = ["Rookie", "Champion", "Ultimate", "Mega"] as const;

/** refaz a luta como o palco e anota o que o desenho do apoio le em cada passo */
function assistir(e: EntradaLutaPoc) {
  const L = criarLutaPoc(configLutaPoc(e), sorteiosPoc(e.semente)); L.eventos = [];
  const v = visualNovoPoc(), formas = [ladoDesenho(e.a.forma).forma, ladoDesenho(e.b.forma).forma] as const, voos = new Set<VooPoc>();
  let avancoMax = 0, perto = 0, impactosApoio = 0, clipeOk = true;
  while (!L.fim && L.relogio < LIMITE_POC_MS) {
    const n = passosDoTiro(L, 3);
    for (let q = 0; q < n && !L.fim && L.relogio < LIMITE_POC_MS; q++) {
      aplicarEventosPoc(v, L, passoPoc(L), formas);
      for (const o of v.voos) voos.add(o);
      impactosApoio += v.impactos.filter(i => i.apoio && i.t0 === Math.round(L.relogio / 16)).length;
      for (const u of [L.a, L.b]) {
        if (u.estado === "attack" && u.usandoApoio && u.ap && !u.ap.proj) { perto++; avancoMax = Math.max(avancoMax, avancoDoApoio(u)); }
        if (u.estado === "attack" && u.usandoApoio && !u.morto && !L.fim) {
          const c = clipeDoLutador(u, 0, false);
          if (c.clipe !== "Attack_1" || Math.abs(c.t - u.t * u.msAtk / u.msAp) > 1e-9 || c.t < u.t) clipeOk = false;
        }
      }
    }
  }
  return { L, voos: [...voos], avancoMax, perto, impactosApoio, clipeOk };
}

describe("com as chaves desligadas, o palco le o de antes", () => {
  for (const nivel of NIVEIS) test(nivel, () => {
    const [a, b] = par(nivel), L = criarLutaPoc(configLutaPoc(ent("campo", a, b, 101, false)), sorteiosPoc(101));
    expect(L.el).toBe(ELIPSE_POC);
    expect(L.esc).toBe(1);
    expect(caixaDoMundo(L)).toEqual({ x0: 0, x1: 480, y0: 0, y1: 280 });
    const x = assistir(ent("campo", a, b, 101, false));
    expect(x.perto + x.impactosApoio + x.voos.filter(o => o.apoio).length).toBe(0);
    expect(x.clipeOk).toBe(true);
  });
  test("fora do apoio, o tempo do ataque e o da luta", () => {
    const [a, b] = par("Rookie"), L = criarLutaPoc(configLutaPoc(ent("campo", a, b, 101, false)), sorteiosPoc(101));
    expect(tempoDoAtaque({ ...L.a, estado: "attack", t: 40 })).toBe(40);
    expect(clipeDoLutador({ ...L.a, estado: "attack", t: 40 }, 0, false)).toEqual({ clipe: "Attack_1", t: 40 });
  });
});

describe("com as chaves ligadas: o apoio no desenho, sem mudar a luta", () => {
  for (const nivel of NIVEIS) test(nivel, () => {
    const [a, b] = par(nivel);
    let perto = 0, fracos = 0, impactos = 0;
    for (const s of [101, 202]) for (const cena of ["campo", "floresta"] as const) {
      const e = ent(cena, a, b, s, true), r = lutarArena(e), x = assistir(e);
      expect(x.L.vencedor).toBe(r.vencedor); expect(x.L.relogio).toBe(r.relogio); expect(x.L.a.hp).toBe(r.vidaA); expect(x.L.b.hp).toBe(r.vidaB);
      expect(x.clipeOk).toBe(true);
      expect(x.avancoMax).toBeLessThanOrEqual(APOIO_POC.avanco + 1e-9);
      if (x.perto) expect(x.avancoMax).toBeGreaterThan(0);
      perto += x.perto; impactos += x.impactosApoio;
      /* o tiro fraco: so de quem bate de perto (o lado b), sem o efeito do jogo */
      for (const o of x.voos.filter(q => q.apoio)) { fracos++; expect(o.de).toBe(1); expect(o.prefab).toBeNull(); expect(o.nosso).toBe(false); }
    }
    expect(perto).toBeGreaterThan(0);
    expect(impactos).toBeGreaterThan(0);
    expect(fracos).toBeGreaterThan(0);
  });
});

describe("a elipse maior na camera", () => {
  const geo = (L: LutaPoc, Wp: number, Hp: number) => {
    const v = visualNovoPoc(); v.cam = { cx: L.el.cx, cy: L.el.cy - 30, nivel: 0, nivelDe: 0, trocaEm: -1e9 };
    /* os dois nas pontas da elipse: o nivel 0 mostra a arena inteira */
    const A = { ...L.a, x: L.el.cx - L.el.rx + 10 }, B = { ...L.b, x: L.el.cx + L.el.rx - 10 };
    return geometriaPoc(Wp, Hp, 1, Wp, Hp, v, { ...L, a: A, b: B }, 0, false, [60, 60]);
  };
  for (const [nivel, k] of [["Champion", 1], ["Ultimate", ARENA_POR_ESTAGIO_LP6.Ultimate], ["Mega", ARENA_POR_ESTAGIO_LP6.Mega]] as const)
    test(`${nivel}: fator ${k}; no desktop, a elipse inteira cabe na largura; a escala dos sprites e a de sempre`, () => {
      const [a, b] = par(nivel), L = criarLutaPoc(configLutaPoc(ent("campo", a, b, 101, true)), sorteiosPoc(101));
      const L0 = criarLutaPoc(configLutaPoc(ent("campo", a, b, 101, false)), sorteiosPoc(101));
      expect(L.esc).toBeCloseTo(k, 12);
      const g = geo(L, 1920, 950), g0 = geo(L0, 1920, 950);
      expect(g.es).toBe(g0.es);
      expect(1920 / g.e).toBeGreaterThanOrEqual(2 * L.el.rx);
      if (k === 1) expect(g).toEqual(g0);
    });
});

describe("a luta montada das capturas", () => {
  const busca = (lp6: string) => `?luta_poc=1&palco_poc=campo,cirro_crianca_arisco,ferrugem_crianca_arisco,7&palco_lp6=${lp6}`;
  test("ligadas e desligadas: a v23 com e sem as chaves; outro valor falha alto", () => {
    const lig = lutaMontadaDoEndereco(busca("ligadas")), des = lutaMontadaDoEndereco(busca("desligadas"));
    if (!lig || !des) throw new Error("teste: a luta da POC desligada (LUTA_POC_LIGADA)");
    expect(lig.entrada.apoio).toEqual(APOIO_LP6); expect(lig.entrada.arenaPorEstagio).toEqual(ARENA_POR_ESTAGIO_LP6); expect(lig.entrada.tiro).toEqual(T.tiro);
    expect(des.entrada.apoio).toBeUndefined(); expect(des.entrada.tiro).toEqual(T.tiro);
    expect(() => lutaMontadaDoEndereco(busca("talvez"))).toThrow(/palco_lp6/);
  });
  test("lp6_3 (LP6-4): a v23 com as chaves nos numeros da LP6-3, o apoio so no Ultimate e no Mega e a elipse 1,2/1,4", () => {
    const x = lutaMontadaDoEndereco(busca("lp6_3"));
    if (!x) throw new Error("teste: a luta da POC desligada (LUTA_POC_LIGADA)");
    expect(x.entrada.apoio).toEqual({ dano: 0.6, recarga: 3, longeMs: 1500, desde: "Ultimate" });
    expect(x.entrada.apoio).toEqual(APOIO_LP6_3);
    expect(x.entrada.arenaPorEstagio).toEqual({ Ultimate: 1.2, Mega: 1.4 });
    expect(x.entrada.arenaPorEstagio).toEqual(ARENA_POR_ESTAGIO_LP6_3);
    expect(x.entrada.tiro).toEqual(T.tiro);
  });
});

describe("a borda cortada do export (o conserto das capturas da LP6-2)", () => {
  /* um quadro w x h com os pixels cheios onde cheio(i, j) */
  const quadro = (w: number, h: number, cheio: (i: number, j: number) => boolean) => {
    const d = new Array<number>(w * h * 4).fill(0);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (cheio(i, j)) { const k = (j * w + i) * 4; d[k] = d[k + 1] = d[k + 2] = 200; d[k + 3] = 255; }
    return d;
  };
  test("a explosao cortada na borda da caixa conta; a ponta de lanca e o lado que nao encosta na caixa, nao", () => {
    const w = 40, h = 40, toca = { esq: true, dir: true, topo: true };
    const explosao = quadro(w, h, (i, j) => i >= 20 && j >= 5 && j < 35);   /* encosta na direita em 30 de 40 linhas */
    expect(ladosCortados(explosao, w, h, toca)).toEqual(["dir"]);
    expect(ladosCortados(explosao, w, h, { esq: true, dir: false, topo: true })).toEqual([]);
    const lanca = quadro(w, h, (i, j) => i >= 19 && i <= 20);              /* encosta no topo em 2 de 40 colunas */
    expect(ladosCortados(lanca, w, h, toca)).toEqual([]);
  });
  test("o esfumado: o alfa cai em rampa ate a borda cortada, e o resto do quadro fica igual", () => {
    const w = 40, h = 10, d = quadro(w, h, () => true), antes = [...d];
    esfumarBordas(d, w, h, ["dir"]);
    const alfa = (i: number) => d[(5 * w + i) * 4 + 3];
    expect(alfa(w - 1)).toBeLessThan(20);
    for (let i = w - BORDA_CORTADA.largura; i < w - 1; i++) expect(alfa(i)).toBeGreaterThan(alfa(i + 1));
    for (let i = 0; i < w - BORDA_CORTADA.largura; i++) expect(alfa(i)).toBe(255);
    for (let k = 0; k < d.length; k++) if (k % 4 !== 3) expect(d[k]).toBe(antes[k]);
  });
});
