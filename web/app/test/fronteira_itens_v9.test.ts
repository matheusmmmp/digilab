/* Rodada de equilibrio geral, fase 3 (docs/EQUILIBRIO_GERAL.md, metas M-C1 a M-C3, M-D1 a M-D3 e M-E1): o fim de jogo e os itens dos pets
   v9, separados por versao. A Liga (fator por lider, cura entre as lutas medida e nao adotada), a Fabrica (regras por tentativa, no evento
   do Tamer: as tentativas gravadas se refazem iguais), o Salao (fator por nivel) e os itens (a trava do treino minimo, a carta so contra NPC,
   o chip de regra no fim da lista, o chip de stat pela metade) valem so nos v9; os pets v6-v8 e as tentativas antigas nao mudam. */
import { afterAll, beforeAll, describe, expect, test } from "vitest";
import {
  ALUGUEIS_FABRICA, CESC_V6, CIT, CIT_V9, CTR, CV21D, CV21E, DUR_EVO, ESTAGIOS_SALAO, FATOR_INSTALACAO, FATOR_LIGA, FATOR_LIGA_V9,
  FATOR_RIVAL_FABRICA_V9, FATOR_SALAO, FATOR_SALAO_V9, LIGA, LUGARES_V6, MEDALHAS, Motor, STATS, TentativaFabrica, VERSAO_FABRICA,
  VERSAO_FABRICA_V9, CURA_LIGA_V9, bonusChipsStat, chaveRegra, chipDe, curaLiga, fatorLiga, fatorSalao, gambitsAdulto, hashSemente,
  itensValem, jogarLiga, jogarSequencia, jogarSerie, listaComChips, lutadorLiga, lutadoresLiga, lutadorPet, regraFabrica, rivalInstalacao,
  rivalSalao, sementeFabrica, type Stats,
} from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";
import { Tamer, type EventoTamer } from "../src/tamer.ts";

const escalaAntes = ESCALA.ligada;
beforeAll(() => ligarEscala(true));
afterAll(() => ligarEscala(escalaAntes));
const zeros = (): Stats => Object.fromEntries(STATS.map(k => [k, 0])) as Stats;
/** um Tamer campeao, com as 6 medalhas */
function campeao(): Tamer {
  const t = new Tamer(), m = new Motor(1, 6);
  for (const md of MEDALHAS) t.ganhar(md.id, m, 1);
  t.ganharTitulo(m, 2);
  return t;
}

describe("a Liga dos v9: fator por lider, sem cura; os v6-v8 como antes", () => {
  test("o fator e a cura vem das regras da luta: V21E (pets v9) com FATOR_LIGA_V9, V21D com FATOR_LIGA e sem cura", () => {
    LIGA.forEach((x, i) => {
      expect(fatorLiga(i, CV21D)).toBe(FATOR_LIGA);
      expect(fatorLiga(i, CV21E)).toBe(FATOR_LIGA_V9[x.arena]);
      expect(lutadorLiga(i, CV21D).cond.escala).toBe(CESC_V6.vida.mega * FATOR_LIGA);
      expect(lutadorLiga(i, CV21E).cond.escala).toBeCloseTo(CESC_V6.vida.mega * FATOR_LIGA_V9[x.arena], 9);
    });
    expect(curaLiga(CV21D)).toBe(0);
    expect(curaLiga(CV21E)).toBe(CURA_LIGA_V9);
    /* pelo motor do pet: o v8 luta contra os lideres de antes, o v9 com os fatores dos v9 */
    const l8 = new Motor(3, 8).lutadores("liga").lideres!, l9 = new Motor(3, 9).lutadores("liga").lideres!;
    LIGA.forEach((x, i) => {
      expect(l8[i].cond.escala).toBe(CESC_V6.vida.mega);
      expect(l9[i].cond.escala).toBeCloseTo(CESC_V6.vida.mega * FATOR_LIGA_V9[x.arena], 9);
    });
  });
  test("jogarLiga sem cura e a serie de sempre; com cura o pet comeca a luta seguinte com a vida do fim mais a cura", () => {
    const A = lutadorLiga(5, CV21D, 3);   /* um Mega forte no lado A: vence algumas lutas seguidas */
    const Ls = lutadoresLiga(CV21D, 0.2);
    for (let s = 0; s < 30; s++) expect(jogarLiga(A, s, CV21D, 1, Ls)).toEqual(jogarSerie(A, Ls, s, CV21D, 1, null));
    /* uma semente com duas lutas: a segunda comeca com min(max, vida do fim + 0,3 x max) */
    let feito = false;
    for (let s = 0; s < 200 && !feito; s++) {
      const r = jogarLiga(A, s, CV21D, 1, Ls, 0.3);
      if (r.length < 2) continue;
      const fim = r[0].E.L[0], ini = r[1].E0.L[0];
      expect(ini.hp).toBeCloseTo(Math.min(fim.hpMax, fim.hp + 0.3 * fim.hpMax), 9);
      expect(ini.guts).toBe(Math.min(fim.guts, ini.gutsMax));
      feito = true;
    }
    expect(feito).toBe(true);
    expect(() => jogarSequencia(A, () => Ls[0], 2, 1, CV21D, 1, null, 1.5)).toThrow(/cura/);
  });
  test("a Torre de Batalha e o Palacio seguem com o fator de antes (M-E1 passou sem mudar)", () => {
    for (const R of [CV21D, CV21E]) expect(rivalInstalacao(77, 0, R).cond.escala).toBe(CESC_V6.vida.mega * FATOR_INSTALACAO);
  });
});

