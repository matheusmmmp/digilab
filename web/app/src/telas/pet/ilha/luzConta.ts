/* As contas da hierarquia de luz (cena.ts, o termo no shader do curvar; LUZ_HIERARQUIA em constantes.ts), sem DOM, para o teste:
   a proposta da pagina (`?luz=`), quais materiais recebem o termo e os focos da planta A. PROTOTIPO da prancha docs/pranchas/ux-ilha-luz/:
   sem `?luz=` nada daqui liga. Os numeros sao PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { LUZ_HIERARQUIA, PLANTA_ILHA } from "./constantes.ts";
import type { Ilha } from "./grade.ts";

export type PropostaLuz = keyof typeof LUZ_HIERARQUIA.propostas;
/** a proposta da pagina (`?luz=`), ou null: sem ela nenhum shader muda */
export const LUZ_PROPOSTA: PropostaLuz | null = (() => {
  try {
    const q = new URLSearchParams(location.search).get("luz");
    return q === "a" || q === "b" || q === "c" ? q : null;
  } catch { return null; }
})();
export const LUZ_MAX = 48;
/** o peso da luz no material: 1, ou LUZ_HIERARQUIA.pesoChao no chao, nas flores e nos tufos (userData.luzChao), para a grama nao
    ficar cinza; o que muda a cor e o que fica de pe (arvores, pedras, enfeites, lugares) */
export const pesoLuz = (m: THREE.Material): number => m.userData.luzChao ? LUZ_HIERARQUIA.pesoChao : 1;
export const recebeLuz = (m: THREE.Material, proposta = LUZ_PROPOSTA): boolean => proposta !== null && m.blending !== THREE.AdditiveBlending
  && !(m.transparent && !m.depthWrite) && !(m as THREE.LineBasicMaterial).isLineBasicMaterial;
/** os focos da luz (x, z, raio em celulas): os destinos e os caminhos da planta A, com o lar no ninho do layout. Sem three e sem DOM */
export function listaDeFocos(ilha: Ilha): [number, number, number][] {
  const R = LUZ_HIERARQUIA.raio, L = ilha.cm.layout, f: [number, number, number][] = [];
  f.push([L.ninho[0] + 0.5, L.ninho[1] + 0.5, R.lar], [(L.ninho[0] + L.comedouro[0]) / 2 + 0.5, (L.ninho[1] + L.comedouro[1]) / 2 + 0.5, R.lar]);
  f.push([PLANTA_ILHA.praca.x, PLANTA_ILHA.praca.z, R.praca]);
  for (const l of ilha.lugares) f.push([l.x, l.z, R[l.nome as keyof typeof R] ?? R.portao]);
  for (const c of ilha.caminhos) for (let k = 1; k < c.length; k++) {
    const [ax, az] = c[k - 1], [bx, bz] = c[k], n = Math.max(1, Math.round(Math.hypot(bx - ax, bz - az) / LUZ_HIERARQUIA.passo));
    for (let t = 0; t <= n; t++) f.push([ax + ((bx - ax) * t) / n, az + ((bz - az) * t) / n, LUZ_HIERARQUIA.raioCaminho]);
  }
  if (f.length > LUZ_MAX) throw new Error(`luz: ${f.length} focos, o maximo e ${LUZ_MAX}`);
  return f;
}
