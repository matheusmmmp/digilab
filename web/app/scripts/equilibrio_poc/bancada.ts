/* LUTA_POC, LP5 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secoes 2 e 4.1): os grupos da bancada. Cada grupo roda as lutas das metas dele e grava
   um JSON com as contas brutas (vitorias, lutas, empates, sem fim e o relogio em histograma); o resumo_metas.ts le os JSON e da a tabela.
   Os tamanhos das amostras sao PROPOSTOS, SEM FONTE (secao 4.1; os cortes estao no desvio D-LP5-0-3).
   uso (em web/app): node scripts/equilibrio_poc/bancada.ts --grupo <grupo> --faixa calibracao --fase lp5_0 [--candidato v21]
   grupos: lideres, sparring, vida, treino, estagio, formas_crianca, formas_adolescente, formas_adulto, formas_mega, torneios */
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  ACOES_DONO_JOGO_V11, ARENA_POR_ID, CAMPANHA_V6, CAT, CD, CMD, CTR, IDS_CENA, LIGA, LUGARES_V6, LUTAS_MAX_INSTALACAO, MAPA_FABRICA, MAPA_SALAO,
  MAPA_TORRE, Motor, NPC, STATS, TPD, VERSAO_V22, alugueisFabrica, arenaDaLuta, caraterCanonico, caraterDoRivalSalao, chaveSprite, criarDono, criarRng,
  LIMITE_POC_MS, condicaoDe, configLutaPoc, criarLutaPoc, formaLiga, formaRivalFabrica, passoPoc, sorteiosPoc, formaRivalInstalacao, formaRivalSalao, hashSemente, mapaDoLugar, rivaisArena, sementeDaSerie, sementeLutaFabrica,
  type Exercicio, type Forma, type FormaAdultaNormal, type IdCena, type Stat, type StatsPoc, type TiroPoc, type EsquivaPoc, type VisaoDono,
} from "../../motor/index.ts";
import {
  CANDIDATO_V21, ESTAGIOS_LUTA, atira, esquivaDe, tiroDaPoc, TETO, TIPICO, argumento, commitAtual, contar, juntar, lutador, lutadorDoPet, lutar, novaConta, npc,
  petDoEstagio, pontosNumStat, rivalCanonico, rivalDaForma, sementeLuta, taxa,
  type Candidato, type Conta, type EstagioLuta, type Lado, type Luta1, type PetBancada,
} from "./comum.ts";
import { basesDa } from "./faixas.ts";
import { candidatoDaLinha } from "./candidatos.ts";

/** os tamanhos (PROPOSTOS, SEM FONTE; secao 4.1 e o desvio D-LP5-0-3) */
export const TAM: Record<string, number> = {
  pets: 20,          // pets por estagio e por base (100 por estagio nas 5 bases)
  lutas: 20,         // lutas por par (pet, rival, mapa) nas metas de um rival so (P1-P3, T1, G4) e no sparring (P4, V2)
  lutasT2: 5,        // T2: um stat por vez, 8 mapas
  lutasGrade: 2,     // T3: a grade dos pontos contra todas as formas do estagio
  lutasE1: 4,        // E1: contra todas as formas do estagio de cima
  lutasFormas: 25,   // A1, V1, S1: por par ordenado e mapa, em cada base
  lutasTiro: 1,      // A2: por par (quem atira, o outro), mapa, lado e base (D-LP5-12)
  tentativas: 20,    // torneios: tentativas por pet (a Liga, a Torre, o Salao) e por pet-equivalente (a Fabrica)
  vidas: 20,         // P5: vidas por base
  diasVida: 4,       // P5: a vida vai ate o Mega ou ate 4 dias de jogo (o Mega precisa de ~2,4 dias)
  seriesFabrica: 7,  // G3: a tentativa para no fim da 7a serie (21 lutas), para acabar
};
/** --rapido: a fumaca (1 pet, poucas lutas, 1 base), so para conferir que o grupo roda; o artefato vai para --saida, fora das medicoes */
const RAPIDO = { pets: 1, lutas: 2, lutasT2: 1, lutasGrade: 1, lutasE1: 1, lutasFormas: 1, lutasTiro: 1, tentativas: 2, vidas: 1 };

const LIDERES = LIGA.map(x => x.lider);
const DESAFIANTES = ["npc_tier2_sentinela", "npc_tier2_porteiro", "npc_v5_puppetmon", "npc_v5_machinedramon"];

