/* O cerebro A em TS (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapas 2 e 3): o nucleo de digilab/policies/lobos.py sem aprender (L0,
   etapa 2) e o aprendizado do v11 (etapa 3): a consequencia da propria acao pelos receptores do corpo (corpo.ts, Corpo.receptores())
   e os gestos do dono, o tapa (o sinal direto) e o carinho (so pelo corpo). So o motor e a paridade; nenhuma tela e nenhuma versao de
   pet nova (o v11 e a etapa 4).

   Os quatro lobos, como no Python:
     PERCEPCAO        Observacao -> x = (1, Estado.vetor, min(1, ticks sem cuidado / escala)), os floats que o instinto le; com o corpo,
                      mais as leituras dos receptores novos / S, so nas regras de tempo livre (uma tabela de pesos a parte, prior 0);
     MEMORIA/EMOCAO   contribuicao zero em toda decisao; so conta as decisoes e as acoes do dono (MemoriaEmocao);
     IMPULSOS         as regras do instinto (policy.py, PoliticaInstinto.agir), rodadas com uma rng-sonda que nao consome a rng do
                      motor: a regra que disparou e os candidatos, na ordem do instinto;
     DECISAO          pesos INTEIROS w[regra][acao][entrada] na escala S = 2**bits, no prior do instinto (os coeficientes vezes S).
                      Peso efetivo = sum_j (w_j / S) * x_j, da esquerda para a direita; a acao sai de UMA chamada de rng.random(),
                      pela conta de random.choices(k=1) do CPython (cumulativa, total = ultima + 0.0, bisect_right ate n - 1).

   Com S potencia de dois, w_j / S e exato e o peso efetivo e o mesmo float que o instinto escreve, somado na mesma ordem: a decisao e
   a do instinto, byte a byte (o G-PAR-L0, test/lobos.test.ts contra a secao l0 de test/gabaritos/lobos_python.json). Nenhuma funcao
   transcendental (nada de Math.exp ou Math.log): o Chrome difere do Node so no ultimo bit delas, e o nucleo fica fora disso.

   O aprendizado (Aprendiz e PoliticaLobos do Python, so as chaves do v11) e todo em inteiros na escala S: o registro de cada decisao
   (X, P, W), a regra da L1 (atualizarPesos), o sinal pelo corpo (sinalCorpo, D = soma w_d falta_d^2 sobre os receptores) separado por
   canal (sinalCorpoCanais, a soma telescopica do contrato K-6), o tapa (recompensa_tapa x S, a ultima decisao) e o carinho (o sinalCorpo
   dos receptores antes e depois dele, a ultima decisao). As chaves que o v11 nao tem (o traco, os pesos da janela, o elogio e a bronca,
   o mundo, as frutas, o banheiro, o paladar, o plano) falham alto em vez de virar um caminho sem gabarito.

   O motivo de cada decisao usa os nomes em snake_case do Python de proposito: e o mesmo dado de `_registrar`, conferido campo a campo;
   o estadoInterno() tambem, e o do estado_interno do Python. */
import { C, CLB, type ConfigCorpo } from "./constantes.ts";
import { VALOR_TAPA } from "./corpo.ts";
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

// ================================================================== os nomes do corpo e do sinal (lobos.py)
/** os receptores de hoje (a leitura e S - falta), na ordem de Estado.vetor: o nome do receptor pelo indice do drive */
export const RECEPTORES_HOJE = ["fome", "higiene", "energia", "humor", "saude"] as const;
/** os receptores novos (a leitura e a falta; na dor e no susto, a concentracao), na ordem do Python */
export const RECEPTORES_NOVOS = ["tedio", "curiosidade", "solidao", "estresse", "dor", "susto", "vontade", "conforto"] as const;
/** os drives novos do sinal (o susto fica fora, TAREFA_V2_CORPO_DRIVES, secao 9) */
export const DRIVES_NOVOS_SINAL = ["tedio", "curiosidade", "solidao", "estresse", "dor", "vontade", "conforto"] as const;
/** BN-6: o receptor do conforto le a concentracao; a falta e S - leitura */
export const RECEPTORES_FALTA_INVERTIDA = ["conforto"] as const;
/** as regras que leem as entradas do corpo (as de tempo livre; sem o mundo, so `tempo_livre`) */
export const REGRAS_ENTRADAS_CORPO = ["tempo_livre", "bola_no_cenario", "fruta_no_cenario"] as const;
/** CANAIS-REFORCO: o grupo de pesos que cada canal credita; os canais novos vao todos ao corpo (a tabela do lobo de decisao) */
export const ALVOS_CANAIS = ["corpo", "fruta"] as const;
export type AlvoCanal = (typeof ALVOS_CANAIS)[number];
export const ROTA_CANAIS: Readonly<Record<string, AlvoCanal>> = { fome: "corpo", higiene: "corpo", energia: "corpo", humor: "fruta" };
export const ROTA_CANAIS_CORPO: Readonly<Record<string, AlvoCanal>> = Object.fromEntries(DRIVES_NOVOS_SINAL.map(d => [d, "corpo"]));
/** as acoes do dono que sao cuidado e as que sao feedback (lobos.CUIDADOS, lobos.FEEDBACK), pelo valor do AcaoUsuario */
export const CUIDADOS: readonly string[] = ["alimentar", "limpar", "brincar", "acariciar", "petisco", "levar_ao_banheiro", "tratar_lesao"];
export const FEEDBACK: readonly string[] = ["elogiar", "repreender"];

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

