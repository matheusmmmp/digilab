// O empurrao de verdade de quem leva o golpe (docs/TAREFA_V3_LUTA_EMPURRAO.md, etapa 3; EMP-1 a EMP-8): so na v18 (RELOGIO_V18), com os
// casos da tabela 3.2 (a forca por golpe, a queda, as posturas, a cerca), o determinismo e a versao do pet. As lutas da v13 a v17 nao mudam:
// quem confere e o gabarito de test/luta_tr_hoje.test.ts.
import { describe, expect, test } from "vitest";
import {
  CTR_TR, CV21E_TR, CV21E_TR14, CV21E_TR18, Cd, EMPURRAO_V18, FORMAS_AD, Motor, RELOGIO_V14, RELOGIO_V18, Rg, VERSAO_PET, VERSOES_PET,
  criarLutaTR, ehCerebroTrocavel, jogarTR, lutadorBot, passoTR, perfilNeutro, regrasDaVersao, relogioDe, type EventoTR, type Lutador,
  type ResultadoLutaTR,
} from "../motor/index.ts";

const R = CV21E_TR18;
/** Guts sobrando: o atacante prepara e bate sem parar */
const cheio = () => ({ ...perfilNeutro(), guts0: 1000, gutsMax: 1000, regen: 1000 });
const lista = (regras: ReturnType<typeof Rg>[], final = "carregar"): Lutador =>
  ({ nome: "teste", estilo: { nome: "teste", gambits: { regras, final }, eps: 0 }, cond: cheio() });
const pesado = () => lista([Rg(Cd("distancia_eh", 0), "preparar_pesado"), Rg(Cd("sempre"), "avancar")]);
const comTecnica = (L: Lutador, t: string): Lutador => ({ ...L, cond: { ...L.cond, tecnica: t as Lutador["cond"]["tecnica"] } });
const investida = () => comTecnica(lista([Rg(Cd("distancia_eh", 1), "investida"), Rg(Cd("sempre"), "avancar")]), "investida");
const rapido = () => lista([Rg(Cd("distancia_eh", 0), "golpe_rapido"), Rg(Cd("sempre"), "avancar")]);
const postura = (p: string) => p === "contra_golpe" ? comTecnica(lista([Rg(Cd("sempre"), p)], p), p) : lista([Rg(Cd("sempre"), p)], p);
type Emp = Extract<EventoTR, { tipo: "empurrao" }>;
const empurroes = (r: ResultadoLutaTR, lado: number): Emp[] => r.eventos!.filter((e): e is Emp => e.tipo === "empurrao" && e.lado === lado);
const resumo = (r: ResultadoLutaTR) => ({ pontosA: r.pontosA, fim: r.fim, passos: r.passos, hp: r.E.L.map(l => l.hp), acoes: r.acoes, eventos: r.eventos });
const LIMITE_DIR = CTR_TR.centro + CTR_TR.meiaLargura;
/** a luta inteira, comecando com os dois a `d` px (no medio, para a investida sair: quem avanca so para no contato) */
function lutaDe(A: Lutador, B: Lutador, d: number) {
  const Lt = criarLutaTR(A, B, 1, { R, eventos: true });
  Lt.S.L[0].x = Lt.S.L[1].x - d;
  while (!passoTR(Lt));
  return { acoes: Lt.acoes, eventos: Lt.eventos! } as unknown as ResultadoLutaTR;
}

