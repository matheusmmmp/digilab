/* LUTA_EFEITOS, E4 (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4, 3.5 e 4): as posturas como efeito, so vista.
   - O icone sai da acao em curso (ou do preparo pronto), igual a etiqueta de antes; cada postura tem o seu icone 7 x 7, com nome.
   - O escudo no defender acende quando um golpe bate nele; o contra-golpe acende o clarao quando devolve o golpe; a esquiva abre as copias; o
     carregar tem a aura (e a elipse da E3 no chao continua a unica coisa no chao); a pele dura brilha enquanto vale (peleAte).
   - O desenho das posturas e o mesmo para a mesma luta, passo a passo, e nenhum efeito muda o ResultadoLutaTR; nada empurra.
   - Com o movimento reduzido nada pisca nem treme: o mesmo desenho em todo passo; os icones ficam. */
import { describe, expect, test } from "vitest";
import { CV21E_TR18, criarLutaTR, jogarLuta, lutadorBot, passoTR } from "../motor/index.ts";
import { aplicarEventosTR, visualNovoTR } from "../src/telas/lutar/palcoTR/efeitosTR.ts";
import { telegrafiaDoPasso } from "../src/telas/lutar/palcoTR/chaoTR.ts";
import { NOME_POSTURA, POSTURA, POSTURAS_TR, efeitoDaPostura, pixelsDaAura, pixelsDoContra, pixelsDoEscudo, pixelsDoIcone, posturaDoLado,
  type PosturaTR } from "../src/telas/lutar/palcoTR/posturasTR.ts";

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
/* as lutas que mostram as posturas: o tita contra o espelho (defender, esquivar, carregar, contra-golpe com o golpe devolvido, pele dura,
   preparo e pronto) e o sentinela, que marca */
const LUTAS = [["tita", "espelho", 7], ["espelho", "tita", 101], ["sentinela", "tartaruga", 7]] as const;

describe("E4: o icone da postura", () => {
  test("sai da acao em curso ou do preparo pronto, como a etiqueta de antes; nenhum no nocaute", () => {
    const vistos = new Set<PosturaTR>();
    for (const [a, b, s] of LUTAS) jogar(a, b, s, (sim) => sim.S.L.forEach(l => {
      const p = posturaDoLado(l);
      if (l.hp <= 0) { expect(p).toBeNull(); return; }
      if (l.prep) expect(p).toBe("pesado_pronto");
      else if (l.acao && ["defender", "esquivar", "carregar", "contra_golpe", "preparar_pesado", "marcar", "pele_dura"].includes(l.acao.nome)) expect(p).toBe(l.acao.nome);
      else expect(p).toBeNull();
      if (p) vistos.add(p);
    }));
    /* todas as posturas aparecem nestas lutas */
    expect([...vistos].sort()).toEqual([...POSTURAS_TR].sort());
  });
  test("cada postura tem um icone 7 x 7 diferente, com a placa em volta, e um nome", () => {
    const desenhos = new Set<string>();
    for (const p of POSTURAS_TR) {
      const px = pixelsDoIcone(p, "brasa", 1);
      for (const x of px) { expect(x.dx).toBeGreaterThanOrEqual(-1); expect(x.dx).toBeLessThanOrEqual(POSTURA.icone); expect(x.dy).toBeGreaterThanOrEqual(-1); expect(x.dy).toBeLessThanOrEqual(POSTURA.icone); }
      /* a placa: (icone + 2)^2 pixels, e o desenho por cima */
      expect(px.length).toBeGreaterThan((POSTURA.icone + 2) ** 2);
      desenhos.add(JSON.stringify(px.slice((POSTURA.icone + 2) ** 2).map(x => [x.dx, x.dy, x.cor === "#ffffff"])));
      expect(NOME_POSTURA[p].length).toBeGreaterThan(0);
    }
    expect(desenhos.size).toBe(POSTURAS_TR.length);
    /* a esquiva aponta para tras: espelha entre os lados; o escudo nao */
    expect(pixelsDoIcone("esquivar", "cirro", 0)).not.toEqual(pixelsDoIcone("esquivar", "cirro", 1));
    expect(pixelsDoIcone("defender", "cirro", 0)).toEqual(pixelsDoIcone("defender", "cirro", 1));
  });
});

