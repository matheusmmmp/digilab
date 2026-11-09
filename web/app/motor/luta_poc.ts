/* A luta do pet no nucleo da POC (docs/TAREFA_V3_LUTA_POC.md, LP2): os numeros do lutador a partir dos 6 stats do pet (LP-3), os rivais da
   Arena e da Campanha e o mapa de cada lugar (LP-4). As seis decisoes da LP2 sao do Matheus ("Aprovo as 6", 2026-11-08); os numeros sao
   PROPOSTOS, SEM FONTE, ate a LP5. Sem rng: so contas sobre o estado. */
import { ERRO_MIRA_POC, FORMAS_ARENA, IDS_CENA, type IdCena, type Stats as StatsArena } from "./arena/index.ts";
import { NPC, type Lugar } from "./bots.ts";
import { caraterCanonico, multEstagio, statsDe } from "./catalogo.ts";
import { CTR, LINHA_DA_FORMA, STATS } from "./constantes.ts";
import { DIGIMON_DA_FORMA } from "./nomes.ts";
import type { Carater, Especie, Estagio, Forma, FormaAdultaNormal, Linha, Ramo, Stats } from "./tipos.ts";


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

/** os numeros da luta de 6 stats, no estagio e na condicao dados. Falha alto com stat que nao e positivo */
export function statsDaLuta(s: Stats, est: Estagio, condicao: number): StatsArena {
  for (const k of STATS) if (!(typeof s[k] === "number" && Number.isFinite(s[k]) && s[k] > 0)) throw new Error(`luta: o stat ${k} precisa ser positivo (${s[k]})`);
  if (!(condicao > 0)) throw new Error(`luta: condicao invalida (${condicao})`);
  const M = MAPA_STATS, r = (x: number) => x / M.neutro;
  return {
    hp: Math.max(1, Math.round(M.hp * r(s.vigor) * multEstagio(est) * condicao)),
    atk: M.atk * r(s.forca), def: M.def * r(s.guarda), vel: M.vel * r(s.folego),
    cad: M.cad / r(s.recuperacao), hcd: M.hcd / r(s.recuperacao),
    crit: M.crit * r(s.mira), erro: M.erro / r(s.mira),
    hpot: M.hpot, esquiva: M.esquiva, atordoa: M.atordoa,
  };
}

/** os 6 stats do pet na luta: os da especie, do carater e da forma (statsDe) mais o treino e os chips de stat (pontos), com o peso de
    combate de sempre (CTR.pesoPontoCombate, o ganho absoluto da campanha: treinar sobe a luta) */
export function statsDoPet(f: Forma, car: Partial<Carater> | null, pontos: Stats | null): Stats {
  const b = statsDe(f, car);
  return pontos ? Object.fromEntries(STATS.map(k => [k, b[k] + CTR.pesoPontoCombate * (pontos[k] || 0)])) as Stats : b;
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
export function statsRivalArena(chave: string): StatsArena {
  const f = formaDaChave(chave);
  return statsDaLuta(statsDe(f, f.adulta ? caraterCanonico(f.adulta as FormaAdultaNormal) : null), f.est, 1);
}

/** os numeros do NPC da Campanha: o perfilNPC (o total dividido igualmente pelos 6 stats) no estagio do lugar dele (LP2, decisao 3) */
export function statsNpc(k: string): StatsArena {
  const n = NPC[k];
  if (!n) throw new Error(`luta: ${k} nao e um NPC`);
  const v = n.total / STATS.length;
  return statsDaLuta(Object.fromEntries(STATS.map(s => [s, v])) as Stats, n.est, 1);
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