describe("a versao 18 e a chave", () => {
  test("os ovos novos nascem v18; a v13 a v17 seguem abrindo; a v18 tem o cerebro trocavel da v17", () => {
    expect(VERSAO_PET).toBe(19); expect(VERSOES_PET).toEqual([13, 14, 15, 17, 18, 19]);
    expect(new Motor(101).versao).toBe(19);
    for (const v of [13, 14, 15, 17]) expect(new Motor(101, v).versao).toBe(v);
    expect(ehCerebroTrocavel(17)).toBe(true); expect(ehCerebroTrocavel(18)).toBe(true); expect(ehCerebroTrocavel(15)).toBe(false);
  });
  test("so a v18 tem o empurrao: as regras, o relogio e a chave desligada nas outras", () => {
    expect(regrasDaVersao(18)).toBe(CV21E_TR18);
    for (const v of [14, 15, 16, 17]) expect(regrasDaVersao(v)).toBe(CV21E_TR14);
    expect(relogioDe(CV21E_TR18)).toBe(RELOGIO_V18); expect(relogioDe(CV21E_TR14)).toBe(RELOGIO_V14);
    expect(relogioDe(CV21E_TR).empurraoAlvo).toBeNull(); expect(RELOGIO_V14.empurraoAlvo).toBeNull();
    /* o RELOGIO_V18 e o da v14 com o empurrao: nada mais muda */
    expect({ ...RELOGIO_V18, empurraoAlvo: null }).toEqual(RELOGIO_V14);
    expect(EMPURRAO_V18).toEqual({ forca: { investida: 20, pesado: 60 }, derruba: ["investida", "pesado"], queda: 62, deslize: 10, guarda: .5, defesa: 0 });
  });
  test("a v14 nao empurra nem derruba (nenhum evento de empurrao)", () => {
    const r = jogarTR(pesado(), postura("carregar"), 1, { R: CV21E_TR14, eventos: true });
    expect(r.eventos!.some(e => e.tipo === "empurrao")).toBe(false);
  });
  test("o determinismo: a mesma luta v18 da o mesmo resultado, nas 8 formas adultas", () => {
    for (const a of FORMAS_AD) for (const b of FORMAS_AD) {
      const A = lutadorBot(a, R), B = lutadorBot(b, R);
      expect(resumo(jogarTR(A, B, 4242, { R, eventos: true }))).toEqual(resumo(jogarTR(A, B, 4242, { R, eventos: true })));
    }
  });
});

describe("a forca de cada golpe e a queda (EMP-1, EMP-2, EMP-6)", () => {
  test("o pesado empurra 60 px em 10 passos e derruba por 62 passos; o caido nao decide ate levantar", () => {
    const Lt = criarLutaTR(pesado(), postura("carregar"), 1, { R, eventos: true }), S = Lt.S;
    let t0 = -1, x0 = 0;
    while (t0 < 0) { passoTR(Lt); const e = Lt.eventos!.find(e => e.tipo === "empurrao"); if (e) { t0 = e.t; x0 = S.L[1].x; } }
    expect(Lt.eventos!.find(e => e.tipo === "empurrao")).toEqual({ t: t0, tipo: "empurrao", lado: 1, px: 60, queda: true });
    expect(S.L[1].acao).toBeNull(); expect(S.L[1].atordoadoAte).toBe(t0 + 62); expect(S.L[1].quedaDe).toBe(t0);
    for (let i = 0; i < 10; i++) passoTR(Lt);
    expect(S.L[1].x - x0).toBeCloseTo(60, 9);
    /* o deslize acabou: o caido nao anda mais */
    const x1 = S.L[1].x; passoTR(Lt); expect(S.L[1].x).toBe(x1);
    while (S.passo < t0 + 62) passoTR(Lt);
    expect(Lt.acoes.some(a => a.lado === 1 && a.inicio > t0 && a.inicio < t0 + 62)).toBe(false);
  });
  test("a investida empurra pela forca dela e derruba se esta em derruba", () => {
    const r = lutaDe(investida(), postura("carregar"), 100);
    expect(r.acoes.some(a => a.lado === 0 && a.nome === "investida")).toBe(true);
    expect(empurroes(r, 1)[0]).toMatchObject({ px: EMPURRAO_V18.forca.investida, queda: EMPURRAO_V18.derruba.includes("investida") });
  });
  test("o golpe rapido e o disparo nao empurram", () => {
    const r = jogarTR(rapido(), postura("carregar"), 1, { R, eventos: true });
    expect(r.eventos!.some(e => e.tipo === "dano" && e.lado === 1)).toBe(true);
    expect(r.eventos!.some(e => e.tipo === "empurrao")).toBe(false);
    const r2 = jogarTR(lista([Rg(Cd("sempre"), "disparo")]), postura("carregar"), 1, { R, eventos: true });
    expect(r2.eventos!.some(e => e.tipo === "dano" && e.lado === 1)).toBe(true);
    expect(r2.eventos!.some(e => e.tipo === "empurrao")).toBe(false);
  });
});

