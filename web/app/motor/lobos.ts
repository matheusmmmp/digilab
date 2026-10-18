/* O cerebro A em TS (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md): o porte de digilab/policies/lobos.py. Etapa 2, o nucleo com o aprendizado
   desligado (L0); etapa 3, o aprendizado pela consequencia no corpo e os gestos (o pet v11, sem elogio nem bronca). So o motor e a
   paridade; nenhuma tela e nenhuma versao de pet nova (o v11 no Motor e a etapa 4).

   Os quatro lobos, como no Python:
     PERCEPCAO        Observacao -> x = (1, Estado.vetor, min(1, ticks sem cuidado / escala)), os floats que o instinto le; com o corpo,
                      tambem os receptores novos (tedio, solidao, estresse, dor, susto) / S, as entradas do corpo;
     MEMORIA/EMOCAO   contribuicao zero em toda decisao; so conta o que passou por ele (MemoriaEmocao do Python);
     IMPULSOS         as regras do instinto (policy.py, PoliticaInstinto.agir), rodadas com uma rng-sonda que nao consome a rng do
                      motor: a regra que disparou e os candidatos, na ordem do instinto;
     DECISAO          pesos INTEIROS w[regra][acao][entrada] na escala S = 2**bits, no prior do instinto (os coeficientes vezes S), e,
                      com o corpo, uma tabela a parte nas regras de tempo livre, um peso por (acao, receptor novo), prior 0.
                      Peso efetivo = sum_j (w_j / S) * x_j, da esquerda para a direita; a acao sai de UMA chamada de rng.random(),
                      pela conta de random.choices(k=1) do CPython (cumulativa, total = ultima + 0.0, bisect_right ate n - 1).

   Com S potencia de dois, w_j / S e exato e, no prior, o peso efetivo e o mesmo float que o instinto escreve, somado na mesma ordem: a
   decisao e a do instinto, byte a byte (o G-PAR-L0, test/lobos.test.ts contra a secao l0 de test/gabaritos/lobos_python.json).

   O aprendizado (etapa 3) e todo em inteiros: o sinal da consequencia sobre os receptores do corpo (`sinalCorpo`, separado por canal
   com a soma telescopica, contrato K-6), o carinho pelo corpo (`mudancaNoCorpo`), o tapa com a recompensa direta e a regra da L1
   (`atualizarPesos`, cortada em prior +- teto). O G-PAR-L1 (test/lobos_v11.test.ts) rejoga os ganchos das vidas v11 do gabarito.

   Nenhuma funcao transcendental (nada de Math.exp ou Math.log): o Chrome difere do Node so no ultimo bit delas, e o nucleo fica fora
   disso. O motivo de cada decisao e o estado do aprendizado usam os nomes em snake_case do Python de proposito: e o mesmo dado de
   `_registrar` e de `estado_interno`, conferido campo a campo. */
import { C, CLB, type ConfigCorpo } from "./constantes.ts";
import { eNoite } from "./estado.ts";
import { divArred } from "./mundo.ts";
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

/** os receptores de hoje (leitura = S - falta, na ordem de Estado.vetor) e os novos (leitura = a falta; dor e susto: a concentracao;
 *  a vontade e o conforto, do banheiro, a concentracao), pelo nome dos campos da PercepcaoCorpo (motor_corpo.py) */
export const RECEPTORES_HOJE_LOBOS = ["fome", "higiene", "energia", "humor", "saude"] as const;
export const RECEPTORES_NOVOS_LOBOS = ["tedio", "curiosidade", "solidao", "estresse", "dor", "susto", "vontade", "conforto"] as const;
/** os drives novos que entram no sinal (secao 9 da TAREFA_V2_CORPO_DRIVES: o susto fica fora) */
export const DRIVES_NOVOS_SINAL = ["tedio", "curiosidade", "solidao", "estresse", "dor", "vontade", "conforto"] as const;
/** BN-6: o receptor do conforto le a concentracao; a falta e S - leitura */
const RECEPTORES_FALTA_INVERTIDA: readonly string[] = ["conforto"];
/** as regras com as entradas do corpo (secao 11: so as de tempo livre); as do mundo (bola e fruta) nao existem no TS */
export const REGRAS_ENTRADAS_CORPO: readonly RegraLobos[] = ["tempo_livre"];
/** CANAIS-REFORCO: o canal de cada drive de hoje pelo indice em Estado.vetor, e o grupo de pesos que cada canal credita (o humor vai a
 *  fruta; os drives novos, todos ao corpo) */
const CANAL_DO_DRIVE: Readonly<Record<number, string>> = { 0: "fome", 1: "higiene", 2: "energia", 3: "humor" };
const ROTA_CANAIS: Readonly<Record<string, "corpo" | "fruta">> = { fome: "corpo", higiene: "corpo", energia: "corpo", humor: "fruta" };
const ALVOS_CANAIS = ["corpo", "fruta"] as const;
/** as acoes do dono que sao cuidado (lobos.CUIDADOS) e as do feedback, que o v11 nao tem */
const CUIDADOS: readonly string[] = ["alimentar", "limpar", "brincar", "acariciar", "petisco", "levar_ao_banheiro", "tratar_lesao"];
const FEEDBACK: readonly string[] = ["elogiar", "repreender"];
export const VALOR_TAPA_LOBOS = "tapa";

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

// ================================================================== a aritmetica inteira do aprendizado
const semMenosZero = (q: number): number => (q === 0 ? 0 : q);

/** o inteiro mais proximo, meio longe do zero (lobos.arred: int(x + 0.5), simetrico; o round() do Python e meio-para-par) */
export function arred(x: number): number {
  if (!Number.isFinite(x)) throw new Error(`arred de um numero nao finito: ${x}`);
  return x >= 0.0 ? Math.trunc(x + 0.5) : semMenosZero(-Math.trunc(-x + 0.5));
}

