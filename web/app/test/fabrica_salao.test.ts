/* A Fabrica e o Salao da Fronteira (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4c; so no jogo, so o pet v13).
   Fabrica: o sorteio reproduzivel (alugados e rivais da semente da tentativa, que sai do numero da tentativa no registro do Tamer), a serie
   sem cura, a troca, o fim na derrota, o recorde e o replay so pelo registro do Tamer (nenhum pet envolvido).
   Salao: um pet por estagio, a luta no registro de cada pet (semente do registro dele, rival do estagio), o recorde no Tamer, o app
   (src/fronteira.ts) com o ativo e os guardados. Os pets de verdade sao v13 feitos aqui (petAte: o dono atencioso so com as acoes do jogo,
   treino em rodizio): o Mega do teste da Liga e os guardados do Salao (um Rookie, um Champion e um Ultimate), porque os saves do e2e
   (save_liga.json, save_salao.json) sao de pets v6. A Fabrica nao usa pet: os testes de TentativaFabrica sem versao seguem na dela (6, por
   turnos, ate a R3); as tentativas do Tamer gravam v: 13 (luta em tempo real). */
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import {
  ACOES_DONO_JOGO_V11, CAT, CD, CMG, CTR, MEDALHAS_LIGA, TPD, criarDono, criarRng, fatorSalao, tamanhoLuta,
  ADOL_V21, ALUGUEIS_FABRICA, CESC_V6, CRIANCA_V21, CV21D, ESPECIES, ESTAGIOS_SALAO, FATOR_FABRICA, FATOR_INSTALACAO, FATOR_SALAO, FORMAS_AD, LINHAS,
  LUTAS_SERIE_FABRICA, MEDALHAS, RIVAL_SALAO, TentativaFabrica, alugueisFabrica, formaRivalFabrica, formaRivalSalao, gambitsAdulto, hashSemente, megaFabrica,
  rivalSalao, sementeFabrica, sementeLutaFabrica, sementeSalao, type EventoRegistro,
} from "../motor/index.ts";
import { ESCALA, ligarEscala } from "../motor/catalogo.ts";
import { Motor } from "../motor/motor.ts";
import { CHAVE, type Armazenamento } from "../src/save.ts";
import { CHAVE_TAMER, Tamer, gravarTamer, lerTamer, sincronizarPet, textoTamer, type EventoTamer, type LutaSalao } from "../src/tamer.ts";
import { iniciarJogo, jogoAtual, tamerAtual } from "../src/jogo.ts";
import { CHAVE_GUARDADOS, lerGuardados } from "../src/pets.ts";
import { candidatosSalao, estagiosQueFaltam, tentarSalao } from "../src/fronteira.ts";

const escalaAntes = ESCALA.ligada;
beforeEach(() => ligarEscala(true));
afterEach(() => ligarEscala(escalaAntes));
type Salvo = { semente: number; log: EventoRegistro[]; versao: number };
const EX = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"] as const;
/** a vida (a de e2e/gerar_save_salao.mjs, no pet v13): dono atencioso so com as acoes do jogo, treino em rodizio, lutas de treino do Champion e
    do Ultimate, ate o pet chegar ao estagio pedido e treinar nele `horas` de jogo (no Mega, ate o teto de treino); null se nao chegou */
