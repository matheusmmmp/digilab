/* O cerebro A em TS (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 2): o nucleo de digilab/policies/lobos.py com o aprendizado
   desligado (L0). So o motor e a paridade; nenhuma tela e nenhuma versao de pet nova (o v11 e a etapa 4).

   Os quatro lobos, como no Python:
     PERCEPCAO        Observacao -> x = (1, Estado.vetor, min(1, ticks sem cuidado / escala)), os floats que o instinto le;
     MEMORIA/EMOCAO   contribuicao zero em toda decisao (os contadores do Python entram com o aprendizado, na etapa 3);
     IMPULSOS         as regras do instinto (policy.py, PoliticaInstinto.agir), rodadas com uma rng-sonda que nao consome a rng do
                      motor: a regra que disparou e os candidatos, na ordem do instinto;
     DECISAO          pesos INTEIROS w[regra][acao][entrada] na escala S = 2**bits, no prior do instinto (os coeficientes vezes S).
                      Peso efetivo = sum_j (w_j / S) * x_j, da esquerda para a direita; a acao sai de UMA chamada de rng.random(),
                      pela conta de random.choices(k=1) do CPython (cumulativa, total = ultima + 0.0, bisect_right ate n - 1).

   Com S potencia de dois, w_j / S e exato e o peso efetivo e o mesmo float que o instinto escreve, somado na mesma ordem: a decisao e
   a do instinto, byte a byte (o G-PAR-L0, test/lobos.test.ts contra a secao l0 de test/gabaritos/lobos_python.json). Nenhuma funcao
   transcendental (nada de Math.exp ou Math.log): o Chrome difere do Node so no ultimo bit delas, e o nucleo fica fora disso.

   O motivo de cada decisao usa os nomes em snake_case do Python de proposito: e o mesmo dado de `_registrar`, conferido campo a campo. */
import { C, CLB } from "./constantes.ts";
import { eNoite } from "./estado.ts";
import type { AcaoPet, Observacao } from "./tipos.ts";

// ================================================================== os nomes
/** as sete acoes de sempre, na ordem do enum do Python (ACOES_PET_HOJE): as linhas de cada regra na tabela de pesos */
export const ACOES_LOBOS: readonly AcaoPet[] = ["ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar"];
export const LOBOS = ["percepcao", "memoria_emocao", "impulsos", "decisao"] as const;
export type Lobo = (typeof LOBOS)[number];
/** as regras do instinto, na ordem em que ele as testa */
export const REGRAS_LOBOS = ["sono_exaustao", "sono_continuar", "sono_noite", "pedido_necessidade", "abandono", "fome_moderada",
  "tempo_livre"] as const;
export type RegraLobos = (typeof REGRAS_LOBOS)[number];
/** as entradas da percepcao: o vies, o Estado.vetor (ordem congelada em state.py) e o tempo sem cuidado */
export const ENTRADAS_LOBOS = ["vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora",
  "ticks_sem_cuidado"] as const;
export type EntradaLobos = (typeof ENTRADAS_LOBOS)[number];

/** o prior do instinto em unidades de 1.0 (vira inteiro vezes S): os literais de PoliticaInstinto.agir. So os candidatos de cada regra
 *  tem coeficiente; o resto da tabela e zero (lobos.PRIOR_INSTINTO; a igualdade com o instinto e o proprio G-PAR-L0) */
export const PRIOR_INSTINTO: Readonly<Record<RegraLobos, Partial<Record<AcaoPet, Partial<Record<EntradaLobos, number>>>>>> = {
  sono_exaustao: { dormir: { vies: 1 } },
  sono_continuar: { dormir: { vies: 1 } },
  sono_noite: { dormir: { vies: 1 } },
  pedido_necessidade: { chamar_atencao: { vies: 1 } },
  abandono: { emburrar: { vies: 1 }, chamar_atencao: { vies: 1 } },
  fome_moderada: { comer: { vies: 1 }, chamar_atencao: { vies: 1 } },
  tempo_livre: { ocioso: { vies: 3 }, explorar: { vies: 2, energia: 2 }, brincar: { vies: 1, humor: 3 }, chamar_atencao: { vies: 1 } },
};

// ================================================================== o instinto, com a regra
/** a rng que o instinto le: random() e um choices(k=1) ponderado, como o random.Random do Python */
export interface RngInstinto {
  random(): number;
  choices(populacao: readonly AcaoPet[], pesos: readonly number[]): AcaoPet;
}

