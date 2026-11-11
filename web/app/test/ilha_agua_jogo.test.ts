/* As ilhas do jogo (docs/TAREFA_V3_ILHA_AGUA.md): a IA4 (a v22 e o "mi" para a ilha com agua; decisoes do Matheus de 2026-11-10) e a IG4
   (a v23 e o "mi" para a ilha grande; decisoes de 2026-11-11: "Mundo maior no motor", "128 x 60", "tudo na v23", e a IG-7, "deslocados
   junto com o lar").
     - o ovo novo e v23: a v22 que nasce na ilha grande (128 x 60), com as arvores e os marcos em que o pet nao pisa; vive, anda so em
       celula livre, e o replay refaz a vida; a v22 (a ilha com agua de 64 x 30) e a v21 seguem abrindo;
     - os pets v21 e v22 vivos passam para a ilha grande pelo evento "mi" do registro, uma vez: tudo anda o deslocamento do lar, o que
       cai em celula fechada vai para a terra, nada do pet muda alem do mundo, e o replay refaz a vida; antes do "mi" a vida e a de antes;
     - o registro gravado entre a IA4 e a IG4 (o v21 com o "mi" para a ilha com agua) continua abrindo, e esse pet tambem passa;
     - o que nao vale falha alto: o pet de teste, o morto, a segunda ida, o registro malformado;
     - no app: o save passa ao abrir e e gravado; o pet guardado e o ovo novo tambem chegam a ilha grande. */
import { describe, expect, test } from "vitest";
import {
  CMU_GRANDE, CMU_MVP, CMU_MVP_AGUA, ILHA_DOS_V21, ILHA_DOS_VIVOS, TICK_INICIAL, TPD, VERSAO_PET, VERSAO_PET_LAB, VERSAO_V21, VERSAO_V22, VERSAO_V23, VERSOES_PET,
  ehCerebroTrocavel, ehLutaPoc,
} from "../motor/constantes.ts";
import { CONFIG_CONTRATO_AGUA, bloqueioEm } from "../motor/contrato.ts";
import { Motor } from "../motor/motor.ts";
import { solidosDaAgua, tamanhoDoMapa } from "../motor/mundo.ts";
import type { AcaoDono, EventoRegistro } from "../motor/tipos.ts";
import { passarParaIlhaComAgua } from "../src/ilhaAgua.ts";
import { iniciarJogo, jogoAtual, novoPet, trocarMotor } from "../src/jogo.ts";
import { versaoDoOvo, versoesQueAbrem } from "../src/lutaPoc.ts";
import { ligarProduto } from "../src/produto.ts";
import { ehPetDoJogador } from "../src/nivelTela.ts";
import { CHAVE, petExemplo, textoSave, type Armazenamento } from "../src/save.ts";

const R = CONFIG_CONTRATO_AGUA.r_pet, SUB = CMU_GRANDE.sub;
const DX = (CMU_GRANDE.layout.ninho[0] - CMU_MVP.layout.ninho[0]) * SUB, DY = (CMU_GRANDE.layout.ninho[1] - CMU_MVP.layout.ninho[1]) * SUB;
const emTerra = (m: Motor): boolean => bloqueioEm(m.mundo!.pet[0], m.mundo!.pet[1], R, solidosDaAgua(m.mundo!.cm)) === null;
const copia = (log: readonly EventoRegistro[]) => JSON.parse(JSON.stringify(log)) as EventoRegistro[];
/** os pontos fechados de cada ilha em que o dono poe a racao e solta o pet, de proposito: na de 64 x 30, a agua; na grande, o rio, o
    mar, o lago e o carro */
const FECHADOS: Record<string, [number, number][]> = {
  mvp: [[670, 250], [5, 5], [200, 370], [690, 60]], mvp_agua: [[670, 250], [5, 5], [200, 370], [690, 60]],
  grande: [[1352, 408], [5, 5], [432, 656], [31 * SUB + 8, 21 * SUB + 8]],
};
/** o dono do jogo com o mundo (o do cerebro_primario.test.ts), que de vez em quando poe a racao e solta o pet em pontos fechados da
    ilha em que o pet esta; devolve quantas vezes o pet ou uma comida foi visto em celula fechada */
