/* O toque digital do estilo Digital (docs/TAREFA_V3_MAPA_DIGITAL.md, etapa D3): so vista, sobre a mesma grade.
     - as particulas de dados: pequenos cristais ciano flutuando sobre a area e a moldura perto dela, que sobem e descem devagar e giram
       (o movimento e do shader, pelo uTempo da curva: parado com movimento reduzido); mais fortes a noite. Um InstancedMesh so;
     - a grade no ceu: linhas ciano fracas, desenhadas por cima do ceu pintado (meridianos que saem de um ponto de fuga acima da imagem e
       arcos em volta dele), so de dia; a noite fica o degrade de sempre;
     - os fios entre os postes: cada poste ligado aos vizinhos mais perto (ate DIGITAL.fios.alcance celulas), um fio pendurado (uma
       parabola) do alto de um ao do outro. Uma malha de segmentos so.
   Tudo deterministico (a rng da grade com um sal proprio). Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { curvar } from "./cena.ts";
import { DIGITAL } from "./constantes.ts";
import { rng, type Ilha } from "./grade.ts";
import { ENFEITES_MODELOS } from "./modelos.ts";

/** as particulas, e o que a vista chama quando a noite muda */
export function particulas(ilha: Ilha): { malha: THREE.InstancedMesh; noite: (n: boolean) => void } {
  const P = DIGITAL.particulas, r = rng(P.sal), n = P.quantas;
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
  const malha = new THREE.InstancedMesh(new THREE.OctahedronGeometry(P.tamanho, 0), mat, n);
  const m = new THREE.Matrix4();
  for (let i = 0; i < n; i++) {
    const x = -P.margem + r() * (ilha.area.w + 2 * P.margem), z = -P.margem + r() * (ilha.area.h + 2 * P.margem);
    m.makeTranslation(x, ilha.altura(x, z) + P.altura[0] + r() * (P.altura[1] - P.altura[0]), z);
    malha.setMatrixAt(i, m);
  }
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

/** os fios entre os postes: uma malha de segmentos */
export function fios(ilha: Ilha): THREE.LineSegments {
  const F = DIGITAL.fios, postes = ilha.enfeites.filter(e => e.nome === "poste");
  const topo = (e: { x: number; z: number }) => new THREE.Vector3(e.x, ilha.altura(e.x, e.z) + ENFEITES_MODELOS.poste.altura * F.alto, e.z);
  const ligados = new Set<string>(), pos: number[] = [];
  postes.forEach((a, i) => {
    const viz = postes.map((b, j) => ({ j, d: Math.hypot(a.x - b.x, a.z - b.z) })).filter(v => v.j !== i && v.d <= F.alcance)
      .sort((p, q) => p.d - q.d);
    for (const v of viz.slice(0, F.porPoste)) {
      const chave = `${Math.min(i, v.j)}-${Math.max(i, v.j)}`;
      if (ligados.has(chave)) continue;
      ligados.add(chave);
      const p0 = topo(a), p1 = topo(postes[v.j]), queda = v.d * F.queda;
      let ant = p0;
      for (let s = 1; s <= F.segmentos; s++) {
        const u = s / F.segmentos, p = p0.clone().lerp(p1, u);
        p.y -= 4 * queda * u * (1 - u);
        pos.push(ant.x, ant.y, ant.z, p.x, p.y, p.z);
        ant = p;
      }
    }
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  const l = new THREE.LineSegments(g, curvar(new THREE.LineBasicMaterial({ color: F.cor })));
  l.frustumCulled = false;
  return l;
}
