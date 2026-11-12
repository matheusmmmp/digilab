// As chaves da N3 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 4; D-N-5, "As 4 (Recommended)", Matheus, 2026-11-12):
// cada uma desligada sem o campo na entrada (o gabarito test/luta_nucleo_n3_gabarito.test.ts confere as lutas de antes), a regra de cada
// uma ligada e o replay bit a bit com ela.
import { describe, expect, test } from "vitest";
import { MS_DO_PULO, OPCOES_PADRAO, configLuta, criarLuta, rodarAteOFim, sorteiosPorFluxo, type EntradaLuta, type Evento } from "../motor/arena/index.ts";
import { LUTA_V23 } from "../motor/luta_poc.ts";
import { resumoLutaLp6 } from "./arena_lp6_lutas.ts";
import { entradaDaTabela, lutasDoGabaritoN3 } from "./luta_nucleo_n3_lutas.ts";

/** os eventos de uma luta inteira */
function eventos(e: EntradaLuta): Evento[] {
  const L = criarLuta(configLuta(e), sorteiosPorFluxo(e.semente)), ev: Evento[] = [];
  rodarAteOFim(L, x => { ev.push(...x); });
  return ev;
}
/* o Agumon (Vaccine) contra o Guilmon (Virus): o Vaccine tem a vantagem */
const AGU_GUI = entradaDaTabela(LUTA_V23, "campo", "brasa_crianca_sereno", "brasa_crianca_arisco", 101);

describe("a chave forcaAtr (a vantagem do atributo na entrada)", () => {
  test("sem ela, a forca e a do OPCOES_PADRAO; com 1,5, a luta e a mesma", () => {
    expect(configLuta(AGU_GUI).forca).toBe(OPCOES_PADRAO.forca);
    expect(resumoLutaLp6({ ...AGU_GUI, forcaAtr: OPCOES_PADRAO.forca })).toEqual(resumoLutaLp6(AGU_GUI));
  });
  test("com 1, o triangulo nao pesa: todo dano sai com mult 1", () => {
    const ev = eventos({ ...AGU_GUI, forcaAtr: 1 }).filter(x => x.tipo === "dano");
    expect(ev.length).toBeGreaterThan(0);
    for (const x of ev) if (x.tipo === "dano") expect(x.mult).toBe(1);
    const de = eventos(AGU_GUI).filter(x => x.tipo === "dano").map(x => x.tipo === "dano" ? x.mult : 0);
    expect(de).toContain(1.5);
  });
  test("o valor entra no mult do dano (1,25 e 1/1,25)", () => {
    const ms = new Set(eventos({ ...AGU_GUI, forcaAtr: 1.25 }).flatMap(x => x.tipo === "dano" ? [x.mult] : []));
    for (const m of ms) expect([1.25, 1 / 1.25]).toContain(m);
  });
  test("fora da faixa falha alto", () => {
    for (const x of [0.99, 3.01, Number.NaN, Infinity]) expect(() => configLuta({ ...AGU_GUI, forcaAtr: x })).toThrow(/vantagem do atributo invalida/);
  });
  test("o replay bit a bit com ela ligada", () => {
    const e = { ...AGU_GUI, forcaAtr: 1.15 };
    expect(resumoLutaLp6(e)).toEqual(resumoLutaLp6(e));
  });
});

