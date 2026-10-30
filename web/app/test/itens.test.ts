/* Itens do Tamer (medalhas, parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13; so no jogo; hoje no pet v13, com as regras dos itens dos v9): o catalogo, cada item
   fazendo o que diz (chip de stat dentro dos tetos, chip de regra na lista, cartas na luta), as vagas pelas medalhas, os eventos "i" e
   "k" no registro do pet e o replay com eles, o inventario no registro do Tamer (item da medalha, carta da revanche com a espera, carta
   usada) (os pets de antes saem do Motor na COMBATE-TR R2b). */
import { describe, expect, test } from "vitest";
import {
  CARTA_DA_REVANCHE, CAT, CIT, CIT_V9, CTR, CV, CV21E_TR, DUR_EVO, ITENS, ITEM_DA_MEDALHA, MEDALHAS, Motor, STATS, TECNICAS, bonusChipsStat, cartaDe, chaveRegra,
  chipDe, chipServe, comCarta, hashSemente, itemDe, jogarArena, jogarLuta, jogarTR, lutadorBot, lutadorPet, vagasDeChip, type Estagio, type EventoRegistro,
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
  treinarAte(m, CTR.tetoEstagio.adolescente);   /* o pet v13 luta em tempo real: sem treino nao passa dos 80% de vitoria contra o aleatorio */
  while (m.sparring < CAT.sparring) lutarCuidando(m, "aleatorio", hashSemente("sp", m.semente, k++));
  for (let j = 0; j < 40 && m.estagioAtual === "adolescente"; j++) { m.avancar(60); if (m.estagioAtual === "adolescente") lutarCuidando(m, "aleatorio", hashSemente("sp", m.semente, k++)); }
  if (m.estagioAtual !== "adulto") throw new Error("o pet de teste nao chegou a Ultimate");
}
const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"] as const;
/** treina ate o total pedido (respeitando fadiga e intervalo; o pet v13 so usa chips e cartas com o treino minimo do nivel) */
function treinarAte(m: Motor, alvo: number): void {
  for (let k = 0; k < 600 && m.treino.total < alvo; k++) {
    if (m.treino.fadiga < CTR.fadigaSessao && m.treino.podeTocar(m.e.tick)) { try { m.treinar(EX[k % EX.length]); continue; } catch { /* dormindo */ } }
    m.avancar(30);
  }
}
/** treina ate os itens valerem no estagio atual (itens.itensValem dos pets v9 em diante) */
function comItensValendo(m: Motor): Motor { treinarAte(m, CIT_V9.treinoMinimo * CIT.tipico[m.estagioAtual]!); if (!m.itensValem) throw new Error("os itens nao valem"); return m; }
/** trata a lesao, se houver (o pet de teste nao morre) */
const cuidar = (m: Motor): void => { if (m.lesionadoDesde !== null) m.observar("tratar_lesao"); };
/** o primeiro rival da campanha (a carta so vale contra NPC nos pets v9 em diante) */
const NPC1 = (m: Motor): string => m.lugares[0].rivais[0];
/** pet v13 no estagio pedido, sem treino, com `medalhas` conhecidas desde o comeco */
function petV13(semente: number, est: Estagio, medalhas: number): Motor {
  const m = new Motor(semente);
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
  test("no pet: o chip muda o treino da luta (e so a luta: o treino do registro fica igual); sem o treino minimo nao vale", () => {
    const m = petV13(71, "crianca", 1);
    m.equipar("chip_forca");
    expect(m.itensValem).toBe(false);
    expect(m.pontosDeLuta()).toBeNull();
    comItensValendo(m);
    const antes = lutadorPet(m, "a").cond.stats, total = m.treino.total;
    m.desequipar("chip_forca");
    const semChip = lutadorPet(m, "a").cond;
    m.equipar("chip_forca");
    const b = m.pontosDeLuta()!;
    expect(STATS.reduce((a, k) => a + b[k] - m.treino.pontos[k], 0)).toBeCloseTo(2 * CIT_V9.fatorChipStat, 9);   /* nos v9 o ponto do chip vale a metade */
    expect(m.treino.total).toBe(total);
    expect(antes).not.toEqual(semChip.stats);
    m.desequipar("chip_forca");
    expect(lutadorPet(m, "a").cond).toEqual(semChip);
  });
});

