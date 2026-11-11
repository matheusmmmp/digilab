/* O fim da ilha (o Matheus, 2026-11-08: "adicionar um final [...] para a ilha, para ela nao acabar no meio do nada"; FIM_ILHA em
   constantes.ts; docs/pranchas/ux-ilha-planta-a/). So vista: nada daqui entra no motor, no save nem no replay.
   - o mar em volta da grade inteira, ate o horizonte, com a agua da ilha (cena.ts, materialAgua): debaixo da terra ele nao aparece, e alem
     da moldura ele encontra o ceu, em qualquer direcao da camera.
   - as silhuetas ao longe (as ilhas e os morros) sairam em 2026-11-10: o Matheus as leu como "uns negocios verde esquisito solto no ceu".
   Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { AGUA_FRAG, materialAgua } from "./cena.ts";
import { FIM_ILHA } from "./constantes.ts";
import { NIVEL_AGUA, type Ilha } from "./grade.ts";

export interface FimDaIlha {
  grupo: THREE.Group;
}

/** o fim da ilha: o mar em volta, ate o horizonte */
export function fimDaIlha(ilha: Ilha): FimDaIlha {
  const F = FIM_ILHA, grupo = new THREE.Group();
  /* o mar: um quadrado grande no nivel da agua, um pouco abaixo do mar da grade (que fica por cima onde os dois existem) */
  const cx = ilha.x0 + ilha.larg / 2, cz = ilha.z0 + ilha.prof / 2;
  const mar = new THREE.PlaneGeometry(F.mar, F.mar, 48, 48).rotateX(-Math.PI / 2).translate(cx, NIVEL_AGUA - 0.03, cz);
  mar.setAttribute("aMargem", new THREE.Float32BufferAttribute(new Array(mar.attributes.position.count).fill(6), 1));
  grupo.add(Object.assign(new THREE.Mesh(mar, materialAgua(AGUA_FRAG)), { frustumCulled: false, renderOrder: -1 }));
  return { grupo };
}
