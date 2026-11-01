/* O sono desenhado (o Matheus, 2026-11-01): o atlas do UP nao tem pose de dormir (os clipes sao Idle, Run, Attack_1, Stun, Die e Evol),
   entao o pet dormindo e o quadro parado do Idle achatado, respirando devagar, num tom mais apagado, com o "zz" subindo por cima. Vale
   para todos os Digimon de uma vez. So desenho: nao muda a vida, o log nem o replay. Os numeros sao PROPOSTO, SEM FONTE. */
import { S, desenharGrade, type Paleta } from "../../grades.ts";

export const SONO = {
  /** a altura do papel dormindo (fracao da acordada) e a variacao da respiracao em volta dela */
  achata: 0.84, respira: 0.035,
  /** o periodo de uma respiracao (ms) */
  respiraMs: 2600,
  /** o tom que multiplica o papel dormindo (de dia; a noite, o da noite ja e mais escuro) */
  tom: 0xc9cfe8,
  /** um "z" leva zzMs para subir zzSobe px de CSS e sumir; dois ao mesmo tempo, defasados de meio ciclo */
  zzMs: 2600, zzSobe: 26,
} as const;

/** a fracao da altura dormindo agora; com movimento reduzido, parada no meio */
export function alturaSono(agora: number, reduzido: boolean): number {
  return reduzido ? SONO.achata : SONO.achata + Math.sin((agora / SONO.respiraMs) * Math.PI * 2) * SONO.respira;
}

/** o "zz" subindo do alto do pet (x, y, w em px de CSS; K = px do canvas por px de CSS): o "z" claro com sombra escura, em escala inteira */
export function desenharZz(cx: CanvasRenderingContext2D, K: number, x: number, y: number, w: number, agora: number, reduzido: boolean, pal: Paleta): void {
  const g = S.zz, fases = reduzido ? [0.35] : [0, 0.5];
  for (const [i, f0] of fases.entries()) {
    const f = reduzido ? f0 : ((agora / SONO.zzMs) + f0) % 1;
    const esc = Math.max(1, Math.round((i === 0 ? 4 : 3) * K));
    const bx = Math.round((x + w * 0.6 + f * 12) * K), by = Math.round((y + 4 - g.length * esc / K - f * SONO.zzSobe) * K);
    cx.save();
    cx.globalAlpha = reduzido ? 0.9 : Math.min(1, (1 - f) * 1.6);
    cx.setTransform(esc, 0, 0, esc, bx + esc, by + esc);
    desenharGrade(cx, g, 0, 0, { ...pal, k: "#1D2233" });
    cx.setTransform(esc, 0, 0, esc, bx, by);
    desenharGrade(cx, g, 0, 0, { ...pal, k: "#EEF3FF" });
    cx.restore();
  }
}