describe("chip de regra: uma regra nova na lista do pet", () => {
  test("entra no fim da lista de luta (nos v9 em diante), sem tirar nenhuma; o pet nao troca, o dono nem trava nem veta, e sai ao desequipar", () => {
    const m = petV13(72, "adolescente", 1), gp = m.gp!, antes = [...gp.ativas];
    expect(antes).toHaveLength(5);
    m.equipar("chip_recuo");
    comItensValendo(m);
    expect(gp.ativas).toEqual(antes);                                                  /* a lista do pet nao muda */
    expect(gp.chipsRegra).toEqual([RECUO]);
    const lista = () => lutadorPet(m, "p").estilo.gambits!.regras.map(chaveRegra);
    expect(lista()).toEqual([...gp.ativas, RECUO]);                                    /* o chip so entra no fim da lista de luta */
    expect(() => m.intervirGambit("vetar", RECUO)).toThrow(/desequipe o chip/);
    expect(() => m.intervirGambit("travar", RECUO)).toThrow(/regra ativa/);        /* nao esta entre as ativas: o dono nem trava */
    for (let k = 0; k < 30; k++) lutarCuidando(m, "agressivo", hashSemente("chip", 72, k));
    expect(gp.chipsRegra).toContain(RECUO);                                            /* a troca do pet nunca o tira */
    expect(gp.ativas).not.toContain(RECUO);
    m.desequipar("chip_recuo");
    expect(gp.chipsRegra).not.toContain(RECUO);
    expect(lista()).toEqual(gp.ativas);
    expect(gp.ativas).toHaveLength(5);
  });
  test("vagas, estagio e duplicado: o motor recusa com o porque", () => {
    const m = petV13(73, "adolescente", 1);
    expect(m.porqueNaoEquipa("chip_perseguidor")).toMatch(/pede um Ultimate/);
    expect(() => m.equipar("chip_perseguidor")).toThrow(/pede um Ultimate/);
    m.equipar("chip_recuo");
    expect(() => m.equipar("chip_recuo")).toThrow(/já está equipado/);
    expect(() => m.equipar("chip_forca")).toThrow(/vaga/);
    expect(() => m.desequipar("chip_forca")).toThrow(/não está equipado/);
    expect(() => new Motor(1).equipar("chip_forca")).toThrow(/sem vaga|pede/);    /* bebe e sem medalha */
  });
  test("a regra do chip atravessa a evolucao (Champion -> Ultimate)", () => {
    const m = petV13(74, "adulto", 3);
    m.equipar("chip_perseguidor");
    expect(m.gp!.chipsRegra).toEqual([PERSEGUIDOR]);
    /* (na luta em tempo real algumas sementes nao passam dos 80% de vitoria contra o aleatorio mesmo treinadas: a 77 vira Ultimate) */
    const c = petV13(77, "adolescente", 1), op = chaveRegra((chipDe("chip_oportunista") as { regra: Parameters<typeof chaveRegra>[0] }).regra);
    c.equipar("chip_oportunista");
    c.liberar(3);
    virarUltimate(c);
    expect(c.gp!.chipsRegra).toEqual([op]);
  });
});

