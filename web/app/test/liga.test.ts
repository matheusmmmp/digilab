/* A Liga dos Lideres na Fronteira (docs/DESIGN_FRONTEIRA.md, secoes 2 e 4; medalhas parte 4a; so no jogo, so pets v6): a tabela dos 6
   lideres e dos Megas deles, a entrada com as 6 medalhas, a sequencia sem cura, a proibicao de carta, o limite de turnos do desafiado (o
   lider), o replay com as lutas da Liga, o titulo no registro do Tamer, a conclusao da jornada e os pets v1-v5 de fora. O pet de verdade
   e o do teste ponta a ponta (e2e/save_liga.json, e2e/gerar_save_liga.mjs): um Mega v6 treinado ate o teto, que conhece as 6 medalhas. */
import { readFileSync } from "node:fs";
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import {
  CESC_V6, CIT, CV21D, ESPECIES, FATOR_LIGA, FATOR_LIGA_DESENHO, LIGA, MEDALHAS, MEDALHAS_LIGA, NOME_ARQ, NPC, RIVAL_LIGA, formaLiga, hashSemente,
  jogarArena, jogarSerie, jogarV2, lutadorLiga, lutadoresLiga, nomeForma, nomeMegaLiga, sementeDaSerie, type EventoRegistro,
} from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";
import { Motor } from "../motor/motor.ts";
import { Tamer, conferirCampeao, lerTamer, gravarTamer, type EventoTamer } from "../src/tamer.ts";
import { concluiuJornada, marcos } from "../src/jornada.ts";
// @ts-expect-error: modulo .mjs sem tipos (os pets de referencia da parte 2)
import { R as R_REF, formasDe, lutador } from "./itens_ref.mjs";

/* as lutas da Liga como no app: com a escala ligada */
const escalaAntes = ESCALA.ligada;
beforeEach(() => ligarEscala(true));
afterEach(() => ligarEscala(escalaAntes));
const SAVE: { semente: number; log: EventoRegistro[]; versao: number } = JSON.parse(readFileSync(new URL("../e2e/save_liga.json", import.meta.url), "utf8"));
/** o Mega do save, reproduzido do registro */
const mega = (): Motor => Motor.reproduzir(SAVE.semente, SAVE.log, SAVE.versao);
/** a semente da tentativa pelo botao do app */
const sementeDoBotao = (m: Motor): number => hashSemente("luta", m.semente, m.log.length);
const PIEDMON = "npc_v5_piedmon";
const armaz = () => { const dados: Record<string, string> = {}; return { dados, getItem: (k: string) => (k in dados ? dados[k] : null), setItem(k: string, v: string) { dados[k] = v; } }; };
/** um Tamer com as 6 medalhas */
function tamer6(): Tamer {
  const t = new Tamer(), m = new Motor(1, 6);
  for (const md of MEDALHAS) t.ganhar(md.id, m, 1);
  return t;
}

describe("a tabela da Liga", () => {
  test("6 lideres na ordem das arenas, cada um com um Mega de arquetipo diferente; as 4 especies", () => {
    expect(LIGA.map(x => [NPC[x.lider]!.nome, x.arena])).toEqual([["Gazimon", "campina"], ["Guardromon", "torre"], ["Youkomon", "floresta"],
      ["Myotismon", "cidadela"], ["MarinBullmon", "lago"], ["Piedmon", "espiral"]]);
    expect(LIGA.map((_, i) => [nomeMegaLiga(i), NOME_ARQ[LIGA[i].adulta]])).toEqual([["WarGreymon", "Furioso"], ["Seraphimon", "Espelho"],
      ["MegaGargomon", "Sentinela"], ["Vikemon", "Titã"], ["Rosemon", "Muralha"], ["Imperialdramon Dragon Mode", "Duelista"]]);
    expect(new Set(LIGA.map(x => x.adulta)).size).toBe(6);
    expect(new Set(LIGA.map(x => x.esp))).toEqual(new Set(ESPECIES));
    expect(MEDALHAS_LIGA).toBe(MEDALHAS.length);
  });
  test("cada lider luta com o Mega: tecnica da linha, passiva da forma, lista canonica V21D; E = vida do Mega na escala v6 x fator", () => {
    for (let i = 0; i < LIGA.length; i++) {
      const L = lutadorLiga(i, CV21D), f = formaLiga(i);
      expect(L.cond.est).toBe("mega");
      expect(L.cond.passiva).toBe(LIGA[i].adulta);
      expect(L.cond.tecnica).not.toBeNull();
      expect(L.cond.escala).toBeCloseTo(CESC_V6.vida.mega * FATOR_LIGA, 6);
      expect(f.est).toBe("mega");
    }
    /* a muralha (Rosemon) luta com a lista do espelho nas regras V21D */
    expect(lutadorLiga(4, CV21D).estilo.gambits).toEqual(lutadorLiga(1, CV21D).estilo.gambits);
    /* o fator: sem fator (1); o do desenho (o do Piedmon na Espiral) fica so para a conferencia */
    expect(FATOR_LIGA).toBe(1);
    expect(FATOR_LIGA_DESENHO).toBe(1.6);
  });
});

