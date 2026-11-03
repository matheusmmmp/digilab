/* Evolucao canonica (docs/DESIGN_EVOLUCAO_CANONICA.md): Champion -> Ultimate -> Mega no pet v13 (o unico que ficou no motor;
   as medalhas liberam as evolucoes, entao os helpers dao as 5 de uma vez). */
import { afterEach, describe, expect, test } from "vitest";
import { ACOES_DONO_JOGO_V11, CAT, CD, CESC_V9, CMD, CMG, CSO, CTR, DUR_EVO, ESPECIES, LINHAS, TICK_INICIAL, TPD, VERSAO_PET } from "../motor/constantes.ts";
import { CAMPANHA_V6, LUGARES_V6, NPC } from "../motor/bots.ts";
import { ESCALA, ligarEscala, perfilDe } from "../motor/catalogo.ts";
import { criarDono, type VisaoDono } from "../motor/donos.ts";
import { lutadorBot } from "../motor/gambits_pet.ts";
import { Motor } from "../motor/motor.ts";
import { DIGIMON_DA_FORMA, chaveSprite, nomeEstagio, nomeForma, nomeFormaLegado } from "../motor/nomes.ts";
import { criarRng, hashSemente } from "../motor/rng.ts";
import { TreinoPet } from "../motor/treino.ts";
import type { Forma, FormaAdultaNormal } from "../motor/tipos.ts";

const INI_ADOL = TICK_INICIAL + DUR_EVO.bebe + DUR_EVO.crianca;
const escalaAntes = ESCALA.ligada;
afterEach(() => ligarEscala(escalaAntes));

/** adulto (Ultimate) sem passar pelo dono: o sparring e as vitorias do estagio postos a mao (so para testar a regra) */
function ultimate(s: number, sobrecarga = 0): Motor {
  const m = new Motor(s, 13);
  m.liberar(CMD.mega);
  m.avancar(INI_ADOL - TICK_INICIAL + 15);
  m.sparring = CAT.sparring;
  m.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 };
  m.treino.sobrecarga = sobrecarga;
  m.avancar(DUR_EVO.adolescente);
  expect(m.estagioAtual).toBe("adulto");
  return m;
}
/** uma vida de verdade com o dono simulado (cuida da lesao e luta na arena ate qualificar), para o replay */
function vida(tipo: "aleatorio" | "atencioso", semente: number, dias: number): Motor {
  const m = new Motor(semente, 13), dono = criarDono(tipo), r = criarRng(hashSemente("dono", semente, tipo));
  const passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0;
  m.liberar(CMD.mega);
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, r).filter(a => ACOES_DONO_JOGO_V11.includes(a));
    if (m.lesionadoDesde !== null && acoes.length) acoes[0] = "tratar_lesao";
    for (const a of acoes) { m.observar(a); gasto++; }
    if ((m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) || (m.estagioAtual === "adulto" && m.lutas.lutas < 12))
      m.lutar("aleatorio", hashSemente("sparring", semente, p));
  }
  return m;
}

