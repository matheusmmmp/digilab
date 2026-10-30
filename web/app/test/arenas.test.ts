/* Arenas com lideres (docs/DESIGN_MEDALHAS_ARENAS.md, secao 3; medalhas parte 2; pets v6, so no jogo): a tabela nova das
   medalhas e das arenas, cada regra (Torre: contra-golpe; Floresta: muda de padrao no turno 10; Cidadela: tres lutas
   seguidas sem cura; Lago: sem travas nem vetos), o replay de uma vida com lutas de arena. Pet v13 (o unico que ficou): as arenas sao as dos v9 e as lutas de arena jogam em tempo
   real; as regras de turno (Torre, Floresta) seguem testadas nas funcoes por turnos. */
import { afterEach, beforeAll, describe, expect, test } from "vitest";
import {
  ARENAS, ARENA_POR_ID, CAMPANHA_V5, CAMPANHA_V6, CAT, CTR, CV21E_TR, DUR_EVO, GAMBITS_ARENA, LUGARES_V6, MEDALHAS, NPC,
  arenaDaLuta, chaveRegra, gambitNPC, hashSemente, jogarArena, jogarLuta, jogarV2, lutadorBot, perfilNPC, sementeDaSerie,
} from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";
import { Motor } from "../motor/motor.ts";
import { Tamer, conferirMedalhas } from "../src/tamer.ts";

const escalaAntes = ESCALA.ligada;
afterEach(() => ligarEscala(escalaAntes));
const GUARDROMON = "npc_tier2_carcereiro", YOUKOMON = "npc_v6_youkomon", MYOTISMON = "npc_v5_myotismon", MARINBULLMON = "npc_v6_marinbullmon";

/** trata a lesao na hora (a vida de teste nao pode morrer de lesao sem tratar) */
function lutar(m: Motor, rival: string, s: number) {
  const r = m.lutar(rival, s);
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  return r;
}
/** primeira semente (de uma sequencia deterministica) em que a luta sai como `quer` (pela montagem pura, sem mexer no pet) */
function sementeQue(m: Motor, rival: string, quer: (serie: ReturnType<Motor["montarLuta"]>["serie"]) => boolean, rotulo: string): number {
  for (let k = 0; k < 400; k++) {
    const s = hashSemente(rotulo, m.semente, m.log.length, k);
    if (quer(m.montarLuta(rival, s).serie)) return s;
  }
  throw new Error(`nenhuma semente serve (${rotulo}, ${rival})`);
}
const venceTudo = (n: number) => (serie: { pontosA: number }[]) => serie.length === n && serie[serie.length - 1].pontosA === 1;
/** treina no estagio de agora ate o teto dele (sessoes com a fadiga baixa, esperando entre elas; o sono espera) */
function treinarNoEstagio(m: Motor): void {
  const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"] as const, est = m.estagioAtual as "crianca" | "adolescente" | "adulto";
  for (let k = 0; k < 400 && m.treino.pontosEst[est] < CTR.tetoEstagio[est]; k++) {
    if (m.treino.fadiga < CTR.fadigaSessao && m.treino.podeTocar(m.e.tick)) { try { m.treinar(EX[k % EX.length]); continue; } catch { /* dormindo */ } }
    m.avancar(30);
  }
  if (m.estagioAtual !== est) throw new Error("o pet de teste evoluiu no meio do treino");
}
/** um Ultimate v13 de registro legitimo (liberacoes, tempo, treino ate o teto de cada estagio e lutas de treino contra o
    aleatorio). Treinado: com a escala dos pets o pet sem treino quase nunca vence um lider (meta <= 0,05) */
function ultimateV13(semente: number, treinados: readonly string[] = ["crianca", "adolescente", "adulto"]): Motor {
  const m = new Motor(semente);
  m.liberar(3);
  const esperarEvoluir = (): void => { const est = m.estagioAtual; for (let j = 0; j < 200 && m.estagioAtual === est; j++) m.avancar(30); };
  const treinar = (): void => { if (treinados.includes(m.estagioAtual)) treinarNoEstagio(m); };
  m.avancar(DUR_EVO.bebe + 15);
  treinar();
  esperarEvoluir();
  treinar();
  let k = 0;
  while (m.sparring < CAT.sparring) lutar(m, "aleatorio", hashSemente("sp", semente, k++));
  /* a passagem para Ultimate pede a taxa de vitoria das lutas do estagio: se o tempo passou e ele nao evoluiu, luta mais */
  for (let j = 0; j < 40 && m.estagioAtual === "adolescente"; j++) { esperarEvoluir(); if (m.estagioAtual === "adolescente") lutar(m, "aleatorio", hashSemente("sp", semente, k++)); }
  if (m.estagioAtual !== "adulto") throw new Error("o pet de teste nao chegou a Ultimate");
  treinar();
  return m;
}
/** vence (com uma semente que ganha) o primeiro rival de cada lugar antes do lugar `L` */
function abrirAte(m: Motor, L: number): void {
  for (let i = 0; i < L; i++) {
    if (m.lugarVencido(i)) continue;
    const k = m.lugares[i].rivais[0], n = m.arenaDe(k)?.lutas ?? 1;
    lutar(m, k, sementeQue(m, k, venceTudo(n), "abrir"));
  }
}