describe("a Liga e completavel (conferencia, sem calibracao)", () => {
  test("com o fator adotado, o Mega de referencia certo (furioso, treino tipico) vence a Liga inteira; com o do desenho, nenhuma forma", () => {
    const furioso = formasDe("mega").find((f: [string]) => f[0] === "furioso");
    const titulos = (fator: number, formas: unknown[]) => {
      let t = 0;
      for (const fo of formas) for (const e of ESPECIES) for (let k = 0; k < 5; k++) {
        const A = lutador(fo, e, CIT.tipico.mega, [], true);
        const serie = jogarSerie(A, lutadoresLiga(R_REF, fator), hashSemente("teste-liga", e, k), R_REF, 1, null);
        if (serie.length === LIGA.length && serie[LIGA.length - 1].pontosA === 1) t++;
      }
      return t;
    };
    expect(titulos(FATOR_LIGA, [furioso])).toBeGreaterThan(0);
    expect(titulos(FATOR_LIGA_DESENHO, formasDe("mega"))).toBe(0);
  });
});

describe("a entrada e as regras da Liga (Motor)", () => {
  test("so pets v6 com as 6 medalhas; o In-Training nao luta", () => {
    const v5 = new Motor(40, 5); v5.avancar(300);
    expect(() => v5.lutar(RIVAL_LIGA, 1)).toThrow(/só de pets v6/);
    const m = new Motor(41, 6);
    m.liberar(5); m.avancar(300);
    expect(m.porqueNaoLiga()).toMatch(/6 medalhas/);
    expect(() => m.lutar(RIVAL_LIGA, 1)).toThrow(/6 medalhas/);
    const bebe = new Motor(42, 6); bebe.liberar(6);
    expect(() => bebe.lutar(RIVAL_LIGA, 1)).toThrow(/In-Training/);
    expect(bebe.log.filter(e => e[1] === "l")).toHaveLength(0);
    expect(mega().porqueNaoLiga()).toBeNull();
  });
  test("seis lutas seguidas sem cura: o pet leva a vida e o guts; cada lider comeca inteiro; para na primeira derrota", () => {
    const m = mega();
    let viuDerrota = false, viuTitulo = false;
    for (let k = 0; k < 60 && !(viuDerrota && viuTitulo); k++) {
      const s = hashSemente("serie-liga", k), L = m.montarLuta(RIVAL_LIGA, s), serie = L.serie;
      expect(L.lideres).toHaveLength(LIGA.length);
      expect(L.carta).toBeNull();
      serie.forEach((res, j) => {
        expect(res.E0.L[1].hp).toBe(res.E0.L[1].hpMax);                            /* o lider comeca inteiro */
        if (j) {
          const antes = serie[j - 1].E.L[0];
          expect(res.E0.L[0].hp).toBe(antes.hp);                                   /* sem cura */
          expect(res.E0.L[0].guts).toBe(Math.min(antes.guts, res.E0.L[0].gutsMax));
          expect(serie[j - 1].pontosA).toBe(1);                                    /* so segue depois de vencer */
        } else expect(res.E0.L[0].hp).toBe(res.E0.L[0].hpMax);
        /* a mesma luta que jogarV2 daria, com a semente derivada e o comeco da anterior */
        const ini = j ? { hp: serie[j - 1].E.L[0].hp, guts: serie[j - 1].E.L[0].guts } : null;
        expect(res.turnos.map(t => [t.a, t.b])).toEqual(jogarV2(L.A, L.lideres![j], sementeDaSerie(s, j), m.regras, ini, 1).turnos.map(t => [t.a, t.b]));
      });
      if (serie[serie.length - 1].pontosA !== 1) viuDerrota = true;
      if (serie.length === LIGA.length && serie[LIGA.length - 1].pontosA === 1) viuTitulo = true;
    }
    expect(viuTitulo).toBe(true);
    expect(viuDerrota).toBe(true);
  });
  test("as cartas nao valem: o motor recusa a carta antes da Liga, e o replay com um 'k' logo antes da luta da Liga falha", () => {
    const m = mega(), n = m.log.length;
    expect(() => m.lutar(RIVAL_LIGA, 7, "carta_folego")).toThrow(/cartas não valem/);
    expect(m.log).toHaveLength(n);                                                 /* nada entrou no registro */
    const t = m.e.tick, log: EventoRegistro[] = [...SAVE.log, [t, "k", { id: "carta_folego" }], [t, "l", { r: RIVAL_LIGA, s: 7 }]];
    expect(() => Motor.reproduzir(SAVE.semente, log, 6)).toThrow(/cartas não valem/);
  });
  test("o limite de turnos e do desafiado (o lider): a luta que chega ao limite e do lider e quebra a Liga, mesmo com o pet na frente", () => {
    /* o motor joga a Liga com o desafiado = o lider (lado B) */
    const m = mega();
    for (let k = 0; k < 10; k++) {
      const s = hashSemente("motor-liga", k), L = m.montarLuta(RIVAL_LIGA, s);
      expect(L.serie).toEqual(jogarSerie(L.A, L.lideres!, s, m.regras, 1, null));
    }
    /* com um Mega de referencia (vigia, treino tipico), a Liga pela regra do limite x pela fracao de vida */
    const vigia = formasDe("mega").find((f: [string]) => f[0] === "vigia"), Ls = lutadoresLiga(R_REF);
    let achou = false;
    for (const e of ESPECIES) for (let k = 0; k < 40 && !achou; k++) {
      const A = lutador(vigia, e, CIT.tipico.mega, [], true), s = hashSemente("limite-liga", e, k), serie = jogarSerie(A, Ls, s, R_REF, 1, null);
      serie.forEach((res, j) => {
        if (res.fim !== "limite") return;
        expect(res.pontosA).toBe(0);                                               /* no limite, sempre do lider */
        expect(j).toBe(serie.length - 1);                                          /* e a Liga para ali */
        const ini = j ? { hp: serie[j - 1].E.L[0].hp, guts: serie[j - 1].E.L[0].guts } : null;
        const livre = jogarV2(A, Ls[j], sementeDaSerie(s, j), R_REF, ini, null);
        expect(livre.turnos).toEqual(res.turnos);                                  /* a regra so muda quem fica com a luta */
        if (livre.pontosA === 1) achou = true;                                     /* pela fracao de vida o pet teria vencido */
      });
    }
    expect(achou).toBe(true);
  });
});

