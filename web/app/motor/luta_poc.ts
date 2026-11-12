/* A luta do pet no nucleo da POC (docs/TAREFA_V3_LUTA_POC.md, LP2): os numeros do lutador a partir dos 6 stats do pet (LP-3), os rivais da
   Arena e da Campanha e o mapa de cada lugar (LP-4). As seis decisoes da LP2 sao do Matheus ("Aprovo as 6", 2026-11-08); os numeros sao
   PROPOSTOS, SEM FONTE, ate a LP5. Sem rng: so contas sobre o estado. */
import { APOIO_LP6_3, ARENA_POR_ESTAGIO_LP6_3, ERRO_MIRA_POC, FORMAS_ARENA, IDS_CENA, type Apoio, type ArenaPorEstagio, type Esquiva, type IdCena, type Stats as StatsArena, type Tiro } from "./arena/index.ts";
import { NPC, type Lugar } from "./bots.ts";
import { caraterCanonico, multEstagio, statsDe } from "./catalogo.ts";
import { CTR, LINHA_DA_FORMA, STATS, ehLutaLp6, ehLutaV23 } from "./constantes.ts";
import { DIGIMON_DA_FORMA } from "./nomes.ts";
import type { Carater, Especie, Estagio, Forma, FormaAdultaNormal, Linha, Ramo, Stat, Stats } from "./tipos.ts";


/** o mapeamento dos 6 stats do pet para os numeros da luta (LP-3; LP2, decisao 2): o pet neutro, com `neutro` em cada stat, recebe os
    STATS_PADRAO da POC, e cada numero escala na razao do stat (ou na razao inversa, no ciclo, na recarga e no erro de mira). A vida
    leva tambem o multiplicador do estagio e a condicao, como o hpMax do perfilDe. PROPOSTO, SEM FONTE (a POC: remaster/fonte/site/arena.html,
    STATS_PADRAO; o erro de mira, o da dificuldade "normal") */
export const MAPA_STATS = {
  neutro: 10,
  hp: 900,       // vigor
  atk: 100,      // forca
  def: 50,       // guarda
  vel: 70,       // folego (px/s)
  cad: 2000,     // recuperacao, inversa (ms)
  hcd: 8,        // recuperacao, inversa (s)
  crit: 10,      // mira (%)
  erro: ERRO_MIRA_POC.normal,   // mira, inversa (px)
  hpot: 2, esquiva: 0, atordoa: 0,   // iguais para todos (a POC)
} as const;

/* ---------------------------------------------------------------- a tabela da luta de cada versao (LUTA_POC, LP5-5; D-LP5-7) */
/** os numeros da luta que mudam por versao de pet: o nucleo e o mesmo, e so o mapeamento, os NPCs e os rivais mudam (D-LP5-7) */
export interface TabelaLuta {
  versao: number;
  /** o lutador neutro (o MAPA_STATS da v21) */
  mapa: { readonly [K in keyof typeof MAPA_STATS]: number };
  /** o expoente de cada stat na razao ((s / neutro)^gama); null = 1 em todos, a linha reta da v21 (D-LP5-4) */
  gama: Readonly<Record<Stat, number>> | null;
  /** o peso de um ponto de treino (e de chip) na luta */
  pesoPonto: number;
  /** o multiplicador da vida e do ataque por estagio; null = o multEstagio do catalogo na vida e 1 no ataque (a v21) */
  multVida: Readonly<Partial<Record<Estagio, number>>> | null;
  multAtk: Readonly<Partial<Record<Estagio, number>>> | null;
  /** o total dos NPCs que muda (os outros, o de bots.ts) */
  npcTotal: Readonly<Record<string, number>>;
  /** o fator nos 6 stats dos rivais de cada torneio do pet (a Liga, a Torre e o Salao; D-LP5-20). A Fabrica e do Tamer e nao muda */
  fatorRival: Readonly<{ liga: number; torre: number; salao: number }>;
  /** a distancia do tiro e a esquiva do nucleo (D-LP5-12 e D-LP5-14); null = a luta da POC */
  tiro: Readonly<Tiro> | null;
  esquiva: Readonly<Esquiva & { gamaMira: number; gamaFolego: number; kAtento: number }> | null;
  /** o golpe de apoio e a arena maior por estagio do nucleo (LP6); ausentes = sem eles (a v21 a v27) */
  apoio?: Readonly<Apoio>;
  arenaPorEstagio?: Readonly<ArenaPorEstagio>;
}
/** a luta da v21 e da v22: a de sempre */
export const LUTA_V21: TabelaLuta = Object.freeze({
  versao: 21, mapa: MAPA_STATS, gama: null, pesoPonto: CTR.pesoPontoCombate, multVida: null, multAtk: null, npcTotal: {},
  fatorRival: { liga: 1, torre: 1, salao: 1 }, tiro: null, esquiva: null,
});
/** a luta da v23: o candidato lp5_3 da rodada de equilibrio (docs/PLANO_EQUILIBRIO_LUTA_POC.md; a calibracao, D-LP5-15 a D-LP5-21; a
    conferencia do PR #798; o "Sim, liga" do Matheus, 2026-11-11). Os numeros sao os do lp5_3 (scripts/equilibrio_poc/candidatos.ts), e o
    teste test/equilibrio_poc_bancada.test.ts confere que a bancada e o Motor v23 dao os mesmos. PROPOSTOS, SEM FONTE */