/** n tem de ser um inteiro exato no double (|n| < 2^53): a conta do Python e em inteiros sem limite, a do JS so ate ai (falha alto) */
function inteiro(n: number, onde: string): number {
  if (!Number.isSafeInteger(n)) throw new Error(`${onde}: ${n} fora dos inteiros exatos do double`);
  return n;
}

/** a tabela de uma regra: acao -> um inteiro por entrada */
export type PesosDaRegra = Record<AcaoPet, number[]>;

/** o registro de uma decisao, para o credito (o `_registro_decisao` do Python): X = arred(x S), P = arred(p S), W = max(1, arred(w S));
 *  `corpo.X` sao as entradas do corpo da decisao (arred(leitura / S x S), a leitura) */
export interface RegistroLobos {
  regra: RegraLobos; candidatos: AcaoPet[]; acao: AcaoPet; X: number[];
  P: Partial<Record<AcaoPet, number>>; W: Partial<Record<AcaoPet, number>>; corpo?: { X: number[] };
}

/** lobos.atualizar_pesos, a regra da L1 em inteiros na tabela de uma regra: dw[a][j] = div_arred(f_S passo X_j (S 1[a=a*] - P_a),
 *  S S W_a), cortado em prior +- teto. Devolve quantos cortes no teto */
export function atualizarPesos(pesos: PesosDaRegra, prior: PesosDaRegra, registro: Pick<RegistroLobos, "candidatos" | "acao" | "X" | "P" | "W">,
  fS: number, passo: number, teto: number, S: number): number {
  let cortes = 0;
  for (const a of registro.candidatos) {
    const fator = (a === registro.acao ? S : 0) - registro.P[a]!;
    if (fator === 0) continue;
    const w = pesos[a], w0 = prior[a];
    const denominador = inteiro(S * S * registro.W[a]!, "atualizar_pesos, denominador");
    registro.X.forEach((X, j) => {
      if (X === 0) return;
      const delta = divArred(inteiro(fS * passo * X * fator, "atualizar_pesos, numerador"), denominador);
      if (delta === 0) return;
      let novo = w[j] + delta;
      if (novo > w0[j] + teto) { novo = w0[j] + teto; cortes += 1; }
      else if (novo < w0[j] - teto) { novo = w0[j] - teto; cortes += 1; }
      w[j] = novo;
    });
  }
  return cortes;
}

// ================================================================== o sinal da consequencia
/** a configuracao da consequencia (ConfigConsequencia do Python, so os campos que o v11 usa): os drives do N3 (indices em Estado.vetor),
 *  o ganho, os canais e os w_d do corpo pelo nome do receptor */
export interface ConfigConsequenciaWeb {
  drives: readonly number[]; ganho: number; canais: boolean; pesosDrivesCorpo: Readonly<Record<string, number>>;
}

/** D(h) = soma_i (S - arred(h_i S))^2 sobre os drives (indices em Estado.vetor), ponto de ajuste 1.0 */
export function deficitHomeostatico(v: readonly number[], drives: readonly number[], S: number): number {
  let d = 0;
  for (const i of drives) {
    const h = v[i];
    if (!(h >= 0.0 && h <= 1.0)) throw new Error(`drive ${i} fora de [0, 1]: ${h}`);
    const falta = S - arred(h * S);
    d += falta * falta;
  }
  return d;
}

/** o par de observacoes de uma decisao (a Transicao do Python, sem a recompensa) */
export interface TransicaoLobos { observacao: ObservacaoLobos; acao: AcaoPet; observacaoSeguinte: ObservacaoLobos }

/** lobos.sinal_homeostatico (N3): div_arred(ganho (D(antes) - D(depois)), S) sobre a transicao do engine */
export function sinalHomeostatico(t: TransicaoLobos, S: number, cc: ConfigConsequenciaWeb): number {
  if (!Number.isInteger(cc.ganho) || cc.ganho < 0) throw new Error(`ganho precisa ser inteiro >= 0: ${cc.ganho}`);
  const antes = deficitHomeostatico(t.observacao.v, cc.drives, S), depois = deficitHomeostatico(t.observacaoSeguinte.v, cc.drives, S);
  return divArred(inteiro(cc.ganho * (antes - depois), "sinal_homeostatico"), S);
}

/** a PercepcaoCorpo: os receptores na escala S, pelo nome (um receptor que o corpo nao tem fica de fora) */
export type PercepcaoCorpoLobos = Readonly<Record<string, number>>;
/** a Observacao do motor com o corpo (Observacao.corpo do Python) */
export interface ObservacaoLobos extends Observacao { corpo?: PercepcaoCorpoLobos }

/** lobos.leitura_receptor: o inteiro em [0, S] do receptor; um que nao existe, ou fora da escala, falha alto */
export function leituraReceptor(pc: PercepcaoCorpoLobos, nome: string, S: number): number {
  const v = pc[nome];
  if (v === undefined || v === null) throw new Error(`corpo: o receptor ${nome} nao existe nesta Observacao.corpo`);
  if (!Number.isInteger(v) || v < 0 || v > S) throw new Error(`corpo: receptor ${nome} fora de inteiros em [0, ${S}]: ${v}`);
  return v;
}