function viver(m: Motor, dias: number): number {
  const passos = Math.round(dias * TPD / 30);
  let fora = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e, mu = m.mundo!, pontos = FECHADOS[mu.cm.layout.nome], [largura] = tamanhoDoMapa(mu.cm);
    if (m.naIlhaComAgua && !emTerra(m)) fora++;
    if (e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(largura - 1, mu.pet[0] + 24)), mu.pet[1]);
    if (p % 7 === 3) m.deixarComida("racao", ...pontos[p % pontos.length]);
    if (p % 9 === 4 && !e.dormindo) m.levarPet(...pontos[(p + 1) % pontos.length]);
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
/** a assinatura sem o mundo: o que nao pode mudar numa troca de ilha */
function semMundo(x: Motor): string {
  const a = (JSON.parse(x.assinatura()) as unknown[]).slice(0, -1), v11 = a[a.length - 1] as [string, unknown, Record<string, unknown>, number];
  if (v11[0] !== "v11" || !("mundo" in v11[2])) throw new Error("a assinatura mudou de forma");
  delete v11[2].mundo;
  return JSON.stringify(a);
}
const semTrajetoriaFechada = (m: Motor): void => {
  const s = solidosDaAgua(m.mundo!.cm);
  for (const d of m.mundo!.contratoDecisoes) for (const [x, y] of d.trajetoria ?? []) if (bloqueioEm(x, y, R, s) !== null) throw new Error(`o pet em celula fechada: (${x}, ${y})`);
};

