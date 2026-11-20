// Mudar de canal na TV do dono (GOSTO_VISUAL, 2026-11-12; docs/registro/2026-11.md, D-GV-CANAL-1 a 8; src/gostoVisual/canais.ts e
// sessaoTv.ts). Sem DOM (vitest em node): as fontes são falsas, cada uma devolvendo um vetor constante. Cobre a lista de canais (até
// MAX_CANAIS, a troca dando a volta, a lista cheia, a fonte encerrada saindo), a leitura só do canal atual, o quadro anterior atravessando a
// troca, e, no jogo, o "st" só com os números do canal atual e a troca sem parar a sessão nem o cérebro.
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { Motor, ResumoTela, valorSentidoTelaDesligada, type EventoRegistro } from "../motor/index.ts";
import { ligarProduto } from "../src/produto.ts";
import { CHAVE, textoSave } from "../src/save.ts";
import { iniciarJogo, jogoAtual } from "../src/jogo.ts";
import { Canais, MAX_CANAIS, PERIODO_MS, type Fonte } from "../src/gostoVisual/canais.ts";
import { vetorDoSentido } from "../src/gostoVisual/cerebroTv.ts";
import { ligarCanal, pararTv, proximoCanal, sessaoTv, usarPet } from "../src/gostoVisual/sessaoTv.ts";
import { PainelTv, passandoEmPalavras } from "../src/gostoVisual/PainelTv.tsx";
import { TV } from "../src/gostoVisual/estadoTv.ts";
import type { Sentido } from "../src/gostoVisual/gosto.ts";

const sentido = (x: number): Sentido => ({ visao: { cor: x, brilho: x, movimento: x / 2, complexidade: x }, som: { volume: x / 3, variacao: x, timbre: x } });

interface Falsa extends Fonte { x: number; lidas: number; ativa: boolean; parada: boolean; anteriores: (number | null)[] }
/** uma fonte falsa: o mesmo vetor a cada segundo; a luminância é um número só, o próprio x */
function falsa(x: number, tipo: Fonte["tipo"] = "tela"): Falsa {
  const f: Falsa = {
    x, tipo, temSom: tipo === "tela", video: null, lidas: 0, ativa: false, parada: false, anteriores: [],
    sentir(anterior) { if (f.parada) throw new Error("leu uma fonte parada"); f.lidas++; f.anteriores.push(anterior === null ? null : anterior[0]!); return { sentido: sentido(x), lum: new Float32Array([x]) }; },
    ativar(sim) { f.ativa = sim; },
    parar() { f.parada = true; f.ativa = false; },
  };
  return f;
}

