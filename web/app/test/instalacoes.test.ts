/* As instalacoes da Fronteira (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4b; so no jogo, so o pet v13): a Torre de Batalha e o
   Palacio. O sorteio reproduzivel dos rivais (da semente da tentativa, que sai do registro do pet), a sequencia sem cura, o fim na
   derrota, o Palacio sem travas, vetos e chips de regra, a entrada depois do titulo (evento "f"), o recorde no registro do Tamer e o replay.
   As lutas do pet v13 sao em tempo real (res.tr). O pet de verdade e um Mega v13 feito aqui (megaTreinado, o mesmo
   do teste da Liga: o e2e/save_liga.json e de um pet v6), que conhece as 6 medalhas. */
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import {
  ACOES_DONO_JOGO_V11, CAT, CD, CMG, CTR, MEDALHAS_LIGA, TPD, criarDono, criarRng, jogarLuta, nomeForma,
  CESC_V9, CV21E_TR, ESPECIES, FATOR_INSTALACAO, FATOR_LIGA, FORMAS_AD, INSTALACOES, LUTAS_MAX_INSTALACAO, MEDALHAS, chaveRegra, chipDe, ehInstalacao,
  formaRivalInstalacao, gambitsAdulto, hashSemente, instalacaoDe, jogarSequencia, jogarSerie, lutadorLiga, lutadorPet, regraDe, rivalInstalacao,
  sementeDaSerie, sementeTentativa, type EventoRegistro, type IdInstalacao,
} from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";
import { Motor } from "../motor/motor.ts";
import { Tamer, conferirRecordes, gravarTamer, lerTamer, sincronizarPet, type EventoTamer } from "../src/tamer.ts";

const escalaAntes = ESCALA.ligada;
beforeEach(() => ligarEscala(true));
afterEach(() => ligarEscala(escalaAntes));
const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"] as const;
/** a vida (a de e2e/gerar_save_liga.mjs, no pet v13): dono atencioso so com as acoes do jogo, treino em rodizio, lutas de treino do Champion e do
    Ultimate, ate o Mega chegar ao teto de treino; o registro termina num avanco de tempo */
function megaTreinado(semente: number, dias = 8): Motor | null {
  const m = new Motor(semente), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  m.liberar(MEDALHAS_LIGA);
  const passos = Math.round(dias * TPD / CD.passo), orc = Math.round(CD.porDia * dias);
  let gasto = 0, ex = 0, k = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    if (m.morte) return null;
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, rng).filter(a => ACOES_DONO_JOGO_V11.includes(a));
    if (m.lesionadoDesde !== null) acoes.unshift("tratar_lesao");
    for (const a of acoes) { m.observar(a); gasto++; }
    if (m.estagioAtual !== "bebe" && m.treino.podeTocar(m.e.tick) && m.treino.fadiga + CTR.fadigaSessao < CTR.limiarPausa) { try { m.treinar(EX[ex++ % EX.length]); } catch { /* o motor recusou: tenta no proximo passo */ } }
    if ((m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) || (m.estagioAtual === "adulto" && m.lutas.lutas < 12)) {
      m.lutar("aleatorio", hashSemente("sparring", semente, k++));
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    }
    if (m.estagioAtual === "mega" && m.treino.total >= CMG.tetoVida) break;
  }
  if (m.estagioAtual !== "mega" || m.morte) return null;
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  m.avancar(CD.passo);
  return m;
}
/** o Mega do teste: a primeira semente (a partir de 9100) que chega a Mega treinado; feito uma vez e reproduzido do registro a cada teste */
let _mega: { semente: number; log: EventoRegistro[] } | null = null;
function SAVE(): { semente: number; log: EventoRegistro[]; versao: number } {
  if (!_mega) {
    ligarEscala(true);
    for (let s = 9100; s < 9140 && !_mega; s++) { const m = megaTreinado(s); if (m) _mega = { semente: m.semente, log: m.log }; }
    if (!_mega) throw new Error("nenhuma semente deu um Mega v13 treinado");
  }
  return { ..._mega, versao: 13 };
}
const TORRE: IdInstalacao = "torre_batalha", PALACIO: IdInstalacao = "palacio";
/** o Mega do save (conhece as 6 medalhas), reproduzido do registro; `aberta`: com a Fronteira aberta (evento "f") */
function mega(aberta = true): Motor {
  const x = SAVE(), m = Motor.reproduzir(x.semente, x.log, x.versao);
  if (aberta) m.abrirFronteira();
  return m;
}
/** uma tentativa como o app faz: a semente da proxima tentativa do pet; a lesao da derrota tratada */
function tentar(m: Motor, inst: IdInstalacao) {
  const r = m.lutar(inst, m.sementeInstalacao(inst));
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  return r;
}
const armaz = () => { const dados: Record<string, string> = {}; return { dados, getItem: (k: string) => (k in dados ? dados[k] : null), setItem(k: string, v: string) { dados[k] = v; } }; };
/** um Tamer com as 6 medalhas e, com `titulo`, campeao da Liga */
function tamer(titulo: boolean): Tamer {
  const t = new Tamer(), m = new Motor(1);
  for (const md of MEDALHAS) t.ganhar(md.id, m, 1);
  if (titulo) t.ganharTitulo(m, 2);
  return t;
}

