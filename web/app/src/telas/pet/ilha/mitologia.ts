/* MITOLOGIA na ilha (docs/TAREFA_V3_MITOLOGIA.md, E0 e E1). So com a chave `mitologia` ligada; tudo sai das lendas (motor/lendas.ts e
   motor/lendas_e1.ts, funcao pura do pet refeito do log), recalculadas so quando o log cresce. Nenhum texto e nenhum som: sutil de proposito.
     - os sinais dos cinco deuses, cada um por um dia de jogo depois do evento: a nuvenzinha dourada da Diversao (E0) sobre o ninho, a chama
       da Coragem, as duas flores da Amizade, o marco do Conhecimento e o broto da Sinceridade em volta dele; no dia 81, os cinco juntos;
     - a pedra do macaco na mata (sempre, com a chave) e, depois de muita exploracao la, as pegadas do ninho ate ela;
     - o pessego dourado perto do ninho por um dia, para quem decifrou o enigma do Jijimon (src/mitologia.ts);
     - o Myotismon: com a repeticao a exaustao, morcegos sobre o ninho e o canvas mais escuro (o atributo data-myotismon no <html>). */
import * as THREE from "three";
import {
  DEUSES, diaDeVida, CMIT_E1, myotismonNoTick, pedraEm, pegadasDe, sinaisDe, sinaisNoTick, type Deus,
} from "../../../../motor/index.ts";
import type { Motor } from "../../../../motor/motor.ts";
import { enigmaResolvidoEm } from "../../../mitologia.ts";
import { toon } from "./cena.ts";

const TPD_DIA = 1440;
/** onde cada sinal fica, a partir do ninho (unidades da ilha) e a altura; PROPOSTO, so vista */
const POS_SINAL: Readonly<Record<Deus, readonly [number, number, number]>> = {
  diversao: [1.1, 2.2, 0.2], coragem: [-1.5, 0, 0.9], amizade: [1.5, 0, 1.1], conhecimento: [-1.3, 0, -1.2], sinceridade: [1.3, 0, -1.1],
};
const POS_PESSEGO: readonly [number, number] = [0.2, 1.5];
const BALANCO = 0.12, PERIODO_MS = 4200, N_PEGADAS = 14;

const malha = (geo: THREE.BufferGeometry, mat: THREE.Material, x = 0, y = 0, z = 0) => {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.frustumCulled = false;                                 // a dobra do mundo move o vertice no shader
  return m;
};

