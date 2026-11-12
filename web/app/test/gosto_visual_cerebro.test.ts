/* GOSTO_VISUAL: a captura ligada ao cerebro no jogo (a v32; docs/registro/2026-11.md, D-GV-CEREBRO-1 a 10). Confere, no motor do jogo:
     - o G2: sem nenhum "st" no registro, a vida da v32 e a da v27, byte a byte no que a vida e (as decisoes, o estado do pet, o corpo fora dos
       quimicos da tela, a posicao), com o mesmo registro; e os pets de antes (a v27 e o grupo v28) nao ganham a TV;
     - o replay: uma vida com o "st" gravado (o ResumoTela sobre amostras sinteticas, as duas fontes, o pet levado ate a TV) refaz a mesma
       assinatura pelo registro, e o save em texto reabre igual;
     - o olhar no motivo: o modular escolhe a unidade de olhar, o pet olha a TV (o assistir no corpo e o agrado pela subchave), e a leitura do
       painel mostra "olhar";
     - o save antigo: um pet v27 gravado abre igual (a mesma assinatura) e recusa o "st";
     - ler a tela nao muda o pet (D-GV-CEREBRO-7), o cerebro A com a TV (a regra provisoria da P1c) e a ligacao do P0 (cerebroTv.ts) no jogo:
       o vetor de cada segundo vira o "st" so na mudanca, e parar grava a tela preta. */
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import {
  CELULA_PERTO_DA_TV_JOGO, CONFIG_TV_JOGO, GrupoDoJogo, Motor, ResumoTela, VERSAO_GRUPO, VERSAO_PET, centroDaCelula, valorSentidoTela,
  type EventoRegistro, type MotorCorpoMundo,
} from "../motor/index.ts";
import { CMU_GRANDE } from "../motor/constantes.ts";
import { leituraLab } from "../motor/digibrain/leitura.ts";
import { ligarProduto } from "../src/produto.ts";
import { CHAVE, lerSave, textoSave } from "../src/save.ts";
import { iniciarJogo, jogoAtual } from "../src/jogo.ts";
import { comecarNoCerebro, leituraDoCerebro, pararNoCerebro, sentirNoCerebro } from "../src/gostoVisual/cerebroTv.ts";

type Dict = Record<string, any>;
const laco = (m: Motor): MotorCorpoMundo => m.v11!.laco as MotorCorpoMundo;
/** o ovo novo do jogo, numa versao: as chaves do produto, o cerebro do ovo (o modular) e a ponte da luta */
const ovo = (semente: number, versao: number): Motor => ligarProduto(new Motor(semente, versao));
/** o dono de um pet so: a racao a cada 3 h, o carinho a cada 5 h e a limpeza a cada 8 h, acordado (sem rng) */
function cuidar(m: Motor, horas: number, cada?: (m: Motor, h: number) => void): void {
  for (let h = 1; h <= horas; h++) {
    m.avancar(60);
    if (h % 3 === 0) m.observar("alimentar");
    if (h % 5 === 0 && !m.e.dormindo) m.observar("acariciar");
    if (h % 8 === 0) m.observar("limpar");
    cada?.(m, h);
  }
}
/** o pet perto da TV (o gesto de levar o pet, v19), com ele acordado */
function levarATv(m: Motor): void {
  if (m.e.dormindo) return;
  const [x, y] = centroDaCelula(CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE);
  m.levarPet(x, y);
}
/** amostras sinteticas de um "programa" por hora (sete numeros em [0, 1]), sem rng: o programa h muda o perfil */
const amostra = (h: number, s: number): number[] => [0, 1, 2, 3, 4, 5, 6].map(k => ((h * 7 + k * 3 + (s % 5)) % 11) / 10);