describe("as instalacoes e o sorteio dos rivais", () => {
  test("duas instalacoes (Torre de Batalha, Palacio), com a regra em uma frase; ids que nao sao rival de campanha", () => {
    expect(INSTALACOES.map(x => [x.id, x.nome, x.regra])).toEqual([[TORRE, "Torre de Batalha", "sequencia"], [PALACIO, "Palácio", "sozinho"]]);
    for (const x of INSTALACOES) { expect(x.frase.length).toBeGreaterThan(20); expect(ehInstalacao(x.id)).toBe(true); }
    expect(ehInstalacao("liga")).toBe(false);
    expect(ehInstalacao("torre")).toBe(false);                                     /* a arena da Torre de pedra nao e a Torre de Batalha */
    expect(() => instalacaoDe("fabrica")).toThrow(/desconhecida/);
    expect(FATOR_INSTALACAO).toBe(FATOR_LIGA);
  });
  test("a semente da tentativa sai do registro (pet, instalacao, numero) e o sorteio e reproduzivel; as 8 formas e as 4 especies aparecem", () => {
    expect(sementeTentativa(7, TORRE, 1)).toBe(sementeTentativa(7, TORRE, 1));
    expect(new Set([sementeTentativa(7, TORRE, 1), sementeTentativa(7, TORRE, 2), sementeTentativa(8, TORRE, 1), sementeTentativa(7, PALACIO, 1)]).size).toBe(4);
    expect(() => sementeTentativa(7, TORRE, 0)).toThrow(/tentativa/);
    const formas = new Set<string>(), esps = new Set<string>();
    for (let n = 1; n <= 30; n++) for (let k = 0; k < 5; k++) {
      const s = sementeTentativa(99, TORRE, n), f = formaRivalInstalacao(s, k);
      expect(formaRivalInstalacao(s, k)).toEqual(f);                                /* a mesma semente, o mesmo rival */
      expect(f.est).toBe("mega");
      formas.add(f.adulta!); esps.add(f.esp);
    }
    expect([...formas].sort()).toEqual([...FORMAS_AD].sort());
    expect([...esps].sort()).toEqual([...ESPECIES].sort());
  });
  test("o rival e o Mega canonico: tecnica da linha, passiva da forma, lista canonica das regras da luta, E = vida do Mega na escala x fator", () => {
    for (let k = 0; k < 20; k++) {
      const s = hashSemente("rival", k), f = formaRivalInstalacao(s, 0), L = rivalInstalacao(s, 0, CV21E_TR);
      expect(L.cond.est).toBe("mega");
      expect(L.cond.passiva).toBe(f.adulta);
      expect(L.cond.tecnica).not.toBeNull();
      expect(L.cond.escala).toBeCloseTo(CESC_V9.vida.mega * FATOR_INSTALACAO, 6);
      expect(L.estilo.gambits).toEqual(gambitsAdulto(f.adulta as (typeof FORMAS_AD)[number], CV21E_TR));
    }
  });
});