/** lobos.falta_receptor: S - leitura nos de hoje (e no conforto), a propria leitura nos novos */
export function faltaReceptor(pc: PercepcaoCorpoLobos, nome: string, S: number): number {
  const v = leituraReceptor(pc, nome, S);
  if ((RECEPTORES_HOJE_LOBOS as readonly string[]).includes(nome) || RECEPTORES_FALTA_INVERTIDA.includes(nome)) return S - v;
  if ((RECEPTORES_NOVOS_LOBOS as readonly string[]).includes(nome)) return v;
  throw new Error(`receptor desconhecido: ${nome}`);
}

/** lobos.contribuicoes_corpo, sem a janela da A2.4: c_d = w_d (falta_d(antes)^2 - falta_d(depois)^2), na ordem dos drives */
export function contribuicoesCorpo(antes: PercepcaoCorpoLobos, depois: PercepcaoCorpoLobos, drives: readonly string[], S: number,
  pesosDrives: Readonly<Record<string, number>>): Record<string, number> {
  const c: Record<string, number> = {};
  for (const d of drives) {
    const fa = faltaReceptor(antes, d, S), fd = faltaReceptor(depois, d, S);
    const wd = pesosDrives[d];
    if (wd === undefined) throw new Error(`w_d do drive ${d} ausente`);
    if (!Number.isInteger(wd) || wd < 0) throw new Error(`w_d do drive ${d} precisa ser inteiro >= 0: ${wd}`);
    c[d] = wd * (fa * fa - fd * fd);
  }
  return c;
}

/** lobos.sinal_corpo: div_arred(ganho soma_d c_d, S) sobre os receptores */
export function sinalCorpo(antes: PercepcaoCorpoLobos, depois: PercepcaoCorpoLobos, drives: readonly string[], ganho: number, S: number,
  pesosDrives: Readonly<Record<string, number>>): number {
  if (!Number.isInteger(ganho) || ganho < 0) throw new Error(`ganho precisa ser inteiro >= 0: ${ganho}`);
  let total = 0;
  for (const c of Object.values(contribuicoesCorpo(antes, depois, drives, S, pesosDrives))) total += c;
  return divArred(inteiro(ganho * total, "sinal_corpo"), S);
}

/** lobos.sinal_corpo_canais: o sinal_corpo separado por drive, pela soma telescopica (a soma dos canais e o escalar, contrato K-6) */
export function sinalCorpoCanais(antes: PercepcaoCorpoLobos, depois: PercepcaoCorpoLobos, drives: readonly string[], ganho: number,
  S: number, pesosDrives: Readonly<Record<string, number>>): Record<string, number> {
  if (!Number.isInteger(ganho) || ganho < 0) throw new Error(`ganho precisa ser inteiro >= 0: ${ganho}`);
  const canais: Record<string, number> = {};
  let acumulado = 0, anterior = 0;
  for (const [d, c] of Object.entries(contribuicoesCorpo(antes, depois, drives, S, pesosDrives))) {
    if (!(d in ROTA_CANAIS) && !(DRIVES_NOVOS_SINAL as readonly string[]).includes(d)) throw new Error(`drive ${d} sem canal`);
    acumulado += c;
    const parcial = divArred(inteiro(ganho * acumulado, "sinal_corpo_canais"), S);
    canais[d] = parcial - anterior;
    anterior = parcial;
  }
  return canais;
}

/** lobos.receptores_novos, sem o mundo fisico: tedio, solidao e estresse com os drives novos, dor e susto com os gestos. O banheiro (a
 *  vontade e o conforto) nao existe no cerebro TS: falha alto */
export function receptoresNovos(cc: Pick<ConfigCorpo, "drives_novos" | "gestos" | "banheiro">): string[] {
  if (cc.banheiro) throw new Error("o banheiro (a vontade e o conforto) nao existe no cerebro A em TS");
  const tem = new Set<string>();
  if (cc.drives_novos) for (const r of ["tedio", "solidao", "estresse"]) tem.add(r);
  if (cc.gestos) for (const r of ["dor", "susto"]) tem.add(r);
  return RECEPTORES_NOVOS_LOBOS.filter(r => tem.has(r));
}

// ================================================================== a tabela de pesos
export type TabelaPesos = Record<RegraLobos, PesosDaRegra>;

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
    const porAcao = {} as PesosDaRegra;
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

const copiar = <T extends Partial<Record<string, PesosDaRegra>>>(t: T): T =>
  Object.fromEntries(Object.entries(t).map(([r, acoes]) => [r, Object.fromEntries(Object.entries(acoes!).map(([a, v]) => [a, [...v]]))])) as T;

// ================================================================== memoria e emocao
/** lobos.MemoriaEmocao: o lobo nomeado, sem efeito na decisao; so registra o que passou por ele */
export class MemoriaEmocao {
  elogios = 0;
  broncas = 0;
  cuidados = 0;
  outrasAcoesDono = 0;
  decisoes = 0;
  tickUltimaAcaoDono: number | null = null;

  acaoDono(acao: string, tick: number): void {
    if (acao === "elogiar") this.elogios += 1;
    else if (acao === "repreender") this.broncas += 1;
    else if (CUIDADOS.includes(acao)) this.cuidados += 1;
    else this.outrasAcoesDono += 1;
    this.tickUltimaAcaoDono = tick;
  }

  decisao(): void { this.decisoes += 1; }

  paraDict() {
    return { elogios: this.elogios, broncas: this.broncas, cuidados: this.cuidados, outras_acoes_dono: this.outrasAcoesDono,
      decisoes: this.decisoes, tick_ultima_acao_dono: this.tickUltimaAcaoDono };
  }
}

// ================================================================== o cerebro
/** os termos do peso efetivo de cada candidato: impulsos (o prior), decisao (os pesos menos o prior, e as entradas do corpo),
 *  memoria_emocao (zero) e piso (so com o aprendizado ligado), nesta ordem, a do Python */
