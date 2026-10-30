/* O controlador da luta em tempo real (docs/ESPEC_COMBATE_TR.md, item 2): a lista SE/ENTAO do lutador, avaliada quando ele fica livre.
   E o decidirV2 de hoje com as condicoes reescritas para o tempo real: as listas, o repertorio, as travas e os vetos valem como estao.
   O oraculo nao luta aqui (D-6). So + - x / e comparacoes (D-7). */
import { ACOES_V2, custoV2, type Cond, type Contexto, type Estilo, type RegrasLuta } from "../combate.ts";
import { CV, TECNICAS } from "../constantes.ts";
import type { Rng } from "../rng.ts";
import { CTR_TR, T_TR } from "./constantes_tr.ts";
import type { EstadoTR, LadoTR } from "./luta.ts";

/** a faixa da distancia agora: 0 = perto, 1 = medio, 2 = longe (espec 1.2) */
export function faixaTR(S: EstadoTR): number {
  const d = S.L[1].x - S.L[0].x;
  return d <= CTR_TR.perto ? 0 : d <= CTR_TR.medio ? 1 : 2;
}
export const peleAtivaTR = (S: EstadoTR, l: LadoTR): boolean => S.passo < l.peleAte;
export const marcaAtivaTR = (S: EstadoTR, l: LadoTR): boolean => S.passo < l.marcaAte;
/** o lado esta preparandoTR o pesado: na acao de preparo, ou com o preparo pronto e a execucao por decidir */
export const preparandoTR = (l: LadoTR): boolean => l.prep || l.acao?.nome === "preparar_pesado";

/** a acao e legal agora (o legalV2 de hoje, com a faixa e o tempo; espec 1.3 a 1.5) */
export function legalTR(S: EstadoTR, lado: number, a: string): boolean {
  const eu = S.L[lado], p = eu.p, d = faixaTR(S);
  if (a === "fintar") return eu.prep;
  if (eu.prep || a === "pesado" || !ACOES_V2.includes(a)) return false;
  if (a === "avancar" && d === 0) return false;
  if (a === "recuar" && d === 2) return false;
  if ((TECNICAS as readonly string[]).includes(a) && p.tecnica !== a) return false;
  if (eu.guts < custoV2(a)) return false;
  if (a === "golpe_rapido" || a === "preparar_pesado") return d === 0;
  if (a === "disparo") return d !== 0;
  if (a === "investida") return d === 1;
  if (a === "contra_golpe") return p.passiva === "espelho" || d === 0;
  if (a === "marcar") return d !== 0 && !marcaAtivaTR(S, eu);
  if (a === "pele_dura") return !peleAtivaTR(S, eu);
  if (a === "defender") return p.passiva !== "furioso" && p.passiva !== "devastador";
  if (a === "esquivar") return p.passiva !== "devastador";
  if (a === "recuar") return p.passiva !== "predador";
  return true;
}
export const legaisTR = (S: EstadoTR, lado: number): string[] => ACOES_V2.filter(a => legalTR(S, lado, a));

/** a condicao vale agora (o catalogo de hoje, CATALOGO_V2, reescrito para o tempo real; espec item 2) */
export function valeCondTR(c: Cond, S: EstadoTR, lado: number, ctx: Contexto | null, R: RegrasLuta | null): boolean {
  const eu = S.L[lado], op = S.L[1 - lado], p = c.p;
  switch (c.n) {
    case "sempre": return true;
    case "distancia_eh": return faixaTR(S) === p[0];
    case "hp_proprio_abaixo": return eu.hp / eu.hpMax < (p[0] as number);
    case "guts_proprio_abaixo": return eu.guts < (p[0] as number);
    case "guts_proprio_acima": return eu.guts >= (p[0] as number);
    /* V21D: o preparo feito sob pele dura nao aparece */
    case "oponente_preparando": return preparandoTR(op) && !(R?.preparoSobPeleOculto && op.prepPele);
    case "oponente_hp_abaixo": return op.hp / op.hpMax < (p[0] as number);
    case "oponente_guts_abaixo": return op.guts < (p[0] as number);
    case "oponente_repete": { const u = op.hist.slice(-(p[1] as number)); return u.length === p[1] && u.every(x => x === p[0]); }
    case "oponente_frequente": { const u = op.hist.slice(-CV.janelaFreq); return u.filter(x => x === p[0]).length / CV.janelaFreq >= CV.limiarFreq; }
    /* o turno t vira o relogio t x T_TR */
    case "turno_execucao": return S.passo >= (p[0] as number) * T_TR;
    case "oponente_vai_preparar": return !!ctx && ctx.intencao === "preparar_pesado";
    case "executando_pesado": return eu.prep;
  }
  throw new Error("condição sem avaliador no tempo real: " + c.n);
}

function semOraculo(estilo: Estilo): void {
  if (estilo.oraculo) throw new Error(`o oráculo (${estilo.nome}) não luta em tempo real (D-6)`);
  if (!estilo.gambits) throw new Error(`o estilo ${estilo.nome} não tem lista de regras`);
}
/** o que a lista do lado escolheria agora, sem exploracao e sem rng (o que o vigia ve) */
export function intencaoTR(estilo: Estilo, S: EstadoTR, lado: number, R: RegrasLuta | null): string | null {
  semOraculo(estilo);
  if (S.L[lado].prep) return null;
  const g = estilo.gambits!;
  for (const r of g.regras) if (r.se.every(c => valeCondTR(c, S, lado, null, R)) && legalTR(S, lado, r.entao)) return r.entao;
  return legalTR(S, lado, g.final) ? g.final : "carregar";
}
/** a decisao do lado livre: [acao, motivo] (o indice da regra, "exploracao" ou "pesado_automatico"), como o decidirV2 */
export function decidirTR(estilo: Estilo, S: EstadoTR, lado: number, rng: Rng, ctx: Contexto | null, R: RegrasLuta | null): [string, number | string] {
  semOraculo(estilo);
  const g = estilo.gambits!;
  if (S.L[lado].prep) {
    /* a finta: a primeira regra de fintar que vale troca o pesado (sem exploracao) */
    for (let i = 0; i < g.regras.length; i++) {
      const r = g.regras[i];
      if (r.entao === "fintar" && r.se.every(c => valeCondTR(c, S, lado, ctx, R))) return ["fintar", i];
    }
    return ["pesado", "pesado_automatico"];
  }
  const leg = legaisTR(S, lado);
  if (estilo.eps > 0 && rng.random() < estilo.eps) return [leg[rng.int(leg.length)], "exploracao"];
  for (let i = 0; i < g.regras.length; i++) {
    const r = g.regras[i];
    if (r.se.every(c => valeCondTR(c, S, lado, ctx, R)) && legalTR(S, lado, r.entao)) return [r.entao, i];
  }
  /* furioso nao defende: a final 'defender' cai para carregar */
  return [legalTR(S, lado, g.final) ? g.final : "carregar", g.regras.length];
}
