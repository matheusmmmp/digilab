/* LUTA_EFEITOS, E5 (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4, 3.5 e 4): o nocaute e a camera, so vista.
   - A barra com o dano atrasado: o pedaco que saiu fica branco, segura, esvazia ate a vida e nunca passa dela; a vida da barra e a da luta.
   - A camera lenta do nocaute so muda quantos passos cada quadro mostra: a luta mostrada passa pelos mesmos passos e acaba no mesmo fim.
   - O escuro e o "K.O." saem do passo do nocaute; o "K.O." em pixels inteiros, que encolhem ate o final (de uma vez com o movimento reduzido).
   - A camera: a mesma luta da a mesma camera; o sprite fica em escala inteira (px do canvas), nunca menor que a de sempre; os dois lutadores
     ficam na tela em todo passo (o empurrao da v18 e a cerca), o cenario cobre a tela, e o mundo (o x da luta, as marcas, os projeteis) vai
     junto com o zoom. Sem estado, a geometria e a de antes.
   - Nada disso muda o ResultadoLutaTR. */
import { describe, expect, test } from "vitest";
import { CV21E_TR18, criarLutaTR, jogarLuta, lutadorBot, passoTR } from "../motor/index.ts";
import { aplicarEventosTR, visualNovoTR } from "../src/telas/lutar/palcoTR/efeitosTR.ts";
import { BARRA, NOCAUTE, barraDoPasso, escuroDoPasso, koDoPasso, passosDaEspera, passosDoQuadro, pixelsDoKO } from "../src/telas/lutar/palcoTR/nocauteTR.ts";
import { CAMERA, cameraDoQuadro, escDoNivel, nivelDaDistancia } from "../src/telas/lutar/palcoTR/cameraTR.ts";
import { geometriaTR, pontoDoVoo, xTela } from "../src/telas/lutar/palcoTR/projeteisTR.ts";

const R = CV21E_TR18;
type Sim = ReturnType<typeof criarLutaTR>;
type Vis = ReturnType<typeof visualNovoTR>;
/** as caixas de sprite de verdade (o atlas do UP): o Gabumon Rookie, o Zudomon (o Vigia) e dois adultos grandes */
const ROOKIE: [number, number] = [98, 76], VIGIA: [number, number] = [177, 148], GRANDE: [number, number] = [205, 187];
/** as telas: o palco no desktop e no celular, com 1 e 3 px do canvas por px de CSS */
const TELAS = [[1280, 720, 1], [390, 600, 1], [390, 600, 3], [1920, 950, 1]] as const;
const LUTAS = [["aleatorio", "vigia", 7], ["agressivo", "espelho", 101], ["duelista", "tita", 4242], ["furioso", "emboscador", 777]] as const;

/** joga a luta passo a passo como o luta.ts (os eventos de cada passo no estado visual) e chama olhar a cada passo */
function jogar(a: string, b: string, s: number, olhar: (sim: Sim, v: Vis, ev: readonly { tipo: string }[]) => void = () => {}) {
  const sim = criarLutaTR(lutadorBot(a, R), lutadorBot(b, R), s, { R, eventos: true }), v = visualNovoTR();
  let lidos = 0, fim: [number, string] | null = null;
  while (!fim) { fim = passoTR(sim) as [number, string] | null; const ev = sim.eventos!.slice(lidos); aplicarEventosTR(v, sim, ev); lidos = sim.eventos!.length; olhar(sim, v, ev); }
  return { fim, passos: sim.S.passo, v };
}