describe("a entrada (depois do titulo, evento 'f')", () => {
  test("sem o titulo do Tamer as instalacoes ficam fechadas; com ele, o pet que conhece as 6 medalhas entra", () => {
    const m = mega(false);
    for (const x of INSTALACOES) {
      expect(m.porqueNaoInstalacao(x.id)).toMatch(/depois do título/);
      expect(() => m.lutar(x.id, m.sementeInstalacao(x.id))).toThrow(/depois do título/);
    }
    expect(m.log.filter(e => e[1] === "l" && ehInstalacao(e[2].r))).toHaveLength(0);
    m.abrirFronteira();
    expect(m.log[m.log.length - 1]).toEqual([m.e.tick, "f", { campeao: true }]);
    for (const x of INSTALACOES) expect(m.porqueNaoInstalacao(x.id)).toBeNull();
    expect(() => m.abrirFronteira()).toThrow(/já está aberta/);
    /* a Fronteira so abre com as 6 medalhas conhecidas; o In-Training nao luta */
    const cinco = new Motor(41); cinco.liberar(5);
    expect(() => cinco.abrirFronteira()).toThrow(/6 medalhas/);
    const bebe = new Motor(42); bebe.liberar(6); bebe.abrirFronteira();
    expect(bebe.porqueNaoInstalacao(TORRE)).toMatch(/In-Training/);
  });
  test("o app grava o 'f' quando o Tamer tem o titulo (sincronizarPet), uma vez; sem o titulo, nao", () => {
    const m = mega(false);
    expect(sincronizarPet(tamer(false), m)).toBe(false);
    expect(m.fronteira).toBe(false);
    expect(sincronizarPet(tamer(true), m)).toBe(true);
    expect(m.fronteira).toBe(true);
    expect(sincronizarPet(tamer(true), m)).toBe(false);
    expect(m.log.filter(e => e[1] === "f")).toHaveLength(1);
  });
  test("as cartas nao valem, e a semente e a do registro: outra semente falha (ninguem escolhe os rivais)", () => {
    const m = mega(), n = m.log.length;
    expect(() => m.lutar(TORRE, m.sementeInstalacao(TORRE), "carta_folego")).toThrow(/cartas não valem/);
    expect(() => m.lutar(PALACIO, m.sementeInstalacao(PALACIO) + 1)).toThrow(/sai do registro/);
    expect(m.log).toHaveLength(n);
  });
});

