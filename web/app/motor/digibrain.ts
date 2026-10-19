/* A leitura do painel DigiBrain dos pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 4 e etapa 5): o espelho de
   digilab/painel_digibrain.py, com paridade bit a bit pelo gabarito (test/gabaritos/painel_digibrain_python.json). A tela nao calcula
   nada: as barras por lobo, a percepcao, as chances, a sonda "quem decidiu" e o "o que aprendeu" saem daqui. Leituras puras do motivo
   e do desvio aprendido: nao mudam peso, motivo, memoria nem rng. */
import { ACOES_LOBOS, ENTRADAS_LOBOS, sortear, type MotivoLobos } from "./lobos.ts";
import type { AcaoPet } from "./tipos.ts";

/** quantas entradas a percepcao lista e quantas acoes o "o que aprendeu" lista (N_PERCEPCAO, N_APRENDIDO; so apresentacao) */
export const N_PERCEPCAO = 3, N_APRENDIDO = 3;
export const LOBOS_BARRAS = ["impulsos", "decisao", "corpo", "memoria_emocao", "piso"] as const;
export type LoboBarra = (typeof LOBOS_BARRAS)[number];

/** a leitura de uma decisao para o painel */
export interface LeituraDecisao {
  n: number; regra: MotivoLobos["regra"]; acao: AcaoPet;
  /** a contribuicao de cada lobo na acao escolhida / o peso efetivo dela; o aprendido (decisao) e o corpo podem ser negativos */
  barras: Record<LoboBarra, number>;
  /** os candidatos na ordem do sorteio, com o peso efetivo / a soma */
  chances: { acao: AcaoPet; chance: number }[];
  /** a sonda contrafactual (V3-1 da auditoria E0): o sorteio so com os impulsos e o mesmo u */
  quem_decidiu: { escolha: boolean; acao_instinto: AcaoPet; mudou: boolean };
  /** as entradas de maior |w.x| na acao escolhida (PW-5), sem o vies e sem termo zero */
  percepcao: { entrada: string; x: number; termo: number }[];
}

/** da esquerda para a direita a partir de 0.0, como `ativacao` */
function soma(valores: readonly number[]): number {
  let acumulado = 0.0;
  for (const v of valores) acumulado = acumulado + v;
  return acumulado;
}

/** leitura_decisao: `priorLinha` e a linha do prior da regra e da acao escolhida (inteiros na escala S, na ordem de ENTRADAS_LOBOS);
 *  `receptores` sao os receptores novos do cerebro, na ordem de `aprendido_corpo` (vazio sem o corpo) */
export function leituraDecisao(motivo: MotivoLobos, priorLinha: readonly number[], S: number, receptores: readonly string[],
  nPercepcao: number = N_PERCEPCAO): LeituraDecisao {
  const a = motivo.acao, cand = motivo.candidatos, c = motivo.contribuicoes;
  if (!cand.includes(a)) throw new Error(`acao ${a} fora dos candidatos ${cand}`);
  if (priorLinha.length !== ENTRADAS_LOBOS.length) throw new Error(`linha do prior com ${priorLinha.length} pesos, esperados ${ENTRADAS_LOBOS.length}`);
  const efetivo = motivo.pesos[a]!;
  if (!(efetivo > 0.0)) throw new Error(`peso efetivo nao positivo na acao escolhida: ${efetivo}`);
  const aprendido = motivo.aprendido, aprendidoCorpo = motivo.aprendido_corpo;
  let decisao: number, corpo: number;
  if (aprendido === null) {
    if (aprendidoCorpo !== undefined) throw new Error("aprendido do corpo sem o aprendido");
    decisao = c.decisao[a]!; corpo = 0.0;
  } else {
    decisao = soma(aprendido[a]!);
    corpo = aprendidoCorpo === undefined ? 0.0 : soma(aprendidoCorpo[a]!);
    if (decisao + corpo !== c.decisao[a]) throw new Error(`a decisao do motivo (${c.decisao[a]}) nao e o aprendido (${decisao}) mais o corpo (${corpo})`);
  }
  const partes: Record<LoboBarra, number> = { impulsos: c.impulsos[a]!, decisao, corpo, memoria_emocao: c.memoria_emocao[a]!, piso: c.piso[a]! };
  const barras = Object.fromEntries(LOBOS_BARRAS.map(l => [l, partes[l] / efetivo])) as Record<LoboBarra, number>;

  const total = soma(cand.map(x => motivo.pesos[x]!));
  const chances = cand.map(x => ({ acao: x, chance: motivo.pesos[x]! / total }));

  let quem: LeituraDecisao["quem_decidiu"];
  if (motivo.u === null) {
    if (cand.length !== 1) throw new Error(`decisao sem u com ${cand.length} candidatos`);
    quem = { escolha: false, acao_instinto: a, mudou: false };
  } else {
    const soImpulsos = cand[sortear(cand.map(x => c.impulsos[x]!), motivo.u)];
    quem = { escolha: true, acao_instinto: soImpulsos, mudou: soImpulsos !== a };
  }

  const x = motivo.percepcao, entradas: [string, number, number][] = [];
  ENTRADAS_LOBOS.forEach((e, j) => {
    if (e === "vies") return;
    let termo = (priorLinha[j] / S) * x[e];
    if (aprendido !== null) termo = termo + aprendido[a]![j];
    entradas.push([e, x[e], termo]);
  });
  if (aprendidoCorpo !== undefined) {
    const xc = motivo.percepcao_corpo!, t = aprendidoCorpo[a]!;
    if (receptores.length !== t.length) throw new Error(`${receptores.length} receptores para ${t.length} termos do corpo`);
    receptores.forEach((r, i) => entradas.push([r, xc[r], t[i]]));
  }
  const ordem = entradas.map((_, k) => k).filter(k => entradas[k][2] !== 0.0)
    .sort((p, q) => { const ap = Math.abs(entradas[p][2]), aq = Math.abs(entradas[q][2]); return ap > aq ? -1 : ap < aq ? 1 : p - q; });
  const percepcao = ordem.slice(0, nPercepcao).map(k => ({ entrada: entradas[k][0], x: entradas[k][1], termo: entradas[k][2] }));

  return { n: motivo.n, regra: motivo.regra, acao: a, barras, chances, quem_decidiu: quem, percepcao };
}

/** leitura_aprendido: as acoes de maior |desvio aprendido|, sem as de desvio zero; no empate, a ordem de ACOES_LOBOS (ACOES_PET_HOJE) */
export function leituraAprendido(desvio: Partial<Record<AcaoPet, number>>, n: number = N_APRENDIDO): { acao: AcaoPet; desvio: number }[] {
  const chaves = Object.keys(desvio) as AcaoPet[];
  const fora = chaves.filter(a => !ACOES_LOBOS.includes(a));
  if (fora.length) throw new Error(`acoes fora de ACOES_PET_HOJE: ${fora}`);
  const acoes = chaves.filter(a => desvio[a] !== 0.0).sort((p, q) => {
    const ap = Math.abs(desvio[p]!), aq = Math.abs(desvio[q]!);
    return ap > aq ? -1 : ap < aq ? 1 : ACOES_LOBOS.indexOf(p) - ACOES_LOBOS.indexOf(q);
  });
  return acoes.slice(0, n).map(a => ({ acao: a, desvio: desvio[a]! }));
}