// ================================================================== a conta inteira do aprendizado
/** arred: o inteiro mais proximo, meio longe do zero (o int(x + 0.5) do Python), sem o -0 do JS */
export function arred(x: number): number {
  if (x >= 0.0) return Math.trunc(x + 0.5);
  const q = Math.trunc(-x + 0.5);
  return q === 0 ? 0 : -q;
}

/** o produto inteiro, e so se for exato no double (o Python nao tem teto; aqui, passar de 2^53 falha alto) */
function produtoExato(...fatores: number[]): number {
  let p = 1;
  for (const f of fatores) p *= f;
  if (!Number.isSafeInteger(p)) throw new Error(`conta inteira fora de 2^53: ${fatores.join(" x ")}`);
  return p;
}

/** o registro de uma decisao para o credito (Aprendiz._registrar): a regra, os candidatos, a acao, X = arred(x S), P = arred(p S) e
 *  W = max(1, arred(peso S)); com o corpo, o X das entradas do corpo */
export interface RegistroDecisao {
  regra: RegraLobos; candidatos: AcaoPet[]; acao: AcaoPet; X: number[];
  P: Partial<Record<AcaoPet, number>>; W: Partial<Record<AcaoPet, number>>; corpo?: { X: number[] };
}

/** a regra da L1 na tabela de uma regra: dw[a][j] = div_arred(f_S passo X_j (S 1[a=a*] - P_a), S S W_a), cortado em prior +- teto.
 *  Devolve quantos cortes no teto */
export function atualizarPesos(pesos: Partial<Record<AcaoPet, number[]>>, prior: Partial<Record<AcaoPet, number[]>>,
  registro: Pick<RegistroDecisao, "candidatos" | "acao" | "X" | "P" | "W">, fS: number, passo: number, teto: number, S: number): number {
  let cortes = 0;
  for (const a of registro.candidatos) {
    const fator = (a === registro.acao ? S : 0) - registro.P[a]!;
    if (fator === 0) continue;
    const w = pesos[a]!, w0 = prior[a]!;
    const denominador = produtoExato(S, S, registro.W[a]!);
    registro.X.forEach((X, j) => {
      if (X === 0) return;
      const delta = divArred(produtoExato(fS, passo, X, fator), denominador);
      if (delta === 0) return;
      let novo = w[j] + delta;
      if (novo > w0[j] + teto) { novo = w0[j] + teto; cortes += 1; }
      else if (novo < w0[j] - teto) { novo = w0[j] - teto; cortes += 1; }
      w[j] = novo;
    });
  }
  return cortes;
}

/** os receptores do corpo na escala S, o que Corpo.receptores() devolve (corpo.ts) */
export type ReceptoresCorpo = Readonly<Record<string, number>>;
/** a observacao com os receptores do corpo: o que o cerebro com a chave do corpo le */
export interface ObservacaoLobos extends Observacao { corpo?: ReceptoresCorpo }
/** a transicao de uma decisao (a do engine: a observacao da decisao e a seguinte, sem os estimulos do corpo) */
export interface TransicaoLobos { observacao: ObservacaoLobos; acao: AcaoPet; observacaoSeguinte: ObservacaoLobos }

