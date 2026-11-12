// LUTA_POC, LP2 (docs/TAREFA_V3_LUTA_POC.md): o pet v21 luta no nucleo da POC. O mapeamento dos 6 stats (decisao 2), os rivais da Arena e da
// Campanha (decisoes 3 e 4), o mapa de cada lugar (LP-4), o que sai da v21 (decisao 6), os lugares fechados ate a LP2b, a ponte da luta, o
// replay bit a bit e o gabarito da vida nova (test/gabaritos/lp2_vidas_v21.json, por test/lp2_v21.ts --gravar).
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import {
  DIGIMON_DA_FORMA, PALACIO_NA_TORRE, FORMAS_ARENA, IDS_CENA, LUGARES_V6, LUTA_POC_LIGADA, MAPA_DO_LUGAR, MAPA_STATS, Motor, NPC, STATS,
  VERSAO_PET, VERSAO_PET_LAB, VERSAO_V21, VERSAO_V22, VERSAO_V23, VERSOES_PET, VERSOES_PET_POC, chaveSprite, formaDaChave, hashSemente, rivaisArena, statsDaLuta, statsDoPet, statsNpc,
  statsRivalArena, type EventoRegistro, type Stats,
} from "../motor/index.ts";
import { DIAS_V21, SEMENTES_V21, VARIANTES_V21, gravarV21, nascerV21, viverV21, type VidaV21 } from "./lp2_v21.ts";

const neutro = Object.fromEntries(STATS.map(k => [k, 10])) as Stats;

describe("a chave e a versao", () => {
  test("a chave ligou na LP4: os ovos de hoje nascem v21, e so a v21 abre", () => {
    expect(LUTA_POC_LIGADA).toBe(true);
    expect(VERSAO_PET).toBe(31);
    expect(VERSOES_PET).toEqual([VERSAO_V21, 22, 23, 24, 25, 26, 27, 28, 29, 31]);   // a v26: os dois pets (CO4c)
    expect(VERSOES_PET_POC).toEqual([21, 22, 23, 24, 25, 26, 27, 28, 29, 31]);
    for (const v of [13, 14, 15, 17, 18, 19]) expect(() => new Motor(101, v), `v${v}`).toThrow(/versão de pet desconhecida/);
    expect(new Motor(101, VERSAO_V21).versao).toBe(21);
    expect(() => new Motor(101, 20)).toThrow(/versão de pet desconhecida/);
  });
});

describe("o mapeamento dos stats (decisao 2, PROPOSTO)", () => {
  test("o pet neutro (10 em cada stat), adulto e com a condicao 1, recebe os STATS_PADRAO da POC", () => {
    expect(statsDaLuta(neutro, "adulto", 1)).toEqual({ hp: 900, atk: 100, def: 50, vel: 70, cad: 2000, hcd: 8, crit: 10, erro: 18, hpot: 2, esquiva: 0, atordoa: 0 });
    expect(MAPA_STATS.neutro).toBe(10);
  });
  test("cada numero escala na razao do stat (inversa no ciclo, na recarga e no erro); a vida leva o estagio e a condicao", () => {
    const d = (k: keyof Stats, v: number) => statsDaLuta({ ...neutro, [k]: v }, "adulto", 1);
    expect(d("vigor", 20).hp).toBe(1800);
    expect(d("forca", 20).atk).toBe(200);
    expect(d("guarda", 5).def).toBe(25);
    expect(d("folego", 20).vel).toBe(140);
    expect([d("recuperacao", 20).cad, d("recuperacao", 20).hcd]).toEqual([1000, 4]);
    expect([d("mira", 20).crit, d("mira", 20).erro]).toEqual([20, 9]);
    expect(statsDaLuta(neutro, "crianca", 1).hp).toBe(Math.round(900 * 0.6));
    expect(statsDaLuta(neutro, "adulto", 0.5).hp).toBe(450);
    expect(() => statsDaLuta({ ...neutro, mira: 0 }, "adulto", 1)).toThrow(/mira/);
  });
  test("o treino sobe os stats (o peso de combate de sempre), e a luta sobe com eles", () => {
    const f = formaDaChave("brasa_crianca_sereno"), sem = statsDoPet(f, null, null);
    const com = statsDoPet(f, null, { ...Object.fromEntries(STATS.map(k => [k, 0])), forca: 2 } as Stats);
    expect(com.forca).toBe(sem.forca + 6);
    expect(statsDaLuta(com, "crianca", 1).atk).toBeGreaterThan(statsDaLuta(sem, "crianca", 1).atk);
  });
});

