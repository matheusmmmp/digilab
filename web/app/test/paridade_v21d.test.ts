/* Combate V21D nos pets v6 (docs/VALIDACAO_V21D.md): paridade Python x web e o que muda por versao de pet.
   Gabarito: experiments/exportar_gabarito_v21d.py (272 partidas do Python, V21C e a variante a_c_e2v_v, mesmas sementes).
   O TS refaz cada partida: decisoes por regra, leitura do vigia e resolucao sao do motor em TS; so as acoes de exploracao
   (epsilon) vem do gabarito, porque a rng do Python nao e a da web. Os pets v1-v5 continuam na V21C (os gabaritos de
   paridade com o HTML e as assinaturas nao mudam: gabaritos.test.mjs e paridade_ts.test.mjs). */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { ADOL_V21, BOTS_V21, BOTS_V21D, REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE, gambitsAdulto } from "../motor/bots.ts";
import { caraterCanonico, perfilDe } from "../motor/catalogo.ts";
import { decidirV2, estadoV2, fimV2, intencaoV2, regrasDaVersao, resolverV2, valeCond, type ListaGambits, type Lutador, type RegrasLuta } from "../motor/combate.ts";
import { CAT, CV21D, CV21E_TR, FORMAS_AD, LINHA_DA_FORMA, SOMBRIA, VERSAO_PET } from "../motor/constantes.ts";
import { GambitsPet, REPERTORIO, chaveRegra, lutadorBot, regraDe, sementeDe } from "../motor/gambits_pet.ts";
import { Motor } from "../motor/motor.ts";
import { criarRng } from "../motor/rng.ts";
import type { Forma, FormaAdultaNormal, Linha } from "../motor/tipos.ts";

interface Desc { tipo: "adulto" | "adolescente"; forma?: string; linha?: Linha; especie: string }
interface Partida {
  variante: "v21c" | "a_c_e2v_v"; n: number; a: Desc; b: Desc; perfil_a: Record<string, number>; perfil_b: Record<string, number>;
  turnos: string; sha256_turnos: string; pontos_a: number; motivo: string; n_turnos: number; hp_a: number; hp_b: number;
}
const G = JSON.parse(readFileSync(new URL("./gabaritos/combate_v21d_python.json", import.meta.url), "utf8")) as {
  chaves_v21d: Record<string, boolean>; listas_v21d: Record<string, { regras: { se: { nome: string; params: (string | number)[] }[]; entao: string }[]; final: { entao: string } }>;
  partidas: Partida[];
};
const DIST: Record<string, number> = { perto: 0, medio: 1, longe: 2 };

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

describe("combate V21D: paridade com o Python", () => {
  test("constantes: as 4 chaves ligadas da variante e so elas (as outras da V21D nao existem na web)", () => {
    const ligadas = Object.entries(G.chaves_v21d).filter(([, x]) => x).map(([k]) => k).sort();
    expect(ligadas).toEqual(["muralha_lista_espelho", "preparo_sob_pele_oculto", "vigia_bate_em_quem_recua", "vigia_recua_do_preparo_sob_pele"]);
    expect([CV21D.preparoSobPeleOculto, CV21D.muralhaListaEspelho, CV21D.vigiaBateEmQuemRecua, CV21D.vigiaRecuaDoPreparoSobPele]).toEqual([true, true, true, true]);
    expect(CV21D.versaoPet).toBe(6); expect(VERSAO_PET).toBeGreaterThanOrEqual(6);   /* do v6 em diante (o v7, voz propria, herda) */                  /* os pets v6 (os de agora); sem v7 */
  });

  test("listas variantes da muralha e do vigia = as do Python", () => {
    const conv = (g: ListaGambits) => ({ regras: g.regras.map(r => ({ se: r.se.map(c => ({ nome: c.n, params: c.p })), entao: r.entao })), final: g.final });
    for (const f of ["muralha", "vigia"] as const) {
      const py = G.listas_v21d[f];
      const esperado = { regras: py.regras.map(r => ({ se: r.se.map(c => ({ nome: c.nome, params: c.nome === "distancia_eh" ? [DIST[c.params[0]]] : c.params })), entao: r.entao })), final: py.final.entao };
      expect(conv(BOTS_V21D[f]!), f).toEqual(esperado);
    }
    expect(BOTS_V21D.vigia!.regras).toContain(REGRA_BATE_EM_QUEM_RECUA);
    expect(BOTS_V21D.vigia!.regras[0]).toBe(REGRA_RECUA_DO_PREPARO_SOB_PELE);
  });

  for (const variante of ["v21c", "a_c_e2v_v"] as const) {
    test(`${variante}: ${G.partidas.filter(p => p.variante === variante).length} partidas do Python refeitas no TS (perfil, sha dos turnos, fim)`, () => {
      const R = variante === "v21c" ? null : CV21D;
      let comExploracao = 0;
      for (const P of G.partidas.filter(p => p.variante === variante)) {
        const A = lutador(P.a, R), B = lutador(P.b, R), rot = `${variante} #${P.n} ${A.nome} x ${B.nome}`;
        for (const [py, ts] of PERFIL) {
          expect(Math.abs((A.cond[ts] as number) - P.perfil_a[py]), `${rot}: ${py} de a`).toBeLessThanOrEqual(1e-12);
          expect(Math.abs((B.cond[ts] as number) - P.perfil_b[py]), `${rot}: ${py} de b`).toBeLessThanOrEqual(1e-12);
        }
        const r = refazer(P, A, B, R);
        expect(r.txt, rot).toBe(P.turnos);
        expect(sha(r.txt), rot).toBe(P.sha256_turnos);
        expect([r.pontos, r.motivo, r.E.turno], rot).toEqual([P.pontos_a, P.motivo, P.n_turnos]);
        expect(Math.abs(r.E.L[0].hp - P.hp_a), `${rot}: vida final de a`).toBeLessThanOrEqual(1e-9);
        expect(Math.abs(r.E.L[1].hp - P.hp_b), `${rot}: vida final de b`).toBeLessThanOrEqual(1e-9);
        if (P.turnos.includes("exploracao")) comExploracao++;
      }
      expect(comExploracao).toBeGreaterThan(50);                 /* a exploracao injetada foi exercitada */
    });
  }

  test("o gabarito separa as variantes: partidas que mudam com a V21D (e so as com colosso, muralha ou vigia)", () => {
    const v = G.partidas.filter(p => p.variante === "v21c"), d = G.partidas.filter(p => p.variante === "a_c_e2v_v");
    const mudam = d.filter((p, i) => p.sha256_turnos !== v[i].sha256_turnos);
    expect(mudam.length).toBeGreaterThan(20);
    const envolvidos = (x: Desc) => ["muralha", "vigia", "tita", "colosso_partido"].includes(x.forma ?? "") || x.linha === "colosso";
    for (const p of mudam) expect(envolvidos(p.a) || envolvidos(p.b), `#${p.n}`).toBe(true);
  });
});