describe("registro e replay", () => {
  test("a tentativa e um evento de luta so, {r, s}; o replay reconstroi o mesmo pet, e a Liga so entra na assinatura depois dela", () => {
    const m = mega(), antes = m.assinatura();
    expect(antes).not.toMatch(/"liga"/);
    /* uma derrota e depois o titulo, com sementes que dao cada um */
    const acha = (quer: boolean) => { for (let k = 0; k < 200; k++) { const s = hashSemente("replay-liga", m.log.length, k), sr = m.montarLuta(RIVAL_LIGA, s).serie;
      if ((sr.length === LIGA.length && sr[LIGA.length - 1].pontosA === 1) === quer) return s; } throw new Error("sem semente"); };
    const r1 = m.lutar(RIVAL_LIGA, acha(false));
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    expect(r1.venceu).toBe(false);
    m.avancar(30);
    const r2 = m.lutar(RIVAL_LIGA, acha(true));
    expect(r2.venceu).toBe(true);
    expect(r2.serie).toHaveLength(LIGA.length);
    expect(m.liga).toEqual({ tentativas: 2, titulos: 1 });
    const ls = m.log.filter(e => e[1] === "l" && e[2].r === RIVAL_LIGA);
    expect(ls).toHaveLength(2);
    for (const e of ls) expect(Object.keys(e[2]).sort()).toEqual(["r", "s"]);
    const r = Motor.reproduzir(m.semente, m.log, m.versao);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.liga).toEqual(m.liga);
    expect(m.assinatura()).toMatch(/"liga"/);
    /* o historico conta cada luta com o lider e o Mega */
    expect(m.historico.some(h => h.a.startsWith("na Liga dos Líderes, contra WarGreymon de Gazimon (luta 1 de 6)"))).toBe(true);
  });
  test("luta da Liga no registro sem as 6 medalhas falha alto no replay", () => {
    const t0 = 700, log: EventoRegistro[] = [[480, "u", { n: 5 }], [480, "t", t0 - 480], [t0, "l", { r: RIVAL_LIGA, s: 3 }]];
    expect(() => Motor.reproduzir(99, log, 6)).toThrow(/Liga no registro sem poder/);
  });
  test("pets v1-v5: a Liga nao existe (e a regra da serie da Cidadela nao mudou com a generalizacao)", () => {
    for (const v of [1, 2, 3, 4, 5]) {
      const m = new Motor(50 + v, v); m.avancar(300);
      expect(() => m.lutar(RIVAL_LIGA, 1)).toThrow(/só de pets v6/);
    }
    /* jogarArena = jogarSerie com o mesmo rival n vezes */
    const A = lutadorLiga(0, CV21D), B = lutadorLiga(5, CV21D);
    expect(jogarArena(A, B, 77, CV21D, 3, 1)).toEqual(jogarSerie(A, [B, B, B], 77, CV21D, 1));
  });
});