export type Contribuicoes = Record<"impulsos" | "decisao" | "memoria_emocao" | "piso", Partial<Record<AcaoPet, number>>>;

/** o motivo de uma decisao, os campos de Aprendiz._registrar e de PoliticaLobos.agir; `aprendido` e null com o aprendizado desligado.
 *  Com o corpo: a percepcao do corpo (as entradas novas), o aprendido nelas (so nas regras de tempo livre, aprendendo) e o sinal da
 *  consequencia (posto no credito, depois da decisao) */
export interface MotivoLobos {
  n: number; regra: RegraLobos; candidatos: AcaoPet[]; percepcao: Record<EntradaLobos, number>; contribuicoes: Contribuicoes;
  pesos: Partial<Record<AcaoPet, number>>; u: number | null; acao: AcaoPet; lobo_decisivo: Exclude<Lobo, "percepcao">;
  aprendido: Partial<Record<AcaoPet, number[]>> | null;
  percepcao_corpo?: Record<string, number>;
  aprendido_corpo?: Partial<Record<AcaoPet, number[]>>;
  sinal_corpo?: { f: number; drives: Record<string, number> };
}

/** o aprendiz (ConfigLobos com o aprendizado ligado): passo, teto e piso na escala S e a recompensa do tapa em unidades de 1.0 */
export interface ConfigAprendizWeb { passo: number; teto: number; piso: number; recompensaTapa: number }

/** a ConfigLobos do TS. `aprendiz` e obrigatorio com o aprendizado ligado; `corpo` liga a leitura do corpo (os receptores novos) */
export interface ConfigLobosWeb {
  aprendizadoLigado: boolean; bits: number; escalaTdc: number; maxPesos: number;
  aprendiz?: ConfigAprendizWeb;
  corpo?: Pick<ConfigCorpo, "ligada" | "drives_novos" | "gestos" | "banheiro" | "escala_receptor">;
}

/** a rng que o cerebro consome: uma chamada de random() por decisao com mais de um candidato, e nenhuma nas deterministas */
export interface RngCerebro { random(): number }

/** o que aconteceu na decisao, no gancho do corpo (o `ocorrido` do MotorCorpo): a acao e os estimulos dela */
export interface OcorridoCorpo { acao: string; estimulos: readonly (readonly (string | number)[])[] }

/** os totais dos canais (CANAIS-REFORCO), so depois do primeiro credito por canal */
export interface CanaisLobos { creditos: number; por_canal: Record<string, number>; por_alvo: Record<"corpo" | "fruta", number> }

/** o credito pendente pelo corpo, entre observarConsequencia e o gancho do corpo */
interface CorpoPendente { registro: RegistroLobos; antes: PercepcaoCorpoLobos; cc: ConfigConsequenciaWeb }

/** PoliticaLobos (sem as chaves do mundo, das frutas, do plano, do traco, da janela A2.4 e do banheiro): agir, o motivo e o
 *  aprendizado pela consequencia no corpo, pelo carinho e pelo tapa */
export class CerebroA {
  readonly escala: number;
  readonly prior: TabelaPesos;
  readonly pesos: TabelaPesos;
  readonly motivos: MotivoLobos[] = [];
  readonly cfg: ConfigLobosWeb;
  readonly memoria = new MemoriaEmocao();
  /** os receptores novos que o cerebro le (vazio sem o corpo) e os drives novos do sinal que o corpo tem */
  readonly receptoresNovos: readonly string[] = [];
  readonly canaisNovos: readonly string[] = [];
  /** a tabela das entradas do corpo, regra -> acao -> um peso por receptor novo (prior 0; vazia sem receptores novos) */
  readonly priorCorpo: Partial<Record<RegraLobos, PesosDaRegra>> = {};
  readonly pesosCorpo: Partial<Record<RegraLobos, PesosDaRegra>> = {};
  private readonly temCorpo: boolean;
  private readonly piso: number;
  private _ultimaRegra: RegraLobos | null = null;
  private xCorpo: number[] = [];
  private registroDecisao: RegistroLobos | null = null;
  private ultima: RegistroLobos | null = null;
  private acaoSemGancho: AcaoPet | null = null;
  private corpoPendente: CorpoPendente | null = null;
  private ccCorpo: ConfigConsequenciaWeb | null = null;
  private tickUltimoCuidado = 0;
  private readonly tickUltimaDecisao = -1;     // so o observar da fonte dono o anda (os chamados), que o v11 nao tem
  private nAtualizacoes = 0;
  private cortesTeto = 0;
  private readonly recompensas: Record<string, number> = { elogio: 0, repreensao: 0, latencia: 0, ignorado: 0 };
  private canais: CanaisLobos | null = null;

