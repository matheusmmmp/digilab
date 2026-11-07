/* LUTA_EFEITOS, E2 (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4, 3.5 e 4; D-LE-1): os projeteis e os golpes por elemento, so vista.
   - O defeito do disparo que nao aparecia (o Gabumon contra o Vigia, no GIF do empurrao): em todo passo em que o projetil existe no S.projeteis,
     a cabeca dele e desenhada entre o atirador e o alvo, na altura do corpo, e fica na tela em quadros suficientes mesmo quando o motor o faz
     acertar em 5 passos.
   - O desenho dos efeitos e o mesmo para a mesma luta, passo a passo, e nenhum efeito muda o ResultadoLutaTR.
   - Todo lutador da tela tem elemento; os pixels ficam na grade do sprite; o movimento reduzido nao pisca nem estica o rastro. */
import { describe, expect, test } from "vitest";
import { BOTS_V21, CV21E_TR18, Cd, LIGA, NPC, Rg, chaveSprite, criarLutaTR, formaLiga, formaRival, jogarLuta, lutadorBot, passoTR, perfilNeutro,
  type FormaAdultaNormal, type Lutador } from "../motor/index.ts";
import { RIVAIS_CLASSICOS } from "../src/luta.ts";
import { aplicarEventosTR, visualNovoTR } from "../src/telas/lutar/palcoTR/efeitosTR.ts";
import { ELEMENTO_SEM_LINHAGEM, elementoDoSprite } from "../src/telas/lutar/palcoTR/elementosTR.ts";
import { GOLPES_RAJADA, VOO, cabecaVisivel, fracaoDaRajada, fracaoDoVoo, geometriaTR, pixelsDaCabeca, pixelsDoEstouro, pixelsDoRastro, pontoDoVoo, xTela } from "../src/telas/lutar/palcoTR/projeteisTR.ts";

const R = CV21E_TR18;
const cheio = () => ({ ...perfilNeutro(), guts0: 1000, gutsMax: 1000, regen: 1000 });
const lista = (regras: ReturnType<typeof Rg>[], final = "carregar"): Lutador =>
  ({ nome: "teste", estilo: { nome: "teste", gambits: { regras, final }, eps: 0 }, cond: cheio() });
/** atira sempre (de longe, do medio e do contato: o alvo avanca ate encostar) */
const atirador = () => lista([Rg(Cd("sempre"), "disparo")]);
/** o passo de desenho do luta.ts: 3 passos por quadro, 12 com o movimento reduzido */
const QUADRO = 3, QUADRO_REDUZ = 12;
/** as medidas de dois sprites (o Gabumon e um adulto do tamanho do Zudomon) e as telas de 390 e 1280 px */
const DIMS = [[38, 40], [64, 60]] as const, TELAS = [[390, 560, 2], [1280, 720, 1]] as const;

/** joga a luta passo a passo como o luta.ts (os eventos de cada passo no estado visual) e chama olhar a cada passo */
function jogar(A: Lutador, B: Lutador, s: number, olhar: (sim: ReturnType<typeof criarLutaTR>, v: ReturnType<typeof visualNovoTR>) => void) {
  const sim = criarLutaTR(A, B, s, { R, eventos: true }), v = visualNovoTR();
  let lidos = 0, fim = null;
  while (!fim) { fim = passoTR(sim); aplicarEventosTR(v, sim, sim.eventos!.slice(lidos)); lidos = sim.eventos!.length; olhar(sim, v); }
  return { fim, passos: sim.S.passo };
}