describe("as posturas (EMP-5)", () => {
  test("a defesa e o contra-golpe nao sao empurrados nem caem (EMP-5 trocada)", () => {
    /* entre duas posturas ha a brecha ate a proxima decisao (o ritmo): ali o pesado pega em cheio */
    for (const [p, px] of [["defender", 0], ["contra_golpe", 0]] as const) {
      const r = jogarTR(pesado(), postura(p), 1, { R, eventos: true }), es = empurroes(r, 1);
      const acertosNaPostura = r.eventos!.filter(e => e.tipo === "dano" && e.lado === 1 &&
        r.acoes.some(a => a.lado === 1 && a.nome === p && e.t >= a.inicio && e.t < a.inicio + 125));
      expect(acertosNaPostura.length, p).toBeGreaterThan(0);
      if (px > 0) expect(es.some(e => e.px === px && !e.queda), p).toBe(true);
      for (const e of es) {
        const naPostura = r.acoes.some(a => a.lado === 1 && a.nome === p && e.t >= a.inicio && e.t < a.inicio + 125);
        if (naPostura) expect(px, p).toBeGreaterThan(0);
        expect(e, p).toMatchObject(naPostura ? { px, queda: false } : { px: 60, queda: true });
      }
    }
  });
  test("a investida aparada pela defesa nao empurra ninguem", () => {
    const r = lutaDe(investida(), postura("defender"), 100);
    expect(r.acoes.some(a => a.lado === 0 && a.nome === "investida")).toBe(true);
    expect(r.eventos!.some(e => e.tipo === "empurrao")).toBe(false);
  });
  test("a esquiva anula o pesado: nem dano nem empurrao", () => {
    const r = jogarTR(pesado(), postura("esquivar"), 1, { R, eventos: true });
    expect(r.acoes.some(a => a.lado === 0 && a.nome === "pesado")).toBe(true);
    expect(empurroes(r, 1)).toEqual([]);
  });
  test("sob a pele dura, o pesado empurra pela metade e nao derruba", () => {
    const B = lista([Rg(Cd("sempre"), "pele_dura")]);
    B.cond = { ...B.cond, tecnica: "pele_dura" as const };
    const es = empurroes(jogarTR(pesado(), B, 1, { R, eventos: true }), 1);
    expect(es.some(e => e.px === 30 && !e.queda)).toBe(true);
    for (const e of es) expect(e.px === 30 ? !e.queda : e.px === 60 && e.queda).toBe(true);
  });
});

describe("a borda (EMP-4)", () => {
  test("quem e empurrado contra a cerca para nela, e o resto se perde", () => {
    const Lt = criarLutaTR(pesado(), postura("carregar"), 1, { R, eventos: true }), S = Lt.S;
    S.L[1].x = LIMITE_DIR - 10; S.L[0].x = S.L[1].x - 80;
    while (!Lt.eventos!.some(e => e.tipo === "empurrao")) { passoTR(Lt); expect(S.L[1].x).toBeLessThanOrEqual(LIMITE_DIR); }
    for (let i = 0; i < 12; i++) { passoTR(Lt); expect(S.L[1].x).toBeLessThanOrEqual(LIMITE_DIR); }
    expect(S.L[1].x).toBe(LIMITE_DIR);
  });
});
