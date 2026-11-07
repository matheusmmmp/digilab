/* Os lugares da ilha na cena (docs/TAREFA_V3_LUGARES_3D.md, secao 12; P-11 de docs/PLANO_V3_PROGRESSAO_TUTORIAL.md): so vista. A grade
   (grade.ts, porLugares) diz onde ficam e abre a clareira; aqui cada modelo de LUGARES_MODELOS (public/lugares/<nome>/) entra pelo
   carregarVariante, como os enfeites (enfeites.ts), com a sombra redonda quando o modelo tem.
   Aberto e trancado sao o mesmo modelo: aberto, as partes da mascara (LUGARES_LUZ, o emissiveMap) acendem na cor do lugar; trancado,
   apagam. Ainda nao ha o nivel do Tamer (plano V da progressao), entao `LUGAR_ABERTO` diz o estado de cada um: o portao e a barraca
   abertos (os menus Lutar e Diario existem hoje), o cais trancado (o multiplayer e futuro). O cadeado e o "Nv" na tela ficam para quando o
   nivel existir. Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { GEO_SOMBRA, carregarVariante, materialSombra } from "./cena.ts";
import { LUGAR_LUZ } from "./constantes.ts";
import type { Ilha } from "./grade.ts";
import { LUGARES_LUZ, LUGARES_MODELOS, type NomeLugar } from "./modelos.ts";

/** o estado de cada lugar enquanto nao ha o nivel do Tamer */
export const LUGAR_ABERTO: Record<NomeLugar, boolean> = { portao: true, barraca: true, cais: false };

/** os lugares prontos: o grupo e o que acende ou apaga um lugar */
export interface Lugares { grupo: THREE.Group; abrir: (nome: NomeLugar, aberto: boolean) => void }

/** carrega os modelos e poe os lugares da ilha; falha alto se um arquivo nao carrega (a ilha cai na reserva, como sem os kits) */
export async function lugares(ilha: Ilha, base: string): Promise<Lugares> {
  const grupo = new THREE.Group(), gltf = new GLTFLoader(), acesos = new Map<NomeLugar, THREE.MeshToonMaterial[]>();
  const sombras: { x: number; z: number; r: number }[] = [];
  for (const l of ilha.lugares) {
    const m = LUGARES_MODELOS[l.nome];
    const { pecas } = await carregarVariante(gltf, new URL("lugares/" + m.arquivos[0], base).href, m);
    const pos = new THREE.Matrix4().compose(new THREE.Vector3(l.x, l.y, l.z), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), l.giro),
      new THREE.Vector3(1, 1, 1));
    const luz = LUGARES_LUZ[l.nome];
    const t = luz ? await new THREE.TextureLoader().loadAsync(new URL("lugares/" + luz, base).href) : null;
    /* a mascara usa os UVs do glTF: sem virar a imagem, como o GLTFLoader faz com as texturas dele */
    if (t) t.flipY = false;
    const mats: THREE.MeshToonMaterial[] = [];
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
      grupo.add(malha);
    }
    acesos.set(l.nome, mats);
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
  for (const l of ilha.lugares) abrir(l.nome, LUGAR_ABERTO[l.nome]);
  return { grupo, abrir };
}
