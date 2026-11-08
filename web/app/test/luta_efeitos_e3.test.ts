/* LUTA_EFEITOS, E3 (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4, 3.5 e 4): a telegrafia e o chao, so vista.
   - A elipse do preparar_pesado fecha do comeco ao fim do preparo e fica fechada (pronta) ate o pesado sair; a do carregar fecha no carregar.
   - O acerto do pesado deixa a onda de choque e a cratera no x do alvo; o empurrao (a v18) deixa o arrasto do x de onde o alvo saiu ao x onde
     o deslize acabou; as marcas somem em CHAO.durMarca passos.
   - A poeira acompanha a corrida, a arrancada, o deslize e o pouso da queda.
   - O desenho do chao e o mesmo para a mesma luta, passo a passo, e nenhum efeito muda o ResultadoLutaTR. */
import { describe, expect, test } from "vitest";
import { CV21E_TR18, criarLutaTR, jogarLuta, lutadorBot, passoTR } from "../motor/index.ts";
import { aplicarEventosTR, visualNovoTR } from "../src/telas/lutar/palcoTR/efeitosTR.ts";
import { CHAO, alfaDaMarca, anelDaElipse, pixelsDaCratera, pixelsDaOnda, pixelsDaTelegrafia, pixelsDoArrasto, poeiraDaNuvem, poeiraDoPassoTR,
  telegrafiaDoPasso, type MarcaTR } from "../src/telas/lutar/palcoTR/chaoTR.ts";

const R = CV21E_TR18;
type Sim = ReturnType<typeof criarLutaTR>;
type Vis = ReturnType<typeof visualNovoTR>;

/** joga a luta passo a passo como o luta.ts (os eventos de cada passo no estado visual) e chama olhar a cada passo */
function jogar(a: string, b: string, s: number, olhar: (sim: Sim, v: Vis, ev: readonly unknown[]) => void) {
  const sim = criarLutaTR(lutadorBot(a, R), lutadorBot(b, R), s, { R, eventos: true }), v = visualNovoTR();
  let lidos = 0, fim = null;
  while (!fim) { fim = passoTR(sim); const ev = sim.eventos!.slice(lidos); aplicarEventosTR(v, sim, ev); lidos = sim.eventos!.length; olhar(sim, v, ev); }
  return { fim, passos: sim.S.passo };
}

describe("E3: a telegrafia", () => {
  test("a elipse do pesado fecha durante o preparo, fica pronta ate o golpe sair e some no golpe", () => {
    let preparos = 0, prontosAteGolpe = 0;
    const ultimo: (ReturnType<typeof telegrafiaDoPasso>)[] = [null, null];
    jogar("agressivo", "vigia", 7, (sim) => {
      sim.S.L.forEach((l, i) => {
        const tg = telegrafiaDoPasso(l, sim.S.passo), antes = ultimo[i];
        if (l.acao?.nome === "preparar_pesado" && l.hp > 0) {
          preparos++;
          expect(tg).toMatchObject({ tipo: "pesado", pronto: false });
          /* fecha: a fracao nunca volta dentro do mesmo preparo */
          if (antes && antes.tipo === "pesado" && !antes.pronto) expect(tg!.f).toBeGreaterThanOrEqual(antes.f);
        }
        if (l.acao?.nome === "pesado" && !l.acao.feito && l.hp > 0) { prontosAteGolpe++; expect(tg).toEqual({ tipo: "pesado", f: 1, pronto: true }); }
        if (l.acao?.nome === "pesado" && l.acao.feito) expect(tg).toBeNull();
        ultimo[i] = tg;
      });
    });
    expect(preparos).toBeGreaterThan(0); expect(prontosAteGolpe).toBeGreaterThan(0);
  });
  test("a elipse do carregar fecha de 0 a 1 do comeco ao fim do carregar", () => {
    let vistos = 0;
    jogar("aleatorio", "vigia", 7, (sim) => sim.S.L.forEach(l => {
      if (l.acao?.nome !== "carregar" || l.hp <= 0) return;
      vistos++;
      const tg = telegrafiaDoPasso(l, sim.S.passo)!, a = l.acao;
      expect(tg.tipo).toBe("carregar");
      expect(tg.f).toBeCloseTo((sim.S.passo - a.inicio) / (a.fim - a.inicio), 10);
    }));
    expect(vistos).toBeGreaterThan(0);
  });
  test("o anel aberto e maior que o fechado; o pronto pisca, e nao pisca com o movimento reduzido", () => {
    const larg = (px: { dx: number }[]) => Math.max(...px.map(p => p.dx)) - Math.min(...px.map(p => p.dx));
    const aberta = pixelsDaTelegrafia({ tipo: "pesado", f: 0, pronto: false }, "brasa", 20, 0, false);
    const fechada = pixelsDaTelegrafia({ tipo: "pesado", f: 1, pronto: false }, "brasa", 20, 0, false);
    expect(larg(aberta)).toBeGreaterThan(larg(fechada) * 1.5);
    const pronta = (p: number, red: boolean) => pixelsDaTelegrafia({ tipo: "pesado", f: 1, pronto: true }, "brasa", 20, p, red);
    expect(pronta(0, false)).not.toEqual(pronta(CHAO.piscaPronta / 2, false));
    expect(pronta(0, true)).toEqual(pronta(CHAO.piscaPronta / 2, true));
  });
});