  constructor(cfg: ConfigLobosWeb = { aprendizadoLigado: false, ...CLB }) {
    this.cfg = cfg;
    if (!Number.isInteger(cfg.bits) || cfg.bits < 1) throw new Error("bits_ponto_fixo precisa ser inteiro >= 1");
    this.escala = 2 ** cfg.bits;
    this.prior = tabelaPrior(this.escala);
    this.pesos = copiar(this.prior);
    if (this.nPesos() >= cfg.maxPesos) throw new Error(`${this.nPesos()} pesos, teto ${cfg.maxPesos}`);
    if (cfg.aprendizadoLigado) {
      const ap = cfg.aprendiz;
      if (ap === undefined) throw new Error("o aprendizado ligado precisa do aprendiz (passo, teto, piso, recompensaTapa)");
      for (const nome of ["passo", "teto", "piso"] as const) {
        if (!Number.isInteger(ap[nome]) || ap[nome] <= 0) throw new Error(`ConfigLobos.${nome} precisa ser inteiro positivo: ${ap[nome]}`);
      }
      if (!Number.isFinite(ap.recompensaTapa)) throw new Error(`recompensa_tapa precisa ser finita: ${ap.recompensaTapa}`);
    }
    this.piso = cfg.aprendizadoLigado ? cfg.aprendiz!.piso / this.escala : 0;
    this.temCorpo = cfg.corpo !== undefined && cfg.corpo.ligada;
    if (this.temCorpo) {
      const cc = cfg.corpo!;
      if (cc.escala_receptor !== this.escala) throw new Error(`receptores na escala ${cc.escala_receptor}, cerebro na escala ${this.escala}`);
      this.receptoresNovos = receptoresNovos(cc);
      this.canaisNovos = DRIVES_NOVOS_SINAL.filter(d => this.receptoresNovos.includes(d));
      if (this.receptoresNovos.length) {
        for (const r of REGRAS_ENTRADAS_CORPO) {
          this.priorCorpo[r] = Object.fromEntries(ACOES_LOBOS.map(a => [a, this.receptoresNovos.map(() => 0)])) as PesosDaRegra;
        }
        Object.assign(this.pesosCorpo, copiar(this.priorCorpo));
        if (this.nPesos() >= cfg.maxPesos) throw new Error(`${this.nPesos()} pesos, teto ${cfg.maxPesos}`);
      }
    }
  }

  get aprende(): boolean { return this.cfg.aprendizadoLigado; }
  get ultimaRegra(): RegraLobos | null { return this._ultimaRegra; }
  get ultimoMotivo(): MotivoLobos | null { return this.motivos.length ? this.motivos[this.motivos.length - 1] : null; }
  private get ap(): ConfigAprendizWeb { return this.cfg.aprendiz!; }

  nPesos(): number {
    let n = 0;
    for (const tabela of [this.pesos, this.pesosCorpo] as Partial<Record<RegraLobos, PesosDaRegra>>[]) {
      for (const acoes of Object.values(tabela)) for (const v of Object.values(acoes!)) n += v.length;
    }
    return n;
  }

  /** |w - w0| de cada peso: a tabela da decisao e a do corpo */
  private *desvios(): Generator<number> {
    for (const [prior, pesos] of [[this.prior, this.pesos], [this.priorCorpo, this.pesosCorpo]] as Partial<Record<RegraLobos, PesosDaRegra>>[][]) {
      for (const [r, acoes] of Object.entries(pesos)) {
        for (const [a, v] of Object.entries(acoes!)) {
          const v0 = prior[r as RegraLobos]![a as AcaoPet];
          for (let j = 0; j < v.length; j++) yield Math.abs(v[j] - v0[j]);
        }
      }
    }
  }

  /** max |w - w0| sobre todos os pesos */
  desvioMaximo(): number { let m = -Infinity; for (const d of this.desvios()) m = Math.max(m, d); return m; }

  /** quantos pesos estao exatamente no teto */
  pesosNoTeto(): number { let n = 0; for (const d of this.desvios()) if (d === this.ap.teto) n += 1; return n; }

  percepcao(obs: Observacao): number[] { return percepcao(obs, this.cfg.escalaTdc); }

  /** Aprendiz._pesos_efetivos, sem as chaves do mundo, do plano e do banheiro: (contribuicoes por termo, peso efetivo por candidato) */
  pesosEfetivos(regra: RegraLobos, candidatos: readonly AcaoPet[], x: readonly number[]): { contrib: Contribuicoes; efetivos: Partial<Record<AcaoPet, number>> } {
    const S = this.escala, prior = this.prior[regra], pesos = this.pesos[regra];
    const contrib: Contribuicoes = { impulsos: {}, decisao: {}, memoria_emocao: {}, piso: {} };
    for (const a of candidatos) contrib.impulsos[a] = ativacao(prior[a], x, S);
    for (const a of candidatos) contrib.decisao[a] = ativacao(pesos[a].map((w, j) => w - prior[a][j]), x, S);
    for (const a of candidatos) contrib.memoria_emocao[a] = 0.0;
    const tabela = this.pesosCorpo[regra];
    if (tabela !== undefined) {
      /* CORPO: as entradas novas (receptores novos / S) nas regras de tempo livre, prior 0: todo o termo e aprendido */
      for (const a of candidatos) contrib.decisao[a] = contrib.decisao[a]! + ativacao(tabela[a], this.xCorpo, S);
    }
    for (const a of candidatos) {
      const soma = contrib.impulsos[a]! + contrib.decisao[a]! + contrib.memoria_emocao[a]!;
      contrib.piso[a] = this.aprende && soma < this.piso ? this.piso - soma : 0.0;
    }
    const efetivos: Partial<Record<AcaoPet, number>> = {};
    for (const a of candidatos) efetivos[a] = contrib.impulsos[a]! + contrib.decisao[a]! + contrib.memoria_emocao[a]! + contrib.piso[a]!;
    return { contrib, efetivos };
  }

  /** PoliticaLobos.agir: a percepcao (e a do corpo), os impulsos, o peso efetivo e o sorteio (uma chamada de rng.random() so com mais
   *  de um candidato), o motivo e o registro da decisao para o credito */
  agir(obs: ObservacaoLobos, rng: RngCerebro): AcaoPet {
    const S = this.escala;
    if (this.temCorpo) {
      if (this.acaoSemGancho !== null || this.corpoPendente !== null) throw new Error("corpo: a decisao anterior ficou sem o gancho de consequencia");
      if (obs.corpo === undefined) throw new Error("corpo: Observacao sem o campo corpo (o cerebro com a chave do corpo precisa do corpo)");
      this.xCorpo = this.receptoresNovos.map(r => leituraReceptor(obs.corpo!, r, S) / S);
    }
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
    if (this.receptoresNovos.length) {
      const motivo = this.motivos[this.motivos.length - 1];
      motivo.percepcao_corpo = Object.fromEntries(this.receptoresNovos.map((r, i) => [r, this.xCorpo[i]]));
      const tabela = this.pesosCorpo[regra];
      if (tabela !== undefined && this.aprende) {
        motivo.aprendido_corpo = Object.fromEntries(candidatos.map(a => [a, termos(tabela[a], this.xCorpo, S)]));
        this.registroDecisao!.corpo = { X: this.xCorpo.map(v => arred(v * S)) };
      }
    }
    return acao;
  }