function petAte(semente: number, alvo: string, horas = 8, dias = 8): Motor | null {
  const m = new Motor(semente), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  m.liberar(MEDALHAS_LIGA);
  const passos = Math.round(dias * TPD / CD.passo), orc = Math.round(CD.porDia * dias);
  let gasto = 0, ex = 0, k = 0, chegou: number | null = null;
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
    if (m.estagioAtual === alvo && chegou === null) chegou = m.e.tick;
    if (alvo === "mega" ? m.estagioAtual === "mega" && m.treino.total >= CMG.tetoVida : chegou !== null && (m.estagioAtual !== alvo || m.e.tick - chegou >= horas * 60)) break;
  }
  if (m.estagioAtual !== alvo || m.morte) return null;
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  m.avancar(CD.passo);                                                              /* o registro termina num avanco de tempo */
  return m;
}
/** a primeira luta do pet no Salao (numa copia com a Fronteira aberta, como o app faz): venceu? */
function venceSalao(m: Motor): boolean {
  const x = Motor.reproduzir(m.semente, m.log, m.versao);
  x.abrirFronteira();
  return x.lutar(RIVAL_SALAO, x.sementeSalao()).venceu;
}
/** o primeiro pet (a partir de `de`) que chega ao estagio e vence a primeira luta dele no Salao */
function petQueVence(de: number, alvo: string): Salvo {
  for (let sem = de; sem < de + 200; sem++) {
    const m = petAte(sem, alvo);
    if (m && venceSalao(m)) return { semente: m.semente, log: m.log, versao: m.versao };
  }
  throw new Error("nenhuma semente deu um " + alvo + " v13 que vence a luta do Salao");
}
/** o Mega do teste da Liga e os guardados do Salao (Rookie, Champion, Ultimate), feitos uma vez e reproduzidos do registro a cada teste */
let _pets: { liga: Salvo; guardados: Salvo[] } | null = null;
function PETS(): { liga: Salvo; guardados: Salvo[] } {
  if (!_pets) {
    ligarEscala(true);
    _pets = { liga: petQueVence(9100, "mega"), guardados: [petQueVence(9200, "crianca"), petQueVence(9300, "adolescente"), petQueVence(9400, "adulto")] };
  }
  return _pets;
}
const abrir = (x: Salvo): Motor => Motor.reproduzir(x.semente, x.log, x.versao);
/** um Tamer com as 6 medalhas e, com `titulo`, campeao da Liga */
function tamer(titulo = true): Tamer {
  const t = new Tamer(), m = new Motor(1);
  for (const md of MEDALHAS) t.ganhar(md.id, m, 1);
  if (titulo) t.ganharTitulo(m, 2);
  return t;
}
/** um Rookie v13 de reserva, sem treino, que conhece as 6 medalhas */
function rookieReserva(semente = 7007): Motor {
  const m = new Motor(semente);
  m.liberar(6);
  while (m.estagioAtual === "bebe") m.avancar(30);
  return m;
}
/** a primeira tentativa (n, escolha) cuja primeira luta e vitoria, a partir de n0 */
function tentativaQueVence(n0 = 1): { n: number; escolha: number } {
  for (let n = n0; n < n0 + 200; n++) for (let e = 0; e < ALUGUEIS_FABRICA; e++) {
    const x = new TentativaFabrica(n, e);
    if (x.lutar(x.proxima()!.s).venceu) return { n, escolha: e };
  }
  throw new Error("nenhuma tentativa vence a primeira luta");
}

describe("Fábrica: o sorteio", () => {
  test("a semente sai do número da tentativa; os 3 alugados são Megas de arquétipos distintos; tudo reproduzível; as 8 formas e 4 espécies aparecem", () => {
    expect(sementeFabrica(1)).toBe(sementeFabrica(1));
    expect(new Set([1, 2, 3, 4].map(sementeFabrica)).size).toBe(4);
    expect(() => sementeFabrica(0)).toThrow(/inválido/);
    const formas = new Set<string>(), esps = new Set<string>(), rivais = new Set<string>();
    for (let n = 1; n <= 60; n++) {
      const s = sementeFabrica(n), a = alugueisFabrica(s);
      expect(alugueisFabrica(s)).toEqual(a);
      expect(a).toHaveLength(ALUGUEIS_FABRICA);
      expect(new Set(a.map(f => f.adulta)).size).toBe(ALUGUEIS_FABRICA);
      for (const f of a) { expect(f.est).toBe("mega"); formas.add(f.adulta!); esps.add(f.esp); }
      for (let k = 0; k < 4; k++) { expect(formaRivalFabrica(s, k)).toEqual(formaRivalFabrica(s, k)); rivais.add(formaRivalFabrica(s, k).adulta!); }
    }
    expect([...formas].sort()).toEqual([...FORMAS_AD].sort());
    expect([...rivais].sort()).toEqual([...FORMAS_AD].sort());
    expect([...esps].sort()).toEqual([...ESPECIES].sort());
  });
  test("o alugado e o rival: Mega canônico, lista V21D, sem treino, E = vida do Mega na escala v6 × 1, mesmo com a chave da escala desligada", () => {
    expect(FATOR_FABRICA).toBe(FATOR_INSTALACAO);
    const f = alugueisFabrica(sementeFabrica(3))[0], L = megaFabrica(f, "x");
    ligarEscala(false);
    expect(megaFabrica(f, "x")).toEqual(L);
    expect(L.cond.escala).toBeCloseTo(CESC_V6.vida.mega, 6);
    expect(L.cond.passiva).toBe(f.adulta);
    expect(L.estilo.gambits).toEqual(gambitsAdulto(f.adulta as (typeof FORMAS_AD)[number], CV21D));
    expect(() => megaFabrica({ ...f, est: "adulto" }, "x")).toThrow(/só tem Megas/);
  });
});

