/* Correcao do vigia V21D (pets v6, so no jogo): as duas regras novas do vigia (bots.REGRA_BATE_EM_QUEM_RECUA e
   REGRA_RECUA_DO_PREPARO_SOB_PELE) estao na semente do vigia v13, mas fora do repertorio de candidatas. Sem a correcao, a
   primeira troca que as tirasse da lista as tiraria para sempre. Agora elas voltam como candidatas de troca, so para a forma
   do vigia e so com as regras V21D (que o v13 tem, CV21E_TR); as outras formas tem as mesmas candidatas de antes. */
import { describe, expect, test } from "vitest";
import { CV21E_TR, LINHA_DA_FORMA } from "../motor/constantes.ts";
import { REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE } from "../motor/bots.ts";
import { GambitsPet, REPERTORIO, candidatasDoVigia, chaveRegra } from "../motor/gambits_pet.ts";
import type { ResultadoLuta } from "../motor/combate.ts";
import type { Forma, FormaAdultaNormal } from "../motor/tipos.ts";

const NOVAS = [REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE].map(chaveRegra);
const adulto = (f: FormaAdultaNormal, est: "adulto" | "mega" = "adulto"): Forma => ({ esp: "limo", est, ramo: "sereno", linha: LINHA_DA_FORMA[f], adulta: f });
function gp(f: Forma, R: typeof CV21E_TR): GambitsPet { const g = new GambitsPet(); g.semear(f, "x", R); return g; }

describe("candidatas de troca do vigia", () => {
  test("as duas regras novas estao fora do repertorio e na semente do vigia v13", () => {
    for (const k of NOVAS) expect(REPERTORIO.has(k)).toBe(false);
    expect(gp(adulto("vigia"), CV21E_TR).ativas).toEqual(expect.arrayContaining(NOVAS));
  });
  test("pet v13 vigia: a regra nova que saiu da lista volta como candidata", () => {
    const g = gp(adulto("vigia"), CV21E_TR);
    expect(g.candidatas().filter(k => NOVAS.includes(k))).toEqual([]);   /* as duas ja estao ativas */
    g.ativas = g.ativas.filter(k => !NOVAS.includes(k));
    expect(g.candidatas().slice(-2)).toEqual(NOVAS);                       /* no fim: a ordem do repertorio nao muda */
    g.vetos.push(NOVAS[0]);
    expect(g.candidatas()).not.toContain(NOVAS[0]);                        /* veto do dono vale */
  });
  test("o Mega vigia (v13) tambem as recebe", () => { expect(candidatasDoVigia(adulto("vigia", "mega"), CV21E_TR)).toEqual(NOVAS); });
  test("sem regras ou em outra forma: as candidatas sao so o repertorio", () => {
    expect(candidatasDoVigia(adulto("vigia"), null)).toEqual([]);
    for (const f of ["duelista", "muralha", "tita", "sentinela"] as FormaAdultaNormal[]) {
      expect(candidatasDoVigia(adulto(f), CV21E_TR)).toEqual([]);
      expect(gp(adulto(f), CV21E_TR).candidatas().every(k => REPERTORIO.has(k))).toBe(true);
    }
  });
  test("uma troca de verdade pode trazer a regra nova de volta", () => {
    /* luta falsa: nenhum turno, derrota; a pior regra livre fica abaixo do limiar e e trocada */
    const res = { E0: { L: [{ hpMax: 100 }] }, tr: { acoes: [] }, pontosA: 0 } as unknown as ResultadoLuta;
    const trouxe = (R: typeof CV21E_TR): boolean => {
      for (let s = 0; s < 400; s++) {
        const g = gp(adulto("vigia"), R);
        g.ativas = g.ativas.filter(k => !NOVAS.includes(k));
        for (const k of g.ativas) g.notas[k] = -1;
        g.aprender(res, s);
        if (g.ativas.some(k => NOVAS.includes(k))) return true;
      }
      return false;
    };
    expect(trouxe(CV21E_TR)).toBe(true);
  });
});
