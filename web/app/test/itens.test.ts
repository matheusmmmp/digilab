/* Itens do Tamer (medalhas, parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13; so no jogo e so nos pets v6): o catalogo, cada item
   fazendo o que diz (chip de stat dentro dos tetos, chip de regra na lista, cartas na luta), as vagas pelas medalhas, os eventos "i" e
   "k" no registro do pet e o replay com eles, o inventario no registro do Tamer (item da medalha, carta da revanche com a espera, carta
   usada) e os pets v1-v5 e os v6 sem item intactos. */
import { describe, expect, test } from "vitest";
import {
  CARTA_DA_REVANCHE, CAT, CIT, CTR, CV, DUR_EVO, ITENS, ITEM_DA_MEDALHA, MEDALHAS, Motor, STATS, TECNICAS, bonusChipsStat, cartaDe, chaveRegra,
  chipDe, chipServe, comCarta, hashSemente, itemDe, jogarArena, jogarV2, lutadorBot, lutadorPet, vagasDeChip, type Estagio, type EventoRegistro,
  type Stats,
} from "../motor/index.ts";
import { CHAVE, textoSave, type Armazenamento } from "../src/save.ts";
import { iniciarJogo, jogoAtual, mudarTamer, tamerAtual } from "../src/jogo.ts";
import {
  CHAVE_TAMER, Tamer, conferirItensDasMedalhas, conferirRevanche, gravarTamer, lerTamer, porqueSemCarta, type EventoTamer,
} from "../src/tamer.ts";

const zeros = (): Stats => Object.fromEntries(STATS.map(k => [k, 0])) as Stats;
const soma = (s: Stats | null): number => (s ? STATS.reduce((a, k) => a + s[k], 0) : 0);
const armaz = (dados: Record<string, string> = {}) => {
  const a: Armazenamento & { dados: Record<string, string> } = { dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } };
  return a;
};
const RECUO = chaveRegra((chipDe("chip_recuo") as { regra: Parameters<typeof chaveRegra>[0] }).regra);
const PERSEGUIDOR = chaveRegra((chipDe("chip_perseguidor") as { regra: Parameters<typeof chaveRegra>[0] }).regra);

/** luta e trata a lesao na hora (o pet de teste nao morre) */
function lutarCuidando(m: Motor, rival: string, s: number): void { m.lutar(rival, s); if (m.lesionadoDesde !== null) m.observar("tratar_lesao"); }
/** Champion -> Ultimate: as lutas de treino e o tempo (o pet ja conhece as 3 medalhas) */
function virarUltimate(m: Motor): void {
  let k = 0;
  while (m.sparring < CAT.sparring) lutarCuidando(m, "aleatorio", hashSemente("sp", m.semente, k++));
  for (let j = 0; j < 40 && m.estagioAtual === "adolescente"; j++) { m.avancar(60); if (m.estagioAtual === "adolescente") lutarCuidando(m, "aleatorio", hashSemente("sp", m.semente, k++)); }
  if (m.estagioAtual !== "adulto") throw new Error("o pet de teste nao chegou a Ultimate");
}
/** pet v6 no estagio pedido, sem treino, com `medalhas` conhecidas desde o comeco */
function petV6(semente: number, est: Estagio, medalhas: number): Motor {
  const m = new Motor(semente, 6);
  if (medalhas) m.liberar(medalhas);
  const esperar = (alvo: Estagio): void => { for (let j = 0; j < 400 && m.estagioAtual !== alvo; j++) m.avancar(30); };
  esperar("crianca");
  if (est === "crianca") return m;
  esperar("adolescente");
  if (est === "adolescente") return m;
  virarUltimate(m);
  return m;
}

