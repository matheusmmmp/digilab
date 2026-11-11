// Os momentos do pet no habitat (src/telas/pet/momentos.ts; docs/PLANO_V3_HABITAT_REACOES.md, HR1): so vista, sem DOM. Cada instante novo, o
// clipe que ele pede, a fila (o momento espera o corpo ficar livre e sai depois de esperaMaxMs) e o rosto que vai para reacao.ts.
import { beforeEach, expect, test } from "vitest";
import { CLIPES_ACOES, CLIPES_REACOES } from "../src/atlas.ts";
import {
  MOMENTOS, ROSTOS_DOS_MOMENTOS, estadoAgora, esquecerMomentos, momentoAgora, momentoDoCarinho, momentoDoDono, tentouPegarDormindo, vigiarMomentos,
  virandoAgora, type EntradaMomentos,
} from "../src/telas/pet/momentos.ts";
import { escolherReacao, esquecerReacaoRosto, type EntradaReacao } from "../src/telas/pet/reacao.ts";

const BASE: EntradaMomentos = { chave: "p", nascendo: 0, dormindo: false, morto: false, acao: "ocioso", abertos: [], urgente: false, atendidos: 0, consumos: 0, ultimo: null, vazio: null };
const em = (o: Partial<EntradaMomentos> = {}): EntradaMomentos => ({ ...BASE, ...o });
const CICLO = 800, ciclo = () => CICLO;
const CORPO: EntradaReacao = { chave: "p", humor: 0.7, energia: 0.9, saude: 1, lesionado: false, dormindo: false };
const rosto = (t: number) => escolherReacao(CORPO, t)?.reacao ?? null;
beforeEach(() => { esquecerMomentos(); esquecerReacaoRosto(); });

test("os clipes dos momentos existem no atlas (acoes e rostos)", () => {
  for (const c of ["Feliz", "Sacudir", "Chamar"]) expect(CLIPES_ACOES as readonly string[]).toContain(c);
  for (const r of ROSTOS_DOS_MOMENTOS) expect(CLIPES_REACOES as readonly string[]).toContain(r);
});

test("a primeira olhada e a troca de pet nao contam", () => {
  vigiarMomentos(em({ nascendo: 5 }), 0);
  vigiarMomentos(em({ chave: "q", nascendo: 0 }), 10);
  expect(momentoAgora(20, true, ciclo)).toBeNull();
});

test("a casca quebra: Feliz uma vez, por um ciclo do clipe", () => {
  vigiarMomentos(em({ nascendo: 3 }), 0);
  vigiarMomentos(em({ nascendo: 0 }), 100);
  expect(momentoAgora(100, true, ciclo)).toEqual({ clipe: "Feliz", desde: 100 });
  expect(momentoAgora(100 + CICLO - 1, true, ciclo)?.clipe).toBe("Feliz");
  expect(momentoAgora(100 + CICLO, true, ciclo)).toBeNull();
});

test("o momento espera o corpo ficar livre e sai depois de esperaMaxMs", () => {
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ atendidos: 1 }), 0);
  expect(momentoAgora(500, false, ciclo)).toBeNull();
  expect(momentoAgora(600, true, ciclo)?.clipe).toBe("Feliz");
  esquecerMomentos();
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ atendidos: 1 }), 0);
  expect(momentoAgora(MOMENTOS.esperaMaxMs + 1, true, ciclo)).toBeNull();
});

test("a forma sem o clipe: o momento sai sem tocar", () => {
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ atendidos: 1 }), 0);
  expect(momentoAgora(0, true, () => null)).toBeNull();
  expect(momentoAgora(10, true, ciclo)).toBeNull();
});

test("limpar sacode e tratar deixa Feliz, depois da espera do dono; o carinho que relaxou, depois do pulinho", () => {
  vigiarMomentos(em(), 0);
  momentoDoDono("limpar", 0);
  expect(momentoAgora(MOMENTOS.esperaDonoMs - 1, true, ciclo)).toBeNull();
  expect(momentoAgora(MOMENTOS.esperaDonoMs, true, ciclo)?.clipe).toBe("Sacudir");
  esquecerMomentos(); vigiarMomentos(em(), 0);
  momentoDoDono("tratar_lesao", 0);
  expect(momentoAgora(MOMENTOS.esperaDonoMs, true, ciclo)?.clipe).toBe("Feliz");
  esquecerMomentos(); vigiarMomentos(em(), 0);
  momentoDoDono("alimentar", 0);
  expect(momentoAgora(MOMENTOS.esperaDonoMs, true, ciclo)).toBeNull();
  momentoDoCarinho(0);
  expect(momentoAgora(MOMENTOS.carinhoMs - 1, true, ciclo)).toBeNull();
  expect(momentoAgora(MOMENTOS.carinhoMs, true, ciclo)?.clipe).toBe("Feliz");
});