describe("Fábrica: a série, a troca e o fim", () => {
  test("sem cura dentro da série: o alugado leva a vida e o guts; cada rival começa inteiro; a série seguinte começa inteira", () => {
    let visto = 0;
    for (let n = 1; n <= 400 && visto < 2; n++) {
      const x = new TentativaFabrica(n, 0);
      while (!x.acabou) x.lutar(x.proxima()!.s);
      if (x.lutas.length < 2) continue;
      x.lutas.forEach((l, k) => {
        const L0 = l.res.E0.L;
        expect(L0[1].hp).toBe(L0[1].hpMax);                                          /* o rival inteiro */
        expect(l.s).toBe(sementeLutaFabrica(x.s, k));
        if (k % LUTAS_SERIE_FABRICA === 0) expect(L0[0].hp).toBe(L0[0].hpMax);       /* comeco de serie: inteiro */
        else { const a = x.lutas[k - 1].res.E.L[0]; expect(L0[0].hp).toBe(a.hp); expect(L0[0].guts).toBe(Math.min(a.guts, L0[0].gutsMax)); }
      });
      if (x.lutas.length > LUTAS_SERIE_FABRICA) visto++;
      expect(x.series).toBe(Math.floor(x.vitorias / LUTAS_SERIE_FABRICA));
    }
    expect(visto, "alguma tentativa passou da primeira série").toBeGreaterThan(0);
  });
  test("perdeu, acabou; a semente é a da tentativa (ninguém escolhe o rival)", () => {
    const x = new TentativaFabrica(5, 1), p = x.proxima()!;
    expect(() => x.lutar(p.s + 1)).toThrow(/semente/);
    expect(() => x.trocar()).toThrow(/depois de uma vitória/);
    while (!x.acabou) x.lutar(x.proxima()!.s);
    expect(x.lutas[x.lutas.length - 1].venceu).toBe(false);
    expect(x.lutas.slice(0, -1).every(l => l.venceu)).toBe(true);
    expect(x.proxima()).toBeNull();
    expect(() => x.lutar(1)).toThrow(/já acabou/);
    expect(() => x.trocar()).toThrow(/acabou/);
  });
  test("a troca: depois da vitória o alugado vira o rival derrotado, com a mesma fração da vida (a troca não cura), uma vez", () => {
    const { n, escolha } = tentativaQueVence(), x = new TentativaFabrica(n, escolha);
    const l = x.lutar(x.proxima()!.s), vida = x.vidaAgora;
    expect(l.venceu).toBe(true);
    expect(vida).toBeGreaterThan(0);
    expect(x.porqueNaoTroca()).toBeNull();
    x.trocar();
    expect(x.alugado).toEqual(l.rival);
    expect(l.trocou).toBe(true);
    expect(x.vidaAgora).toBeCloseTo(vida, 12);
    expect(() => x.trocar()).toThrow(/já trocou/);
    /* a proxima luta e com o novo alugado, na vida que sobrou */
    const { A, ini } = x.lutadores();
    expect(A.cond.passiva).toBe(l.rival.adulta);
    expect(ini!.hp / A.cond.hpMax).toBeCloseTo(vida, 12);
  });
});

