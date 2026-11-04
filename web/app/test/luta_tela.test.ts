// A tela da luta no layout habitat (B3, etapa 2; docs/TAREFA_V3_LUTA_LAYOUT.md, testes 2 e 3). Sem DOM (vitest em node): renderToStaticMarkup.
//   - os data-testid e os aria-label de hoje existem; o relogio mostra m:ss, "ate 1:20" e "morte subita" nos casos certos; o cartao de contexto
//     mostra o texto de serie, Liga, carta e Lago; a etiqueta do modo; o dock;
//   - o desenho nao mexe na simulacao: a luta refeita passo a passo com os numeros que sobem (aplicarEventosTR) e sem eles da o mesmo estado
//     quadro a quadro, nos pets v13, v14 e v15 (o motor em web/app/motor nao muda nesta tarefa).
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { CTR_TR, Motor, PASSO_TR_MS, criarLutaTR, jogarLuta, lutadorBot, passoTR, regrasDaVersao } from "../motor/index.ts";
import { iniciarJogo } from "../src/jogo.ts";
import { LUTA, exibirBot, exibirPet, type Palco } from "../src/luta.ts";
import { type Armazenamento } from "../src/save.ts";
import { TelaLuta, etiquetaModo } from "../src/telas/lutar/TelaLuta.tsx";
import { PalcoTR, relogio } from "../src/telas/lutar/palcoTR/PalcoTR.tsx";
import { aplicarEventosTR, visualNovoTR } from "../src/telas/lutar/palcoTR/desenhoTR.ts";
import { cartaDe } from "../motor/index.ts";

/* o aviso de som usa useSyncExternalStore sem getServerSnapshot: no render de servidor ele sai (nao e da luta) */
vi.mock("../src/componentes/AvisoSom.tsx", () => ({ AvisoSom: () => null }));

let dados: Record<string, string>;
const armaz = (): Armazenamento => ({ getItem: k => (k in dados ? dados[k]! : null), setItem(k, v) { dados[k] = v; } });
beforeEach(() => { dados = {}; vi.stubGlobal("Image", class { onload: (() => void) | null = null; onerror: (() => void) | null = null; set src(_: string) { /* o mapa nunca carrega no node */ } }); vi.stubGlobal("localStorage", { getItem: (k: string) => (k in dados ? dados[k]! : null), setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; } }); });
afterEach(() => { vi.unstubAllGlobals(); LUTA.palco = null; LUTA.replay = null; LUTA.lutando = false; LUTA.rivalFixo = null; });

function palcoDe(extra: Partial<Palco> = {}): Palco {
  const m = new Motor(101); m.avancar(300);
  iniciarJogo(armaz());
  const A = exibirPet(m, lutadorBot("duelista", regrasDaVersao(14))), B = exibirBot("agressivo");
  return { modo: "arena", A, B, cena: "ringue", hud: [{ hp: 80, hpMax: 100, guts: 40, gutsMax: 100 }, { hp: 55, hpMax: 100, guts: 10, gutsMax: 100 }], sim: null, visual: visualNovoTR(),
    koEm: [null, null], segundos: 75, morteSubita: false, regra: { motivo: "exploracao", nome: "golpe_rapido" }, texto: "Seu pet acertou", callout: "", resultado: null, ...extra };
}
const tela = (p: Palco, ajuda: Partial<{ replay: number | null; lutando: boolean }> = {}): string => {
  LUTA.palco = p; LUTA.replay = ajuda.replay ?? null; LUTA.lutando = ajuda.lutando ?? true;
  return renderToStaticMarkup(h(TelaLuta, { sair: () => {}, verReplay: () => {}, sairReplay: () => {}, pedidoDesistir: false, fecharPedido: () => {} }));
};

