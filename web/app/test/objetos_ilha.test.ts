// Os objetos que falam (direcao A da ilha interativa; prancha docs/pranchas/ux-ilha-a/, decisoes I1-1 e I1-4 a I1-9): as contas da tela
// (src/telas/pet/objetosIlha.ts) e o toque na cena (src/componentes/ObjetosDaIlha.tsx, ligarToqueObjetos). Sem DOM (vitest em node): o alvo e um
// EventTarget com o retangulo, e a vista do mundo e uma falsa. So leitura: ler o motor para a tela nao muda a assinatura nem o registro.
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import { CTR, Motor, TPD, VERSAO_PET } from "../motor/index.ts";
import { CENA } from "../src/telas/pet/cenaEstado.ts";
import {
  CHAVE_DIARIO_VISTO, alvoAtual, diarioNovo, esquecerDiarioVisto, lerDiarioVisto, linhaAprendeu, marcarDiarioVisto, racoesNaTigela, seloDoSaco, treinosHoje, ultimaNovidade,
} from "../src/telas/pet/objetosIlha.ts";
import { atualizarPosicoes, estadoToqueObjetos, fecharCartao, ligarToqueObjetos, objetoNoPonto } from "../src/componentes/ObjetosDaIlha.tsx";

/** o pet da prancha (semente 6503, v de hoje): a racao no comedouro pelo Alimentar */
function petComRacao(): Motor {
  const m = new Motor(6503, VERSAO_PET);
  m.avancar(120);
  m.observar("alimentar");
  m.avancar(5);
  return m;
}

describe("as contas da tela", () => {
  test("a racao na tigela conta so as maduras da celula do comedouro", () => {
    const m = petComRacao(), mu = m.mundo!;
    expect(racoesNaTigela(mu, m.e.tick)).toBe(1);
    /* uma racao posta longe da tigela nao conta */
    m.deixarComida("racao", mu.comedouro[0] + 4 * mu.cm.sub, mu.comedouro[1]);
    expect(racoesNaTigela(mu, m.e.tick)).toBe(1);
  });

  test("ler a tela nao muda o pet: a assinatura e o registro ficam iguais", () => {
    const m = petComRacao(), antes = m.assinatura(), log = JSON.stringify(m.log);
    racoesNaTigela(m.mundo!, m.e.tick); alvoAtual(m); seloDoSaco(m); ultimaNovidade(m); m.digibrain();
    expect(m.assinatura()).toBe(antes);
    expect(JSON.stringify(m.log)).toBe(log);
  });

  test("ler a tela a cada tick nao muda a vida: dois pets gemeos, so um lido, saem iguais", () => {
    const a = petComRacao(), b = petComRacao();
    for (let i = 0; i < 600; i++) {
      if (i % 120 === 0) { a.observar("alimentar"); b.observar("alimentar"); }
      a.avancar(1); b.avancar(1);
      racoesNaTigela(b.mundo!, b.e.tick); alvoAtual(b); seloDoSaco(b); ultimaNovidade(b);
      if (i % 60 === 0) b.digibrain();
    }
    expect(b.assinatura()).toBe(a.assinatura());
    expect(JSON.stringify(b.log)).toBe(JSON.stringify(a.log));
  });

  test("o alvo atual: a bola quando brinca, a tigela quando come e ela e a comida mais perto, e nada dormindo", () => {
    const m = petComRacao();
    const viu = new Set<string>();
    for (let i = 0; i < 3000 && viu.size < 3; i++) {
      m.avancar(1);
      const a = alvoAtual(m);
      if (m.e.dormindo) expect(a).toBeNull();
      if (m.acao === "brincar" && !m.e.dormindo) expect(a).toBe("bola");
      if (a === "tigela") expect(m.acao).toBe("comer");
      viu.add(String(a));
      if (i % 120 === 0) m.observar("alimentar");
    }
    expect(viu.has("bola") || viu.has("tigela")).toBe(true);
  });

  test("a linha do que aprendeu: o sinal do desvio da acao do objeto, e 'nada novo' fora das 3 maiores", () => {
    expect(linhaAprendeu([{ acao: "brincar", desvio: -0.11 }], "bola")).toEqual({ texto: "Brinca menos", sinal: -1 });
    expect(linhaAprendeu([{ acao: "comer", desvio: 0.2 }], "tigela")).toEqual({ texto: "Come mais", sinal: 1 });
    expect(linhaAprendeu([{ acao: "ocioso", desvio: 0.3 }], "tigela")).toEqual({ texto: "Nada novo sobre comer", sinal: 0 });
    expect(linhaAprendeu(null, "bola")).toEqual({ texto: "Nada novo sobre brincar", sinal: 0 });
  });

  test("os treinos de hoje contam os 'tr' do dia do jogo de agora", () => {
    const dia = 3 * TPD, log = [[dia - 10, "tr", "corrida"], [dia + 5, "tr", "corrida"], [dia + 400, "tr", "nado"], [dia + 400, "t", 60]];
    expect(treinosHoje(log, dia + 500)).toBe(2);
    expect(treinosHoje(log, dia - 1)).toBe(1);
    expect(treinosHoje([], dia)).toBe(0);
  });

  test("o selo do saco: sem treino, pode treinar; a proxima vez e o ultimo treino mais o intervalo", () => {
    const m = petComRacao();
    expect(seloDoSaco(m)).toEqual({ hoje: 0, proxima: null });
    m.treino.ultimo = m.e.tick - 1;                    /* so a leitura: o TreinoPet de um pet que treinou ha 1 min */
    expect(seloDoSaco(m).proxima).toBe(m.e.tick - 1 + CTR.intervalo);
  });
});

