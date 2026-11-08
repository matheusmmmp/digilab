// LUTA_POC, LP2b (docs/TAREFA_V3_LUTA_POC.md, LP-5 revista): os torneios no nucleo da POC, na v21. A Liga (os 6 lideres em sequencia, sem cura,
// no mapa do lugar de cada lider), a Torre de Batalha (Megas sorteados, sem cura, com o Palacio junto), o Salao (um rival do estagio) e a
// Fabrica da luta da POC (os 3 alugados, as series de 3 e a troca, no registro do Tamer). O replay bit a bit e o gabarito
// (test/gabaritos/lp2b_torneios_v21.json, por test/lp2b_torneios.ts --gravar).
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import {
  LIGA, LUTAS_SERIE_FABRICA, MEDALHAS, MAPA_FABRICA, MAPA_SALAO, MAPA_TORRE, MEDALHAS_LIGA, Motor, PALACIO_NA_TORRE, RIVAL_LIGA, RIVAL_SALAO, TentativaFabrica,
  VERSAO_FABRICA_ATUAL, VERSAO_FABRICA_POC, VERSAO_V21, VERSOES_FABRICA, chaveSprite, formaLiga, formaRivalInstalacao, formaRivalSalao, regraFabrica,
  sementeFabrica, type EventoRegistro,
} from "../motor/index.ts";
import { SEMENTES_LP2B, gravarTorneios, petDosTorneios, tentativaFabrica, treinarMuito, viverTorneios, type VidaTorneios } from "./lp2b_torneios.ts";

const sementeFixa = 7101;

describe("a entrada dos torneios na v21", () => {
  test("os torneios nao escolhem mapa, e as entradas de sempre valem (medalhas, titulo, semente da tentativa)", () => {
    const m = petDosTorneios(101);
    expect(() => m.lutarPoc(RIVAL_LIGA, 1, "campo")).toThrow(/não escolhem mapa/);
    expect(() => m.lutarPoc("torre_batalha", m.sementeInstalacao("torre_batalha") + 1, null)).toThrow(/semente da tentativa/);
    expect(() => m.lutarPoc(RIVAL_SALAO, m.sementeSalao() + 1, null)).toThrow(/semente da luta no Salão/);
    expect(() => m.lutarPoc("palacio", 1, null)).toThrow(PALACIO_NA_TORRE);
    expect(m.porqueNaoInstalacao("palacio")).toBe(PALACIO_NA_TORRE);
    const novo = new Motor(202, VERSAO_V21);
    expect(novo.porqueNaoLutaPoc(RIVAL_LIGA, null)).toMatch(/In-Training|medalhas/);
  });
});

describe("as series: o rival, o mapa e a vida que passa de uma luta para a outra", () => {
  const m = petDosTorneios(202);
  treinarMuito(m, 1500);
  const liga = m.lutarPoc(RIVAL_LIGA, sementeFixa, null);
  test("a Liga: os 6 lideres na ordem, cada um no mapa do lugar dele, sem cura entre as lutas; o evento nao tem mapa", () => {
    expect(m.log.at(-1)).toEqual([m.e.tick, "l", { r: RIVAL_LIGA, s: sementeFixa }]);
    expect(liga.mapa).toBeNull();
    expect(liga.torneio).toBe(true);
    const mapas = ["campo", "coliseu", "floresta", "castelo", "praia", "caverna"];
    liga.serie.forEach((x, k) => {
      expect(x.contra).toBe(chaveSprite(formaLiga(k)));
      expect(x.mapa).toBe(mapas[k]);
      if (k) expect(x.vida0).toBe(liga.serie[k - 1].vidaA);
    });
    expect(liga.serie.length).toBeGreaterThan(1);
    expect(m.liga.tentativas).toBe(1);
    expect(m.liga.titulos).toBe(liga.venceu ? 1 : 0);
    expect(liga.venceu).toBe(liga.serie.length === LIGA.length && liga.serie.at(-1)!.pontosA === 1);
  });
  test("a Torre: Megas sorteados da semente da tentativa, no mapa dela, sem cura; o recorde do pet ali", () => {
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    const s = m.sementeInstalacao("torre_batalha"), t = m.lutarPoc("torre_batalha", s, null);
    t.serie.forEach((x, k) => {
      expect(x.contra).toBe(chaveSprite(formaRivalInstalacao(s, k)));
      expect(x.mapa).toBe(MAPA_TORRE);
      if (k) expect(x.vida0).toBe(t.serie[k - 1].vidaA);
    });
    const v = t.serie.filter(x => x.pontosA === 1).length;
    expect(m.instalacoes.torre_batalha).toEqual({ tentativas: 1, recorde: v, ultima: v });
  });
  test("o Salao: um rival do estagio do pet, no mapa dele, uma luta", () => {
    const s = m.sementeSalao(), est = m.estagioAtual, r = m.lutarPoc(RIVAL_SALAO, s, null);
    expect(r.serie).toHaveLength(1);
    expect(r.serie[0].contra).toBe(chaveSprite(formaRivalSalao(s, est)));
    expect(r.serie[0].mapa).toBe(MAPA_SALAO);
    expect(m.salao.tentativas).toBe(1);
  });
  test("o replay do registro refaz os torneios: a mesma assinatura", () => {
    expect(Motor.reproduzir(202, m.log, VERSAO_V21).assinatura()).toBe(m.assinatura());
  });
});