describe("Fábrica: o registro do Tamer", () => {
  test("a tentativa inteira fica no Tamer (grava v: 13, a luta em tempo real) e se refaz só dele, sem pet e sem a chave da escala; o recorde são as séries vencidas", () => {
    const t = tamer();
    /* tentativas ate uma serie vencida: escolha 0, sem troca, e numa delas uma troca */
    let trocou = false;
    for (let i = 0; i < 400 && !t.recordeFabrica; i++) {
      const x = t.alugarFabrica(0, 100 + i);
      while (t.fabricaAtual) {
        const l = t.lutarFabrica(200 + i);
        if (l.venceu && !trocou && x.lutas.length === 1) { t.trocarFabrica(); trocou = true; }
      }
    }
    expect(trocou).toBe(true);
    const rec = t.recordeFabrica!;
    expect(rec.valor).toBeGreaterThanOrEqual(1);
    expect(rec.valor).toBe(Math.max(...t.fabrica.map(x => x.series)));
    expect(t.fabrica.find(x => x.n === rec.n)!.series).toBe(rec.valor);
    const tipos = new Set(t.log.map(e => e[0]));
    expect([...tipos].filter(x => x.startsWith("fabrica")).sort()).toEqual(["fabrica", "fabrica_luta", "fabrica_troca"]);
    /* o replay so pelo registro do Tamer (texto gravado), com a chave da escala desligada: as mesmas lutas */
    const a = { dados: {} as Record<string, string>, getItem(k: string) { return this.dados[k] ?? null; }, setItem(k: string, v: string) { this.dados[k] = v; } };
    gravarTamer(a, t);
    expect(JSON.parse(a.dados[CHAVE_TAMER]).versao).toBe(7);
    ligarEscala(false);
    const r = lerTamer(a);
    expect(r.fabrica.map(x => x.lutas.map(l => [l.s, l.venceu, tamanhoLuta(l.res), l.vidaFim, l.trocou]))).toEqual(t.fabrica.map(x => x.lutas.map(l => [l.s, l.venceu, tamanhoLuta(l.res), l.vidaFim, l.trocou])));
    expect(r.recordeFabrica).toEqual(rec);
    expect(textoTamer(r)).toBe(textoTamer(t));
  });
  test("falha alto: antes do título, fora de ordem, com outra semente, troca sem vitória, outra tentativa com uma em andamento", () => {
    const ev = (x: EventoTamer[]) => () => Tamer.reproduzir(x);
    const base = tamer().log, s1 = sementeFabrica(1);
    expect(ev([...tamer(false).log, ["fabrica", { n: 1, s: s1, alugado: 0, quando: 1 }]])).toThrow(/antes do título/);
    expect(ev([...base, ["fabrica", { n: 2, s: sementeFabrica(2), alugado: 0, quando: 1 }]])).toThrow(/fora de ordem/);
    expect(ev([...base, ["fabrica", { n: 1, s: s1 + 1, alugado: 0, quando: 1 }]])).toThrow(/semente/);
    expect(ev([...base, ["fabrica", { n: 1, s: s1, alugado: 3, quando: 1 }]])).toThrow(/escolha/);
    const ini: EventoTamer[] = [...base, ["fabrica", { n: 1, s: s1, alugado: 0, quando: 1 }]];
    expect(ev([...ini, ["fabrica", { n: 2, s: sementeFabrica(2), alugado: 0, quando: 1 }]])).toThrow(/em andamento/);
    expect(ev([...ini, ["fabrica_luta", { n: 1, k: 1, s: sementeLutaFabrica(s1, 1), quando: 1 }]])).toThrow(/fora de ordem/);
    expect(ev([...ini, ["fabrica_luta", { n: 1, k: 0, s: 7, quando: 1 }]])).toThrow(/semente/);
    expect(ev([...ini, ["fabrica_troca", { n: 1, k: 0, quando: 1 }]])).toThrow(/Fábrica/);
    expect(ev([...base, ["fabrica_luta", { n: 1, k: 0, s: sementeLutaFabrica(s1, 0), quando: 1 }]])).toThrow(/não está em andamento/);
    expect(ev([...base, ["fabrica_x" as "fabrica", { n: 1, s: s1, alugado: 0, quando: 1 }]])).toThrow(/desconhecido/);
  });
});