describe("a tabela das medalhas e das arenas (pet v13)", () => {
  test("seis arenas na ordem do nivel; a 3a medalha vem do lider da Floresta e a 5a do lider do Lago", () => {
    expect(LUGARES_V6.map(L => L.nome)).toEqual(["Campina", "Torre de pedra", "Floresta", "Cidadela", "Lago", "Montanha Espiral"]);
    expect(LUGARES_V6.map(L => L.sugerido)).toEqual(["Rookie", "Champion", "Champion", "Ultimate", "Ultimate", "Mega"]);
    expect(MEDALHAS.map(md => [md.id, NPC[md.lider]!.nome, LUGARES_V6[md.lugar].nome])).toEqual([
      ["campina", "Gazimon", "Campina"], ["torre", "Guardromon", "Torre de pedra"], ["floresta", "Youkomon", "Floresta"],
      ["cidadela", "Myotismon", "Cidadela"], ["lago", "MarinBullmon", "Lago"], ["espiral", "Piedmon", "Montanha Espiral"]]);
    for (const md of MEDALHAS) {
      expect(md).not.toHaveProperty("provisoria");
      expect(LUGARES_V6[md.lugar].rivais).toContain(md.lider);
      const ar = ARENA_POR_ID[md.id];
      expect([ar.lider, ar.lugar]).toEqual([md.lider, md.lugar]);
    }
    expect(ARENAS.map(a => a.regra)).toEqual(["nenhuma", "paciencia", "leitura", "resistencia", "vinculo", "chefe"]);
  });
  test("os NPCs de antes continuam como desafiantes, com as mesmas chaves (o replay dos v6 ja salvos acha todos)", () => {
    const v6 = CAMPANHA_V6.map(c => c.k);
    for (const c of CAMPANHA_V5) expect(v6).toContain(c.k);
    expect(LUGARES_V6[1].rivais.map(k => NPC[k]!.nome)).toEqual(["Tortomon", "Guardromon", "Devidramon"]);
    expect(LUGARES_V6[5].rivais.map(k => NPC[k]!.nome)).toEqual(["Puppetmon", "Machinedramon", "Piedmon"]);
    const m = new Motor(1);
    expect(Object.keys(m.campanha)).toEqual(v6);
    expect(m.lugares).toBe(LUGARES_V6);
    expect(m.lugarDe(MYOTISMON)).toBe(3);
  });
  test("os lideres novos estao no atlas do jogo (sprites do Digimon UP) e nao sao formas de pet", () => {
    /* a chave do NPC e a do atlas (catalogo_sprites_up.json, fora do repo): aqui so o que o motor garante */
    expect(NPC[YOUKOMON]).toMatchObject({ nome: "Youkomon", est: "adolescente", estilo: "arena:floresta" });
    expect(NPC[MARINBULLMON]).toMatchObject({ nome: "MarinBullmon", est: "adulto" });
  });
});

