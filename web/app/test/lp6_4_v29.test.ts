/* LUTA_POC, LP6-4: a v29, a v28 (o grupo de dois com o sono que segura, #861) com a luta da LP6 (docs/PLANO_LP6_SEGUNDO_GOLPE.md; o
   lp6_3_u120 da LP6-3). A tabela e a da v23 com o apoio so no Ultimate e no Mega, sem o recuo, e a elipse 1,2/1,4; o ovo do brasao choca o
   grupo v29; antes do Ultimate a vida e a mesma da v28, e no Ultimate e no Mega o apoio e a arena entram; o palco refaz a luta com eles; os
   grupos v26 e v28 de antes seguem abrindo como eram; o gabarito da vida alta e o replay. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import {
  APOIO_LP6_3, ARENA_POR_ESTAGIO_LP6_3, GrupoDoJogo, LIMITE_POC_MS, LUTA_V23, LUTA_V29, VERSAO_GRUPO, VERSAO_PET, VERSAO_V26, VERSAO_V27, VERSAO_V28,
  VERSAO_V29, configLutaPoc, criarLutaPoc, ehDoGrupo, ehLutaLp6, nasceComSonoSegura, passoPoc, sorteiosPoc, tabelaLuta,
} from "../motor/index.ts";
import { extrasLp6 } from "../scripts/equilibrio_poc/comum.ts";
import { LP5_3, LP6_3_U120 } from "../scripts/equilibrio_poc/candidatos.ts";
import { lutasDoResultado } from "../src/lutaPocTela.ts";
import { CHAVE, lerSave, textoSaveGrupo, type Armazenamento } from "../src/save.ts";
import { passoDe } from "../src/telas/lutar/palcoPoc/visualPoc.ts";
import { SEMENTES_ALTA, gabaritoAlta, gravarAlta, reproduzirAlta, viverAlta, type VidaAlta } from "./lp6_4_luta_alta.ts";

describe("a versao e a tabela (LP6-4)", () => {
  test("a v29 e do grupo, com o sono que segura, luta pela LUTA_V29, e o grupo de hoje e ela; a v26 a v28 seguem na LUTA_V23", () => {
    expect(VERSAO_GRUPO).toBe(37);   // a v37 (a v36 com a CO6 e a CO7) desde a CO7c;   // a v31 desde a BB2 (a v29 com o lance); a v36 (a v31 com a TV no jogo) desde a TV no jogo
    expect(ehLutaLp6(36)).toBe(true);
    expect(VERSAO_PET).toBe(35);   // o ovo de um pet so: a v32 (a v27 com a TV, sem o lance; D-BB2-6), na luta da v23
    expect([ehDoGrupo(VERSAO_V29), nasceComSonoSegura(VERSAO_V29)]).toEqual([true, true]);
    expect([ehLutaLp6(VERSAO_V26), ehLutaLp6(VERSAO_V27), ehLutaLp6(VERSAO_V28), ehLutaLp6(VERSAO_V29)]).toEqual([false, false, false, true]);
    expect(tabelaLuta(VERSAO_V29)).toBe(LUTA_V29);
    for (const v of [23, 24, 25, 26, 27, 28]) expect(tabelaLuta(v)).toBe(LUTA_V23);
    expect(LUTA_V23.apoio).toBeUndefined(); expect(LUTA_V23.arenaPorEstagio).toBeUndefined();
  });
  test("a LUTA_V29 e a LUTA_V23 com o apoio e a arena do lp6_3_u120, e o lp6_3_u120 e o lp5_3 (a v23) com as duas chaves", () => {
    const { apoio, arenaPorEstagio, versao, ...resto } = LUTA_V29, { versao: _v, ...resto23 } = LUTA_V23;
    expect(versao).toBe(29);
    expect(resto).toEqual(resto23);
    expect(apoio).toEqual({ dano: .6, recarga: 3, longeMs: 1500, desde: "Ultimate" });
    expect(apoio).not.toHaveProperty("recua");
    expect(arenaPorEstagio).toEqual({ Ultimate: 1.2, Mega: 1.4 });
    expect([apoio, arenaPorEstagio]).toEqual([APOIO_LP6_3, ARENA_POR_ESTAGIO_LP6_3]);
    expect(extrasLp6(LP6_3_U120)).toEqual({ apoio: { ...APOIO_LP6_3 }, arenaPorEstagio: { ...ARENA_POR_ESTAGIO_LP6_3 } });
    const { apoio: _a, arena: _r, nome: _n, ...c } = LP6_3_U120, { apoio: _a3, arena: _r3, nome: _n3, ...c3 } = LP5_3;
    expect(c).toEqual(c3);
  });
  test("os grupos v26 e v28 de antes seguem abrindo pelo save, com a versao deles", () => {
    const dados: Record<string, string> = {};
    const a: Armazenamento = { getItem: k => (k in dados ? dados[k]! : null), setItem(k, v) { dados[k] = v; } };
    for (const versao of [VERSAO_V26, VERSAO_V28]) {
      const g = new GrupoDoJogo(101, versao);
      for (const i of g.ids) g.agir(i, m => m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true }));
      for (let k = 0; k < 8; k++) g.avancar(15);
      dados[CHAVE] = textoSaveGrupo(g, "A");
      const l = lerSave(a);
      if (l.tipo !== "ok") throw new Error(JSON.stringify(l));
      expect(l.grupo!.versao).toBe(versao);
      expect(l.grupo!.assinatura()).toBe(g.assinatura());
    }
  });
});

describe("a vida do grupo v29 contra a do v28 (a mesma semente)", () => {
  const s = SEMENTES_ALTA[0], a = viverAlta(s, VERSAO_V28), b = viverAlta(s, VERSAO_V29);
  test("ate a primeira luta no Ultimate, as lutas sao as mesmas; depois, a luta muda", () => {
    const i = a.res.findIndex(r => r.startsWith("adulto:"));
    expect(i).toBeGreaterThan(0);
    expect(b.res.findIndex(r => r.startsWith("adulto:"))).toBe(i);
    expect(b.res.slice(0, i)).toEqual(a.res.slice(0, i));
    expect(b.res.slice(i)).not.toEqual(a.res.slice(i));
  });
  test("so a luta muda: a v29 e a v28 tem o mesmo registro ate o Ultimate", () => {
    expect(b.v.m.versao).toBe(VERSAO_V29);
    const la = a.v.log() as unknown[][], lb = b.v.log() as unknown[][];
    const tUlt = b.v.m.evolucoes.find(e => e.estagio === "adulto")!.tick;
    const antes = (l: unknown[][]) => l.filter(e => (e[0] as number) < tUlt);
    expect(antes(lb)).toEqual(antes(la));
  });
  test("o palco refaz as lutas do Mega da v29 com o apoio e a arena da tabela, e acabam como no motor", () => {
    const m = b.v.m;
    expect(m.estagioAtual).toBe("mega");
    for (const [k, mapa] of (["campo", "praia", "deserto"] as const).entries()) {
      const r = b.v.agir(x => x.lutarPoc(x.rivaisArenaPoc()[k]!, 9100 + k, mapa));
      expect(r.apoio).toBe(LUTA_V29.apoio); expect(r.arenaPorEstagio).toBe(LUTA_V29.arenaPorEstagio);
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

const gab = JSON.parse(readFileSync(new URL(gabaritoAlta(VERSAO_V29), import.meta.url), "utf8")) as { vidas: VidaAlta[] };
describe("a vida alta da v29: o gabarito e o replay bit a bit", () => {
  for (const s of SEMENTES_ALTA) {
    test(`v29 @${s}`, () => {
      const x = viverAlta(s, VERSAO_V29), g = gravarAlta(s, x);
      expect(g).toEqual(gab.vidas.find(y => y.semente === s));
      expect(g.estagio).toBe("mega");
      expect(reproduzirAlta(x)).toBe(g.assinatura);
    });
  }
});