/** a ConfigConsequencia do Python, com os nomes dele (o sinal da consequencia: o N3, os canais e o corpo) */
export interface ConfigConsequenciaLobos {
  drives: readonly number[]; ganho: number; humor_na_fruta: boolean; canais_ligados: boolean; pesos_janela: boolean;
  janela_pesos: number; pesos_drives_corpo: readonly (readonly [string, number])[]; ganho_gosto: number;
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

/** o f_S do N3 sobre a transicao do engine: div_arred(ganho (D(antes) - D(depois)), S). Os pesos da janela (A2.4) nao existem no TS */
export function sinalHomeostatico(t: TransicaoLobos, S: number, cc: ConfigConsequenciaLobos): number {
  if (!Number.isInteger(cc.ganho) || cc.ganho < 0) throw new Error(`ganho precisa ser inteiro >= 0: ${cc.ganho}`);
  if (cc.pesos_janela) throw new Error("pesos_janela (A2.4) nao existe no TS: o v11 nao tem a janela");
  const antes = deficitHomeostatico(t.observacao.v, cc.drives, S);
  const depois = deficitHomeostatico(t.observacaoSeguinte.v, cc.drives, S);
  return divArred(produtoExato(cc.ganho, antes - depois), S);
}

/** os receptores novos que o corpo tem com estas chaves (lobos.receptores_novos), na ordem de RECEPTORES_NOVOS. O banheiro nao existe
 *  no cerebro do TS */
export function receptoresNovos(cc: ConfigCorpo, mundoFisico: boolean): string[] {
  if (cc.banheiro) throw new Error("o banheiro nao existe no cerebro do TS");
  const tem = new Set<string>();
  if (cc.drives_novos) for (const r of ["tedio", "solidao", "estresse", ...(mundoFisico ? ["curiosidade"] : [])]) tem.add(r);
  if (cc.gestos) for (const r of ["dor", "susto"]) tem.add(r);
  return RECEPTORES_NOVOS.filter(r => tem.has(r));
}

/** a leitura do receptor `nome` (inteiro em [0, S]); um receptor que o corpo nao tem, ou fora da escala, falha alto */
export function leituraReceptor(pc: ReceptoresCorpo, nome: string, S: number): number {
  const v = pc[nome];
  if (v === undefined) throw new Error(`corpo: o receptor ${nome} nao existe nesta Observacao.corpo`);
  if (!Number.isInteger(v) || v < 0 || v > S) throw new Error(`corpo: receptor ${nome} fora de inteiros em [0, ${S}]: ${v}`);
  return v;
}

/** a falta na escala S: S - leitura nos drives de hoje e no conforto, a propria leitura nos novos */
export function faltaReceptor(pc: ReceptoresCorpo, nome: string, S: number): number {
  const v = leituraReceptor(pc, nome, S);
  if ((RECEPTORES_HOJE as readonly string[]).includes(nome) || (RECEPTORES_FALTA_INVERTIDA as readonly string[]).includes(nome)) return S - v;
  if ((RECEPTORES_NOVOS as readonly string[]).includes(nome)) return v;
  throw new Error(`receptor desconhecido: ${nome}`);
}

/** c_d = w_d (falta_d(antes)^2 - falta_d(depois)^2) por drive, na ordem de `drives` (sem os pesos da janela: o v11 nao os tem) */
export function contribuicoesCorpo(antes: ReceptoresCorpo, depois: ReceptoresCorpo, drives: readonly string[], S: number,
  pesosDrives: Readonly<Record<string, number>>): Record<string, number> {
  const c: Record<string, number> = {};
  for (const d of drives) {
    const fa = faltaReceptor(antes, d, S), fd = faltaReceptor(depois, d, S);
    const wd = pesosDrives[d];
    if (!Number.isInteger(wd) || wd < 0) throw new Error(`w_d do drive ${d} precisa ser inteiro >= 0: ${wd}`);
    c[d] = produtoExato(wd, fa * fa - fd * fd);
  }
  return c;
}

/** f_S = div_arred(ganho (D(antes) - D(depois)), S), D = soma_d w_d falta_d^2 sobre os receptores */
export function sinalCorpo(antes: ReceptoresCorpo, depois: ReceptoresCorpo, drives: readonly string[], ganho: number, S: number,
  pesosDrives: Readonly<Record<string, number>>): number {
  if (!Number.isInteger(ganho) || ganho < 0) throw new Error(`ganho precisa ser inteiro >= 0: ${ganho}`);
  const c = contribuicoesCorpo(antes, depois, drives, S, pesosDrives);
  let total = 0;
  for (const d of drives) total += c[d];
  return divArred(produtoExato(ganho, total), S);
}

/** sinalCorpo separado por canal, um por drive, pela soma telescopica: a soma dos canais e o escalar (contrato K-6) */
export function sinalCorpoCanais(antes: ReceptoresCorpo, depois: ReceptoresCorpo, drives: readonly string[], ganho: number, S: number,
  pesosDrives: Readonly<Record<string, number>>): Record<string, number> {
  if (!Number.isInteger(ganho) || ganho < 0) throw new Error(`ganho precisa ser inteiro >= 0: ${ganho}`);
  const c = contribuicoesCorpo(antes, depois, drives, S, pesosDrives);
  const canais: Record<string, number> = {};
  let acumulado = 0, anterior = 0;
  for (const d of drives) {
    if (!(d in ROTA_CANAIS) && !(d in ROTA_CANAIS_CORPO)) throw new Error(`drive ${d} sem canal`);
    acumulado += c[d];
    const parcial = divArred(produtoExato(ganho, acumulado), S);
    canais[d] = parcial - anterior;
    anterior = parcial;
  }
  return canais;
}

/** o lobo de memoria e emocao: sem efeito na decisao (contribuicao zero); so conta o que passou por ele */
export class MemoriaEmocao {
  elogios = 0; broncas = 0; cuidados = 0; outrasAcoesDono = 0; decisoes = 0;
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
/** os termos do peso efetivo de cada candidato: impulsos (o prior), decisao (os pesos menos o prior, mais as entradas do corpo),
 *  memoria_emocao (zero) e piso (o que falta ate o piso, so com o aprendizado), nesta ordem, a do Python */
export type Contribuicoes = Record<"impulsos" | "decisao" | "memoria_emocao" | "piso", Partial<Record<AcaoPet, number>>>;

/** o motivo de uma decisao, os campos de Aprendiz._registrar e os do corpo de PoliticaLobos.agir; `aprendido` e null sem o aprendizado.
 *  `sinal_corpo` entra depois, no gancho do corpo da mesma decisao */
export interface MotivoLobos {
  n: number; regra: RegraLobos; candidatos: AcaoPet[]; percepcao: Record<EntradaLobos, number>; contribuicoes: Contribuicoes;
  pesos: Partial<Record<AcaoPet, number>>; u: number | null; acao: AcaoPet; lobo_decisivo: Exclude<Lobo, "percepcao">;
  aprendido: Partial<Record<AcaoPet, number[]>> | null;
  percepcao_corpo?: Record<string, number>; aprendido_corpo?: Partial<Record<AcaoPet, number[]>>;
  sinal_corpo?: { f: number; drives: Record<string, number> };
}

/** os parametros do aprendizado (a parte da L1 e do corpo da ConfigLobos do Python), so os que o v11 usa */
export interface ConfigAprendizadoLobos {
  passo: number; teto: number; pisoPeso: number; janelaLatencia: number; recompensaTapa: number; tracoDecisoes: number;
}
export interface ConfigLobosWeb {
  aprendizadoLigado: boolean; bits: number; escalaTdc: number; maxPesos: number; aprendizado?: ConfigAprendizadoLobos;
}

/** a rng que o cerebro consome: uma chamada de random() por decisao com mais de um candidato, e nenhuma nas deterministas */
export interface RngCerebro { random(): number }

/** o que o gancho do corpo diz da decisao: a acao e os estimulos dela (o `ocorrido` do MotorCorpo) */
export interface OcorridoCorpo { acao: string; estimulos: readonly (readonly unknown[])[] }

type TabelaParcial = Partial<Record<string, Partial<Record<AcaoPet, number[]>>>>;
interface CorpoPendente { registro: RegistroDecisao; transicao: TransicaoLobos; cc: ConfigConsequenciaLobos; fruta: null }

/** PoliticaLobos: agir e o motivo (L0, etapa 2) e, com o aprendizado ligado, o credito do v11 (etapa 3): observarConsequencia (a
 *  decisao observada; o credito fica pendente ate o gancho do corpo), consequenciaCorpo (o sinal pelos receptores), receberAcaoDono
 *  (o tapa) e mudancaNoCorpo (o carinho). `cfgCorpo` e a ConfigCorpo do corpo do pet (corpo.ts): o cerebro le so as chaves e a escala */
export class CerebroA {
  readonly escala: number;
  readonly prior: TabelaPesos;
  readonly pesos: TabelaPesos;
  readonly motivos: MotivoLobos[] = [];
  readonly cfg: ConfigLobosWeb;
  readonly memoria = new MemoriaEmocao();
  /* o corpo (null sem a chave): os receptores novos, os canais novos e a tabela das entradas do corpo (prior 0) */
  readonly corpo: ConfigCorpo | null = null;
  readonly receptoresNovos: string[] = [];
  readonly canaisNovos: string[] = [];
  readonly priorCorpo: TabelaParcial = {};
  readonly pesosCorpo: TabelaParcial = {};
  private _ultimaRegra: RegraLobos | null = null;
  private readonly aprende: boolean;
  private readonly piso: number;
  private xCorpo: number[] = [];
  private registroDecisao: RegistroDecisao | null = null;
  private ultima: RegistroDecisao | null = null;
  private acaoSemGancho: AcaoPet | null = null;
  private corpoPendente: CorpoPendente | null = null;
  private ccCorpo: ConfigConsequenciaLobos | null = null;
  private tickUltimoCuidado = 0;
  private readonly tickUltimaDecisao = -1;   // so o `observar` da fonte dono o anda (fora do v11)
  private readonly recompensas: Record<string, number> = { elogio: 0, repreensao: 0, latencia: 0, ignorado: 0 };
  private nAtualizacoes = 0;
  private cortesTeto = 0;
  private canais: { creditos: number; por_canal: Record<string, number>; por_alvo: Record<AlvoCanal, number> } | null = null;

