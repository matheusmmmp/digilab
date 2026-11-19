/* As tacas da temporada na cena (MMO7): o modelo de docs/objetos3d/cartoon/trofeu.py, uma taca por temporada ganha, nos pontos de
   premiosConta.ts, perto do cais, com a sombra redonda como os enfeites. A frente (a estrela) fica para o sul (+z do glTF), para a camera.
   So vista: quem diz quais temporadas e o servidor (trancas.ts, TACAS_DA_CONTA). */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { GEO_SOMBRA, carregarVariante, materialSombra } from "./cena.ts";
import type { Ilha } from "./grade.ts";
import { PREMIOS_MODELOS } from "./modelos.ts";
import { pontosDasTacas } from "./premiosConta.ts";

/** o grupo das `n` tacas (vazio se n = 0 ou se nao ha lugar perto do cais); falha alto se o arquivo nao carrega */
export async function montarTacas(ilha: Ilha, base: string, n: number): Promise<THREE.Group> {
  const grupo = new THREE.Group();
  grupo.name = "tacas_da_temporada";
  const pontos = pontosDasTacas(ilha, n);
  if (!pontos.length) return grupo;
  const m = PREMIOS_MODELOS.trofeu;
  const { pecas } = await carregarVariante(new GLTFLoader(), new URL("enfeites/" + m.arquivos[0], base).href, m);
  const lugar = pontos.map(([x, z]) => new THREE.Matrix4().makeTranslation(x, ilha.altura(x, z), z));
  for (const p of pecas) {
    const im = new THREE.InstancedMesh(p.geo, p.mat, lugar.length);
    lugar.forEach((l, i) => im.setMatrixAt(i, l.clone().multiply(p.local)));
    im.frustumCulled = false;     // a dobra muda onde a peca aparece
    grupo.add(im);
  }
  const s = new THREE.InstancedMesh(GEO_SOMBRA, materialSombra(), pontos.length);
  pontos.forEach(([x, z], i) => s.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(x, ilha.altura(x, z) + 0.02, z),
    new THREE.Quaternion(), new THREE.Vector3(m.sombra * 2, 1, m.sombra * 2))));
  s.frustumCulled = false;
  s.renderOrder = 1;
  grupo.add(s);
  return grupo;
}