describe("o catalogo (secao 13.2)", () => {
  test("9 itens: 2 chips de stat, 4 de regra e 3 cartas; cada medalha da um chip e cada revanche uma carta", () => {
    expect(ITENS.map(x => x.tipo).sort()).toEqual(["carta", "carta", "carta", "chip_regra", "chip_regra", "chip_regra", "chip_regra", "chip_stat", "chip_stat"]);
    expect(new Set(ITENS.map(x => x.id)).size).toBe(9);
    expect(MEDALHAS.map(md => ITEM_DA_MEDALHA[md.id])).toEqual(["chip_forca", "chip_recuo", "chip_oportunista", "chip_guarda", "chip_perseguidor", "chip_aparo"]);
    for (const md of MEDALHAS) expect(itemDe(CARTA_DA_REVANCHE[md.id]).tipo).toBe("carta");
    for (const c of ITENS.filter(x => x.tipo === "carta")) expect(Object.values(CARTA_DA_REVANCHE)).toContain(c.id);
    expect(() => itemDe("chip_nenhum")).toThrow(/desconhecido/);
    expect(() => cartaDe("chip_forca")).toThrow(/não é carta/);
    expect(() => chipDe("carta_cura")).toThrow(/não é chip/);
  });
  test("chip de regra: nunca tecnica nem a leitura da intencao (a regra que define outro arquetipo)", () => {
    for (const it of ITENS) if (it.tipo === "chip_regra") {
      expect(TECNICAS).not.toContain(it.regra.entao);
      expect(it.regra.se.map(c => c.n)).not.toContain("oponente_vai_preparar");
    }
  });
  test("vagas de chip pelas medalhas: 1 com 1, 2 com 3, 3 com 5", () => {
    expect([0, 1, 2, 3, 4, 5, 6].map(vagasDeChip)).toEqual([0, 1, 1, 2, 2, 3, 3]);
  });
  test("em que estagio cada chip serve: stat do Rookie em diante; regra pelas condicoes do estagio", () => {
    const serve = (id: string) => (["bebe", "crianca", "adolescente", "adulto", "mega"] as Estagio[]).filter(e => chipServe(chipDe(id), e));
    expect(serve("chip_forca")).toEqual(["crianca", "adolescente", "adulto", "mega"]);
    expect(serve("chip_recuo")).toEqual(["adolescente", "adulto", "mega"]);
    expect(serve("chip_oportunista")).toEqual(["adolescente", "adulto", "mega"]);
    expect(serve("chip_perseguidor")).toEqual(["adulto", "mega"]);
    expect(serve("chip_aparo")).toEqual(["adulto", "mega"]);
  });
});

describe("chip de stat: +2 pontos, dentro dos tetos", () => {
  test("sem treino: o Rookie ganha +1 forca e +1 vigor; dois chips no Rookie ficam em 25% do tipico (2)", () => {
    expect(bonusChipsStat(["chip_forca"], "crianca", zeros(), 0)).toMatchObject({ forca: 1, vigor: 1, guarda: 0 });
    const dois = bonusChipsStat(["chip_forca", "chip_guarda"], "crianca", zeros(), 0)!;
    expect(soma(dois)).toBeCloseTo(CIT.tetoChipStat * CIT.tipico.crianca!, 12);
    expect(dois.forca).toBeCloseTo(.5, 12);
    expect(soma(bonusChipsStat(["chip_forca", "chip_guarda"], "adolescente", zeros(), 0))).toBe(4);   /* <= 5,5 */
  });
  test("adianta treino, nao passa do teto: estagio cheio, vida cheia ou stat cheio nao ganham", () => {
    const p = zeros(); p.forca = 5; p.vigor = 5;
    expect(soma(bonusChipsStat(["chip_forca"], "crianca", p, CTR.tetoEstagio.crianca))).toBe(0);            /* estagio no teto */
    expect(soma(bonusChipsStat(["chip_forca"], "crianca", p, CTR.tetoEstagio.crianca - .5))).toBeCloseTo(.5, 12);  /* so o que falta */
    const cheio = Object.fromEntries(STATS.map(k => [k, CTR.tetoVida / STATS.length])) as Stats;
    expect(soma(bonusChipsStat(["chip_forca"], "adulto", cheio, 0))).toBe(0);                               /* vida no teto */
    const q = zeros(); q.forca = CTR.tetoStat;
    expect(bonusChipsStat(["chip_forca"], "crianca", q, 0)).toMatchObject({ forca: 0, vigor: 1 });          /* stat no teto */
    expect(bonusChipsStat(["chip_recuo"], "adolescente", zeros(), 0)).toBeNull();                           /* chip de regra: nada */
  });
  test("no pet: o chip muda o treino da luta (e so a luta: o treino do registro fica igual)", () => {
    const m = petV6(71, "crianca", 1), antes = lutadorPet(m, "a").cond;
    m.equipar("chip_forca");
    const depois = lutadorPet(m, "a").cond;
    expect(m.pontosDeLuta()).toMatchObject({ forca: 1, vigor: 1 });
    expect(m.treino.total).toBe(0);
    expect(depois.stats).not.toEqual(antes.stats);
    m.desequipar("chip_forca");
    expect(lutadorPet(m, "a").cond).toEqual(antes);
  });
});