describe("o diario lido (so a tela)", () => {
  const dados: Record<string, string> = {};
  beforeEach(() => {
    esquecerDiarioVisto();
    for (const k of Object.keys(dados)) delete dados[k];
    Object.assign(globalThis, { localStorage: { getItem: (k: string) => (k in dados ? dados[k] : null), setItem: (k: string, v: string) => { dados[k] = v; } } });
  });
  afterEach(() => { delete (globalThis as { localStorage?: unknown }).localStorage; });

  test("a marca e por pet, e o ponto aparece so com novidade depois dela", () => {
    expect(lerDiarioVisto(1)).toBeNull();
    marcarDiarioVisto(1, 900);
    expect(lerDiarioVisto(1)).toBe(900);
    expect(lerDiarioVisto(2)).toBeNull();
    /* outro pet nao apaga a marca do primeiro */
    marcarDiarioVisto(2, 50);
    esquecerDiarioVisto();
    expect(lerDiarioVisto(1)).toBe(900);
    expect(lerDiarioVisto(2)).toBe(50);
    expect(diarioNovo(null, null)).toBe(false);
    expect(diarioNovo(800, null)).toBe(true);
    expect(diarioNovo(800, 900)).toBe(false);
    expect(diarioNovo(901, 900)).toBe(true);
  });

  test("a marca invalida falha alto", () => {
    dados[CHAVE_DIARIO_VISTO] = "{\"6503\":\"x\"}";
    expect(() => lerDiarioVisto(1)).toThrow(/marca do diário inválida/);
  });

  test("a ultima novidade e a ultima evolucao ou linha de regras", () => {
    const m = petComRacao();
    expect(ultimaNovidade(m)).toBe(m.evolucoes.length ? Math.max(...m.evolucoes.map(e => e.tick)) : null);
  });
});

