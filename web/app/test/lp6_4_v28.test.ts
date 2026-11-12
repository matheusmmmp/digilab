/* LUTA_POC, LP6-4: a v28, a v26 (o grupo de dois) com a luta da LP6 (docs/PLANO_LP6_SEGUNDO_GOLPE.md; o lp6_3_u120 da LP6-3). A tabela e a
   da v23 com o apoio so no Ultimate e no Mega, sem o recuo, e a elipse 1,2/1,4; o ovo do brasao choca o grupo v28; antes do Ultimate a luta
   e a mesma da v26, e no Ultimate e no Mega o apoio e a arena entram; o palco refaz a luta com eles; o gabarito da vida alta e o replay. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import {
  APOIO_LP6_3, ARENA_POR_ESTAGIO_LP6_3, LIMITE_POC_MS, LUTA_V23, LUTA_V28, VERSAO_GRUPO, VERSAO_V26, VERSAO_V27, VERSAO_V28, configLutaPoc,
  criarLutaPoc, ehDoGrupo, ehLutaLp6, passoPoc, sorteiosPoc, tabelaLuta,
} from "../motor/index.ts";
import { extrasLp6 } from "../scripts/equilibrio_poc/comum.ts";
import { LP5_3, LP6_3_U120 } from "../scripts/equilibrio_poc/candidatos.ts";
import { lutasDoResultado } from "../src/lutaPocTela.ts";
import { passoDe } from "../src/telas/lutar/palcoPoc/visualPoc.ts";
import { SEMENTES_ALTA, gabaritoAlta, gravarAlta, reproduzirAlta, viverAlta, type VidaAlta } from "./lp6_4_luta_alta.ts";

describe("a versao e a tabela (LP6-4)", () => {
  test("a v28 e do grupo, luta pela LUTA_V28, e o grupo de hoje e ela; a v26 e a v27 seguem na LUTA_V23", () => {
    expect(VERSAO_GRUPO).toBe(VERSAO_V28);
    expect(ehDoGrupo(VERSAO_V28)).toBe(true);
    expect([ehLutaLp6(VERSAO_V26), ehLutaLp6(VERSAO_V27), ehLutaLp6(VERSAO_V28)]).toEqual([false, false, true]);
    expect(tabelaLuta(VERSAO_V28)).toBe(LUTA_V28);
    for (const v of [23, 24, 25, 26, 27]) expect(tabelaLuta(v)).toBe(LUTA_V23);
    expect(LUTA_V23.apoio).toBeUndefined(); expect(LUTA_V23.arenaPorEstagio).toBeUndefined();
  });
  test("a LUTA_V28 e a LUTA_V23 com o apoio e a arena do lp6_3_u120, e o lp6_3_u120 e o lp5_3 (a v23) com as duas chaves", () => {
    const { apoio, arenaPorEstagio, versao, ...resto } = LUTA_V28, { versao: _v, ...resto23 } = LUTA_V23;
    expect(versao).toBe(28);
    expect(resto).toEqual(resto23);
    expect(apoio).toEqual({ dano: .6, recarga: 3, longeMs: 1500, desde: "Ultimate" });
    expect(apoio).not.toHaveProperty("recua");
    expect(arenaPorEstagio).toEqual({ Ultimate: 1.2, Mega: 1.4 });
    expect([apoio, arenaPorEstagio]).toEqual([APOIO_LP6_3, ARENA_POR_ESTAGIO_LP6_3]);
    const x = extrasLp6(LP6_3_U120);
    expect(x).toEqual({ apoio: { ...APOIO_LP6_3 }, arenaPorEstagio: { ...ARENA_POR_ESTAGIO_LP6_3 } });
    const { apoio: _a, arena: _r, nome: _n, ...c } = LP6_3_U120, { apoio: _a3, arena: _r3, nome: _n3, ...c3 } = LP5_3;
    expect(c).toEqual(c3);
  });
});

describe("a vida do grupo v28 contra a do v26 (a mesma semente)", () => {
  const s = SEMENTES_ALTA[0], a = viverAlta(s, VERSAO_V26), b = viverAlta(s, VERSAO_V28);
  test("ate a primeira luta no Ultimate, as lutas sao as mesmas; depois, a luta muda", () => {
    const i = a.res.findIndex(r => r.startsWith("adulto:"));
    expect(i).toBeGreaterThan(0);
    expect(b.res.findIndex(r => r.startsWith("adulto:"))).toBe(i);
    expect(b.res.slice(0, i)).toEqual(a.res.slice(0, i));
    expect(b.res.slice(i)).not.toEqual(a.res.slice(i));
  });
  test("so a luta muda: a v28 e a v26 tem o mesmo mundo e o mesmo registro ate o Ultimate", () => {
    expect(b.v.m.versao).toBe(VERSAO_V28);
    const la = a.v.log() as unknown[][], lb = b.v.log() as unknown[][];
    const tUlt = b.v.m.evolucoes.find(e => e.estagio === "adulto")!.tick;
    const antes = (l: unknown[][]) => l.filter(e => (e[0] as number) < tUlt);
    expect(antes(lb)).toEqual(antes(la));
  });
  test("o palco refaz as lutas do Mega da v28 com o apoio e a arena da tabela, e acabam como no motor", () => {
    const m = b.v.m;
    expect(m.estagioAtual).toBe("mega");
    for (const [k, mapa] of (["campo", "praia", "deserto"] as const).entries()) {
      const r = b.v.agir(x => x.lutarPoc(x.rivaisArenaPoc()[k]!, 9100 + k, mapa));
      expect(r.apoio).toBe(LUTA_V28.apoio); expect(r.arenaPorEstagio).toBe(LUTA_V28.arenaPorEstagio);
      for (const l of lutasDoResultado(r)) {
        expect(l.entrada.apoio).toBe(r.apoio); expect(l.entrada.arenaPorEstagio).toBe(r.arenaPorEstagio);
        const L = criarLutaPoc(configLutaPoc(l.entrada), sorteiosPoc(l.entrada.semente));
        while (!L.fim && L.relogio < LIMITE_POC_MS) passoPoc(L);
        expect({ vencedor: L.vencedor, relogio: L.relogio, passos: passoDe(L) }).toEqual({ vencedor: l.esperado!.vencedor, relogio: l.esperado!.relogio, passos: l.esperado!.passos });
      }
      if (m.lesionadoDesde !== null) b.v.agir(x => x.observar("tratar_lesao"));
      b.v.avancar(30);
    }
  });
});

const gab = JSON.parse(readFileSync(new URL(gabaritoAlta(VERSAO_V28), import.meta.url), "utf8")) as { vidas: VidaAlta[] };
describe("a vida alta da v28: o gabarito e o replay bit a bit", () => {
  for (const s of SEMENTES_ALTA) {
    test(`v28 @${s}`, () => {
      const x = viverAlta(s, VERSAO_V28), g = gravarAlta(s, x);
      expect(g).toEqual(gab.vidas.find(y => y.semente === s));
      expect(g.estagio).toBe("mega");
      expect(reproduzirAlta(x)).toBe(g.assinatura);
    });
  }
});
