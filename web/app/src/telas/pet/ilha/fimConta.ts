/* As contas do fim da ilha (fimDaIlha.ts), sem three e sem DOM, para o teste: a linha do horizonte do mar curvo vista da camera e o perfil
   das silhuetas. Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import { NIVEL_AGUA, rng } from "./grade.ts";

/** a linha do horizonte do mar curvo vista da camera, a `raio` celulas do foco (a altura, em celulas, em relacao ao chao do foco). A camera
    esta `h` acima do chao do foco e `c` atras dele, na direcao da dobra; o mar cai `dobra * d^2` a `d` do foco. A reta da camera que tangencia o
    mar toca em d* = -c + sqrt(c^2 + h / dobra), com a inclinacao -2 dobra d*; sem dobra, o horizonte e o nivel da agua */
export function horizonte(h: number, c: number, dobra: number, raio: number): number {
  if (dobra <= 0) return NIVEL_AGUA;
  const d = -c + Math.sqrt(c * c + Math.max(h, 0.01) / dobra), m = -2 * dobra * d;
  return h + m * (raio + c);
}

/** o perfil de uma faixa, por volta (0 a 1): picos que se repetem na volta, sem emenda; 0 e o mar aberto, 1 a altura toda */
export function perfil(semente: number, picos: number, largos: boolean): (u: number) => number {
  const r = rng(semente), lista = Array.from({ length: picos }, () => ({ u: r(), a: 0.45 + r() * 0.55, w: (largos ? 0.05 : 0.018) + r() * (largos ? 0.07 : 0.03) }));
  return u => {
    let v = 0;
    for (const p of lista) {
      let d = Math.abs(u - p.u);
      d = Math.min(d, 1 - d);
      const t = d / p.w;
      if (t < 1) v = Math.max(v, p.a * (largos ? Math.cos((t * Math.PI) / 2) : Math.sqrt(1 - t * t)));
    }
    return v;
  };
}