describe("chip de regra: uma regra nova na lista do pet", () => {
  test("entra no topo, tira a livre de nota mais baixa, o pet nao troca, o dono trava mas nao veta, e sai ao desequipar", () => {
    const m = petV6(72, "adolescente", 1), gp = m.gp!, antes = [...gp.ativas];
    expect(antes).toHaveLength(5);
    m.equipar("chip_recuo");
    expect(gp.ativas[0]).toBe(RECUO);
    expect(gp.ativas).toHaveLength(5);
    expect(gp.ativas.slice(1)).toEqual(antes.slice(0, 4));                         /* saiu a ultima (a de nota mais baixa na semente) */
    expect(gp.notas[RECUO]).toBe(Math.max(...gp.ativas.map(k => gp.notas[k])));
    expect(() => m.intervirGambit("vetar", RECUO)).toThrow(/desequipe o chip/);
    m.intervirGambit("travar", RECUO); m.intervirGambit("destravar", RECUO);
    for (let k = 0; k < 30; k++) lutarCuidando(m, "agressivo", hashSemente("chip", 72, k));
    expect(gp.ativas).toContain(RECUO);                                               /* a troca do pet nunca o tira */
    m.desequipar("chip_recuo");
    expect(gp.ativas).not.toContain(RECUO);
    expect(gp.ativas).toHaveLength(5);
  });
  test("vagas, estagio e duplicado: o motor recusa com o porque", () => {
    const m = petV6(73, "adolescente", 1);
    expect(m.porqueNaoEquipa("chip_perseguidor")).toMatch(/pede um Ultimate/);
    expect(() => m.equipar("chip_perseguidor")).toThrow(/pede um Ultimate/);
    m.equipar("chip_recuo");
    expect(() => m.equipar("chip_recuo")).toThrow(/já está equipado/);
    expect(() => m.equipar("chip_forca")).toThrow(/vaga/);
    expect(() => m.desequipar("chip_forca")).toThrow(/não está equipado/);
    expect(() => new Motor(1, 6).equipar("chip_forca")).toThrow(/sem vaga|pede/);    /* bebe e sem medalha */
  });
  test("a regra do chip atravessa a evolucao (Champion -> Ultimate)", () => {
    const m = petV6(74, "adulto", 3);
    m.equipar("chip_perseguidor");
    expect(m.gp!.ativas[0]).toBe(PERSEGUIDOR);
    /* (o guardiao sem treino de outras sementes nao passa dos 80% de vitoria contra o aleatorio: nao vira Ultimate) */
    const c = petV6(76, "adolescente", 1), op = chaveRegra((chipDe("chip_oportunista") as { regra: Parameters<typeof chaveRegra>[0] }).regra);
    c.equipar("chip_oportunista");
    c.liberar(3);
    virarUltimate(c);
    expect(c.gp!.ativas).toContain(op);
    expect(c.gp!.chipsRegra).toEqual([op]);
  });
});