describe("os rivais e os mapas (decisoes 3 e 4, LP-4)", () => {
  test("formaDaChave e o inverso do chaveSprite nas 60 formas", () => {
    for (const k of Object.keys(DIGIMON_DA_FORMA)) expect(chaveSprite(formaDaChave(k)), k).toBe(k);
  });
  test("os rivais da Arena sao as formas do estagio do pet, todos na tabela e com numeros", () => {
    for (const est of ["bebe", "crianca", "adolescente", "adulto", "mega"] as const) {
      const r = rivaisArena(est);
      expect(r.length, est).toBeGreaterThan(0);
      for (const k of r) { expect(k in FORMAS_ARENA).toBe(true); expect(statsRivalArena(k).hp).toBeGreaterThan(0); }
    }
    expect(rivaisArena("bebe")).toHaveLength(4);
  });
  test("os 10 NPCs da Campanha estao na tabela, com os numeros do perfilNPC no estagio do lugar", () => {
    const npcs = LUGARES_V6.flatMap(L => L.rivais);
    expect(npcs).toHaveLength(10);
    for (const k of npcs) {
      expect(FORMAS_ARENA[k].nome).toBe(NPC[k]!.nome);
      const v = NPC[k]!.total / 6;
      expect(statsNpc(k)).toEqual(statsDaLuta(Object.fromEntries(STATS.map(s => [s, v])) as Stats, NPC[k]!.est, 1));
    }
  });
  test("cada lugar da Campanha tem o mapa fixo da LP-4", () => {
    expect(LUGARES_V6.map(L => MAPA_DO_LUGAR[L.nome])).toEqual(["campo", "coliseu", "floresta", "castelo", "praia", "caverna"]);
    for (const m of Object.values(MAPA_DO_LUGAR)) expect(IDS_CENA).toContain(m);
  });
});

/** um pet v21 que ja e Rookie (a vida do gabarito ate a primeira luta) */
function rookie(semente = 101): Motor {
  const m = nascerV21("v21_modular", semente);
  for (let p = 0; m.estagioAtual === "bebe" && p < 2000; p++) { m.avancar(30); if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, m.mundo!.pet[0] + 24)), m.mundo!.pet[1]); if (m.e.sujeira >= 2) m.observar("limpar"); }
  expect(m.estagioAtual).toBe("crianca");
  return m;
}

describe("a luta do pet v21", () => {
  test("a luta entra no registro com o rival, a semente e o mapa; conta como as de sempre", () => {
    const m = rookie(), rival = m.rivaisArenaPoc()[0];
    const R = m.lutarPoc(rival, 4242, "floresta");
    expect(m.log.at(-1)).toEqual([m.e.tick, "l", { r: rival, s: 4242, m: "floresta" }]);
    expect(R.serie).toHaveLength(1);
    expect(R.pet).toEqual(m.statsLutaPoc());
    expect(m.lutas.lutas).toBe(1);
    expect(R.serie[0].fim).toBe(true);
  });
  test("a entrada falha alto: rival de outro estagio, mapa desconhecido, NPC fora do mapa do lugar ou com o desafio fechado", () => {
    const m = rookie();
    expect(() => m.lutarPoc("brasa_adolescente_brigao", 1, "campo")).toThrow(/estágio/);
    expect(() => m.lutarPoc(m.rivaisArenaPoc()[0], 1, "lua" as never)).toThrow(/mapa/);
    expect(() => m.lutarPoc(m.lugares[0].rivais[0], 1, "ringue")).toThrow(/mapa do lugar/);
    expect(() => m.lutarPoc(m.lugares[1].rivais[0], 1, "coliseu")).toThrow(/bloqueado/);
    expect(() => m.lutarPoc("agressivo", 1, "campo")).toThrow(/rival desconhecido/);
  });
  test("sai da v21: o combate de antes, os gambits, as cartas e os chips de regra; os torneios pedem as entradas de sempre (LP2b) e o Palacio foi para a Torre", () => {
    const m = rookie();
    /* o combate por turnos saiu do motor na LP4: nada de gp, lutar, montarLuta nem intervirGambit */
    for (const k of ["gp", "lutar", "montarLuta", "intervirGambit", "regras", "carta"]) expect(k in m, k).toBe(false);
    expect(m.porqueNaoLiga()).toMatch(/6 medalhas/);
    expect(m.porqueNaoSalao()).toMatch(/título da Liga/);
    expect(m.porqueNaoInstalacao("torre_batalha")).toMatch(/título da Liga/);
    expect(m.porqueNaoInstalacao("palacio")).toBe(PALACIO_NA_TORRE);
    m.liberar(1);   /* a primeira medalha abre a primeira vaga de chip */
    expect(m.porqueNaoEquipa("chip_recuo")).toMatch(/chip de regra/);
    expect(() => m.equipar("chip_recuo")).toThrow(/chip de regra/);
    const log: EventoRegistro[] = [...m.log, [m.e.tick, "g", { op: "travar", k: "x" }]];
    expect(() => Motor.reproduzir(101, log, VERSAO_V21)).toThrow(/evento "g"/);
    const log2 = [...m.log, [m.e.tick, "k", { id: "x" }]] as EventoRegistro[];
    expect(() => Motor.reproduzir(101, log2, VERSAO_V21)).toThrow(/evento "k"/);
    /* um "l" sem mapa de um rival de antes (o bot do combate por turnos) tambem nao refaz */
    const log3 = [...m.log, [m.e.tick, "l", { r: "aleatorio", s: 1 }]] as EventoRegistro[];
    expect(() => Motor.reproduzir(101, log3, VERSAO_V21)).toThrow(/sem poder/);
  });
  test("o pet de teste (v16) nao luta (LP4)", () => {
    const m = new Motor(101, VERSAO_PET_LAB);
    expect(m.porqueNaoLutaPoc("x", "campo")).toMatch(/pet de teste/);
  });
  test("a ponte da luta le o resultado novo: com ela, as lutas chegam ao corpo e ao cerebro (a vida muda)", () => {
    const com = viverV21("v21_modular", 202, 3, true), sem = viverV21("v21_modular", 202, 3, false);
    expect(com.m.lutas.lutas).toBeGreaterThan(0);
    expect(com.m.assinatura()).not.toBe(sem.m.assinatura());
  });
});