/* ---------------------------------------------------------------- a duracao (D1, D2): toda luta conta, por estagio e por forma */
class Duracao {
  por_estagio: Record<string, Conta> = {};
  por_forma: Record<string, Conta> = {};
  add(est: string, formas: string[], r: Luta1): void {
    contar(this.por_estagio[est] ??= novaConta(), r);
    for (const f of new Set(formas)) contar(this.por_forma[f] ??= novaConta(), r);
  }
}
const D = new Duracao();
let LUTAS = 0;
/** o tiro do candidato que roda (rodar() o poe; a luta so o leva quando ele nao e o da POC) */
let TIRO: TiroPoc | undefined;
/** a esquiva do candidato que roda (so ligada; D-LP5-14) */
let ESQ: EsquivaPoc | undefined;
function luta(est: string, cena: IdCena, s: number, a: Lado, b: Lado): Luta1 {
  const r = lutar(cena, s, a, b, TIRO, ESQ); LUTAS++; D.add(est, [a.forma, b.forma], r); return r;
}
/** uma serie sem cura para o pet (a Cidadela, a Liga, a Torre): vai ate a primeira que nao for vitoria ou ate n. Cada rival entra inteiro */
function serie(est: string, s: number, pet: Lado, rivais: (j: number) => { lado: Lado; mapa: IdCena } | null, n: number): { vitorias: number; relogio: number } {
  let vida0 = pet.stats.hp, v = 0, rel = 0;
  for (let j = 0; j < n; j++) {
    const rv = rivais(j); if (!rv) break;
    const r = luta(est, rv.mapa, sementeDaSerie(s, j), { ...pet, ...(j ? { vida0 } : {}) }, rv.lado);
    rel += r.relogio;
    if (r.vencedor !== "a") break;
    v++; vida0 = r.vidaA;
  }
  return { vitorias: v, relogio: rel };
}
const ladoPet = (c: Candidato, p: PetBancada, n: number): Lado => ({ forma: p.chave, stats: lutadorDoPet(c, p, n) });
const petsDo = (bases: number[], est: EstagioLuta): PetBancada[] => bases.flatMap(b => Array.from({ length: TAM.pets }, (_, i) => petDoEstagio(b, i, est)));
const add = (m: Record<string, Conta>, k: string, r: Luta1) => contar(m[k] ??= novaConta(), r);
const lugarV6 = (k: string): number => { const c = CAMPANHA_V6.find(x => x.k === k); if (!c) throw new Error(`bancada: ${k} fora da campanha v6`); return c.lug; };

/* ---------------------------------------------------------------- P1, P2, P3, D3: os lideres e os desafiantes */
function lideres(c: Candidato, bases: number[]) {
  const out: Record<string, unknown> = {};
  for (const k of [...LIDERES, ...DESAFIANTES]) {
    const n = NPC[k]!, est = n.est as EstagioLuta, mapa = mapaDoLugar(LUGARES_V6[lugarV6(k)]), ns = arenaDaLuta(k)?.lutas ?? 1;
    const rival: Lado = { forma: k, stats: npc(c, k) }, pets = petsDo(bases, est), conds: Record<string, unknown> = {};
    for (const [nome, pts] of [["sem_treino", 0], ["tipico", TIPICO[est]]] as const) {
      const total = novaConta(), esp: Record<string, Conta> = {}, forma: Record<string, Conta> = {}, relSerie: Record<string, number> = {};
      for (const p of pets) {
        const lado = ladoPet(c, p, pts);
        for (let q = 0; q < TAM.lutas; q++) {
          const s = sementeLuta(p.base, p.i * TAM.lutas + q), r = serie(est, s, lado, () => ({ lado: rival, mapa }), ns);
          const fake: Luta1 = { vencedor: r.vitorias === ns ? "a" : "b", fim: true, relogio: r.relogio, vidaA: 0 };
          contar(total, fake); add(esp, p.especie, fake); add(forma, p.chave, fake);
          if (ns > 1) { const b = String(Math.floor(r.relogio / 100)); relSerie[b] = (relSerie[b] ?? 0) + 1; }
        }
      }
      conds[nome] = { pontos: pts, total, por_especie: esp, por_forma: forma, ...(ns > 1 ? { relogio_serie: relSerie } : {}) };
    }
    out[k] = { nome: n.nome, estagio: est, mapa, lutas_serie: ns, lider: LIDERES.includes(k), ...conds };
  }
  return out;
}