describe("cartas: o efeito de uma luta so", () => {
  test("Folego: +20 de guts no comeco (ate o maximo); Foco: sem exploracao", () => {
    const L = lutadorBot("agressivo"), f = comCarta(L, cartaDe("carta_folego").carta), o = comCarta(L, cartaDe("carta_foco").carta);
    expect(f.cond.guts0).toBe(Math.min(L.cond.gutsMax, L.cond.guts0 + CIT.gutsFolego));
    expect(jogarLuta(f, lutadorBot("tartaruga"), 1, CV21E_TR).E0.L[0].guts).toBe(f.cond.guts0);
    expect(o.estilo.eps).toBe(0);
    expect(comCarta(L, null)).toBe(L);
  });
  test("Cura: na primeira vez abaixo de 30% cura 20% da vida maxima, uma vez so; caido nao cura", () => {
    const c = cartaDe("carta_cura").carta.cura!;
    let viu = 0;
    for (let s = 0; s < 60; s++) {
      const r = jogarTR(lutadorBot("aleatorio"), lutadorBot("agressivo"), s, { R: CV21E_TR, curas: [c, null], eventos: true });
      const ev = r.eventos!, curas = ev.filter(e => e.tipo === "cura");
      expect(curas.length).toBeLessThanOrEqual(1);
      expect(r.curou).toEqual([curas.length === 1, false]);
      if (!curas.length) continue;
      viu++;
      const i = ev.indexOf(curas[0]), ganho = (curas[0] as { valor: number }).valor, hpMax = r.E0.hpMax[0];
      /* a vida logo antes da cura: o resto do ultimo dano que o lado A levou */
      const antes = (ev.slice(0, i).filter(e => e.tipo === "dano" && e.lado === 0).pop() as { resta: number }).resta;
      expect((curas[0] as { lado: number }).lado).toBe(0);
      expect(ganho).toBeCloseTo(Math.min(c.fracao * hpMax, hpMax - antes), 9);
      expect(antes).toBeLessThan(c.abaixo * hpMax);
      expect(antes).toBeGreaterThan(0);
    }
    expect(viu).toBeGreaterThan(5);
    /* sem carta, a luta de sempre */
    expect(jogarLuta(lutadorBot("aleatorio"), lutadorBot("agressivo"), 3, CV21E_TR).tr.curou).toEqual([false, false]);
  });
  test("na serie (Cidadela) a cura vale uma vez para as tres lutas", () => {
    const A = { ...lutadorBot("furioso"), cond: { ...lutadorBot("furioso").cond } }, B = lutadorBot("aleatorio");
    for (let s = 0; s < 30; s++) {
      const serie = jogarArena(A, B, s, CV21E_TR, 3, null, cartaDe("carta_cura").carta);
      expect(serie.reduce((n, r) => n + (r.tr.curou[0] ? 1 : 0), 0)).toBeLessThanOrEqual(1);
    }
  });
  test("no pet: a carta entra no registro logo antes da luta, vale nela e sai (so contra NPC e com o treino minimo)", () => {
    const m = comItensValendo(petV13(76, "crianca", 1)), npc = NPC1(m);
    expect(m.porqueSemCartaV9("agressivo")).toMatch(/campanha/);
    expect(() => m.lutar("agressivo", 777, "carta_foco")).toThrow(/campanha/);
    expect(m.carta).toBeNull();
    const r = m.lutar(npc, 777, "carta_foco");
    expect(m.log.slice(-2).map(e => e[1])).toEqual(["k", "l"]);
    expect(m.log[m.log.length - 2][2]).toEqual({ id: "carta_foco" });
    expect(r.carta).toBe("carta_foco");
    expect(m.carta).toBeNull();
    expect(m.cartasUsadas).toEqual(["carta_foco"]);
    /* a luta em tempo real: o resultado fica em tr (turnos vazio) e o registro refaz o pet igual */
    expect(r.res.tr).toBeDefined();
    expect(Motor.reproduzir(m.semente, m.log).assinatura()).toBe(m.assinatura());
    /* antes da luta do registro: sem carta armada; refazer a luta do registro (Diario): a mesma, com a carta */
    expect(Motor.reproduzir(m.semente, m.log.slice(0, -2)).montarLuta(npc, 777).carta).toBeNull();
    const reco = Motor.reproduzir(m.semente, m.log.slice(0, -1)).montarLuta(npc, 777);
    expect(reco.carta).toBe("carta_foco");
    expect(reco.serie[0].tr).toEqual(r.res.tr);
    expect(() => m.lutar(npc, 1, "chip_forca")).toThrow(/não é carta/);
  });
});