function nuvem(): THREE.Group {
  const g = new THREE.Group(), mat = toon({ color: 0xfff6d8, emissive: 0x8a6a1c, emissiveIntensity: 0.55 });
  for (const [x, y, z, r] of [[0, 0, 0, 0.42], [0.42, -0.05, 0.05, 0.32], [-0.4, -0.06, -0.02, 0.3], [0.12, 0.2, -0.08, 0.28]] as const)
    g.add(malha(new THREE.SphereGeometry(r, 10, 7).scale(1, 0.72, 1), mat, x, y, z));
  g.scale.setScalar(0.62);
  return g;
}
function chama(): THREE.Group {
  const g = new THREE.Group();
  g.add(malha(new THREE.CylinderGeometry(0.12, 0.16, 0.18, 8), toon({ color: 0x6b4a2e }), 0, 0.09, 0));
  g.add(malha(new THREE.ConeGeometry(0.16, 0.42, 8), toon({ color: 0xff8a2a, emissive: 0xc2410c, emissiveIntensity: 0.8 }), 0, 0.38, 0));
  g.add(malha(new THREE.ConeGeometry(0.08, 0.24, 8), toon({ color: 0xffe08a, emissive: 0xffb020, emissiveIntensity: 0.9 }), 0, 0.36, 0.02));
  return g;
}
function flores(): THREE.Group {
  const g = new THREE.Group(), caule = toon({ color: 0x4f8f3a }), petala = toon({ color: 0xcfe8ff, emissive: 0x335577, emissiveIntensity: 0.3 });
  for (const s of [-1, 1]) {
    g.add(malha(new THREE.CylinderGeometry(0.02, 0.02, 0.36, 5), caule, s * 0.12, 0.18, 0));
    const flor = malha(new THREE.SphereGeometry(0.1, 8, 6).scale(1, 0.6, 1), petala, s * 0.12, 0.38, 0);
    flor.rotation.z = -s * 0.5;                           // uma vira para a outra
    g.add(flor);
  }
  return g;
}
function marco(): THREE.Group {
  const g = new THREE.Group();
  g.add(malha(new THREE.BoxGeometry(0.22, 0.5, 0.16), toon({ color: 0xa8643a }), 0, 0.25, 0));
  g.add(malha(new THREE.BoxGeometry(0.14, 0.03, 0.17), toon({ color: 0xfff1c2, emissive: 0xc28a2a, emissiveIntensity: 0.6 }), 0, 0.33, 0));
  return g;
}
function broto(): THREE.Group {
  const g = new THREE.Group(), verde = toon({ color: 0x7ccf4a, emissive: 0x2f6b12, emissiveIntensity: 0.35 });
  g.add(malha(new THREE.CylinderGeometry(0.025, 0.03, 0.22, 5), verde, 0, 0.11, 0));
  for (const s of [-1, 1]) {
    const folha = malha(new THREE.SphereGeometry(0.09, 6, 4).scale(1.4, 0.35, 0.8), verde, s * 0.09, 0.22, 0);
    folha.rotation.z = s * 0.4;
    g.add(folha);
  }
  return g;
}
function pedra(): THREE.Group {
  const g = new THREE.Group();
  g.add(malha(new THREE.DodecahedronGeometry(0.55, 0).scale(1, 1.25, 0.9), toon({ color: 0x8d8a83 }), 0, 0.55, 0));
  /* a racha de onde o macaco saiu: um risco dourado */
  g.add(malha(new THREE.BoxGeometry(0.05, 0.6, 0.05), toon({ color: 0xffd36b, emissive: 0xb07a12, emissiveIntensity: 0.7 }), 0.05, 0.65, 0.48));
  return g;
}
function pessego(): THREE.Group {
  const g = new THREE.Group();
  g.add(malha(new THREE.SphereGeometry(0.16, 10, 8), toon({ color: 0xffb37a, emissive: 0xc2602a, emissiveIntensity: 0.35 }), 0, 0.17, 0));
  g.add(malha(new THREE.SphereGeometry(0.06, 6, 4).scale(1.6, 0.4, 0.9), toon({ color: 0x5f9a3a }), 0.08, 0.33, 0));
  return g;
}
function morcego(mat: THREE.Material): THREE.Group {
  const g = new THREE.Group();
  g.add(malha(new THREE.SphereGeometry(0.07, 6, 4), mat));
  for (const s of [-1, 1]) {
    const asa = malha(new THREE.ConeGeometry(0.09, 0.28, 3).rotateZ(s * Math.PI / 2), mat, s * 0.17, 0, 0);
    asa.name = s < 0 ? "asaE" : "asaD";
    g.add(asa);
  }
  return g;
}
function pegada(mat: THREE.Material): THREE.Mesh {
  return malha(new THREE.CircleGeometry(0.09, 8).scale(1, 1.5, 1).rotateX(-Math.PI / 2), mat, 0, 0.02, 0);
}

export class SinaisDaIlha {
  readonly raiz = new THREE.Group();
  private readonly sinais: Record<Deus, THREE.Group>;
  private readonly pedra = pedra();
  private readonly pegadas = new THREE.Group();
  private readonly pessego = pessego();
  private readonly morcegos = new THREE.Group();
  private readonly ninho: readonly [number, number];
  private cacheLog = -1;
  private cacheMotor: Motor | null = null;
  private derivado: { sinais: ReturnType<typeof sinaisDe>; pegadas: number | null } = { sinais: [], pegadas: null };
  private myoAntes: boolean | null = null;