/* ---------------------------------------------------------------- P4, V2: o sparring (o pet tipico contra as formas do estagio, no Campo) */
function sparring(c: Candidato, bases: number[]) {
  const out: Record<string, unknown> = {};
  for (const est of ESTAGIOS_LUTA) {
    const rv = rivaisArena(est), rivais = rv.map(k => ({ forma: k, stats: rivalCanonico(c, k, c.treinoRival.arena) }));
    const pets: unknown[] = [], esp: Record<string, Conta> = {};
    for (const p of petsDo(bases, est)) {
      const lado = ladoPet(c, p, TIPICO[est]), conta = novaConta();
      rivais.forEach((b, j) => { for (let q = 0; q < TAM.lutas; q++) { const r = luta(est, "campo", sementeLuta(p.base, (p.i * rv.length + j) * TAM.lutas + q), lado, b); contar(conta, r); add(esp, p.especie, r); } });
      pets.push({ base: p.base, i: p.i, chave: p.chave, especie: p.especie, n: conta.n, v: conta.v });
    }
    out[est] = { rivais: rv, pontos: TIPICO[est], pets, por_especie: esp };
  }
  return out;
}

/* ---------------------------------------------------------------- P5: a vida do dono simulado (o Motor de verdade) */
const EXERCICIOS = Object.keys(CTR.exercicios) as Exercicio[];
/** o Motor da vida com os numeros da luta do candidato, so nesta instancia (LP5-2; desvio D-LP5-1-2): o pet pelo lutador() do candidato,
    com o treino, os chips e a condicao do Motor, e o rival da Arena pelo rivalCanonico(); o jogo nao muda. O v21 fica com o Motor de sempre,
    e o teste confere que o remendo com os numeros do v21 da a mesma vida */
export function motorDoCandidato(c: Candidato, semente: number, remendar = c.nome !== CANDIDATO_V21.nome): Motor {
  /* a bancada mediu sobre a v22 (a luta de sempre); a v23 e o candidato lp5_3 no jogo (LP5-5), e o teste confere que dao o mesmo */
  const m = new Motor(semente, VERSAO_V22);
  if (!remendar) return m;
  const x = m as unknown as Record<string, unknown>, rivalDoMotor = (x._rivalPoc as (...a: unknown[]) => { forma: string; stats: StatsPoc } | null).bind(m);
  x.statsLutaPoc = () => lutador(c, m.forma, m.carater(), m.pontosDeLuta(), condicaoDe(m.e.saude));
  /* o tiro do candidato pela entrada opcional do Motor (desvio D-LP5-1-11); o da POC fica fora, e a luta sai a de sempre */
  if (!tiroDaPoc(c.tiro)) m.tiroLutaPoc = { ...c.tiro };
  const esq = esquivaDe(c); if (esq) m.esquivaLutaPoc = esq;
  x._rivalPoc = (rival: string, ...resto: unknown[]) => {
    if (!rivaisArena(m.estagioAtual).includes(rival)) throw new Error(`bancada: a vida do candidato so luta na Arena, nao com ${rival}`);
    const rv = rivalDoMotor(rival, ...resto);
    return rv && { ...rv, stats: rivalCanonico(c, rv.forma, c.treinoRival.arena) };
  };
  return m;
}
function vida(c: Candidato, bases: number[]) {
  const vidas: unknown[] = [];
  for (const base of bases) for (let i = 0; i < TAM.vidas; i++) {
    const semente = hashSemente("equilibrio-poc-pet", base, i), m = motorDoCandidato(c, semente), dono = criarDono("atencioso");
    const r = criarRng(hashSemente("dono", semente, "atencioso")), passos = Math.round(TAM.diasVida * TPD / CD.passo), orc = Math.round(CD.porDia * TAM.diasVida);
    let gasto = 0, ex = 0, k = 0;
    const lutasEst: Record<string, { n: number; v: number }> = {};
    m.liberar(CMD.mega);
    for (let p = 0; p < passos && m.estagioAtual !== "mega" && !m.morte; p++) {
      m.avancar(CD.passo);
      if (m.morte) break;
      const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
      const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
      const acoes = dono.decidir(v, r).filter(a => ACOES_DONO_JOGO_V11.includes(a));
      if (m.lesionadoDesde !== null && acoes.length) acoes[0] = "tratar_lesao";
      for (const a of acoes) { m.observar(a); gasto++; }
      if (m.morte) break;
      const est = m.estagioAtual;
      /* o dono treina os 6 exercicios, um por vez, ate o tipico do estagio (D-LP5-2) */
      if (est !== "bebe" && m.treino.total < TIPICO[est as EstagioLuta] - 1e-9 && m.treino.podeTocar(m.e.tick) && !m.treino.pedePausa) m.treinar(EXERCICIOS[ex++ % EXERCICIOS.length]);
      /* e luta como o dono de test/evolucao_canonica.test.ts: o sparring contra uma forma do estagio, no Campo */
      if ((est === "adolescente" && m.sparring < CAT.sparring) || (est === "adulto" && m.lutas.lutas < 12)) {
        const rv = m.rivaisArenaPoc(), s = hashSemente("equilibrio-poc", base, "vida", i, k++);
        const res = m.lutarPoc(rv[s % rv.length], s, "campo"), u = res.serie[res.serie.length - 1];
        D.add(est, [res.forma, u.contra], { vencedor: u.vencedor, fim: u.fim, relogio: u.relogio, vidaA: u.vidaA }); LUTAS++;
        const L = lutasEst[est] ??= { n: 0, v: 0 }; L.n++; if (res.venceu) L.v++;
      }
    }
    vidas.push({ base, i, semente, especie: m.especie, estagio: m.estagioAtual, mega: m.estagioAtual === "mega", morte: m.morte?.causa ?? null, tick: m.e.tick, treino: m.treino.total, lutas: lutasEst });
  }
  return { dias: TAM.diasVida, vidas };
}