describe("a v32: a TV no cerebro", () => {
  test("os ovos novos de um pet so nascem v32; o grupo segue v29, sem a TV", () => {
    expect(VERSAO_PET).toBe(32);
    expect(new Motor(1).temTv).toBe(true);
    expect(new Motor(1, 27).temTv).toBe(false);
    expect(laco(new Motor(1, 27)).tv).toBeNull();
    const g = new GrupoDoJogo(101, VERSAO_GRUPO);
    for (const i of g.ids) { expect(g.motor(i).temTv).toBe(false); expect(laco(g.motor(i)).tv).toBeNull(); }
    const t = laco(new Motor(1)).tv!;
    expect(t.cfg).toEqual(CONFIG_TV_JOGO);
    expect(t.cfg.fonte).toBe("evento");
    expect(t.em(0)).toBeNull();                                    // sem nenhum "st", a TV esta desligada
  });

  test("G2: sem nenhum \"st\", a vida da v32 e a da v27 (as decisoes, o estado, o corpo fora da tela e a posicao), sementes 101 e 202, 2 dias", () => {
    for (const s of [101, 202]) {
      const a = ovo(s, 27), b = ovo(s, 32);
      cuidar(a, 48); cuidar(b, 48);
      expect(b.log).toEqual(a.log);
      expect(b.lab!.motivos.map(x => x["escolha"])).toEqual(a.lab!.motivos.map(x => x["escolha"]));
      expect(b.lab!.motivos.map(x => x["u"])).toEqual(a.lab!.motivos.map(x => x["u"]));
      expect(b.e).toEqual(a.e);
      expect(b.historico).toEqual(a.historico);
      expect(laco(b).mundo.pet).toEqual(laco(a).mundo.pet);
      const semTela = (q: Record<string, number>) => Object.fromEntries(Object.entries(q).filter(([k]) => !k.startsWith("adaptacao_tela")));
      expect(semTela(laco(b).corpo.q)).toEqual(semTela(laco(a).corpo.q));
      expect(b.lab!.motivos.every(x => x["olhar"]["olha"] === null && x["olhar"]["telas"].length === 0)).toBe(true);
      expect(a.lab!.motivos.every(x => !("olhar" in x))).toBe(true);
    }
  });

  test("o \"st\" so na v32; mal formado ou fora da forma do ResumoTela falha alto antes do registro", () => {
    const v27 = ovo(101, 27);
    expect(() => v27.sentidoTela("tela|1|1|1|1|1|1|1")).toThrow(/v32/);
    expect(v27.log.some(e => e[1] === "st")).toBe(false);
    const m = ovo(101, 32), n = m.log.length;
    expect(() => m.sentidoTela("tela|1|1|1|1|1|1")).toThrow(/malformado/);
    expect(() => m.sentidoTela("tela|16|1|1|1|1|1|1")).toThrow(/fora de 0 a 15/);
    expect(() => m.sentidoTela("radio|1|1|1|1|1|1|1")).toThrow(/malformado/);
    expect(() => m.sentidoTela("tela|01|1|1|1|1|1|1")).toThrow(/malformado/);
    expect(m.log.length).toBe(n);
    m.sentidoTela("tv|3|4|5|6|7|8|9");
    expect(m.log[m.log.length - 1]).toEqual([m.e.tick, "st", "tv|3|4|5|6|7|8|9"]);
    expect(m.ultimoSentidoTela).toBe("tv|3|4|5|6|7|8|9");
    expect(laco(m).tv!.em(laco(m).mundo.tm(m.e.tick))).not.toBeNull();
  });
});

/** uma vida de jogo com a TV: o pet levado ate a TV a cada 2 h, e o P0 mandando um vetor por "segundo" (12 por hora de jogo, um evento a cada
    10 amostras so na mudanca), a fonte trocando no meio da vida */
function vidaComTv(s: number, horas: number): { m: Motor; eventos: number } {
  const m = ovo(s, 32);
  let r = new ResumoTela("tela"), eventos = 0;
  cuidar(m, horas, (mm, h) => {
    if (h === Math.floor(horas / 2)) r = new ResumoTela("tv");
    if (h % 2 === 0) levarATv(mm);
    for (let k = 0; k < 20; k++) {
      const v = r.amostra(amostra(Math.floor(h / 3), s + k));
      if (v !== null) { mm.sentidoTela(v); eventos++; }
    }
  });
  return { m, eventos };
}