describe("E4: os efeitos das posturas", () => {
  test("o escudo no defender acende quando um golpe bate nele; o contra-golpe acende o clarao quando devolve", () => {
    let escudos = 0, acesos = 0, guardas = 0, claroes = 0;
    for (const [a, b, s] of LUTAS) jogar(a, b, s, (sim, v, ev) => {
      sim.S.L.forEach((l, i) => {
        const ef = efeitoDaPostura(l, i, sim.S.passo, v.batidas, false);
        if (l.hp > 0 && l.acao?.nome === "defender") { escudos++; expect(ef.escudo).not.toBeNull(); } else expect(ef.escudo).toBeNull();
        if (ef.escudo && ef.escudo.aceso > 0) acesos++;
        if (l.hp > 0 && l.acao?.nome === "contra_golpe") { guardas++; expect(ef.contra?.guarda).toBe(true); }
        if (ef.contra && ef.contra.clarao > 0) claroes++;
      });
      /* o golpe devolvido: dano em quem bateu, no passo em que o outro esta no contra-golpe, vira a batida "contra" do outro */
      for (const e of ev as { tipo: string; lado: number; t: number }[]) if (e.tipo === "dano" && sim.S.L[1 - e.lado].acao?.nome === "contra_golpe")
        expect(v.batidas.some(b => b.tipo === "contra" && b.lado === 1 - e.lado && b.t0 === e.t)).toBe(true);
    });
    expect(escudos).toBeGreaterThan(0); expect(acesos).toBeGreaterThan(0); expect(guardas).toBeGreaterThan(0); expect(claroes).toBeGreaterThan(0);
  });
  test("a esquiva abre as copias para tras; o carregar tem a aura e so a elipse da E3 no chao; a pele dura brilha enquanto vale", () => {
    let fantasmas = 0, auras = 0, peles = 0, peleForaDaAcao = 0;
    for (const [a, b, s] of LUTAS) jogar(a, b, s, (sim, v) => sim.S.L.forEach((l, i) => {
      const p = sim.S.passo, ef = efeitoDaPostura(l, i, p, v.batidas, false);
      if (l.hp > 0 && l.acao?.nome === "esquivar") {
        fantasmas++; expect(ef.fantasmas.length).toBe(POSTURA.fantasmas.length);
        /* abrem: a segunda copia fica mais longe que a primeira */
        expect(ef.fantasmas[1].dx).toBeGreaterThan(ef.fantasmas[0].dx);
      } else expect(ef.fantasmas).toEqual([]);
      if (l.hp > 0 && l.acao?.nome === "carregar") {
        auras++; expect(ef.aura).toBe(true);
        /* o chao do carregar e a elipse tracejada da E3; a aura so tem pixels acima do chao (dy <= 0) */
        expect(telegrafiaDoPasso(l, p)?.tipo).toBe("carregar");
        expect(pixelsDaAura("cirro", 12, 40, p, false).every(x => x.dy <= 0)).toBe(true);
      }
      if (l.hp > 0 && p < l.peleAte) { peles++; expect(ef.pele).not.toBeNull(); if (l.acao?.nome !== "pele_dura") peleForaDaAcao++; }
      else expect(ef.pele).toBeNull();
    }));
    expect(fantasmas).toBeGreaterThan(0); expect(auras).toBeGreaterThan(0); expect(peles).toBeGreaterThan(0);
    /* a pele dura vale alem da acao: o brilho continua depois do icone */
    expect(peleForaDaAcao).toBeGreaterThan(0);
  });
});

/** a marca de tudo o que a E4 desenha num passo: o icone, o efeito e os pixels de cada lado */
function marcasDasPosturas(a: string, b: string, s: number, reduzido: boolean) {
  const out: string[] = [];
  const r = jogar(a, b, s, (sim, v) => {
    const p = sim.S.passo;
    out.push(JSON.stringify([p, sim.S.L.map((l, i) => {
      const ic = posturaDoLado(l), ef = efeitoDaPostura(l, i, p, v.batidas, reduzido);
      return [ic, ic ? pixelsDoIcone(ic, "limo", i) : null, ef,
        ef.escudo ? pixelsDoEscudo(30, ef.escudo.aceso) : null,
        ef.contra ? pixelsDoContra(ef.contra.guarda, ef.contra.clarao, p, reduzido) : null,
        ef.aura ? pixelsDaAura("brasa", 12, 40, p, reduzido) : null];
    }), v.batidas]));
  });
  return { out, ...r };
}