  constructor(ninhoEm: readonly [number, number], sub: number) {
    this.ninho = ninhoEm;
    this.sinais = { diversao: nuvem(), coragem: chama(), amizade: flores(), conhecimento: marco(), sinceridade: broto() };
    for (const d of DEUSES) {
      const [dx, y, dz] = POS_SINAL[d], g = this.sinais[d];
      g.position.set(ninhoEm[0] + dx, y, ninhoEm[1] + dz);
      g.visible = false;
      this.raiz.add(g);
    }
    const [px, py] = pedraEm();
    const pedraIlha: [number, number] = [px / sub, py / sub];
    this.pedra.position.set(pedraIlha[0], 0, pedraIlha[1]);
    this.pedra.rotation.y = 0.6;
    /* as pegadas: do ninho ate a pedra, em pares que se alternam de lado */
    const matPegada = toon({ color: 0x5a3e28 }), [ax, az] = ninhoEm, [bx, bz] = pedraIlha;
    const ang = Math.atan2(bx - ax, bz - az), nx = Math.cos(ang), nz = -Math.sin(ang);
    for (let i = 1; i <= N_PEGADAS; i++) {
      const t = i / (N_PEGADAS + 1), lado = i % 2 ? 0.12 : -0.12, p = pegada(matPegada);
      p.position.set(ax + (bx - ax) * t + nx * lado, 0.02, az + (bz - az) * t + nz * lado);
      p.rotation.y = ang;
      this.pegadas.add(p);
    }
    this.pessego.position.set(ninhoEm[0] + POS_PESSEGO[0], 0, ninhoEm[1] + POS_PESSEGO[1]);
    const matMorcego = toon({ color: 0x241a33 });
    for (let i = 0; i < 3; i++) this.morcegos.add(morcego(matMorcego));
    for (const o of [this.pedra, this.pegadas, this.pessego, this.morcegos]) { o.visible = false; this.raiz.add(o); }
  }

  /** a cada quadro: o que se ve com a chave, no tick do pet */
  sincronizar(m: Motor, ligada: boolean, agora: number, reduzido: boolean): void {
    if (!ligada) {
      this.raiz.visible = false;
      this.marcarMyotismon(false);
      return;
    }
    this.raiz.visible = true;
    if (m !== this.cacheMotor || m.log.length !== this.cacheLog) {
      this.cacheMotor = m; this.cacheLog = m.log.length;
      this.derivado = { sinais: sinaisDe(m), pegadas: pegadasDe(m) };
    }
    const tick = m.e.tick, raro = diaDeVida(tick) === CMIT_E1.diaRaro;
    const ativos = new Set<Deus>(raro ? DEUSES : sinaisNoTick(this.derivado.sinais, tick));
    const bal = reduzido ? 0 : Math.sin((agora / PERIODO_MS) * Math.PI * 2);
    for (const d of DEUSES) {
      const g = this.sinais[d];
      g.visible = ativos.has(d);
      if (g.visible) g.position.y = POS_SINAL[d][1] + (d === "diversao" ? BALANCO * bal : 0);
    }
    this.pedra.visible = true;
    this.pegadas.visible = this.derivado.pegadas !== null && this.derivado.pegadas <= tick;
    const enigma = enigmaResolvidoEm(m);
    this.pessego.visible = enigma !== null && enigma <= tick && tick < enigma + TPD_DIA;
    const myo = myotismonNoTick(m, tick);
    this.morcegos.visible = myo;
    if (myo) this.voarMorcegos(agora, reduzido);
    this.marcarMyotismon(myo);
  }

  private voarMorcegos(agora: number, reduzido: boolean): void {
    const [x, z] = this.ninho;
    this.morcegos.children.forEach((b, i) => {
      const a = (reduzido ? 0 : agora / 2600) + (i * Math.PI * 2) / 3, r = 1.6 + 0.3 * i;
      b.position.set(x + Math.cos(a) * r, 3 + 0.25 * i, z + Math.sin(a) * r);
      b.rotation.y = -a;
      const bater = reduzido ? 0 : Math.sin(agora / 90 + i) * 0.6;
      for (const asa of b.children) if (asa.name) asa.rotation.x = asa.name === "asaE" ? bater : -bater;
    });
  }

  /** o canvas escurece pelo CSS (html[data-myotismon]) */
  private marcarMyotismon(v: boolean): void {
    if (v === this.myoAntes) return;
    this.myoAntes = v;
    if (v) document.documentElement.dataset.myotismon = "1";
    else delete document.documentElement.dataset.myotismon;
  }

  descartar(): void { this.marcarMyotismon(false); }
}