describe("Salão: os rivais", () => {
  test("o rival é o bot canônico do estágio, sorteado da semente; E = vida do estágio na escala v6 × 1", () => {
    const tipos: Record<string, Set<string>> = { crianca: new Set(), adolescente: new Set(), adulto: new Set(), mega: new Set() }, esps = new Set<string>();
    for (let n = 1; n <= 80; n++) for (const est of ESTAGIOS_SALAO) {
      const s = sementeSalao(77, n), f = formaRivalSalao(s, est), L = rivalSalao(s, est, CV21D);
      expect(formaRivalSalao(s, est)).toEqual(f);
      expect(f.est).toBe(est);
      expect(L.cond.escala).toBeCloseTo(CESC_V6.vida[est] * FATOR_SALAO, 6);
      expect(L.estilo.gambits).toEqual(est === "crianca" ? CRIANCA_V21[f.ramo!] : est === "adolescente" ? ADOL_V21[f.linha!] : gambitsAdulto(f.adulta as (typeof FORMAS_AD)[number], CV21D));
      tipos[est].add(f.adulta ?? f.linha ?? f.ramo!); esps.add(f.esp);
    }
    expect([...tipos.crianca].sort()).toEqual(["arisco", "sereno"]);
    expect([...tipos.adolescente].sort()).toEqual([...LINHAS].sort());
    expect([...tipos.adulto].sort()).toEqual([...FORMAS_AD].sort());
    expect([...tipos.mega].sort()).toEqual([...FORMAS_AD].sort());
    expect([...esps].sort()).toEqual([...ESPECIES].sort());
    expect(() => formaRivalSalao(1, "bebe")).toThrow(/fora do Salão/);
    expect(() => sementeSalao(1, 0)).toThrow(/inválido/);
  });
});

describe("Salão: a luta no registro do pet", () => {
  test("a entrada pede o título (evento 'f'); a semente sai do registro do pet; as cartas não valem; o In-Training não entra", () => {
    const m = abrir(PETS().guardados[0]), n = m.log.length;
    expect(m.estagioAtual).toBe("crianca");
    expect(m.porqueNaoSalao()).toMatch(/depois do título/);
    expect(() => m.lutar(RIVAL_SALAO, m.sementeSalao())).toThrow(/depois do título/);
    m.abrirFronteira();
    expect(m.porqueNaoSalao()).toBeNull();
    expect(m.sementeSalao()).toBe(sementeSalao(m.semente, 1));
    expect(() => m.lutar(RIVAL_SALAO, m.sementeSalao() + 1)).toThrow(/sai do registro/);
    expect(() => m.lutar(RIVAL_SALAO, m.sementeSalao(), "carta_folego")).toThrow(/cartas não valem/);
    expect(m.log).toHaveLength(n + 1);                                              /* so o "f" */
    const bebe = new Motor(42); bebe.liberar(6); bebe.abrirFronteira();
    expect(bebe.porqueNaoSalao()).toMatch(/In-Training/);
  });
  test("uma luta contra o rival do estágio: um evento 'l' {r: 'salao', s}, conta no pet, e o replay do registro dá o mesmo pet", () => {
    for (const x of [...PETS().guardados, PETS().liga]) {
      const m = abrir(x), antes = m.assinatura();
      expect(antes).not.toContain('"salao"');                                       /* a assinatura de quem nunca lutou la nao muda */
      m.abrirFronteira();
      const s = m.sementeSalao(), est = m.estagioAtual, L = m.lutadores(RIVAL_SALAO, s);
      expect(L.B.cond.passiva).toBe(formaRivalSalao(s, est).adulta ?? null);
      expect(L.B.cond.escala).toBeCloseTo(CESC_V6.vida[est] * fatorSalao(est, m.regras), 6);   /* no v13, o fator por nivel dos v9 */
      const r = m.lutar(RIVAL_SALAO, s);
      expect(r.serie).toHaveLength(1);
      expect(m.log[m.log.length - 1]).toEqual([m.e.tick, "l", { r: RIVAL_SALAO, s }]);
      expect(m.salao).toEqual({ tentativas: 1, vitorias: r.venceu ? 1 : 0 });
      expect(m.sementeSalao()).toBe(sementeSalao(m.semente, 2));
      expect(m.historico.some(h => h.quem === "luta" && h.a.startsWith("no Salão, contra"))).toBe(true);
      const rep = Motor.reproduzir(m.semente, m.log, m.versao);
      expect(rep.assinatura()).toBe(m.assinatura());
      expect(rep.assinatura()).toContain('"salao"');
      /* outra semente no registro falha no replay */
      const log = m.log.map(e => [...e] as EventoRegistro);
      (log[log.length - 1][2] as { s: number }).s += 1;
      expect(() => Motor.reproduzir(m.semente, log, m.versao)).toThrow(/semente/);
    }
  });
});

