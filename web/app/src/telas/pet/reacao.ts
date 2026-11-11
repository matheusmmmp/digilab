/* As reacoes de rosto dos Digimon do estagio crianca (docs/TAREFA_V3_SPRITES_REACOES.md, R-rosto-jogo): o quadro do Idle com so o rosto mudado
   (Triste, Cansado, Carinho, Medo, Envergonhado, Recusa, Doente; `CLIPES_REACOES` em atlas.ts), com um emote por cima. SO VISTA: le o que o motor
   ja tem (humor, energia, saude, lesao) e o que o dono acabou de fazer (acoes.ts), nao escreve no motor, no log nem no save. Sem DOM nas contas.
   Os gatilhos (a tabela da secao 3.3 da tarefa), todos PROPOSTOS e SEM FONTE:
     - Triste: humor baixo, ou o tapa;           - Medo: o tapa repetido (a lesao e o Doente, que ja mostra o corpo mal);
     - Cansado: energia abaixo do limiar do instinto de exaustao (CVB.limEnergia), com o pet acordado;
     - Carinho: acariciar (o botao; o toque no pet usa o mesmo evento);
     - Recusa: alimentar sem fome (a fome acima do limiar em que o instinto come, 0,45);
     - Doente: lesao ou saude baixa;
     - Envergonhado: SEM GATILHO no jogo de hoje (o elogio nao existe nas acoes do dono dos pets v11): o quadro entra no atlas e fica sem ligacao. */
import type { ClipeReacao } from "../../atlas.ts";

export type ReacaoRosto = ClipeReacao;

/** os numeros da vista: ms, limiares na escala 0..1 do corpo, e o movimento em texels. PROPOSTO, SEM FONTE */
export const REACAO = {
  /** a reacao de uma acao do dono dura isto; o Idle vem antes, por `idleMs`, e so depois entra a expressao e o emote */
  eventoMs: 3000, idleMs: 300,
  /** o tapa repetido: `tapasMedo` tapas dentro de `janelaMedoMs` viram Medo */
  tapasMedo: 2, janelaMedoMs: 20000,
  humorBaixo: 0.3, energiaBaixa: 0.25, saudeBaixa: 0.3,
  /** alimentar com a fome do pet acima disto e Recusa (o instinto so come abaixo de 0,45: motor/lobos.ts, fome_moderada) */
  semFome: 0.45,
  /** o movimento: 1 texel inteiro para cima, trocando a cada `bobMs` */
  bobMs: 700, bobTexels: 1,
} as const;

/** o emote de cada reacao (a chave de grades.ts; null = nao tem um proprio: o Carinho usa o coracao do flash do dono e dos coracoes do toque) */
export const EMOTE_DA_REACAO: Readonly<Record<ReacaoRosto, string | null>> = {
  Triste: "lagrima", Cansado: "reticencias", Carinho: null, Medo: "gota", Envergonhado: null, Recusa: "x", Doente: "espiral",
};

/** o que a vista le do pet para decidir a reacao de estado */
export interface EntradaReacao { chave: string; humor: number; energia: number; saude: number; lesionado: boolean; dormindo: boolean }

let evento: { reacao: ReacaoRosto; desde: number; ms: number } | null = null;
let tapas: number[] = [];
let atual: { chave: string; reacao: ReacaoRosto; desde: number } | null = null;

/** o dono fez uma acao agora (acoes.ts, `agir`): vira o evento da reacao, se for uma das que tem. `fome` e a do pet antes da acao */
export function registrarAcaoDono(acao: string, agora: number, fome: number): void {
  if (!Number.isFinite(fome)) throw new Error("registrarAcaoDono: fome nao finita");
  if (acao === "tapa") {
    tapas = [...tapas.filter(t => agora - t < REACAO.janelaMedoMs), agora];
    evento = { reacao: tapas.length >= REACAO.tapasMedo ? "Medo" : "Triste", desde: agora, ms: REACAO.eventoMs };
  } else if (acao === "acariciar") evento = { reacao: "Carinho", desde: agora, ms: REACAO.eventoMs };
  else if (acao === "alimentar" && fome > REACAO.semFome) evento = { reacao: "Recusa", desde: agora, ms: REACAO.eventoMs };
}
/** um momento do pet que pede um rosto (momentos.ts, HR1: o Cansado ao acordar, o Triste do chamado perdido, a Recusa da fruta podre), por `ms` */
export function registrarMomentoRosto(r: ReacaoRosto, agora: number, ms: number): void {
  if (!(ms > 0) || !Number.isFinite(ms)) throw new Error("registrarMomentoRosto: ms invalido");
  evento = { reacao: r, desde: agora, ms };
}

/** a reacao de agora, ou null: o evento do dono (por eventoMs), senao o estado do corpo (Doente, Triste, Cansado, nesta ordem). `mostrar` so fica
    verdadeiro depois de `idleMs` do inicio dela: antes, o pet segue no Idle (o Idle, depois a expressao). Dormindo, nenhuma */
export function escolherReacao(e: EntradaReacao, agora: number): { reacao: ReacaoRosto; mostrar: boolean } | null {
  for (const k of ["humor", "energia", "saude"] as const) if (!Number.isFinite(e[k])) throw new Error(`escolherReacao: ${k} nao finito`);
  let r: ReacaoRosto | null = null, desde = agora;
  if (e.dormindo) { atual = null; return null; }
  if (evento && agora >= evento.desde && agora - evento.desde < evento.ms) { r = evento.reacao; desde = evento.desde; }
  else if (e.lesionado || e.saude < REACAO.saudeBaixa) r = "Doente";
  else if (e.humor < REACAO.humorBaixo) r = "Triste";
  else if (e.energia < REACAO.energiaBaixa) r = "Cansado";
  if (r === null) { atual = null; return null; }
  if (!atual || atual.chave !== e.chave || atual.reacao !== r) atual = { chave: e.chave, reacao: r, desde };
  return { reacao: r, mostrar: agora - atual.desde >= REACAO.idleMs };
}

/** o movimento da reacao: 1 texel inteiro, subindo e descendo a cada bobMs; com movimento reduzido, nenhum */
export const bobDaReacao = (agora: number, reduzido: boolean): number =>
  reduzido ? 0 : (Math.floor(agora / REACAO.bobMs) % 2) * REACAO.bobTexels;

/** o clipe de reacao no corpo agora (a ilha marca a cada quadro; o e2e le por window.__digilab.reacaoRosto) e o emote dele, para a vista pintar */
let noCorpo: ReacaoRosto | null = null;
export const marcarReacaoRosto = (r: ReacaoRosto | null): void => { noCorpo = r; };
export const reacaoRostoAgora = (): ReacaoRosto | null => noCorpo;
/** o emote da reacao que esta no corpo (null sem reacao ou sem emote proprio) */
export const emoteDaReacaoAgora = (): string | null => (noCorpo ? EMOTE_DA_REACAO[noCorpo] : null);

/** so para os testes */
export function esquecerReacaoRosto(): void { evento = null; tapas = []; atual = null; noCorpo = null; }
