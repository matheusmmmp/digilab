/* A bola de fogo do mapa_ac (o Pepper Breath do Agumon): o extrator do DSTS não exporta os efeitos de batalha, então ela é feita aqui,
   com esferas somadas (núcleo, halo, rastro) que dobram com o mundo. Só desenho, fora do motor: PROPOSTO, SEM FONTE.
     - o voo: sai da boca para a frente, com um arco leve de gravidade, e vive até bater ou acabar o tempo;
     - a batida: no chão e no penhasco (a altura do terreno passa a da bola), num objeto que bloqueia (o raio dele, até a altura dele)
       ou na água (apaga, sem explosão de fogo);
     - a explosão: um clarão que cresce e some, e faíscas com gravidade que quicam no chão perdendo energia. */
import * as THREE from "three";
import { curvar } from "./cena.ts";
import { type Mapa, NIVEL_AGUA, rng } from "./mapa.ts";

const VEL = 9;                         // a velocidade de saída, em células por segundo
const SUBIDA = 1.2;                    // a velocidade vertical de saída
const GRAVIDADE = 5;                   // células por segundo ao quadrado (a bola: um arco leve)
const GRAV_FAISCA = 14;                // as faíscas caem bem mais
const RAIO = 0.16;                     // o raio de colisão da bola
const VIDA_S = 2.5;                    // a bola some sem bater depois disso
const FAISCAS = 26;                    // faíscas por explosão
const QUIQUE = 0.45;                   // quanto da velocidade vertical a faísca guarda no quique
const ATRITO_QUIQUE = 0.7;             // e da horizontal
const ALTURA_OBJETO: Record<string, number> = { arvore_redonda: 4.2, pinheiro: 5.0 };  // a altura (células) que bloqueia; o resto, 1

const GEO = new THREE.IcosahedronGeometry(1, 2);
/* somada (o núcleo e as faíscas, que brilham) ou normal (halo, rastro e clarão: somados sobre a grama clara virariam amarelo-branco) */
const somada = (cor: number, opacidade: number, soma = true) =>
  curvar(new THREE.MeshBasicMaterial({ color: cor, transparent: true, opacity: opacidade, depthWrite: false,
    blending: soma ? THREE.AdditiveBlending : THREE.NormalBlending }));

interface Particula { malha: THREE.Mesh; mat: THREE.MeshBasicMaterial; vel: THREE.Vector3; vida: number; total: number; r0: number; r1: number; op0: number; quica: boolean }
interface Bola { grupo: THREE.Group; vel: THREE.Vector3; vida: number; rastro: number }

export class Projeteis {
  readonly raiz = new THREE.Group();
  private bolas: Bola[] = [];
  private particulas: Particula[] = [];
  private readonly sorte = rng(4242);
  /** chamado em cada batida: o ponto e o que foi atingido */
  aoBater: ((ponto: THREE.Vector3, alvo: string) => void) | null = null;

  private readonly mapa: Mapa;

  constructor(mapa: Mapa) { this.mapa = mapa; }

  disparar(boca: THREE.Vector3, frente: THREE.Vector3): void {
    const grupo = new THREE.Group();
    const nucleo = new THREE.Mesh(GEO, somada(0xfff2b0, 1));
    nucleo.scale.setScalar(RAIO * 0.8);
    const halo = new THREE.Mesh(GEO, somada(0xff7a1a, 0.7, false));
    halo.scale.setScalar(RAIO * 1.9);
    const halo2 = new THREE.Mesh(GEO, somada(0xff3a00, 0.3, false));
    halo2.scale.setScalar(RAIO * 3.0);
    grupo.add(halo2, halo, nucleo);
    grupo.position.copy(boca);
    this.raiz.add(grupo);
    this.bolas.push({ grupo, vel: frente.clone().setY(0).normalize().multiplyScalar(VEL).setY(SUBIDA), vida: 0, rastro: 0 });
  }

  private particula(pos: THREE.Vector3, vel: THREE.Vector3, cor: number, vida: number, r0: number, r1: number, op0: number, quica: boolean, soma = quica): void {
    const mat = somada(cor, op0, soma);
    const malha = new THREE.Mesh(GEO, mat);
    malha.position.copy(pos);
    malha.scale.setScalar(r0);
    this.raiz.add(malha);
    this.particulas.push({ malha, mat, vel, vida, total: vida, r0, r1, op0, quica });
  }

  private aleatorio(a: number, b: number): number { return a + (b - a) * this.sorte(); }