describe("combate V21D: so nos pets v6", () => {
  test("regras por versao: a V21D e a do v6 (funcao); o pet v13 joga a V21E em tempo real", () => {
    expect(regrasDaVersao(6)).toBe(CV21D);
    expect(new Motor(123).regras).toBe(CV21E_TR);
  });

  test("preparo sob pele: oculto so com a V21D", () => {
    const f: Forma = { esp: "brasa", est: "adulto", ramo: "sereno", linha: "colosso", adulta: "tita" };
    const tita = perfilDe(f, caraterCanonico("tita")), esp = perfilDe({ ...f, linha: "guardiao", adulta: "espelho" }, caraterCanonico("espelho"));
    let E = estadoV2(tita, esp);
    E = { ...E, dist: 0, L: E.L.map(x => ({ ...x, guts: x.gutsMax })) };
    E = resolverV2(E, "pele_dura", "defender").E;
    E = resolverV2(E, "preparar_pesado", "defender").E;
    expect([E.L[0].prep, E.L[0].prepPele]).toEqual([true, true]);
    const prep = { n: "oponente_preparando", p: [] };
    expect(valeCond(prep, E, 1, null)).toBe(true);
    expect(valeCond(prep, E, 1, null, CV21D)).toBe(false);
    /* sem a pele o preparo aparece nas duas */
    let E2 = estadoV2(tita, esp);
    E2 = { ...E2, dist: 0 };
    E2 = resolverV2(E2, "preparar_pesado", "defender").E;
    expect([valeCond(prep, E2, 1, null), valeCond(prep, E2, 1, null, CV21D)]).toEqual([true, true]);
  });

  test("bots: a muralha e o vigia com a lista variante so contra pet v6; o resto igual", () => {
    for (const f of FORMAS_AD) {
      expect(lutadorBot(f).estilo.gambits, f).toEqual(BOTS_V21[f]);
      expect(lutadorBot(f, CV21D).estilo.gambits, f).toEqual(gambitsAdulto(f, CV21D));
      expect(gambitsAdulto(f, CV21D) === BOTS_V21[f], f).toBe(f !== "muralha" && f !== "vigia");
    }
    for (const nome of ["npc_tier2_carcereiro", "npc_v5_puppetmon", "npc_tier2_porteiro"])
      expect(lutadorBot(nome, CV21D).estilo.gambits, nome).toEqual(lutadorBot(nome).estilo.gambits);
  });

  test("semente dos gambits: o pet v6 muralha ou vigia semeia a lista variante; as regras novas so saem da semente", () => {
    for (const adulta of ["muralha", "vigia"] as const) {
      const f: Forma = { esp: "limo", est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[adulta], adulta };
      const g5 = new GambitsPet(), g6 = new GambitsPet();
      g5.semear(f, adulta); g6.semear(f, adulta, CV21D);
      expect(g5.ativas).toEqual(BOTS_V21[adulta].regras.map(chaveRegra));
      expect(g6.ativas).toEqual(BOTS_V21D[adulta]!.regras.map(chaveRegra));
      expect(g6.estilo().gambits).toEqual(BOTS_V21D[adulta]);
    }
    for (const r of [REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE]) {
      expect(REPERTORIO.has(chaveRegra(r))).toBe(false);           /* o repertorio (candidatas) nao muda */
      expect(regraDe(chaveRegra(r))).toEqual(r);
    }
  });
});