describe("E4: so vista, deterministico", () => {
  test("mesma luta, mesmas posturas; o fim e o do ResultadoLutaTR", () => {
    for (const [a, b, s] of [...LUTAS, ["agressivo", "vigia", 4242]] as const) {
      const res = jogarLuta(lutadorBot(a, R), lutadorBot(b, R), s, R).tr!;
      for (const red of [false, true]) {
        const x = marcasDasPosturas(a, b, res.entrada.semente, red), y = marcasDasPosturas(a, b, res.entrada.semente, red);
        expect(x.out).toEqual(y.out);
        expect(x.passos).toBe(res.passos); expect(x.fim![0]).toBe(res.pontosA); expect(x.fim![1]).toBe(res.fim);
      }
    }
  });
  test("as posturas nao empurram: com ou sem os efeitos, as posicoes da luta e o estado visual da E1-E3 sao os mesmos", () => {
    const xs = (com: boolean) => {
      const out: string[] = [];
      jogar("tita", "espelho", 7, (sim, v) => {
        if (com) sim.S.L.forEach((l, i) => efeitoDaPostura(l, i, sim.S.passo, v.batidas, false));
        out.push(JSON.stringify([sim.S.L.map(l => [l.x, l.hp, l.deslizeAte]), v.impactos, v.marcas, v.numeros]));
      });
      return out;
    };
    expect(xs(true)).toEqual(xs(false));
  });
  test("todos os pixels de postura na grade do sprite (deslocamento e tamanho inteiros)", () => {
    for (const el of ["brasa", "cirro", "ferrugem", "limo"] as const) for (let p = 0; p < 40; p += 3) for (const red of [false, true]) {
      const todos = [...pixelsDoEscudo(17 + p % 5, (p % 10) / 10), ...pixelsDoContra(p % 2 === 0, (p % 7) / 7, p, red), ...pixelsDaAura(el, 11, 37, p, red),
        ...POSTURAS_TR.flatMap(q => pixelsDoIcone(q, el, p % 2))];
      for (const x of todos) { expect(Number.isInteger(x.dx) && Number.isInteger(x.dy) && Number.isInteger(x.tam)).toBe(true); expect(x.tam).toBeGreaterThan(0); }
    }
    for (const g of efeitoDaPostura({ ...lutadorEsquivando(), acao: { ...lutadorEsquivando().acao!, inicio: 0 } }, 0, 2, [], false).fantasmas) expect(Number.isInteger(g.dx)).toBe(true);
  });
  test("com o movimento reduzido nada pisca nem treme: o mesmo desenho em todo passo, sem clarao nem escudo aceso; os icones ficam", () => {
    for (let p = 0; p < 40; p++) {
      expect(pixelsDaAura("cirro", 12, 40, p, true)).toEqual(pixelsDaAura("cirro", 12, 40, 0, true));
      expect(pixelsDoContra(true, 0, p, true)).toEqual(pixelsDoContra(true, 0, 0, true));
    }
    expect(pixelsDaAura("cirro", 12, 40, 0, false)).not.toEqual(pixelsDaAura("cirro", 12, 40, 5, false));
    let icones = 0;
    jogar("tita", "espelho", 7, (sim, v) => sim.S.L.forEach((l, i) => {
      const ef = efeitoDaPostura(l, i, sim.S.passo, v.batidas, true);
      expect(ef.escudo?.aceso ?? 0).toBe(0); expect(ef.contra?.clarao ?? 0).toBe(0);
      if (ef.pele) expect(ef.pele.faixa).toBeNull();
      if (l.acao?.nome === "esquivar") expect(ef.fantasmas.map(g => g.dx)).toEqual(POSTURA.fantasmas.map((_, k) => (k + 1) * POSTURA.fantasmaPx));
      if (posturaDoLado(l)) icones++;
    }));
    expect(icones).toBeGreaterThan(0);
  });
});

/** um lado no comeco da esquiva (so os campos que efeitoDaPostura le) */
function lutadorEsquivando(): Sim["S"]["L"][number] {
  const sim = criarLutaTR(lutadorBot("tita", R), lutadorBot("espelho", R), 7, { R });
  const l = sim.S.L[0];
  return { ...l, acao: { nome: "esquivar", motivo: 0, inicio: 0, fim: 10, idx: 0, x0: l.x, feito: false, sentinela: false } };
}
