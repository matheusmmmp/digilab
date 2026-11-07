/* O toque digital do estilo Digital (docs/TAREFA_V3_MAPA_DIGITAL.md, etapa D3): so vista, sobre a mesma grade.
     - as particulas de dados: pequenos cristais ciano flutuando sobre a area e a moldura perto dela, que sobem e descem devagar e giram
       (o movimento e do shader, pelo uTempo da curva: parado com movimento reduzido); mais fortes a noite. Um InstancedMesh so;
     - a grade no ceu: linhas ciano fracas, desenhadas por cima do ceu pintado (meridianos que saem de um ponto de fuga acima da imagem e
       arcos em volta dele), so de dia; a noite fica o degrade de sempre;
     - os fios entre os postes: cada poste ligado aos vizinhos mais perto (ate DIGITAL.fios.alcance celulas), um fio pendurado (uma
       parabola) do alto de um ao do outro. Uma malha de segmentos so.
   Tudo deterministico (a rng da grade com um sal proprio); as contas ficam em digitalConta.ts, sem DOM. Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { carregarVariante, curvar } from "./cena.ts";
import { DIGITAL } from "./constantes.ts";
import { lugarDaLata, lugaresDasParticulas, segmentosDosFios } from "./digitalConta.ts";
import type { Ilha } from "./grade.ts";

/** as particulas, e o que a vista chama quando a noite muda */
export function particulas(ilha: Ilha): { malha: THREE.InstancedMesh; noite: (n: boolean) => void } {
  const P = DIGITAL.particulas;
  const mat = curvar(new THREE.MeshBasicMaterial({
    color: new THREE.Color(P.cor), transparent: true, opacity: P.opacidade[0], depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
  }), 0, {
    nome: "particula",
    glsl: `
#ifdef USE_INSTANCING
  vec3 baseP = instanceMatrix[3].xyz;
#else
  vec3 baseP = vec3(0.0);
#endif
float faseP = baseP.x * 1.7 + baseP.z * 0.9;
float giroP = uTempo * ${P.giro.toFixed(2)} + faseP;
transformed.xz = mat2(cos(giroP), -sin(giroP), sin(giroP), cos(giroP)) * transformed.xz;
transformed.y += sin(uTempo * ${P.vel.toFixed(2)} + faseP) * ${P.sobe.toFixed(2)};`,
  });
  const lugares = lugaresDasParticulas(ilha), malha = new THREE.InstancedMesh(new THREE.OctahedronGeometry(P.tamanho, 0), mat, lugares.length);
  const m = new THREE.Matrix4();
  lugares.forEach(([x, y, z], i) => malha.setMatrixAt(i, m.makeTranslation(x, y, z)));
  malha.frustumCulled = false;
  malha.renderOrder = 3;
  return { malha, noite: noite => { mat.opacity = P.opacidade[noite ? 1 : 0]; } };
}

/** o ceu pintado com a grade digital por cima: um canvas desenhado sobre a imagem ja carregada, que vira a imagem da textura do ceu */
export function ceuComGrade(img: HTMLImageElement | ImageBitmap): HTMLCanvasElement {
  const G = DIGITAL.grade, c = document.createElement("canvas");
  c.width = img.width; c.height = img.height;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  g.drawImage(img, 0, 0);
  const w = c.width, h = c.height, cx = w / 2, cy = -h * G.fuga;
  g.strokeStyle = G.cor; g.lineWidth = G.espessura; g.globalAlpha = G.alfa;
  /* os meridianos: do ponto de fuga (acima da imagem) para baixo, em leque */
  for (let k = -G.meridianos; k <= G.meridianos; k++) {
    g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + k * (w / G.meridianos) * 1.4, h); g.stroke();
  }
  /* os paralelos: arcos em volta do ponto de fuga, mais juntos perto dele */
  for (let k = 1; k <= G.paralelos; k++) {
    const raio = (h - cy) * Math.pow(k / G.paralelos, 1.6);
    g.beginPath(); g.arc(cx, cy, raio, 0, Math.PI); g.stroke();
  }
  return c;
}

/** a lata gigante (D4): o glTF de public/mapa_digital/lata/ (gerado pela Meshy, License.txt ao lado), na altura de DIGITAL.lata, sem sombra
    no chao; o `quadro` a poe no horizonte a cada quadro, pelo foco da camera (digitalConta.ts, lugarDaLata) */
export async function lata(ilha: Ilha, base: string):
    Promise<{ grupo: THREE.Group; quadro: (foco: readonly [number, number], dobra: number, dir: readonly [number, number], meiaLargura: number) => void }> {
  const L = DIGITAL.lata, { pecas } = await carregarVariante(new GLTFLoader(), new URL(L.arquivo, base).href,
    { arquivos: [L.arquivo], altura: L.altura, vento: 0, sombra: 0, baixo: false });
  const grupo = new THREE.Group();
  for (const p of pecas) {
    const m = new THREE.Mesh(p.geo, p.mat);
    (p.mat as THREE.MeshToonMaterial).fog = false;   /* longe, a nevoa do estilo a apagaria; o marco fica com as cores da maquete */
    m.matrixAutoUpdate = false;
    m.matrix.copy(p.local);
    m.frustumCulled = false;   /* o mundo curvo desce o que esta longe no shader: a caixa da malha nao vale */
    grupo.add(m);
  }
  grupo.rotation.y = L.giro;
  return {
    grupo,
    quadro: (foco, dobra, dir, meiaLargura) => { const { x, y, z } = lugarDaLata(ilha, foco, dobra, dir, meiaLargura); grupo.position.set(x, y, z); },
  };
}

/** os fios entre os postes: uma malha de segmentos (digitalConta.ts, segmentosDosFios) */
export function fios(ilha: Ilha): THREE.LineSegments {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(segmentosDosFios(ilha), 3));
  const l = new THREE.LineSegments(g, curvar(new THREE.LineBasicMaterial({ color: DIGITAL.fios.cor })));
  l.frustumCulled = false;
  return l;
}
