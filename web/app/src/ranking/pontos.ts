/* MMO1, a conta dos pontos (docs/PLANO_V3_MMO.md, secoes 4 e 5; MMO-7 e MMO-9 APROVADAS em 2026-11-11). Uma funcao pura, fora do
   motor: do registro do pet e da lista das sementes que o servidor entregou, os pontos de cada luta ranqueada, a semana de cada uma e as
   linhas das tabelas da semana (uma por estagio do pet). O servidor (MMO3) roda esta mesma conta no Node; o cliente a usa para a previa.
   Nada aqui toca o motor, o save ou as telas: o registro e refeito com Motor.aplicarEvento.

   As regras (secao 4):
     - so a vitoria ranqueada vale ponto, pela faixa do rival: Rookie 10, Champion 20, Ultimate 40, Mega 80 (PROPOSTO, SEM FONTE);
     - a vitoria repetida contra o mesmo rival na mesma semana vale a metade da anterior;
     - a derrota vale 0, e a semente entregue que nao aparece no registro tambem (conta como luta usada);
     - no maximo 10 lutas ranqueadas por dia de relogio (PROPOSTO, SEM FONTE): a semente a mais nao conta;
     - so a Arena: uma semente gasta na Fronteira (a Liga, a Torre, a Fabrica, o Salao) ou na Campanha nao vale ponto.
   O pedido da semente (MMO4) leva o tamanho do registro naquela hora (`indice`): a luta ranqueada e o evento "l" que esta exatamente nessa
   posicao, com a mesma semente. O hash do registro ate ali e conferido pelo servidor (MMO3/MMO4), nao aqui.

   A semana e o dia (secao 5): pelo relogio do servidor (`hora`, em milissegundos UTC), no horario de Brasilia (UTC-3, sem horario de
   verao); a semana vai de segunda 00:00 a domingo 23:59. */
import { DIGIMON_DA_FORMA, Motor, NIVEL_DO_ESTAGIO, type EventoRegistro, type IdCena } from "../../motor/index.ts";

/** os pontos da vitoria pela faixa do rival (PROPOSTO, SEM FONTE) */
export const PONTOS_FAIXA: Readonly<Record<string, number>> = { Rookie: 10, Champion: 20, Ultimate: 40, Mega: 80 };
/** as lutas ranqueadas por dia de relogio (PROPOSTO, SEM FONTE; MMO-8) */
export const LUTAS_POR_DIA = 10;
/** o horario de Brasilia: UTC-3, sem horario de verao */
export const FUSO_BRASILIA_MS = -3 * 3600_000;
const DIA_MS = 86_400_000;

/** uma semente que o servidor entregou: a semente, o tamanho do registro do pet no pedido e a hora do servidor (ms UTC) */
export interface SementeEntregue { semente: number; indice: number; hora: number }
/** o que aconteceu com a semente entregue */
export type Situacao =
  | "vitoria" | "derrota"
  | "nao_enviada"     // o registro ja passou do indice e o evento ali nao e esta luta: conta como derrota
  | "pendente"        // o registro ainda nao chegou ao indice: 0 por enquanto (o servidor fecha como derrota no fim da semana)
  | "fora_da_arena"   // a semente foi gasta na Fronteira ou na Campanha: 0
  | "acima_do_limite"; // a 11a semente do dia em diante: nao conta
export interface LutaRanqueada {
  semente: number; indice: number; hora: number; dia: string; semana: string;
  situacao: Situacao; rival: string | null; faixa: string | null;
  /** o estagio do pet na hora do pedido (o nome do Digimon: Rookie, Champion, Ultimate, Mega); null se o registro nao chegou la */
  estagio: string | null;
  pontos: number;
  /** a vida que sobrou ao pet no fim da ultima luta da serie (null fora da vitoria e da derrota) */
  vidaFinal: number | null;
}
/** uma linha da tabela da semana de um estagio, com os campos do desempate (secao 5) */
export interface LinhaSemana {
  semana: string; estagio: string; pontos: number;
  /** 2o criterio: os rivais diferentes vencidos */
  rivaisVencidos: number;
  /** 3o criterio: as lutas ranqueadas usadas (contam as derrotas, as nao enviadas e as pendentes) */
  lutasUsadas: number;
  /** 4o criterio: a hora do servidor da ultima luta que somou pontos (quem chegou antes aos pontos); null sem pontos */
  horaDosPontos: number | null;
}