describe("as regras das arenas", () => {
  beforeAll(() => ligarEscala(true));
  test("o pet v13 tem a arena contra o lider; os desafiantes lutam sem arena", () => {
    /* a arena e a do pet v6 em diante; so o fator do lider e calibrado por versao */
    for (const a of ARENAS) expect(arenaDaLuta(a.lider, 13)).toEqual({ ...a, fator: arenaDaLuta(a.lider, 13)!.fator });
    expect(arenaDaLuta("npc_tier2_sentinela", 13)).toBeNull();
    const m = new Motor(3);
    expect(m.regras).toBe(CV21E_TR);
    expect(m.arenaDe(GUARDROMON)).toEqual(arenaDaLuta(GUARDROMON, 13));
    expect(m.arenaDe(GUARDROMON)!.id).toBe("torre");
  });
  test("Torre de pedra (paciencia): o lider tem o contra-golpe e as regras dele, e devolve o golpe forte", () => {
    ligarEscala(true);
    const m = new Motor(5), B = m.lutadores(GUARDROMON).B, R = m.regras;
    expect(B.cond.tecnica).toBe("contra_golpe");
    expect(B.estilo.gambits!.regras.filter(r => r.entao === "contra_golpe").length).toBeGreaterThan(0);
    /* escala dos pets v6: a lista propria da Torre; contra quem atira com frequencia ele vai buscar (nao contra-golpeia) */
    expect(B.estilo.gambits).toEqual(GAMBITS_ARENA.torre);
    expect(B.estilo.gambits!.regras.find(r => r.se.some(c => c.n === "oponente_frequente" && c.p[0] === "disparo"))!.entao).toBe("avancar");
    expect(lutadorBot(GUARDROMON, R).cond.tecnica).toBeNull();       /* fora da luta de arena, o de sempre */
    expect(gambitNPC("v21:espelho", R).regras.some(r => r.entao === "contra_golpe")).toBe(false);
    /* um brigao que prepara o pesado de perto leva o golpe de volta */
    const brig = { nome: "brigao", estilo: { nome: "b", gambits: { regras: [{ se: [{ n: "distancia_eh", p: [1] }], entao: "avancar" },
      { se: [{ n: "distancia_eh", p: [0] }], entao: "preparar_pesado" }], final: "carregar" }, eps: 0 }, cond: perfilNPC(90, "adulto", 600) };
    let devolveu = 0;
    for (let s = 0; s < 20; s++) for (const tr of jogarV2(brig, B, s, R).turnos)
      if (tr.b === "contra_golpe" && (tr.a === "pesado" || tr.a === "golpe_rapido") && tr.dano[0] > 0) devolveu++;
    expect(devolveu).toBeGreaterThan(0);
  });
  test("Floresta (leitura): o lider muda de padrao no turno 10 (as regras de turno so disparam dali em diante)", () => {
    ligarEscala(true);
    const m = new Motor(6), B = m.lutadores(YOUKOMON).B, R = m.regras, g = B.estilo.gambits!;
    expect(g.regras.map(chaveRegra)).toEqual(GAMBITS_ARENA.floresta.regras.map(chaveRegra));
    const deTurno = g.regras.map(r => r.se.some(c => c.n === "turno_execucao" && c.p[0] === 10));
    const A = { nome: "alvo", estilo: { nome: "a", gambits: { regras: [], final: "defender" }, eps: .3 }, cond: perfilNPC(90, "adulto", 600) };
    const antes = new Set<string>(), depois = new Set<string>();
    for (let s = 0; s < 30; s++) for (const tr of jogarV2(A, B, s, R).turnos) {
      if (typeof tr.mb !== "number" || tr.mb >= g.regras.length) continue;
      if (deTurno[tr.mb]) { expect(tr.antes.turno).toBeGreaterThanOrEqual(10); depois.add(tr.b); }
      else if (tr.antes.turno < 10) antes.add(tr.b);
    }
    expect([...antes].sort()).toEqual(expect.arrayContaining(["disparo", "recuar"]));
    expect([...depois]).toEqual(expect.arrayContaining(["avancar", "golpe_rapido"]));
    expect(antes.has("golpe_rapido")).toBe(false);
  });
  test("Cidadela (resistencia): tres lutas seguidas sem cura; para na primeira que nao for vitoria", () => {
    ligarEscala(true);
    const m = ultimateV13(101), { A, B, arena } = m.lutadores(MYOTISMON);
    expect(arena).toEqual(ARENA_POR_ID.cidadela);
    expect(arena!.lutas).toBe(3);
    for (let s = 0; s < 40; s++) {
      const serie = jogarArena(A, B, s, m.regras, 3);
      expect(serie.length).toBeLessThanOrEqual(3);
      serie.forEach((res, k) => {
        if (k < serie.length - 1) expect(res.pontosA).toBe(1);
        expect(res.E0.L[1].hp).toBe(B.cond.hpMax);                                   /* o lider volta inteiro */
        if (k) {
          expect(res.E0.L[0].hp).toBe(serie[k - 1].E.L[0].hp);                       /* a vida passa */
          expect(res.E0.L[0].guts).toBe(Math.min(serie[k - 1].E.L[0].guts, A.cond.gutsMax));   /* e o guts */
          expect(res).toEqual(jogarLuta(A, B, sementeDaSerie(s, k), m.regras, { hp: serie[k - 1].E.L[0].hp, guts: serie[k - 1].E.L[0].guts }));
        } else expect(res).toEqual(jogarLuta(A, B, s, m.regras));
      });
    }
  });
  test("Cidadela: a medalha e a vitoria no lugar so vem com as tres vitorias", () => {
    ligarEscala(true);
    /* treinado so no Rookie: forte o bastante para vencer as tres, fraco o bastante para perder no meio */
    const m = ultimateV13(101, ["crianca"]), t = new Tamer();
    abrirAte(m, 3);
    for (const md of conferirMedalhas(t, m)) expect(["campina", "torre", "floresta"]).toContain(md.id);
    /* perde no meio: nada conta, mas as lutas jogadas contam (e ensinam) */
    const lutasAntes = m.lutas.lutas;
    const r1 = lutar(m, MYOTISMON, sementeQue(m, MYOTISMON, s => s.length >= 2 && s[s.length - 1].pontosA !== 1, "meio"));
    expect(r1.venceu).toBe(false);
    expect(r1.serie.length).toBeGreaterThanOrEqual(2);
    expect(m.lutas.lutas - lutasAntes).toBe(r1.serie.length);
    expect(m.campanha[MYOTISMON]).toBe(0);
    expect(m.lugarVencido(3)).toBe(false);
    expect(conferirMedalhas(t, m).map(x => x.id)).not.toContain("cidadela");
    /* vence as tres */
    const r2 = lutar(m, MYOTISMON, sementeQue(m, MYOTISMON, venceTudo(3), "tres"));
    expect(r2.venceu).toBe(true);
    expect(r2.serie).toHaveLength(3);
    expect(m.campanha[MYOTISMON]).toBe(1);
    expect(m.desafioAberto(MARINBULLMON)).toBe(true);
    expect(conferirMedalhas(t, m).map(x => x.id)).toEqual(["cidadela"]);
  });
  test("Lago (vinculo): as travas e os vetos do dono nao valem; sem eles, a lista e a de sempre", () => {
    ligarEscala(true);
    const m = ultimateV13(404), gp = m.gp!;
    expect(m.lutadores(MARINBULLMON).usadas).toEqual(gp.ativas);   /* sem intervencao: a mesma lista */
    const terceira = gp.ativas[2], ultima = gp.ativas[gp.ativas.length - 1];
    m.intervirGambit("vetar", terceira);
    m.intervirGambit("travar", ultima);
    const ativa = m.gp!.ativas, sozinho = m.lutadores(MARINBULLMON);
    expect(ativa).not.toContain(terceira);
    expect(sozinho.usadas).toContain(terceira);                     /* o veto nao vale */
    expect(sozinho.usadas).toEqual(m.gp!.listaSozinho());
    const porNota = [...sozinho.usadas!].sort((a, b) => m.gp!.notas[b] - m.gp!.notas[a]);
    expect(sozinho.usadas).toEqual(porNota);                        /* a trava nao vale: so a nota ordena */
    expect(sozinho.A.estilo.gambits!.regras.map(chaveRegra)).toEqual(sozinho.usadas);
    expect(m.lutadores("npc_tier2_sentinela").usadas).toEqual(ativa);   /* fora do Lago, a lista do dono */
    /* a luta do Lago ensina pelas regras com que ele lutou */
    abrirAte(m, 4);
    const notas = { ...m.gp!.notas }, r = lutar(m, MARINBULLMON, hashSemente("lago", 1));
    const disparou = new Set(r.res.turnos.filter(tr => typeof tr.ma === "number" && tr.ma < r.usadas!.length).map(tr => r.usadas![tr.ma as number]));
    for (const k of disparou) expect(m.gp!.notas[k]).not.toBe(notas[k]);
  });
});

