/* Carater do pet, que decide a linha (adolescente) e a forma adulta. Pelo cerebro A (pets v11 em diante; PW-4 opcao (b)): o mesmo metodo do Python, com paridade (test/carater_v11.test.ts contra
     test/gabaritos/carater_v11_python.json): as sondas de metrics.estados_sonda com os receptores do corpo (a rng `sonda-corpo`, como a
     bancada), as distribuicoes de metrics.distribuicoes_de_acao (o Mersenne Twister do CPython), o cerebro recem-nascido como base, e a
     escala e o deslocamento proprios (CCP_V11, DESLOC_CARATER_V11).
   O carater pelo desvio do Bandit (pets v3-v10) e pelos tracos (v1-v2) saiu com o descarte 6 (COMBATE-TR, etapa R2b; D-9). */
import { ACOES_PET, CA, CAT, CCP, CCP_V11, COMBATE, DESLOC_CARATER_V11, EIXO_TRACO, LINHAS } from "./constantes.ts";
import { CCO_CORPO_V11 } from "./corpo.ts";
import { arred, receptoresNovos, type CerebroA, type ObservacaoLobos } from "./lobos.ts";
import { RandomPy, derivarSemente, divArred } from "./mundo.ts";
import { bracoV11 } from "./pet_v11.ts";
import type { AcaoPet, Carater, FormaAdultaNormal, Linha, TracoCombate } from "./tipos.ts";

export type QuandoCarater = "adolescente" | "adulto";

/** afinidades soma-zero dos tracos (espelho de arena.py) */
export function afinidades(tracos: Record<AcaoPet, number>): Record<TracoCombate, number> {
  const bruto = Object.fromEntries(COMBATE.map(c => [c, 0])) as Record<TracoCombate, number>;
  for (const a of ACOES_PET) bruto[CA.mapa[a]] += tracos[a];
  const med = Object.values(bruto).reduce((s, x) => s + x, 0) / COMBATE.length;
  for (const c of COMBATE) bruto[c] -= med;
  return bruto;
}

/* previsao na aba Evolucao: o carater pelo cerebro custa uma sonda; recalcula a cada 2 h de jogo ou acao do dono */
let cacheCarPrev: { chave: string | null; car: Carater | null } = { chave: null, car: null };
export function caraterPrevisto(m: { semente: number; e: { tick: number }; nDono: number; evolucoes: unknown[]; cerebro: CerebroA | null }, quando: QuandoCarater): Carater {
  const chave = [m.semente, Math.floor(m.e.tick / 120), m.nDono, m.evolucoes.length, quando].join("|");
  if (cacheCarPrev.chave !== chave) cacheCarPrev = { chave, car: caraterV11(m.cerebro!, quando) };
  return cacheCarPrev.car!;
}
/** eixo dominante decide a linha (empate: ordem fixa); sinal do complementar decide a forma adulta */
export function linhaDoCarater(car: Carater): Linha { return LINHAS.reduce((m, l) => car[CAT.adolescente[l].eixo] > car[CAT.adolescente[m].eixo] ? l : m, LINHAS[0]); }
export function formaAdultaDe(linha: Linha, car: Carater): FormaAdultaNormal {
  const a = CAT.adulto[linha];
  return Object.entries(a.formas).find(([, f]) => (f!.sinal > 0) === (car[a.comp] >= 0))![0] as FormaAdultaNormal;
}
export function corDominante(tracos: Record<AcaoPet, number>): TracoCombate { const af = afinidades(tracos); return COMBATE.reduce((m, c) => af[c] > af[m] ? c : m, COMBATE[0]); }

/* ---------------------------------------------------------------- pets v11 */
/** metrics.estados_sonda(CCP.nEstados, CCP.semente) com os receptores do corpo do v11 (bancada.percepcao_da_sonda, a rng
    derivar_semente("sonda-corpo", semente), um sorteio por receptor novo, na ordem deles, sonda a sonda) */