describe("o titulo no Tamer e a conclusao da jornada", () => {
  test("vencer a Liga grava 'campeao' no Tamer (pet e forma), uma vez por pet; o registro reproduz e le a versao 3", () => {
    const m = mega(), t = tamer6();
    expect(conferirCampeao(t, m)).toBeNull();                                     /* ainda nao venceu */
    for (let k = 0; ; k++) {
      const s = hashSemente("titulo", k), sr = m.montarLuta(RIVAL_LIGA, s).serie;
      if (sr.length === LIGA.length && sr[LIGA.length - 1].pontosA === 1) { m.lutar(RIVAL_LIGA, s); break; }
    }
    const c = conferirCampeao(t, m, 123)!;
    expect(c).toMatchObject({ n: 1, quando: 123, pet: m.semente, tick: m.e.tick });
    expect(c.forma).toBe(nomeForma(m.forma));
    expect(t.titulo).toEqual(c);
    expect(conferirCampeao(t, m)).toBeNull();                                     /* um por pet */
    const a = armaz(); gravarTamer(a, t);
    const r = lerTamer(a);
    expect(r.campeoes).toEqual(t.campeoes);
    expect(JSON.parse(Object.values(a.dados)[0]).versao).toBe(3);
    /* sem as 6 medalhas, o titulo nao entra (nem no replay) */
    expect(conferirCampeao(new Tamer(), m)).toBeNull();
    const ev: EventoTamer = ["campeao", { n: 1, quando: 1, pet: 1, forma: "WarGreymon", tick: 1 }];
    expect(() => Tamer.reproduzir([ev])).toThrow(/antes das 6 medalhas/);
    const seis = tamer6().log;
    expect(() => Tamer.reproduzir([...seis, ev, ["campeao", { ...ev[1], n: 2 }]])).toThrow(/repetido/);
    expect(() => Tamer.reproduzir([...seis, ["campeao", { ...ev[1], n: 2 }]])).toThrow(/fora de ordem/);
    expect(Tamer.reproduzir([...seis, ev]).titulo).toMatchObject({ pet: 1, forma: "WarGreymon" });
  });
  test("a jornada dos pets v6 termina na Liga, nao no Piedmon; os marcos tem a Liga", () => {
    const m = mega();
    const x = marcos(m);
    expect(x).toHaveLength(12);
    expect(x[x.length - 1]).toEqual({ rotulo: "Venceu a Liga dos Líderes", feito: false });
    m.campanha[PIEDMON] = 1;                                                        /* o Piedmon so nao basta */
    expect(concluiuJornada(m)).toBe(false);
    m.liga.titulos = 1;
    expect(concluiuJornada(m)).toBe(true);
    expect(marcos(m)[11].feito).toBe(true);
    /* pets v5: continua o Piedmon */
    const v5 = new Motor(60, 5);
    expect(concluiuJornada(v5)).toBe(false);
    v5.campanha[PIEDMON] = 1;
    expect(concluiuJornada(v5)).toBe(true);
    expect(marcos(v5).some(y => y.rotulo.includes("Liga"))).toBe(false);
  });
});
