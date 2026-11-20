/* A ponte da ilha com agua (docs/TAREFA_V3_ILHA_AGUA.md, IA3): o tabuado e o corrimao de cada celula de ponte do mapa do motor, em
   formas lisas e cores chapadas (o padrao cartoon de 2026-11-10), feita por codigo, sem asset. A conta das caixas fica em ponteConta.ts
   (sem three); aqui so a malha: uma so, com a cor por vertice, no material do terreno (toon, com a dobra do mundo). So vista. */
import * as THREE from "three";
import { Malha, toon } from "./cena.ts";
import { PONTE_ILHA } from "./constantes.ts";
import type { Ilha } from "./grade.ts";
import { caixasDaPonte, type Caixa } from "./ponteConta.ts";

const corDe = (c: Caixa): THREE.Color =>
  new THREE.Color(c.peca === "tabua" ? PONTE_ILHA.cor.tabua[c.tom] : c.peca === "corrimao" ? PONTE_ILHA.cor.corrimao : PONTE_ILHA.cor.poste);

/** a malha das pontes da ilha (vazia de vertices se a ilha nao tem ponte) */
export function ponte(ilha: Ilha): THREE.Mesh {
  const m = new Malha(), v = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
  for (const c of caixasDaPonte(ilha)) {
    const [x0, y0, z0] = c.min, [x1, y1, z1] = c.max, k = corDe(c);
    m.quad(v(x0, y1, z0), v(x1, y1, z0), v(x1, y1, z1), v(x0, y1, z1), k, v(0, 1, 0));
    m.quad(v(x0, y0, z0), v(x1, y0, z0), v(x1, y1, z0), v(x0, y1, z0), k, v(0, 0, -1));
    m.quad(v(x0, y0, z1), v(x1, y0, z1), v(x1, y1, z1), v(x0, y1, z1), k, v(0, 0, 1));
    m.quad(v(x0, y0, z0), v(x0, y0, z1), v(x0, y1, z1), v(x0, y1, z0), k, v(-1, 0, 0));
    m.quad(v(x1, y0, z0), v(x1, y0, z1), v(x1, y1, z1), v(x1, y1, z0), k, v(1, 0, 0));
  }
  const malha = new THREE.Mesh(m.geometria(), toon({ vertexColors: true }));
  malha.name = "ponte";
  malha.frustumCulled = false;                 // a dobra do mundo muda onde a peca aparece (como as outras malhas dobradas da cena)
  return malha;
}
