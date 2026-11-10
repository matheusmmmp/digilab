/* A ilha com agua ligada no jogo (docs/TAREFA_V3_ILHA_AGUA.md, IA4; decisoes do Matheus de 2026-11-10: "v22" e "Migram por evento"):
     - o ovo novo e v22: a v21 que nasce na ilha com agua, com o controlador do contrato; vive, anda so em terra, e o replay refaz a vida;
     - o pet v21 passa para a mesma ilha pelo evento "mi" do registro, uma vez: o que esta na agua vai para a terra mais perto, nada do
       pet muda alem do mundo, e o replay refaz a vida bit a bit; antes do "mi" a vida do v21 e a de antes;
     - o que nao vale falha alto: a v22 e o pet de teste nao tem o "mi", o v21 nao passa duas vezes, o registro malformado;
     - no app: o save v21 passa ao abrir e e gravado; o pet guardado e o ovo novo tambem chegam a ilha com agua; o pet de teste nao. */
import { describe, expect, test } from "vitest";
import {
  CMU_MVP, CMU_MVP_AGUA, ILHA_DOS_V21, TICK_INICIAL, TPD, VERSAO_PET, VERSAO_PET_LAB, VERSAO_V21, VERSAO_V22, VERSOES_PET, ehCerebroTrocavel, ehLutaPoc,
} from "../motor/constantes.ts";
import { CONFIG_CONTRATO_AGUA, bloqueioEm } from "../motor/contrato.ts";
import { Motor } from "../motor/motor.ts";
import { solidosDaAgua } from "../motor/mundo.ts";
import type { AcaoDono, EventoRegistro } from "../motor/tipos.ts";
import { passarParaIlhaComAgua } from "../src/ilhaAgua.ts";
import { iniciarJogo, jogoAtual, novoPet, trocarMotor } from "../src/jogo.ts";
import { versaoDoOvo, versoesQueAbrem } from "../src/lutaPoc.ts";
import { ligarProduto } from "../src/produto.ts";
import { ehPetDoJogador } from "../src/nivelTela.ts";
import { CHAVE, petExemplo, textoSave, type Armazenamento } from "../src/save.ts";

const SOLIDOS = solidosDaAgua(CMU_MVP_AGUA), R = CONFIG_CONTRATO_AGUA.r_pet;
const emTerra = (m: Motor): boolean => bloqueioEm(m.mundo!.pet[0], m.mundo!.pet[1], R, SOLIDOS) === null;
const copia = (log: readonly EventoRegistro[]) => JSON.parse(JSON.stringify(log)) as EventoRegistro[];
/** o dono do jogo com o mundo (o do cerebro_primario.test.ts), que de vez em quando poe a racao e solta o pet em pontos que sao agua
    na ilha nova; devolve quantas vezes o pet foi visto fora da terra */
function viver(m: Motor, dias: number): number {
  const passos = Math.round(dias * TPD / 30), agua: [number, number][] = [[670, 250], [5, 5], [200, 370], [690, 60]];
  let fora = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e, mu = m.mundo!;
    if (m.naIlhaComAgua && !emTerra(m)) fora++;
    if (e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
    if (p % 7 === 3) m.deixarComida("racao", ...agua[p % agua.length]);
    if (p % 9 === 4 && !e.dormindo) m.levarPet(...agua[(p + 1) % agua.length]);
    if (e.sujeira >= 2) m.observar("limpar");
    if (p % 5 === 0) m.observar("acariciar");
    if (p % 11 === 10) m.observar("tapa" as AcaoDono);
    if (m.naIlhaComAgua) {
      if (!emTerra(m)) fora++;
      for (const c of mu.comidas.values()) if (!mu.seca(c.x, c.y)) fora++;
    }
  }
  return fora;
}

