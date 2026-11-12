/* A luta inteira, sem tela (LP1): a entrada (o mapa, as duas formas, os stats de cada lado e a semente) da sempre o mesmo resultado, que
   e o que o replay da LP2 vai refazer. Os dois lados sao a IA da arena na dificuldade "normal" (a LP-3); a tela da LP3 assiste passo a
   passo com a mesma configuracao. */
import { ACAO, BORDA_RINGUE_FAIXA, FORCA_ATR_MAX, LIMITE_MS, PULO_MAX_FAIXA, OPCOES_PADRAO, ORDEM_ESTAGIOS, type Apoio, type ArenaPorEstagio, type Esquiva, type Tiro } from "./constantes.ts";
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
export interface EntradaLuta { cena: IdCena; a: { forma: string; stats: Stats; vida0?: number }; b: { forma: string; stats: Stats; vida0?: number }; semente: number; tiro?: Tiro; esquiva?: Esquiva;
  /** as chaves da LP6-1 (desligadas sem elas): o golpe de apoio e a elipse pelo estagio */
  apoio?: Apoio; arenaPorEstagio?: ArenaPorEstagio;
  /** as chaves da N3 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 4; D-N-5, "As 4 (Recommended)", Matheus, 2026-11-12),
      desligadas sem elas; nenhuma versao de pet as liga. `forcaAtr`: a vantagem do atributo (sem ela, o OPCOES_PADRAO.forca, 1,5) */
  forcaAtr?: number;
  /** `tiroDoMorto` ligado (true): o projetil de quem ja caiu some no ar, sem dano (a causa da maior parte dos empates, a N2) */
  tiroDoMorto?: true;
  /** `puloMax`: o teto (px) do pulo da esquiva; a velocidade do pulo fica ate puloMax / a duracao dele (sem ela, o pulo sem teto) */
  puloMax?: number;
  /** `bordaRingue`: no Ringue, o recuo (tambem o da preparacao do tiro) e o pulo da esquiva param nesta fracao do raio da elipse; o empurrao
      e a investida nao (sem ela, o recuo e o pulo nao olham a borda) */
  bordaRingue?: number }

