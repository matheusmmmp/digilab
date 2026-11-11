/* MITOLOGIA, E0 (docs/TAREFA_V3_MITOLOGIA.md): o detalhe na ilha depois da brincadeira variada. Uma nuvenzinha dourada (a nuvem em que o
   macaco da lenda saltava) para sobre o ninho por um dia de jogo, e some. So com a chave `mitologia` ligada; o evento e o das lendas
   (motor/lendas.ts, funcao pura do pet refeito do log), recalculado so quando o log cresce. Nenhum texto, nenhum som: sutil de proposito. */
import * as THREE from "three";
import { detalheNoTick, lendas, type EventoLenda } from "../../../../motor/index.ts";
import type { Motor } from "../../../../motor/motor.ts";
import { toon } from "./cena.ts";

/** onde a nuvem para, a partir do ninho (unidades da ilha, uma por celula) e a altura; PROPOSTO, so vista */
const DESDE_NINHO: readonly [number, number] = [1.1, 0.2];
const ALTURA = 2.2, ESCALA = 0.62, BALANCO = 0.12, PERIODO_MS = 4200;

function nuvem(): THREE.Group {
  const g = new THREE.Group(), mat = toon({ color: 0xfff6d8, emissive: 0x8a6a1c, emissiveIntensity: 0.55 });
  for (const [x, y, z, r] of [[0, 0, 0, 0.42], [0.42, -0.05, 0.05, 0.32], [-0.4, -0.06, -0.02, 0.3], [0.12, 0.2, -0.08, 0.28]] as const) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 7).scale(1, 0.72, 1), mat);
    b.position.set(x, y, z);
    b.frustumCulled = false;                               // a dobra do mundo move o vertice no shader
    g.add(b);
  }
  g.scale.setScalar(ESCALA);
  return g;
}

export class NuvemDoDia {
  readonly raiz = new THREE.Group();
  private readonly g = nuvem();
  private cacheLog = -1;
  private cacheMotor: Motor | null = null;
  private eventos: EventoLenda[] = [];

  constructor(ninhoEm: readonly [number, number]) {
    this.g.position.set(ninhoEm[0] + DESDE_NINHO[0], ALTURA, ninhoEm[1] + DESDE_NINHO[1]);
    this.g.visible = false;
    this.raiz.add(this.g);
  }

  /** a cada quadro: visivel so com a chave e com um evento da brincadeira variada que ainda vale no tick */
  sincronizar(m: Motor, ligada: boolean, agora: number, reduzido: boolean): void {
    if (!ligada) { this.g.visible = false; return; }
    if (m !== this.cacheMotor || m.log.length !== this.cacheLog) {
      this.cacheMotor = m; this.cacheLog = m.log.length; this.eventos = lendas(m);
    }
    const e = detalheNoTick(this.eventos, m.e.tick);
    this.g.visible = e !== null;
    if (e && !reduzido) this.g.position.y = ALTURA + BALANCO * Math.sin((agora / PERIODO_MS) * Math.PI * 2);
  }
}
