/* Os Bits, a moeda do jogo (docs/PLANO_V3_MOEDA.md, etapa MO1; decisoes M-1 a M-10 do Matheus de 2026-11-10). So no jogo: o motor do pet
   nao sabe deles, e o Python nao os tem. Esta e a conta pura: que feitos de um pet (ou do Tamer) valem Bits, e quanto. Quem grava e o
   tamer.ts (o evento "bits"), chamado pelo jogo.ts depois de toda mudanca do pet, como as medalhas.

   A regra (secao 2 do plano): a moeda paga o FEITO, nao o clique.
   - a vitoria contra um rival, pela faixa dele, com a novidade: a 1a contra um rival no dia do pet paga cheio, cada repeticao no mesmo dia
     paga a metade da anterior (M-3). A derrota, o empate e a Fronteira (Liga, Torre, Salao) nao pagam;
   - a 1a medalha de cada lider: 5x a faixa do lugar dele;
   - o chamado do bebe atendido e o cuidado na hora certa do Rookie em diante (Motor.feitosCuidado), com o teto de Bits por dia do pet;
   - a pausa do treino atendida;
   - os marcos: cada evolucao e cada nivel do Tamer.
   Cada feito tem um id estavel (a ordem dele no que o motor deriva do registro, que so cresce), entao conferir de novo nao paga duas vezes.
   Todos os numeros sao PROPOSTOS, SEM FONTE (M-10: a rodada de equilibrio os acerta numa vida gravada). */
import { LUGARES_V6, MEDALHA_POR_ID, RIVAL_LIGA, RIVAL_SALAO, TPD, ehInstalacao, nasceComEquilibrioCuidado, type Estagio, type Motor } from "../motor/index.ts";

/** de onde vieram os Bits de um evento do Tamer */
export type OrigemBits = "luta" | "lider" | "chamado" | "pausa" | "cuidado" | "evolucao" | "nivel";
export const ORIGENS_BITS: readonly OrigemBits[] = ["luta", "lider", "chamado", "pausa", "cuidado", "evolucao", "nivel"];
/** as origens que sao do Tamer, nao de um pet: o id basta (a medalha e o nivel acontecem uma vez por Tamer) */
export const ORIGENS_DO_TAMER: readonly OrigemBits[] = ["lider", "nivel"];

/** os valores (PROPOSTOS, SEM FONTE; docs/PLANO_V3_MOEDA.md, secao 2) */
export const BITS = {
  /** a vitoria pela faixa do rival (o bebe nao luta; se lutar, conta como Rookie) */
  faixa: { bebe: 10, crianca: 10, adolescente: 25, adulto: 60, mega: 150 } as Record<Estagio, number>,
  /** a 1a medalha de um lider: este tanto de vezes a faixa do lugar dele */
  lider: 5,
  chamado: 2,
  pausa: 3,
  cuidado: 1,
  /** o teto do chamado e do cuidado juntos, em Bits por dia do pet */
  tetoCuidadoDia: 20,
  /** cada evolucao, pelo estagio a que o pet chegou */
  evolucao: { bebe: 0, crianca: 50, adolescente: 100, adulto: 200, mega: 400 } as Record<Estagio, number>,
  /** cada nivel do Tamer */
  nivel: 30,
} as const;

/** a forma da tabela dos Bits (a de hoje, BITS, e a do E1, BITS_V2) */
export interface TabelaBits {
  readonly faixa: Record<Estagio, number>; readonly lider: number; readonly chamado: number; readonly pausa: number; readonly cuidado: number;
  readonly tetoCuidadoDia: number; readonly evolucao: Record<Estagio, number>; readonly nivel: number;
}

/** EQUILIBRIO_CUIDADO, E1 (docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E1.md): a tabela da calibracao. Desde o E3 (EQ-6), a dos pets v38 e v39
    (tabelaBitsDe); os pets das versoes de antes seguem com a BITS. Os valores que mudam (o cuidado na hora certa, o teto do dia e a evolucao
    para o Rookie) foram APROVADOS pelo Matheus em 2026-11-12 ("Aprovo, siga"), SEM FONTE, pela grade do E1; o resto e o da BITS */