/** PoliticaInstinto.agir (policy.py), linha a linha, devolvendo tambem a regra que decidiu (o ultima_regra do Python). E o mesmo
 *  instinto de distInstinto (bandit.ts), em forma de decisao: o teste confere os dois decisao a decisao */
export function agirInstinto(obs: Observacao, rng: RngInstinto): { acao: AcaoPet; regra: RegraLobos } {
  const [fome, higiene, energia, humor, , , dormindo, hora] = obs.v;
  if (energia < 0.25) return { acao: "dormir", regra: "sono_exaustao" };
  if (dormindo > 0.5 && energia < 0.85) return { acao: "dormir", regra: "sono_continuar" };
  if (eNoite(Math.floor(hora * 1440)) && energia < 0.55) return { acao: "dormir", regra: "sono_noite" };
  if (fome < 0.25 || higiene < 0.25) return { acao: "chamar_atencao", regra: "pedido_necessidade" };
  if (obs.tdc > C.janelaAtencao) return { acao: humor < 0.35 ? "emburrar" : "chamar_atencao", regra: "abandono" };
  if (fome < 0.45) return { acao: rng.random() < 0.5 ? "comer" : "chamar_atencao", regra: "fome_moderada" };
  const acoes: AcaoPet[] = ["ocioso", "explorar", "brincar", "chamar_atencao"];
  const pesos = [3.0, 2.0 + 2.0 * energia, 1.0 + 3.0 * humor, 1.0];
  return { acao: rng.choices(acoes, pesos), regra: "tempo_livre" };
}

/** a rng-sonda (lobos._RngSonda): devolve sempre o mesmo u em random(); em choices() guarda a populacao e devolve o primeiro.
 *  Um segundo choices() falha alto */
class RngSonda implements RngInstinto {
  chamadasRandom = 0;
  escolha: AcaoPet[] | null = null;
  private readonly u: number;
  constructor(u: number) { this.u = u; }
  random(): number { this.chamadasRandom += 1; return this.u; }
  choices(populacao: readonly AcaoPet[], pesos: readonly number[]): AcaoPet {
    if (this.escolha !== null || pesos.length !== populacao.length) throw new Error("sonda so suporta um unico choices(k=1) ponderado");
    this.escolha = [...populacao];
    return populacao[0];
  }
}

/** o lobo de impulsos: a regra do instinto que dispara nesta observacao e os candidatos, na ordem dele. Regra determinista: um
 *  candidato. Um `random() < t` (fome moderada): os dois lados, com u = 0 e u -> 1. Um choices(): a populacao */
export function impulsos(obs: Observacao): { regra: RegraLobos; candidatos: AcaoPet[] } {
  const sonda = new RngSonda(0.0);
  const { acao: a0, regra } = agirInstinto(obs, sonda);
  if (sonda.escolha !== null) {
    if (sonda.chamadasRandom) throw new Error("instinto usou random() e choices() na mesma decisao");
    return { regra, candidatos: sonda.escolha };
  }
  if (sonda.chamadasRandom === 0) return { regra, candidatos: [a0] };
  if (sonda.chamadasRandom > 1) throw new Error("instinto chamou random() mais de uma vez");
  const a1 = agirInstinto(obs, new RngSonda(1.0 - 1e-15)).acao;
  if (a1 === a0) throw new Error("instinto chamou random() sem que o resultado dependesse dele");
  return { regra, candidatos: [a0, a1] };
}

// ================================================================== percepcao, ativacao, sorteio
/** o lobo de percepcao: (1, Estado.vetor, min(1, ticks sem cuidado / escala)) */
export function percepcao(obs: Observacao, escalaTdc: number = CLB.escalaTdc): number[] {
  const x = [1.0, ...obs.v, Math.min(1.0, obs.tdc / escalaTdc)];
  if (x.length !== ENTRADAS_LOBOS.length) throw new Error(`percepcao com ${x.length} entradas, esperadas ${ENTRADAS_LOBOS.length}`);
  return x;
}

/** sum_j (w_j / S) * x_j, da esquerda para a direita, sem somatorio compensado */
export function ativacao(pesos: readonly number[], x: readonly number[], escala: number): number {
  if (pesos.length !== x.length) throw new Error(`${pesos.length} pesos para ${x.length} entradas`);
  let acumulado = 0.0;
  for (let j = 0; j < pesos.length; j++) acumulado = acumulado + (pesos[j] / escala) * x[j];
  return acumulado;
}