describe("E3: o chao", () => {
  test("o acerto do pesado deixa a cratera e a onda no x do alvo; o empurrao deixa o arrasto do deslize inteiro", () => {
    const crateras: MarcaTR[] = [], arrastos: { m: MarcaTR; x0: number; deslize: number }[] = [];
    const fimEm = jogar("agressivo", "vigia", 7, (sim, v, ev) => {
      for (const e of ev as { tipo: string; lado: number; t: number; px?: number }[]) {
        if (e.tipo === "empurrao" && e.px! > 0) {
          const m = v.marcas.find(m => m.tipo === "arrasto" && m.lado === e.lado && m.t0 === e.t)!;
          expect(m).toBeDefined(); arrastos.push({ m, x0: sim.S.L[e.lado].x, deslize: e.px! });
        }
      }
      /* a cratera nasce no passo do acerto, no x do alvo nesse passo */
      for (const m of v.marcas) if (m.tipo === "cratera" && !crateras.includes(m)) { crateras.push(m); expect(m.x0).toBe(sim.S.L[m.lado].x); }
    }).passos;
    expect(crateras.length).toBeGreaterThan(0); expect(arrastos.length).toBeGreaterThan(0);
    /* o arrasto vai do x de onde o alvo saiu ao fim do deslize (o empurrao inteiro, a menos da parede) */
    for (const a of arrastos) {
      expect(a.m.x0).toBe(a.x0);
      expect(Math.abs(a.m.x1 - a.m.x0)).toBeLessThanOrEqual(a.deslize + 1e-9);
      /* o deslize que acabou antes do fim da luta andou (a luta que acaba no meio do deslize para de seguir) */
      if (a.m.ate < fimEm) expect(Math.abs(a.m.x1 - a.m.x0)).toBeGreaterThan(0);
    }
    for (const m of crateras) {
      expect(pixelsDaOnda("brasa", 0, 20, false).length).toBeGreaterThan(0);
      expect(pixelsDaCratera(m, "brasa", 20, m.t0).length).toBeGreaterThan(0);
    }
  });
  test("a marca fica inteira e depois some em CHAO.durMarca passos (~2 s)", () => {
    const m: MarcaTR = { tipo: "cratera", lado: 1, t0: 100, x0: 300, x1: 300, ate: 100 };
    expect(alfaDaMarca(m, 99)).toBe(0); expect(alfaDaMarca(m, 100)).toBe(1);
    expect(alfaDaMarca(m, 100 + CHAO.durMarca - CHAO.someMarca)).toBe(1);
    expect(alfaDaMarca(m, 100 + CHAO.durMarca - 1)).toBeGreaterThan(0); expect(alfaDaMarca(m, 100 + CHAO.durMarca)).toBe(0);
    expect(pixelsDaCratera(m, "limo", 20, 100 + CHAO.durMarca)).toEqual([]);
    expect(CHAO.durMarca * 16).toBeGreaterThanOrEqual(1900); expect(CHAO.durMarca * 16).toBeLessThanOrEqual(2100);
  });
  test("a poeira acompanha a corrida, a arrancada, o deslize e o pouso da queda", () => {
    const tipos = new Set<string>();
    for (const [a, b, s] of [["agressivo", "vigia", 7], ["emboscador", "duelista", 101], ["tita", "sentinela", 777]] as const)
      jogar(a, b, s, (sim, v) => { for (const f of poeiraDoPassoTR(sim, v.marcas, sim.S.passo)) {
        tipos.add(f.tipo);
        const l = sim.S.L[f.lado];
        if (f.tipo === "deslize") expect(sim.S.passo).toBeLessThan(l.deslizeAte);
        if (f.tipo === "pouso") expect(l.quedaDe).toBeGreaterThanOrEqual(0);
      } });
    for (const t of ["corrida", "deslize", "pouso", "pesado"]) expect(tipos.has(t)).toBe(true);
  });
});