describe("E5: a barra com o dano atrasado", () => {
  test("a vida da barra e a da luta; o pedaco fica branco, segura e esvazia ate a vida, sem passar dela", () => {
    let brancos = 0, vermelhos = 0, cheias = 0;
    const ultimoDano = [-Infinity, -Infinity];
    jogar("agressivo", "vigia", 7, (sim, v, ev) => {
      for (const e of ev) if (e.tipo === "dano") { const d = e as unknown as { lado: number; t: number }; ultimoDano[d.lado] = d.t; }
      sim.S.L.forEach((l, i) => {
        const b = barraDoPasso(v.vidas[i], sim.S.passo); if (!b) return;
        expect(b.hp).toBeCloseTo(l.hp, 9);
        expect(b.rastro).toBeGreaterThanOrEqual(b.hp);
        expect(b.rastro).toBeLessThanOrEqual(l.hpMax + 1e-9);
        const idade = sim.S.passo - ultimoDano[i];
        if (b.rastro > b.hp) { if (b.branco) { brancos++; expect(idade).toBeLessThan(BARRA.branco); } else vermelhos++; }
        if (idade >= 0 && idade < BARRA.branco && b.rastro > b.hp) expect(b.branco).toBe(true);
        if (b.rastro === b.hp) cheias++;
      });
    });
    expect(brancos).toBeGreaterThan(0); expect(vermelhos).toBeGreaterThan(0); expect(cheias).toBeGreaterThan(0);
  });
  test("o pedaco segura BARRA.segura passos e depois esvazia BARRA.taxa da vida maxima por passo, ate a vida", () => {
    const vida = { ini: 100, hpMax: 100, ev: [{ t: 10, hp: 70, dano: true }] };
    expect(barraDoPasso(vida, 10)).toEqual({ hp: 70, rastro: 100, branco: true });
    expect(barraDoPasso(vida, 10 + BARRA.segura)!.rastro).toBe(100);
    expect(barraDoPasso(vida, 10 + BARRA.segura + 10)!.rastro).toBeCloseTo(100 - 10 * BARRA.taxa * 100, 9);
    expect(barraDoPasso(vida, 10 + BARRA.segura + 1000)).toEqual({ hp: 70, rastro: 70, branco: false });
    /* um golpe novo antes do fim: o pedaco continua de onde estava e segura de novo */
    const dois = { ini: 100, hpMax: 100, ev: [{ t: 10, hp: 70, dano: true }, { t: 10 + BARRA.segura + 5, hp: 60, dano: true }] };
    const r = barraDoPasso(dois, 10 + BARRA.segura + 5)!.rastro;
    expect(r).toBeCloseTo(100 - 5 * BARRA.taxa * 100, 9);
    expect(barraDoPasso(dois, 10 + BARRA.segura + 5 + BARRA.segura)!.rastro).toBeCloseTo(r, 9);
    /* a cura sobe a vida e o pedaco junto */
    expect(barraDoPasso({ ini: 50, hpMax: 100, ev: [{ t: 5, hp: 80, dano: false }] }, 6)).toEqual({ hp: 80, rastro: 80, branco: false });
  });
});

describe("E5: o nocaute", () => {
  /** o agendador do luta.ts: os passos de cada quadro ate o fim; devolve os quadros e o fim */
  function mostrar(a: string, b: string, s: number, base: number, reduzido: boolean) {
    const res = jogarLuta(lutadorBot(a, R), lutadorBot(b, R), s, R).tr!, en = res.entrada;
    const sim = criarLutaTR(en.A, en.B, en.semente, { ...en.o, eventos: true }), v = visualNovoTR(), quadros: number[] = [];
    let fim = null, lidos = 0;
    while (!fim) {
      const n = passosDoQuadro(sim.S.passo, base, res, reduzido); quadros.push(n);
      for (let q = 0; q < n && !fim; q++) { fim = passoTR(sim, en.o.desafiado ?? null); const ev = sim.eventos!.slice(lidos); lidos = sim.eventos!.length; aplicarEventosTR(v, sim, ev); }
    }
    return { res, fim, passos: sim.S.passo, quadros };
  }
  test("a camera lenta so muda os passos por quadro: o fim e o do ResultadoLutaTR", () => {
    let kos = 0;
    for (const [a, b, s] of LUTAS) for (const base of [3, 6]) {
      const x = mostrar(a, b, s, base, false), y = mostrar(a, b, s, base, true);
      for (const m of [x, y]) { expect(m.passos).toBe(m.res.passos); expect(m.fim).toEqual([m.res.pontosA, m.res.fim]); }
      if (x.res.fim === "ko") {
        kos++;
        /* os ultimos NOCAUTE.lentaAntes passos em quadros de NOCAUTE.lentaPassos: mais quadros que sem a lenta */
        expect(x.quadros.length).toBeGreaterThan(y.quadros.length);
        expect(x.quadros.slice(-5).every(n => n === NOCAUTE.lentaPassos)).toBe(true);
      } else expect(x.quadros).toEqual(y.quadros);
      expect(y.quadros.every(n => n === base)).toBe(true);
    }
    expect(kos).toBeGreaterThan(0);
  });
  test("a espera do fim anda devagar so depois de um nocaute e sem o movimento reduzido", () => {
    expect(passosDaEspera(0, 3, true, false)).toBe(NOCAUTE.lentaPassos);
    expect(passosDaEspera(NOCAUTE.lentaDepois, 3, true, false)).toBe(3);
    expect(passosDaEspera(0, 3, false, false)).toBe(3);
    expect(passosDaEspera(0, 3, true, true)).toBe(3);
  });
  test("o escuro sobe ate NOCAUTE.escuro; o K.O. sai depois do atraso, em pixels inteiros que encolhem ate o final", () => {
    expect(escuroDoPasso(-1)).toBe(0);
    for (let i = 1; i < 60; i++) expect(escuroDoPasso(i)).toBeGreaterThanOrEqual(escuroDoPasso(i - 1));
    expect(escuroDoPasso(NOCAUTE.escurecer)).toBe(NOCAUTE.escuro);
    expect(koDoPasso(NOCAUTE.koAtraso - 1, 1280, 720, false)).toBeNull();
    for (const [W, H] of [[1280, 720], [390, 600], [1170, 1800]]) {
      const ps = Array.from({ length: NOCAUTE.koPop + 4 }, (_, k) => koDoPasso(NOCAUTE.koAtraso + k, W, H, false)!.p);
      for (const p of ps) expect(Number.isInteger(p)).toBe(true);
      for (let k = 1; k < ps.length; k++) expect(ps[k]).toBeLessThanOrEqual(ps[k - 1]);
      const fim = ps[ps.length - 1], { w, h } = pixelsDoKO();
      expect(ps[0]).toBeGreaterThan(fim);
      expect(w * fim).toBeLessThanOrEqual(W * NOCAUTE.koLargura); expect(h * fim).toBeLessThanOrEqual(H * NOCAUTE.koAltura);
      /* com o movimento reduzido, ja no tamanho final */
      expect(koDoPasso(NOCAUTE.koAtraso, W, H, true)!.p).toBe(fim);
    }
    expect(pixelsDoKO()).toMatchObject({ w: 15, h: 5 });
  });
});

