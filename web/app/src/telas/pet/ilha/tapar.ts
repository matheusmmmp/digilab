/* Quem tapa o pet (docs/TAREFA_V3_MOITA_NINHO.md), sem three e sem DOM: os objetos altos da decoracao (TAPAR_PET.modelos) viram cilindros
   de pe, e o pet, alguns pontos de um cilindro curto (TAPAR_PET.amostras da altura dele, com o raio TAPAR_PET.raio somado ao do objeto).
   O objeto tapa se a linha da camera a um desses pontos atravessa o cilindro dele, entre a base e o topo, antes de chegar ao pet. So vista:
   o motor e o mapa nao mudam. */

/** um objeto que pode tapar: o centro no chao (x, z, em celulas), a base e o topo (y ja dobrados, como o shader os desenha) e o raio */
export interface Tapavel { x: number; z: number; y0: number; topo: number; raio: number }
export type Ponto = readonly [number, number, number];

/** o trecho [t1, t2] (0 = a camera, 1 = o alvo) em que a linha de `c` a `p`, vista de cima, fica a menos de `r` do centro (x, z); null se nao chega */
function trechoNoCirculo(c: Ponto, p: Ponto, x: number, z: number, r: number): [number, number] | null {
  const dx = p[0] - c[0], dz = p[2] - c[2], ox = c[0] - x, oz = c[2] - z;
  const a = dx * dx + dz * dz, b = 2 * (ox * dx + oz * dz), cc = ox * ox + oz * oz - r * r;
  if (a < 1e-12) return cc <= 0 ? [0, 1] : null;          // a camera bem em cima do alvo: so se ela esta dentro do circulo
  const disc = b * b - 4 * a * cc;
  if (disc < 0) return null;
  const s = Math.sqrt(disc), t1 = Math.max(0, (-b - s) / (2 * a)), t2 = Math.min(1, (-b + s) / (2 * a));
  return t1 < t2 ? [t1, t2] : null;
}

/** os indices (na ordem da lista) dos objetos que tapam o pet: o pe dele em `pe` (y ja dobrado), com a altura `altura`; `raioPet` soma ao raio
    de cada objeto. Um objeto cujo centro fica atras do pet (visto da camera) nao tapa */
export function quemTapa(camera: Ponto, pe: Ponto, lista: readonly Tapavel[], altura: number, raioPet: number, amostras: readonly number[]): number[] {
  const fora: number[] = [];
  const dx = pe[0] - camera[0], dz = pe[2] - camera[2], L2 = dx * dx + dz * dz;
  lista.forEach((o, i) => {
    /* atras do pet: a projecao do centro na linha passa do pet */
    if (L2 > 1e-12 && ((o.x - camera[0]) * dx + (o.z - camera[2]) * dz) / L2 >= 1) return;
    for (const f of amostras) {
      const alvo: Ponto = [pe[0], pe[1] + f * altura, pe[2]];
      const tr = trechoNoCirculo(camera, alvo, o.x, o.z, o.raio + raioPet);
      if (!tr) continue;
      /* a altura da linha nos dois lados do trecho: tapa se o intervalo cruza [base, topo] */
      const y = (t: number) => camera[1] + t * (alvo[1] - camera[1]);
      const ya = y(tr[0]), yb = y(tr[1]);
      if (Math.min(ya, yb) <= o.topo && Math.max(ya, yb) >= o.y0) { fora.push(i); return; }
    }
  });
  return fora;
}

/** a opacidade que anda para o alvo: com a constante de tempo `tauMs`, ou na hora com "reduzir movimento" */
export function opacidadeAgora(atual: number, alvo: number, dtMs: number, tauMs: number, reduzido: boolean): number {
  if (reduzido || tauMs <= 0) return alvo;
  const k = 1 - Math.exp(-Math.max(0, dtMs) / tauMs), v = atual + (alvo - atual) * k;
  return Math.abs(v - alvo) < 0.01 ? alvo : v;
}