export const BITS_V2: TabelaBits = { ...BITS, cuidado: 5, tetoCuidadoDia: 40, evolucao: { ...BITS.evolucao, crianca: 60 } };
/** a tabela dos Bits de um pet, pela versao dele: a BITS_V2 na v38 e na v39 (o E3), a BITS nas de antes */
export const tabelaBitsDe = (versao: number): TabelaBits => nasceComEquilibrioCuidado(versao) ? BITS_V2 : BITS;

/** um feito que vale Bits */
export interface Feito { id: string; valor: number; origem: OrigemBits; tick: number }

/** o estagio do pet no tick (pela lista das evolucoes) */
function estagioNoTick(m: Motor, tick: number): Estagio {
  let est: Estagio = "bebe";
  for (const ev of m.evolucoes) if (ev.tick <= tick) est = ev.estagio;
  return est;
}
/** a faixa do rival: o lugar da campanha do NPC; na Arena, o estagio do pet na hora (a Arena so oferece rivais do estagio dele) */
function faixaDoRival(m: Motor, rival: string, tick: number): Estagio {
  const i = m.lugares.findIndex(L => L.rivais.includes(rival));
  return i >= 0 ? m.lugares[i].est : estagioNoTick(m, tick);
}
const ehTorneio = (rival: string): boolean => rival === RIVAL_LIGA || rival === RIVAL_SALAO || ehInstalacao(rival);

/** os feitos do pet que valem Bits, na ordem do registro dele. Puro: le so o que o motor deriva do replay. `tabela`: a da versao do pet
    (tabelaBitsDe: a BITS_V2 na v38 e na v39, a BITS nas de antes); a bancada do E1 passa a dela */
export function feitosDoPet(m: Motor, tabela: TabelaBits = tabelaBitsDe(m.versao)): Feito[] {
  const BITS = tabela;
  const feitos: Feito[] = [];
  /* as vitorias, com a novidade por rival e por dia do pet */
  const repeticoes = new Map<string, number>();
  m.vida5.lutas.forEach((l, i) => {
    if (l.resultado !== "vitoria" || ehTorneio(l.rival)) return;
    const chave = `${l.rival}@${Math.floor(l.tick / TPD)}`, k = repeticoes.get(chave) ?? 0;
    repeticoes.set(chave, k + 1);
    const valor = Math.floor(BITS.faixa[faixaDoRival(m, l.rival, l.tick)] / 2 ** k);
    if (valor > 0) feitos.push({ id: `luta:${i}`, valor, origem: "luta", tick: l.tick });
  });
  /* o chamado e o cuidado na hora, com o teto do dia; a pausa por fora do teto */
  const noDia = new Map<number, number>();
  m.feitosCuidado.forEach((f, i) => {
    if (f.tipo === "pausa") { feitos.push({ id: `pausa:${i}`, valor: BITS.pausa, origem: "pausa", tick: f.tick }); return; }
    const dia = Math.floor(f.tick / TPD), ja = noDia.get(dia) ?? 0, v = Math.min(BITS[f.tipo], BITS.tetoCuidadoDia - ja);
    if (v <= 0) return;
    noDia.set(dia, ja + v);
    feitos.push({ id: `${f.tipo}:${i}`, valor: v, origem: f.tipo, tick: f.tick });
  });
  /* as evolucoes */
  for (const ev of m.evolucoes) if (BITS.evolucao[ev.estagio] > 0)
    feitos.push({ id: `evolucao:${ev.estagio}`, valor: BITS.evolucao[ev.estagio], origem: "evolucao", tick: ev.tick });
  return feitos;
}
/** os Bits da 1a medalha de um lider: 5x a faixa do lugar da arena dele */
export function bitsDaMedalha(id: string): number {
  const md = MEDALHA_POR_ID[id];
  if (!md) throw new Error(`medalha desconhecida nos Bits: ${JSON.stringify(id)}`);
  return BITS.lider * BITS.faixa[LUGARES_V6[md.lugar].est];
}
