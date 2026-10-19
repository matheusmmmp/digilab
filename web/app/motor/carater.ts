/* Carater do pet, que decide a linha (adolescente) e a forma adulta.
   - pets v3: pelo desvio da politica (espelho de evolucao.carater, ConfigEvolucaoPesquisa): em estados-sonda
     fixos, com numeros aleatorios comuns, a distribuicao de acoes da politica aprendida menos a da MESMA
     politica recem-nascida (mesmo temperamento). Cada acao vai para o traco de combate (CA.mapa), cada eixo
     junta seus tracos, divide pela escala e corta em [-1, 1].
   - pets v1/v2: PROVISORIO, so na web, pelos tracos (afinidade - linha de base / escala).
   - pets v11 (o cerebro A; PW-4 opcao (b)): o mesmo metodo do Python, com paridade (test/carater_v11.test.ts contra
     test/gabaritos/carater_v11_python.json): as sondas de metrics.estados_sonda com os receptores do corpo (a rng `sonda-corpo`, como a
     bancada), as distribuicoes de metrics.distribuicoes_de_acao (o Mersenne Twister do CPython), o cerebro recem-nascido como base, e a
     escala e o deslocamento proprios (CCP_V11, DESLOC_CARATER_V11). */
import { ACOES_PET, BASE_CARATER, CA, CAT, CCP, CCP_V11, COMBATE, DESLOC_CARATER, DESLOC_CARATER_V11, EIXO_TRACO, LINHAS } from "./constantes.ts";
import { Bandit } from "./bandit.ts";
import { CCO_CORPO_V11 } from "./corpo.ts";
import { arred, receptoresNovos, type CerebroA, type ObservacaoLobos } from "./lobos.ts";
import { RandomPy, derivarSemente, divArred } from "./mundo.ts";
import { bracoV11 } from "./pet_v11.ts";
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
  if (m.versao >= 11) throw new Error("os gostos da historia pelo desvio do Bandit nao valem nos pets v11 (o cerebro e o A; a fala e a etapa 6)");
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
export function caraterPrevisto(m: { pol: Bandit; temp: Temperamento; versao: number; semente: number; e: { tick: number }; nDono: number; evolucoes: unknown[]; tracos: Record<AcaoPet, number>; cerebro: CerebroA | null }, quando: QuandoCarater): Carater {
  if (m.versao < 3) return caraterDe(m.tracos, quando);
  const chave = [m.semente, Math.floor(m.e.tick / 120), m.nDono, m.evolucoes.length, quando].join("|");
  /* v11: o carater do cerebro A (caraterV11) */
  if (cacheCarPrev.chave !== chave) cacheCarPrev = { chave, car: m.versao >= 11 ? caraterV11(m.cerebro!, quando) : caraterPolitica(m, quando) };
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
