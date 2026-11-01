// O pet v14 (docs/TAREFA_V3_COMBATE_V14.md, B2): o jogo passa a nascer pets v14, que lutam exatamente com o candidato que a conferencia unica da
// rodada 2 mediu (docs/EQUILIBRIO_COMBATE_TR.md, R2-5; scripts/equilibrio_tr/fase4_progressao.ts). Os pets v13 seguem vivos (CV14-1) e as
// vidas deles nao mudam (test/vidas_v13.test.ts). Aqui: a versao, o replay do pet v14 e a luta v14 do jogo contra a luta da bancada, com a
// mesma semente e o mesmo par.
import { afterAll, beforeAll, describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import {
  ARENAS, CESC_V9, CV, CV21E_TR, ESPECIES, FATORES_V14, FATOR_RIVAL_FABRICA_V9, FORMAS_AD, GambitsPet, LIGA, LINHA_DA_FORMA, LISTAS_LIDER_V14, LISTAS_V14,
  Motor, NPC, PetMorto, RELOGIO_V14, TPD, VERSAO_PET, VERSOES_PET, alugueisFabrica, arenaDaLuta, caraterCanonico, copiarGambits, ehV14, formaLiga, formaRivalFabrica,
  formaRivalInstalacao, formaRivalSalao, gambitsAdulto, hashSemente, jogarTR, lutadorBot, lutadorLiga, megaFabrica, perfilDe, regrasDaVersao, regraFabrica, rivalInstalacao,
  rivalSalao, sementeDe, ESTAGIOS_SALAO, type EventoRegistro, type Forma, type FormaAdultaNormal, type Lutador, type RegrasLuta,
} from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";

const sha = (x: string): string => createHash("sha256").update(x).digest("hex");
const R14 = regrasDaVersao(14);
/** as regras da bancada da conferencia: as v13 com o relogio candidato (fase4_progressao.ts) */
const RB: RegrasLuta = { ...CV21E_TR, relogio: RELOGIO_V14 };
let escalaAntes = false;
beforeAll(() => { escalaAntes = ESCALA.ligada; ligarEscala(true); });
afterAll(() => ligarEscala(escalaAntes));

describe("a versao 14", () => {
  test("os ovos novos nascem v15 (o v14 com a bola no golpe), e a v13 e a v14 seguem abrindo (CV14-1)", () => {
    expect(VERSAO_PET).toBe(15);
    expect(VERSOES_PET).toEqual([13, 14, 15]);
    expect(new Motor(1).versao).toBe(15);
    expect(new Motor(1, 14).versao).toBe(14);
    expect(new Motor(1, 13).versao).toBe(13);
    expect(regrasDaVersao(15)).toBe(regrasDaVersao(14));
    expect(() => new Motor(1, 12)).toThrow(/versão de pet desconhecida/);
    expect(regrasDaVersao(13)).toBe(CV21E_TR);
    expect(ehV14(R14)).toBe(true);
    expect(ehV14(CV21E_TR)).toBe(false);
    expect(() => regrasDaVersao(12)).toThrow();
  });
  test("o replay de um pet v14 e bit a bit, e o GambitsPet dele liga o candidato (so nos v14)", () => {
    const viver = (versao: number): Motor => {
      const m = new Motor(1407, versao), rivais = ["aleatorio", "npc_tier1_brutamontes", "npc_tier2_sentinela", "duelista"];
      let k = 0;
      for (let p = 0; p < Math.round(4 * TPD / 30) && !m.morte; p++) {
        m.avancar(30);
        const r = hashSemente("pet-v14", p) % 100;
        try {
          if (m.e.fome < .6 && p % 2 === 0) m.observar("alimentar");
          if (m.e.sujeira >= 2) m.observar("limpar");
          if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
          if (m.medalhas < 3) m.liberar(3);
          if (m.estagioAtual !== "bebe" && r < 30) m.treinar(["corrida", "alvo", "meditar"][k++ % 3] as never);
          if (m.estagioAtual !== "bebe" && r >= 30 && r < 60) m.lutar(rivais[k++ % rivais.length], hashSemente("luta", m.semente, m.log.length), null);
        } catch (err) { if (err instanceof PetMorto) throw err; /* o motor recusou: segue */ }
      }
      return m;
    };
    for (const versao of [14, 13]) {
      const m = viver(versao);
      expect(m.gp, "o pet chegou ao Rookie").not.toBeNull();
      expect(m.regras).toBe(regrasDaVersao(versao));
      expect(m.gp!.reservaNoFim).toBe(versao === 14);
      expect(m.gp!.chipAntes).toBe(versao === 14);
      expect(m.gp!.aprendizadoTR !== null).toBe(versao === 14);
      expect(m.log.some(ev => ev[1] === "l"), "o pet lutou").toBe(true);
      const x = new Motor(m.semente, versao);
      m.log.forEach((ev: EventoRegistro) => x.aplicarEvento(ev));
      expect(sha(x.assinatura())).toBe(sha(m.assinatura()));
      expect(sha(Motor.reproduzir(m.semente, m.log, versao).assinatura())).toBe(sha(m.assinatura()));
    }
  });
});

/** a forma do lutador e a lista candidata (a do pet adulto da bancada) */
function pet(adulta: FormaAdultaNormal, est: Forma["est"], versao: number): Lutador {
  const f: Forma = { esp: "brasa", est, ramo: "sereno", linha: LINHA_DA_FORMA[adulta], adulta };
  return { nome: "pet", estilo: { nome: adulta, gambits: copiarGambits(LISTAS_V14[adulta] ?? gambitsAdulto(adulta, RB)), eps: CV.eps }, cond: perfilDe(f, caraterCanonico(adulta), 1, null, true, versao, true) };
}
const comLista = (L: Lutador, id: string): Lutador => LISTAS_V14[id] ? { ...L, estilo: { ...L.estilo, gambits: copiarGambits(LISTAS_V14[id]) } } : L;
const comFator = (L: Lutador, de: number, para: number): Lutador => ({ ...L, cond: { ...L.cond, escala: L.cond.escala! / de * para } });
/** a luta do jogo (R14) contra a da bancada (RB) com o mesmo pet de cada lado: o mesmo resultado inteiro */
function igual(nome: string, jogo: Lutador, bancada: Lutador, semente: number): void {
  expect(jogo.cond, nome).toEqual(bancada.cond);
  expect(jogo.estilo.gambits, nome).toEqual(bancada.estilo.gambits);
  for (const adulta of ["duelista", "sentinela", "tita"] as FormaAdultaNormal[]) {
    const a = jogarTR(pet(adulta, "mega", 14), jogo, semente, { R: R14, desafiado: 1 });
    const b = jogarTR(pet(adulta, "mega", 13), bancada, semente, { R: RB, desafiado: 1 });
    /* menos `entrada` (a entrada da luta, com as regras R, que e o que muda de proposito: a v14 sem o relogio no objeto, a bancada com ele) */
    expect({ ...a, entrada: null }, `${nome} x ${adulta}`).toEqual({ ...b, entrada: null });
  }
}

describe("a luta v14 do jogo e a da bancada da conferencia (R2-5)", () => {
  test("os lideres das arenas: o fator e a lista candidata", () => {
    for (const a of ARENAS) {
      const arena = arenaDaLuta(a.lider, 14)!;
      expect(arena.fator, a.id).toBe(FATORES_V14.lider[a.id]);
      const B = lutadorBot(a.lider, RB, { ...arenaDaLuta(a.lider, 13)!, fator: FATORES_V14.lider[a.id] });
      const L = LISTAS_LIDER_V14[a.id];
      igual("lider " + a.id, lutadorBot(a.lider, R14, arena), L ? { ...B, estilo: { ...B.estilo, gambits: copiarGambits(L) } } : B, hashSemente("pet-v14-lider", a.id));
    }
  });
  test("os desafiantes da campanha: o fator proprio (G-2), e os que nao tem ficam como na v13", () => {
    for (const k of Object.keys(FATORES_V14.npc))
      igual("npc " + k, lutadorBot(k, R14), comFator(lutadorBot(k, RB), CESC_V9.fatorNpc[k], FATORES_V14.npc[k]), hashSemente("pet-v14-npc", k));
    for (const k of Object.keys(NPC)) if (!(k in FATORES_V14.npc)) expect(lutadorBot(k, R14), k).toEqual(lutadorBot(k, CV21E_TR));
  });
  test("a Liga: o fator de cada lider e a lista candidata (G-3)", () => {
    LIGA.forEach((x, i) => igual("liga " + x.arena, lutadorLiga(i, R14), comLista(lutadorLiga(i, RB, FATORES_V14.liga[x.arena]), x.adulta), hashSemente("pet-v14-liga", i)));
  });
  test("as instalacoes (G-4): a semente de cada tentativa", () => {
    for (let s = 1; s <= 6; s++) {
      const f = formaRivalInstalacao(s, 0);
      igual("instalacao " + s, rivalInstalacao(s, 0, R14), comLista(rivalInstalacao(s, 0, RB, FATORES_V14.instalacao), f.adulta!), hashSemente("pet-v14-torre", s));
    }
  });
  test("o Salao (G-6): cada nivel", () => {
    for (const est of ESTAGIOS_SALAO) for (let s = 1; s <= 4; s++) {
      const f = formaRivalSalao(s, est), id = f.adulta ?? f.linha ?? f.ramo!;
      igual(`salao ${est} ${s}`, rivalSalao(s, est, R14), comLista(rivalSalao(s, est, RB, FATORES_V14.salao[est]), id), hashSemente("pet-v14-salao", est, s));
    }
  });
  test("a Fabrica (G-5): as regras v14, o fator dos rivais e as listas dos alugados e dos rivais", () => {
    const regra = regraFabrica(14);
    expect(regra.R).toBe(R14);
    expect(regra.fatorRival).toBe(FATORES_V14.fabrica);
    expect(regraFabrica(13).fatorRival).toBe(FATOR_RIVAL_FABRICA_V9);
    for (let s = 1; s <= 4; s++) {
      const f = formaRivalFabrica(s, 0);
      igual("fabrica " + s, megaFabrica(f, "r", regra.fatorRival, R14), comLista(megaFabrica(f, "r", FATORES_V14.fabrica, RB), f.adulta!), hashSemente("pet-v14-fabrica", s));
      for (const al of alugueisFabrica(s)) expect(megaFabrica(al, "a", 1, R14).estilo.gambits, al.adulta).toEqual(LISTAS_V14[al.adulta!] ?? megaFabrica(al, "a", 1, CV21E_TR).estilo.gambits);
    }
  });
  test("o pet v14 semeia a lista candidata da forma; o v13, a de sempre", () => {
    for (const adulta of FORMAS_AD) {
      const f: Forma = { esp: "brasa", est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[adulta], adulta };
      expect(sementeDe(f, R14), adulta).toEqual(LISTAS_V14[adulta] ?? sementeDe(f, CV21E_TR));
      const gp = new GambitsPet();
      gp.chipsNoFim = true; gp.reservaNoFim = true; gp.semear(f, adulta, R14);
      expect(gp.estilo().gambits!.regras.length, adulta).toBeGreaterThan(0);
    }
    expect(ESPECIES.length).toBe(4);
    expect(formaLiga(0).est).toBe("mega");
  });
});