describe("a sequencia", () => {
  test("sem cura: o pet leva a vida e o guts; cada rival sorteado comeca inteiro; para na primeira derrota; o limite e do rival", () => {
    const m = mega();
    let longas = 0;
    for (let n = 1; n <= 12; n++) {
      const s = sementeTentativa(m.semente, TORRE, n), L = m.montarLuta(TORRE, s), serie = L.serie;
      expect(L.instalacao?.id).toBe(TORRE);
      expect(L.carta).toBeNull();
      expect(L.rivais).toHaveLength(serie.length);
      serie.forEach((res, j) => {
        expect(L.rivais![j]).toEqual(rivalInstalacao(s, j, m.regras));             /* o rival sorteado da luta j */
        expect(res.E0.L[1].hp).toBe(res.E0.L[1].hpMax);
        if (j) {
          const antes = serie[j - 1].E.L[0];
          expect(res.E0.L[0].hp).toBe(antes.hp);                                   /* sem cura */
          expect(res.E0.L[0].guts).toBe(Math.min(antes.guts, res.E0.L[0].gutsMax));
          expect(serie[j - 1].pontosA).toBe(1);                                    /* so segue depois de vencer */
        } else expect(res.E0.L[0].hp).toBe(res.E0.L[0].hpMax);
        const ini = j ? { hp: serie[j - 1].E.L[0].hp, guts: serie[j - 1].E.L[0].guts } : null;
        const livre = jogarLuta(L.A, L.rivais![j], sementeDaSerie(s, j), m.regras, ini, 1);
        expect(res.tr!.acoes).toEqual(livre.tr!.acoes);                              /* a mesma luta; o limite e do desafiado, o rival (lado B) */
        expect(res.tr!.passos).toBe(livre.tr!.passos);
        expect(res.pontosA).toBe(livre.pontosA);
        if (res.fim === "limite") expect(res.pontosA).toBe(0);
      });
      /* perdeu (ou empatou), acabou: a ultima nao e vitoria (o teto fica longe) */
      expect(serie.length).toBeLessThan(LUTAS_MAX_INSTALACAO);
      expect(serie[serie.length - 1].pontosA).not.toBe(1);
      if (serie.length >= 3) longas++;
    }
    expect(longas).toBeGreaterThan(0);
  });
  test("a tentativa conta: a sequencia de vitorias (a ultima), o recorde do pet e as tentativas; a proxima tem outra semente", () => {
    const m = mega(), s1 = m.sementeInstalacao(TORRE);
    const r = tentar(m, TORRE), v = r.serie.filter(x => x.pontosA === 1).length;
    expect(r.venceu).toBe(false);
    expect(m.instalacoes[TORRE]).toEqual({ tentativas: 1, recorde: v, ultima: v });
    expect(m.instalacoes[PALACIO]).toEqual({ tentativas: 0, recorde: 0, ultima: 0 });
    expect(m.sementeInstalacao(TORRE)).toBe(sementeTentativa(m.semente, TORRE, 2));
    expect(m.sementeInstalacao(TORRE)).not.toBe(s1);
    const ls = m.log.filter(e => e[1] === "l" && e[2].r === TORRE);
    expect(ls).toEqual([[expect.any(Number), "l", { r: TORRE, s: s1 }]]);
    expect(m.historico.some(h => /^na Torre de Batalha, contra .+ \(luta 1\): (venceu|perdeu|empatou)$/.test(h.a))).toBe(true);
  });
  test("jogarSerie e jogarSequencia com os rivais de uma lista: as mesmas lutas (a Liga e a Cidadela nao mudam)", () => {
    const A = lutadorLiga(0, CV21E_TR), Bs = [1, 2, 3].map(i => lutadorLiga(i, CV21E_TR));
    expect(jogarSerie(A, Bs, 55, CV21E_TR, 1)).toEqual(jogarSequencia(A, k => Bs[k], Bs.length, 55, CV21E_TR, 1));
    expect(() => jogarSequencia(A, () => Bs[0], 0, 55, CV21E_TR, 1)).toThrow(/sem luta/);
  });
  test("nada da Fronteira deixa o pet mais forte: treino, chips, cartas e stats de luta iguais depois das tentativas", () => {
    const m = mega(), antes = { tr: JSON.stringify(m.treino.assinatura()), chips: [...m.chips], pontos: m.pontosDeLuta(), cartas: [...m.cartasUsadas], carta: m.carta };
    for (let k = 0; k < 3; k++) { tentar(m, TORRE); tentar(m, PALACIO); }
    expect(JSON.stringify(m.treino.assinatura())).toBe(antes.tr);
    expect(m.chips).toEqual(antes.chips);
    expect(m.pontosDeLuta()).toEqual(antes.pontos);
    expect(m.cartasUsadas).toEqual(antes.cartas);
    expect(m.carta).toBe(antes.carta);
  });
});