describe("replay com as lutas de arena", () => {
  test("uma vida v13 com Torre, Floresta, Cidadela (serie) e Lago (com trava e veto): o replay da a mesma assinatura", () => {
    ligarEscala(true);
    const m = ultimateV13(101);
    abrirAte(m, 3);
    lutar(m, GUARDROMON, hashSemente("rev", 1));
    lutar(m, YOUKOMON, hashSemente("rev", 2));
    lutar(m, MYOTISMON, sementeQue(m, MYOTISMON, s => s.length >= 2, "rev3"));
    abrirAte(m, 4);
    m.intervirGambit("vetar", m.gp!.ativas[1]);
    m.intervirGambit("travar", m.gp!.ativas[m.gp!.ativas.length - 1]);
    lutar(m, MARINBULLMON, hashSemente("rev", 4));
    m.avancar(60);
    const eventos = m.log.filter(e => e[1] === "l").map(e => (e[2] as { r: string }).r);
    for (const k of [GUARDROMON, YOUKOMON, MYOTISMON, MARINBULLMON]) expect(eventos).toContain(k);
    /* o evento de luta continua so com rival e semente */
    for (const e of m.log.filter(x => x[1] === "l")) expect(Object.keys(e[2] as object).sort()).toEqual(["r", "s"]);
    const r = Motor.reproduzir(m.semente, m.log, 13);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.campanha).toEqual(m.campanha);
  });
});
