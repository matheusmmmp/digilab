// A decisao da reacao de rosto (src/telas/pet/reacao.ts; docs/TAREFA_V3_SPRITES_REACOES.md, R-rosto-jogo): so vista, sem DOM. O gatilho de cada
// reacao, a ordem (evento do dono, depois o estado do corpo), o Idle antes da expressao e o movimento de 1 texel.
import { beforeEach, expect, test } from "vitest";
import { REACAO, bobDaReacao, emoteDaReacaoAgora, escolherReacao, esquecerReacaoRosto, marcarReacaoRosto, registrarAcaoDono, type EntradaReacao } from "../src/telas/pet/reacao.ts";
import { S } from "../src/grades.ts";
import { EMOTE_DA_REACAO } from "../src/telas/pet/reacao.ts";

const BEM: EntradaReacao = { chave: "p", humor: 0.7, energia: 0.9, saude: 1, lesionado: false, dormindo: false };
const em = (o: Partial<EntradaReacao> = {}): EntradaReacao => ({ ...BEM, ...o });
beforeEach(() => esquecerReacaoRosto());

test("sem gatilho, nenhuma reacao", () => {
  expect(escolherReacao(BEM, 1000)).toBeNull();
});

test("o estado do corpo: Doente (lesao ou saude baixa) > Triste (humor baixo) > Cansado (energia baixa)", () => {
  expect(escolherReacao(em({ lesionado: true, humor: 0.1, energia: 0.1 }), 0)?.reacao).toBe("Doente");
  expect(escolherReacao(em({ saude: REACAO.saudeBaixa - 0.01, humor: 0.1 }), 0)?.reacao).toBe("Doente");
  expect(escolherReacao(em({ humor: REACAO.humorBaixo - 0.01, energia: 0.1 }), 0)?.reacao).toBe("Triste");
  expect(escolherReacao(em({ energia: REACAO.energiaBaixa - 0.01 }), 0)?.reacao).toBe("Cansado");
  expect(escolherReacao(em({ energia: REACAO.energiaBaixa }), 0)).toBeNull();
});

test("dormindo, nenhuma reacao (o Dormir e o corpo)", () => {
  expect(escolherReacao(em({ dormindo: true, lesionado: true }), 0)).toBeNull();
});

test("o Idle vem antes da expressao: so mostra depois de idleMs", () => {
  const e = em({ humor: 0.1 });
  expect(escolherReacao(e, 1000)).toEqual({ reacao: "Triste", mostrar: false });
  expect(escolherReacao(e, 1000 + REACAO.idleMs - 1)?.mostrar).toBe(false);
  expect(escolherReacao(e, 1000 + REACAO.idleMs)?.mostrar).toBe(true);
});

test("o tapa: Triste; o segundo dentro da janela, Medo; fora dela, Triste de novo", () => {
  registrarAcaoDono("tapa", 0, 0.5);
  expect(escolherReacao(BEM, 10)?.reacao).toBe("Triste");
  registrarAcaoDono("tapa", 5000, 0.5);
  expect(escolherReacao(BEM, 5010)?.reacao).toBe("Medo");
  registrarAcaoDono("tapa", 5000 + REACAO.janelaMedoMs + 1, 0.5);
  expect(escolherReacao(BEM, 5000 + REACAO.janelaMedoMs + 2)?.reacao).toBe("Triste");
});

test("acariciar: Carinho; o evento acaba depois de eventoMs", () => {
  registrarAcaoDono("acariciar", 100, 0.5);
  expect(escolherReacao(BEM, 200)?.reacao).toBe("Carinho");
  expect(escolherReacao(BEM, 100 + REACAO.eventoMs)).toBeNull();
});

test("alimentar: Recusa so sem fome (a fome acima de 0,45); com fome, nada", () => {
  registrarAcaoDono("alimentar", 0, REACAO.semFome);
  expect(escolherReacao(BEM, 10)).toBeNull();
  registrarAcaoDono("alimentar", 50, REACAO.semFome + 0.01);
  expect(escolherReacao(BEM, 60)?.reacao).toBe("Recusa");
});

test("o evento do dono vale mais que o estado do corpo, e o estado volta depois", () => {
  const doente = em({ lesionado: true });
  expect(escolherReacao(doente, 0)?.reacao).toBe("Doente");
  registrarAcaoDono("acariciar", 1000, 0.5);
  expect(escolherReacao(doente, 1100)?.reacao).toBe("Carinho");
  expect(escolherReacao(doente, 1000 + REACAO.eventoMs)?.reacao).toBe("Doente");
});

test("acoes sem reacao (limpar, brincar, tratar) nao criam evento; o Envergonhado nao tem gatilho", () => {
  for (const a of ["limpar", "brincar", "tratar_lesao", "elogiar"]) registrarAcaoDono(a, 0, 0.9);
  expect(escolherReacao(BEM, 10)).toBeNull();
});

test("falha alto: leitura nao finita", () => {
  expect(() => escolherReacao(em({ humor: NaN }), 0)).toThrow(/humor nao finito/);
  expect(() => registrarAcaoDono("tapa", 0, NaN)).toThrow(/fome nao finita/);
});

test("o movimento: 1 texel inteiro, alternando; reduzido, nenhum", () => {
  expect(bobDaReacao(0, false)).toBe(0);
  expect(bobDaReacao(REACAO.bobMs, false)).toBe(1);
  expect(bobDaReacao(2 * REACAO.bobMs, false)).toBe(0);
  expect(bobDaReacao(REACAO.bobMs, true)).toBe(0);
});

test("o emote de cada reacao existe em grades.ts (o Carinho e o Envergonhado ficam sem proprio)", () => {
  for (const [r, g] of Object.entries(EMOTE_DA_REACAO)) if (g !== null) expect(S[g], `${r}: ${g}`).toBeDefined();
  expect(EMOTE_DA_REACAO.Carinho).toBeNull(); expect(EMOTE_DA_REACAO.Envergonhado).toBeNull();
  marcarReacaoRosto("Triste"); expect(emoteDaReacaoAgora()).toBe("lagrima");
  marcarReacaoRosto("Carinho"); expect(emoteDaReacaoAgora()).toBeNull();
  marcarReacaoRosto(null); expect(emoteDaReacaoAgora()).toBeNull();
});

test("as grades novas: retangulares e so com as cores da paleta", () => {
  for (const g of ["lagrima", "reticencias", "x", "espiral"]) {
    const w = S[g][0].length;
    expect(S[g].every(l => l.length === w), g).toBe(true);
    expect([...S[g].join("")].every(c => ".kcwrg".includes(c)), g).toBe(true);
  }
});
