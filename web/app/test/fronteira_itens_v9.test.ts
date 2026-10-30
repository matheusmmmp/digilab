/* Rodada de equilibrio geral, fase 3 (docs/EQUILIBRIO_GERAL.md, metas M-C1 a M-C3, M-D1 a M-D3 e M-E1): o fim de jogo e os itens dos pets
   v9, separados por versao. A Liga (fator por lider, cura entre as lutas medida e nao adotada), a Fabrica (regras por tentativa, no evento
   do Tamer: as tentativas gravadas se refazem iguais), o Salao (fator por nivel) e os itens (a trava do treino minimo, a carta so contra NPC,
   o chip de regra no fim da lista, o chip de stat pela metade) valem so nos v9 em diante (hoje so o v13 existe: os casos dos v6-v8 e da
   Fabrica de antes sairam com o combate por turnos, COMBATE-TR R3). */
import { afterAll, beforeAll, describe, expect, test } from "vitest";
import {
  ALUGUEIS_FABRICA, CESC_V9, CIT, CIT_V9, CTR, CV21E, CV21E_TR, DUR_EVO, ESTAGIOS_SALAO, FATOR_INSTALACAO, FATOR_LIGA, FATOR_LIGA_V9,
  FATOR_RIVAL_FABRICA_V9, FATOR_SALAO, FATOR_SALAO_V9, LIGA, LUGARES_V6, MEDALHAS, Motor, STATS, TentativaFabrica,
  VERSAO_FABRICA_TR, CURA_LIGA_V9, bonusChipsStat, chaveRegra, chipDe, curaLiga, fatorLiga, fatorSalao, gambitsAdulto, hashSemente,
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
  const t = new Tamer(), m = new Motor(1);
  for (const md of MEDALHAS) t.ganhar(md.id, m, 1);
  t.ganharTitulo(m, 2);
  return t;
}

describe("a Liga dos v9: fator por lider, sem cura", () => {
  test("o fator e a cura vem das regras da luta: V21E (pets v9 em diante) com FATOR_LIGA_V9", () => {
    LIGA.forEach((x, i) => {
      expect(fatorLiga(i, CV21E)).toBe(FATOR_LIGA_V9[x.arena]);
      expect(fatorLiga(i, CV21E_TR)).toBe(FATOR_LIGA_V9[x.arena]);
      expect(lutadorLiga(i, CV21E_TR).cond.escala).toBeCloseTo(CESC_V9.vida.mega * FATOR_LIGA_V9[x.arena], 9);
      expect(lutadorLiga(i, CV21E_TR, FATOR_LIGA).cond.escala).toBe(CESC_V9.vida.mega * FATOR_LIGA);
    });
    expect(curaLiga(CV21E_TR)).toBe(CURA_LIGA_V9);
    /* pelo motor do pet: o v13 luta contra os lideres com os fatores dos v9 */
    const l13 = new Motor(3).lutadores("liga").lideres!;
    LIGA.forEach((x, i) => expect(l13[i].cond.escala).toBeCloseTo(CESC_V9.vida.mega * FATOR_LIGA_V9[x.arena], 9));
  });
  test("jogarLiga sem cura e a serie de sempre; com cura o pet comeca a luta seguinte com a vida do fim mais a cura", () => {
    const A = lutadorLiga(5, CV21E_TR, 3);   /* um Mega forte no lado A: vence algumas lutas seguidas */
    const Ls = lutadoresLiga(CV21E_TR, 0.2);
    for (let s = 0; s < 30; s++) expect(jogarLiga(A, s, CV21E_TR, 1, Ls)).toEqual(jogarSerie(A, Ls, s, CV21E_TR, 1, null));
    /* uma semente com duas lutas: a segunda comeca com min(max, vida do fim + 0,3 x max) */
    let feito = false;
    for (let s = 0; s < 200 && !feito; s++) {
      const r = jogarLiga(A, s, CV21E_TR, 1, Ls, 0.3);
      if (r.length < 2) continue;
      const fim = r[0].E.L[0], ini = r[1].E0.L[0];
      expect(ini.hp).toBeCloseTo(Math.min(fim.hpMax, fim.hp + 0.3 * fim.hpMax), 9);
      expect(ini.guts).toBe(Math.min(fim.guts, ini.gutsMax));
      feito = true;
    }
    expect(feito).toBe(true);
    expect(() => jogarSequencia(A, () => Ls[0], 2, 1, CV21E_TR, 1, null, 1.5)).toThrow(/cura/);
  });
  test("a Torre de Batalha e o Palacio seguem com o fator de sempre (M-E1 passou sem mudar)", () => {
    for (const R of [CV21E, CV21E_TR]) expect(rivalInstalacao(77, 0, R).cond.escala).toBe(CESC_V9.vida.mega * FATOR_INSTALACAO);
  });
});