export const LUTA_V23: TabelaLuta = Object.freeze({
  versao: 23,
  mapa: { ...MAPA_STATS, hp: 1300, vel: 60 },
  gama: { vigor: .02, folego: .14, recuperacao: .02, forca: .02, mira: .14, guarda: .06 },
  pesoPonto: 15,
  /* o In-Training nao luta no jogo (so na luta montada do Lab): fica com o da v21 (0,4 e 1), como o Rookie, que a rodada deixou no da v21 */
  multVida: { bebe: .4, crianca: .6, adolescente: .9, adulto: 1.35, mega: 2.025 },
  multAtk: { bebe: 1, crianca: 1, adolescente: 1.5, adulto: 2.25, mega: 3.375 },
  /* o Gazimon em 0,8 vez o total de hoje (D-LP5-17) */
  npcTotal: { npc_tier1_brutamontes: 76.8 },
  /* o Salao em 0,8 (D-LP5-20); a Liga e a Torre em 1 */
  fatorRival: { liga: 1, torre: 1, salao: .8 },
  tiro: { distMin: 110, esperaMax: 1500, recuaAbaixo: .75, recuo: 1.5, recuaNaPrep: 2, danoProj: .7, velProj: 1 },
  esquiva: { kChance: 1, kReacao: 1, kDash: 1, chanceMax: .95, pertoChance: 0, pertoReacao: 200, contraMs: 0, gamaMira: .6, gamaFolego: .6, kAtento: .5 },
});
/** a luta da v28: a da v23 com o segundo golpe e a arena por estagio da LP6 (docs/PLANO_LP6_SEGUNDO_GOLPE.md; o lp6_3_u120 da LP6-3, PR
    #834: o apoio so no Ultimate e no Mega, sem o recuo, e a elipse 1,2/1,4; as capturas da LP6-4 aprovadas, "Aprovo, segue", Matheus,
    2026-11-11). Os numeros sao os do lp6_3_u120 (scripts/equilibrio_poc/candidatos.ts). PROPOSTOS, SEM FONTE */
export const LUTA_V28: TabelaLuta = Object.freeze({ ...LUTA_V23, versao: 28, apoio: APOIO_LP6_3, arenaPorEstagio: ARENA_POR_ESTAGIO_LP6_3 });
/** a tabela da luta de uma versao de pet: a v28 tem a dela (a da v23 com a LP6), a v23 a v27 a da v23; as outras (a v21 e a v22), a de sempre */
export const tabelaLuta = (versao: number): TabelaLuta => ehLutaLp6(versao) ? LUTA_V28 : ehLutaV23(versao) ? LUTA_V23 : LUTA_V21;
/** a esquiva da tabela na entrada do nucleo (so os numeros do nucleo); null sem esquiva */
export const esquivaDaTabela = (T: TabelaLuta): Esquiva | null => {
  if (!T.esquiva) return null;
  const { kChance, kReacao, kDash, chanceMax, pertoChance, pertoReacao, contraMs } = T.esquiva;
  return { kChance, kReacao, kDash, chanceMax, pertoChance, pertoReacao, contraMs };
};