  /** Aprendiz._registrar: o registro da decisao (so aprendendo) e o motivo. O lobo decisivo e o de maior contribuicao na acao escolhida
   *  entre memoria_emocao, impulsos e decisao; no empate, o primeiro na ordem dos lobos */
  private registrar(regra: RegraLobos, candidatos: AcaoPet[], acao: AcaoPet, x: number[], pesos: Partial<Record<AcaoPet, number>>,
    contrib: Contribuicoes, u: number | null): void {
    let aprendido: MotivoLobos["aprendido"] = null;
    let registro: RegistroLobos | null = null;
    if (this.aprende) {
      const S = this.escala, prior = this.prior[regra], tabela = this.pesos[regra];
      aprendido = Object.fromEntries(candidatos.map(a => [a, termos(tabela[a].map((w, j) => w - prior[a][j]), x, S)]));
      let total = 0.0;
      for (const a of candidatos) total = total + pesos[a]!;
      registro = {
        regra, candidatos: [...candidatos], acao, X: x.map(xj => arred(xj * S)),
        P: Object.fromEntries(candidatos.map(a => [a, arred(pesos[a]! / total * S)])),
        W: Object.fromEntries(candidatos.map(a => [a, Math.max(1, arred(pesos[a]! * S))])),
      };
    }
    this.registroDecisao = registro;
    const presentes = ["memoria_emocao", "impulsos", "decisao"] as const;
    let maior: (typeof presentes)[number] = presentes[0];
    for (const lobo of presentes.slice(1)) if (contrib[lobo][acao]! > contrib[maior][acao]!) maior = lobo;
    this.motivos.push({
      n: this.motivos.length, regra, candidatos: [...candidatos],
      percepcao: Object.fromEntries(ENTRADAS_LOBOS.map((e, j) => [e, x[j]])) as Record<EntradaLobos, number>,
      contribuicoes: contrib, pesos: { ...pesos }, u, acao, lobo_decisivo: maior, aprendido,
    });
  }

  // ------------------------------------------------------------- os ganchos do motor
  /** CORPO: cada decisao observada espera UM gancho do corpo antes da proxima */
  private esperarGanchoCorpo(t: TransicaoLobos): void {
    if (!this.temCorpo) return;
    if (this.acaoSemGancho !== null) throw new Error(`corpo: a decisao anterior (${this.acaoSemGancho}) ficou sem o gancho de consequencia`);
    if (t.observacao.corpo === undefined || t.observacaoSeguinte.corpo === undefined) throw new Error("corpo: transicao sem Observacao.corpo");
    this.acaoSemGancho = t.acao;
  }

  /** Aprendiz.observar_consequencia com a chave do corpo (o `f_S` e o do N3 sobre a transicao do engine: conferido e nao creditado; o
   *  credito espera o gancho do corpo, `consequenciaCorpo`). Sem o corpo, o N3 nao foi portado: falha alto */
  observarConsequencia(t: TransicaoLobos, fS: number, cc: ConfigConsequenciaWeb): void {
    this.memoria.decisao();
    this.esperarGanchoCorpo(t);
    if (!this.aprende) return;
    const registro = this.registroDecisao;
    if (registro === null || registro.acao !== t.acao) throw new Error("registro da decisao nao corresponde a acao observada");
    this.ultima = registro;
    this.recompensas.consequencia = (this.recompensas.consequencia ?? 0) + 1;
    if (!this.temCorpo) throw new Error("a consequencia sem o corpo (o N3 da transicao) nao existe no cerebro A em TS");
    if (fS !== sinalHomeostatico(t, this.escala, cc)) throw new Error("corpo: o f_S recebido nao e o sinal_homeostatico da transicao");
    this.ccCorpo = cc;
    this.corpoPendente = { registro, antes: t.observacao.corpo!, cc };
  }

  /** Aprendiz.consequencia_corpo, sem o mundo fisico: uma vez por decisao, depois dos estimulos da propria acao; credita o
   *  `sinal_corpo` pendente. A fruta (E2) nao existe no TS: um estimulo de fruta falha alto */
  consequenciaCorpo(acao: AcaoPet, ocorrido: OcorridoCorpo, obsDepois: ObservacaoLobos): void {
    if (!this.temCorpo) return;
    const esperada = this.acaoSemGancho;
    this.acaoSemGancho = null;
    if (esperada === null) throw new Error("corpo: gancho de consequencia sem decisao observada (ou a segunda chamada na mesma decisao)");
    if (esperada !== acao || ocorrido.acao !== acao) throw new Error(`corpo: gancho de ${acao} (${ocorrido.acao}) para a decisao observada de ${esperada}`);
    if (ocorrido.estimulos.some(e => e[0] === "fruta")) throw new Error("corpo: a fruta (E2) nao existe no cerebro A em TS");
    this.creditarCorpo(obsDepois);
  }