describe("registro do pet e replay com itens", () => {
  test("uma vida v13 com equipar, desequipar e cartas: o replay da a mesma assinatura", () => {
    const m = comItensValendo(petV13(77, "adolescente", 1));
    m.equipar("chip_recuo"); m.avancar(30);
    cuidar(m); m.lutar(NPC1(m), 11, "carta_cura"); cuidar(m); m.avancar(15);
    m.desequipar("chip_recuo"); m.equipar("chip_forca");
    m.lutar(NPC1(m), 12, "carta_folego"); cuidar(m); m.lutar("tartaruga", 13); cuidar(m); m.avancar(45);
    const r = Motor.reproduzir(m.semente, m.log);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.chips).toEqual(["chip_forca"]);
    expect(r.cartasUsadas).toEqual(["carta_cura", "carta_folego"]);
  });
  test("carta sem a luta logo depois, item invalido e evento desconhecido falham alto no replay", () => {
    const m = comItensValendo(petV13(78, "crianca", 1)), t = m.e.tick, base = m.log;
    const com = (evs: EventoRegistro[]) => () => Motor.reproduzir(m.semente, [...base, ...evs]);
    expect(com([[t, "k", { id: "carta_cura" }], [t, "t", 10]])).toThrow(/não é luta/);
    expect(com([[t, "k", { id: "carta_cura" }], [t, "k", { id: "carta_foco" }]])).toThrow(/não é luta/);
    expect(com([[t, "i", { op: "equipar", id: "chip_nada" }]])).toThrow(/desconhecido/);
    expect(com([[t, "i", { op: "equipar", id: "chip_forca" }], [t, "i", { op: "equipar", id: "chip_guarda" }]])).toThrow(/vaga/);
    expect(com([[t, "i", { op: "trocar", id: "chip_forca" } as never]])).toThrow(/operação de item desconhecida/);
    expect(com([[t, "x", 1] as never])).toThrow(/desconhecido/);
    expect(com([[t, "k", { id: "carta_cura" }], [t, "l", { r: "aleatorio", s: 1 }]])).toThrow(/campanha/);   /* a carta so vale contra NPC */
    expect(com([[t, "k", { id: "carta_cura" }], [t, "l", { r: NPC1(m), s: 1 }]])).not.toThrow();
  });
  test("sem item a assinatura dos v13 nao muda (nenhum campo novo); com item, muda", () => {
    const a = petV13(79, "adolescente", 1), b = Motor.reproduzir(a.semente, a.log);
    const campos = JSON.parse(a.assinatura()).length;
    b.equipar("chip_recuo");
    expect(JSON.parse(b.assinatura()).length).toBe(campos + 1);
    expect(JSON.parse(a.assinatura())[8]).toHaveLength(9);                           /* gambits: os 9 campos de antes */
    expect(JSON.parse(b.assinatura())[8]).toHaveLength(10);
  });
});

describe("inventario no registro do Tamer", () => {
  const gaz = MEDALHAS[0].lider;
  test("a medalha da o item dela (uma vez); o Tamer de antes recebe o item das medalhas que ja tinha", () => {
    const t = new Tamer(), m = new Motor(90);
    expect(conferirItensDasMedalhas(t, m, 1)).toEqual([]);
    t.ganhar("campina", m, 1); t.ganhar("torre", m, 2);
    const novos = conferirItensDasMedalhas(t, m, 3);
    expect(novos.map(x => [x.id, x.origem, x.n])).toEqual([["chip_forca", "medalha", 1], ["chip_recuo", "medalha", 2]]);
    expect(conferirItensDasMedalhas(t, m, 4)).toEqual([]);
    expect(t.temChip("chip_forca") && t.temChip("chip_recuo") && !t.temChip("chip_aparo")).toBe(true);
      const r = Tamer.reproduzir(t.log);
    expect(r.itens).toEqual(t.itens);
  });
  test("carta da revanche: medalha antes, pet do nivel da arena e a espera de 24 h do relogio do pet", () => {
    const t = new Tamer(), m = petV13(92, "crianca", 1);
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
    const u = petV13(93, "adolescente", 1);
    expect(porqueSemCarta(t, u, gaz, true)).toMatch(/nível da arena/);            /* Champion na Campina: sem carta */
    expect(Tamer.reproduzir(t.log).itens).toEqual(t.itens);
  });
  test("o replay confere tudo: item antes da medalha, item errado, repetido, espera e carta sem estoque falham alto", () => {
    const m = new Motor(94), med: EventoTamer = ["medalha", { id: "campina", n: 1, quando: 1, pet: 94, forma: "x", tick: 500 }];
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
  test("o registro grava a versao 7 (as regras de cada tentativa da Fabrica, fase 3) e le da 1 (so medalhas) a 5 (a Fabrica e o Salao)", () => {
    const t = new Tamer(), m = new Motor(95), a = armaz();
    t.ganhar("campina", m, 1);
    gravarTamer(a, t);
    expect(JSON.parse(a.dados[CHAVE_TAMER]).versao).toBe(7);
    for (const versao of [1, 2, 3, 4, 5, 6]) expect(lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao, log: t.log }) })).n).toBe(1);
    expect(() => lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 8, log: [] }) }))).toThrow(/versão/);
  });
  test("no app: a abertura da o item das medalhas de antes; mudarTamer grava", () => {
    const m = petV13(96, "crianca", 1), t = new Tamer();
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
  for (const s of [1, 2, 3]) expect(JSON.stringify(jogarLuta(A, B, s, CV21E_TR, null, null, null))).toBe(JSON.stringify(jogarLuta(A, B, s, CV21E_TR)));
  for (const s of [4, 5]) expect(JSON.stringify(jogarArena(A, B, s, CV21E_TR, 3, null, null))).toBe(JSON.stringify(jogarArena(A, B, s, CV21E_TR, 3)));
  expect(CV.eps).toBeGreaterThan(0);
});
