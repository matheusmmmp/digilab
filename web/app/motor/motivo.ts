/* Motivo (espelho de digilab/motivo.py). Somente leitura: nao muda decisao.
   Fator so se a contribuicao e positiva, >= limiar e o termo aprendido MUDOU a escolha (sem ele,
   log-prior + Gumbel daria outra acao). */
import { ACOES_PET, CE, CV, FATORES_MEMORIA } from "./constantes.ts";
import type { Bandit } from "./bandit.ts";
import { CATALOGO_V2, Cd, DIST, type Cond, type Estilo, type Regra, type Turno } from "./combate.ts";
import type { AcaoPet, MotivoCombate, MotivoVida, Observacao } from "./tipos.ts";

export const FATOR_BASE = ["habito", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "hora", "tempo_sem_cuidado"];
export const FATOR_DA_FEATURE = [...FATOR_BASE, ...FATORES_MEMORIA];

export function motivoVida(m: { pol: Bandit; nDono: number }, obs: Observacao, acao: AcaoPet, tick: number): MotivoVida {
  const d = m.pol.ultDecisao;
  if (!d || d.acao !== acao) throw new Error("registro da decisao nao corresponde a acao devolvida");
  const outras = ACOES_PET.filter(a => a !== acao), contrib: Record<string, number> = {};
  d.x.forEach((xi, i) => {
    const media = outras.reduce((s, a) => s + d.amostras[a][i], 0) / outras.length;
    const n = i < FATOR_BASE.length ? FATOR_BASE[i] : m.pol.fatMem[i - FATOR_BASE.length]; contrib[n] = (contrib[n] || 0) + xi * (d.amostras[acao][i] - media);
  });
  let arg: AcaoPet | null = null, best = -Infinity;
  for (const a of ACOES_PET) { const s = d.logPrior[a] + d.gumbel[a]; if (s > best) { best = s; arg = a; } }
  const valorDecidiu = arg !== acao;
  const pos = Object.entries(contrib).filter(([, c]) => c >= CE.limiar).sort((x, y) => y[1] - x[1]);
  const fatores = valorDecidiu ? pos.slice(0, 2).map(([n]) => n) : [];
  const somaPos = Object.values(contrib).filter(c => c > 0).reduce((s, c) => s + c, 0);
  const intensidade = fatores.length && somaPos > 0 ? Math.min(1, pos[0][1] / somaPos) : 0;
  const refs: number[] = [];
  for (const f of fatores) {
    if (f === "tempo_sem_cuidado" && m.nDono > 0) refs.push(m.nDono);
    else if (m.pol.fatMem.includes(f) && d.refsMem[f] != null) refs.push(d.refsMem[f]!);
  }
  return {
    origem: "vida", tick, acao, fatores, refsOrd: [...new Set(refs)].sort((a, b) => a - b), intensidade,
    exploracao: false, humor: obs.v[3], valorDecidiu,
  };
}

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