/** o dia de Brasilia de uma hora do servidor, AAAA-MM-DD */
export function diaDe(hora: number): string { return new Date(hora + FUSO_BRASILIA_MS).toISOString().slice(0, 10); }
/** a semana de Brasilia de uma hora do servidor: a segunda-feira que a abre, AAAA-MM-DD */
export function semanaDe(hora: number): string {
  const local = hora + FUSO_BRASILIA_MS, d = new Date(local), desdeSegunda = (d.getUTCDay() + 6) % 7;
  return new Date(Math.floor(local / DIA_MS) * DIA_MS - desdeSegunda * DIA_MS).toISOString().slice(0, 10);
}

/** as lutas ranqueadas de um pet: refaz o registro e acha, para cada semente entregue, a luta dela. Falha alto num registro que nao
    reproduz, numa semente entregue duas vezes e em indices fora de ordem (o servidor nunca entrega assim) */
export function lutasRanqueadas(semente: number, versao: number, log: readonly EventoRegistro[], entregues: readonly SementeEntregue[]): LutaRanqueada[] {
  const vistas = new Set<number>();
  entregues.forEach((x, k) => {
    if (!Number.isInteger(x.semente) || !Number.isInteger(x.indice) || x.indice < 0 || !Number.isFinite(x.hora))
      throw new Error(`semente entregue inválida: ${JSON.stringify(x)}`);
    if (vistas.has(x.semente)) throw new Error(`semente entregue duas vezes: ${x.semente}`);
    vistas.add(x.semente);
    if (k > 0 && (x.indice < entregues[k - 1].indice || x.hora < entregues[k - 1].hora)) throw new Error(`sementes entregues fora de ordem: ${x.semente}`);
  });
  /* o estagio do pet em cada indice pedido e o resultado da luta que esta nele, refazendo o registro uma vez */
  const pedidos = new Map<number, SementeEntregue[]>();
  for (const x of entregues) pedidos.set(x.indice, [...(pedidos.get(x.indice) ?? []), x]);
  const noIndice = new Map<number, { estagio: string; venceu: boolean | null; rival: string | null; s: number | null; vida: number | null }>();
  const m = new Motor(semente, versao);
  for (let i = 0; i <= log.length; i++) {
    let venceu: boolean | null = null, rival: string | null = null, s: number | null = null, vida: number | null = null;
    const estagio = NIVEL_DO_ESTAGIO[m.estagioAtual];
    if (i < log.length) {
      const ev = log[i];
      if (ev[1] === "l") {
        /* a luta pelo lutarPoc, para ler o resultado; o tick e conferido aqui, como no aplicarEvento */
        if (ev[0] !== m.e.tick) throw new Error(`registro fora de ordem no tick ${ev[0]}`);
        const r = m.lutarPoc(ev[2].r, ev[2].s, (ev[2].m ?? null) as IdCena | null);   // o mapa do registro; o lutarPoc o confere
        venceu = r.venceu; rival = ev[2].r; s = ev[2].s; vida = r.serie.length ? r.serie[r.serie.length - 1].vidaA : null;
      } else m.aplicarEvento(ev);
    }
    if (pedidos.has(i)) noIndice.set(i, { estagio, venceu, rival, s, vida });
  }
  /* as sementes do dia, na ordem: a 11a em diante fica acima do limite */
  const porDia = new Map<string, number>();
  const lutas: LutaRanqueada[] = entregues.map(x => {
    const dia = diaDe(x.hora), semana = semanaDe(x.hora), n = (porDia.get(dia) ?? 0) + 1;
    porDia.set(dia, n);
    const base = { semente: x.semente, indice: x.indice, hora: x.hora, dia, semana, rival: null, faixa: null, pontos: 0, vidaFinal: null };
    if (n > LUTAS_POR_DIA) return { ...base, situacao: "acima_do_limite" as const, estagio: null };
    if (x.indice >= log.length) return { ...base, situacao: "pendente" as const, estagio: x.indice === log.length ? noIndice.get(x.indice)!.estagio : null };
    const o = noIndice.get(x.indice)!;
    if (o.s !== x.semente) return { ...base, situacao: "nao_enviada" as const, estagio: o.estagio };
    const faixa = DIGIMON_DA_FORMA[o.rival!]?.[1] ?? null;
    if (faixa === null || PONTOS_FAIXA[faixa] === undefined) return { ...base, situacao: "fora_da_arena" as const, rival: o.rival, estagio: o.estagio };
    return { ...base, situacao: o.venceu ? "vitoria" as const : "derrota" as const, rival: o.rival, faixa, estagio: o.estagio, vidaFinal: o.vida };
  });
  /* os pontos: a vitoria pela faixa, com a metade para cada vitoria anterior contra o mesmo rival na mesma semana */
  const repeticoes = new Map<string, number>();
  for (const l of lutas) {
    if (l.situacao !== "vitoria") continue;
    const chave = l.semana + "|" + l.rival, k = repeticoes.get(chave) ?? 0;
    repeticoes.set(chave, k + 1);
    l.pontos = PONTOS_FAIXA[l.faixa!] / 2 ** k;
  }
  return lutas;
}

