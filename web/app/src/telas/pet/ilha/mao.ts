/* O pet na mao do dono (docs/TAREFA_V3_PEGAR_PET.md, P2), sem three e sem DOM: as contas do desenho enquanto o dono segura o pet e logo
   depois que ele o solta. SO VISTA: nada disso entra no motor, no log ou no save (PP-1); a posicao do motor so muda pelo "levar pet" ao
   soltar (PegarPet.tsx).
   - o pendulo: o papel pende do alto (a "nuca") e balanca. O alvo do angulo e um balanco de agonia (seno de `periodoMs`) menos o arrasto
     (o corpo fica para tras do lado em que a mao anda); o angulo segue o alvo como uma mola amortecida;
   - o tremor: 1 texel de lado, trocando a cada `tremorMs`, por cima do balanco;
   - a altura: o papel sobe `alturaTexels` do chao (a sombra fica no chao, onde ele vai cair);
   - ao soltar: a queda da altura ate o chao em `quedaMs` e um quique de `quiqueTexels` em `quiqueMs`;
   - com movimento reduzido: sem balanco, sem tremor e sem quique (fica so a careta; a altura nao anima).
   Angulo positivo: o pe vai para a direita na tela. Todos os numeros sao PROPOSTO, SEM FONTE. */

export const MAO = {
  /** quanto o papel sobe do chao na mao (texels do sprite) */
  alturaTexels: 6,
  /** o balanco de agonia: amplitude (rad) e periodo (ms) */
  amplitude: 0.2, periodoMs: 820,
  /** o arrasto: rad por px de CSS por ms da mao, e o maximo (rad) */
  arrasto: 0.35, arrastoMax: 0.55,
  /** a mola do angulo: o amortecimento relativo (0..1) */
  amortece: 0.35,
  /** a velocidade da mao e suavizada com esta constante de tempo (ms) */
  velTauMs: 60,
  /** o tremor: texels e o tempo de cada troca (ms) */
  tremorTexels: 1, tremorMs: 70,
  /** ao soltar: a queda (ms) e o quique (texels, ms) */
  quedaMs: 110, quiqueTexels: 3, quiqueMs: 240,
  /** depois de soltar, o foco da camera e da dobra volta ao pet com esta constante de tempo (ms) */
  focoTauMs: 180,
} as const;

/** o pendulo do papel na mao: `passo` a cada quadro, com o x da mao em px de CSS */
export class Pendulo {
  angulo = 0;
  private vel = 0;
  private vx = 0;
  private xAntes: number | null = null;
  private t0: number | null = null;

  /** recomeca parado (o pet acabou de ser pego) */
  zerar(): void { this.angulo = 0; this.vel = 0; this.vx = 0; this.xAntes = null; this.t0 = null; }

  /** um quadro de `dtMs`, com a mao em `x` (px de CSS) no instante `agora`; devolve o angulo (rad). Reduzido: 0 */
  passo(dtMs: number, x: number, agora: number, reduzido: boolean): number {
    if (!Number.isFinite(x) || !Number.isFinite(agora)) throw new Error("Pendulo.passo: x ou agora nao finito");
    if (this.t0 === null) this.t0 = agora;
    if (reduzido) { this.zerarMovimento(x); return (this.angulo = 0); }
    const dt = Math.min(50, Math.max(0, dtMs));
    if (dt > 0 && this.xAntes !== null) {
      const v = (x - this.xAntes) / dt, k = 1 - Math.exp(-dt / MAO.velTauMs);
      this.vx += (v - this.vx) * k;
    }
    this.xAntes = x;
    if (!(dt > 0)) return this.angulo;
    const w = (2 * Math.PI) / MAO.periodoMs;
    const arr = Math.max(-MAO.arrastoMax, Math.min(MAO.arrastoMax, -this.vx * MAO.arrasto));
    const alvo = MAO.amplitude * Math.sin(w * (agora - this.t0)) + arr;
    /* a mola amortecida, em passos de no maximo 8 ms (estavel com quadros longos) */
    for (let r = dt; r > 0; r -= 8) {
      const h = Math.min(8, r), acc = -w * w * (this.angulo - alvo) - 2 * MAO.amortece * w * this.vel;
      this.vel += acc * h; this.angulo += this.vel * h;
    }
    return this.angulo;
  }
  private zerarMovimento(x: number): void { this.vel = 0; this.vx = 0; this.xAntes = x; }
}

/** o tremor de agora em texels inteiros (-1, 0 ou 1 vezes `tremorTexels`); reduzido: 0 */
export function tremorAgora(agora: number, reduzido: boolean): number {
  if (reduzido) return 0;
  const k = Math.floor(agora / MAO.tremorMs);
  /* uma sequencia fixa que nao repete o mesmo lado duas vezes seguidas */
  return [1, -1, 0, -1, 1, 0][((k % 6) + 6) % 6] * MAO.tremorTexels;
}

/** a altura do papel sobre o chao (texels, pode ser fracionaria) `ms` depois de soltar: a queda, o quique e 0. Reduzido: 0 na hora */
export function alturaDepoisDeSoltar(ms: number, reduzido: boolean): number {
  if (reduzido || !(ms >= 0)) return 0;
  if (ms < MAO.quedaMs) { const f = ms / MAO.quedaMs; return MAO.alturaTexels * (1 - f * f); }
  const q = ms - MAO.quedaMs;
  if (q < MAO.quiqueMs) return MAO.quiqueTexels * Math.sin(Math.PI * (q / MAO.quiqueMs));
  return 0;
}
/** a animacao de soltar acabou `ms` depois? */
export const soltarAcabou = (ms: number, reduzido: boolean): boolean => reduzido || ms >= MAO.quedaMs + MAO.quiqueMs;