/** a configuracao da luta 1 contra 1: os dois pela IA, com a dificuldade, o atributo e os projeteis do padrao da POC */
export function configLuta(e: EntradaLuta, tabela: TabelaFormas = FORMAS_ARENA): ConfigLuta {
  return { cena: e.cena, dific: OPCOES_PADRAO.dific, forca: e.forcaAtr !== undefined ? conferirForcaAtr(e.forcaAtr) : OPCOES_PADRAO.forca, pvel: OPCOES_PADRAO.pvel,
    a: { forma: formaArena(e.a.forma, tabela), stats: e.a.stats, ...(e.a.vida0 !== undefined ? { vida0: e.a.vida0 } : {}) },
    b: { forma: formaArena(e.b.forma, tabela), stats: e.b.stats, ...(e.b.vida0 !== undefined ? { vida0: e.b.vida0 } : {}) },
    ...(e.tiro ? { tiro: conferirTiro(e.tiro) } : {}), ...(e.esquiva ? { esquiva: conferirEsquiva(e.esquiva) } : {}),
    ...(e.apoio ? { apoio: conferirApoio(e.apoio) } : {}), ...(e.arenaPorEstagio ? { arenaPorEstagio: conferirArenaPorEstagio(e.arenaPorEstagio) } : {}),
    ...(e.tiroDoMorto !== undefined ? { tiroDoMorto: conferirLigada(e.tiroDoMorto, "tiroDoMorto") } : {}),
    ...(e.puloMax !== undefined ? { puloMax: conferirPuloMax(e.puloMax) } : {}),
    ...(e.bordaRingue !== undefined ? { bordaRingue: conferirBordaRingue(e.bordaRingue) } : {}) };
}
const numOk = (v: unknown, min: number, max: number) => typeof v === "number" && Number.isFinite(v) && v >= min && v <= max;
/** uma chave ligada da N3: so true (desligada = sem o campo, para a configuracao sair igual a de antes), senao falha alto */
function conferirLigada(x: unknown, nome: string): true {
  if (x !== true) throw new Error(`arena: a chave ${nome} so vale ligada (true) ou fora da entrada (${JSON.stringify(x)})`);
  return true;
}
/** o teto do pulo da entrada (N3, a chave puloMax): finito, de PULO_MAX_FAIXA[0] a PULO_MAX_FAIXA[1] px, senao falha alto */
export function conferirPuloMax(x: number): number {
  if (!numOk(x, PULO_MAX_FAIXA[0], PULO_MAX_FAIXA[1])) throw new Error(`arena: teto do pulo invalido ${JSON.stringify(x)}`);
  return x;
}
/** o limite da borda do Ringue da entrada (N3, a chave bordaRingue): finito, de BORDA_RINGUE_FAIXA[0] a [1] do raio, senao falha alto */
export function conferirBordaRingue(x: number): number {
  if (!numOk(x, BORDA_RINGUE_FAIXA[0], BORDA_RINGUE_FAIXA[1])) throw new Error(`arena: limite da borda do Ringue invalido ${JSON.stringify(x)}`);
  return x;
}
/** a vantagem do atributo da entrada (N3, a chave forcaAtr): finita, de 1 (sem vantagem) a FORCA_ATR_MAX, senao falha alto */
export function conferirForcaAtr(x: number): number {
  if (!numOk(x, 1, FORCA_ATR_MAX)) throw new Error(`arena: vantagem do atributo invalida ${JSON.stringify(x)}`);
  return x;
}
/** o golpe de apoio da entrada (LP6-1): cada numero finito e na faixa, senao falha alto */
export function conferirApoio(x: Apoio): Apoio {
  if (!numOk(x.dano, 0.05, 2) || !numOk(x.recarga, 0.25, 10) || !numOk(x.longeMs, 0, 10_000)) throw new Error(`arena: golpe de apoio invalido ${JSON.stringify(x)}`);
  if (x.desde !== undefined && !(ORDEM_ESTAGIOS as readonly string[]).includes(x.desde)) throw new Error(`arena: estagio do apoio invalido ${JSON.stringify(x.desde)}`);
  if (x.recua !== undefined && typeof x.recua !== "boolean") throw new Error(`arena: recua do apoio invalido ${JSON.stringify(x.recua)}`);
  return { dano: x.dano, recarga: x.recarga, longeMs: x.longeMs, ...(x.desde !== undefined ? { desde: x.desde } : {}), ...(x.recua !== undefined ? { recua: x.recua } : {}) };
}
/** a elipse pelo estagio da entrada (LP6-1): fatores finitos, de 1 a 2, e o do Mega pelo menos o do Ultimate, senao falha alto */
export function conferirArenaPorEstagio(x: ArenaPorEstagio): ArenaPorEstagio {
  if (!numOk(x.Ultimate, 1, 2) || !numOk(x.Mega, 1, 2) || x.Mega < x.Ultimate) throw new Error(`arena: elipse por estagio invalida ${JSON.stringify(x)}`);
  return { Ultimate: x.Ultimate, Mega: x.Mega };
}
/** a esquiva da entrada (D-LP5-14): cada numero finito e na faixa, senao falha alto */
export function conferirEsquiva(x: Esquiva): Esquiva {
  const ok = (v: unknown, min: number, max: number) => typeof v === "number" && Number.isFinite(v) && v >= min && v <= max;
  if (!ok(x.kChance, 0, 4) || !ok(x.kReacao, 0, 4) || !ok(x.kDash, 0, 4) || !ok(x.chanceMax, 0, 1) || !ok(x.pertoChance, 0, 1) || !ok(x.pertoReacao, 0, 2000) || !ok(x.contraMs, 0, 5000))
    throw new Error(`arena: esquiva invalida ${JSON.stringify(x)}`);
  return { kChance: x.kChance, kReacao: x.kReacao, kDash: x.kDash, chanceMax: x.chanceMax, pertoChance: x.pertoChance, pertoReacao: x.pertoReacao, contraMs: x.contraMs };
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