describe("o replay e o olhar com o \"st\" gravado", () => {
  const vidas = [101, 202, 303].map(s => ({ s, ...vidaComTv(s, 36) }));

  test("as vidas gravam o \"st\" e o replay pelo registro da a mesma assinatura; o save em texto reabre igual", () => {
    for (const { s, m, eventos } of vidas) {
      expect(eventos).toBeGreaterThan(5);
      expect(m.log.filter(e => e[1] === "st").length).toBe(eventos);
      expect(m.log.filter(e => e[1] === "st").every(e => /^(tela|tv)(\|([0-9]|1[0-5])){7}$/.test(e[2] as string))).toBe(true);
      const r = Motor.reproduzir(s, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], m.versao);
      expect(r.assinatura()).toBe(m.assinatura());
      const mapa = new Map<string, string>(), arm = { getItem: (k: string) => mapa.get(k) ?? null, setItem: (k: string, v: string) => { mapa.set(k, v); } };
      arm.setItem("digilab-web-v21-sprites", textoSave(m));
      const l = lerSave(arm);
      if (l.tipo !== "ok") throw new Error("o save nao abriu");
      expect(l.motor.assinatura()).toBe(m.assinatura());
    }
  });

  test("o modular escolhe olhar a TV: o OCIOSO do olhar, o assistir e o agrado no corpo; a leitura do painel diz \"olhar\"", () => {
    let olhares = 0;
    for (const { m } of vidas) {
      const mot = m.lab!.motivos as Dict[];
      const olhou = mot.filter(x => x["olhar"]["olha"] !== null);
      for (const x of olhou) { expect(x["escolha"][0]).toBe("olhar"); expect(x["acao"]).toBe("ocioso"); expect(x["escolha"][2]).toBe(1); }
      olhares += olhou.length;
      expect(mot.some(x => x["olhar"]["agrado"] !== null)).toBe(true);           // o termo gosto: o pet ja olhava e leu o nivel
    }
    expect(olhares).toBeGreaterThan(0);
    /* o painel: a leitura do modular sobre um motivo de olhar (o mesmo cerebro, com aquele motivo como o ultimo) */
    const { m } = vidas.find(v => (v.m.lab!.motivos as Dict[]).some(x => x["olhar"]["olha"] !== null))!;
    const mo = (m.lab!.motivos as Dict[]).find(x => x["olhar"]["olha"] !== null)!;
    const l = leituraLab(Object.create(m.lab!, { ultimoMotivo: { value: mo } }))!;
    expect(l.escolha[0]).toBe("olhar");
    expect(l.chances.find(c => c.escolhida)!.acao).toBe("olhar");
  });
});

describe("o save antigo", () => {
  test("um pet v27 gravado abre igual, com a mesma assinatura, e segue sem a TV", () => {
    const a = ovo(404, 27);
    cuidar(a, 30);
    const mapa = new Map<string, string>(), arm = { getItem: (k: string) => mapa.get(k) ?? null, setItem: (k: string, v: string) => { mapa.set(k, v); } };
    arm.setItem("digilab-web-v21-sprites", textoSave(a));
    const l = lerSave(arm);
    if (l.tipo !== "ok") throw new Error("o save v27 nao abriu");
    expect(l.motor.versao).toBe(27);
    expect(l.motor.assinatura()).toBe(a.assinatura());
    expect(l.motor.temTv).toBe(false);
    expect(l.motor.tvNoCerebro()).toBeNull();
    expect(() => l.motor.aplicarEvento([l.motor.e.tick, "st", valorSentidoTela("tela", [1, 1, 1, 1, 1, 1, 1])])).toThrow(/v32/);
  });
});

describe("ler a tela nao muda o pet (D-GV-CEREBRO-7)", () => {
  test("com a TV ligada e um \"st\" de volume alto no mesmo tick, a leitura (observacao, DigiBrain, TV no cerebro) nao muda a assinatura nem o replay", () => {
    const m = ovo(505, 32);
    cuidar(m, 10, (mm, h) => { if (h % 2 === 0) levarATv(mm); mm.sentidoTela(valorSentidoTela("tv", h % 2 ? [3, 3, 3, 3, 2, 2, 2] : [12, 12, 12, 12, 15, 15, 15])); });
    m.sentidoTela(valorSentidoTela("tv", [1, 1, 1, 1, 15, 15, 15]));     // o salto de volume: o susto so no proximo sentir do laco
    const antes = m.assinatura();
    m.observacaoAgora(); m.digibrain(); m.leituraLab(); m.tvNoCerebro(); leituraDoCerebro(m); m.desejoAtual(m.observacaoAgora(), m.e.tick);
    expect(m.assinatura()).toBe(antes);
    m.avancar(30);
    const r = Motor.reproduzir(505, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], 32);
    expect(r.assinatura()).toBe(m.assinatura());
  });
});