describe("a versao 22: o ovo novo nasce na ilha com agua", () => {
  test("a v22 e a v21 com o mundo da agua e o controlador; a v21 segue abrindo", () => {
    expect([VERSAO_PET, VERSAO_V22, VERSAO_V21]).toEqual([22, 22, 21]);
    expect(VERSOES_PET).toEqual([21, 22]);
    expect([versaoDoOvo(), versoesQueAbrem()]).toEqual([22, [21, 22]]);
    expect([21, 22].map(v => [ehCerebroTrocavel(v), ehLutaPoc(v)])).toEqual([[true, true], [true, true]]);
    expect(ehLutaPoc(VERSAO_PET_LAB)).toBe(false);
    const novo = new Motor(101), velho = new Motor(101, 21);
    expect([novo.versao, novo.naIlhaComAgua, novo.podeMudarIlha]).toEqual([22, true, false]);
    expect([velho.versao, velho.naIlhaComAgua, velho.podeMudarIlha]).toEqual([21, false, true]);
    expect(novo.mundo!.cm).toEqual(CMU_MVP_AGUA);
    expect(novo.mundo!.cct).toEqual(CONFIG_CONTRATO_AGUA);
    expect(velho.mundo!.cm).toEqual(CMU_MVP);
    expect(novo.mundo!.bolaNoGolpe).toBe(true);
    /* a v22 luta como a v21: o motivo de nao lutar agora e o do bebe, nao o da versao */
    expect(String(novo.porqueNaoLutaPoc("x", 0))).not.toMatch(/só os pets v/);
    expect(novo.mundo!.trocaIlha).toBeNull();
  });

  for (const s of [101, 202, 303]) test(`a v22 @${s}: 3 dias com a racao e o pet soltos na agua; nada fica na agua, e o replay refaz a vida`, () => {
    const m = ligarProduto(new Motor(s));
    expect(viver(m, 3)).toBe(0);
    expect(m.mundo!.contratoDecisoes.length).toBeGreaterThan(20);
    for (const d of m.mundo!.contratoDecisoes) for (const [x, y] of d.trajetoria ?? []) if (bloqueioEm(x, y, R, SOLIDOS) !== null) throw new Error(`o pet na agua: (${x}, ${y})`);
    expect(m.mundo!.levadas.some(l => l.para[0] !== l.pedido[0] || l.para[1] !== l.pedido[1])).toBe(true);
    expect(m.log.some(e => e[1] === "mi")).toBe(false);
    const r = Motor.reproduzir(s, copia(m.log), 22);
    expect(r.assinatura()).toBe(m.assinatura());
  });

  test("a v22 e o pet de teste nao tem o evento da troca; o registro malformado falha alto", () => {
    const novo = new Motor(101), lab = new Motor(101, VERSAO_PET_LAB);
    expect(() => novo.mudarIlha()).toThrow(/v21/);
    expect(() => lab.mudarIlha()).toThrow(/v21/);
    expect(() => novo.aplicarEvento([TICK_INICIAL, "mi", { ilha: ILHA_DOS_V21 }])).toThrow(/v21/);
    expect(() => lab.aplicarEvento([TICK_INICIAL, "mi", { ilha: ILHA_DOS_V21 }])).toThrow(/v21/);
    for (const ruim of [{ ilha: "outra_ilha" }, { ilha: "Mvp_agua" }, { ilha: 5 }, { ilha: ILHA_DOS_V21, x: 1 }, {}, null, "mvp_agua"])
      expect(() => new Motor(101, 21).aplicarEvento([TICK_INICIAL, "mi", ruim] as unknown as EventoRegistro), JSON.stringify(ruim)).toThrow();
  });
});

describe("o pet v21 passa para a ilha com agua (o evento mi)", () => {
  for (const s of [101, 202]) test(`a v21 @${s}: so o mundo muda na troca; depois dela nada fica na agua; o replay refaz a vida`, () => {
    const m = ligarProduto(new Motor(s, 21)), gemeo = ligarProduto(new Motor(s, 21));
    viver(m, 1.5); viver(gemeo, 1.5);
    expect(m.assinatura()).toBe(gemeo.assinatura());
    const t = m.e.tick, n = m.log.length, hist = m.historico.length, nDono = m.nDono, e = JSON.stringify(m.e);
    const semMundo = (x: Motor): string => {
      const a = (JSON.parse(x.assinatura()) as unknown[]).slice(0, -1), v11 = a[a.length - 1] as [string, unknown, Record<string, unknown>, number];
      if (v11[0] !== "v11" || !("mundo" in v11[2])) throw new Error("a assinatura mudou de forma");
      delete v11[2].mundo;
      return JSON.stringify(a);
    };
    const antes = semMundo(m);
    m.mudarIlha();
    expect(m.log.slice(n)).toEqual([[t, "mi", { ilha: "mvp_agua" }]]);
    expect([m.versao, m.naIlhaComAgua, m.podeMudarIlha, emTerra(m)]).toEqual([21, true, false, true]);
    expect(semMundo(m)).toBe(antes);
    expect([m.e.tick, m.historico.length, m.nDono, JSON.stringify(m.e)]).toEqual([t, hist, nDono, e]);
    expect(m.mundo!.cm).toEqual(CMU_MVP_AGUA);
    expect(m.mundo!.trocaIlha!.tick).toBe(t);
    for (const c of m.mundo!.comidas.values()) expect(m.mundo!.seca(c.x, c.y)).toBe(true);
    expect(() => m.mudarIlha()).toThrow(/v21/);
    expect(() => m.aplicarEvento([t, "mi", { ilha: "mvp_agua" }])).toThrow();
    /* dali em diante */
    expect(viver(m, 2)).toBe(0);
    expect(m.mundo!.contratoDecisoes.length).toBeGreaterThan(10);
    const r = Motor.reproduzir(s, copia(m.log), 21);
    expect(r.assinatura()).toBe(m.assinatura());
    /* o registro cortado antes do "mi" e a vida de antes, byte a byte */
    expect(Motor.reproduzir(s, copia(m.log.slice(0, n)), 21).assinatura()).toBe(gemeo.assinatura());
  });

  test("a troca vale com o pet dormindo; o pet morto nao passa", () => {
    const m = ligarProduto(new Motor(303, 21));
    for (let i = 0; i < 3000 && !m.e.dormindo; i++) m.avancar(7);
    expect(m.e.dormindo).toBe(true);
    m.mudarIlha();
    expect([m.naIlhaComAgua, m.e.dormindo, emTerra(m)]).toEqual([true, true, true]);
    expect(Motor.reproduzir(303, copia(m.log), 21).assinatura()).toBe(m.assinatura());
    const morto = new Motor(404, 21);
    morto.morte = { tick: morto.e.tick, causa: "lesoes" };
    expect([morto.podeMudarIlha, passarParaIlhaComAgua(morto)]).toEqual([false, false]);
  });
});