test("comer: a comida madura que encheu a barriga e Feliz; a fruta podre e Recusa; a racao que encheu pouco, nada", () => {
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ consumos: 1, ultimo: { tipo: "racao", situacao: "madura", fome_antes: 0.2, fome_depois: 0.6 } }), 0);
  expect(momentoAgora(0, true, ciclo)?.clipe).toBe("Feliz");
  esquecerMomentos();
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ consumos: 1, ultimo: { tipo: "racao", situacao: "madura", fome_antes: 0.5, fome_depois: 0.6 } }), 0);
  expect(momentoAgora(0, true, ciclo)).toBeNull();
  esquecerMomentos();
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ consumos: 1, ultimo: { tipo: "maca", situacao: "podre", fome_antes: 0.5, fome_depois: 0.5 } }), 1000);
  expect(momentoAgora(1000, true, ciclo)).toBeNull();
  expect(rosto(1000)).toBe("Recusa");
  expect(rosto(1000 + MOMENTOS.podreMs)).toBeNull();
});

test("acordar e Cansado por acordarMs; o chamado perdido e Triste; o atendido e Feliz", () => {
  vigiarMomentos(em({ dormindo: true }), 0);
  vigiarMomentos(em(), 100);
  expect(rosto(100)).toBe("Cansado");
  expect(rosto(100 + MOMENTOS.acordarMs)).toBeNull();
  esquecerMomentos(); esquecerReacaoRosto();
  vigiarMomentos(em({ abertos: ["fome"] }), 0);
  vigiarMomentos(em({ abertos: [] }), 50);
  expect(rosto(50)).toBe("Triste");
  expect(momentoAgora(50, true, ciclo)).toBeNull();
  esquecerMomentos(); esquecerReacaoRosto();
  vigiarMomentos(em({ abertos: ["fome"] }), 0);
  vigiarMomentos(em({ abertos: [], atendidos: 1 }), 50);
  expect(rosto(50)).toBeNull();
  expect(momentoAgora(50, true, ciclo)?.clipe).toBe("Feliz");
});

test("os estados em laco: Die morto, Chamar com chamado aberto, Feliz brincando; no ovo e dormindo, nada", () => {
  expect(estadoAgora(em({ morto: true, dormindo: true }))).toBe("Die");
  expect(estadoAgora(em({ abertos: ["higiene"] }))).toBe("Chamar");
  expect(estadoAgora(em({ acao: "chamar_atencao" }))).toBe("Chamar");
  expect(estadoAgora(em({ acao: "brincar" }))).toBe("Feliz");
  expect(estadoAgora(em({ acao: "brincar", dormindo: true }))).toBeNull();
  expect(estadoAgora(em({ nascendo: 2, morto: true }))).toBeNull();
  expect(estadoAgora(em())).toBeNull();
});

test("morto: a fila se apaga", () => {
  vigiarMomentos(em(), 0);
  momentoDoDono("limpar", 0);
  vigiarMomentos(em({ morto: true }), 10);
  expect(momentoAgora(MOMENTOS.esperaDonoMs, true, ciclo)).toBeNull();
});

test("o pet dormindo vira de lado por viraMs quando o dono tenta pegar", () => {
  expect(virandoAgora(0)).toBe(false);
  tentouPegarDormindo(1000);
  expect(virandoAgora(1000)).toBe(true);
  expect(virandoAgora(1000 + MOMENTOS.viraMs)).toBe(false);
});

test("falha alto com numero nao finito", () => {
  expect(() => vigiarMomentos(em({ atendidos: Number.NaN }), 0)).toThrow(/nao finito/);
  vigiarMomentos(em(), 0);
  expect(() => vigiarMomentos(em({ consumos: 1, ultimo: { tipo: "racao", situacao: "madura", fome_antes: Number.NaN, fome_depois: 1 } }), 0)).toThrow(/fome/);
});

test("o lugar lembrado vazio (CADEIA, D6): um episodio nao_havia novo e Triste por vazioMs; o mesmo episodio nao repete", () => {
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ vazio: 7 }), 100);
  expect(rosto(100)).toBe("Triste");
  expect(rosto(100 + MOMENTOS.vazioMs)).toBeNull();
  vigiarMomentos(em({ vazio: 7 }), 3000);
  expect(rosto(3000)).toBeNull();
  vigiarMomentos(em({ vazio: 9 }), 4000);
  expect(rosto(4000)).toBe("Triste");
});