/** os numeros da luta de 6 stats, no estagio e na condicao dados, pela tabela da versao (sem ela, a v21). `atento` e o eixo do carater, so
    na perspicacia da esquiva. Falha alto com stat que nao e positivo */
export function statsDaLuta(s: Stats, est: Estagio, condicao: number, T: TabelaLuta = LUTA_V21, atento = 0): StatsArena {
  for (const k of STATS) if (!(typeof s[k] === "number" && Number.isFinite(s[k]) && s[k] > 0)) throw new Error(`luta: o stat ${k} precisa ser positivo (${s[k]})`);
  if (!(condicao > 0)) throw new Error(`luta: condicao invalida (${condicao})`);
  const M = T.mapa, G = T.gama, r = (k: Stat) => !G || G[k] === 1 ? s[k] / M.neutro : (s[k] / M.neutro) ** G[k];
  const mv = T.multVida ? T.multVida[est] : multEstagio(est), ma = T.multAtk ? T.multAtk[est] : 1;
  if (mv === undefined || ma === undefined) throw new Error(`luta: a tabela da v${T.versao} nao tem o estagio ${est}`);
  const E = T.esquiva;
  return {
    hp: Math.max(1, Math.round(M.hp * r("vigor") * mv * condicao)),
    atk: M.atk * r("forca") * ma, def: M.def * r("guarda"), vel: M.vel * r("folego"),
    cad: M.cad / r("recuperacao"), hcd: M.hcd / r("recuperacao"),
    crit: M.crit * r("mira"), erro: M.erro / r("mira"),
    hpot: M.hpot, esquiva: M.esquiva, atordoa: M.atordoa,
    /* a perspicacia (a mira e o carater atento) e a agilidade (o folego), so com a esquiva da tabela (D-LP5-14) */
    ...(E ? { perc: Math.max(.1, (s.mira / M.neutro) ** E.gamaMira * (1 + E.kAtento * atento)), agil: (s.folego / M.neutro) ** E.gamaFolego } : {}),
  };
}

/** os 6 stats do pet na luta: os da especie, do carater e da forma (statsDe) mais o treino e os chips de stat (pontos), com o peso de
    combate de sempre (CTR.pesoPontoCombate, o ganho absoluto da campanha: treinar sobe a luta) */
export function statsDoPet(f: Forma, car: Partial<Carater> | null, pontos: Stats | null, T: TabelaLuta = LUTA_V21): Stats {
  const b = statsDe(f, car);
  return pontos ? Object.fromEntries(STATS.map(k => [k, b[k] + T.pesoPonto * (pontos[k] || 0)])) as Stats : b;
}

/** o nivel do Digimon de cada estagio do pet (o rotulo da tabela) */
export const NIVEL_DO_ESTAGIO: Readonly<Record<Estagio, string>> = { bebe: "In-Training", crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };

/** a forma (o objeto) de uma chave da tabela (chaveSprite): o inverso do chaveSprite. O adulto com o Digimon do Mega e o estagio "mega" */
export function formaDaChave(chave: string): Forma {
  if (!DIGIMON_DA_FORMA[chave]) throw new Error(`luta: ${chave} nao e uma forma do jogo`);
  const [esp, est, x] = chave.split("_") as [Especie, string, string | undefined];
  if (est === "bebe") return { esp, est: "bebe" };
  if (est === "crianca") return { esp, est: "crianca", ramo: x as Ramo };
  if (est === "adolescente") return { esp, est: "adolescente", linha: x as Linha };
  const adulta = x as FormaAdultaNormal, mega = DIGIMON_DA_FORMA[chave][1] === "Mega";
  return { esp, est: mega ? "mega" : "adulto", linha: LINHA_DA_FORMA[adulta], adulta };
}