describe("a lista de canais (canais.ts)", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  test("até MAX_CANAIS; o novo vira o atual; o Canal ▸ dá a volta; só o canal atual é lido; o quadro anterior atravessa a troca", () => {
    expect(MAX_CANAIS).toBe(3);
    const vistos: number[] = [];
    let mudou = 0;
    const c = new Canais(s => vistos.push(s.visao.cor), () => { mudou++; }, () => { throw new Error("não acabou"); });
    const a = falsa(0.1), b = falsa(0.2), d = falsa(0.3);
    c.adicionar(a);
    expect(c.agora).toEqual({ n: 1, de: 1, tipo: "tela" }); expect(a.ativa).toBe(true);
    vi.advanceTimersByTime(2 * PERIODO_MS);
    c.adicionar(b);
    expect(c.agora).toEqual({ n: 2, de: 2, tipo: "tela" }); expect(a.ativa).toBe(false); expect(b.ativa).toBe(true);
    vi.advanceTimersByTime(2 * PERIODO_MS);
    c.proximo();                                                       // volta ao primeiro
    expect(c.atual).toBe(a); expect(a.ativa).toBe(true); expect(b.ativa).toBe(false);
    vi.advanceTimersByTime(PERIODO_MS);
    c.adicionar(d);
    vi.advanceTimersByTime(PERIODO_MS);
    expect(vistos).toEqual([0.1, 0.1, 0.2, 0.2, 0.1, 0.3]);
    expect([a.lidas, b.lidas, d.lidas]).toEqual([3, 2, 1]);
    /* o primeiro segundo de cada canal mede o movimento contra o último quadro do canal de antes (D-GV-CANAL-4) */
    const f = Math.fround;                                             // a luminância é Float32
    expect(a.anteriores).toEqual([null, f(0.1), f(0.2)]); expect(b.anteriores).toEqual([f(0.1), f(0.2)]); expect(d.anteriores).toEqual([f(0.1)]);
    c.proximo(); expect(c.atual).toBe(a);                              // 3 -> 1
    c.proximo(); c.proximo(); expect(c.atual).toBe(d);
    expect(mudou).toBe(7);
    c.parar();
    expect([a.parada, b.parada, d.parada]).toEqual([true, true, true]);
    vi.advanceTimersByTime(3 * PERIODO_MS);
    expect(vistos.length).toBe(6);                                     // parado, nada mais é lido
    expect(() => c.adicionar(falsa(0.4))).toThrow(/depois de parar/);
  });

  test("com a lista cheia, o canal novo toma o lugar do atual, que é solto; com um canal só, o Canal ▸ não muda nada", () => {
    const c = new Canais(() => undefined, () => undefined, () => undefined);
    const f = [falsa(0.1), falsa(0.2), falsa(0.3)];
    for (const x of f) c.adicionar(x);
    c.proximo();                                                       // o atual é o primeiro
    const novo = falsa(0.9);
    c.adicionar(novo);
    expect(c.quantos).toBe(MAX_CANAIS);
    expect(c.agora).toEqual({ n: 1, de: 3, tipo: "tela" });
    expect(c.atual).toBe(novo); expect(f[0]!.parada).toBe(true); expect(c.tem(f[0]!)).toBe(false);
    expect(f[1]!.parada || f[2]!.parada).toBe(false);
    expect(() => c.adicionar(novo)).toThrow(/já é um canal/);
    const so = new Canais(() => undefined, () => undefined, () => undefined), u = falsa(0.5);
    so.adicionar(u); so.proximo();
    expect(so.atual).toBe(u); expect(u.ativa).toBe(true);
    c.parar(); so.parar();
  });

  test("a fonte encerrada sai da lista: a de antes, a de depois e a atual; a última encerrada acaba a TV com o motivo", () => {
    const vistos: number[] = [], acabou: string[] = [];
    const c = new Canais(s => vistos.push(s.visao.cor), () => undefined, m => acabou.push(m));
    const [a, b, d] = [falsa(0.1), falsa(0.2), falsa(0.3)];
    c.adicionar(a); c.adicionar(b); c.adicionar(d); c.proximo(); c.proximo();      // o atual é o b (2 de 3)
    expect(c.atual).toBe(b);
    c.encerrada(a, "fim");                                             // antes do atual: o atual segue, agora 1 de 2
    expect(c.atual).toBe(b); expect(c.agora).toEqual({ n: 1, de: 2, tipo: "tela" }); expect(a.parada).toBe(true);
    c.encerrada(b, "fim");                                             // o atual: vai ao que ficou no lugar dele
    expect(c.atual).toBe(d); expect(d.ativa).toBe(true); expect(c.agora).toEqual({ n: 1, de: 1, tipo: "tela" });
    vi.advanceTimersByTime(PERIODO_MS);
    expect(vistos).toEqual([0.3]);
    expect(() => c.encerrada(a, "de novo")).toThrow(/não é canal/);
    expect(acabou).toEqual([]);
    c.encerrada(d, "o compartilhamento da tela acabou");
    expect(acabou).toEqual(["o compartilhamento da tela acabou"]); expect(c.atual).toBeNull();
    vi.advanceTimersByTime(3 * PERIODO_MS);
    expect(vistos).toEqual([0.3]);
  });

  test("o canal em palavras, sem o nome da janela nem o do arquivo", () => {
    expect(passandoEmPalavras({ origem: "tela", programa: null })).toBe("a sua tela");
    expect(passandoEmPalavras({ origem: "tela", programa: null, canal: { n: 1, de: 1, tipo: "tela" } })).toBe("a sua tela");
    expect(passandoEmPalavras({ origem: "tela", programa: null, canal: { n: 2, de: 3, tipo: "tela" } })).toBe("a sua tela, canal 2 de 3");
    expect(passandoEmPalavras({ origem: "tela", programa: null, canal: { n: 3, de: 3, tipo: "video" } })).toBe("um vídeo seu, canal 3 de 3");
    expect(passandoEmPalavras({ origem: "jogo", programa: "planilha" })).toBe("a TV do jogo, planilha");
  });
});

