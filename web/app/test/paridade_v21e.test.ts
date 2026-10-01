/* Combate V21E nos pets v9 (rodada de equilibrio geral, fase 1; docs/EQUILIBRIO_GERAL.md): paridade Python x web e o que muda
   por versao de pet. Gabarito: experiments/exportar_gabarito_v21e.py (136 partidas do Python com a variante escolhida,
   experiments/configs/v21e/calibracao.json; mesmos confrontos e sementes do gabarito da V21D). O TS refaz cada partida: decisoes
   por regra, leitura do vigia e resolucao sao do motor em TS; so as acoes de exploracao (epsilon) vem do gabarito. Os pets v6-v8
   continuam na V21D e os v1-v5 na V21C (paridade_v21d.test.ts, gabaritos.test.mjs e paridade_ts.test.mjs). */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { ADOL_V21, BOTS_V21, BOTS_V21D, BOTS_V21E, REGRA_CONTRA_GOLPE_NA_PELE, REGRA_DEFENDE_DO_GOLPE, gambitNPC, gambitsAdulto } from "../motor/bots.ts";
import { caraterCanonico, perfilDe } from "../motor/catalogo.ts";
import { decidirV2, estadoV2, fimV2, intencaoV2, jogarV2, regrasDaVersao, resolverV2, type ListaGambits, type Lutador, type RegrasLuta } from "../motor/combate.ts";
import { CAT, CV21D, CV21E, FORMAS_AD, LINHA_DA_FORMA, SOMBRIA, VERSAO_PET } from "../motor/constantes.ts";
import { GambitsPet, REPERTORIO, candidatasV21E, chaveRegra, lutadorBot, lutadorPet, regraDe, sementeDe } from "../motor/gambits_pet.ts";
import { Motor } from "../motor/motor.ts";
import { criarRng } from "../motor/rng.ts";
import type { Forma, FormaAdultaNormal, Linha } from "../motor/tipos.ts";

interface Desc { tipo: "adulto" | "adolescente"; forma?: string; linha?: Linha; especie: string }
interface Partida {
  variante: "v21e"; n: number; a: Desc; b: Desc; perfil_a: Record<string, number>; perfil_b: Record<string, number>;
  turnos: string; sha256_turnos: string; pontos_a: number; motivo: string; n_turnos: number; hp_a: number; hp_b: number;
}
type ListaPy = { regras: { se: { nome: string; params: (string | number)[] }[]; entao: string }[]; final: { entao: string } };
const G = JSON.parse(readFileSync(new URL("./gabaritos/combate_v21e_python.json", import.meta.url), "utf8")) as {
  chaves_v21e: Record<string, boolean>; listas_v21e: Record<string, ListaPy>; partidas: Partida[]; resumo: { diferentes_da_v21d: number };
};
const DIST: Record<string, number> = { perto: 0, medio: 1, longe: 2 };
const camel = (k: string): string => k.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase());