  constructor(cfg: ConfigLobosWeb = { aprendizadoLigado: false, ...CLB }, cfgCorpo: ConfigCorpo | null = null) {
    this.cfg = cfg;
    if (!Number.isInteger(cfg.bits) || cfg.bits < 1) throw new Error("bits_ponto_fixo precisa ser inteiro >= 1");
    this.escala = 2 ** cfg.bits;
    this.prior = tabelaPrior(this.escala);
    this.pesos = Object.fromEntries(REGRAS_LOBOS.map(r => [r, Object.fromEntries(ACOES_LOBOS.map(a => [a, [...this.prior[r][a]]]))])) as TabelaPesos;
    if (this.nPesos() >= cfg.maxPesos) throw new Error(`${this.nPesos()} pesos, teto ${cfg.maxPesos}`);
    this.aprende = cfg.aprendizadoLigado;
    const ca = cfg.aprendizado;
    if (this.aprende) {
      if (ca === undefined) throw new Error("o aprendizado ligado precisa dos parametros da L1 (cfg.aprendizado)");
      for (const nome of ["passo", "teto", "pisoPeso", "janelaLatencia", "tracoDecisoes"] as const) {
        if (!Number.isInteger(ca[nome])) throw new Error(`ConfigLobos.${nome} precisa ser inteiro`);
      }
      if (ca.passo <= 0 || ca.teto <= 0 || ca.pisoPeso <= 0 || ca.janelaLatencia <= 0) {
        throw new Error("passo, teto, piso_peso e janela_latencia_ticks precisam ser positivos");
      }
      if (ca.tracoDecisoes !== 0) throw new Error("o traco de elegibilidade (traco_decisoes > 0) nao existe no TS: o v11 nao tem traco");
    }
    this.piso = (ca?.pisoPeso ?? 0) / this.escala;
    if (cfgCorpo !== null && cfgCorpo.ligada) {
      if (cfgCorpo.escala_receptor !== this.escala) {
        throw new Error(`receptores na escala ${cfgCorpo.escala_receptor}, cerebro na escala ${this.escala}: tem de ser a mesma S`);
      }
      if (cfgCorpo.paladar) throw new Error("o paladar nao existe no cerebro do TS");
      this.corpo = cfgCorpo;
      this.receptoresNovos = receptoresNovos(cfgCorpo, false);
      this.canaisNovos = DRIVES_NOVOS_SINAL.filter(d => this.receptoresNovos.includes(d));
      if (this.receptoresNovos.length) {
        const n = this.receptoresNovos.length;
        for (const r of REGRAS_ENTRADAS_CORPO) {
          if (!(REGRAS_LOBOS as readonly string[]).includes(r)) continue;     // sem o mundo, so o tempo livre tem tabela
          this.priorCorpo[r] = Object.fromEntries(ACOES_LOBOS.map(a => [a, new Array<number>(n).fill(0)]));
          this.pesosCorpo[r] = Object.fromEntries(ACOES_LOBOS.map(a => [a, new Array<number>(n).fill(0)]));
        }
        if (this.nPesos() >= cfg.maxPesos) throw new Error(`${this.nPesos()} pesos, teto ${cfg.maxPesos}`);
      }
    }
  }