describe("o cerebro A com a TV", () => {
  test("com o A decidindo, o pet olha pela regra provisoria da P1c (parado, acordado e com a TV no raio), sem agrado; o replay confere", () => {
    const m = ovo(303, 32);
    m.trocarCerebro("a");
    let olhou = 0;
    cuidar(m, 24, (mm, h) => { levarATv(mm); mm.sentidoTela(valorSentidoTela("tela", [h % 16, 8, 8, 8, 4, 4, 4])); if (mm.tvNoCerebro()!.olhando) olhou++; });
    expect(m.cerebroAtual).toBe("a");
    expect(laco(m).novidadesTela.length + olhou).toBeGreaterThan(0);
    const r = Motor.reproduzir(303, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], 32);
    expect(r.assinatura()).toBe(m.assinatura());
  });
});

describe("a ligacao do P0 ao cerebro no jogo (cerebroTv.ts)", () => {
  const dados: Record<string, string> = {};
  beforeEach(() => {
    for (const k of Object.keys(dados)) delete dados[k];
    vi.stubGlobal("localStorage", { getItem: (k: string) => (k in dados ? dados[k]! : null), setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; } });
  });
  afterEach(() => { vi.unstubAllGlobals(); });
  const armaz = (d: Record<string, string>) => ({ d, getItem: (k: string) => (k in d ? d[k]! : null), setItem(k: string, v: string) { d[k] = v; } });
  const sentido = (x: number) => ({ visao: { cor: x, brilho: x, movimento: x / 2, complexidade: x }, som: { volume: x / 3, variacao: x, timbre: x } });

  test("um vetor por segundo: o \"st\" so a cada 10, so na mudanca, com a fonte da origem; parar grava a tela preta uma vez; o replay confere", () => {
    const pet = ovo(101, 32); cuidar(pet, 2);
    const a = armaz({ [CHAVE]: textoSave(pet) });
    iniciarJogo(a);
    comecarNoCerebro("jogo");
    for (let k = 0; k < 10; k++) sentirNoCerebro(sentido(0.6));
    for (let k = 0; k < 10; k++) sentirNoCerebro(sentido(0.6));            // os mesmos niveis: nenhum evento
    for (let k = 0; k < 10; k++) sentirNoCerebro(sentido(0.2));
    for (let k = 0; k < 4; k++) sentirNoCerebro(sentido(0.9));             // a janela incompleta: descartada
    pararNoCerebro();
    pararNoCerebro();
    const m = jogoAtual().motor, st = m.log.filter(e => e[1] === "st").map(e => e[2]);
    expect(st.length).toBe(3); expect(st[0]).toBe("tv|9|9|4|9|3|9|9"); expect(st[2]).toBe("tv|0|0|0|0|0|0|0"); expect(["tv|3|3|1|3|1|3|3", "tv|3|3|2|3|1|3|3"]).toContain(st[1]);
    sentirNoCerebro(sentido(0.5));                                         // parada: nada mais entra
    expect(m.log.filter(e => e[1] === "st").length).toBe(3);
    expect(Motor.reproduzir(101, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], 32).assinatura()).toBe(m.assinatura());
  });

  test("num pet sem a TV no cerebro (a v27) nada entra no registro", () => {
    const pet = ovo(202, 27); cuidar(pet, 2);
    iniciarJogo(armaz({ [CHAVE]: textoSave(pet) }));
    const n = jogoAtual().motor.log.length;
    comecarNoCerebro("tela");
    for (let k = 0; k < 30; k++) sentirNoCerebro(sentido(k / 30));
    pararNoCerebro();
    expect(jogoAtual().motor.log.length).toBe(n);
    expect(leituraDoCerebro(jogoAtual().motor)).toBeNull();
  });
});
