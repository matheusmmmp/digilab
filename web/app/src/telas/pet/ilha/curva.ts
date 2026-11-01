/* O mundo curvo da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, regra 6 e H2), sem three e sem DOM: a mesma dobra do shader (cena.ts,
   GLSL_PROJETAR, a do POC poc/mapa_ac/cena.ts), y' = y - k (z - foco)^2, e o caminho de volta da tela ao chao dobrado.
   - paraTela: o ponto do chao (em celulas) desce pela dobra e entra na camera (o projetar dela devolve as coordenadas normalizadas);
   - paraMundo: o raio da camera (origem o, direcao d) encontra a superficie dobrada y = yChao - k (z - foco)^2 numa equacao do segundo
     grau em t, sem iteracao: a t^2 + b t + c = 0, com a = k dz^2, b = dy + 2 k dz (oz - foco), c = oy - yChao + k (oz - foco)^2. Vale a
     menor raiz positiva (o primeiro toque do raio no chao).
   A camera entra pelo que a vista sabe dela (CameraLida), para os testes conferirem com uma camera do three sem DOM. */

/** a dobra: a forca k (por celula) e o foco (o pet), em celulas. Sem `dir`, ela dobra ao longo de z (a camera que nao gira); com a camera
    livre, ao longo da direcao [x, z] (unitaria, no chao) para onde a camera olha: s = (x - focoX) dir.x + (z - focoZ) dir.z */
export interface Dobra { k: number; focoZ: number; focoX?: number; dir?: readonly [number, number] }
/** a distancia ao foco ao longo do eixo da dobra */
const eixo = (x: number, z: number, d: Dobra): number => d.dir ? (x - (d.focoX ?? 0)) * d.dir[0] + (z - d.focoZ) * d.dir[1] : z - d.focoZ;
/** o que a curva precisa da camera: o ponto do mundo em coordenadas normalizadas da tela (-1 a 1) e o raio de um ponto da tela */
export interface CameraLida {
  projetar(x: number, y: number, z: number): [number, number];
  raio(nx: number, ny: number): { o: [number, number, number]; d: [number, number, number] };
}

/** a altura dobrada de um ponto do mundo (a do shader) */
export const dobrarY = (y: number, z: number, dobra: Dobra, x = dobra.focoX ?? 0): number => y - dobra.k * eixo(x, z, dobra) ** 2;

/** onde o raio o + t d toca o chao dobrado na altura yChao; [x, z] em celulas, ou null se nao toca na frente da camera. Ao longo do raio,
    o eixo da dobra e u + t w (u o da origem, w o da direcao), e a conta e a mesma do eixo z */
export function tocarChao(o: readonly [number, number, number], d: readonly [number, number, number], dobra: Dobra, yChao = 0): [number, number] | null {
  const u = eixo(o[0], o[2], dobra), w = dobra.dir ? d[0] * dobra.dir[0] + d[2] * dobra.dir[1] : d[2];
  const a = dobra.k * w * w, b = d[1] + 2 * dobra.k * w * u, c = o[1] - yChao + dobra.k * u * u;
  let t: number;
  if (Math.abs(a) < 1e-12) {
    if (Math.abs(b) < 1e-12) return null;
    t = -c / b;
  } else {
    const disc = b * b - 4 * a * c;
    if (disc < 0) return null;
    const r = Math.sqrt(disc), t1 = (-b - r) / (2 * a), t2 = (-b + r) / (2 * a);
    t = t1 > 1e-9 && t2 > 1e-9 ? Math.min(t1, t2) : t1 > 1e-9 ? t1 : t2;
  }
  if (!(t > 1e-9)) return null;
  return [o[0] + t * d[0], o[2] + t * d[2]];
}

/** o ponto do chao (celulas, na altura y) nas coordenadas normalizadas da tela, ja dobrado */
export const paraTelaNdc = (cam: CameraLida, dobra: Dobra, x: number, z: number, y = 0): [number, number] => cam.projetar(x, dobrarY(y, z, dobra, x), z);

/** o ponto normalizado da tela no chao dobrado (celulas), ou null (o ceu, ou atras da camera) */
export function paraMundoCel(cam: CameraLida, dobra: Dobra, nx: number, ny: number, yChao = 0): [number, number] | null {
  const { o, d } = cam.raio(nx, ny);
  return tocarChao(o, d, dobra, yChao);
}