describe("o Salao dos v9: fator por nivel", () => {
  test("V21E (pets v9 em diante) com FATOR_SALAO_V9", () => {
    for (const est of ESTAGIOS_SALAO) {
      expect(fatorSalao(est, CV21E)).toBe(FATOR_SALAO_V9[est]);
      expect(fatorSalao(est, CV21E_TR)).toBe(FATOR_SALAO_V9[est]);
      expect(rivalSalao(11, est, CV21E_TR).cond.escala).toBeCloseTo(CESC_V9.vida[est] * FATOR_SALAO_V9[est], 9);
      expect(rivalSalao(11, est, CV21E_TR, FATOR_SALAO).cond.escala).toBeCloseTo(CESC_V9.vida[est] * FATOR_SALAO, 9);
    }
  });
});

describe("a Fabrica: as regras vao na tentativa", () => {
  test("as regras da Fabrica (so a v13); as versoes de antes e desconhecidas falham alto", () => {
    expect(regraFabrica(VERSAO_FABRICA_TR)).toMatchObject({ versao: 13, R: CV21E_TR, fatorRival: FATOR_RIVAL_FABRICA_V9, trocaInteira: true });
    for (const v of [6, 7, 9]) expect(() => regraFabrica(v)).toThrow(/desconhecida/);
  });
  test("na tentativa o rival tem o fator dos v9 e o alugado nao", () => {
    const x = new TentativaFabrica(3, 0), { A, B } = x.lutadores();
    expect(x.regra.versao).toBe(VERSAO_FABRICA_TR);
    expect(A.cond.escala).toBe(CESC_V9.vida.mega);
    expect(B.cond.escala).toBeCloseTo(CESC_V9.vida.mega * FATOR_RIVAL_FABRICA_V9, 9);
    expect(A.estilo.gambits).toEqual(gambitsAdulto(x.alugado.adulta as never, CV21E_TR));
  });
  test("a troca entra com a vida cheia", () => {
    const acha = () => {
      for (let n = 1; n < 300; n++) for (let e = 0; e < ALUGUEIS_FABRICA; e++) {
        const x = new TentativaFabrica(n, e), l = x.lutar(x.proxima()!.s);
        if (l.venceu && l.vidaFim < 0.99) return x;
      }
      throw new Error("nenhuma tentativa com vitoria gasta");
    };
    const x = acha();
    x.trocar();
    expect(x.vidaAgora).toBe(1);
    expect(x.lutadores().ini).toBeNull();
  });
  test("o Tamer grava v: 13 nas tentativas novas (a luta em tempo real); a antiga (sem v ou v 9) nao se refaz mais; v desconhecida falha", () => {
    const t = campeao(), base = t.log.slice();
    const antiga: EventoTamer[] = [...base, ["fabrica", { n: 1, s: sementeFabrica(1), alugado: 1, quando: 3 }]];
    expect(() => Tamer.reproduzir(antiga)).toThrow(/antes do combate em tempo real/);
    expect(() => Tamer.reproduzir([...base, ["fabrica", { n: 1, s: sementeFabrica(1), alugado: 1, quando: 3, v: 9 }]])).toThrow(/versão 9/);
    const t1 = Tamer.reproduzir(base);
    t1.alugarFabrica(1, 3);
    const ev = t1.log[t1.log.length - 1] as ["fabrica", { v?: number }];
    expect(ev[0]).toBe("fabrica");
    expect(ev[1].v).toBe(VERSAO_FABRICA_TR);
    expect(t1.fabrica[0].regra.versao).toBe(VERSAO_FABRICA_TR);
    expect(t1.fabrica[0].regra.R?.tempoReal).toBe(true);
    const ref = new TentativaFabrica(1, 1);
    while (t1.fabricaAtual) { const p = t1.fabricaAtual.proxima()!; t1.lutarFabrica(4); expect(p.s).toBe(ref.proxima()!.s); ref.lutar(p.s); }
    expect(t1.fabrica[0].lutas.map(l => [l.venceu, l.vidaFim])).toEqual(ref.lutas.map(l => [l.venceu, l.vidaFim]));
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
    const m = new Motor(9101);
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
    expect(Motor.reproduzir(m.semente, m.log).assinatura()).toBe(m.assinatura());
    /* a carta: nao na arena contra bots; contra NPC, com o treino minimo */
    expect(m.porqueSemCartaV9("aleatorio")).toMatch(/campanha/);
    expect(() => m.lutar("aleatorio", 1, "carta_folego")).toThrow(/campanha/);
    expect(m.porqueSemCartaV9(npc)).toBeNull();
    /* o replay falha com a carta antes de uma luta contra bot */
    const log = [...m.log, [m.e.tick, "k", { id: "carta_folego" }], [m.e.tick, "l", { r: "aleatorio", s: 1 }]] as typeof m.log;
    expect(() => Motor.reproduzir(m.semente, log)).toThrow(/campanha/);
  });
});