const gab = JSON.parse(readFileSync(new URL("./gabaritos/lp2_vidas_v21.json", import.meta.url), "utf8")) as
  { versao: number; dias: number; sementes: number[]; variantes: string[]; vidas: VidaV21[] };
describe("a vida nova: o gabarito e o replay bit a bit", () => {
  test("a forma do gabarito: as 2 variantes x as 5 sementes, todas com lutas", () => {
    expect([gab.versao, gab.dias]).toEqual([1, DIAS_V21]);
    expect(gab.sementes).toEqual([...SEMENTES_V21]);
    expect(gab.variantes).toEqual([...VARIANTES_V21]);
    expect(gab.vidas.every(v => v.lutas > 0)).toBe(true);
  });
  for (const v of VARIANTES_V21) for (const s of SEMENTES_V21) {
    test(`${v} @${s}: a vida sai igual ao gabarito, e o replay do registro da a mesma assinatura`, () => {
      const g = gab.vidas.find(x => x.variante === v && x.semente === s)!;
      const { m, log, res } = viverV21(v, s);
      expect(gravarV21(v, s, m, log, res)).toEqual(g);
      const r = Motor.reproduzir(s, log, VERSAO_V21);
      expect(r.assinatura()).toBe(m.assinatura());
      expect(JSON.stringify(r.log)).toBe(JSON.stringify(log));
    });
  }
  test("outra semente de luta, outra luta (a semente vai ao nucleo)", () => {
    const a = rookie(303), b = rookie(303), rv = a.rivaisArenaPoc()[1];
    const ra = a.lutarPoc(rv, hashSemente("x", 1), "campo"), rb = b.lutarPoc(rv, hashSemente("x", 2), "campo");
    expect(ra.serie[0].relogio === rb.serie[0].relogio && ra.serie[0].vidaA === rb.serie[0].vidaA).toBe(false);
  });
});

/* LUTA_POC, LP5-5: o gabarito da v22, gravado antes da v23 entrar (a regra da mecanica nova): a v22 sai byte a byte */
const gab22 = JSON.parse(readFileSync(new URL("./gabaritos/lp2_vidas_v22.json", import.meta.url), "utf8")) as typeof gab;
describe("a vida da v22 (LP5-5): o gabarito e o replay bit a bit", () => {
  for (const v of VARIANTES_V21) for (const s of SEMENTES_V21) {
    test(`v22 ${v} @${s}: a vida sai igual ao gabarito, e o replay do registro da a mesma assinatura`, () => {
      const g = gab22.vidas.find(x => x.variante === v && x.semente === s)!;
      const { m, log, res } = viverV21(v, s, DIAS_V21, true, VERSAO_V22);
      expect(m.versao).toBe(VERSAO_V22);
      expect(gravarV21(v, s, m, log, res)).toEqual(g);
      const r = Motor.reproduzir(s, log, VERSAO_V22);
      expect(r.assinatura()).toBe(m.assinatura());
    });
  }
});

/* LUTA_POC, LP5-5: o gabarito da v23, a vida da versao nova, gravada depois dela entrar */
const gab23 = JSON.parse(readFileSync(new URL("./gabaritos/lp2_vidas_v23.json", import.meta.url), "utf8")) as typeof gab;
describe("a vida da v23 (LP5-5): o gabarito e o replay bit a bit", () => {
  for (const v of VARIANTES_V21) for (const s of SEMENTES_V21) {
    test(`v23 ${v} @${s}: a vida sai igual ao gabarito, e o replay do registro da a mesma assinatura`, () => {
      const g = gab23.vidas.find(x => x.variante === v && x.semente === s)!;
      const { m, log, res } = viverV21(v, s, DIAS_V21, true, VERSAO_V23);
      expect(m.versao).toBe(VERSAO_V23);
      expect(gravarV21(v, s, m, log, res)).toEqual(g);
      const r = Motor.reproduzir(s, log, VERSAO_V23);
      expect(r.assinatura()).toBe(m.assinatura());
    });
  }
});