/** as linhas das tabelas da semana de um pet: uma por (semana, estagio) em que ele usou uma luta ranqueada. A semente acima do limite e a
    pendente sem estagio nao entram */
export function linhasDaSemana(lutas: readonly LutaRanqueada[]): LinhaSemana[] {
  const linhas = new Map<string, LinhaSemana & { rivais: Set<string> }>();
  for (const l of lutas) {
    if (l.situacao === "acima_do_limite" || l.estagio === null) continue;
    const chave = l.semana + "|" + l.estagio;
    const x = linhas.get(chave) ?? { semana: l.semana, estagio: l.estagio, pontos: 0, rivaisVencidos: 0, lutasUsadas: 0, horaDosPontos: null, rivais: new Set<string>() };
    x.lutasUsadas++;
    if (l.situacao === "vitoria") { x.rivais.add(l.rival!); x.pontos += l.pontos; x.horaDosPontos = l.hora; }
    x.rivaisVencidos = x.rivais.size;
    linhas.set(chave, x);
  }
  return [...linhas.values()].map(({ rivais: _r, ...x }) => x);
}

/** a ordem da tabela da semana (secao 5): 1) mais pontos; 2) mais rivais diferentes vencidos; 3) menos lutas usadas; 4) quem chegou
    antes aos pontos. O que empata nos quatro fica na ordem de entrada (a ordenacao e estavel) */
export function compararLinhas(a: LinhaSemana, b: LinhaSemana): number {
  return (b.pontos - a.pontos) || (b.rivaisVencidos - a.rivaisVencidos) || (a.lutasUsadas - b.lutasUsadas)
    || horaAntes(a.horaDosPontos, b.horaDosPontos);
}
/** a hora menor vem antes; sem pontos (null) vem depois de quem tem */
function horaAntes(a: number | null, b: number | null): number {
  if (a === b) return 0;
  if (a === null) return 1;
  if (b === null) return -1;
  return a - b;
}
export function ordenarTabela<T extends LinhaSemana>(linhas: readonly T[]): T[] {
  if (linhas.some(l => l.semana !== linhas[0].semana || l.estagio !== linhas[0].estagio)) throw new Error("tabela com semanas ou estágios misturados");
  return [...linhas].sort(compararLinhas);
}