  /** Aprendiz._creditar_corpo, sem a fruta, o paladar e a janela: antes = a percepcao da decisao, depois = `obsDepois.corpo`; a conta
   *  fica no motivo da decisao (`sinal_corpo`) */
  private creditarCorpo(obsDepois: ObservacaoLobos): void {
    const p = this.corpoPendente;
    this.corpoPendente = null;
    if (p === null) return;
    if (obsDepois.corpo === undefined) throw new Error("corpo: obs_depois sem Observacao.corpo");
    const S = this.escala, drives = this.drivesCorpo(p.cc);
    const contrib = contribuicoesCorpo(p.antes, obsDepois.corpo, drives, S, p.cc.pesosDrivesCorpo);
    const f = sinalCorpo(p.antes, obsDepois.corpo, drives, p.cc.ganho, S, p.cc.pesosDrivesCorpo);
    if (this.motivos.length) this.motivos[this.motivos.length - 1].sinal_corpo = { f, drives: contrib };
    if (p.cc.canais) this.creditarCanais(p.registro, sinalCorpoCanais(p.antes, obsDepois.corpo, drives, p.cc.ganho, S, p.cc.pesosDrivesCorpo), f);
    else if (f !== 0) this.creditar(p.registro, f);
  }

  /** os drives do sinal pelo corpo, pelo nome do receptor: os do N3 e os drives novos que o corpo tem (o humor so com a fruta) */
  private drivesCorpo(cc: ConfigConsequenciaWeb): string[] {
    return [...cc.drives.map(i => {
      const r = RECEPTORES_HOJE_LOBOS[i];
      if (r === undefined) throw new Error(`drive ${i} sem receptor`);
      return r;
    }), ...this.canaisNovos];
  }

  /** Aprendiz._creditar_canais: a soma dos canais e o escalar (contrato K-6, falha alto); cada canal vai ao seu grupo de pesos. Sem
   *  pesos que leiam a fruta no TS, o canal da fruta tem de vir zero */
  private creditarCanais(registro: RegistroLobos, canais: Record<string, number>, fS: number): void {
    let total = 0;
    const alvos = { corpo: 0, fruta: 0 };
    for (const [canal, f] of Object.entries(canais)) {
      if (!(canal in ROTA_CANAIS) && !this.canaisNovos.includes(canal)) throw new Error(`canal desconhecido: ${canal}`);
      total += f;
      alvos[canal in ROTA_CANAIS ? ROTA_CANAIS[canal] : "corpo"] += f;
    }
    if (total !== fS) throw new Error(`CANAIS-REFORCO: soma dos canais ${total} != escalar ${fS} (contrato K-6)`);
    if (alvos.fruta !== 0) throw new Error("CANAIS-REFORCO: canal da fruta sem peso que leia a fruta nesta decisao");
    if (this.canais === null) {
      this.canais = { creditos: 0, por_canal: Object.fromEntries([...Object.keys(ROTA_CANAIS), ...this.canaisNovos].map(c => [c, 0])),
        por_alvo: { corpo: 0, fruta: 0 } };
    }
    this.canais.creditos += 1;
    for (const [canal, f] of Object.entries(canais)) this.canais.por_canal[canal] += f;
    for (const a of ALVOS_CANAIS) this.canais.por_alvo[a] += alvos[a];
    if (alvos.corpo !== 0 || alvos.fruta !== 0) this.aplicarSinal(registro, alvos.corpo);
  }

  /** Aprendiz._creditar sem o traco: o sinal na decisao, so */
  private creditar(registro: RegistroLobos, fS: number): void { this.aplicarSinal(registro, fS); }

  /** Aprendiz._aplicar_sinal: a regra da L1 na tabela da regra e, com o corpo, nas entradas novas (X = a leitura), com o canal do corpo */
  private aplicarSinal(registro: RegistroLobos, fCorpo: number): void {
    const g = registro.regra, { passo, teto } = this.ap, S = this.escala;
    this.cortesTeto += atualizarPesos(this.pesos[g], this.prior[g], registro, fCorpo, passo, teto, S);
    if (registro.corpo !== undefined) {
      this.cortesTeto += atualizarPesos(this.pesosCorpo[g]!, this.priorCorpo[g]!, { ...registro, X: registro.corpo.X }, fCorpo, passo, teto, S);
    }
    this.nAtualizacoes += 1;
  }

  /** Aprendiz.receber_acao_dono: o dono passa pela memoria; aprendendo, acerta o relogio do cuidado e o tapa credita a ultima decisao
   *  com a recompensa direta (CD-10). O elogio e a bronca (o v11 nao os tem, PW-1) e os chamados pendentes (so na fonte dono) nao foram
   *  portados: o elogio e a bronca falham alto, e os outros cuidados nao tem chamado a pagar */
  receberAcaoDono(acao: string, tick: number): void {
    this.memoria.acaoDono(acao, tick);
    if (!this.aprende) return;
    if (tick < this.tickUltimoCuidado) throw new Error(`acao do dono no passado: ${tick} < ${this.tickUltimoCuidado}`);
    this.tickUltimoCuidado = tick;
    if (FEEDBACK.includes(acao)) throw new Error(`${acao}: o elogio e a bronca nao existem no cerebro A em TS (o v11 nao os tem, PW-1)`);
    if (acao === VALOR_TAPA_LOBOS) {
      if (this.ultima === null) return;
      this.creditar(this.ultima, arred(this.ap.recompensaTapa * this.escala));
      this.recompensas.tapa = (this.recompensas.tapa ?? 0) + 1;
    }
  }