describe("cartas: o efeito de uma luta so", () => {
  test("Folego: +20 de guts no comeco (ate o maximo); Foco: sem exploracao", () => {
    const L = lutadorBot("agressivo"), f = comCarta(L, cartaDe("carta_folego").carta), o = comCarta(L, cartaDe("carta_foco").carta);
    expect(f.cond.guts0).toBe(Math.min(L.cond.gutsMax, L.cond.guts0 + CIT.gutsFolego));
    expect(jogarV2(f, lutadorBot("tartaruga"), 1).E0.L[0].guts).toBe(f.cond.guts0);
    expect(o.estilo.eps).toBe(0);
    expect(comCarta(L, null)).toBe(L);
  });
  test("Cura: na primeira vez abaixo de 30% cura 20% da vida maxima, uma vez so; caido nao cura", () => {
    const c = cartaDe("carta_cura").carta.cura!;
    let viu = 0;
    for (let s = 0; s < 60; s++) {
      const r = jogarV2(lutadorBot("aleatorio"), lutadorBot("agressivo"), s, null, null, null, [c, null]);
      const curas = r.turnos.filter(t => t.cura);
      expect(curas.length).toBeLessThanOrEqual(1);
      if (!curas.length) continue;
      viu++;
      const t = curas[0], hpMax = t.depois.L[0].hpMax, ganho = t.cura![0];
      expect(t.cura![1]).toBe(0);
      expect(ganho).toBeCloseTo(Math.min(c.fracao * hpMax, hpMax - (t.depois.L[0].hp - ganho)), 9);
      expect(t.depois.L[0].hp - ganho).toBeLessThan(c.abaixo * hpMax);
      expect(t.depois.L[0].hp - ganho).toBeGreaterThan(0);
    }
    expect(viu).toBeGreaterThan(5);
    /* sem carta, a luta de sempre */
    expect(jogarV2(lutadorBot("aleatorio"), lutadorBot("agressivo"), 3).turnos.some(t => t.cura)).toBe(false);
  });
  test("na serie (Cidadela) a cura vale uma vez para as tres lutas", () => {
    const A = { ...lutadorBot("furioso"), cond: { ...lutadorBot("furioso").cond } }, B = lutadorBot("aleatorio");
    for (let s = 0; s < 30; s++) {
      const serie = jogarArena(A, B, s, null, 3, null, cartaDe("carta_cura").carta);
      expect(serie.reduce((n, r) => n + r.turnos.filter(t => t.cura).length, 0)).toBeLessThanOrEqual(1);
    }
  });
  test("no pet: a carta entra no registro logo antes da luta, vale nela e sai", () => {
    const m = petV6(76, "crianca", 1);
    const r = m.lutar("agressivo", 777, "carta_foco");
    expect(m.log.slice(-2).map(e => e[1])).toEqual(["k", "l"]);
    expect(m.log[m.log.length - 2][2]).toEqual({ id: "carta_foco" });
    expect(r.carta).toBe("carta_foco");
    expect(r.res.turnos.some(t => t.ma === "exploracao")).toBe(false);
    expect(m.carta).toBeNull();
    expect(m.cartasUsadas).toEqual(["carta_foco"]);
    /* sem a carta o pet v6 sem disciplina explora (epsilon > 0); com o Foco, nunca */
    const antes = Motor.reproduzir(m.semente, m.log.slice(0, -2), 6), sementes = [1, 2, 3, 4, 5, 6, 7, 8];
    expect(antes.montarLuta("agressivo", 777).carta).toBeNull();
    expect(sementes.some(s => antes.montarLuta("agressivo", s).serie[0].turnos.some(t => t.ma === "exploracao"))).toBe(true);
    const outro = Motor.reproduzir(m.semente, m.log, 6);
    for (const s of sementes) expect(outro.lutar("agressivo", s, "carta_foco").res.turnos.some(t => t.ma === "exploracao")).toBe(false);
    /* refazer a luta do registro (Diario): a mesma, com a carta */
    const reco = Motor.reproduzir(m.semente, m.log.slice(0, -1), 6).montarLuta("agressivo", 777);
    expect(reco.carta).toBe("carta_foco");
    expect(reco.serie[0].turnos.length).toBe(r.res.turnos.length);
    expect(() => m.lutar("agressivo", 1, "chip_forca")).toThrow(/não é carta/);
    expect(() => new Motor(5, 5).lutar("aleatorio", 1, "carta_cura")).toThrow(/v6/);
  });
});