describe("a troca de canal na sessão e no cérebro (sessaoTv.ts e cerebroTv.ts)", () => {
  const dados: Record<string, string> = {};
  const fins = new Map<Fonte, (m: string) => void>();
  /** um canal falso pela mesma porta do seletor (ligarCanal); guarda o aoAcabar para o teste encerrar a fonte */
  const abrir = (f: Falsa) => ligarCanal(async aoAcabar => { fins.set(f, aoAcabar); return f; });
  beforeEach(() => {
    for (const k of Object.keys(dados)) delete dados[k];
    fins.clear();
    vi.stubGlobal("localStorage", { getItem: (k: string) => (k in dados ? dados[k]! : null), setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; } });
    vi.useFakeTimers();
  });
  afterEach(() => { pararTv(); vi.useRealTimers(); vi.unstubAllGlobals(); });

  /** o "st" que dez segundos de um vetor constante dão, pelo mesmo ResumoTela do cérebro */
  const stDe = (x: number): string => {
    const r = new ResumoTela("tela");
    let v: string | null = null;
    for (let k = 0; k < 10; k++) v = r.amostra(vetorDoSentido(sentido(x))) ?? v;
    if (v === null) throw new Error("o resumo não fechou");
    return v;
  };

  test("o \"st\" só leva os números do canal atual, no formato de sempre; a troca não para a sessão; a fonte encerrada sai; o replay confere", async () => {
    const pet = ligarProduto(new Motor(101, 35));
    for (let h = 1; h <= 2; h++) { pet.avancar(60); if (h % 2 === 0) pet.observar("alimentar"); }
    iniciarJogo({ getItem: (k: string) => (k === CHAVE ? textoSave(pet) : null), setItem() { /* nada */ } } as unknown as Storage);
    usarPet(jogoAtual().motor.semente);
    const a = falsa(0.6), b = falsa(0.2);
    await abrir(a);
    expect(sessaoTv().origem).toBe("tela"); expect(sessaoTv().canal).toEqual({ n: 1, de: 1, tipo: "tela" });
    await abrir(b);                                                    // "+ Canal": entra e vira o atual, sem desligar
    expect(sessaoTv().canal).toEqual({ n: 2, de: 2, tipo: "tela" }); expect(TV.ligada).toBe(true);
    vi.advanceTimersByTime(10 * PERIODO_MS);
    proximoCanal();                                                    // "Canal ▸": volta ao a
    expect(sessaoTv().origem).toBe("tela"); expect(sessaoTv().canal).toEqual({ n: 1, de: 2, tipo: "tela" });
    vi.advanceTimersByTime(10 * PERIODO_MS);
    expect([a.lidas, b.lidas]).toEqual([10, 10]);
    const m = jogoAtual().motor, st = () => m.log.filter(e => e[1] === "st").map(e => e[2]);
    expect(st()).toEqual([stDe(0.2), stDe(0.6)]);                      // o b e depois o a; nada desligado entre os dois
    expect(st().every(v => /^tela(\|([0-9]|1[0-5])){7}$/.test(v as string))).toBe(true);
    /* o a encerrado por fora: sai, o b fica, e a sessão segue */
    fins.get(a)!("o compartilhamento da tela acabou");
    expect(sessaoTv().origem).toBe("tela"); expect(sessaoTv().canal).toEqual({ n: 1, de: 1, tipo: "tela" }); expect(a.parada).toBe(true);
    vi.advanceTimersByTime(10 * PERIODO_MS);
    expect(st()).toEqual([stDe(0.2), stDe(0.6), stDe(0.2)]);
    /* o último encerrado: a TV desliga com o motivo, e o cérebro grava a TV desligada uma vez */
    fins.get(b)!("o compartilhamento da tela acabou");
    expect(sessaoTv().origem).toBeNull(); expect(sessaoTv().canal).toBeNull(); expect(sessaoTv().erro).toBe("o compartilhamento da tela acabou");
    expect(TV.ligada).toBe(false);
    expect(st()).toEqual([stDe(0.2), stDe(0.6), stDe(0.2), valorSentidoTelaDesligada("tela")]);
    vi.advanceTimersByTime(10 * PERIODO_MS);
    expect(st().length).toBe(4);
    expect(Motor.reproduzir(101, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], 35).assinatura()).toBe(m.assinatura());
  });

  test("o canal novo cancelado no seletor não desliga a captura; o Canal ▸ só aparece com mais de um canal", async () => {
    usarPet(4242);
    await abrir(falsa(0.5));
    await ligarCanal(async () => { throw new DOMException("cancelou", "NotAllowedError"); });
    expect(sessaoTv().origem).toBe("tela"); expect(sessaoTv().erro).toBeNull(); expect(sessaoTv().canal).toEqual({ n: 1, de: 1, tipo: "tela" });
    const um = renderToStaticMarkup(h(PainelTv, { nome: "Agumon", movel: false }));
    expect(um).toContain("Passando: a sua tela"); expect(um).not.toContain("data-tv-canal");
    await abrir(falsa(0.7, "video"));
    expect(sessaoTv().canal).toEqual({ n: 2, de: 2, tipo: "video" });
    const dois = renderToStaticMarkup(h(PainelTv, { nome: "Agumon", movel: false }));
    expect(dois).toContain("data-tv-canal"); expect(dois).toContain("Canal ▸"); expect(dois).toContain("Passando: um vídeo seu, canal 2 de 2");
    const folha = renderToStaticMarkup(h(PainelTv, { nome: "Agumon", movel: true }));
    expect(folha).toContain("data-tv-canal");
    vi.advanceTimersByTime(3 * PERIODO_MS);
    expect(sessaoTv().sentido!.visao.cor).toBe(0.7);
    proximoCanal();
    vi.advanceTimersByTime(PERIODO_MS);
    expect(sessaoTv().sentido!.visao.cor).toBe(0.5);
    pararTv();
    expect(() => proximoCanal()).toThrow(/sem a tela do dono/);
  });
});