describe("as versoes: o ovo novo nasce na ilha grande", () => {
  test("a v23 e a v22 com o mundo grande; a v22 e a v21 seguem abrindo", () => {
    expect([VERSAO_PET, VERSAO_V23, VERSAO_V22, VERSAO_V21]).toEqual([23, 23, 22, 21]);
    expect(VERSOES_PET).toEqual([21, 22, 23]);
    expect([versaoDoOvo(), versoesQueAbrem()]).toEqual([23, [21, 22, 23]]);
    expect([21, 22, 23].map(v => [ehCerebroTrocavel(v), ehLutaPoc(v)])).toEqual([[true, true], [true, true], [true, true]]);
    expect(ehLutaPoc(VERSAO_PET_LAB)).toBe(false);
    const novo = new Motor(101), meio = new Motor(101, 22), velho = new Motor(101, 21);
    expect([novo.versao, novo.naIlhaComAgua, novo.naIlhaGrande, novo.podeMudarIlha]).toEqual([23, true, true, false]);
    expect([meio.versao, meio.naIlhaComAgua, meio.naIlhaGrande, meio.podeMudarIlha]).toEqual([22, true, false, true]);
    expect([velho.versao, velho.naIlhaComAgua, velho.naIlhaGrande, velho.podeMudarIlha]).toEqual([21, false, false, true]);
    expect(novo.mundo!.cm).toEqual(CMU_GRANDE);
    expect(meio.mundo!.cm).toEqual(CMU_MVP_AGUA);
    expect(velho.mundo!.cm).toEqual(CMU_MVP);
    expect([novo.mundo!.cct, meio.mundo!.cct]).toEqual([CONFIG_CONTRATO_AGUA, CONFIG_CONTRATO_AGUA]);
    expect(novo.mundo!.pet).toEqual([CMU_GRANDE.layout.ninho[0] * SUB + SUB / 2, CMU_GRANDE.layout.ninho[1] * SUB + SUB / 2]);
    expect(novo.mundo!.bolaNoGolpe).toBe(true);
    /* a v23 luta como a v21: o motivo de nao lutar agora e o do bebe, nao o da versao */
    expect(String(novo.porqueNaoLutaPoc("x", 0))).not.toMatch(/só os pets v/);
    expect([novo.mundo!.trocaIlha, novo.mundo!.trocaMaior]).toEqual([null, null]);
  });

  for (const [v, s] of [[23, 101], [23, 202], [23, 303], [22, 101]] as const)
    test(`a v${v} @${s}: 3 dias com a racao e o pet soltos em pontos fechados; nada fica neles, e o replay refaz a vida`, () => {
      const m = ligarProduto(new Motor(s, v));
      expect(viver(m, 3)).toBe(0);
      expect(m.mundo!.contratoDecisoes.length).toBeGreaterThan(20);
      semTrajetoriaFechada(m);
      expect(m.mundo!.levadas.some(l => l.para[0] !== l.pedido[0] || l.para[1] !== l.pedido[1])).toBe(true);
      expect(m.log.some(e => e[1] === "mi")).toBe(false);
      expect(Motor.reproduzir(s, copia(m.log), v).assinatura()).toBe(m.assinatura());
    });

  test("a racao e a bola valem ate o tamanho do mapa de cada pet, e falham alto antes do registro fora dele", () => {
    const novo = new Motor(101), velho = new Motor(101, 21);
    novo.avancar(5); velho.avancar(5);
    novo.deixarComida("racao", 1800, 700);
    novo.deixarBola(1800, 700);
    expect(novo.log.slice(-2).map(e => e[1])).toEqual(["dc", "db"]);
    const n = [novo.log.length, velho.log.length];
    expect(() => novo.deixarComida("racao", 2048, 10)).toThrow(/fora do mapa/);
    expect(() => novo.deixarBola(10, 960)).toThrow(/fora do mapa/);
    expect(() => velho.deixarComida("racao", 1800, 700)).toThrow(/fora do mapa/);
    expect(() => velho.deixarBola(1800, 700)).toThrow(/fora do mapa/);
    expect([novo.log.length, velho.log.length]).toEqual(n);
    expect(Motor.reproduzir(101, copia(novo.log), 23).assinatura()).toBe(novo.assinatura());
    /* o mesmo registro num pet do mapa de 64 x 30 falha alto no replay */
    expect(() => Motor.reproduzir(101, copia(novo.log), 21)).toThrow(/fora do mapa/);
  });

  test("a v23 e o pet de teste nao passam de ilha; o registro malformado falha alto", () => {
    const novo = new Motor(101), lab = new Motor(101, VERSAO_PET_LAB), meio = new Motor(101, 22);
    expect(() => novo.mudarIlha()).toThrow(/ilha grande/);
    expect(() => lab.mudarIlha()).toThrow(/ilha grande/);
    for (const ilha of [ILHA_DOS_V21, ILHA_DOS_VIVOS]) {
      expect(() => novo.aplicarEvento([TICK_INICIAL, "mi", { ilha }])).toThrow();
      expect(() => lab.aplicarEvento([TICK_INICIAL, "mi", { ilha }])).toThrow();
    }
    /* a v22 nasceu na agua: nao tem o "mi" para a ilha com agua, so para a grande */
    expect(() => meio.aplicarEvento([TICK_INICIAL, "mi", { ilha: ILHA_DOS_V21 }])).toThrow(/v22/);
    for (const ruim of [{ ilha: "outra_ilha" }, { ilha: "Mvp_agua" }, { ilha: 5 }, { ilha: ILHA_DOS_VIVOS, x: 1 }, {}, null, "grande"])
      expect(() => new Motor(101, 21).aplicarEvento([TICK_INICIAL, "mi", ruim] as unknown as EventoRegistro), JSON.stringify(ruim)).toThrow();
  });
});

