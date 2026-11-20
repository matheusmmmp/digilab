/* As tacas da temporada na ilha (MMO7, docs/PLANO_V3_MMO.md secao 7; o enfeite que nao se vende na loja), sem three e sem DOM, para o
   teste ler no node: onde cada taca fica, perto do cais. So vista: nada daqui entra no motor, no log nem no save; quem diz que a conta
   ganhou a taca e o servidor (GET /premios, cais/premios.ts), e sem a chave do cais nada daqui roda.

   O lugar: as celulas de terra plana mais perto do cais, fora do pier, longe dos objetos, dos enfeites e dos outros lugares, uma taca por
   temporada ganha (as mais novas primeiro), ate TACAS_NA_ILHA. Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import type { Ilha } from "./grade.ts";

export const TACAS = {
  /** a distancia ao centro do cais: o pier tem ~5,7 x 5,8 celulas, entao a taca fica alem da meia diagonal dele, e nao longe demais */
  deCais: { min: 4.2, max: 10 },
  /** a folga ate um objeto, um enfeite ou outro lugar, e entre duas tacas */
  folga: 1.8,
  entreTacas: 1.6,
} as const;
/** quantas tacas a ilha mostra (as das temporadas mais novas) */
export const TACAS_NA_ILHA = 4;

/** os pontos das tacas (x, z em celulas, no centro da celula), do mais perto do cais ao mais longe; menos que `n` se nao houver lugar */
export function pontosDasTacas(ilha: Ilha, n: number): [number, number][] {
  const cais = ilha.lugares.find(l => l.nome === "cais");
  if (!cais || n <= 0) return [];
  const ocupado: [number, number][] = [
    ...ilha.objetos.map(o => [o.x, o.z] as [number, number]), ...ilha.extras.map(o => [o.x, o.z] as [number, number]),
    ...ilha.enfeites.map(e => [e.x, e.z] as [number, number]), ...ilha.lugares.filter(l => l.nome !== "cais").map(l => [l.x, l.z] as [number, number]),
  ];
  const cand: { x: number; z: number; d: number }[] = [];
  const r = Math.ceil(TACAS.deCais.max);
  for (let dz = -r; dz <= r; dz++) for (let dx = -r; dx <= r; dx++) {
    const cx = Math.floor(cais.x) + dx, cz = Math.floor(cais.z) + dz, x = cx + 0.5, z = cz + 0.5;
    const d = Math.hypot(x - cais.x, z - cais.z);
    if (d < TACAS.deCais.min || d > TACAS.deCais.max) continue;
    const c = ilha.cel(cx, cz);
    if (!c || c.tipo === "agua" || c.cantos.some(h => h !== c.cantos[0])) continue;
    if (ocupado.some(([ox, oz]) => Math.hypot(ox - x, oz - z) < TACAS.folga)) continue;
    cand.push({ x, z, d });
  }
  /* o mais perto primeiro; no empate, a ordem da grade (z, depois x) */
  cand.sort((a, b) => a.d - b.d || a.z - b.z || a.x - b.x);
  const out: [number, number][] = [];
  for (const p of cand) {
    if (out.length >= n) break;
    if (out.some(([x, z]) => Math.hypot(x - p.x, z - p.z) < TACAS.entreTacas)) continue;
    out.push([p.x, p.z]);
  }
  return out;
}

/** as temporadas que a ilha mostra: as mais novas, ate TACAS_NA_ILHA */
export const temporadasNaIlha = (temporadas: readonly number[]): number[] => [...new Set(temporadas)].sort((a, b) => b - a).slice(0, TACAS_NA_ILHA);
