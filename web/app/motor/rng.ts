/* RNG do jogo web (mulberry32) e hash de semente (FNV-1a 32 bits). Porte exato do HTML: a ORDEM de
   consumo das sequencias e parte do registro (replay). Nao reproduz os artefatos Python (outro gerador). */

export interface Rng {
  random(): number;
  gauss(): number;
  escolher<T>(itens: readonly T[], pesos: readonly number[]): T;
  int(n: number): number;
}

export function criarRng(seed: number): Rng {
  let a = seed >>> 0;
  const r: Rng = {
    random() { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; },
    gauss() { let u = 0; while (u === 0) u = r.random(); const v = r.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
    escolher(itens, pesos) { const tot = pesos.reduce((s, w) => s + w, 0); let x = r.random() * tot; for (let i = 0; i < itens.length; i++) { x -= pesos[i]; if (x < 0) return itens[i]; } return itens[itens.length - 1]; },
    int(n) { return Math.floor(r.random() * n); },
  };
  return r;
}

/** semente derivada das partes (juntas por "|"), iterando por ponto de codigo como o HTML */
export function hashSemente(...partes: (string | number)[]): number {
  let h = 2166136261 >>> 0;
  for (const c of partes.join("|")) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; }
  return h;
}