describe("nomes e sprites no canone", () => {
  test("as duas formas da linha sao o Ultimate da cadeia; o Mega e o da forma de sinal -", () => {
    for (const esp of ESPECIES) for (const l of LINHAS) {
      const [mais, menos] = (Object.entries(CAT.adulto[l].formas) as [FormaAdultaNormal, { sinal: number }][]).sort((a, b) => b[1].sinal - a[1].sinal).map(x => x[0]);
      const f = (adulta: FormaAdultaNormal, mega = false): Forma => ({ esp, est: mega ? "mega" : "adulto", ramo: "sereno", linha: l, adulta });
      expect(chaveSprite(f(mais))).toBe(chaveSprite(f(menos)));
      expect(DIGIMON_DA_FORMA[chaveSprite(f(menos))][1]).toBe("Ultimate");
      expect(DIGIMON_DA_FORMA[chaveSprite(f(menos, true))][1]).toBe("Mega");
      expect(chaveSprite(f(mais, true))).toBe(`${esp}_adulto_${menos}`);
      expect(nomeEstagio(f(menos))).toBe("Ultimate"); expect(nomeEstagio(f(mais, true))).toBe("Mega");
      /* o rotulo antigo (que entra na assinatura dos pets v1-v4) nao muda */
      expect(nomeFormaLegado(f(menos))).toBe(DIGIMON_DA_FORMA[`${esp}_adulto_${menos}`][0]);
    }
    expect(nomeForma({ esp: "brasa", est: "adulto", ramo: "sereno", linha: "brigao", adulta: "furioso" })).toBe("MetalGreymon");
    expect(nomeForma({ esp: "brasa", est: "adulto", ramo: "sereno", linha: "brigao", adulta: "furioso", est: "mega" })).toBe("WarGreymon");
    /* a sombria usa o Ultimate da linha */
    expect(nomeForma({ esp: "brasa", est: "adulto", ramo: "sereno", linha: "brigao", adulta: "devastador" })).toBe("MetalGreymon sombrio");
    expect(nomeFormaLegado({ esp: "brasa", est: "adulto", ramo: "sereno", linha: "brigao", adulta: "devastador" })).toBe("WarGreymon sombrio");
  });
});

describe("Ultimate -> Mega (pet v13)", () => {
  test("ovos novos sao v13 (v5 + medalhas + confianca + combate equilibrado + vinculo B + o cerebro A e o corpo + o mundo fisico + a luta em tempo real)", () => { expect(VERSAO_PET).toBe(15); expect(new Motor(1).versao).toBe(15); });

  test("com tempo, lutas, vitorias e vinculo vira Mega: estagio novo, com a forma adulta do Ultimate", () => {
    const m = ultimate(3101), adulta = m.forma.adulta;
    expect(m.requisitosMega()!.tempo).toBe(false);
    m.lutas = { lutas: 10, vitorias: 9, derrotas: 1, empates: 0, lesoes: 0, tratadas: 0 };
    /* no vinculo B (v13) o vinculo parado nao cai com o tempo (nasce em 0,5, acima do limiar): posto a mao, para o registro da evolucao */
    m.vinc.valor = .8; m.avancar(m.requisitosMega()!.falta - 2); expect(m.estagioAtual).toBe("adulto"); m.avancar(3);
    expect(m.estagioAtual).toBe("mega");
    expect(m.forma.est).toBe("mega");
    expect(m.forma.adulta).toBe(adulta);
    const ev = m.evolucoes[m.evolucoes.length - 1];
    expect(ev.estagio).toBe("mega"); expect(ev.vinculo).toBe(.8);
    expect(m.gp!.linha).toBe(nomeForma(m.forma));
    expect(m.treino.estagio).toBe("mega");
    expect(m.requisitosMega()).toBeNull();
  });

  test("sem vinculo, sem as vitorias ou antes do tempo: continua Ultimate", () => {
    for (const [vinc, vit] of [[CMG.vinculo - .1, 10], [.9, 7]] as const) {
      const m = ultimate(3202);
      m.lutas = { lutas: 10, vitorias: vit, derrotas: 10 - vit, empates: 0, lesoes: 0, tratadas: 0 };
      m.vinc.valor = vinc;
      m.avancar(CMG.durRapida + 60);
      expect(m.estagioAtual).toBe("adulto");
    }
    const m = ultimate(3303);
    m.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 };
    m.vinc.valor = .9;
    m.avancar(CMG.durRapida - 30);
    expect(m.estagioAtual).toBe("adulto");
  });

  test("a sombria nunca vira Mega, nem com vinculo acima do limiar", () => {
    const m = ultimate(3404, CSO.sombrio + 10);
    expect(m.sombria).toBe(true);
    m.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 };
    m.avancar(CMG.durRapida - 2); m.vinc.valor = Math.min(.95, m.vinc.teto); m.avancar(3);
    expect(m.vinc.valor).toBeGreaterThanOrEqual(CMG.vinculo);
    expect(m.estagioAtual).toBe("adulto");
    expect(m.requisitosMega()).toBeNull();
  });

  test("o Mega e mais forte: vida e guts x multEstagio", () => {
    const f: Forma = { esp: "cirro", est: "adulto", ramo: "sereno", linha: "cacador", adulta: "emboscador" };
    const u = perfilDe(f, null), g = perfilDe({ ...f, est: "mega" }, null);
    expect(g.hpMax).toBeCloseTo(u.hpMax * CMG.multEstagio, 9);
    expect(g.gutsMax).toBeCloseTo(u.gutsMax * CMG.multEstagio, 9);
    expect(g.passiva).toBe(u.passiva);
  });

  test("treino do Mega: teto proprio do estagio e teto de vida maior", () => {
    const t = new TreinoPet("brasa");
    t.pontos = { vigor: 6, folego: 6, recuperacao: 6, forca: 6, mira: 6, guarda: 6 };
    t.avancar(TICK_INICIAL, false, true, "adulto");
    expect(t.sessao(TICK_INICIAL, "corrida", true).ganho).toEqual({ folego: 0, recuperacao: 0 });
    t.avancar(TICK_INICIAL + 100, false, true, "mega");
    const s = t.sessao(TICK_INICIAL + 100, "corrida", true);
    expect(s.ganho.folego! + s.ganho.recuperacao!).toBeGreaterThan(0);
    expect(t.total).toBeLessThanOrEqual(CMG.tetoVida);
    expect(t.pontosEst.mega).toBeGreaterThan(0);
    expect(CMG.tetoVida).toBeGreaterThan(CTR.tetoVida);
  });

  test("vida com o dono simulado chega ao Mega e o replay reconstroi igual", () => {
    const m = vida("aleatorio", 2002, 3);
    expect(m.estagioAtual).toBe("mega");
    const r = Motor.reproduzir(m.semente, m.log, m.versao);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.forma).toEqual(m.forma);
  });

  test("herança: Mega cruza, e o filho e da versao atual", () => {
    const p = ultimate(3606), q = ultimate(3707);
    p.lutas = { lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 }; p.avancar(CMG.durRapida - 2); p.vinc.valor = .9; p.avancar(3);
    expect(p.estagioAtual).toBe("mega");
    expect(Motor.cruzar(p, q, 12, 13, "t").versao).toBe(VERSAO_PET);
  });
});