let SONDAS_V11: ObservacaoLobos[] | null = null;
export function sondasCaraterV11(): ObservacaoLobos[] {
  if (SONDAS_V11) return SONDAS_V11;
  const r = new RandomPy(derivarSemente("sonda", CCP.semente));
  const estados = Array.from({ length: CCP.nEstados }, () => {
    const v = [r.random(), r.random(), r.random(), r.random(), r.random(), r.randrange(6) / 5, r.random() < .3 ? 1 : 0, r.random()];
    return { v, tdc: r.randrange(0, 481) };
  });
  const cc = CCO_CORPO_V11, C = cc.escala, S = cc.escala_receptor, novos = receptoresNovos(cc);
  const rc = new RandomPy(derivarSemente("sonda-corpo", CCP.semente));
  SONDAS_V11 = estados.map(o => {
    const corpo: Record<string, number> = {};
    ["fome", "higiene", "energia", "humor", "saude"].forEach((nome, i) => { corpo[nome] = S - divArred(arred((1 - o.v[i]) * C) * S, C); });
    for (const n of novos) corpo[n] = rc.randrange(S + 1);
    return { ...o, corpo };
  });
  return SONDAS_V11;
}
/** metrics.distribuicoes_de_acao: a frequencia de cada acao em cada sonda, com a rng derivar_semente("dist", semente, k) (numeros
    aleatorios comuns). O cerebro sorteia pelo `amostrar`, que nao mexe nele */
export function distCerebroV11(cerebro: CerebroA): Record<AcaoPet, number>[] {
  return sondasCaraterV11().map((obs, k) => {
    const r = new RandomPy(derivarSemente("dist", CCP.semente, k)), cont = Object.fromEntries(ACOES_PET.map(a => [a, 0])) as Record<AcaoPet, number>;
    for (let i = 0; i < CCP.amostras; i++) cont[cerebro.amostrar(obs, r)]++;
    return Object.fromEntries(ACOES_PET.map(a => [a, cont[a] / CCP.amostras])) as Record<AcaoPet, number>;
  });
}
let DIST_BASE_V11: Record<AcaoPet, number>[] | null = null;
/** a distribuicao do cerebro recem-nascido (o instinto), a base do desvio */
export function distBaseV11(): Record<AcaoPet, number>[] { return DIST_BASE_V11 ??= distCerebroV11(bracoV11().cerebro); }
/** sum() do CPython 3.12 em diante sobre floats, a partir do 0: a soma compensada de Neumaier (bltinmodule.c, builtin_sum_impl), com a
    compensacao somada no fim so se for nao nula e finita. O Python 3.10 e o 3.11 somam sem compensacao (o exportador do gabarito
    recusa os dois) */
export function somaPy(xs: readonly number[]): number {
  let f = 0, c = 0;
  for (const x of xs) {
    const t = f + x;
    c += Math.abs(f) >= Math.abs(x) ? (f - t) + x : (x - t) + f;
    f = t;
  }
  return c !== 0 && Number.isFinite(c) ? f + c : f;
}
/** o desvio bruto por eixo (a conta de experiments/medir_carater_v11.carater, na mesma ordem de soma): por acao, a media do desvio de
    frequencia sobre as sondas, somada no traco dela; por eixo, a media dos tracos */
export function brutoV11(cerebro: CerebroA): Carater {
  const dp = distCerebroV11(cerebro), db = distBaseV11(), porTraco: Partial<Record<TracoCombate, number>> = {};
  for (const a of ACOES_PET) {
    const s = somaPy(dp.map((p, k) => p[a] - db[k][a]));
    porTraco[CA.mapa[a]] = (porTraco[CA.mapa[a]] ?? 0) + s / dp.length;
  }
  return Object.fromEntries(Object.entries(EIXO_TRACO).map(([eixo, ts]) => [eixo, somaPy(ts.map(tr => porTraco[tr]!)) / ts.length])) as Carater;
}
/** o carater do pet v11: o bruto / CCP_V11.escala, mais o DESLOC_CARATER_V11 do estagio, cortado em [-1, 1] */
export function caraterV11(cerebro: CerebroA, quando: QuandoCarater): Carater {
  const bruto = brutoV11(cerebro), d = DESLOC_CARATER_V11[quando];
  return Object.fromEntries(Object.entries(bruto).map(([e, v]) => [e, Math.max(-1, Math.min(1, v / CCP_V11.escala + d[e as keyof Carater]))])) as Carater;
}