/* ---------------------------------------------------------------- T1, T2, T3 */
function treino(c: Candidato, bases: number[]) {
  const t1: Record<string, Conta> = {}, t2: Record<string, Record<string, Conta>> = {}, t3: Record<string, Record<string, Conta>> = {}, t3r: Record<string, Conta> = {};
  for (const est of ESTAGIOS_LUTA) {
    const pets = petsDo(bases, est), rv = rivaisArena(est), rivais = rv.map(k => ({ forma: k, stats: rivalCanonico(c, k) }));
    for (const p of pets) {
      const sem = ladoPet(c, p, 0), tip = ladoPet(c, p, TIPICO[est]);
      IDS_CENA.forEach((m, j) => { for (let q = 0; q < TAM.lutas; q++) contar(t1[est] ??= novaConta(), luta(est, m, sementeLuta(p.base, ((p.i * 8 + j) * TAM.lutas + q)), tip, sem)); });
      if (est === "crianca" || est === "adulto") for (const st of STATS as readonly Stat[]) {
        const um: Lado = { forma: p.chave, stats: lutador(c, p.forma, p.carater, pontosNumStat(st, TIPICO.crianca)) };
        IDS_CENA.forEach((m, j) => { for (let q = 0; q < TAM.lutasT2; q++) contar((t2[est] ??= {})[st] ??= novaConta(), luta(est, m, sementeLuta(p.base, 1_000_000 + (p.i * 8 + j) * TAM.lutasT2 + q), um, sem)); });
      }
      for (let n = 0; n <= TETO[est]; n += 2) {
        const lado = ladoPet(c, p, n);
        rivais.forEach((b, j) => { for (let q = 0; q < TAM.lutasGrade; q++) contar((t3[est] ??= {})[String(n)] ??= novaConta(), luta(est, "campo", sementeLuta(p.base, 2_000_000 + (p.i * rv.length + j) * TAM.lutasGrade + q), lado, b)); });
      }
      if (est === "crianca") {
        const teto = ladoPet(c, p, TETO.crianca);
        IDS_CENA.forEach((m, j) => { for (let q = 0; q < TAM.lutas; q++) contar(t3r.crianca ??= novaConta(), luta(est, m, sementeLuta(p.base, 3_000_000 + (p.i * 8 + j) * TAM.lutas + q), teto, tip)); });
      }
    }
  }
  return { t1_tipico_contra_sem: t1, t2_um_stat_contra_sem: t2, t3_grade_contra_rivais: t3, t3_teto_contra_tipico: t3r, pontos_t2: TIPICO.crianca };
}