describe("campanha do pet v13", () => {
  test("o pet v13 tem a campanha de seis lugares, com a Montanha Espiral", () => {
    const m = new Motor(1, 13);
    expect(Object.keys(m.campanha)).toEqual(CAMPANHA_V6.map(c => c.k));
    expect(m.lugares).toBe(LUGARES_V6);
    expect(LUGARES_V6.map(L => L.nome)).toEqual(["Campina", "Torre de pedra", "Floresta", "Cidadela", "Lago", "Montanha Espiral"]);
    expect(LUGARES_V6[5].rivais.map(k => NPC[k]!.nome)).toEqual(["Puppetmon", "Machinedramon", "Piedmon"]);
    expect(LUGARES_V6[3].rivais.map(k => NPC[k]!.nome)).toEqual(["Myotismon"]);
  });

  test("um pet nao luta contra NPC fora da campanha dele", () => {
    const m = new Motor(7, 13); m.avancar(DUR_EVO.bebe + 30);
    expect(() => m.lutar("npc_tier3_soberano", 1)).toThrow(/não está na campanha/);
  });

  test("na escala, os NPCs da Espiral tem E pela vida do Mega; o Myotismon e o Piedmon de sempre", () => {
    ligarEscala(true);
    const piedmon5 = lutadorBot("npc_v5_piedmon"), myot = lutadorBot("npc_v5_myotismon"), sob = lutadorBot("npc_tier3_soberano");
    expect(piedmon5.cond.escala).toBeCloseTo(CESC_V9.vida.mega * NPC.npc_v5_piedmon!.fator!, 9);   /* a escala do v13 (CESC_V9) */
    expect(piedmon5.cond.est).toBe("mega");
    expect(myot.cond).toEqual(sob.cond);
    expect([myot.estilo.gambits, myot.estilo.eps]).toEqual([sob.estilo.gambits, sob.estilo.eps]);
  });

});