describe("Salão: a tentativa (um pet por estágio) e o recorde no Tamer", () => {
  test("o app: o ativo (Mega) e os guardados (Rookie, Champion, Ultimate) lutam, cada um no registro dele; o recorde vai para o Tamer", () => {
    const dados: Record<string, string> = {}, a: Armazenamento & { removeItem(k: string): void } = {
      getItem: k => dados[k] ?? null, setItem(k, v) { dados[k] = v; }, removeItem(k) { delete dados[k]; } };
    (globalThis as { localStorage?: unknown }).localStorage = a;
    try {
      dados[CHAVE] = JSON.stringify(PETS().liga);
      /* os guardados v13 (Rookie, Champion, Ultimate) e um Rookie de reserva, sem treino */
      const reserva = rookieReserva();
      dados[CHAVE_GUARDADOS] = JSON.stringify([...PETS().guardados, { semente: reserva.semente, log: reserva.log, versao: 13 }]);
      gravarTamer(a, tamer());
      iniciarJogo(a);
      expect(jogoAtual().motor.fronteira).toBe(true);                               /* o ativo recebeu o "f" na abertura */
      const c = candidatosSalao();
      expect(c.map(x => [x.origem, x.est, x.erro, x.m.versao])).toEqual([["ativo", "mega", null, 13], [0, "crianca", null, 13], [1, "adolescente", null, 13], [2, "adulto", null, 13], [3, "crianca", null, 13]]);
      expect(estagiosQueFaltam(c)).toEqual([]);
      expect(estagiosQueFaltam(c.filter(x => x.est !== "adolescente"))).toEqual(["adolescente"]);
      expect(() => tentarSalao([0, 1, 2, 2])).toThrow(/mesmo pet/);
      expect(() => tentarSalao([1, 0, 2, "ativo"])).toThrow(/não Rookie/);
      const antes = PETS().guardados.map(g => g.log.length), r = tentarSalao([0, 1, 2, "ativo"]);
      /* os pets do teste (petQueVence) vencem a primeira luta dele no Salao */
      expect(r.lutas.map(x => [x.est, x.venceu])).toEqual(ESTAGIOS_SALAO.map(e => [e, true]));
      const t = tamerAtual();
      expect(t.recordeSalao).toEqual({ valor: 4, n: 1, quando: expect.any(Number) });
      const ev = t.salao[0];
      expect(ev.lutas.map(l => [l.est, l.k, l.s])).toEqual([PETS().guardados[0], PETS().guardados[1], PETS().guardados[2], PETS().liga].map((x, i) => [ESTAGIOS_SALAO[i], 1, sementeSalao(x.semente, 1)]));
      /* cada guardado: o "f" e a luta no registro dele (continua guardado, na hora parada dele) */
      lerGuardados().slice(0, 3).forEach((g, i) => {
        expect(g.log.length).toBe(antes[i] + 2);
        expect(g.log[g.log.length - 2][1]).toBe("f");
        expect(g.log[g.log.length - 1]).toEqual([g.log[g.log.length - 1][0], "l", { r: RIVAL_SALAO, s: sementeSalao(g.semente, 1) }]);
        expect(Motor.reproduzir(g.semente, g.log, g.versao).salao).toEqual({ tentativas: 1, vitorias: 1 });
      });
      const m = jogoAtual().motor;
      expect(m.salao).toEqual({ tentativas: 1, vitorias: 1 });
      expect(Motor.reproduzir(m.semente, m.log, m.versao).assinatura()).toBe(m.assinatura());
      /* o registro do Tamer gravado se refaz sozinho; a segunda tentativa usa a luta 2 de cada pet */
      expect(lerTamer(a).recordeSalao).toEqual(t.recordeSalao);
      const r2 = tentarSalao([0, 1, 2, "ativo"]);
      expect(tamerAtual().salao[1].lutas.every(l => l.k === 2)).toBe(true);
      expect(tamerAtual().recordeSalao!.valor).toBe(4);
      expect(r2.lutas.length).toBeGreaterThanOrEqual(1);
      /* o Rookie de reserva no lugar do primeiro guardado */
      const n3 = tamerAtual().salao.length, r3 = tentarSalao([3, 1, 2, "ativo"]);
      expect(tamerAtual().salao[n3].lutas[0]).toMatchObject({ est: "crianca", pet: 7007, k: 1 });
      expect(r3.lutas[0].est).toBe("crianca");
      const g3 = lerGuardados()[3];
      expect(g3.versao).toBe(13);
      expect(Motor.reproduzir(g3.semente, g3.log, 13).salao.tentativas).toBe(1);
    } finally { delete (globalThis as { localStorage?: unknown }).localStorage; }
  });
  test("falha alto no Tamer: fora da ordem dos estágios, segue depois de derrota, para numa vitória, o mesmo pet duas vezes, outra semente, antes do título", () => {
    const luta = (est: string, pet: number, venceu: boolean, k = 1): LutaSalao => ({ est: est as LutaSalao["est"], pet, forma: "X", k, s: sementeSalao(pet, k), tick: 1, venceu });
    const ev = (lutas: LutaSalao[], t = tamer()) => () => Tamer.reproduzir([...t.log, ["salao", { n: 1, quando: 1, lutas }]]);
    expect(ev([luta("crianca", 1, false)])).not.toThrow();
    expect(ev([luta("crianca", 1, true), luta("adolescente", 2, true), luta("adulto", 3, true), luta("mega", 4, false)])).not.toThrow();
    expect(ev([luta("adolescente", 1, false)])).toThrow(/estágio/);
    expect(ev([luta("crianca", 1, false), luta("adolescente", 2, false)])).toThrow(/depois de uma derrota/);
    expect(ev([luta("crianca", 1, true)])).toThrow(/parou numa vitória/);
    expect(ev([luta("crianca", 1, true), luta("adolescente", 1, false)])).toThrow(/mesmo pet/);
    expect(ev([{ ...luta("crianca", 1, false), s: 5 }])).toThrow(/semente/);
    expect(ev([luta("crianca", 1, false)], tamer(false))).toThrow(/antes do título/);
    expect(() => Tamer.reproduzir([...tamer().log, ["salao", { n: 2, quando: 1, lutas: [luta("crianca", 1, false)] }]])).toThrow(/fora de ordem/);
    const t = Tamer.reproduzir([...tamer().log, ["salao", { n: 1, quando: 1, lutas: [luta("crianca", 1, true), luta("adolescente", 2, false)] }]]);
    expect(t.recordeSalao).toEqual({ valor: 1, n: 1, quando: 1 });
  });
  test("o registro do Tamer lê as versões 1 a 5; evento desconhecido falha", () => {
    const a = { dados: {} as Record<string, string>, getItem(k: string) { return this.dados[k] ?? null; }, setItem(k: string, v: string) { this.dados[k] = v; } };
    for (const v of [1, 2, 3, 4, 5]) { a.dados[CHAVE_TAMER] = JSON.stringify({ versao: v, log: tamer().log }); expect(lerTamer(a).titulo).not.toBeNull(); }
    a.dados[CHAVE_TAMER] = JSON.stringify({ versao: 8, log: [] });
    expect(() => lerTamer(a)).toThrow(/versão/);
    expect(hashSemente("fronteira", "salao", 1, 1)).toBe(sementeSalao(1, 1));
  });
});

describe("sincronizarPet num guardado", () => {
  test("o guardado v6 recebe o 'f' quando o Tamer tem o título; nada mais muda nele", () => {
    const m = abrir(PETS().guardados[1]), n = m.log.length, est = m.estagioAtual;
    expect(sincronizarPet(tamer(), m)).toBe(true);
    expect(m.log.length).toBe(n + 1);
    expect(m.estagioAtual).toBe(est);
  });
});