/** a luta, com o lado que caiu primeiro e se algum dano veio de quem ja tinha caido */
function tiroDeQuemCaiu(e: EntradaLuta): { vencedor: string | null; doMorto: number } {
  const L = criarLuta(configLuta(e), sorteiosPorFluxo(e.semente)), caiu = new Set<string>();
  let doMorto = 0;
  const r = rodarAteOFim(L, ev => { for (const x of ev) { if (x.tipo === "dano" && caiu.has(x.at.lado)) doMorto++; if (x.tipo === "queda") caiu.add(x.u.lado); } });
  return { vencedor: r.vencedor, doMorto };
}
describe("a chave tiroDoMorto (o projetil de quem caiu some)", () => {
  /* as lutas do gabarito da v23 em que o tiro de quem caiu ainda acertou */
  const comTiro = lutasDoGabaritoN3().filter(l => l.id.startsWith("v23|")).map(l => l.entrada).filter(e => tiroDeQuemCaiu(e).doMorto > 0);
  test("o gabarito tem lutas em que o tiro de quem caiu acerta (sem a chave)", () => {
    expect(comTiro.length).toBeGreaterThan(0);
  });
  test("com a chave, nenhum dano vem de quem ja caiu, e as lutas desses tiros deixam de empatar", () => {
    let empatesAntes = 0, empatesDepois = 0;
    for (const e of comTiro) {
      const antes = tiroDeQuemCaiu(e), depois = tiroDeQuemCaiu({ ...e, tiroDoMorto: true });
      expect(depois.doMorto).toBe(0);
      if (antes.vencedor === null) empatesAntes++;
      if (depois.vencedor === null) empatesDepois++;
    }
    expect(empatesAntes).toBeGreaterThan(0);
    expect(empatesDepois).toBeLessThan(empatesAntes);
  });
  test("a luta sem tiro no ar quando alguem cai sai igual com a chave", () => {
    const sem = lutasDoGabaritoN3().filter(l => l.id.startsWith("v23|")).map(l => l.entrada).find(e => {
      const L = criarLuta(configLuta(e), sorteiosPorFluxo(e.semente)); let ar = false;
      rodarAteOFim(L, (ev, Lx) => { if (ev.some(x => x.tipo === "queda") && Lx.projeteis.length) ar = true; });
      return !ar;
    })!;
    const { sha: a, ...ra } = resumoLutaLp6(sem), { sha: b, ...rb } = resumoLutaLp6({ ...sem, tiroDoMorto: true });
    expect(rb).toEqual(ra); expect(b).toBe(a);
  });
  test("so vale ligada; o replay bit a bit com ela", () => {
    expect(() => configLuta({ ...AGU_GUI, tiroDoMorto: false as unknown as true })).toThrow(/so vale ligada/);
    const e = { ...comTiro[0], tiroDoMorto: true as const };
    expect(resumoLutaLp6(e)).toEqual(resumoLutaLp6(e));
  });
});

/** os pulos da esquiva do lado a (px andados de ponta a ponta) */
function pulosDoA(e: EntradaLuta): number[] {
  const L = criarLuta(configLuta(e), sorteiosPorFluxo(e.semente)), out: number[] = [];
  let em = false, x0 = 0, y0 = 0;
  rodarAteOFim(L, (_ev, Lx) => {
    const u = Lx.a;
    if (u.dash > 0 && !em) { em = true; x0 = u.x; y0 = u.y; }
    else if (u.dash <= 0 && em) { em = false; out.push(Math.hypot(u.x - x0, u.y - y0)); }
  });
  return out;
}
describe("a chave puloMax (o teto do pulo da esquiva)", () => {
  /* o Agumon de agilidade 4,7 (o folego com 8 pontos na v23, a N2) contra o Guilmon, nos mapas sem o mov e sem a borda; varias sementes */
  const agil = (s: number, cena: EntradaLuta["cena"]): EntradaLuta => ({ ...AGU_GUI, cena, semente: s, a: { ...AGU_GUI.a, stats: { ...AGU_GUI.a.stats, agil: 4.7 } } });
  const lutas = [101, 202, 303, 404, 505].flatMap(s => (["campo", "coliseu", "castelo"] as const).map(c => agil(s, c)));
  test("sem a chave, o pulo passa de 150 px", () => {
    expect(Math.max(...lutas.flatMap(pulosDoA))).toBeGreaterThan(150);
  });
  test("com 80 px, nenhum pulo passa do teto", () => {
    const ps = lutas.flatMap(e => pulosDoA({ ...e, puloMax: 80 }));
    expect(ps.length).toBeGreaterThan(0);
    for (const p of ps) expect(p).toBeLessThanOrEqual(80 + 1e-9);
  });
  test("um teto acima do pulo nao muda a luta", () => {
    const e = { ...AGU_GUI };   // a agilidade de sempre: o pulo neutro e 380 px/s x 192 ms, ~73 px
    expect(380 * MS_DO_PULO / 1000).toBeLessThan(400);
    expect(resumoLutaLp6({ ...e, puloMax: 400 })).toEqual(resumoLutaLp6(e));
  });
  test("fora da faixa falha alto; o replay bit a bit com ela", () => {
    for (const x of [9, 401, Number.NaN]) expect(() => configLuta({ ...AGU_GUI, puloMax: x })).toThrow(/teto do pulo invalido/);
    const e = { ...lutas[0], puloMax: 90 };
    expect(resumoLutaLp6(e)).toEqual(resumoLutaLp6(e));
  });
});