describe("o Palacio: o pet decide sozinho", () => {
  test("travas, vetos e chips de regra nao valem (a lista do Lago sem os chips); os chips de stat valem; a Torre usa a lista do dono", () => {
    const m = mega(), gp = m.gp!;
    /* um chip de regra que a lista ainda nao tem, um chip de stat, uma regra vetada e uma travada */
    const chip = ["chip_recuo", "chip_oportunista", "chip_perseguidor", "chip_aparo"].find(id => {
      const c = chipDe(id) as { regra?: Parameters<typeof chaveRegra>[0] };
      return !gp.ativas.includes(chaveRegra(c.regra!)) && m.porqueNaoEquipa(id) === null;
    })!;
    expect(chip).toBeTruthy();
    const kChip = chaveRegra((chipDe(chip) as { regra: Parameters<typeof chaveRegra>[0] }).regra);
    m.equipar(chip); m.equipar("chip_forca");
    const livres = gp.ativas.filter(k => k !== kChip);
    const vetada = livres[0], travada = livres[livres.length - 1];
    m.intervirGambit("vetar", vetada); m.intervirGambit("travar", travada);
    expect(gp.chipsRegra).toContain(kChip);                                         /* no v13 o chip de regra fica fora da lista (ativas) */
    expect(gp.ativas).not.toContain(kChip);
    expect(gp.ativas).not.toContain(vetada);
    const lista = gp.listaPalacio();
    expect(lista).not.toContain(kChip);                                             /* o chip de regra nao vale */
    expect(lista).toContain(vetada);                                               /* o veto nao vale */
    const notas = lista.map(k => gp.notas[k]);
    expect(notas).toEqual([...notas].sort((a, b) => b - a));                        /* so a nota ordena: a trava nao vale */
    /* os lutadores: no Palacio a lista sozinho; na Torre a do dono (com o chip); os chips de stat nos dois */
    const P = m.lutadores(PALACIO), T = m.lutadores(TORRE);
    expect(P.usadas).toEqual(lista);
    expect(P.A.estilo.gambits!.regras).toEqual(lista.map(regraDe));
    expect(T.usadas).toEqual(gp.comChips(gp.ativas));                               /* a lista do dono, com a regra do chip no fim */
    expect(T.usadas[T.usadas.length - 1]).toBe(kChip);
    expect(T.usadas).toContain(kChip);
    expect(P.A.cond).toEqual(T.A.cond);
    expect(P.A.cond).toEqual(lutadorPet(m, "x", true).cond);
    /* a luta do Palacio ensina com a lista com que lutou; o replay reconstroi */
    const r = tentar(m, PALACIO);
    expect(r.usadas).toEqual(lista);
    expect(Motor.reproduzir(m.semente, m.log, m.versao).assinatura()).toBe(m.assinatura());
  });
  test("sem chip de regra, a lista do Palacio e a do Lago (listaSozinho); a regra de chip que o pet ja tinha fica", () => {
    const m = mega(), gp = m.gp!;
    expect(gp.listaPalacio()).toEqual(gp.listaSozinho());
    /* um chip cuja regra ja estava na lista: no v13 ela continua nas ativas (o chip so a poe no fim da lista de luta, sem repetir) */
    const ja = ["chip_recuo", "chip_oportunista", "chip_perseguidor", "chip_aparo"].find(id => gp.ativas.includes(chaveRegra((chipDe(id) as { regra: Parameters<typeof chaveRegra>[0] }).regra)));
    if (ja) {
      const k = chaveRegra((chipDe(ja) as { regra: Parameters<typeof chaveRegra>[0] }).regra);
      m.equipar(ja);
      expect(gp.ativas).toContain(k);
      expect(gp.comChips(gp.ativas).filter(x => x === k)).toHaveLength(1);
    }
  });
});