/** os rivais da Arena para um estagio: as formas do jogo do mesmo nivel (LP2, decisao 4), na ordem da tabela */
export function rivaisArena(est: Estagio): string[] {
  return Object.keys(DIGIMON_DA_FORMA).filter(k => DIGIMON_DA_FORMA[k][1] === NIVEL_DO_ESTAGIO[est]);
}

/** os numeros do rival da Arena: o perfil canonico da forma (o carater canonico nos adultos, nenhum antes), sem treino, condicao 1 */
export function statsRivalArena(chave: string, T: TabelaLuta = LUTA_V21): StatsArena {
  const f = formaDaChave(chave), car = f.adulta ? caraterCanonico(f.adulta as FormaAdultaNormal) : null;
  return statsDaLuta(statsDe(f, car), f.est, 1, T, car?.atento ?? 0);
}

/** os numeros do NPC da Campanha: o perfilNPC (o total dividido igualmente pelos 6 stats) no estagio do lugar dele (LP2, decisao 3) */
export function statsNpc(k: string, T: TabelaLuta = LUTA_V21): StatsArena {
  const n = NPC[k];
  if (!n) throw new Error(`luta: ${k} nao e um NPC`);
  const v = (T.npcTotal[k] ?? n.total) / STATS.length;
  return statsDaLuta(Object.fromEntries(STATS.map(s => [s, v])) as Stats, n.est, 1, T);
}

/** o mapa fixo de cada lugar da Campanha (LP-4), pelo nome do lugar */
export const MAPA_DO_LUGAR: Readonly<Record<string, IdCena>> = {
  "Campina": "campo", "Torre de pedra": "coliseu", "Floresta": "floresta", "Cidadela": "castelo", "Lago": "praia", "Montanha Espiral": "caverna",
};
export function mapaDoLugar(L: Lugar): IdCena {
  const m = MAPA_DO_LUGAR[L.nome];
  if (!m) throw new Error(`luta: o lugar ${L.nome} nao tem mapa`);
  return m;
}
export const ehMapa = (m: unknown): m is IdCena => typeof m === "string" && (IDS_CENA as readonly string[]).includes(m);
/** a chave e de um rival da tabela (uma forma ou um NPC)? */
export const naTabela = (k: string): boolean => k in FORMAS_ARENA;

/* ---------------------------------------------------------------- os torneios (LUTA_POC, LP2b; LP-5 revista) */
/** os numeros de um rival de torneio pela forma sorteada (o Mega da Liga, da Torre e da Fabrica; o rival do Salao): o perfil canonico dela
    (o carater canonico que o torneio de antes ja usava), sem treino, condicao 1, pelo mesmo mapeamento (LP2-2) */
export function statsRivalForma(f: Forma, car: Partial<Carater> | null, T: TabelaLuta = LUTA_V21, fator = 1): StatsArena {
  const s = statsDe(f, car);
  if (fator === 1) return statsDaLuta(s, f.est, 1, T, car?.atento ?? 0);
  if (!(Number.isFinite(fator) && fator > 0)) throw new Error(`luta: o fator do rival precisa ser positivo (${fator})`);
  /* o fator nos 6 stats do rival do torneio, antes do mapeamento (D-LP5-20) */
  return statsDaLuta(Object.fromEntries(STATS.map(k => [k, s[k] * fator])) as Stats, f.est, 1, T, car?.atento ?? 0);
}
/** os mapas dos torneios sem lugar na Campanha. PROPOSTOS pelo worker da LP2b, SEM FONTE (o Gerente pediu um mapa onde a LP-4 nao tem):
    a Torre de Batalha no Ringue D-1 Grand Prix (o ringue de torneio; a LP-4 deixou o Ringue para a Arena, e a Torre e uma sequencia de
    lutas de torneio), o Salao no Coliseu (o salao dos campeoes) e a Fabrica no Campo de treino (os alugados lutam sem regra de mapa). A
    Liga usa o mapa do lugar de cada lider (LP-4) */
export const MAPA_TORRE: IdCena = "ringue";
export const MAPA_SALAO: IdCena = "coliseu";
export const MAPA_FABRICA: IdCena = "campo";