describe("a Fabrica da luta da POC", () => {
  test("a versao 21 entra no registro do Tamer; a de hoje segue a 14 com a chave desligada; sem fator de rival", () => {
    expect(VERSOES_FABRICA).toEqual([13, 14, 21]);
    expect(VERSAO_FABRICA_ATUAL).toBe(14);
    expect(regraFabrica(VERSAO_FABRICA_POC).poc).toBe(true);
    expect(() => regraFabrica(VERSAO_FABRICA_POC, 0.5)).toThrow(/fator/);
    expect(MAPA_FABRICA).toBe("campo");
  });
  test("as series de 3 sem cura, a troca pelo derrotado (que entra inteiro) e o fim na primeira derrota; deterministica", () => {
    let alguma = false;
    for (let n = 1; n <= 12; n++) {
      const a = tentativaFabrica(n, n % 3), b = tentativaFabrica(n, n % 3);
      expect(b.resumo).toBe(a.resumo);
      const L = a.t.lutas;
      L.forEach((l, i) => {
        expect(l.res).toBeNull();
        expect(l.poc!.fim || l.poc!.relogio > 0).toBe(true);
        if (!i) return;
        const ant = L[i - 1], mesmaSerie = Math.floor(l.k / LUTAS_SERIE_FABRICA) === Math.floor(ant.k / LUTAS_SERIE_FABRICA);
        const hpMax = a.t.statsPoc(l.alugado).hp;
        /* dentro da serie e sem troca, o alugado entra com a vida do fim da anterior; depois da troca ou no comeco da serie, inteiro */
        if (mesmaSerie && !ant.trocou) { expect(l.poc!.vidaA <= ant.poc!.vidaA).toBe(true); alguma = true; }
        if (!mesmaSerie || ant.trocou) expect(l.poc!.vidaA <= hpMax).toBe(true);
      });
      expect(a.t.acabou || a.t.lutas.length === 60).toBe(true);
      expect(a.t.s).toBe(sementeFabrica(n));
    }
    expect(alguma).toBe(true);
  });
});

const gab = JSON.parse(readFileSync(new URL("./gabaritos/lp2b_torneios_v21.json", import.meta.url), "utf8")) as
  { versao: number; sementes: number[]; vidas: VidaTorneios[]; fabrica: { n: number; s: number; series: number; lutas: number; resumo: string }[] };
describe("o gabarito dos torneios v21 e o replay bit a bit", () => {
  test("a forma do gabarito", () => {
    expect(gab.versao).toBe(1);
    expect(gab.sementes).toEqual([...SEMENTES_LP2B]);
    expect(gab.vidas.every(v => v.liga === 1 && v.torre === 1 && v.salao === 1 && v.lutas > 3)).toBe(true);
  });
  for (const s of SEMENTES_LP2B) {
    test(`@${s}: a Liga, a Torre e o Salao saem iguais ao gabarito, e o replay da a mesma assinatura`, () => {
      const g = gab.vidas.find(x => x.semente === s)!;
      const { m, log, res } = viverTorneios(s);
      expect(gravarTorneios(s, m, log, res)).toEqual(g);
      const r = Motor.reproduzir(s, log as EventoRegistro[], VERSAO_V21);
      expect(r.assinatura()).toBe(m.assinatura());
    });
  }
  test("as 5 tentativas da Fabrica saem iguais ao gabarito", async () => {
    const { createHash } = await import("node:crypto");
    for (const f of gab.fabrica) {
      const { t, resumo } = tentativaFabrica(f.n, f.n % 3);
      expect({ n: f.n, s: t.s, series: t.series, lutas: t.lutas.length, resumo: createHash("sha256").update(resumo).digest("hex") }).toEqual(f);
    }
  });
  test("o pet com as 6 medalhas e o titulo (os eventos u e f) e a base dos torneios", () => {
    const m = petDosTorneios(303);
    expect(m.medalhas).toBe(MEDALHAS_LIGA);
    expect(m.fronteira).toBe(true);
  });
});

test("Tamer: a tentativa da Fabrica v21 entra no registro e se refaz igual", async () => {
  const { Tamer } = await import("../src/tamer.ts");
  /* um Tamer com as 6 medalhas e o titulo da Liga (como no tamer.test.ts): a Fabrica abre depois do titulo */
  const seis = MEDALHAS.slice(0, 6).map((md, i) => ["medalha", { id: md.id, n: i + 1, quando: i + 1, pet: 1, forma: "Agumon", tick: 900 }]);
  const t = Tamer.reproduzir([...seis, ["campeao", { n: 1, quando: 10, pet: 1, forma: "WarGreymon", tick: 950 }]] as never);
  t.alugarFabrica(1, 1000, VERSAO_FABRICA_POC);
  for (let i = 0; i < 10 && t.fabricaAtual; i++) t.lutarFabrica(2000 + i);
  const r = Tamer.reproduzir(t.log);
  expect(r.fabrica.map(x => x.lutas.map(l => [l.venceu, l.poc!.relogio, l.poc!.vidaA]))).toEqual(t.fabrica.map(x => x.lutas.map(l => [l.venceu, l.poc!.relogio, l.poc!.vidaA])));
  expect(t.fabrica[0].regra.versao).toBe(21);
  expect(() => t.alugarFabrica(0, 1, 99)).toThrow(/versão das regras/);
});