describe("os pets vivos passam para a ilha grande (o evento mi)", () => {
  for (const [v, s] of [[21, 101], [21, 202], [22, 101], [22, 202]] as const)
    test(`a v${v} @${s}: so o mundo muda na ida, tudo anda com o lar; depois nada fica em celula fechada; o replay refaz a vida`, () => {
      const m = ligarProduto(new Motor(s, v)), gemeo = ligarProduto(new Motor(s, v));
      viver(m, 1.5); viver(gemeo, 1.5);
      expect(m.assinatura()).toBe(gemeo.assinatura());
      const t = m.e.tick, n = m.log.length, hist = m.historico.length, nDono = m.nDono, e = JSON.stringify(m.e);
      const antes = semMundo(m), pet = [...m.mundo!.pet], comidas = [...m.mundo!.comidas.values()].map(c => [c.id, c.x, c.y]);
      m.mudarIlha();
      expect(m.log.slice(n)).toEqual([[t, "mi", { ilha: "grande" }]]);
      expect([m.versao, m.naIlhaComAgua, m.naIlhaGrande, m.podeMudarIlha, emTerra(m)]).toEqual([v, true, true, false, true]);
      expect(semMundo(m)).toBe(antes);
      expect([m.e.tick, m.historico.length, m.nDono, JSON.stringify(m.e)]).toEqual([t, hist, nDono, e]);
      expect(m.mundo!.cm).toEqual(CMU_GRANDE);
      const reg = m.mundo!.trocaMaior!;
      expect([reg.tick, reg.de, reg.para, reg.deslocamento]).toEqual([t, v === 21 ? "mvp" : "mvp_agua", "grande", [DX, DY]]);
      expect(reg.pet.de).toEqual(pet);
      expect(Math.abs(m.mundo!.pet[0] - pet[0] - DX) <= 2 * SUB && Math.abs(m.mundo!.pet[1] - pet[1] - DY) <= 2 * SUB).toBe(true);
      expect(reg.comidas.map(c => [c.id, ...c.de])).toEqual(comidas);
      for (const c of m.mundo!.comidas.values()) expect(m.mundo!.seca(c.x, c.y)).toBe(true);
      for (const c of reg.comidas) if (m.mundo!.seca(c.de[0] + DX, c.de[1] + DY)) expect(c.para).toEqual([c.de[0] + DX, c.de[1] + DY]);
      expect(() => m.mudarIlha()).toThrow(/ilha grande/);
      expect(() => m.aplicarEvento([t, "mi", { ilha: "grande" }])).toThrow();
      /* dali em diante */
      expect(viver(m, 2)).toBe(0);
      expect(m.mundo!.contratoDecisoes.length).toBeGreaterThan(10);
      semTrajetoriaFechada(m);
      expect(Motor.reproduzir(s, copia(m.log), v).assinatura()).toBe(m.assinatura());
      /* o registro cortado antes do "mi" e a vida de antes, byte a byte */
      expect(Motor.reproduzir(s, copia(m.log.slice(0, n)), v).assinatura()).toBe(gemeo.assinatura());
    });

  test("o registro de entre a IA4 e a IG4 (o v21 com o mi para a ilha com agua) continua abrindo, e esse pet tambem passa", () => {
    const base = ligarProduto(new Motor(303, 21)); viver(base, 1);
    const t = base.e.tick, registro: EventoRegistro[] = [...copia(base.log), [t, "mi", { ilha: "mvp_agua" }]];
    const m = Motor.reproduzir(303, registro, 21);
    expect([m.naIlhaComAgua, m.naIlhaGrande, m.podeMudarIlha, emTerra(m)]).toEqual([true, false, true, true]);
    expect(m.mundo!.cm).toEqual(CMU_MVP_AGUA);
    expect(m.mundo!.trocaIlha!.tick).toBe(t);
    expect(viver(m, 1)).toBe(0);
    expect(passarParaIlhaComAgua(m)).toBe(true);
    expect([m.naIlhaGrande, m.podeMudarIlha, emTerra(m), m.mundo!.trocaIlha !== null, m.mundo!.trocaMaior!.de]).toEqual([true, false, true, true, "mvp_agua"]);
    expect(m.log.filter(e => e[1] === "mi").map(e => (e[2] as { ilha: string }).ilha)).toEqual(["mvp_agua", "grande"]);
    expect(viver(m, 1)).toBe(0);
    expect(Motor.reproduzir(303, copia(m.log), 21).assinatura()).toBe(m.assinatura());
  });

  test("a ida vale com o pet dormindo; o pet morto nao passa", () => {
    const m = ligarProduto(new Motor(303, 21));
    for (let i = 0; i < 3000 && !m.e.dormindo; i++) m.avancar(7);
    expect(m.e.dormindo).toBe(true);
    m.mudarIlha();
    expect([m.naIlhaGrande, m.e.dormindo, emTerra(m)]).toEqual([true, true, true]);
    expect(Motor.reproduzir(303, copia(m.log), 21).assinatura()).toBe(m.assinatura());
    const morto = new Motor(404, 21);
    morto.morte = { tick: morto.e.tick, causa: "lesoes" };
    expect([morto.podeMudarIlha, passarParaIlhaComAgua(morto)]).toEqual([false, false]);
  });
});