describe("TelaLuta: a estrutura da B3", () => {
  test("os data-testid e os aria-label de hoje existem, e o dock tem Pausar, x2 e Desistir", () => {
    const s = tela(palcoDe());
    for (const t of ['data-testid="luta-relogio"', 'data-testid="luta-regra"']) expect(s).toContain(t);
    for (const a of ['aria-label="Palco da luta"', 'aria-label="tempo da luta"', 'aria-label="vida do seu pet"', 'aria-label="guts do seu pet"', 'aria-label="vida do rival"',
      'aria-label="guts do rival"', 'aria-label="Pausar a animação"', 'aria-label="Velocidade dobrada"']) expect(s).toContain(a);
    expect(s).toMatch(/class="luta-dock hud-caixa"/);
    expect(s).toMatch(/luta-desistir[^>]*>Desistir</);
    expect(s).toContain("O QUE ");   /* a frase "o que <pet> faz" */
    expect(s).toContain("Regra em uso");
    expect(s).toContain("Seu pet acertou");   /* o texto do ultimo evento */
  });
  test("as plaquinhas e o relogio sao caixas de HUD; a faixa do titulo de antes saiu", () => {
    const s = tela(palcoDe());
    expect(s.match(/hud-lado[^"]*hud-caixa/g)).toHaveLength(2);
    expect(s).toContain("hud-meio hud-caixa");
    expect(s).not.toContain("luta-topo"); expect(s).not.toContain("luta-controles");
    expect(s).toContain('id="luta-tit"');
  });
  test("pausado o botao diz Continuar; sem luta animada o dock so tem o Desistir desabilitado", () => {
    LUTA.pausado = true;
    expect(tela(palcoDe())).toContain('aria-label="Continuar a animação"');
    LUTA.pausado = false;
    const s = tela(palcoDe(), { lutando: false });
    expect(s).not.toContain("Pausar a animação"); expect(s).toMatch(/luta-desistir[^>]*disabled/);
  });
  test("no replay o dock tem Sair do replay no lugar de Desistir e a etiqueta diz refeita do registro", () => {
    const s = tela(palcoDe(), { replay: 3 });
    expect(s).toContain("Sair do replay"); expect(s).not.toContain(">Desistir<");
    expect(s).toContain("Replay · Arena"); expect(s).toContain("refeita do registro");
  });
  test("sem luta em andamento: o cartao no meio", () => {
    LUTA.palco = null;
    expect(renderToStaticMarkup(h(TelaLuta, { sair: () => {}, verReplay: () => {}, sairReplay: () => {}, pedidoDesistir: false, fecharPedido: () => {} }))).toContain("Nenhuma luta em andamento.");
  });
});

describe("o relogio", () => {
  const fim = Math.round(CTR_TR.limite * PASSO_TR_MS / 1000);
  test("m:ss, o limite e a morte subita", () => {
    expect(relogio(75)).toBe("1:15"); expect(relogio(5)).toBe("0:05"); expect(relogio(fim)).toBe("1:20");
    const a = tela(palcoDe({ segundos: 75 }));
    expect(a).toMatch(/data-testid="luta-relogio">1:15</); expect(a).toContain("até 1:20");
    const b = tela(palcoDe({ segundos: 82, morteSubita: true }));
    expect(b).toContain("morte súbita"); expect(b).not.toContain("até 1:20");
    expect(tela(palcoDe({ segundos: null }))).toMatch(/data-testid="luta-relogio">–</);
  });
});

describe("a etiqueta do modo e o cartao de contexto", () => {
  test("a etiqueta por modo", () => {
    const p = palcoDe();
    expect(etiquetaModo(p, "arena", false, null, false)).toBe("Arena · treino");
    expect(etiquetaModo(p, "arena", false, "2 de 5", false)).toBe("Arena · treino 2 de 5");
    expect(etiquetaModo(p, "arena", false, null, true)).toBe("Arena · cenário");
    expect(etiquetaModo({ ...p, modo: "campanha", serie: { k: 2, n: 3 } }, "campanha", false, null, false)).toBe("Campanha · Luta 2 de 3");
    expect(etiquetaModo(p, "fronteira", true, null, false)).toBe("Replay · Fronteira · refeita do registro");
  });
  test("serie (Cidadela), Liga, carta e Lago mostram o texto de hoje", () => {
    const cid = tela(palcoDe({ modo: "campanha", serie: { k: 2, n: 3 } }));
    expect(cid).toContain("Campanha · Luta 2 de 3"); expect(cid).toContain("Cidadela: sem cura entre as lutas");
    const liga = tela(palcoDe({ modo: "fronteira", serie: { k: 1, n: 6 }, liga: true }));
    expect(liga).toContain("Liga dos Líderes · luta 1 de 6"); expect(liga).toContain("Sem cura entre as lutas; as cartas não valem.");
    const aviso = tela(palcoDe({ modo: "campanha", serie: { k: 1, n: 2 }, avisoSerie: "Aviso da Fábrica" }));
    expect(aviso).toContain("Aviso da Fábrica");
    const id = "carta_cura";
    const carta = tela(palcoDe({ carta: id }));
    expect(carta).toContain('data-testid="luta-carta"'); expect(carta).toContain(cartaDe(id).nome); expect(carta).toContain(cartaDe(id).efeito);
    const lago = tela(palcoDe({ arena: { regra: "vinculo" } as unknown as Palco["arena"] }));
    expect(lago).toContain("Arena do Lago:"); expect(lago).toContain("aqui as suas travas e vetos não valem");
  });
  test("o PalcoTR sozinho tem o cartao da regra (a leitura de antes) e nenhum controle", () => {
    LUTA.palco = palcoDe();
    const s = renderToStaticMarkup(h(PalcoTR));
    expect(s).toContain("palco-luta-baixo"); expect(s).not.toContain("<button");
  });
});

/* o desenho nao mexe na simulacao: dois replays da mesma luta, um aplicando os numeros que sobem (o que o palco faz) e outro so passando o
   motor, dao o mesmo estado a cada quadro. v13, v14 e v15 (a v15 luta com as regras da v14: regrasDaVersao) */
describe("o replay quadro a quadro nao muda com o desenho", () => {
  const marca = (S: ReturnType<typeof criarLutaTR>["S"]): string =>
    JSON.stringify({ passo: S.passo, L: S.L.map(l => [l.x, l.hp, l.guts, l.atordoadoAte, l.acao?.nome ?? null]), pr: S.projeteis.map(q => [q.de, q.x]) });
  for (const versao of [13, 14, 15]) test(`pet v${versao}: 3 lutas, todos os quadros iguais, e o fim e o do motor`, () => {
    const R = regrasDaVersao(versao);
    for (const [a, b, semente] of [["duelista", "tita", 4242], ["emboscador", "muralha", 101], ["furioso", "espelho", 777]] as const) {
      const res = jogarLuta(lutadorBot(a, R), lutadorBot(b, R), semente, R), en = res.tr!.entrada;
      const comDesenho = criarLutaTR(en.A, en.B, en.semente, { ...en.o, eventos: true }), semDesenho = criarLutaTR(en.A, en.B, en.semente, { ...en.o });
      const v = visualNovoTR(); let lidos = 0, fimA: unknown = null, fimB: unknown = null, n = 0;
      for (;;) {
        const f1 = passoTR(comDesenho, en.o.desafiado ?? null), f2 = passoTR(semDesenho, en.o.desafiado ?? null);
        aplicarEventosTR(v, comDesenho, comDesenho.eventos!.slice(lidos)); lidos = comDesenho.eventos!.length;
        expect(marca(comDesenho.S), `${a} x ${b}, passo ${n}`).toBe(marca(semDesenho.S));
        n++;
        if (f1 || f2) { fimA = f1; fimB = f2; break; }
      }
      expect(fimA).toEqual(fimB);
      expect(comDesenho.S.passo).toBe(res.tr!.passos);
      expect((fimA as [number, string])[0]).toBe(res.tr!.pontosA);
    }
  });
});