describe("o Salao dos v9: fator por nivel", () => {
  test("V21E (pets v9) com FATOR_SALAO_V9; V21D com FATOR_SALAO", () => {
    for (const est of ESTAGIOS_SALAO) {
      expect(fatorSalao(est, CV21D)).toBe(FATOR_SALAO);
      expect(fatorSalao(est, CV21E)).toBe(FATOR_SALAO_V9[est]);
      expect(rivalSalao(11, est, CV21D).cond.escala).toBeCloseTo(CESC_V6.vida[est] * FATOR_SALAO, 9);
      expect(rivalSalao(11, est, CV21E).cond.escala).toBeCloseTo(CESC_V6.vida[est] * FATOR_SALAO_V9[est], 9);
    }
  });
});

describe("a Fabrica dos v9: as regras vao na tentativa", () => {
  test("as regras de cada versao; versao desconhecida falha alto", () => {
    expect(regraFabrica(VERSAO_FABRICA)).toMatchObject({ versao: 6, R: CV21D, fatorRival: 1, trocaInteira: false });
    expect(regraFabrica(VERSAO_FABRICA_V9)).toMatchObject({ versao: 9, R: CV21E, fatorRival: FATOR_RIVAL_FABRICA_V9, trocaInteira: true });
    expect(() => regraFabrica(7)).toThrow(/desconhecida/);
  });
  test("sem versao a tentativa e a de antes; na dos v9 o rival tem o fator dos v9 e o alugado nao", () => {
    for (let n = 1; n <= 5; n++) for (let e = 0; e < ALUGUEIS_FABRICA; e++) {
      const a = new TentativaFabrica(n, e), b = new TentativaFabrica(n, e, VERSAO_FABRICA);
      while (!a.acabou) { a.lutar(a.proxima()!.s); b.lutar(b.proxima()!.s); }
      expect(b.lutas.map(l => [l.s, l.venceu, l.res.turnos.length, l.vidaFim])).toEqual(a.lutas.map(l => [l.s, l.venceu, l.res.turnos.length, l.vidaFim]));
    }
    const x = new TentativaFabrica(3, 0, VERSAO_FABRICA_V9), { A, B } = x.lutadores();
    expect(A.cond.escala).toBe(CESC_V6.vida.mega);
    expect(B.cond.escala).toBeCloseTo(CESC_V6.vida.mega * FATOR_RIVAL_FABRICA_V9, 9);
    expect(A.estilo.gambits).toEqual(gambitsAdulto(x.alugado.adulta as never, CV21E));
  });
  test("na dos v9 a troca entra com a vida cheia; na de antes, com a mesma fracao", () => {
    const acha = (v: number) => {
      for (let n = 1; n < 300; n++) for (let e = 0; e < ALUGUEIS_FABRICA; e++) {
        const x = new TentativaFabrica(n, e, v), l = x.lutar(x.proxima()!.s);
        if (l.venceu && l.vidaFim < 0.99) return x;
      }
      throw new Error("nenhuma tentativa com vitoria gasta");
    };
    const x9 = acha(VERSAO_FABRICA_V9);
    x9.trocar();
    expect(x9.vidaAgora).toBe(1);
    expect(x9.lutadores().ini).toBeNull();
    const x6 = acha(VERSAO_FABRICA), vida = x6.lutas[0].vidaFim;
    x6.trocar();
    expect(x6.vidaAgora).toBeCloseTo(vida, 9);
  });
  test("o Tamer grava v: 9 nas tentativas novas; a antiga (sem v) se refaz com as regras de antes; v desconhecida falha", () => {
    const t = campeao(), base = t.log.slice();
    const antiga: EventoTamer[] = [...base, ["fabrica", { n: 1, s: sementeFabrica(1), alugado: 1, quando: 3 }]];
    const t1 = Tamer.reproduzir(antiga);
    expect(t1.fabrica[0].regra.versao).toBe(VERSAO_FABRICA);
    const ref = new TentativaFabrica(1, 1);
    while (t1.fabricaAtual) { const p = t1.fabricaAtual.proxima()!; t1.lutarFabrica(4); expect(p.s).toBe(ref.proxima()!.s); ref.lutar(p.s); }
    expect(t1.fabrica[0].lutas.map(l => [l.venceu, l.vidaFim])).toEqual(ref.lutas.map(l => [l.venceu, l.vidaFim]));
    /* a seguinte e nova: grava a versao dos v9, e o registro inteiro se refaz igual */
    t1.alugarFabrica(0, 5);
    const ev = t1.log[t1.log.length - 1] as ["fabrica", { v?: number }];
    expect(ev[0]).toBe("fabrica");
    expect(ev[1].v).toBe(VERSAO_FABRICA_V9);
    expect(t1.fabrica[1].regra.versao).toBe(VERSAO_FABRICA_V9);
    while (t1.fabricaAtual) t1.lutarFabrica(6);
    const r = Tamer.reproduzir(t1.log);
    expect(r.fabrica.map(x => [x.regra.versao, x.lutas.map(l => [l.s, l.venceu, l.vidaFim])])).toEqual(t1.fabrica.map(x => [x.regra.versao, x.lutas.map(l => [l.s, l.venceu, l.vidaFim])]));
    expect(() => Tamer.reproduzir([...base, ["fabrica", { n: 1, s: sementeFabrica(1), alugado: 0, quando: 3, v: 7 }]])).toThrow(/versão 7/);
  });
});