describe("no app", () => {
  const armaz = (d: Record<string, string> = {}): Armazenamento & { d: Record<string, string> } =>
    ({ d, getItem: k => (k in d ? d[k]! : null), setItem(k, v) { d[k] = v; } });

  for (const v of [21, 22]) test(`o save v${v} passa para a ilha grande ao abrir, e o registro com o evento e gravado na hora; abrir de novo nao repete`, () => {
    const antigo = ligarProduto(new Motor(606, v)); viver(antigo, .5);
    const a = armaz({ [CHAVE]: textoSave(antigo) });
    iniciarJogo(a);
    const m = jogoAtual().motor;
    expect([m.versao, m.naIlhaGrande, emTerra(m)]).toEqual([v, true, true]);
    const s = JSON.parse(a.d[CHAVE]!) as { versao: number; log: EventoRegistro[] };
    expect(s.versao).toBe(v);
    expect(s.log.slice(0, -1)).toEqual(copia(antigo.log));
    expect(s.log.at(-1)).toEqual([antigo.e.tick, "mi", { ilha: "grande" }]);
    expect(Motor.reproduzir(606, s.log, v).assinatura()).toBe(m.assinatura());
    const texto = a.d[CHAVE]!;
    iniciarJogo(a);
    expect(a.d[CHAVE]).toBe(texto);
    expect(jogoAtual().motor.log.filter(e => e[1] === "mi").length).toBe(1);
  });

  test("o pet de exemplo das versoes de antes (v21 e v22) segue nao sendo do jogador, antes e depois de passar para a ilha grande", () => {
    const hoje = petExemplo();
    expect([hoje.versao, ehPetDoJogador(hoje)]).toEqual([23, false]);
    for (const v of [21, 22]) {
      const antigo = petExemplo(v);
      expect([antigo.versao, ehPetDoJogador(antigo)]).toEqual([v, false]);
      antigo.avancar(90);
      expect(passarParaIlhaComAgua(antigo)).toBe(true);
      antigo.avancar(60);
      expect(ehPetDoJogador(antigo), `v${v}`).toBe(false);          // o "mi" e do jogo, nao do jogador
      antigo.observar("acariciar");
      expect(ehPetDoJogador(antigo), `v${v}`).toBe(true);           // um cuidado a mais o faz do jogador, como antes
    }
  });

  test("a bola que rolava para onde esta na troca para a agua (o espelho do teste do Python)", () => {
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

  test("o pet que entra pela troca de pet tambem passa; o ovo novo ja nasce v23 na ilha grande", () => {
    const a = armaz({ [CHAVE]: textoSave(ligarProduto(new Motor(707, 21))) });
    iniciarJogo(a);
    const guardado = ligarProduto(new Motor(808, 22)); viver(guardado, .5);
    expect(guardado.naIlhaGrande).toBe(false);
    trocarMotor(guardado, "save");
    expect([jogoAtual().motor.semente, jogoAtual().motor.naIlhaGrande]).toEqual([808, true]);
    expect((JSON.parse(a.d[CHAVE]!) as { log: EventoRegistro[] }).log.at(-1)).toEqual([guardado.e.tick, "mi", { ilha: "grande" }]);
    novoPet();
    const ovo = jogoAtual().motor;
    expect([ovo.versao, ovo.naIlhaGrande, ovo.log.some(e => e[1] === "mi")]).toEqual([23, true, false]);
    expect((JSON.parse(a.d[CHAVE]!) as { versao: number }).versao).toBe(23);
  });
});
