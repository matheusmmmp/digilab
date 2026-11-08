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
import { horizonte, perfil } from "./fimConta.ts";
import { NIVEL_AGUA, sementeDoLayout, type Ilha } from "./grade.ts";

export interface FimDaIlha {
  grupo: THREE.Group;
  /** a cada quadro: o foco (celulas), a dobra, a direcao dela no chao, a camera, a altura do chao no foco e a cor de baixo da luz do ceu */
  quadro: (foco: readonly [number, number], dobra: number, dir: readonly [number, number], camera: THREE.Camera, chao: number,
    nevoa: THREE.Color, sombra: THREE.Color) => void;
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