describe("E2: o projetil aparece", () => {
  for (const [nome, A, B, s] of [["atirador contra o vigia", atirador(), lutadorBot("vigia", R), 7], ["vigia contra o atirador", lutadorBot("vigia", R), atirador(), 11],
    ["o bot atirador contra o vigia", lutadorBot("atirador", R), lutadorBot("vigia", R), 7]] as const) test(`${nome}: a cabeca e desenhada entre o atirador e o alvo em todo passo do voo`, () => {
    let passosComProjetil = 0;
    jogar(A, B, s, (sim, v) => {
      const S = sim.S, xs = S.L.map(l => l.x);
      for (const pr of S.projeteis) {
        passosComProjetil++;
        const doLado = v.voos.filter(o => o.de === pr.de && o.tFim === null && cabecaVisivel(o, S.passo));
        expect(doLado.length).toBeGreaterThan(0);
        for (const [W, H, K] of TELAS) {
          const g = geometriaTR(W, H, K, DIMS, xs), alvo = 1 - pr.de;
          for (const o of doLado) {
            const p = pontoDoVoo(g, o.de, fracaoDoVoo(o, S.passo)!), [lo, hi] = [g.centros[pr.de], g.centros[alvo]].sort((a, b) => a - b);
            /* entre os dois (estritamente entre os centros: na frente do atirador e antes do meio do alvo) */
            expect(p.x).toBeGreaterThan(lo); expect(p.x).toBeLessThan(hi);
            /* na altura do corpo do atirador, nao nos pes (a causa antiga: PES - 28 px, a 10 px do chao no celular) */
            expect(p.y).toBeGreaterThan(g.topo[pr.de]); expect(p.y).toBeLessThan(g.PES - (g.PES - g.topo[pr.de]) * .3);
          }
        }
      }
    });
    expect(passosComProjetil).toBeGreaterThan(0);
  });

  test("a causa: o voo no motor pode durar 5 passos (2 quadros, ou nenhum no movimento reduzido); a cabeca fica pelo menos 4 quadros", () => {
    const vidas: number[] = [], quadros: number[] = [], quadrosReduz: number[] = [];
    const vistos = new Map<object, { normal: number; reduz: number }>();
    /* o bot atirador contra o vigia: o vigia avanca ate encostar, e o disparo no contato acerta em 5 passos */
    jogar(lutadorBot("atirador", R), lutadorBot("vigia", R), 7, (sim, v) => {
      for (const o of v.voos) {
        const q = vistos.get(o) ?? { normal: 0, reduz: 0 }; vistos.set(o, q);
        if (sim.S.passo % QUADRO === 0 && cabecaVisivel(o, sim.S.passo)) q.normal++;
        if (sim.S.passo % QUADRO_REDUZ === 0 && cabecaVisivel(o, sim.S.passo)) q.reduz++;
        if (o.tFim === sim.S.passo) vidas.push(o.tFim - o.t0);
      }
    });
    for (const [o, q] of vistos) if ((o as { tFim: number | null }).tFim !== null) { quadros.push(q.normal); quadrosReduz.push(q.reduz); }
    expect(vidas.length).toBeGreaterThan(1);
    /* o motor faz acertar em poucos passos no contato: o circulo antigo, so enquanto o projetil existia, saia em 1 ou 2 quadros */
    expect(Math.min(...vidas)).toBeLessThanOrEqual(6);
    expect(Math.min(...quadros)).toBeGreaterThanOrEqual(Math.floor(VOO.minVisivel / QUADRO));
    expect(Math.min(...quadrosReduz)).toBeGreaterThanOrEqual(1);
  });

  test("o golpe rapido que acerta de perto ganha a rajada da boca de quem bate a frente do alvo (o sopro do Gabumon que nao chegava ao Vigia)", () => {
    let rajadas = 0;
    jogar(lista([Rg(Cd("distancia_eh", 0), "golpe_rapido"), Rg(Cd("sempre"), "avancar")]), lutadorBot("vigia", R), 7, (sim, v) => {
      for (const im of v.impactos) {
        const idade = sim.S.passo - im.t0, f = fracaoDaRajada(idade);
        if (!im.golpe || !GOLPES_RAJADA.includes(im.golpe) || f === null) continue;
        rajadas++;
        const de = 1 - im.lado, g = geometriaTR(1280, 720, 1, DIMS, sim.S.L.map(l => l.x)), p = pontoDoVoo(g, de, f), [lo, hi] = [g.centros[de], g.centros[im.lado]].sort((a, b) => a - b);
        expect(p.x).toBeGreaterThan(lo); expect(p.x).toBeLessThan(hi);
      }
    });
    expect(rajadas).toBeGreaterThan(0);
    expect(fracaoDaRajada(VOO.rajada - 2)).toBe(1); expect(fracaoDaRajada(VOO.rajada)).toBeNull(); expect(fracaoDaRajada(-1)).toBeNull();
  });

  test("a causa: o circulo antigo nascia no centro do corpo do atirador, dentro do sprite dele", () => {
    const g = geometriaTR(1280, 720, 1, DIMS, [175, 219]), antigo = xTela(175, 1280), novo = pontoDoVoo(g, 0, 0).x;
    expect(antigo).toBeLessThan(g.centros[0] + g.meias[0]);
    expect(novo).toBeGreaterThan(g.centros[0]);
  });
});

/** a marca de tudo o que a E2 desenha num passo: os voos (fracao, cabeca, rastro) e os estouros */
function marcas(A: Lutador, B: Lutador, s: number, reduzido: boolean) {
  const el = [elementoDoSprite("cirro_crianca_arisco"), elementoDoSprite(chaveSprite(formaRival("vigia")))], out: string[] = [];
  const r = jogar(A, B, s, (sim, v) => {
    const p = sim.S.passo;
    out.push(JSON.stringify([p, v.voos.map(o => [o.de, fracaoDoVoo(o, p), cabecaVisivel(o, p) ? pixelsDaCabeca(el[o.de], p, reduzido) : null,
      [1, 2].map(j => pixelsDoRastro(el[o.de], j, VOO.rastro, p, reduzido))]), v.impactos.map(i => [i.golpe, fracaoDaRajada(p - i.t0), pixelsDoEstouro(el[1 - i.lado], p - i.t0, i.forte, reduzido)])]));
  });
  return { out, ...r };
}