  get ultimaRegra(): RegraLobos | null { return this._ultimaRegra; }
  get ultimoMotivo(): MotivoLobos | null { return this.motivos.length ? this.motivos[this.motivos.length - 1] : null; }

  nPesos(): number {
    let n = 0;
    for (const r of REGRAS_LOBOS) for (const a of ACOES_LOBOS) n += this.pesos[r][a].length;
    for (const acoes of Object.values(this.pesosCorpo)) for (const v of Object.values(acoes!)) n += v!.length;
    return n;
  }

  percepcao(obs: Observacao): number[] { return percepcao(obs, this.cfg.escalaTdc); }

  /** Aprendiz._pesos_efetivos, sem as chaves do mundo, das frutas e do plano: (contribuicoes por termo, peso efetivo por candidato) */
  pesosEfetivos(regra: RegraLobos, candidatos: readonly AcaoPet[], x: readonly number[]): { contrib: Contribuicoes; efetivos: Partial<Record<AcaoPet, number>> } {
    const S = this.escala, prior = this.prior[regra], pesos = this.pesos[regra];
    const contrib: Contribuicoes = { impulsos: {}, decisao: {}, memoria_emocao: {}, piso: {} };
    for (const a of candidatos) contrib.impulsos[a] = ativacao(prior[a], x, S);
    for (const a of candidatos) contrib.decisao[a] = ativacao(pesos[a].map((w, j) => w - prior[a][j]), x, S);
    for (const a of candidatos) contrib.memoria_emocao[a] = 0.0;
    const tabela = this.pesosCorpo[regra];
    if (tabela !== undefined) for (const a of candidatos) contrib.decisao[a] = contrib.decisao[a]! + ativacao(tabela[a]!, this.xCorpo, S);
    for (const a of candidatos) {
      const soma = contrib.impulsos[a]! + contrib.decisao[a]! + contrib.memoria_emocao[a]!;
      contrib.piso[a] = this.aprende && soma < this.piso ? this.piso - soma : 0.0;
    }
    const efetivos: Partial<Record<AcaoPet, number>> = {};
    for (const a of candidatos) efetivos[a] = contrib.impulsos[a]! + contrib.decisao[a]! + contrib.memoria_emocao[a]! + contrib.piso[a]!;
    return { contrib, efetivos };
  }