describe("no app", () => {
  const armaz = (d: Record<string, string> = {}): Armazenamento & { d: Record<string, string> } =>
    ({ d, getItem: k => (k in d ? d[k]! : null), setItem(k, v) { d[k] = v; } });

  test("o save v21 passa para a ilha com agua ao abrir, e o registro com o evento e gravado na hora; abrir de novo nao repete", () => {
    const antigo = ligarProduto(new Motor(606, 21)); viver(antigo, .5);
    const a = armaz({ [CHAVE]: textoSave(antigo) });
    iniciarJogo(a);
    const m = jogoAtual().motor;
    expect([m.versao, m.naIlhaComAgua, emTerra(m)]).toEqual([21, true, true]);
    const s = JSON.parse(a.d[CHAVE]!) as { versao: number; log: EventoRegistro[] };
    expect(s.versao).toBe(21);
    expect(s.log.slice(0, -1)).toEqual(copia(antigo.log));
    expect(s.log.at(-1)).toEqual([antigo.e.tick, "mi", { ilha: "mvp_agua" }]);
    expect(Motor.reproduzir(606, s.log, 21).assinatura()).toBe(m.assinatura());
    const texto = a.d[CHAVE]!;
    iniciarJogo(a);
    expect(a.d[CHAVE]).toBe(texto);
    expect(jogoAtual().motor.log.filter(e => e[1] === "mi").length).toBe(1);
  });

  test("o pet de exemplo de antes da v22 (v21) segue nao sendo do jogador, antes e depois de passar para a ilha com agua", () => {
    const hoje = petExemplo(), antigo = petExemplo(21);
    expect([hoje.versao, antigo.versao]).toEqual([22, 21]);
    expect([ehPetDoJogador(hoje), ehPetDoJogador(antigo)]).toEqual([false, false]);
    antigo.avancar(90);
    expect(passarParaIlhaComAgua(antigo)).toBe(true);
    antigo.avancar(60);
    expect(ehPetDoJogador(antigo)).toBe(false);                  // o "mi" e do jogo, nao do jogador
    antigo.observar("acariciar");
    expect(ehPetDoJogador(antigo)).toBe(true);                   // um cuidado a mais o faz do jogador, como antes
  });

  test("a bola que rolava para onde esta na troca (o espelho do teste do Python)", () => {
    const m = new Motor(303, 21), w = m.mundo!;
    w.deixarBola(60, 300, 240);
    (w as unknown as { rolarBola(t: number, de: [number, number]): void }).rolarBola(60, [280, 240]);
    const meio = w.bolaEm(62), fim = w.bolaEm(9999);
    expect(meio).not.toEqual(fim);
    expect(meio).not.toEqual([300, 240]);
    const reg = w.mudarIlha(62, "mvp_agua");
    expect(reg.bola).toEqual({ de: meio, para: w.emTerra(...meio) });
    expect(w.bolaEm(9999)).toEqual(w.emTerra(...meio));
  });

  test("o pet v21 que entra pela troca de pet tambem passa; o ovo novo ja nasce v22 na ilha com agua", () => {
    const a = armaz({ [CHAVE]: textoSave(ligarProduto(new Motor(707, 21))) });
    iniciarJogo(a);
    const guardado = ligarProduto(new Motor(808, 21)); viver(guardado, .5);
    expect(guardado.naIlhaComAgua).toBe(false);
    trocarMotor(guardado, "save");
    expect([jogoAtual().motor.semente, jogoAtual().motor.naIlhaComAgua]).toEqual([808, true]);
    expect((JSON.parse(a.d[CHAVE]!) as { log: EventoRegistro[] }).log.at(-1)![1]).toBe("mi");
    novoPet();
    const ovo = jogoAtual().motor;
    expect([ovo.versao, ovo.naIlhaComAgua, ovo.log.some(e => e[1] === "mi")]).toEqual([22, true, false]);
    expect((JSON.parse(a.d[CHAVE]!) as { versao: number }).versao).toBe(22);
  });
});