/** o lutador do gabarito no motor em TS (bot canonico: carater canonico, condicao 1, sem treino) */
function lutador(d: Desc, R: RegrasLuta): Lutador {
  if (d.tipo === "adolescente") {
    const f: Forma = { esp: d.especie as Forma["esp"], est: "adolescente", ramo: "sereno", linha: d.linha! };
    const primeira = FORMAS_AD.find(x => LINHA_DA_FORMA[x] === d.linha)!;
    return { nome: `adolescente-${d.linha}@${d.especie}`, estilo: { nome: "adol", gambits: ADOL_V21[d.linha!], eps: 0 }, cond: perfilDe(f, caraterCanonico(primeira)) };
  }
  const s = SOMBRIA[d.forma!], linha = s ? s.linha : LINHA_DA_FORMA[d.forma as FormaAdultaNormal];
  const f: Forma = { esp: d.especie as Forma["esp"], est: "adulto", ramo: "sereno", linha, adulta: d.forma as Forma["adulta"] };
  const car = s ? { [CAT.adolescente[linha].eixo]: .5 } : caraterCanonico(d.forma as FormaAdultaNormal);
  return { nome: `${d.forma}@${d.especie}`, estilo: { nome: d.forma!, gambits: sementeDe(f, R), eps: 0 }, cond: perfilDe(f, car) };
}
/** refaz a partida no TS; a exploracao (so ela) vem dos turnos do Python */
function refazer(P: Partida, A: Lutador, B: Lutador, R: RegrasLuta) {
  const py = P.turnos ? P.turnos.split(";").map(t => t.split(",")) : [], rng = criarRng(1), saida: string[] = [];
  let E = estadoV2(A.cond, B.cond), fim: ReturnType<typeof fimV2>, i = 0;
  while (!(fim = fimV2(E))) {
    const ctx = [A.cond.passiva === "vigia" ? { intencao: intencaoV2(B.estilo, E, 1, R) } : null,
      B.cond.passiva === "vigia" ? { intencao: intencaoV2(A.estilo, E, 0, R) } : null];
    const dec = [0, 1].map(l => py[i]?.[2 * l + 1] === "exploracao" ? [py[i][2 * l], "exploracao"] as const
      : decidirV2(l ? B.estilo : A.estilo, E, l, rng, ctx[l], R));
    saida.push(`${dec[0][0]},${dec[0][1]},${dec[1][0]},${dec[1][1]}`);
    E = resolverV2(E, dec[0][0], dec[1][0]).E;
    if (++i > 100) throw new Error("partida sem fim");
  }
  return { txt: saida.join(";"), pontos: fim[0], motivo: fim[1], E };
}
const sha = (s: string): string => createHash("sha256").update(s, "utf8").digest("hex");
const PERFIL: [string, keyof Lutador["cond"]][] = [["hp_max", "hpMax"], ["guts_inicial", "guts0"], ["guts_max", "gutsMax"], ["regen", "regen"],
  ["mult_perto", "mPerto"], ["mult_disparo", "mDisparo"], ["mult_guarda", "mGuarda"]];

describe("combate V21E: paridade com o Python", () => {
  test("constantes: as chaves ligadas da variante da fase 1 (as 4 da V21D e as 5 da V21E) e so elas", () => {
    const ligadas = Object.entries(G.chaves_v21e).filter(([, x]) => x).map(([k]) => camel(k)).sort();
    const web = Object.entries(CV21E).filter(([, x]) => typeof x === "boolean").map(([k]) => k).sort();
    expect(web).toEqual(ligadas);
    for (const k of web) expect((CV21E as Record<string, unknown>)[k], k).toBe(true);
    expect(CV21E.versaoPet).toBe(9); expect(VERSAO_PET).toBeGreaterThanOrEqual(9);   /* o v10 (vinculo B) herda a V21E */
  });

  test("listas da V21E (duelista, tita, espelho, muralha) e a do vigia = as do Python", () => {
    const conv = (g: ListaGambits) => ({ regras: g.regras.map(r => ({ se: r.se.map(c => ({ nome: c.n, params: c.p })), entao: r.entao })), final: g.final });
    for (const [f, py] of Object.entries(G.listas_v21e)) {
      const esperado = { regras: py.regras.map(r => ({ se: r.se.map(c => ({ nome: c.nome, params: c.nome === "distancia_eh" ? [DIST[c.params[0]]] : c.params })), entao: r.entao })), final: py.final.entao };
      expect(conv(gambitsAdulto(f as FormaAdultaNormal, CV21E)), f).toEqual(esperado);
    }
    expect(Object.keys(BOTS_V21E).sort()).toEqual(["duelista", "espelho", "muralha", "tita"]);
    expect(BOTS_V21E.duelista!.regras[1]).toBe(REGRA_DEFENDE_DO_GOLPE);
    expect(BOTS_V21E.tita!.regras[2]).toBe(REGRA_DEFENDE_DO_GOLPE);
    expect(BOTS_V21E.muralha!.regras[1]).toBe(REGRA_CONTRA_GOLPE_NA_PELE);
    /* as canonicas e as da V21D nao mudam */
    for (const f of FORMAS_AD) expect(BOTS_V21[f].regras.map(chaveRegra)).not.toContain(chaveRegra(REGRA_DEFENDE_DO_GOLPE));
    expect(BOTS_V21D.muralha!.regras).toBe(BOTS_V21.espelho.regras);
  });

  test(`v21e: ${G.partidas.length} partidas do Python refeitas no TS (perfil, sha dos turnos, fim)`, () => {
    let comExploracao = 0;
    for (const P of G.partidas) {
      const A = lutador(P.a, CV21E), B = lutador(P.b, CV21E), rot = `#${P.n} ${A.nome} x ${B.nome}`;
      for (const [py, ts] of PERFIL) {
        expect(Math.abs((A.cond[ts] as number) - P.perfil_a[py]), `${rot}: ${py} de a`).toBeLessThanOrEqual(1e-12);
        expect(Math.abs((B.cond[ts] as number) - P.perfil_b[py]), `${rot}: ${py} de b`).toBeLessThanOrEqual(1e-12);
      }
      const r = refazer(P, A, B, CV21E);
      expect(r.txt, rot).toBe(P.turnos);
      expect(sha(r.txt), rot).toBe(P.sha256_turnos);
      expect([r.pontos, r.motivo, r.E.turno], rot).toEqual([P.pontos_a, P.motivo, P.n_turnos]);
      expect(Math.abs(r.E.L[0].hp - P.hp_a), `${rot}: vida final de a`).toBeLessThanOrEqual(1e-9);
      expect(Math.abs(r.E.L[1].hp - P.hp_b), `${rot}: vida final de b`).toBeLessThanOrEqual(1e-9);
      if (P.turnos.includes("exploracao")) comExploracao++;
    }
    expect(comExploracao).toBeGreaterThan(50);
    expect(G.resumo.diferentes_da_v21d).toBeGreaterThan(20);
  });
});