describe("os itens dos v9", () => {
  test("a trava do treino minimo so nos v9; o chip de stat vale a metade so nos v9", () => {
    for (const est of ["crianca", "adolescente", "adulto", "mega"] as const) {
      const lim = CIT_V9.treinoMinimo * CIT.tipico[est]!;
      for (const v of [6, 7, 8]) expect(itensValem(v, est, 0)).toBe(true);
      expect(itensValem(9, est, 0)).toBe(false);
      expect(itensValem(9, est, lim - 0.5)).toBe(false);
      expect(itensValem(9, est, lim)).toBe(true);
    }
    expect(itensValem(9, "bebe", 100)).toBe(false);
    expect(bonusChipsStat(["chip_forca"], "adulto", zeros(), 0, 6)).toMatchObject({ forca: 1, vigor: 1 });
    expect(bonusChipsStat(["chip_forca"], "adulto", zeros(), 0, 9)).toMatchObject({ forca: CIT_V9.fatorChipStat, vigor: CIT_V9.fatorChipStat });
  });
  test("o chip de regra: no topo nos v6 (sai a ultima se a lista esta cheia); no fim nos v9, sem tirar nenhuma", () => {
    const g = gambitsAdulto("duelista", CV21E), cap = g.regras.length, rec = chipDe("chip_recuo") as { regra: Parameters<typeof chaveRegra>[0] };
    const v6 = listaComChips(g, ["chip_recuo"], cap, 6), v9 = listaComChips(g, ["chip_recuo"], cap, 9);
    expect(chaveRegra(v6.regras[0])).toBe(chaveRegra(rec.regra));
    expect(v6.regras.length).toBe(cap);
    expect(v9.regras.slice(0, cap)).toEqual(g.regras);
    expect(chaveRegra(v9.regras[cap])).toBe(chaveRegra(rec.regra));
    expect(v9.final).toBe(g.final);
  });
  test("no pet v9: o chip de regra fica fora da lista e entra no fim da lista de luta so com o treino minimo; o de stat idem", { timeout: 60000 }, () => {
    const m = new Motor(9101, 9);
    m.liberar(6);
    m.avancar(DUR_EVO.bebe + 15);
    expect(m.estagioAtual).toBe("crianca");
    /* Rookie: treino minimo 4 (metade de 8) */
    m.equipar("chip_forca");
    expect(m.itensValem).toBe(false);
    expect(m.porqueItensNaoValem()).toMatch(/pedem treino/);
    expect(m.pontosDeLuta()).toBeNull();
    const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"] as const;
    const treinarAte = (alvo: number): void => {
      for (let k = 0; k < 600 && m.treino.total < alvo; k++) {
        if (m.treino.fadiga < CTR.fadigaSessao && m.treino.podeTocar(m.e.tick)) { try { m.treinar(EX[k % EX.length]); continue; } catch { /* dormindo */ } }
        m.avancar(30);
      }
    };
    treinarAte(CIT_V9.treinoMinimo * CIT.tipico.crianca!);
    expect(m.estagioAtual).toBe("crianca");
    expect(m.itensValem).toBe(true);
    const b = m.pontosDeLuta()!;
    expect(STATS.reduce((a, k) => a + b[k] - m.treino.pontos[k], 0)).toBeCloseTo(2 * CIT_V9.fatorChipStat, 9);
    /* Champion: o minimo sobe para 11; o chip Recuo nao entra na lista (ativas) */
    for (let j = 0; j < 200 && m.estagioAtual === "crianca"; j++) m.avancar(30);
    expect(m.estagioAtual).toBe("adolescente");
    m.equipar("chip_recuo");
    const k = chaveRegra((chipDe("chip_recuo") as { regra: Parameters<typeof chaveRegra>[0] }).regra);
    expect(m.gp!.ativas).not.toContain(k);
    expect(m.gp!.chipsRegra).toContain(k);
    const lista = () => lutadorPet(m, "p").estilo.gambits!.regras.map(chaveRegra);
    if (!m.itensValem) {
      expect(lista()).toEqual(m.gp!.ativas);
      treinarAte(CIT_V9.treinoMinimo * CIT.tipico.adolescente!);
    }
    expect(m.itensValem).toBe(true);
    expect(lista()).toEqual([...m.gp!.ativas, k]);
    const npc = LUGARES_V6[0].rivais[0];
    expect(m.lutadores(npc).usadas).toEqual([...m.gp!.ativas, k]);
    /* o replay refaz o pet igual */
    expect(Motor.reproduzir(m.semente, m.log, 9).assinatura()).toBe(m.assinatura());
    /* a carta: nao na arena contra bots; contra NPC, com o treino minimo */
    expect(m.porqueSemCartaV9("aleatorio")).toMatch(/campanha/);
    expect(() => m.lutar("aleatorio", 1, "carta_folego")).toThrow(/campanha/);
    expect(m.porqueSemCartaV9(npc)).toBeNull();
    /* o replay falha com a carta antes de uma luta contra bot */
    const log = [...m.log, [m.e.tick, "k", { id: "carta_folego" }], [m.e.tick, "l", { r: "aleatorio", s: 1 }]] as typeof m.log;
    expect(() => Motor.reproduzir(m.semente, log, 9)).toThrow(/campanha/);
  });
  test("nos v8 nada muda: o chip de regra entra no topo da lista, sem trava de treino", { timeout: 60000 }, () => {
    const m = new Motor(9101, 8);
    m.liberar(6);
    m.avancar(DUR_EVO.bebe + 15);
    for (let j = 0; j < 200 && m.estagioAtual === "crianca"; j++) m.avancar(30);
    expect(m.estagioAtual).toBe("adolescente");
    expect(m.itensValem).toBe(true);
    expect(m.porqueSemCartaV9("aleatorio")).toBeNull();
    m.equipar("chip_recuo");
    const k = chaveRegra((chipDe("chip_recuo") as { regra: Parameters<typeof chaveRegra>[0] }).regra);
    expect(m.gp!.ativas[0]).toBe(k);
    expect(m.gp!.chipsNoFim).toBe(false);
  });
});
