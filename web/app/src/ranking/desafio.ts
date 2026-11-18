/* MMO6, o desafio do dia (docs/PLANO_V3_MMO.md, secao 6; MMO-10 e MMO-11 APROVADAS em 2026-11-11): a Fabrica do dia como conta pura, fora do
   motor. Do registro da tentativa (a escolha, as sementes das lutas e as trocas) e da semente do dia, a tentativa refeita pelo motor
   (TentativaFabrica.doDia) e o resultado dela; e o desempate da tabela do dia. O servidor (servidor_web/src/desafio/) roda esta mesma conta no
   Node; o cliente vai usa-la para a previa (a tela e depois da prancha).

   O registro: { v, escolha, lutas, trocas }
     - v: a versao das regras da Fabrica (VERSOES_FABRICA; so a de hoje);
     - escolha: o alugado (0 a 2) entre os 3 da semente do dia;
     - lutas: as sementes das lutas jogadas, na ordem (as que o servidor entregou a conta);
     - trocas: depois de quais vitorias (o indice k da luta) o alugado virou o rival derrotado, em ordem crescente.
   Nada mais: a pontuacao nunca vem do cliente.

   A pontuacao (secao 6): as lutas vencidas seguidas na tentativa. O desempate: 1) mais vitorias; 2) mais vida no fim da ultima luta vencida
   (a vida inteira do alugado, a do nucleo da luta; D-CONTA da MMO6); 3) quem terminou primeiro, pela hora do servidor. */
import { ALUGUEIS_FABRICA, TentativaFabrica, VERSOES_FABRICA } from "../../motor/index.ts";

export interface RegistroDesafio { v: number; escolha: number; lutas: number[]; trocas: number[] }
/** o resultado de uma tentativa do dia, refeita */
export interface ResultadoDesafio {
  /** as lutas vencidas (seguidas: a tentativa para na primeira derrota) */
  vitorias: number;
  /** as series de 3 vencidas */
  series: number;
  /** as lutas jogadas */
  lutas: number;
  /** perdeu (ou empatou) a ultima: a tentativa acabou */
  acabou: boolean;
  /** a vida (inteira) do alugado no fim da ultima luta vencida; 0 sem vitoria */
  vidaUltimaVitoria: number;
}

export class RegistroMalformado extends Error {}

const objeto = (x: unknown): x is Record<string, unknown> => typeof x === "object" && x !== null && !Array.isArray(x);
const u32 = (x: unknown): boolean => Number.isInteger(x) && (x as number) >= 0 && (x as number) <= 0xffffffff;

/** confere a forma do registro; o que falta, sobra ou tem o tipo errado levanta RegistroMalformado */
export function lerRegistroDesafio(d: unknown): RegistroDesafio {
  if (!objeto(d)) throw new RegistroMalformado("o registro é um objeto {v, escolha, lutas, trocas}");
  const extra = Object.keys(d).filter(k => !["v", "escolha", "lutas", "trocas"].includes(k));
  if (extra.length) throw new RegistroMalformado(`campo desconhecido no registro: ${extra.join(", ")} (a pontuação não vem do cliente)`);
  if (!Number.isSafeInteger(d.v)) throw new RegistroMalformado("'v' é a versão das regras da Fábrica, um inteiro");
  if (!Number.isInteger(d.escolha) || (d.escolha as number) < 0 || (d.escolha as number) >= ALUGUEIS_FABRICA)
    throw new RegistroMalformado(`'escolha' é o alugado, de 0 a ${ALUGUEIS_FABRICA - 1}`);
  if (!Array.isArray(d.lutas) || !d.lutas.every(u32)) throw new RegistroMalformado("'lutas' é a lista das sementes das lutas (inteiros sem sinal de 32 bits)");
  if (!Array.isArray(d.trocas) || !d.trocas.every(k => Number.isInteger(k) && k >= 0))
    throw new RegistroMalformado("'trocas' é a lista dos índices das vitórias depois das quais o alugado foi trocado");
  const trocas = d.trocas as number[];
  if (trocas.some((k, i) => i > 0 && k <= trocas[i - 1])) throw new RegistroMalformado("'trocas' vai em ordem crescente, sem repetir");
  return { v: d.v as number, escolha: d.escolha as number, lutas: [...d.lutas as number[]], trocas: [...trocas] };
}

/** refaz a tentativa do dia pelo motor: as regras de r.v, a semente do dia e as sementes das lutas do registro. Levanta o erro do motor
    quando o registro e impossivel (a luta depois da derrota, a troca sem vitoria, a versao desconhecida) */
export function refazerDesafio(sementeDia: number, r: RegistroDesafio): { tentativa: TentativaFabrica; resultado: ResultadoDesafio } {
  if (!VERSOES_FABRICA.includes(r.v)) throw new Error(`versão das regras da Fábrica desconhecida: ${r.v} (o servidor confere a ${VERSOES_FABRICA.join(", ")})`);
  const t = TentativaFabrica.doDia(r.escolha, sementeDia, r.lutas, r.v), trocas = new Set(r.trocas);
  const ultimaTroca = r.trocas.length ? r.trocas[r.trocas.length - 1] : -1;
  if (ultimaTroca >= r.lutas.length) throw new Error(`troca depois da luta ${ultimaTroca}, mas o registro só tem ${r.lutas.length} lutas`);
  for (let k = 0; k < r.lutas.length; k++) {
    t.lutar(r.lutas[k]);
    if (trocas.has(k)) t.trocar();
  }
  const vencidas = t.lutas.filter(l => l.venceu), u = vencidas[vencidas.length - 1];
  return { tentativa: t, resultado: { vitorias: t.vitorias, series: t.series, lutas: t.lutas.length, acabou: t.acabou,
    vidaUltimaVitoria: u ? Math.max(0, u.poc.vidaA) : 0 } };
}

/** uma linha da tabela do dia (o que o desempate olha) */
export interface LinhaDesafio { vitorias: number; vidaUltimaVitoria: number; terminouEm: number }
/** o desempate da secao 6: mais vitorias, mais vida no fim da ultima vitoria, quem terminou antes */
export const compararDesafio = (a: LinhaDesafio, b: LinhaDesafio): number =>
  (b.vitorias - a.vitorias) || (b.vidaUltimaVitoria - a.vidaUltimaVitoria) || (a.terminouEm - b.terminouEm);

/** quantos levam o selo "Top do dia" (MMO-11): os 10 primeiros, ou o 1 % de cima com mais de 1 000 jogadores (PROPOSTO, SEM FONTE) */
export const TOP_DO_DIA = 10;
export const JOGADORES_PARA_O_PERCENTUAL = 1000;
export const selosDoDia = (jogadores: number): number =>
  jogadores > JOGADORES_PARA_O_PERCENTUAL ? Math.ceil(jogadores / 100) : Math.min(TOP_DO_DIA, jogadores);