describe("combate V21E: so nos pets v9", () => {
  test("regras por versao: v1-v5 na V21C, v6-v8 na V21D, v9 na V21E", () => {
    for (const v of [1, 2, 3, 4, 5]) { expect(regrasDaVersao(v)).toBeNull(); expect(new Motor(123, v).regras).toBeNull(); }
    for (const v of [6, 7, 8]) { expect(regrasDaVersao(v)).toBe(CV21D); expect(new Motor(123, v).regras).toBe(CV21D); }
    expect(regrasDaVersao(9)).toBe(CV21E);
    expect(new Motor(123).versao).toBe(10);                       /* o v10 (vinculo B) herda a V21E */
    expect(regrasDaVersao(10)).toBe(CV21E);
    expect(new Motor(123).regras).toBe(CV21E);
  });

  test("bots: as quatro formas da V21E com a lista nova so contra pet v9; o resto igual a V21D", () => {
    for (const f of FORMAS_AD) {
      expect(lutadorBot(f, CV21E).estilo.gambits, f).toEqual(gambitsAdulto(f, CV21E));
      const muda = ["duelista", "tita", "espelho", "muralha"].includes(f);
      expect(gambitsAdulto(f, CV21E) === gambitsAdulto(f, CV21D), f).toBe(!muda);
    }
    /* os NPCs com estilo v21 levam a lista da V21E sem as regras de tecnica (como na V21D) */
    const npc = gambitNPC("v21:tita", CV21E);
    expect(npc.regras.map(chaveRegra)).toContain(chaveRegra(REGRA_DEFENDE_DO_GOLPE));
    expect(npc.regras.some(r => r.entao === "pele_dura")).toBe(false);
  });

  test("semente dos gambits: o pet v9 semeia a lista da V21E; as regras novas voltam como candidatas so nos v9", () => {
    for (const adulta of ["duelista", "tita", "espelho", "muralha"] as const) {
      const f: Forma = { esp: "limo", est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[adulta], adulta };
      const g8 = new GambitsPet(), g9 = new GambitsPet();
      g8.semear(f, adulta, CV21D); g9.semear(f, adulta, CV21E);
      expect(g8.ativas).toEqual(gambitsAdulto(adulta, CV21D).regras.map(chaveRegra));
      expect(g9.ativas).toEqual(BOTS_V21E[adulta]!.regras.map(chaveRegra));
      expect(g9.estilo().gambits).toEqual(BOTS_V21E[adulta]);
    }
    for (const r of [REGRA_DEFENDE_DO_GOLPE, REGRA_CONTRA_GOLPE_NA_PELE]) {
      expect(REPERTORIO.has(chaveRegra(r))).toBe(false);           /* o repertorio (candidatas) nao muda */
      expect(regraDe(chaveRegra(r))).toEqual(r);
    }
    const forma = (adulta: FormaAdultaNormal): Forma => ({ esp: "brasa", est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[adulta], adulta });
    expect(candidatasV21E(forma("duelista"), CV21E)).toEqual([chaveRegra(REGRA_DEFENDE_DO_GOLPE)]);
    expect(candidatasV21E(forma("tita"), CV21E)).toEqual([chaveRegra(REGRA_DEFENDE_DO_GOLPE)]);
    expect(candidatasV21E(forma("muralha"), CV21E)).toEqual([chaveRegra(REGRA_CONTRA_GOLPE_NA_PELE)]);
    for (const f of ["furioso", "espelho", "vigia", "sentinela"] as const) expect(candidatasV21E(forma(f), CV21E), f).toEqual([]);
    for (const f of FORMAS_AD) { expect(candidatasV21E(forma(f), CV21D), f).toEqual([]); expect(candidatasV21E(forma(f), null), f).toEqual([]); }
  });

  test("o v9 herda o resto do v8: medalhas, itens, Fronteira, voz propria e confianca (testes de versao >=)", () => {
    const m8 = new Motor(77, 8), m9 = new Motor(77, 9);
    expect(m9.conf).not.toBeNull();                                          /* confianca (M1, v8 em diante) */
    expect(m9.porqueNaoLiga()).toBe(m8.porqueNaoLiga());                     /* Fronteira: a Liga e as instalacoes */
    expect(m9.porqueNaoInstalacao("torre_batalha")).toBe(m8.porqueNaoInstalacao("torre_batalha"));
    expect(m9.porqueNaoEquipa("chip_forca")).toBe(m8.porqueNaoEquipa("chip_forca"));   /* itens (v6 em diante) */
    expect(m9.vagasChip).toBe(m8.vagasChip);
    expect([m9.honestidade(), m9.chanceMentira()]).toEqual([m8.honestidade(), m8.chanceMentira()]);   /* voz propria (v7 em diante) */
    for (const m of [m8, m9]) { m.avancar(30); m.falar("teste"); m.liberar(1); }          /* fala espontanea e medalhas (evento u) */
    expect(m9.log.map(e => e[1])).toEqual(m8.log.map(e => e[1]));
    expect(Motor.reproduzir(m9.semente, m9.log, 9).assinatura()).toBe(m9.assinatura());
    /* a assinatura so difere pela versao das regras de luta: sem luta, v8 e v9 vivem igual */
    expect(m9.assinatura()).toBe(m8.assinatura());
  });

  test("a luta do motor: o pet v9 joga com a V21E, o v8 com a V21D (e o replay refaz)", () => {
    const viver = (versao: number) => {
      const m = new Motor(4242, versao);
      for (let k = 0; k < 40 && m.estagioAtual !== "adolescente"; k++) {
        m.avancar(60); m.observar("alimentar"); m.observar("limpar");
        if (m.esperandoMedalha()) m.liberar(1);
      }
      return m;
    };
    for (const v of [8, 9]) {
      const m = viver(v), R = regrasDaVersao(v);
      expect(m.estagioAtual).toBe("adolescente");
      expect(m.regras).toBe(v === 9 ? CV21E : CV21D);
      for (const [k, rival] of ["duelista", "tita", "espelho", "muralha", "furioso"].entries()) {
        const A = lutadorPet(m, "Seu pet"), B = lutadorBot(rival, R), esperado = jogarV2(A, B, 77 + k, R, null, 1);
        const res = m.lutar(rival, 77 + k).res;
        expect(res.turnos.map(t => [t.a, t.ma, t.b, t.mb]), `v${v} x ${rival}`).toEqual(esperado.turnos.map(t => [t.a, t.ma, t.b, t.mb]));
        expect(res.pontosA).toBe(esperado.pontosA);
      }
      expect(Motor.reproduzir(m.semente, m.log, m.versao).assinatura()).toBe(m.assinatura());
    }
  });
});
