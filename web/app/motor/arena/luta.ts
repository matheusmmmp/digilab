/* A luta inteira, sem tela (LP1): a entrada (o mapa, as duas formas, os stats de cada lado e a semente) da sempre o mesmo resultado, que
   e o que o replay da LP2 vai refazer. Os dois lados sao a IA da arena na dificuldade "normal" (a LP-3); a tela da LP3 assiste passo a
   passo com a mesma configuracao. */
import { LIMITE_MS, OPCOES_PADRAO } from "./constantes.ts";
import { FORMAS_ARENA } from "./formas.ts";
import { sorteiosPorFluxo } from "./rng.ts";
import { criarLuta, passo } from "./sim.ts";
import type { ConfigLuta, Evento, IdCena, Lado, Luta, Sorteios, Stats } from "./tipos.ts";

/** a forma do jogo (chaveSprite, como "cirro_crianca_arisco") na tabela do git; forma fora da tabela levanta erro */
export function formaArena(chave: string) {
  const f = FORMAS_ARENA[chave];
  if (!f) throw new Error(`arena: a forma ${chave} nao esta na tabela (motor/arena/formas.ts)`);
  return f;
}

export interface EntradaLuta { cena: IdCena; a: { forma: string; stats: Stats }; b: { forma: string; stats: Stats }; semente: number }

/** a configuracao da luta 1 contra 1: os dois pela IA, com a dificuldade, o atributo e os projeteis do padrao da POC */
export function configLuta(e: EntradaLuta): ConfigLuta {
  return { cena: e.cena, dific: OPCOES_PADRAO.dific, forca: OPCOES_PADRAO.forca, pvel: OPCOES_PADRAO.pvel,
    a: { forma: formaArena(e.a.forma), stats: e.a.stats }, b: { forma: formaArena(e.b.forma), stats: e.b.stats } };
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

/** a luta inteira do jogo: um fluxo de sorteio por uso, semeado pela semente da luta */
export function lutar(e: EntradaLuta, r: Sorteios = sorteiosPorFluxo(e.semente)): ResultadoLuta {
  return rodarAteOFim(criarLuta(configLuta(e), r));
}