describe("registro do pet e replay com itens", () => {
  test("uma vida v6 com equipar, desequipar e cartas: o replay da a mesma assinatura", () => {
    const m = petV6(77, "adolescente", 1);
    m.equipar("chip_recuo"); m.avancar(30);
    m.lutar("agressivo", 11, "carta_cura"); m.avancar(15);
    m.desequipar("chip_recuo"); m.equipar("chip_forca");
    m.lutar("tartaruga", 12, "carta_folego"); m.lutar("tartaruga", 13); m.avancar(45);
    const r = Motor.reproduzir(m.semente, m.log, 6);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.chips).toEqual(["chip_forca"]);
    expect(r.cartasUsadas).toEqual(["carta_cura", "carta_folego"]);
  });
  test("carta sem a luta logo depois, item invalido e evento desconhecido falham alto no replay", () => {
    const m = petV6(78, "crianca", 1), t = m.e.tick, base = m.log;
    const com = (evs: EventoRegistro[]) => () => Motor.reproduzir(m.semente, [...base, ...evs], 6);
    expect(com([[t, "k", { id: "carta_cura" }], [t, "t", 10]])).toThrow(/não é luta/);
    expect(com([[t, "k", { id: "carta_cura" }], [t, "k", { id: "carta_foco" }]])).toThrow(/não é luta/);
    expect(com([[t, "i", { op: "equipar", id: "chip_nada" }]])).toThrow(/desconhecido/);
    expect(com([[t, "i", { op: "equipar", id: "chip_forca" }], [t, "i", { op: "equipar", id: "chip_guarda" }]])).toThrow(/vaga/);
    expect(com([[t, "i", { op: "trocar", id: "chip_forca" } as never]])).toThrow(/operação de item desconhecida/);
    expect(com([[t, "x", 1] as never])).toThrow(/desconhecido/);
    expect(com([[t, "k", { id: "carta_cura" }], [t, "l", { r: "aleatorio", s: 1 }]])).not.toThrow();
  });
  test("sem item a assinatura dos v6 nao muda (nenhum campo novo); com item, muda", () => {
    const a = petV6(79, "adolescente", 1), b = Motor.reproduzir(a.semente, a.log, 6);
    const campos = JSON.parse(a.assinatura()).length;
    b.equipar("chip_recuo");
    expect(JSON.parse(b.assinatura()).length).toBe(campos + 1);
    expect(JSON.parse(a.assinatura())[8]).toHaveLength(9);                           /* gambits: os 9 campos de antes */
    expect(JSON.parse(b.assinatura())[8]).toHaveLength(10);
  });
  test("pets v1-v5 nao usam itens (e o replay de um registro v5 com item falha)", () => {
    for (const v of [1, 2, 3, 4, 5]) {
      const m = new Motor(80 + v, v);
      m.avancar(DUR_EVO.bebe + 30);
      expect(m.vagasChip).toBe(0);
      expect(() => m.equipar("chip_forca")).toThrow(/v6/);
      expect(() => m.lutar("aleatorio", 1, "carta_foco")).toThrow(/v6/);
      expect(() => Motor.reproduzir(m.semente, [...m.log, [m.e.tick, "i", { op: "equipar", id: "chip_forca" }]], v)).toThrow(/v6/);
      expect(JSON.stringify(m.assinatura())).not.toContain("chip");
    }
  });
});