describe("o toque nos objetos", () => {
  const lugares = { saco: [300, 300, 100], portao: [900, 200, 120], barraca: [100, 200, 120] } as const;
  const alvo = () => Object.assign(new EventTarget(), { getBoundingClientRect: () => ({ left: 0, top: 0 }) });
  const ev = (tipo: string, x: number, y: number, extra: Record<string, unknown> = {}) =>
    Object.assign(new Event(tipo), { pointerId: 1, clientX: x, clientY: y, button: 0, buttons: 0, pointerType: "mouse", ...extra });
  let desligar: (() => void) | null = null;
  beforeEach(() => {
    CENA.ret = { x: 600, y: 500, w: 40, h: 60 };
    CENA.mundo = { paraMundo: () => null, paraTela: () => [0, 0], pet: [0, 0], lugarEm: () => null };
    CENA.coberto = false; CENA.bolaNaMao = false; CENA.petNaMao = false;
    /* a tigela com o pe em (500, 400) e a bola em (700, 400); 100 px por celula */
    atualizarPosicoes(lugares, 100, [500, 400], [700, 400], 1920, 950);
  });
  afterEach(() => { desligar?.(); desligar = null; fecharCartao(); CENA.mundo = null; CENA.ret = null; });

  test("o objeto sob o ponto: a tigela, a bola e o saco; o sprite do pet e do pet; com um painel por cima, nada", () => {
    const el = alvo();
    expect(objetoNoPonto(el, 500, 390)).toBe("tigela");
    expect(objetoNoPonto(el, 700, 370)).toBe("bola");
    expect(objetoNoPonto(el, 300, 260)).toBe("saco");
    expect(objetoNoPonto(el, 300, 205)).toBeNull();                 /* acima do topo do saco (0,8 da altura) */
    expect(objetoNoPonto(el, 620, 530)).toBeNull();
    expect(objetoNoPonto(el, 1200, 800)).toBeNull();
    CENA.coberto = true;
    expect(objetoNoPonto(el, 500, 390)).toBeNull();
  });

  test("tocar na tigela abre o cartao, tocar de novo fecha, e um arrasto nao conta", () => {
    const el = alvo();
    desligar = ligarToqueObjetos(el);
    el.dispatchEvent(ev("pointerdown", 500, 390)); el.dispatchEvent(ev("pointerup", 500, 390));
    expect(estadoToqueObjetos().aberto).toBe("tigela");
    el.dispatchEvent(ev("pointerdown", 500, 390)); el.dispatchEvent(ev("pointerup", 500, 390));
    expect(estadoToqueObjetos().aberto).toBeNull();
    el.dispatchEvent(ev("pointerdown", 700, 370)); el.dispatchEvent(ev("pointermove", 760, 370, { buttons: 1 })); el.dispatchEvent(ev("pointerup", 760, 370));
    expect(estadoToqueObjetos().aberto).toBeNull();
  });

  test("tocar na bola abre o cartao dela; tocar fora fecha; no saco o toque e do ToqueLugar (nao abre cartao)", () => {
    const el = alvo();
    desligar = ligarToqueObjetos(el);
    el.dispatchEvent(ev("pointerdown", 700, 370)); el.dispatchEvent(ev("pointerup", 700, 370));
    expect(estadoToqueObjetos().aberto).toBe("bola");
    el.dispatchEvent(ev("pointerdown", 1200, 800)); el.dispatchEvent(ev("pointerup", 1200, 800));
    expect(estadoToqueObjetos().aberto).toBeNull();
    el.dispatchEvent(ev("pointerdown", 300, 260)); el.dispatchEvent(ev("pointerup", 300, 260));
    expect(estadoToqueObjetos().aberto).toBeNull();
  });

  test("o mouse parado sobre um objeto o marca (a etiqueta do hover); sair da cena desmarca", () => {
    const el = alvo();
    desligar = ligarToqueObjetos(el);
    el.dispatchEvent(ev("pointermove", 500, 390));
    expect(estadoToqueObjetos().sobre).toBe("tigela");
    el.dispatchEvent(ev("pointermove", 300, 260));
    expect(estadoToqueObjetos().sobre).toBe("saco");
    el.dispatchEvent(ev("pointerleave", 0, 0));
    expect(estadoToqueObjetos().sobre).toBeNull();
  });

  test("com o pet na mao, o toque nao abre cartao", () => {
    const el = alvo();
    desligar = ligarToqueObjetos(el);
    CENA.petNaMao = true;
    el.dispatchEvent(ev("pointerdown", 500, 390)); el.dispatchEvent(ev("pointerup", 500, 390));
    expect(estadoToqueObjetos().aberto).toBeNull();
  });
});