/** a marca de tudo o que a E3 desenha num passo: a telegrafia de cada lado, as marcas, as ondas e a poeira */
function marcasDoChao(a: string, b: string, s: number, reduzido: boolean) {
  const out: string[] = [];
  const r = jogar(a, b, s, (sim, v) => {
    const p = sim.S.passo;
    out.push(JSON.stringify([p,
      sim.S.L.map(l => { const tg = telegrafiaDoPasso(l, p); return tg ? [tg, pixelsDaTelegrafia(tg, "cirro", 18, p, reduzido)] : null; }),
      v.marcas.map(m => [m, alfaDaMarca(m, p), m.tipo === "cratera" ? [pixelsDaCratera(m, "brasa", 18, p), pixelsDaOnda("brasa", p - m.t0, 18, reduzido)] : pixelsDoArrasto(m, 12, p)]),
      poeiraDoPassoTR(sim, v.marcas, p).map(f => [f, poeiraDaNuvem(f.idade, f.tipo === "pesado")])]));
  });
  return { out, ...r };
}

describe("E3: so vista, deterministico", () => {
  test("mesma luta, mesmo chao; o fim e o do ResultadoLutaTR", () => {
    for (const [a, b, s] of [["agressivo", "vigia", 4242], ["emboscador", "duelista", 101], ["tita", "sentinela", 777]] as const) {
      const res = jogarLuta(lutadorBot(a, R), lutadorBot(b, R), s, R).tr!;
      const x = marcasDoChao(a, b, res.entrada.semente, false), y = marcasDoChao(a, b, res.entrada.semente, false);
      expect(x.out).toEqual(y.out);
      expect(x.passos).toBe(res.passos); expect(x.fim![0]).toBe(res.pontosA); expect(x.fim![1]).toBe(res.fim);
      /* e algo de chao aparece */
      expect(x.out.some(m => JSON.parse(m)[2].length > 0)).toBe(true);
    }
  });
  test("todos os pixels de chao na grade do sprite (deslocamento e tamanho inteiros); o anel nao repete pixel", () => {
    const m: MarcaTR = { tipo: "cratera", lado: 0, t0: 0, x0: 0, x1: 0, ate: 0 };
    for (const el of ["brasa", "cirro", "ferrugem", "limo"] as const) for (let p = 0; p < 30; p += 3) for (const red of [false, true]) {
      const todos = [...pixelsDaTelegrafia({ tipo: p % 2 ? "pesado" : "carregar", f: p / 30, pronto: p > 20 }, el, 17, p, red), ...pixelsDaOnda(el, p, 17, red),
        ...pixelsDaCratera(m, el, 17, p), ...pixelsDoArrasto({ ...m, tipo: "arrasto" }, 9, p)];
      for (const x of todos) { expect(Number.isInteger(x.dx) && Number.isInteger(x.dy) && Number.isInteger(x.tam)).toBe(true); expect(x.tam).toBeGreaterThan(0); }
    }
    const anel = anelDaElipse(20, 6).map(p => p.join(","));
    expect(new Set(anel).size).toBe(anel.length);
  });
  test("com o movimento reduzido a onda e um anel so, sem luz", () => {
    for (let i = 0; i < CHAO.durOnda; i++) expect(pixelsDaOnda("cirro", i, 18, true).some(p => p.luz)).toBe(false);
    expect(pixelsDaOnda("cirro", CHAO.ondaAtraso + 1, 18, true).length).toBeLessThan(pixelsDaOnda("cirro", CHAO.ondaAtraso + 1, 18, false).length);
  });
});