  /** Aprendiz.mudanca_no_corpo: o carinho chega so pelo corpo (CD-4). O sinal_corpo dos receptores antes e depois (os drives do N3 e os
   *  novos, sem o humor) vai a ultima decisao, escalar; o carinho acerta o relogio do cuidado */
  mudancaNoCorpo(antes: ObservacaoLobos, depois: ObservacaoLobos): void {
    const tick = this.tickUltimoCuidado + antes.tdc;
    this.memoria.acaoDono("acariciar", tick);
    if (!this.aprende) return;
    if (!this.temCorpo) throw new Error("mudanca_no_corpo num cerebro que aprende sem a chave do corpo");
    if (antes.corpo === undefined || depois.corpo === undefined) throw new Error("mudanca_no_corpo sem Observacao.corpo");
    if (depois.tdc !== 0) throw new Error("mudanca_no_corpo: o carinho e contato e zera o ticks_desde_cuidado");
    this.tickUltimoCuidado = tick;
    if (this.ultima === null) return;
    const cc = this.ccCorpo;
    if (cc === null) throw new Error("mudanca_no_corpo: decisao creditada sem a ConfigConsequencia do corpo");
    const f = sinalCorpo(antes.corpo, depois.corpo, this.drivesCorpo(cc), cc.ganho, this.escala, cc.pesosDrivesCorpo);
    this.recompensas.carinho = (this.recompensas.carinho ?? 0) + 1;
    if (f !== 0) this.creditar(this.ultima, f);
  }

  // ------------------------------------------------------------- serializacao
  private static registroDict(r: RegistroLobos | null) {
    if (r === null) return null;
    return { regra: r.regra, candidatos: [...r.candidatos], acao: r.acao, X: [...r.X], P: { ...r.P }, W: { ...r.W },
      ...(r.corpo !== undefined ? { corpo: { X: [...r.corpo.X] } } : {}) };
  }

  /** Aprendiz._estado_aprendizado (sem os chamados pendentes, que so a fonte dono tem: sempre vazios) */
  estadoAprendizado() {
    if (!this.aprende) throw new Error("estado do aprendizado com o aprendizado desligado");
    return {
      passo: this.ap.passo, teto: this.ap.teto, piso_peso: this.ap.piso, n_atualizacoes: this.nAtualizacoes, cortes_teto: this.cortesTeto,
      recompensas: { ...this.recompensas }, desvio_maximo: this.desvioMaximo(), pesos_no_teto: this.pesosNoTeto(),
      tick_ultimo_cuidado: this.tickUltimoCuidado, tick_ultima_decisao: this.tickUltimaDecisao, pendentes: [] as never[],
      ultima: CerebroA.registroDict(this.ultima),
      ...(this.corpoPendente !== null ? { corpo_pendente: CerebroA.registroDict(this.corpoPendente.registro) } : {}),
    };
  }

  /** o que o painel e o teste leem do estado interno do Python: os pesos, o prior, as entradas do corpo, a memoria e emocao e os canais */
  estadoInterno() {
    return {
      pesos: copiar(this.pesos), pesos_prior: copiar(this.prior), memoria_emocao: this.memoria.paraDict(), n_decisoes: this.motivos.length,
      ...(this.aprende ? { aprendizado: this.estadoAprendizado() } : {}),
      ...(this.temCorpo ? { corpo: { receptores_novos: [...this.receptoresNovos], canais_novos: [...this.canaisNovos] } } : {}),
      ...(this.receptoresNovos.length ? { pesos_corpo: copiar(this.pesosCorpo) } : {}),
      ...(this.canais !== null ? { canais: { creditos: this.canais.creditos, por_canal: { ...this.canais.por_canal },
        por_alvo: { ...this.canais.por_alvo } } } : {}),
    };
  }
}

// ================================================================== o braco do v11
/** a PoliticaDoBraco do P1-c-tapa (experiments/bancada/bracos.py), o pet v11: o cerebro com a fonte "consequencia" na frente. O sinal
 *  da propria acao sai em `observar` (o N3 da transicao, conferido pelo cerebro, que credita pelo corpo); do dono, so o tapa chega ao
 *  cerebro (o sinal direto, CD-10); o carinho chega pelo corpo (`mudancaNoCorpo`). Nao consome rng nem muda a ordem de nada */
export class BracoConsequencia {
  readonly cerebro: CerebroA;
  readonly cc: ConfigConsequenciaWeb;
  /** as decisoes com o N3 da transicao != 0 e os sinais do dono que chegaram ao cerebro (os tapas) */
  consequencias = 0;
  sinaisEntregues = 0;

  constructor(cerebro: CerebroA, cc: ConfigConsequenciaWeb) {
    if (!cerebro.aprende) throw new Error("o braco da consequencia e de um cerebro que aprende");
    this.cerebro = cerebro;
    this.cc = cc;
  }

  agir(obs: ObservacaoLobos, rng: RngCerebro): AcaoPet { return this.cerebro.agir(obs, rng); }

  observar(t: TransicaoLobos): void {
    const fS = sinalHomeostatico(t, this.cerebro.escala, this.cc);
    if (fS !== 0) this.consequencias += 1;
    this.cerebro.observarConsequencia(t, fS, this.cc);
  }

  receberAcaoDono(acao: string, tick: number): void {
    if (acao !== VALOR_TAPA_LOBOS) return;                 // o resto do dono nao chega na fonte consequencia
    this.sinaisEntregues += 1;
    this.cerebro.receberAcaoDono(acao, tick);
  }

  mudancaNoCorpo(antes: ObservacaoLobos, depois: ObservacaoLobos): void { this.cerebro.mudancaNoCorpo(antes, depois); }

  consequenciaCorpo(acao: AcaoPet, ocorrido: OcorridoCorpo, obsDepois: ObservacaoLobos): void {
    this.cerebro.consequenciaCorpo(acao, ocorrido, obsDepois);
  }
}