/** os termos (w_j / S) * x_j da ativacao, um por entrada */
export function termos(pesos: readonly number[], x: readonly number[], escala: number): number[] {
  if (pesos.length !== x.length) throw new Error(`${pesos.length} pesos para ${x.length} entradas`);
  return pesos.map((w, j) => (w / escala) * x[j]);
}

/** o indice sorteado com os pesos, dado u = rng.random(): a conta de random.choices(k=1) do CPython, passo a passo
 *  (itertools.accumulate, total = ultima + 0.0, bisect_right(cumulativa, u * total, 0, n - 1)) */
export function sortear(pesos: readonly number[], u: number): number {
  const cumulativa: number[] = [];
  let s = 0;
  pesos.forEach((p, i) => { s = i === 0 ? p : s + p; cumulativa.push(s); });
  const total = cumulativa[cumulativa.length - 1] + 0.0;
  if (!(total > 0.0)) throw new Error(`soma dos pesos nao positiva: ${JSON.stringify(pesos)}`);
  const alvo = u * total;
  let lo = 0, hi = cumulativa.length - 1;
  while (lo < hi) {
    const meio = (lo + hi) >> 1;
    if (alvo < cumulativa[meio]) hi = meio; else lo = meio + 1;
  }
  return lo;
}

// ================================================================== a tabela de pesos
export type TabelaPesos = Record<RegraLobos, Record<AcaoPet, number[]>>;

/** coef * S como inteiro, e so se for exato (o prior tem de devolver o mesmo float que o instinto escreve) */
function inteiroExato(coef: number, escala: number): number {
  const v = coef * escala;
  if (!Number.isInteger(v)) throw new Error(`coeficiente ${coef} nao e multiplo de 1/${escala}: o prior nao repetiria o instinto`);
  return v;
}

/** a tabela do prior, regra -> acao -> um inteiro por entrada; cada regra tem as sete acoes (PoliticaLobos._tabela_prior) */
export function tabelaPrior(escala: number): TabelaPesos {
  const tabela = {} as TabelaPesos;
  for (const regra of REGRAS_LOBOS) {
    const porAcao = {} as Record<AcaoPet, number[]>;
    for (const a of ACOES_LOBOS) {
      const coefs = PRIOR_INSTINTO[regra][a] ?? {};
      const desconhecidas = Object.keys(coefs).filter(e => !(ENTRADAS_LOBOS as readonly string[]).includes(e));
      if (desconhecidas.length) throw new Error(`entrada desconhecida no prior: ${desconhecidas}`);
      porAcao[a] = ENTRADAS_LOBOS.map(e => inteiroExato(coefs[e] ?? 0, escala));
    }
    tabela[regra] = porAcao;
  }
  return tabela;
}

// ================================================================== o cerebro
/** os termos do peso efetivo de cada candidato: impulsos (o prior), decisao (os pesos menos o prior), memoria_emocao (zero) e piso
 *  (zero fora do aprendizado), nesta ordem, a do Python */
export type Contribuicoes = Record<"impulsos" | "decisao" | "memoria_emocao" | "piso", Partial<Record<AcaoPet, number>>>;

/** o motivo de uma decisao, os campos de Aprendiz._registrar; `aprendido` e null com o aprendizado desligado */
export interface MotivoLobos {
  n: number; regra: RegraLobos; candidatos: AcaoPet[]; percepcao: Record<EntradaLobos, number>; contribuicoes: Contribuicoes;
  pesos: Partial<Record<AcaoPet, number>>; u: number | null; acao: AcaoPet; lobo_decisivo: Exclude<Lobo, "percepcao">;
  aprendido: null;
}

export interface ConfigLobosWeb { aprendizadoLigado: boolean; bits: number; escalaTdc: number; maxPesos: number }

/** a rng que o cerebro consome: uma chamada de random() por decisao com mais de um candidato, e nenhuma nas deterministas */
export interface RngCerebro { random(): number }

/** PoliticaLobos com o aprendizado desligado (L0): agir e o motivo. O aprendizado e a etapa 3 (falha alto se pedido aqui) */
export class CerebroA {
  readonly escala: number;
  readonly prior: TabelaPesos;
  readonly pesos: TabelaPesos;
  readonly motivos: MotivoLobos[] = [];
  readonly cfg: ConfigLobosWeb;
  private _ultimaRegra: RegraLobos | null = null;