describe("E2: so vista, deterministico", () => {
  test("mesma luta, mesmos projeteis e estouros; o fim e o do ResultadoLutaTR", () => {
    for (const [a, b, s] of [["atirador", "vigia", 4242], ["emboscador", "duelista", 101], ["sentinela", "tita", 777]] as const) {
      const A = lutadorBot(a, R), B = lutadorBot(b, R), res = jogarLuta(A, B, s, R).tr!, en = res.entrada;
      const x = marcas(en.A, en.B, en.semente, false), y = marcas(en.A, en.B, en.semente, false);
      expect(x.out).toEqual(y.out);
      /* com os efeitos lidos a cada passo, a luta acaba no mesmo passo e com os mesmos pontos do resultado guardado */
      expect(x.passos).toBe(res.passos); expect(x.fim![0]).toBe(res.pontosA); expect(x.fim![1]).toBe(res.fim);
    }
  });
  test("o atirador contra o vigia: algum voo e algum estouro aparecem", () => {
    const x = marcas(atirador(), lutadorBot("vigia", R), 7, false);
    expect(x.out.some(m => JSON.parse(m)[1].length > 0)).toBe(true);
    expect(x.out.some(m => JSON.parse(m)[2].some((e: unknown[]) => (e[2] as unknown[]).length > 0))).toBe(true);
  });
});

describe("E2: o elemento de cada lutador (D-LE-1)", () => {
  test("a linhagem: o Gabumon e cirro, o Agumon brasa, o vigia (Zudomon) limo", () => {
    expect(elementoDoSprite("cirro_crianca_arisco")).toBe("cirro");
    expect(elementoDoSprite("brasa_crianca_sereno")).toBe("brasa");
    expect(elementoDoSprite(chaveSprite(formaRival("vigia")))).toBe("limo");
  });
  test("todo rival da tela tem elemento: bots classicos, adultos, NPCs e a Liga; sprite sem elemento falha alto", () => {
    for (const n of RIVAIS_CLASSICOS) expect(() => elementoDoSprite("bot_" + n)).not.toThrow();
    for (const n of Object.keys(BOTS_V21)) expect(() => elementoDoSprite(chaveSprite(formaRival(n as FormaAdultaNormal)))).not.toThrow();
    for (const n of Object.values(NPC)) expect(() => elementoDoSprite(n!.sprite ?? n!.k)).not.toThrow();
    LIGA.forEach((_, i) => expect(() => elementoDoSprite(chaveSprite(formaLiga(i)))).not.toThrow());
    for (const k of Object.keys(ELEMENTO_SEM_LINHAGEM)) expect(k.startsWith("bot_") || NPC[k] !== undefined || Object.values(NPC).some(n => n!.sprite === k)).toBe(true);
    expect(() => elementoDoSprite("bot_desconhecido")).toThrow(/sem elemento/);
  });
});

describe("E2: pixel e movimento reduzido", () => {
  const els = ["brasa", "cirro", "ferrugem", "limo"] as const;
  test("todos os pixels na grade do sprite (deslocamento e tamanho inteiros)", () => {
    for (const el of els) for (let p = 0; p < 6; p++) for (const red of [false, true]) {
      const todos = [...pixelsDaCabeca(el, p, red), ...pixelsDoRastro(el, 1 + p, VOO.rastro, p, red), ...pixelsDoEstouro(el, p * 2, p % 2 === 0, red)];
      for (const x of todos) { expect(Number.isInteger(x.dx) && Number.isInteger(x.dy) && Number.isInteger(x.tam)).toBe(true); expect(x.tam).toBeGreaterThan(0); }
    }
  });
  test("com o movimento reduzido a cabeca nao pisca (igual em todo passo), o estouro nao clareia e o rastro e curto", () => {
    for (const el of els) {
      expect(pixelsDaCabeca(el, 1, true)).toEqual(pixelsDaCabeca(el, 2, true));
      expect(pixelsDaCabeca(el, 1, true).length).toBeGreaterThan(10);
      expect(pixelsDoEstouro(el, 0, true, true).some(p => p.alfa === .55)).toBe(false);
      expect(pixelsDoRastro(el, 1, VOO.rastroReduzido, 3, true)).toHaveLength(1);
    }
    expect(VOO.rastroReduzido).toBeLessThanOrEqual(2);
  });
});
