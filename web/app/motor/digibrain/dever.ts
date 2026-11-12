/* Os deveres do pet com o outro em TS (docs/ESPEC_V3_COOPERACAO_CO7.md; so com a subchave `co7`): o porte de digilab/digibrain/dever.py,
   conta a conta (o G-PAR-CO7, test/cooperacao_co7.test.ts). Tudo em inteiros, sem rng, e so do que o pet ve (o G-RECEPTOR-SOCIAL, CO7-1).
     social       (M-SENS) a percepcao social da decisao em posicoes absolutas, com a posicao de antes de cada outro e o proprio k;
     situacao     (M-ARB) as comidas para as quais um outro aflito vai, a privacao, se o escudo vale, o delta da universalizacao e se a comida
                  e a unica a vista;
     ajustar      (M-ARB) os pesos depois do escudo (as unidades de comer a comida proibida saem) e da universalizacao (reprova e aprova);
     culpaInveja  (M-AFETO) o que a decisao tira da valencia: a culpa (humor alto e um aflito a vista) e a inveja (humor baixo e um outro
                  visto comendo ha pouco), com os pesos neutros.
   Com os atos de hoje, a universalizacao se reduz a tabela de sinais da CO3 (CO7-5). */
import { mul } from "./_comum.ts";

export const AFLICAO: readonly string[] = ["emburrar", "chamar_atencao"];
export const COMIDAS_MADURAS: readonly string[] = ["racao", "a", "b", "c"];

/** os numeros da CO7 que as contas leem (a ConfigCooperacao do Python; o CCOOP e o espelho conferido) */
export interface ConfigDever {
  limiarEscudo: number; rEscudoCelulas: number; pisoPrivacaoS: number; wUniv: number; limiarHumor: number; wCulpa: number; wInveja: number;
  janelaInveja: number;
}

/** a percepcao social que a CO7 le (a do grupo, com o k da CO6) */
export interface SocialDaPercepcao {
  outros: readonly (readonly [string, number, number, number, string])[]; onde_comeu: readonly (readonly [string, number, number, number])[];
  peso_dever?: number;
}
export interface OutroDever { id: string; x: number; y: number; acao: string; aflito: boolean; antes: [number, number] | null }
export interface SocialDever { k: number; outros: OutroDever[]; onde_comeu: { id: string; x: number; y: number; idade: number }[]; r2_escudo: number }
export interface SituacaoDever { k: number; privacao: boolean; escudo: boolean; proibidas: number[]; delta: number; unica: boolean }
export type ChaveDever = readonly unknown[];

const d2 = (ax: number, ay: number, bx: number, by: number): number => (ax - bx) * (ax - bx) + (ay - by) * (ay - by);

/** a percepcao social em posicoes absolutas; `antes`, a posicao em que o pet viu cada outro na ultima decisao em que o via; null sem outro */
export function socialDever(ps: SocialDaPercepcao | null | undefined, pos: readonly [number, number], antes: Readonly<Record<string, readonly [number, number]>>,
                            rEscudo: number): SocialDever | null {
  if (ps === null || ps === undefined) return null;
  if (ps.peso_dever === undefined) throw new Error("deveres: a CO7 le o peso dos deveres da CO6 na percepcao social (a co6 desligada no grupo?)");
  const [x, y] = pos;
  const outros = ps.outros.map(([id, dx, dy, , acao]): OutroDever => {
    if (typeof acao !== "string") throw new Error(`deveres: a acao visivel e o nome da acao: ${JSON.stringify(acao)}`);
    const a = antes[id];
    return { id, x: x + dx, y: y + dy, acao, aflito: AFLICAO.includes(acao), antes: a === undefined ? null : [a[0], a[1]] };
  });
  const comeu = ps.onde_comeu.map(([id, cx, cy, idade]) => ({ id, x: cx, y: cy, idade }));
  return { k: ps.peso_dever, outros, onde_comeu: comeu, r2_escudo: rEscudo * rEscudo };
}

export interface SensDever {
  social: SocialDever | null; leitura: Readonly<Record<string, number>>; pos: readonly [number, number];
  objetos: readonly { id: number; tipo: string; dx: number; dy: number }[];
}

/** o que o escudo e a universalizacao leem na decisao */
export function situacaoDever(sens: SensDever, urgencias: Readonly<Record<string, number>>, cfg: ConfigDever, S: number): SituacaoDever {
  const soc = sens.social!;
  const k = soc.k, fome = sens.leitura["fome"];
  if (fome === undefined) throw new Error("deveres: a privacao le a fome, e ela nao esta na percepcao do corpo");
  const privacao = fome < cfg.pisoPrivacaoS;
  const [x, y] = sens.pos;
  const comidas = sens.objetos.filter(o => COMIDAS_MADURAS.includes(o.tipo));
  const proibidas: number[] = [];
  for (const c of comidas) {
    const cx = x + c.dx, cy = y + c.dy;
    for (const o of soc.outros) {
      if (!o.aflito || o.antes === null) continue;
      const agora = d2(o.x, o.y, cx, cy);
      if (agora <= soc.r2_escudo && agora < d2(o.antes[0], o.antes[1], cx, cy)) { proibidas.push(c.id); break; }
    }
  }
  const urg = Object.values(urgencias);
  const delta = Math.min(mul(k, cfg.wUniv, S), urg.length ? Math.max(...urg) : 0);
  return { k, privacao, escudo: k >= cfg.limiarEscudo && !privacao, proibidas, delta, unica: comidas.length === 1 };
}

/** [os pesos depois do escudo e da universalizacao, o registro: os indices removidos, os que reprovaram e quantas aprovaram] */
export function ajustarDever(chaves: readonly ChaveDever[], w0: readonly number[], sit: SituacaoDever):
  [number[], { removidas: number[]; reprovadas: number[]; aprovadas: number }] {
  const w = [...w0], removidas: number[] = [], reprovadas: number[] = [];
  let aprovadas = 0;
  const proibida = (ch: ChaveDever) => ch[0] === "comer" && ch[1] === "comida" && sit.proibidas.includes(ch[2] as number);
  for (const [i, ch] of chaves.entries()) {
    if (!proibida(ch)) continue;
    if (sit.escudo) { if (w[i]! > 0) removidas.push(i); w[i] = 0; }
    else { if (w[i]! > 0) reprovadas.push(i); w[i] = Math.max(0, w[i]! - sit.delta); }
  }
  if (sit.unica && sit.proibidas.length && sit.delta > 0)
    for (const [i, ch] of chaves.entries()) if (w[i]! > 0 && !proibida(ch)) { w[i] = w[i]! + sit.delta; aprovadas += 1; }
  return [w, { removidas, reprovadas, aprovadas }];
}

/** [a culpa, a inveja] da decisao, na escala S */
export function culpaInveja(sens: Pick<SensDever, "social" | "leitura">, cfg: ConfigDever): [number, number] {
  const soc = sens.social;
  if (soc === null) return [0, 0];
  const humor = sens.leitura["humor"];
  if (humor === undefined) throw new Error("deveres: a culpa e a inveja leem o humor, e ele nao esta na percepcao do corpo");
  if (humor >= cfg.limiarHumor) return [soc.outros.some(o => o.aflito) ? cfg.wCulpa : 0, 0];
  return [0, soc.onde_comeu.some(c => c.idade <= cfg.janelaInveja) ? cfg.wInveja : 0];
}