/* ---------------------------------------------------------------- E1: a evolucao contra o treino */
function estagio(c: Candidato, bases: number[]) {
  const out: Record<string, Conta> = {};
  const contra = (nome: string, est: EstagioLuta, alvo: EstagioLuta, pts: number, desl: number) => {
    const rv = rivaisArena(alvo), rivais = rv.map(k => ({ forma: k, stats: rivalCanonico(c, k) }));
    for (const p of petsDo(bases, est)) {
      const lado = ladoPet(c, p, pts);
      rivais.forEach((b, j) => { for (let q = 0; q < TAM.lutasE1; q++) contar(out[nome] ??= novaConta(), luta(est, "campo", sementeLuta(p.base, desl + (p.i * rv.length + j) * TAM.lutasE1 + q), lado, b)); });
    }
  };
  ESTAGIOS_LUTA.slice(0, 3).forEach((est, x) => {
    const um = ESTAGIOS_LUTA[x + 1];
    contra(`${est}_tipico_contra_${um}`, est, um, TIPICO[est], 4_000_000);
    contra(`${est}_teto_contra_${um}`, est, um, TETO[est], 5_000_000);
    if (x < 2) contra(`${est}_tipico_contra_${ESTAGIOS_LUTA[x + 2]}`, est, ESTAGIOS_LUTA[x + 2], TIPICO[est], 6_000_000);
  });
  return out;
}

/* ---------------------------------------------------------------- A1, V1, S1: as formas contra as formas */
function formas(c: Candidato, bases: number[], est: EstagioLuta) {
  const rv = rivaisArena(est), lados = rv.map(k => ({ forma: k, stats: rivalCanonico(c, k) }));
  const pares: Record<string, Record<string, Conta>> = {};
  for (const m of IDS_CENA) for (let x = 0; x < rv.length; x++) for (let y = 0; y < rv.length; y++) {
    const conta = (pares[m] ??= {})[`${rv[x]}|${rv[y]}`] = novaConta();
    for (const base of bases) for (let q = 0; q < TAM.lutasFormas; q++) contar(conta, luta(est, m, sementeLuta(base, 7_000_000 + q), lados[x], lados[y]));
  }
  return { estagio: est, formas: rv, pares };
}

/* ---------------------------------------------------------------- A2: a distancia do tiro contra quem luta de perto (D-LP5-12) */
/** a distancia (px) no instante em que cada tiro de projetil nasce, em histograma de 4 px: quem atira contra quem luta de perto, nos dois
    lados e nos 8 mapas, sem treino (como o A1); e, so para leitura, quem atira contra quem atira */
function tiro(c: Candidato, bases: number[]) {
  const out: Record<string, unknown> = {};
  for (const est of ESTAGIOS_LUTA) {
    const rv = rivaisArena(est), longe = rv.filter(atira), perto = rv.filter(k => !atira(k)), lados = Object.fromEntries(rv.map(k => [k, { forma: k, stats: rivalCanonico(c, k) }]));
    const hist = { perto: {} as Record<string, number>, longe: {} as Record<string, number> }, voo = { perto: {} as Record<string, number>, longe: {} as Record<string, number> };
    for (const [tipo, alvos] of [["perto", perto], ["longe", longe]] as const) for (const x of longe) for (const y of alvos) for (const m of IDS_CENA) for (const base of bases)
      for (let q = 0; q < TAM.lutasTiro; q++) for (const ladoX of ["a", "b"] as const) {
        const s = sementeLuta(base, 12_000_000 + q), A = ladoX === "a" ? lados[x] : lados[y], B = ladoX === "a" ? lados[y] : lados[x];
        const L = criarLutaPoc(configLutaPoc({ cena: m, semente: s, a: A, b: B, ...(TIRO && !tiroDaPoc(TIRO) ? { tiro: TIRO } : {}), ...(ESQ ? { esquiva: ESQ } : {}) }), sorteiosPoc(s));
        const quem = ladoX === "a" ? L.a : L.b, vistos = new Map<unknown, number>();
        while (!L.fim && L.relogio < LIMITE_POC_MS) {
          passoPoc(L);
          for (const p of L.projeteis) if (p.de === quem && !vistos.has(p)) {
            vistos.set(p, 0);
            const b = String(4 * Math.floor(Math.hypot(L.a.x - L.b.x, L.a.y - L.b.y) / 4)); hist[tipo][b] = (hist[tipo][b] ?? 0) + 1;
          }
          for (const [p, n] of vistos) if (n >= 0) { if (L.projeteis.includes(p as never)) vistos.set(p, n + 1); else { const k = String(n); voo[tipo][k] = (voo[tipo][k] ?? 0) + 1; vistos.set(p, -1); } }
        }
        LUTAS++;
      }
    out[est] = { longe, perto, distancia_px: hist, voo_passos: voo };
  }
  return out;
}