describe("E5: a camera", () => {
  test("o nivel tem histerese: sobe abaixo do limiar menos a folga e so desce acima do limiar mais ela", () => {
    const [l1, l2] = CAMERA.limiares, h = CAMERA.histerese;
    expect(nivelDaDistancia(l1 + h + 1, 0)).toBe(0); expect(nivelDaDistancia(l1 - h - 1, 0)).toBe(1);
    expect(nivelDaDistancia(l1, 1)).toBe(1); expect(nivelDaDistancia(l1 + h + 1, 1)).toBe(0);
    expect(nivelDaDistancia(l2 - h - 1, 1)).toBe(2); expect(nivelDaDistancia(l2 + h - 1, 2)).toBe(2); expect(nivelDaDistancia(l2 + h + 1, 2)).toBe(1);
    expect(escDoNivel(3, 1, 720, 1, 76)).toBe(4); expect(escDoNivel(3, 2, 720, 1, 76)).toBe(5); expect(escDoNivel(9, 1, 1800, 3, 76)).toBe(12);
    /* limitada pela altura: o sprite nao passa de CAMERA.altMax do palco */
    expect(escDoNivel(2, 2, 720, 1, 187)).toBe(Math.max(2, Math.floor(720 * CAMERA.altMax / 187)));
  });
  test("sem estado, a geometria e a de antes (s = 1, x = xTela)", () => {
    const g = geometriaTR(1280, 720, 1, [ROOKIE, VIGIA], [175, 305]), c = cameraDoQuadro(null, 1280, 720, 1, [ROOKIE, VIGIA], [175, 305], 0, false);
    expect(c.geo.s).toBe(1); expect(c.geo.centros).toEqual(g.centros); expect(c.geo.e).toBe(g.e); expect(c.geo.x(175)).toBe(xTela(175, 1280));
  });
  for (const [a, b, s] of LUTAS) test(`${a} x ${b}: a mesma camera; escala inteira; os dois na tela; o mundo junto com o zoom`, () => {
    const marca = (dims: [number, number][], W: number, H: number, K: number, red: boolean) => {
      const out: string[] = []; let zooms = 0, passagens = 0;
      jogar(a, b, s, (sim, v) => {
        const xs = sim.S.L.map(l => l.x), { cam, geo } = cameraDoQuadro(v.cam, W, H, K, dims, xs, sim.S.passo, red), e0 = geometriaTR(W, H, K, dims, xs).e;
        expect(Number.isInteger(geo.e)).toBe(true); expect(geo.e).toBeGreaterThanOrEqual(e0); expect(cam.e).toBe(geo.e);
        if (geo.s > 1) {
          zooms++;
          /* os dois na tela com margem, o cenario cobrindo a tela (o centro preso) */
          for (let i = 0; i < 2; i++) { expect(geo.centros[i] - geo.meias[i]).toBeGreaterThanOrEqual(CAMERA.margem - 1e-9); expect(geo.centros[i] + geo.meias[i]).toBeLessThanOrEqual(W - CAMERA.margem + 1e-9); }
          expect(geo.cx).toBeGreaterThanOrEqual(W / (2 * geo.s) - 1e-9); expect(geo.cx).toBeLessThanOrEqual(W - W / (2 * geo.s) + 1e-9);
          /* fora da passagem (e sempre com o movimento reduzido), o mundo vai exatamente com o sprite */
          if (Math.abs(geo.s - geo.e / e0) > 1e-12) { passagens++; expect(red).toBe(false); }
          /* o mundo: o x da luta e linear com o zoom (as marcas e o arrasto ficam no chao, no x delas), e o projetil vai de um ao outro */
          expect(geo.x(300) - geo.x(200)).toBeCloseTo((xTela(300, W) - xTela(200, W)) * geo.s, 9);
          const p = pontoDoVoo(geo, 0, .5), [lo, hi] = [...geo.centros].sort((m, n) => m - n);
          expect(p.x).toBeGreaterThanOrEqual(lo - geo.meias[0]); expect(p.x).toBeLessThanOrEqual(hi + geo.meias[1]);
        }
        out.push(JSON.stringify([sim.S.passo, v.cam, cam]));
      });
      return { out, zooms, passagens };
    };
    let algumZoom = 0;
    for (const dims of [[ROOKIE, VIGIA], [ROOKIE, ROOKIE], [VIGIA, GRANDE]] as [number, number][][]) for (const [W, H, K] of TELAS) {
      const x = marca(dims, W, H, K, false), y = marca(dims, W, H, K, false), r = marca(dims, W, H, K, true);
      expect(x.out).toEqual(y.out); expect(r.passagens).toBe(0);
      algumZoom += x.zooms;
    }
    expect(algumZoom).toBeGreaterThan(0);
  });
  /* sem zoom, como antes: perto da cerca o sprite largo ja passava um pouco da borda */
  test("o empurrao da v18: nos passos do deslize, os dois continuam na tela com o zoom", () => {
    let deslizes = 0;
    for (const [a, b, s] of LUTAS) jogar(a, b, s, (sim, v) => {
      if (!sim.S.L.some(l => sim.S.passo < l.deslizeAte)) return;
      deslizes++;
      for (const [W, H, K] of TELAS) {
        const xs = sim.S.L.map(l => l.x), { geo } = cameraDoQuadro(v.cam, W, H, K, [ROOKIE, VIGIA], xs, sim.S.passo, false), g0 = geometriaTR(W, H, K, [ROOKIE, VIGIA], xs);
        for (let i = 0; i < 2; i++) {
          expect(geo.centros[i] - geo.meias[i]).toBeGreaterThanOrEqual(Math.min(0, g0.centros[i] - g0.meias[i]) - 1e-9);
          expect(geo.centros[i] + geo.meias[i]).toBeLessThanOrEqual(Math.max(W, g0.centros[i] + g0.meias[i]) + 1e-9);
        }
      }
    });
    expect(deslizes).toBeGreaterThan(0);
  });
});

describe("E5: so vista", () => {
  for (const [a, b, s] of LUTAS) test(`${a} x ${b}: o ResultadoLutaTR nao muda com os efeitos`, () => {
    const res = jogarLuta(lutadorBot(a, R), lutadorBot(b, R), s, R).tr!, x = jogar(a, b, s);
    expect(x.passos).toBe(res.passos); expect(x.fim).toEqual([res.pontosA, res.fim]);
    /* e a mesma luta da a mesma barra, a mesma camera */
    const y = jogar(a, b, s);
    expect(JSON.stringify([x.v.vidas, x.v.cam])).toBe(JSON.stringify([y.v.vidas, y.v.cam]));
  });
});
