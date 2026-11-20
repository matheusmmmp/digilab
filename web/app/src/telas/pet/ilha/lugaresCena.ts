/* Os lugares da ilha na cena (docs/TAREFA_V3_LUGARES_3D.md, secao 12; P-11 de docs/PLANO_V3_PROGRESSAO_TUTORIAL.md): so vista. A grade
   (grade.ts, porLugares) diz onde ficam e abre a clareira; aqui cada modelo de LUGARES_MODELOS (public/lugares/<nome>/) entra pelo
   carregarVariante, como os enfeites (enfeites.ts), com a sombra redonda quando o modelo tem. Na mescla com a UX_TELA_PET (2026-11-07) este
   modulo saiu de ilha/lugares.ts, que ficou com a tabela pura dos lugares (sem three e sem DOM, lida pelos testes sozinha).
   Aberto e trancado sao o mesmo modelo: aberto, as partes da mascara (LUGARES_LUZ, o emissiveMap) acendem na cor do lugar; trancado,
   apagam. O estado de partida e o de LUGAR_ABERTO (lugaresIlha.ts: o cais trancado, o multiplayer e futuro) e o nivel do Tamer (trancas.ts);
   a vista reaplica as trancas quando mudam (vista.ts, aplicarTrancas: apaga o modelo, Apagador, e a luz, `abrir`), e o cadeado com o "Nv" e
   DOM (CadeadosDaIlha.tsx). Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { GEO_SOMBRA, carregarVariante, materialSombra } from "./cena.ts";
import { LUGAR_ABERTO } from "../lugaresIlha.ts";
import { LUGAR_LUZ } from "./constantes.ts";
import type { Ilha } from "./grade.ts";
import { LUGARES_LUZ, LUGARES_MODELOS, type NomeLugar } from "./modelos.ts";
import { lugarTrancado } from "../../../trancas.ts";

/** os lugares prontos: o grupo e o que acende ou apaga um lugar */
export interface Lugares {
  grupo: THREE.Group; abrir: (nome: NomeLugar, aberto: boolean) => void;
  /** o grupo das malhas de cada lugar (o Apagador da vista escurece o trancado; a sombra fica fora, uma so para todos) */
  raizes: Map<NomeLugar, THREE.Group>;
  /** a caixa de cada lugar no mundo (celulas; sem a dobra, que a vista aplica ao projetar): onde o toque acerta o lugar */
  caixas: Map<NomeLugar, THREE.Box3>;
}

/** carrega os modelos e poe os lugares da ilha; falha alto se um arquivo nao carrega (a ilha cai na reserva, como sem os kits) */
export async function lugares(ilha: Ilha, base: string): Promise<Lugares> {
  const grupo = new THREE.Group(), gltf = new GLTFLoader(), acesos = new Map<NomeLugar, THREE.MeshToonMaterial[]>();
  const sombras: { x: number; z: number; r: number }[] = [], caixas = new Map<NomeLugar, THREE.Box3>(), raizes = new Map<NomeLugar, THREE.Group>();
  for (const l of ilha.lugares) {
    const m = LUGARES_MODELOS[l.nome];
    const { pecas } = await carregarVariante(gltf, new URL("lugares/" + m.arquivos[0], base).href, m);
    const pos = new THREE.Matrix4().compose(new THREE.Vector3(l.x, l.y, l.z), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), l.giro),
      new THREE.Vector3(1, 1, 1));
    const luz = LUGARES_LUZ[l.nome];
    const t = luz ? await new THREE.TextureLoader().loadAsync(new URL("lugares/" + luz, base).href) : null;
    /* a mascara usa os UVs do glTF: sem virar a imagem, como o GLTFLoader faz com as texturas dele */
    if (t) t.flipY = false;
    const mats: THREE.MeshToonMaterial[] = [], caixa = new THREE.Box3(), raiz = new THREE.Group();
    raiz.name = "lugar-" + l.nome;
    grupo.add(raiz);
    for (const p of pecas) {
      if (t) {
        const mat = p.mat as THREE.MeshToonMaterial;
        mat.emissiveMap = t; mat.emissive.setStyle(`rgb(${LUGAR_LUZ.cor[l.nome]})`); mat.emissiveIntensity = 0;
        mat.needsUpdate = true;
        mats.push(mat);
      }
      const malha = new THREE.Mesh(p.geo, p.mat);
      malha.matrixAutoUpdate = false;
      malha.matrix.copy(pos.clone().multiply(p.local));
      malha.frustumCulled = false;     // a dobra muda onde a peca aparece; o volume do three nao sabe disso
      raiz.add(malha);
      if (!p.geo.boundingBox) p.geo.computeBoundingBox();
      caixa.union(p.geo.boundingBox!.clone().applyMatrix4(malha.matrix));
    }
    acesos.set(l.nome, mats);
    caixas.set(l.nome, caixa);
    raizes.set(l.nome, raiz);
    if (m.sombra > 0) sombras.push({ x: l.x, z: l.z, r: m.sombra });
  }
  if (sombras.length) {
    const s = new THREE.InstancedMesh(GEO_SOMBRA, materialSombra(), sombras.length);
    sombras.forEach((o, i) => s.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(o.x, ilha.altura(o.x, o.z) + 0.02, o.z),
      new THREE.Quaternion(), new THREE.Vector3(o.r * 2, 1, o.r * 2))));
    s.frustumCulled = false;
    s.renderOrder = 1;
    grupo.add(s);
  }
  const abrir = (nome: NomeLugar, aberto: boolean) => { for (const m of acesos.get(nome) ?? []) m.emissiveIntensity = aberto ? LUGAR_LUZ.forca : 0; };
  /* o estado de partida: LUGAR_ABERTO (o cais trancado) e, no portao e na barraca, o nivel do Tamer (trancas.ts), que a vista reaplica quando muda
     (vista.ts, aplicarTrancas) */
  for (const l of ilha.lugares) abrir(l.nome, LUGAR_ABERTO[l.nome] && !(l.nome !== "cais" && lugarTrancado(l.nome)));
  return { grupo, abrir, caixas, raizes };
}