describe("inventario no registro do Tamer", () => {
  const gaz = MEDALHAS[0].lider;
  test("a medalha da o item dela (uma vez); o Tamer de antes recebe o item das medalhas que ja tinha", () => {
    const t = new Tamer(), m = new Motor(90, 6);
    expect(conferirItensDasMedalhas(t, m, 1)).toEqual([]);
    t.ganhar("campina", m, 1); t.ganhar("torre", m, 2);
    const novos = conferirItensDasMedalhas(t, m, 3);
    expect(novos.map(x => [x.id, x.origem, x.n])).toEqual([["chip_forca", "medalha", 1], ["chip_recuo", "medalha", 2]]);
    expect(conferirItensDasMedalhas(t, m, 4)).toEqual([]);
    expect(t.temChip("chip_forca") && t.temChip("chip_recuo") && !t.temChip("chip_aparo")).toBe(true);
    expect(conferirItensDasMedalhas(t, new Motor(91, 5), 5)).toEqual([]);            /* so com pet v6 */
    const r = Tamer.reproduzir(t.log);
    expect(r.itens).toEqual(t.itens);
  });
  test("carta da revanche: medalha antes, pet do nivel da arena e a espera de 24 h do relogio do pet", () => {
    const t = new Tamer(), m = petV6(92, "crianca", 1);
    t.ganhar("campina", m, 1);
    expect(porqueSemCarta(t, m, gaz, false)).toMatch(/primeira vitória/);
    expect(porqueSemCarta(t, m, "agressivo", true)).toMatch(/líder/);
    expect(conferirRevanche(t, m, gaz, false, true)).toBeNull();                      /* derrota nao da */
    const c = conferirRevanche(t, m, gaz, true, true, 10)!;
    expect(c).toMatchObject({ id: CARTA_DA_REVANCHE.campina, origem: "revanche", lider: gaz, est: "crianca", pet: m.semente });
    expect(t.cartas("carta_folego")).toBe(1);
    expect(porqueSemCarta(t, m, gaz, true)).toMatch(/próxima em/);
    m.avancar(CIT.espera - 1);
    expect(conferirRevanche(t, m, gaz, true, true)).toBeNull();
    m.avancar(1);
    if (m.estagioAtual === "crianca") expect(conferirRevanche(t, m, gaz, true, true)).not.toBeNull();
    else expect(porqueSemCarta(t, m, gaz, true)).toMatch(/nível da arena/);
    const u = petV6(93, "adolescente", 1);
    expect(porqueSemCarta(t, u, gaz, true)).toMatch(/nível da arena/);            /* Champion na Campina: sem carta */
    expect(Tamer.reproduzir(t.log).itens).toEqual(t.itens);
  });
  test("o replay confere tudo: item antes da medalha, item errado, repetido, espera e carta sem estoque falham alto", () => {
    const m = new Motor(94, 6), med: EventoTamer = ["medalha", { id: "campina", n: 1, quando: 1, pet: 94, forma: "x", tick: 500 }];
    const it = (id: string, n: number, origem: "medalha" | "revanche", tick = 600): EventoTamer =>
      ["item", { id, n, quando: 2, origem, lider: gaz, pet: 94, forma: "x", est: "crianca", tick }];
    expect(() => Tamer.reproduzir([it("chip_forca", 1, "medalha")])).toThrow(/antes da Medalha/);
    expect(() => Tamer.reproduzir([med, it("chip_aparo", 1, "medalha")])).toThrow(/dá Chip de Força/);
    expect(() => Tamer.reproduzir([med, it("chip_forca", 1, "medalha"), it("chip_forca", 2, "medalha")])).toThrow(/repetido/);
    expect(() => Tamer.reproduzir([med, it("carta_folego", 1, "revanche"), it("carta_folego", 2, "revanche", 700)])).toThrow(/espera/);
    expect(() => Tamer.reproduzir([med, it("chip_forca", 2, "medalha")])).toThrow(/fora de ordem/);
    expect(() => Tamer.reproduzir([med, ["carta_usada", { id: "carta_folego", quando: 3, pet: 94, tick: 700 }]])).toThrow(/sem estar no inventário/);
    expect(() => Tamer.reproduzir([med, ["loja" as never, {} as never]])).toThrow(/desconhecido/);
    const t = Tamer.reproduzir([med, it("carta_folego", 1, "revanche")]);
    t.usarCarta("carta_folego", m, 5);
    expect(t.cartas("carta_folego")).toBe(0);
    expect(() => t.usarCarta("carta_folego", m, 6)).toThrow(/sem estar no inventário/);
  });
  test("o registro grava a versao 3 (o titulo da Liga, parte 4a) e le a 1 (so medalhas) e a 2 (itens)", () => {
    const t = new Tamer(), m = new Motor(95, 6), a = armaz();
    t.ganhar("campina", m, 1);
    gravarTamer(a, t);
    expect(JSON.parse(a.dados[CHAVE_TAMER]).versao).toBe(3);
    for (const versao of [1, 2]) expect(lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao, log: t.log }) })).n).toBe(1);
    expect(() => lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 4, log: [] }) }))).toThrow(/versão/);
  });
  test("no app: a abertura da o item das medalhas de antes; mudarTamer grava", () => {
    const m = petV6(96, "crianca", 1), t = new Tamer();
    t.ganhar("campina", m, 1);
    const a = armaz({ [CHAVE]: textoSave(m), [CHAVE_TAMER]: JSON.stringify({ versao: 1, log: t.log }) });
    iniciarJogo(a);
    expect(tamerAtual().temChip("chip_forca")).toBe(true);
    expect(JSON.parse(a.dados[CHAVE_TAMER]).log.map((e: EventoTamer) => e[0])).toEqual(["medalha", "item"]);
    mudarTamer(tt => tt.ganharItem("carta_folego", "revanche", MEDALHAS[0].lider, jogoAtual().motor, 9));
    expect(lerTamer(a).cartas("carta_folego")).toBe(1);
  });
});

test("controle: a luta sem carta e sem chip e a de sempre (mesma luta com e sem os parametros novos)", () => {
  const A = lutadorBot("furioso"), B = lutadorBot("espelho");
  for (const s of [1, 2, 3]) expect(JSON.stringify(jogarV2(A, B, s, null, null, null, null))).toBe(JSON.stringify(jogarV2(A, B, s)));
  for (const s of [4, 5]) expect(JSON.stringify(jogarArena(A, B, s, null, 3, null, null))).toBe(JSON.stringify(jogarArena(A, B, s, null, 3)));
  expect(CV.eps).toBeGreaterThan(0);
});