/* ---------------------------------------------------------------- G1-G4: os torneios */
function torneios(c: Candidato, bases: number[]) {
  const pets = petsDo(bases, "mega");
  /* G1, a Liga: os 6 Megas dos lideres, sem cura, cada um no mapa do lugar do lider */
  const liga = { tentativas: 0, titulos: 0, por_forma: {} as Record<string, { n: number; v: number }>, vitorias: {} as Record<string, number> };
  const megasLiga = LIGA.map((x, k) => { const f = formaLiga(k); return { lado: { forma: chaveSprite(f), stats: rivalDaForma(c, f, caraterCanonico(x.adulta), c.treinoRival.liga, c.fatorRival.liga) }, mapa: mapaDoLugar(LUGARES_V6[ARENA_POR_ID[x.arena].lugar]) }; });
  /* G2, a Torre de Batalha: Megas sorteados pela semente da tentativa, no Ringue, sem cura, ate 100 */
  const torre = { tentativas: 0, no_teto: 0, recordes: [] as number[], vitorias: {} as Record<string, number> };
  const megaTorre = (s: number, j: number) => { const f = formaRivalInstalacao(s, j); return { lado: { forma: chaveSprite(f), stats: rivalDaForma(c, f, caraterCanonico(f.adulta as FormaAdultaNormal), c.treinoRival.torre, c.fatorRival.torre) }, mapa: MAPA_TORRE }; };
  for (const p of pets) {
    const lado = ladoPet(c, p, TIPICO.mega);
    let recorde = 0;
    const L = liga.por_forma[p.chave] ??= { n: 0, v: 0 };
    for (let q = 0; q < TAM.tentativas; q++) {
      const r = serie("mega", sementeLuta(p.base, 8_000_000 + p.i * TAM.tentativas + q), lado, j => megasLiga[j] ?? null, LIGA.length);
      liga.tentativas++; L.n++; liga.vitorias[r.vitorias] = (liga.vitorias[r.vitorias] ?? 0) + 1;
      if (r.vitorias === LIGA.length) { liga.titulos++; L.v++; }
      const s = sementeLuta(p.base, 9_000_000 + p.i * TAM.tentativas + q), t = serie("mega", s, lado, j => megaTorre(s, j), LUTAS_MAX_INSTALACAO);
      torre.tentativas++; if (t.vitorias === LUTAS_MAX_INSTALACAO) torre.no_teto++;
      torre.vitorias[t.vitorias] = (torre.vitorias[t.vitorias] ?? 0) + 1; recorde = Math.max(recorde, t.vitorias);
    }
    torre.recordes.push(recorde);
  }
  /* G3, a Fabrica: o alugado escolhido (k % 3), sem troca; a vida passa dentro da serie de 3 */
  const fab = { tentativas: 0, series: {} as Record<string, number> };
  /* o alugado e os rivais com o treino da Fabrica; so os rivais levam o fator (D-LP5-20) */
  const megaFab = (f: Forma, fator: number): Lado => ({ forma: chaveSprite(f), stats: rivalDaForma(c, f, caraterCanonico(f.adulta as FormaAdultaNormal), c.treinoRival.fabrica, fator) });
  for (const base of bases) for (let k = 0; k < TAM.pets * TAM.tentativas; k++) {
    const s = sementeLuta(base, 10_000_000 + k), alugado = megaFab(alugueisFabrica(s)[k % 3], 1);
    let vida0: number | null = null, v = 0;
    for (let j = 0; j < 3 * TAM.seriesFabrica; j++) {
      const r = luta("mega", MAPA_FABRICA, sementeLutaFabrica(s, j), { ...alugado, ...(vida0 !== null && j % 3 ? { vida0 } : {}) }, megaFab(formaRivalFabrica(s, j), c.fatorRival.fabrica));
      if (r.vencedor !== "a") break;
      v++; vida0 = r.vidaA;
    }
    fab.tentativas++; const se = String(Math.floor(v / 3)); fab.series[se] = (fab.series[se] ?? 0) + 1;
  }
  /* G4, o Salao: o pet tipico de cada estagio contra o rival sorteado do estagio, no Coliseu */
  const salao: Record<string, Conta> = {};
  for (const est of ESTAGIOS_LUTA) for (const p of petsDo(bases, est)) {
    const lado = ladoPet(c, p, TIPICO[est]);
    for (let q = 0; q < TAM.tentativas; q++) {
      const s = sementeLuta(p.base, 11_000_000 + p.i * TAM.tentativas + q), f = formaRivalSalao(s, est);
      contar(salao[est] ??= novaConta(), luta(est, MAPA_SALAO, s, lado, { forma: chaveSprite(f), stats: rivalDaForma(c, f, caraterDoRivalSalao(f), c.treinoRival.salao, c.fatorRival.salao) }));
    }
  }
  return { liga, torre, fabrica: fab, salao };
}