describe("o recorde no registro do Tamer", () => {
  test("a maior sequencia do pet vira 'recorde' quando passa a do Tamer; so depois do titulo; o registro reproduz (grava a versao 7, a da luta em tempo real)", () => {
    const m = mega();
    let n = 0;
    while (m.instalacoes[TORRE].recorde < 1 && n++ < 20) tentar(m, TORRE);
    expect(m.instalacoes[TORRE].recorde).toBeGreaterThan(0);
    expect(conferirRecordes(tamer(false), m)).toEqual([]);                          /* sem titulo, nada */
    const t = tamer(true), v = m.instalacoes[TORRE].recorde;
    const novos = conferirRecordes(t, m, 77);
    expect(novos).toEqual([{ inst: TORRE, valor: v, quando: 77, pet: m.semente, forma: nomeForma(m.forma), tick: m.e.tick }]);
    expect(t.recorde(TORRE)?.valor).toBe(v);
    expect(t.recorde(PALACIO)).toBeNull();
    expect(conferirRecordes(t, m)).toEqual([]);                                     /* igual nao e recorde */
    m.instalacoes[TORRE].recorde = v + 2;                                           /* (so o numero: a regra de passar o anterior) */
    expect(conferirRecordes(t, m, 78)).toMatchObject([{ inst: TORRE, valor: v + 2 }]);
    expect(t.recordes).toHaveLength(2);
    const a = armaz(); gravarTamer(a, t);
    expect(JSON.parse(Object.values(a.dados)[0]).versao).toBe(7);
    const r = lerTamer(a);
    expect(r.recordes).toEqual(t.recordes);
    expect(r.recorde(TORRE)?.valor).toBe(v + 2);
  });
  test("recorde antes do titulo, que nao passa o anterior, de instalacao desconhecida ou sem dados falha alto no replay", () => {
    const seis = tamer(false).log, comTitulo = tamer(true).log;
    const rec = (x: object): EventoTamer => ["recorde", { inst: TORRE, valor: 3, quando: 1, pet: 1, forma: "WarGreymon", tick: 1, ...x }] as EventoTamer;
    expect(() => Tamer.reproduzir([...seis, rec({})])).toThrow(/antes do título/);
    expect(() => Tamer.reproduzir([...comTitulo, rec({}), rec({ valor: 3 })])).toThrow(/não passa o anterior/);
    expect(() => Tamer.reproduzir([...comTitulo, rec({ inst: "fabrica" })])).toThrow(/desconhecida/);
    expect(() => Tamer.reproduzir([...comTitulo, rec({ valor: 0 })])).toThrow(/inválido/);
    expect(() => Tamer.reproduzir([...comTitulo, rec({ forma: undefined })])).toThrow(/forma/);
    const ok = Tamer.reproduzir([...comTitulo, rec({}), rec({ inst: PALACIO, valor: 1 }), rec({ valor: 5 })]);
    expect([ok.recorde(TORRE)?.valor, ok.recorde(PALACIO)?.valor]).toEqual([5, 1]);
  });
});

describe("registro e replay", () => {
  test("o 'f' e as tentativas nas duas instalacoes: o replay reconstroi o mesmo pet; a Fronteira so entra na assinatura depois do 'f'", () => {
    const m = mega(false);
    expect(m.assinatura()).not.toMatch(/"fronteira"/);
    m.abrirFronteira();
    expect(m.assinatura()).toMatch(/"fronteira"/);
    tentar(m, TORRE); m.avancar(30); tentar(m, PALACIO); tentar(m, TORRE);
    const r = Motor.reproduzir(m.semente, m.log, m.versao);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.instalacoes).toEqual(m.instalacoes);
    expect(r.instalacoes[TORRE].tentativas).toBe(2);
    for (const e of m.log.filter(x => x[1] === "l" && ehInstalacao(x[2].r))) expect(Object.keys(e[2]).sort()).toEqual(["r", "s"]);
  });
  test("luta de instalacao sem o 'f', com outra semente ou com carta antes, e 'f' malformado falham alto no replay", () => {
    const base = mega(false), t = base.e.tick, s1 = sementeTentativa(SAVE().semente, TORRE, 1), log = SAVE().log;
    expect(() => Motor.reproduzir(SAVE().semente, [...log, [t, "l", { r: TORRE, s: s1 }]], 13)).toThrow(/sem poder: .*depois do título/);
    const f: EventoRegistro = [t, "f", { campeao: true }];
    expect(() => Motor.reproduzir(SAVE().semente, [...log, f, [t, "l", { r: TORRE, s: s1 + 1 }]], 13)).toThrow(/semente/);
    expect(() => Motor.reproduzir(SAVE().semente, [...log, f, [t, "k", { id: "carta_foco" }], [t, "l", { r: PALACIO, s: sementeTentativa(SAVE().semente, PALACIO, 1) }]], 13)).toThrow(/cartas não valem/);
    expect(() => Motor.reproduzir(SAVE().semente, [...log, [t, "f", { campeao: false }] as unknown as EventoRegistro], 13)).toThrow(/Fronteira inválido/);
    expect(() => Motor.reproduzir(SAVE().semente, [...log, f, f], 13)).toThrow(/já está aberta/);
    expect(() => Motor.reproduzir(SAVE().semente, [...log, [t, "x", {}] as unknown as EventoRegistro], 13)).toThrow(/desconhecido/);
    expect(Motor.reproduzir(SAVE().semente, [...log, f, [t, "l", { r: TORRE, s: s1 }]], 13).instalacoes[TORRE].tentativas).toBe(1);
  });
});
