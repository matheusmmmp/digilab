/* A luta inteira, sem tela (LP1): a entrada (o mapa, as duas formas, os stats de cada lado e a semente) da sempre o mesmo resultado, que
   e o que o replay da LP2 vai refazer. Os dois lados sao a IA da arena na dificuldade "normal" (a LP-3); a tela da LP3 assiste passo a
   passo com a mesma configuracao. */
import { ACAO, LIMITE_MS, OPCOES_PADRAO, type Tiro } from "./constantes.ts";
import { FORMAS_ARENA } from "./formas.ts";
import type { DadosForma } from "./tipos.ts";
import { sorteiosPorFluxo } from "./rng.ts";
import { criarLuta, passo } from "./sim.ts";
import type { ConfigLuta, Evento, IdCena, Lado, Luta, Sorteios, Stats } from "./tipos.ts";

/** uma tabela de formas: a do jogo (FORMAS_ARENA, com o projetil da LP-8) ou a da POC (FORMAS_ARENA_POC, so a fidelidade da LP1) */
export type TabelaFormas = Readonly<Record<string, DadosForma>>;

/** a forma do jogo (chaveSprite, como "cirro_crianca_arisco") na tabela do git; forma fora da tabela levanta erro */
export function formaArena(chave: string, tabela: TabelaFormas = FORMAS_ARENA) {
  const f = tabela[chave];
  if (!f) throw new Error(`arena: a forma ${chave} nao esta na tabela (motor/arena/formas.ts)`);
  return f;
}

/** a entrada de uma luta; `vida0`: a vida com que o lado entra numa serie sem cura (sem ela, cheia) */
export interface EntradaLuta { cena: IdCena; a: { forma: string; stats: Stats; vida0?: number }; b: { forma: string; stats: Stats; vida0?: number }; semente: number; tiro?: Tiro }

/** a configuracao da luta 1 contra 1: os dois pela IA, com a dificuldade, o atributo e os projeteis do padrao da POC */
export function configLuta(e: EntradaLuta, tabela: TabelaFormas = FORMAS_ARENA): ConfigLuta {
  return { cena: e.cena, dific: OPCOES_PADRAO.dific, forca: OPCOES_PADRAO.forca, pvel: OPCOES_PADRAO.pvel,
    a: { forma: formaArena(e.a.forma, tabela), stats: e.a.stats, ...(e.a.vida0 !== undefined ? { vida0: e.a.vida0 } : {}) },
    b: { forma: formaArena(e.b.forma, tabela), stats: e.b.stats, ...(e.b.vida0 !== undefined ? { vida0: e.b.vida0 } : {}) },
    ...(e.tiro ? { tiro: conferirTiro(e.tiro) } : {}) };
}
/** a distancia do tiro da entrada (D-LP5-12): cada numero finito e na faixa, senao falha alto */
export function conferirTiro(t: Tiro): Tiro {
  const ok = (x: unknown, min: number, max: number) => typeof x === "number" && Number.isFinite(x) && x >= min && x <= max;
  if (!ok(t.distMin, 0, ACAO.alcanceDist) || !ok(t.esperaMax, 0, 10_000) || !ok(t.recuaAbaixo, 0, 1) || !ok(t.recuo, 0.1, 3) || !ok(t.recuaNaPrep, 0, 3)
    || !ok(t.danoProj, 0.2, 2) || !ok(t.velProj, 0.3, 3))
    throw new Error(`arena: distancia do tiro invalida ${JSON.stringify(t)}`);
  return { distMin: t.distMin, esperaMax: t.esperaMax, recuaAbaixo: t.recuaAbaixo, recuo: t.recuo, recuaNaPrep: t.recuaNaPrep, danoProj: t.danoProj, velProj: t.velProj };
}

export interface ResultadoLuta {
  vencedor: Lado | null;   // null: empate, ou chegou ao limite sem fim
  fim: boolean; relogio: number; passos: number;
  vidaA: number; vidaB: number;   // a vida que sobrou
  danoA: number; danoB: number;   // o dano de golpe que cada lado causou
}

/** roda uma luta montada ate o fim ou o limite; `aoPasso` recebe os eventos de cada passo (a medicao e os testes) */
export function rodarAteOFim(L: Luta, aoPasso?: (ev: Evento[], L: Luta) => void): ResultadoLuta {
  let passos = 0;
  if (aoPasso) { aoPasso(L.eventos, L); L.eventos = []; }
  while (!L.fim && L.relogio < LIMITE_MS) { const ev = passo(L); passos++; aoPasso?.(ev, L); }
  return { vencedor: L.vencedor, fim: L.fim, relogio: L.relogio, passos, vidaA: L.a.hp, vidaB: L.b.hp, danoA: L.a.dano, danoB: L.b.dano };
}

/** a luta inteira do jogo: um fluxo de sorteio por uso, semeado pela semente da luta (a tabela da POC so na fidelidade da LP1) */
export function lutar(e: EntradaLuta, r: Sorteios = sorteiosPorFluxo(e.semente), tabela: TabelaFormas = FORMAS_ARENA): ResultadoLuta {
  return rodarAteOFim(criarLuta(configLuta(e, tabela), r));
}
