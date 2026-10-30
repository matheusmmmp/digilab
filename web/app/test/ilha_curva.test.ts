/* O mundo curvo da ilha (src/telas/pet/ilha/curva.ts; docs/TAREFA_V3_HABITAT_ILHA_3D.md, regra 6): com a camera do POC (H-3) atras do
   pet, paraMundo(paraTela(p)) == p com ate 1 subunidade de diferenca, em pontos do mapa todo, com o foco em varios lugares. Vale para o
   que a camera ve: os pontos na tela, entre o horizonte da dobra e a camera. O raio que nao toca o chao (o ceu) da null. */
import * as THREE from "three";
import { describe, expect, test } from "vitest";
import { CMU_MVP } from "../motor/index.ts";
import { CAMERA_DESLOC, CAMERA_OLHAR, DOBRA_K, FOV_GRAUS } from "../src/telas/pet/ilha/constantes.ts";
import { dobrarY, paraMundoCel, paraTelaNdc, tocarChao, type CameraLida } from "../src/telas/pet/ilha/curva.ts";

const cm = CMU_MVP, sub = cm.sub;

function cameraEm(px: number, pz: number, aspecto: number, afast = 1): CameraLida {
  const c = new THREE.PerspectiveCamera(FOV_GRAUS, aspecto, 0.1, 200);
  c.position.set(px + CAMERA_DESLOC[0] * afast, CAMERA_DESLOC[1] * afast, pz + CAMERA_DESLOC[2] * afast);
  c.lookAt(px + CAMERA_OLHAR[0] * afast, CAMERA_OLHAR[1] * afast, pz + CAMERA_OLHAR[2] * afast);
  c.updateMatrixWorld(); c.updateProjectionMatrix();
  const v = new THREE.Vector3(), r = new THREE.Raycaster();
  return {
    projetar: (x, y, z) => { v.set(x, y, z).project(c); return [v.x, v.y]; },
    raio: (nx, ny) => { r.setFromCamera(new THREE.Vector2(nx, ny), c); const { origin: o, direction: d } = r.ray; return { o: [o.x, o.y, o.z], d: [d.x, d.y, d.z] }; },
  };
}

/** o horizonte da dobra, em celulas a partir do foco (negativo: ao norte): onde o raio da camera tangencia y = -k u^2. A tangente em u0
    passa pela camera (u = Z, y = Y): k u0^2 - 2 k Z u0 - Y = 0 */
function horizonte(afast: number): number {
  const Z = CAMERA_DESLOC[2] * afast, Y = CAMERA_DESLOC[1] * afast, k = DOBRA_K;
  return (2 * k * Z - Math.sqrt(4 * k * k * Z * Z + 4 * k * Y)) / (2 * k);
}

describe("o mundo curvo", () => {
  test("a dobra e a do shader: zero no foco, cai pelo quadrado da distancia", () => {
    expect(dobrarY(0, 10, { k: DOBRA_K, focoZ: 10 })).toBe(0);
    expect(dobrarY(1, 15, { k: 0.01, focoZ: 10 })).toBeCloseTo(1 - 0.25, 12);
    /* sem dobra, o raio vertical toca o chao embaixo dele */
    expect(tocarChao([3, 5, 7], [0, -1, 0], { k: 0, focoZ: 0 })).toEqual([3, 7]);
    /* o raio para cima nao toca o chao */
    expect(tocarChao([3, 5, 7], [0, 1, 0], { k: DOBRA_K, focoZ: 7 })).toBeNull();
  });

  for (const [nome, aspecto, afast] of [["desktop", 1280 / 800, 1], ["celular", 390 / 844, 2.4]] as const)
    test(`ida e volta com ate 1 subunidade em pontos do mapa todo (${nome})`, () => {
      let conferidos = 0;
      for (const [fx, fz] of [[5, 5], [32, 15], [60, 28], [10, 29], [63, 0]] as const) {
        const cam = cameraEm(fx, fz, aspecto, afast), dobra = { k: DOBRA_K, focoZ: fz };
        for (let ys = 0; ys < cm.celulas_y * sub; ys += 7) for (let xs = 0; xs < cm.celulas_x * sub; xs += 11) {
          const x = xs / sub, z = ys / sub;
          /* so o que a camera ve: na tela e aquem do horizonte da dobra, com 2 celulas de folga */
          if (z < fz + horizonte(afast) + 2) continue;
          const [nx, ny] = paraTelaNdc(cam, dobra, x, z);
          if (Math.abs(nx) > 1 || Math.abs(ny) > 1) continue;
          const p = paraMundoCel(cam, dobra, nx, ny);
          expect(p, `${xs},${ys} com o foco em ${fx},${fz}`).not.toBeNull();
          expect(Math.abs(Math.round(p![0] * sub) - xs), `x de ${xs},${ys}`).toBeLessThanOrEqual(1);
          expect(Math.abs(Math.round(p![1] * sub) - ys), `y de ${xs},${ys}`).toBeLessThanOrEqual(1);
          conferidos++;
        }
      }
      expect(conferidos).toBeGreaterThan(300);
    });

  test("o topo da tela (o ceu, alem do horizonte da dobra) nao vira um ponto do chao", () => {
    const cam = cameraEm(32, 15, 1280 / 800);
    expect(paraMundoCel(cam, { k: DOBRA_K, focoZ: 15 }, 0, 0.99)).toBeNull();
  });
});
