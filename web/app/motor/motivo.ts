/* Motivo (espelho de digilab/motivo.py). Somente leitura: nao muda decisao.
   Fator so se a contribuicao e positiva, >= limiar e o termo aprendido MUDOU a escolha (sem ele,
   log-prior + Gumbel daria outra acao). */
import { CV, FATORES_MEMORIA } from "./constantes.ts";
import { CATALOGO_V2, Cd, DIST, type Cond, type Estilo, type Regra, type Turno } from "./combate.ts";
import type { MotivoCombate } from "./tipos.ts";

export const FATOR_BASE = ["habito", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "hora", "tempo_sem_cuidado"];
export const FATOR_DA_FEATURE = [...FATOR_BASE, ...FATORES_MEMORIA];

export function nomeCond(c: Cond): string {
  const tipos = CATALOGO_V2[c.n];
  return c.p.length ? `${c.n}(${c.p.map((x, i) => tipos[i] === "d" ? DIST[x as number] : x).join(",")})` : c.n;
}
/** adaptador de motivo do combate (espelho de motivo.motivos_de_partida) */
export function motivoCombate(tr: Turno, lado: 0 | 1, estilo: Estilo): MotivoCombate {
  const m = lado === 0 ? tr.ma : tr.mb, acao = lado === 0 ? tr.a : tr.b, t = tr.t, histOp = tr.antes.L[1 - lado].hist;
  const base: MotivoCombate = { origem: "combate", turno: t, acao, fatores: [], refs: [], exploracao: false, regra: m };
  if (m === "exploracao") return { ...base, exploracao: true };
  if (m === "pesado_automatico") return { ...base, refs: [t - 1] };
  if (m === "oraculo") return base;
  const g = estilo.gambits!, regra: Regra = (m as number) < g.regras.length ? g.regras[m as number] : { se: [Cd("sempre")], entao: g.final };
  const conds = regra.se.filter(c => c.n !== "sempre"), refs = new Set<number>();
  for (const c of conds) {
    if (c.n === "oponente_preparando") refs.add(t - 1);
    else if (c.n === "oponente_repete") { for (let k = t - (c.p[1] as number); k < t; k++) refs.add(k); }
    else if (c.n === "oponente_frequente") { for (let k = Math.max(1, t - CV.janelaFreq); k < t; k++) if (histOp[k - 1] === c.p[0]) refs.add(k); }
    else refs.add(t);
  }
  return { ...base, fatores: conds.map(nomeCond), refs: [...refs].sort((a, b) => a - b) };
}