  /** PoliticaLobos.agir: a percepcao (e a do corpo), os impulsos, o peso efetivo e o sorteio (uma chamada de rng.random() so com mais
   *  de um candidato), e o motivo e o registro da decisao */
  agir(obs: ObservacaoLobos, rng: RngCerebro): AcaoPet {
    const S = this.escala;
    if (this.corpo !== null) {
      if (this.acaoSemGancho !== null || this.corpoPendente !== null) throw new Error("corpo: a decisao anterior ficou sem o gancho de consequencia");
      const pc = obs.corpo;
      if (pc === undefined) throw new Error("corpo: Observacao sem o campo corpo (o cerebro com a chave do corpo precisa do corpo)");
      this.xCorpo = this.receptoresNovos.map(r => leituraReceptor(pc, r, S) / S);
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
    if (Object.keys(this.pesosCorpo).length) {
      const m = this.motivos[this.motivos.length - 1];
      m.percepcao_corpo = Object.fromEntries(this.receptoresNovos.map((r, j) => [r, this.xCorpo[j]]));
      const tabela = this.pesosCorpo[regra];
      if (tabela !== undefined && this.aprende) {
        m.aprendido_corpo = Object.fromEntries(candidatos.map(a => [a, termos(tabela[a]!, this.xCorpo, S)]));
        this.registroDecisao!.corpo = { X: this.xCorpo.map(v => arred(v * S)) };
      }
    }
    return acao;
  }

  /** Aprendiz._registrar: o registro da decisao (so com o aprendizado) e o motivo. O lobo decisivo e o de maior contribuicao na acao
   *  escolhida entre memoria_emocao, impulsos e decisao; no empate, o primeiro na ordem dos lobos */
  private registrar(regra: RegraLobos, candidatos: AcaoPet[], acao: AcaoPet, x: number[], pesos: Partial<Record<AcaoPet, number>>,
    contrib: Contribuicoes, u: number | null): void {
    let aprendido: Partial<Record<AcaoPet, number[]>> | null = null;
    let registro: RegistroDecisao | null = null;
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

  // ------------------------------------------------------------- o credito
  /** CORPO: cada decisao observada espera UM gancho do corpo antes da proxima */
  private esperarGanchoCorpo(t: TransicaoLobos): void {
    if (this.corpo === null) return;
    if (this.acaoSemGancho !== null) throw new Error(`corpo: a decisao anterior (${this.acaoSemGancho}) ficou sem o gancho de consequencia`);
    if (t.observacao.corpo === undefined || t.observacaoSeguinte.corpo === undefined) throw new Error("corpo: transicao sem Observacao.corpo");
    this.acaoSemGancho = t.acao;
  }

  /** Aprendiz.observar_consequencia com a chave do corpo (o v11): conta a decisao, confere que `fS` e o sinalHomeostatico da transicao
   *  do engine (nao e creditado: o credito espera o gancho do corpo, que le os receptores) e deixa a decisao pendente */
  observarConsequencia(t: TransicaoLobos, fS: number, cc: ConfigConsequenciaLobos): void {
    this.memoria.decisao();
    this.esperarGanchoCorpo(t);
    if (!this.aprende) return;
    const registro = this.registroDecisao;
    if (registro === null || registro.acao !== t.acao) throw new Error("registro da decisao nao corresponde a acao observada");
    this.ultima = registro;
    this.recompensas.consequencia = (this.recompensas.consequencia ?? 0) + 1;
    if (this.corpo === null) throw new Error("a consequencia sem o corpo (o N3 sobre o Estado.vetor) nao existe no TS: o v11 tem o corpo");
    if (fS !== sinalHomeostatico(t, this.escala, cc)) throw new Error("corpo: o f_S recebido nao e o sinal_homeostatico da transicao");
    this.ccCorpo = cc;
    this.corpoPendente = { registro, transicao: t, cc, fruta: null };
  }

  /** Aprendiz.consequencia_corpo, sem o mundo fisico: uma vez por decisao, depois dos estimulos da propria acao; credita o sinalCorpo
   *  pendente (antes = a decisao, depois = `obsDepois`) */
  consequenciaCorpo(acao: AcaoPet, ocorrido: OcorridoCorpo, obsDepois: ObservacaoLobos): void {
    if (this.corpo === null) return;
    const esperada = this.acaoSemGancho;
    this.acaoSemGancho = null;
    if (esperada === null) throw new Error("corpo: gancho de consequencia sem decisao observada (ou a segunda chamada na mesma decisao)");
    if (esperada !== acao || ocorrido.acao !== acao) throw new Error(`corpo: gancho de ${acao} (${ocorrido.acao}) para a decisao observada de ${esperada}`);
    const frutas = ocorrido.estimulos.filter(e => e[0] === "fruta").map(e => e[1]);
    if (frutas.length > 1) throw new Error(`corpo: duas frutas numa decisao ${JSON.stringify(frutas)}`);
    const fruta = frutas.length ? frutas[0] : null;
    /* a fruta pendente so nasce no fruta_comida, que o v11 nao tem: um estimulo de fruta falha alto, como no Python */
    const p = this.corpoPendente;
    if (p !== null && p.fruta !== fruta) throw new Error(`corpo: o estimulo da fruta (${String(fruta)}) nao e a fruta_comida da decisao (${p.fruta})`);
    this.creditarCorpo(obsDepois);
  }

  /** os drives do sinal pelo corpo: os do N3 (cc.drives) pelo nome do receptor e os drives novos que o corpo tem (sem fruta, sem humor) */
  private drivesCorpo(cc: ConfigConsequenciaLobos): string[] {
    return [...cc.drives.map(i => RECEPTORES_HOJE[i]), ...this.canaisNovos];
  }

  /** Aprendiz._creditar_corpo: o sinal da decisao pendente pelos receptores, escalar ou por canal; a conta fica no motivo */
  private creditarCorpo(obsDepois: ObservacaoLobos): void {
    const p = this.corpoPendente;
    this.corpoPendente = null;
    if (p === null) return;
    if (obsDepois.corpo === undefined) throw new Error("corpo: obs_depois sem Observacao.corpo");
    const S = this.escala, cc = p.cc;
    const drives = this.drivesCorpo(cc), pd = Object.fromEntries(cc.pesos_drives_corpo);
    const antes = p.transicao.observacao.corpo!, depois = obsDepois.corpo;
    const contrib = contribuicoesCorpo(antes, depois, drives, S, pd);
    const f = sinalCorpo(antes, depois, drives, cc.ganho, S, pd);
    if (this.motivos.length) this.motivos[this.motivos.length - 1].sinal_corpo = { f, drives: contrib };
    if (cc.canais_ligados) this.creditarCanais(p.registro, sinalCorpoCanais(antes, depois, drives, cc.ganho, S, pd), f);
    else if (f !== 0) this.aplicarSinal(p.registro, f);
  }

  /** contrato K-6: a soma dos canais e o escalar; cada canal vai ao seu grupo de pesos (sem frutas, todos ao corpo) */
  private creditarCanais(registro: RegistroDecisao, canais: Record<string, number>, fS: number): void {
    let total = 0;
    const alvos: Record<AlvoCanal, number> = { corpo: 0, fruta: 0 };
    for (const [canal, f] of Object.entries(canais)) {
      if (!(canal in ROTA_CANAIS) && !this.canaisNovos.includes(canal)) throw new Error(`canal desconhecido: ${canal}`);
      total += f;
      alvos[ROTA_CANAIS[canal] ?? ROTA_CANAIS_CORPO[canal]] += f;
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
    if (alvos.corpo !== 0 || alvos.fruta !== 0) this.aplicarSinal(registro, fS, alvos);
  }

  /** Aprendiz._aplicar_sinal: a regra da L1 na tabela da regra e, com o corpo, nas entradas do corpo (X = as leituras); com `alvos`, o
   *  sinal do canal do corpo */
  private aplicarSinal(registro: RegistroDecisao, fS: number, alvos?: Record<AlvoCanal, number>): void {
    const ca = this.cfg.aprendizado!, S = this.escala, g = registro.regra;
    const fCorpo = alvos === undefined ? fS : alvos.corpo;
    this.cortesTeto += atualizarPesos(this.pesos[g], this.prior[g], registro, fCorpo, ca.passo, ca.teto, S);
    if (registro.corpo !== undefined) {
      this.cortesTeto += atualizarPesos(this.pesosCorpo[g]!, this.priorCorpo[g]!, { ...registro, X: registro.corpo.X }, fCorpo, ca.passo,
        ca.teto, S);
    }
    this.nAtualizacoes += 1;
  }

  /** Aprendiz.receber_acao_dono: o dono passa pela memoria; aprendendo, acerta o relogio do cuidado e o tapa credita a ultima decisao
   *  (recompensa_tapa x S, escalar). O elogio e a bronca nao existem no TS (o v11 nao os tem, PW-1). Os chamados pendentes so nascem no
   *  `observar` da fonte dono, fora do v11: nao ha o que pagar nem o que expirar */
  receberAcaoDono(acao: string, tick: number): void {
    this.memoria.acaoDono(acao, tick);
    if (!this.aprende) return;
    if (tick < this.tickUltimoCuidado) throw new Error(`acao do dono no passado: ${tick} < ${this.tickUltimoCuidado}`);
    this.tickUltimoCuidado = tick;
    if (FEEDBACK.includes(acao)) throw new Error("o elogio e a bronca nao chegam ao cerebro do v11 (PW-1)");
    if (acao === VALOR_TAPA) {
      if (this.ultima === null) return;
      this.aplicarSinal(this.ultima, arred(this.cfg.aprendizado!.recompensaTapa * this.escala));
      this.recompensas.tapa = (this.recompensas.tapa ?? 0) + 1;
    }
  }

  /** Aprendiz.mudanca_no_corpo: o carinho chega so pelo corpo, sem dizer que gesto foi. E cuidado (acerta o relogio; o instante e o
   *  ticks_desde_cuidado de antes) e credita a ultima decisao com o sinalCorpo dos receptores antes e depois dele (sem o humor) */
  mudancaNoCorpo(antes: ObservacaoLobos, depois: ObservacaoLobos): void {
    const tick = this.tickUltimoCuidado + antes.tdc;
    this.memoria.acaoDono("acariciar", tick);
    if (!this.aprende) return;
    if (this.corpo === null) throw new Error("mudanca_no_corpo num cerebro que aprende sem a chave do corpo");
    if (antes.corpo === undefined || depois.corpo === undefined) throw new Error("mudanca_no_corpo sem Observacao.corpo");
    if (depois.tdc !== 0) throw new Error("mudanca_no_corpo: o carinho e contato e zera o ticks_desde_cuidado");
    this.tickUltimoCuidado = tick;
    if (this.ultima === null) return;
    const cc = this.ccCorpo;
    if (cc === null) throw new Error("mudanca_no_corpo: a ConfigConsequencia da ultima decisao nao chegou");
    const f = sinalCorpo(antes.corpo, depois.corpo, this.drivesCorpo(cc), cc.ganho, this.escala, Object.fromEntries(cc.pesos_drives_corpo));
    this.recompensas.carinho = (this.recompensas.carinho ?? 0) + 1;
    if (f !== 0) this.aplicarSinal(this.ultima, f);
  }

  // ------------------------------------------------------------- serializacao
  /** |w - w0| de cada peso, da tabela da decisao e das entradas do corpo */
  private desvios(): number[] {
    const d: number[] = [];
    for (const r of REGRAS_LOBOS) for (const a of ACOES_LOBOS) this.pesos[r][a].forEach((w, j) => d.push(Math.abs(w - this.prior[r][a][j])));
    for (const [r, acoes] of Object.entries(this.pesosCorpo)) for (const [a, v] of Object.entries(acoes!)) {
      const v0 = this.priorCorpo[r]![a as AcaoPet]!;
      v!.forEach((w, j) => d.push(Math.abs(w - v0[j])));
    }
    return d;
  }

  private static registroDict(r: RegistroDecisao | null) {
    if (r === null) return null;
    return { regra: r.regra, candidatos: [...r.candidatos], acao: r.acao, X: [...r.X], P: { ...r.P }, W: { ...r.W },
      ...(r.corpo !== undefined ? { corpo: { X: [...r.corpo.X] } } : {}) };
  }

  /** Aprendiz.estado_interno, com os nomes do Python: o que o painel e o save vao ler (e o que o sha256 do gabarito resume) */
  estadoInterno() {
    const ca = this.cfg.aprendizado;
    const desvios = this.desvios();
    const copia = (t: TabelaParcial) => Object.fromEntries(Object.entries(t).map(([r, acoes]) =>
      [r, Object.fromEntries(Object.entries(acoes!).map(([a, v]) => [a, [...v!]]))]));
    return {
      nome: "lobos", parametros_aprendidos: this.nPesos(), aprendizado_ligado: this.aprende, escala: this.escala,
      entradas: [...ENTRADAS_LOBOS], pesos: copia(this.pesos), pesos_prior: copia(this.prior), memoria_emocao: this.memoria.paraDict(),
      n_decisoes: this.motivos.length, motivos: this.motivos.map(m => ({ ...m })),
      aprendizado: {
        passo: ca?.passo ?? null, teto: ca?.teto ?? null, piso_peso: ca?.pisoPeso ?? null, n_atualizacoes: this.nAtualizacoes,
        cortes_teto: this.cortesTeto, recompensas: { ...this.recompensas }, desvio_maximo: Math.max(...desvios),
        pesos_no_teto: desvios.filter(d => d === ca?.teto).length, tick_ultimo_cuidado: this.tickUltimoCuidado,
        tick_ultima_decisao: this.tickUltimaDecisao, pendentes: [] as unknown[], ultima: CerebroA.registroDict(this.ultima),
        ...(this.corpoPendente !== null ? { corpo_pendente: CerebroA.registroDict(this.corpoPendente.registro) } : {}),
      },
      ...(this.corpo !== null ? { corpo: { receptores_novos: [...this.receptoresNovos], canais_novos: [...this.canaisNovos] } } : {}),
      ...(Object.keys(this.pesosCorpo).length ? { pesos_corpo: copia(this.pesosCorpo) } : {}),
      ...(this.canais !== null ? { canais: { creditos: this.canais.creditos, por_canal: { ...this.canais.por_canal },
        por_alvo: { ...this.canais.por_alvo } } } : {}),
    };
  }
}
