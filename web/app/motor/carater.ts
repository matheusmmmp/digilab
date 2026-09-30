/* Carater do pet, que decide a linha (adolescente) e a forma adulta.
   - pets v3: pelo desvio da politica (espelho de evolucao.carater, ConfigEvolucaoPesquisa): em estados-sonda
     fixos, com numeros aleatorios comuns, a distribuicao de acoes da politica aprendida menos a da MESMA
     politica recem-nascida (mesmo temperamento). Cada acao vai para o traco de combate (CA.mapa), cada eixo
     junta seus tracos, divide pela escala e corta em [-1, 1].
   - pets v1/v2: PROVISORIO, so na web, pelos tracos (afinidade - linha de base / escala). */
import { ACOES_PET, BASE_CARATER, CA, CAT, CCP, COMBATE, DESLOC_CARATER, EIXO_TRACO, LINHAS } from "./constantes.ts";
import { Bandit } from "./bandit.ts";
import { criarRng, hashSemente } from "./rng.ts";
import type { AcaoPet, Carater, FormaAdultaNormal, Linha, Observacao, Temperamento, TracoCombate } from "./tipos.ts";

export type QuandoCarater = "adolescente" | "adulto";

/** afinidades soma-zero dos tracos (espelho de arena.py) */
export function afinidades(tracos: Record<AcaoPet, number>): Record<TracoCombate, number> {
  const bruto = Object.fromEntries(COMBATE.map(c => [c, 0])) as Record<TracoCombate, number>;
  for (const a of ACOES_PET) bruto[CA.mapa[a]] += tracos[a];
  const med = Object.values(bruto).reduce((s, x) => s + x, 0) / COMBATE.length;
  for (const c of COMBATE) bruto[c] -= med;
  return bruto;
}

let SONDAS_CAR: Observacao[] | null = null;
function sondasCarater(): Observacao[] {
  if (SONDAS_CAR) return SONDAS_CAR;
  const r = criarRng(hashSemente("sonda", CCP.semente));
  SONDAS_CAR = Array.from({ length: CCP.nEstados }, () => {
    const v = [r.random(), r.random(), r.random(), r.random(), r.random(), r.int(6) / 5, r.random() < .3 ? 1 : 0, r.random()];
    return { v, tdc: r.int(481) };
  });
  return SONDAS_CAR;
}
function distAcoesSonda(pol: Bandit): Record<AcaoPet, number>[] {
  return sondasCarater().map((obs, k) => {
    const r = criarRng(hashSemente("dist", CCP.semente, k)), cont = Object.fromEntries(ACOES_PET.map(a => [a, 0])) as Record<AcaoPet, number>;
    for (let i = 0; i < CCP.amostras; i++) cont[pol.agir(obs, r)]++;
    return cont;
  });
}
export function caraterPolitica(m: { pol: Bandit; temp: Temperamento; versao: number }, quando: QuandoCarater | null): Carater {
  const guardada = m.pol.ultDecisao;               /* sondar nao pode mexer no motivo da ultima decisao */
  const dp = distAcoesSonda(m.pol);
  m.pol.ultDecisao = guardada;
  const db = distAcoesSonda(new Bandit(m.temp, m.versao));
  const porTraco = Object.fromEntries(COMBATE.map(c => [c, 0])) as Record<TracoCombate, number>;
  for (const a of ACOES_PET) {
    const desvio = dp.reduce((s, c, k) => s + (c[a] - db[k][a]) / CCP.amostras, 0) / dp.length;
    porTraco[CA.mapa[a]] += desvio;
  }
  return Object.fromEntries(Object.entries(EIXO_TRACO).map(([eixo, ts]) => {
    const bruto = ts.reduce((s, t) => s + porTraco[t], 0) / ts.length;
    const desloc = quando ? DESLOC_CARATER[quando][eixo as keyof Carater] : 0;
    return [eixo, Math.max(-1, Math.min(1, bruto / CCP.escala + desloc))];
  })) as Carater;
}
/** desvio medio da politica sobre o bandit recem-nascido, por acao do pet, na sonda do carater (os gostos da historia:
    espelho de digilab/historia.desvio_por_acao). Custa uma sonda (~0,15 s): so na hora da fala */
export function desvioPorAcao(m: { pol: Bandit; temp: Temperamento; versao: number }): [string, number][] {
  const guardada = m.pol.ultDecisao;
  const dp = distAcoesSonda(m.pol);
  m.pol.ultDecisao = guardada;
  const db = distAcoesSonda(new Bandit(m.temp, m.versao));
  return ACOES_PET.map(a => [a, dp.reduce((s, c, k) => s + (c[a] - db[k][a]) / CCP.amostras, 0) / dp.length]);
}
export function caraterDe(tracos: Record<AcaoPet, number>, quando: QuandoCarater): Carater {
  const af = afinidades(tracos), base = BASE_CARATER[quando];
  if (!base) throw new Error("sem linha de base para " + quando);
  return Object.fromEntries(Object.entries(EIXO_TRACO).map(([eixo, ts]) => {
    const d = ts.reduce((s, t) => s + af[t] - base[t], 0) / ts.length;
    return [eixo, Math.max(-1, Math.min(1, d / CAT.escalaCarater))];
  })) as Carater;
}
/* previsao na aba Evolucao: o carater pela politica custa ~0,15 s; recalcula a cada 2 h de jogo ou acao do dono */
let cacheCarPrev: { chave: string | null; car: Carater | null } = { chave: null, car: null };
export function caraterPrevisto(m: { pol: Bandit; temp: Temperamento; versao: number; semente: number; e: { tick: number }; nDono: number; evolucoes: unknown[]; tracos: Record<AcaoPet, number> }, quando: QuandoCarater): Carater {
  if (m.versao < 3) return caraterDe(m.tracos, quando);
  const chave = [m.semente, Math.floor(m.e.tick / 120), m.nDono, m.evolucoes.length, quando].join("|");
  if (cacheCarPrev.chave !== chave) cacheCarPrev = { chave, car: caraterPolitica(m, quando) };
  return cacheCarPrev.car!;
}
/** eixo dominante decide a linha (empate: ordem fixa); sinal do complementar decide a forma adulta */
export function linhaDoCarater(car: Carater): Linha { return LINHAS.reduce((m, l) => car[CAT.adolescente[l].eixo] > car[CAT.adolescente[m].eixo] ? l : m, LINHAS[0]); }
export function formaAdultaDe(linha: Linha, car: Carater): FormaAdultaNormal {
  const a = CAT.adulto[linha];
  return Object.entries(a.formas).find(([, f]) => (f!.sinal > 0) === (car[a.comp] >= 0))![0] as FormaAdultaNormal;
}
export function corDominante(tracos: Record<AcaoPet, number>): TracoCombate { const af = afinidades(tracos); return COMBATE.reduce((m, c) => af[c] > af[m] ? c : m, COMBATE[0]); }