  private explodir(p: THREE.Vector3, agua: boolean): void {
    if (agua) {
      /* na água: um chiado de vapor, sem fogo */
      for (let i = 0; i < 10; i++) {
        this.particula(p, new THREE.Vector3(this.aleatorio(-0.6, 0.6), this.aleatorio(0.8, 1.8), this.aleatorio(-0.6, 0.6)), 0xdff4ff, 0.8, 0.08, 0.35, 0.35, false);
      }
      return;
    }
    this.particula(p, new THREE.Vector3(), 0xffb040, 0.22, 0.12, 0.5, 0.7, false);   // o clarão
    this.particula(p, new THREE.Vector3(), 0xd83a00, 0.4, 0.18, 0.75, 0.4, false);
    for (let i = 0; i < FAISCAS; i++) {
      const ang = this.aleatorio(0, Math.PI * 2), forca = this.aleatorio(2, 5.5);
      const vel = new THREE.Vector3(Math.cos(ang) * forca, this.aleatorio(2.5, 6.5), Math.sin(ang) * forca);
      this.particula(p, vel, i % 3 === 0 ? 0xfff0a0 : 0xff8a20, this.aleatorio(0.6, 1.1), 0.05, 0.02, 1, true);
    }
    for (let i = 0; i < 5; i++) {
      /* a fumaça: sobe devagar e cresce */
      this.particula(p, new THREE.Vector3(this.aleatorio(-0.4, 0.4), this.aleatorio(0.6, 1.2), this.aleatorio(-0.4, 0.4)), 0x6a5a50, 1.2, 0.15, 0.55, 0.22, false);
    }
  }

  /** o que a bola em `p` atinge agora: "chao", "agua", o modelo do objeto, ou null */
  private colisao(p: THREE.Vector3): string | null {
    const chao = this.mapa.altura(p.x, p.z);
    if (chao < NIVEL_AGUA && p.y - RAIO <= NIVEL_AGUA) return "agua";
    if (p.y - RAIO <= chao) return "chao";
    for (const o of this.mapa.objetos) {
      if (o.raio <= 0) continue;
      const alto = (ALTURA_OBJETO[o.modelo] ?? 1) * o.escala;
      if (Math.hypot(p.x - o.x, p.z - o.z) < o.raio + RAIO && p.y < this.mapa.altura(o.x, o.z) + alto) return o.modelo;
    }
    return null;
  }

  atualizar(dt: number): void {
    for (const b of [...this.bolas]) {
      b.vida += dt;
      b.vel.y -= GRAVIDADE * dt;
      /* em passos curtos, para não atravessar um tronco fino */
      const passos = Math.ceil((b.vel.length() * dt) / (RAIO * 0.75));
      let alvo: string | null = null;
      for (let i = 0; i < passos && !alvo; i++) {
        b.grupo.position.addScaledVector(b.vel, dt / passos);
        alvo = this.colisao(b.grupo.position);
      }
      /* o rastro: brasas que ficam para trás */
      b.rastro += dt;
      while (b.rastro > 0.018) {
        b.rastro -= 0.018;
        const jit = new THREE.Vector3(this.aleatorio(-0.3, 0.3), this.aleatorio(0.2, 0.7), this.aleatorio(-0.3, 0.3));
        this.particula(b.grupo.position, jit, this.sorte() < 0.5 ? 0xff9a2a : 0xff5a10, 0.35, RAIO * 1.3, 0.02, 0.6, false);
      }
      b.grupo.rotation.y += dt * 9;
      if (alvo || b.vida > VIDA_S || !this.mapa.cel(Math.floor(b.grupo.position.x), Math.floor(b.grupo.position.z))) {
        if (alvo) {
          this.explodir(b.grupo.position.clone(), alvo === "agua");
          this.aoBater?.(b.grupo.position.clone(), alvo);
        }
        this.raiz.remove(b.grupo);
        for (const m of b.grupo.children) ((m as THREE.Mesh).material as THREE.Material).dispose();
        this.bolas.splice(this.bolas.indexOf(b), 1);
      }
    }
    for (const p of [...this.particulas]) {
      p.vida -= dt;
      if (p.vida <= 0) {
        this.raiz.remove(p.malha);
        p.mat.dispose();
        this.particulas.splice(this.particulas.indexOf(p), 1);
        continue;
      }
      const t = 1 - p.vida / p.total;
      if (p.quica) {
        p.vel.y -= GRAV_FAISCA * dt;
        p.malha.position.addScaledVector(p.vel, dt);
        const chao = this.mapa.altura(p.malha.position.x, p.malha.position.z);
        if (p.malha.position.y < chao && p.vel.y < 0) {
          p.malha.position.y = chao;
          p.vel.y = -p.vel.y * QUIQUE;
          p.vel.x *= ATRITO_QUIQUE;
          p.vel.z *= ATRITO_QUIQUE;
        }
      } else {
        p.malha.position.addScaledVector(p.vel, dt);
      }
      p.malha.scale.setScalar(p.r0 + (p.r1 - p.r0) * t);
      p.mat.opacity = p.op0 * (1 - t);
    }
  }
}
