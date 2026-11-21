/* O ovo no centro da clareira (mapa_ac.html?mapa=clareira): um torno (LatheGeometry) com o perfil de ovo, o material toon do mapa e
   manchas desenhadas num canvas, em pé sobre a laje, com um balanço lento de quem vai chocar. Só desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GEO_SOMBRA, materialSombra, toon } from "./cena.ts";

const ALTURA = 0.95, RAIO = 0.36;

function texturaManchas(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = 64; c.height = 64;
  const g = c.getContext("2d")!;
  g.fillStyle = "#fbf6e8";
  g.fillRect(0, 0, 64, 64);
  g.fillStyle = "#5fbf6a";
  for (const [x, y, r] of [[10, 22, 5], [30, 34, 7], [52, 20, 5], [44, 46, 4], [18, 48, 4], [62, 38, 4], [2, 40, 4]]) {
    g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.magFilter = t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  t.wrapS = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export class Ovo {
  readonly raiz = new THREE.Group();
  private readonly corpo: THREE.Mesh;

  constructor(x: number, y: number, z: number) {
    /* o perfil: mais largo abaixo do meio, a ponta fina em cima */
    const pontos: THREE.Vector2[] = [];
    for (let i = 0; i <= 16; i++) {
      const t = i / 16, a = t * Math.PI;
      const r = Math.sin(a) * RAIO * (1 - 0.18 * t);
      pontos.push(new THREE.Vector2(Math.max(r, 1e-4), (1 - Math.cos(a)) / 2 * ALTURA));
    }
    this.corpo = new THREE.Mesh(new THREE.LatheGeometry(pontos, 20), toon({ map: texturaManchas() }));
    this.raiz.add(this.corpo);
    const sombra = new THREE.Mesh(GEO_SOMBRA, materialSombra());
    sombra.scale.set(RAIO * 2.6, 1, RAIO * 2.6);
    sombra.position.y = 0.02;
    sombra.renderOrder = 1;
    this.raiz.add(sombra);
    this.raiz.position.set(x, y + 0.08, z);
  }

  atualizar(agora: number): void {
    const t = agora / 1000;
    this.corpo.rotation.z = Math.sin(t * 2.1) * 0.06 * Math.max(0, Math.sin(t * 0.45));
  }
}