  constructor(cfg: ConfigLobosWeb = { aprendizadoLigado: false, ...CLB }) {
    this.cfg = cfg;
    if (cfg.aprendizadoLigado) throw new Error("o aprendizado do cerebro A ainda nao existe no TS (W-PORTE, etapa 3)");
    if (!Number.isInteger(cfg.bits) || cfg.bits < 1) throw new Error("bits_ponto_fixo precisa ser inteiro >= 1");
    this.escala = 2 ** cfg.bits;
    this.prior = tabelaPrior(this.escala);
    this.pesos = Object.fromEntries(REGRAS_LOBOS.map(r => [r, Object.fromEntries(ACOES_LOBOS.map(a => [a, [...this.prior[r][a]]]))])) as TabelaPesos;
    const n = this.nPesos();
    if (n >= cfg.maxPesos) throw new Error(`${n} pesos, teto ${cfg.maxPesos}`);
  }

  get ultimaRegra(): RegraLobos | null { return this._ultimaRegra; }
  get ultimoMotivo(): MotivoLobos | null { return this.motivos.length ? this.motivos[this.motivos.length - 1] : null; }

  nPesos(): number {
    let n = 0;
    for (const r of REGRAS_LOBOS) for (const a of ACOES_LOBOS) n += this.pesos[r][a].length;
    return n;
  }

  percepcao(obs: Observacao): number[] { return percepcao(obs, this.cfg.escalaTdc); }

  /** Aprendiz._pesos_efetivos, sem as chaves do mundo, do corpo e do plano: (contribuicoes por termo, peso efetivo por candidato) */
  pesosEfetivos(regra: RegraLobos, candidatos: readonly AcaoPet[], x: readonly number[]): { contrib: Contribuicoes; efetivos: Partial<Record<AcaoPet, number>> } {
    const S = this.escala, prior = this.prior[regra], pesos = this.pesos[regra];
    const contrib: Contribuicoes = { impulsos: {}, decisao: {}, memoria_emocao: {}, piso: {} };
    for (const a of candidatos) contrib.impulsos[a] = ativacao(prior[a], x, S);
    for (const a of candidatos) contrib.decisao[a] = ativacao(pesos[a].map((w, j) => w - prior[a][j]), x, S);
    for (const a of candidatos) contrib.memoria_emocao[a] = 0.0;
    for (const a of candidatos) contrib.piso[a] = 0.0;
    const efetivos: Partial<Record<AcaoPet, number>> = {};
    for (const a of candidatos) efetivos[a] = contrib.impulsos[a]! + contrib.decisao[a]! + contrib.memoria_emocao[a]! + contrib.piso[a]!;
    return { contrib, efetivos };
  }

  /** PoliticaLobos.agir: a percepcao, os impulsos, o peso efetivo e o sorteio (uma chamada de rng.random() so com mais de um
   *  candidato), e o motivo da decisao */
  agir(obs: Observacao, rng: RngCerebro): AcaoPet {
    const x = this.percepcao(obs);
    const { regra, candidatos } = impulsos(obs);
    const { contrib, efetivos } = this.pesosEfetivos(regra, candidatos, x);
    let u: number | null = null, acao: AcaoPet;
    if (candidatos.length === 1) acao = candidatos[0];
    else {
      u = rng.random();
      acao = candidatos[sortear(candidatos.map(a => efetivos[a]!), u)];
    }
    this._ultimaRegra = regra;
    this.registrar(regra, candidatos, acao, x, efetivos, contrib, u);
    return acao;
  }

  /** Aprendiz._registrar, a parte do motivo: o lobo decisivo e o de maior contribuicao na acao escolhida entre memoria_emocao,
   *  impulsos e decisao; no empate, o primeiro na ordem dos lobos */
  private registrar(regra: RegraLobos, candidatos: AcaoPet[], acao: AcaoPet, x: number[], pesos: Partial<Record<AcaoPet, number>>,
    contrib: Contribuicoes, u: number | null): void {
    const presentes = ["memoria_emocao", "impulsos", "decisao"] as const;
    let maior: (typeof presentes)[number] = presentes[0];
    for (const lobo of presentes.slice(1)) if (contrib[lobo][acao]! > contrib[maior][acao]!) maior = lobo;
    this.motivos.push({
      n: this.motivos.length, regra, candidatos: [...candidatos],
      percepcao: Object.fromEntries(ENTRADAS_LOBOS.map((e, j) => [e, x[j]])) as Record<EntradaLobos, number>,
      contribuicoes: contrib, pesos: { ...pesos }, u, acao, lobo_decisivo: maior, aprendido: null,
    });
  }
}
