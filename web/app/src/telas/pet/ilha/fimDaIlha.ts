/* O fim da ilha (o Matheus, 2026-11-08: "adicionar um final [...] para a ilha, para ela nao acabar no meio do nada"; FIM_ILHA em
   constantes.ts; docs/pranchas/ux-ilha-planta-a/). So vista: nada daqui entra no motor, no save nem no replay.
   - o mar em volta da grade inteira, ate o horizonte, com a agua da ilha (cena.ts, materialAgua): debaixo da terra ele nao aparece, e alem
     da moldura ele encontra o ceu, em qualquer direcao da camera;
   - as silhuetas ao longe: duas faixas cilindricas em volta do ponto olhado (o foco da camera), com as ilhas perto e os morros longe,
     desenhadas num canvas com uma rng propria. Elas nao dobram com o mundo curvo: a cada quadro o pe vai para a linha do horizonte do mar
     curvo vista da camera, menos FIM_ILHA.silhuetas.fundo, e o mar curvo na frente cobre o pe. A cor e a da nevoa (o horizonte do dia ou
     da noite, de cada estilo) puxada para a cor de baixo da luz do ceu: nenhuma cor nova.
   Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { AGUA_FRAG, materialAgua } from "./cena.ts";
import { FIM_ILHA } from "./constantes.ts";
import { NIVEL_AGUA, rng, sementeDoLayout, type Ilha } from "./grade.ts";

export interface FimDaIlha {
  grupo: THREE.Group;
  /** a cada quadro: o foco (celulas), a dobra, a direcao dela no chao, a camera, a altura do chao no foco e a cor de baixo da luz do ceu */
  quadro: (foco: readonly [number, number], dobra: number, dir: readonly [number, number], camera: THREE.Camera, chao: number,
    nevoa: THREE.Color, sombra: THREE.Color) => void;
}

/** a linha do horizonte do mar curvo vista da camera, a `raio` celulas do foco (a altura, em celulas, em relacao ao chao do foco). A camera
    esta `h` acima do chao do foco e `c` atras dele, na direcao da dobra; o mar cai `dobra * d^2` a `d` do foco. A reta da camera que tangencia o
    mar toca em d* = -c + sqrt(c^2 + h / dobra), com a inclinacao -2 dobra d*; sem dobra, o horizonte e o nivel da agua */
export function horizonte(h: number, c: number, dobra: number, raio: number): number {
  if (dobra <= 0) return NIVEL_AGUA;
  const d = -c + Math.sqrt(c * c + Math.max(h, 0.01) / dobra), m = -2 * dobra * d;
  return h + m * (raio + c);
}

/** o perfil de uma faixa, por volta (0 a 1): picos que se repetem na volta, sem emenda; 0 e o mar aberto, 1 a altura toda */
export function perfil(semente: number, picos: number, largos: boolean): (u: number) => number {
  const r = rng(semente), lista = Array.from({ length: picos }, () => ({ u: r(), a: 0.45 + r() * 0.55, w: (largos ? 0.05 : 0.018) + r() * (largos ? 0.07 : 0.03) }));
  return u => {
    let v = 0;
    for (const p of lista) {
      let d = Math.abs(u - p.u);
      d = Math.min(d, 1 - d);
      const t = d / p.w;
      if (t < 1) v = Math.max(v, p.a * (largos ? Math.cos((t * Math.PI) / 2) : Math.sqrt(1 - t * t)));
    }
    return v;
  };
}

/* a mascara da faixa: branco ate o perfil, transparente acima; a ilha tem um pe de praia mais largo (o cos da borda) */
function textura(f: (u: number) => number, alto: number): THREE.CanvasTexture {
  const W = 2048, H = 256, c = document.createElement("canvas");
  c.width = W; c.height = H;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  g.fillStyle = "#fff";
  g.beginPath();
  g.moveTo(0, H);
  for (let i = 0; i <= W; i++) g.lineTo(i, H - H * alto * f(i / W) - 1);
  g.lineTo(W, H);
  g.closePath();
  g.fill();
  const t = new THREE.CanvasTexture(c);
  t.wrapS = THREE.RepeatWrapping;
  return t;
}

/** o fim da ilha: o mar em volta e as duas faixas de silhuetas */
export function fimDaIlha(ilha: Ilha): FimDaIlha {
  const F = FIM_ILHA, S = F.silhuetas, grupo = new THREE.Group(), semente = sementeDoLayout(ilha.cm.layout.nome) ^ S.sal;
  /* o mar: um quadrado grande no nivel da agua, um pouco abaixo do mar da grade (que fica por cima onde os dois existem) */
  const cx = ilha.x0 + ilha.larg / 2, cz = ilha.z0 + ilha.prof / 2;
  const mar = new THREE.PlaneGeometry(F.mar, F.mar, 48, 48).rotateX(-Math.PI / 2).translate(cx, NIVEL_AGUA - 0.03, cz);
  mar.setAttribute("aMargem", new THREE.Float32BufferAttribute(new Array(mar.attributes.position.count).fill(6), 1));
  grupo.add(Object.assign(new THREE.Mesh(mar, materialAgua(AGUA_FRAG)), { frustumCulled: false, renderOrder: -1 }));
  /* as faixas: um cilindro aberto por camada, visto de dentro; a de longe primeiro */
  const faixas = ([["longe", S.longe, true], ["perto", S.perto, false]] as const).map(([nome, L, largos], k) => {
    const picos = "morros" in L ? L.morros : L.ilhas;
    const mat = new THREE.MeshBasicMaterial({ map: textura(perfil(semente + k * 7919, picos, largos), L.alto), transparent: true, alphaTest: 0.5,
      side: THREE.BackSide, fog: false, depthWrite: false });
    const m = new THREE.Mesh(new THREE.CylinderGeometry(L.raio, L.raio, S.altura, 128, 1, true), mat);
    m.name = "silhueta_" + nome;
    m.frustumCulled = false;
    m.renderOrder = -1 + k * 0.1;
    grupo.add(m);
    return { m, mat, L };
  });
  const v = new THREE.Vector3();
  return {
    grupo,
    quadro: (foco, dobra, dir, camera, chao, nevoa, sombra) => {
      camera.getWorldPosition(v);
      const h = v.y - chao, c = -((v.x - foco[0]) * dir[0] + (v.z - foco[1]) * dir[1]);
      for (const { m, mat, L } of faixas) {
        const pe = chao + horizonte(h, c, dobra, L.raio) - S.fundo;
        m.position.set(foco[0], pe + S.altura / 2, foco[1]);
        mat.color.copy(nevoa).lerp(sombra, L.sombra);
      }
    },
  };
}
