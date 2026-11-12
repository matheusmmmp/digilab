/* O que tapa o pet fica transparente (docs/TAREFA_V3_MOITA_NINHO.md; so vista): a conta de quem tapa e a de tapar.ts; aqui, o three.
   Os objetos da grade sao instancias (cena.ts, objetos), com o material compartilhado por (modelo, variante): para nao deixar a floresta
   inteira transparente, a instancia que tapa some do InstancedMesh dela (a matriz vira zero) e entra no lugar um InstancedMesh de uma
   instancia so, com a mesma geometria, a mesma matriz e um clone do material, transparente, so dele. O clone guarda a dobra e o vento do
   original (o onBeforeCompile e a chave do programa), escreve a profundidade (as folhas de dentro nao aparecem) e mantem o alphaTest, e vai
   depois do papel do pet (renderOrder 4 > 3): o pet aparece atras dele. O alphaTest do clone desce com a opacidade (o three compara o alfa
   ja multiplicado por ela). Quando a opacidade volta a 1, o clone sai e a instancia volta. */
import * as THREE from "three";
import { TAPAR_PET } from "./constantes.ts";
import { opacidadeAgora, quemTapa, type Ponto, type Tapavel } from "./tapar.ts";

/** uma peca de um objeto: o InstancedMesh e o indice da instancia dele */
export interface PecaTapavel { im: THREE.InstancedMesh; i: number }
/** um objeto que pode tapar: o cilindro (sem a dobra: y0 e o chao dele, topo a altura acima do chao) e as pecas */
export interface ObjetoTapavel { x: number; z: number; chao: number; altura: number; raio: number; pecas: PecaTapavel[] }

const ZERO = new THREE.Matrix4().makeScale(0, 0, 0);

interface Esmaecido { op: number; clones: { peca: PecaTapavel; orig: THREE.Matrix4; malha: THREE.InstancedMesh; mat: THREE.Material; corte: number }[] }

export class Esmaecer {
  private readonly vivos = new Map<number, Esmaecido>();
  private alvos = new Set<number>();
  private quadros = 0;
  private readonly cil: Tapavel[];
  private readonly grupo: THREE.Group;
  private readonly lista: readonly ObjetoTapavel[];
  constructor(grupo: THREE.Group, lista: readonly ObjetoTapavel[]) {
    this.grupo = grupo; this.lista = lista;
    this.cil = lista.map(o => ({ x: o.x, z: o.z, y0: o.chao, topo: o.chao + o.altura, raio: o.raio }));
  }

  /** quantos objetos estao transparentes agora (o e2e le pelo __digilab) */
  get transparentes(): number { return this.vivos.size; }

  /** um quadro: `pe` e o pe do pet em foco (y dobrado); `dobrar` da a altura dobrada de um ponto (a do shader) */
  quadro(camera: Ponto, pe: Ponto, dobrar: (y: number, x: number, z: number) => number, dtMs: number, reduzido: boolean): void {
    if (this.quadros++ % TAPAR_PET.cadaQuadros === 0) {
      this.lista.forEach((o, i) => { const c = this.cil[i]; c.y0 = dobrar(o.chao, o.x, o.z); c.topo = c.y0 + o.altura; });
      this.alvos = new Set(quemTapa(camera, pe, this.cil, TAPAR_PET.alturaPet, TAPAR_PET.raio, TAPAR_PET.amostras));
    }
    for (const i of this.alvos) if (!this.vivos.has(i)) this.vivos.set(i, this.esmaecer(i));
    for (const [i, e] of this.vivos) {
      e.op = opacidadeAgora(e.op, this.alvos.has(i) ? TAPAR_PET.opacidade : 1, dtMs, TAPAR_PET.tauMs, reduzido);
      if (e.op >= 1) { this.voltar(e); this.vivos.delete(i); continue; }
      /* o alphaTest compara o alfa ja multiplicado pela opacidade: o corte das folhas desce junto, senao a peca inteira some */
      for (const c of e.clones) { c.mat.opacity = e.op; c.mat.alphaTest = c.corte * e.op; }
    }
  }

  private esmaecer(i: number): Esmaecido {
    const clones: Esmaecido["clones"] = [];
    for (const peca of this.lista[i].pecas) {
      const orig = new THREE.Matrix4();
      peca.im.getMatrixAt(peca.i, orig);
      peca.im.setMatrixAt(peca.i, ZERO);
      peca.im.instanceMatrix.needsUpdate = true;
      const base = peca.im.material as THREE.Material, mat = base.clone();
      /* o clone do three nao leva o onBeforeCompile nem a chave do programa: sem eles, o objeto perde a dobra e o vento */
      mat.onBeforeCompile = base.onBeforeCompile;
      mat.customProgramCacheKey = base.customProgramCacheKey;
      mat.transparent = true; mat.depthWrite = true; mat.opacity = 1;
      const malha = new THREE.InstancedMesh(peca.im.geometry, mat, 1);
      malha.setMatrixAt(0, orig);
      malha.frustumCulled = false; malha.renderOrder = 4;
      this.grupo.add(malha);
      clones.push({ peca, orig, malha, mat, corte: base.alphaTest });
    }
    return { op: 1, clones };
  }

  private voltar(e: Esmaecido): void {
    for (const c of e.clones) {
      c.peca.im.setMatrixAt(c.peca.i, c.orig);
      c.peca.im.instanceMatrix.needsUpdate = true;
      this.grupo.remove(c.malha);
      c.malha.dispose(); c.mat.dispose();
    }
  }
}