/* ---------------------------------------------------------------- a linha de comando */
export const GRUPOS = ["lideres", "sparring", "vida", "treino", "estagio", "formas_crianca", "formas_adolescente", "formas_adulto", "formas_mega", "torneios", "tiro"] as const;
function rodar(grupo: string, c: Candidato, bases: number[]): unknown {
  TIRO = c.tiro; ESQ = esquivaDe(c);
  switch (grupo) {
    case "tiro": return tiro(c, bases);
    case "lideres": return lideres(c, bases);
    case "sparring": return sparring(c, bases);
    case "vida": return vida(c, bases);
    case "treino": return treino(c, bases);
    case "estagio": return estagio(c, bases);
    case "torneios": return torneios(c, bases);
    default:
      if (grupo.startsWith("formas_")) { const e = grupo.slice(7); if ((ESTAGIOS_LUTA as readonly string[]).includes(e)) return formas(c, bases, e as EstagioLuta); }
      throw new Error(`bancada: grupo desconhecido ${JSON.stringify(grupo)} (${GRUPOS.join(", ")})`);
  }
}
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const grupo = argumento("grupo"), faixa = argumento("faixa"), fase = argumento("fase"), nomeC = argumento("candidato", "v21");
  if (!/^lp5_[0-9a-z_]+$/.test(fase)) throw new Error(`bancada: fase invalida ${fase}`);
  if (faixa === "conferencia" && fase !== "lp5_4") throw new Error("bancada: a conferencia so roda na LP5-4 (secao 4.4)");
  const rapido = process.argv.includes("--rapido"), grade = process.argv.includes("--grade");
  if (rapido && grade) throw new Error("bancada: --rapido ou --grade, nao os dois");
  if (grade && faixa !== "calibracao") throw new Error("bancada: a grade so roda na calibracao");
  const c = candidatoDaLinha(nomeC, argumento("candidato-json", ""), grade);
  if (rapido) Object.assign(TAM, RAPIDO);
  /* a grade (grade.ts): os tamanhos menores e as primeiras bases da calibracao, para escolher entre candidatos; a medida inteira confere */
  if (grade) {
    const t = JSON.parse(argumento("tam")) as Record<string, number>;
    for (const [k, x] of Object.entries(t)) { if (!(k in TAM) || !(Number.isInteger(x) && x >= 1)) throw new Error(`bancada: tamanho invalido ${k}=${x}`); TAM[k] = x; }
  }
  const nb = grade ? Number(argumento("bases")) : 0;
  if (grade && !(Number.isInteger(nb) && nb >= 1 && nb <= 5)) throw new Error(`bancada: --bases de 1 a 5, nao ${nb}`);
  const bases = rapido ? basesDa(faixa).slice(0, 1) : grade ? basesDa(faixa).slice(0, nb) : basesDa(faixa), t0 = Date.now(), commit = commitAtual();
  const dados = rodar(grupo, c, bases);
  const saida = { tarefa: "LUTA_POC, LP5", rapido, grade, grupo, fase, faixa, bases, commit, candidato: c, tamanhos: TAM, lutas: LUTAS, segundos: (Date.now() - t0) / 1000, dados, duracao: D };
  const dir = rapido || grade ? argumento("saida").replace(/[\\/]?$/, "/") : fileURLToPath(new URL(`../medicoes/equilibrio_poc/${fase}/${faixa}/`, import.meta.url));
  mkdirSync(dir, { recursive: true });
  writeFileSync(dir + `${grupo}.json`, JSON.stringify(saida) + "\n");
  console.log(`${grupo}: ${LUTAS} lutas em ${saida.segundos.toFixed(1)} s -> ${dir}${grupo}.json`);
}
export { taxa };
