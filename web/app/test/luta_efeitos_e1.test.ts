/* LUTA_EFEITOS, E1 (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.5 e 4): o estado visual do impacto e o mesmo para a mesma luta, passo a passo;
   respeita os limites da D-LE-2 (tremida <= 4 px inteiros, clarao de 2 quadros); e nenhum efeito muda o resultado da luta. */
import { describe, expect, test } from "vitest";
import { criarLutaTR, jogarLuta, lutadorBot, passoTR, regrasDaVersao } from "../motor/index.ts";
import { IMPACTO, aplicarEventosTR, clarao, consumirPausa, empurraoDoPasso, faiscaDoPasso, pixelsDoTexto, tremidaDoPasso, visualNovoTR } from "../src/telas/lutar/palcoTR/efeitosTR.ts";

/** refaz a luta e devolve a marca dos efeitos a cada passo, mais o resultado do passo final */
function efeitos(a: string, b: string, semente: number, com: boolean) {
  const R = regrasDaVersao(14), res = jogarLuta(lutadorBot(a as never, R), lutadorBot(b as never, R), semente, R), en = res.tr!.entrada;
  const sim = criarLutaTR(en.A, en.B, en.semente, { ...en.o, eventos: true }), v = visualNovoTR(), marcas: string[] = [];
  let lidos = 0, fim: unknown = null, danos = 0, pausa = 0;
  for (;;) {
    fim = passoTR(sim, en.o.desafiado ?? null);
    if (com) {
      const ev = sim.eventos!.slice(lidos); lidos = sim.eventos!.length; danos += ev.filter(e => e.tipo === "dano").length;
      aplicarEventosTR(v, sim, ev); pausa += consumirPausa(v, false);
      const p = sim.S.passo;
      marcas.push(JSON.stringify([p, tremidaDoPasso(v, p), [0, 1].map(l => [clarao(v, p, l), empurraoDoPasso(v, p, l)]), v.impactos.map(i => faiscaDoPasso(i, p)), v.numeros.map(n => [n.txt, n.forte])]));
    }
    if (fim) break;
  }
  return { marcas, fim, passos: sim.S.passo, res: res.tr!, danos, pausa };
}

describe("E1, o impacto: so vista, deterministico", () => {
  for (const [a, b, s] of [["duelista", "tita", 4242], ["emboscador", "muralha", 101], ["furioso", "espelho", 777]] as const) test(`${a} x ${b}: mesma luta, mesmos efeitos`, () => {
    const x = efeitos(a, b, s, true), y = efeitos(a, b, s, true), sem = efeitos(a, b, s, false);
    expect(x.marcas).toEqual(y.marcas); expect(x.danos).toBeGreaterThan(0); expect(x.pausa).toBeGreaterThan(0);
    expect(x.marcas.some(m => JSON.parse(m)[1].x !== 0)).toBe(true);
    /* os efeitos nao mudam o fim nem a duracao da luta, que e a do resultado */
    expect(x.fim).toEqual(sem.fim); expect(x.passos).toBe(sem.passos); expect(x.passos).toBe(x.res.passos);
    expect((x.fim as [number, string])[0]).toBe(x.res.pontosA);
  });
  test("a tremida fica em px inteiros e ate o maximo; o clarao dura 2 quadros; o empurrao volta a zero; a pausa some com o movimento reduzido", () => {
    const x = efeitos("furioso", "espelho", 777, true);
    for (const m of x.marcas) {
      const t = JSON.parse(m)[1]; for (const n of [t.x, t.y]) { expect(Number.isInteger(n)).toBe(true); expect(Math.abs(n)).toBeLessThanOrEqual(IMPACTO.tremidaMaxPx); }
    }
    const v = visualNovoTR(); v.impactos.push({ lado: 0, t0: 100, frac: 1, forte: true });
    expect(clarao(v, 100, 0)).toBe(true); expect(clarao(v, 100 + IMPACTO.clarao, 0)).toBe(false); expect(clarao(v, 100, 1)).toBe(false);
    expect(empurraoDoPasso(v, 100 + IMPACTO.durEmpurrao, 0)).toBe(0); expect(empurraoDoPasso(v, 104, 0)).toBeGreaterThan(0);
    expect(Math.abs(tremidaDoPasso(v, 100).x)).toBeLessThanOrEqual(4);
    v.pausaMs = 70; expect(consumirPausa(v, true)).toBe(0); expect(v.pausaMs).toBe(0);
    v.pausaMs = 70; expect(consumirPausa(v, false)).toBe(70);
  });
  test("a fonte de pixel desenha o dano e falha alto sem glifo", () => {
    expect(pixelsDoTexto("-12.5").w).toBe(5 * 4 - 1); expect(() => pixelsDoTexto("-a")).toThrow(/glifo/);
  });
});
