/* O estilo Floresta do habitat (src/habitat.ts): a ilha da grade com as pecas do kit RPG Tiny Fantasy Forest PBR (Dungeon Mason, Unity
   Asset Store EULA: nao se redistribui), o do POC floresta do #480. O kit fica fora do repositorio, em Assets/kits3d/tiny_fantasy_forest/,
   e so o modo dev do Vite o serve (vite.config.ts); sem ele, os modelos nao carregam e a cena volta para a ilha (voltarParaIlha).
     - o terreno: o da ilha (degraus e faixas), nas cores mais saturadas do kit;
     - os objetos da grade: a arvore, o capim, a flor e as pedras do kit, na altura da tabela MODELOS, com a paleta unica do kit (o
       "Base Map", lido sem filtro) e o degrade de baixo para cima nas arvores e no capim (a base na sombra da copa).
   So vista; todos os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { PALETA_ILHA, curvar, type PaletaTerreno, type Variante } from "./cena.ts";
import { FORA } from "./grade.ts";
import type { Modelo, NomeModelo } from "./modelos.ts";

/** onde o dev serve o kit, relativo a pagina (o mesmo caminho do atlas, src/atlas.ts) */
export const BASE_FLORESTA = "../../../Assets/kits3d/tiny_fantasy_forest/x/Assets/RPG Tiny Fantasy Forest PBR/";

export const PALETA_FLORESTA: PaletaTerreno = {
  ...PALETA_ILHA,
  grama: { casa: [0x86c44a, 0x82c046], jardim: [0x77b843, 0x73b43f], campo: [0x93c24c, 0x8ebd47], mata: [0x5c9e3a, 0x589a36], [FORA]: [0x77b843, 0x73b43f] },
  caminho: [0xc9a46a, 0xc49f65], borda: 0x5f9f3c, estrato: [0xb98a5a, 0xa87a4c, 0x986c42], margem: [0x8a6a44, 0x7d5f3c],
};

/** as pecas do kit no lugar de cada modelo da grade (Mesh/<nome>.fbx); o degrade so nas plantas */
const PECAS: Record<NomeModelo, { arquivos: readonly string[]; degrade: boolean }> = {
  arvore_redonda: { arquivos: ["TreePlants/Tree02"], degrade: true },
  pinheiro: { arquivos: ["TreePlants/Tree02"], degrade: true },
  arbusto: { arquivos: ["TreePlants/Grass01"], degrade: true },
  pedra: { arquivos: ["Rock/Rock01", "Rock/Rock03_1", "Rock/Rock04", "Rock/Rock06_1"], degrade: false },
  flor: { arquivos: ["TreePlants/Flower01"], degrade: true },
  trevo: { arquivos: ["TreePlants/Grass01"], degrade: true },
  grama: { arquivos: ["TreePlants/Grass01"], degrade: true },
  grama_alta: { arquivos: ["TreePlants/Grass01"], degrade: true },
  samambaia: { arquivos: ["TreePlants/Flower01"], degrade: true },
  cogumelo: { arquivos: ["Rock/Cobble01", "Rock/Cobble02"], degrade: false },
};
export const arquivosFloresta = (id: NomeModelo): readonly string[] => PECAS[id].arquivos;

/** a textura do kit sem filtro (filtrar mistura os quadrados de cor vizinhos da paleta) */
function texKit(base: string, arquivo: string): THREE.Texture {
  const t = new THREE.TextureLoader().load(new URL("Texture/" + arquivo, base).href);
  t.colorSpace = THREE.SRGBColorSpace;
  t.magFilter = t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  return t;
}

/** o material do kit (a paleta e a emissao), com o degrade de baixo para cima nas plantas e a dobra/vento da ilha */
function materialKit(mapa: THREE.Texture, emissao: THREE.Texture, degrade: boolean, vento: number): THREE.Material {
  const m = new THREE.MeshStandardMaterial({ map: mapa, emissiveMap: emissao, emissive: 0xffffff, emissiveIntensity: 1, roughness: 0.9, metalness: 0 });
  curvar(m, vento);
  if (degrade) {
    const antes = m.onBeforeCompile;
    m.onBeforeCompile = (s, r) => {
      antes(s, r);
      s.vertexShader = "varying float vAlturaKit;\n" + s.vertexShader.replace("#include <begin_vertex>", "#include <begin_vertex>\n  vAlturaKit = clamp(position.y, 0.0, 1.0);");
      s.fragmentShader = "varying float vAlturaKit;\n" + s.fragmentShader.replace("#include <map_fragment>",
        "#include <map_fragment>\n  diffuseColor.rgb *= mix(0.55, 1.06, smoothstep(0.0, 1.0, vAlturaKit));");
    };
    m.customProgramCacheKey = () => `kit-degrade-${vento}`;
  }
  return m;
}

/** o carregador das pecas do kit: as malhas LOD0 de cada FBX (sem o LOD1 nem os colisores), normalizadas para a altura do modelo */
export async function carregadorFloresta(base: string): Promise<(arquivo: string, id: NomeModelo, modelo: Modelo) => Promise<Variante>> {
  const { FBXLoader } = await import("three/examples/jsm/loaders/FBXLoader.js");
  const raizKit = new URL(BASE_FLORESTA, base).href;
  /* os FBX citam um "Albedo.png" que nao vem no pacote; a cor e a do Base Map */
  const gerente = new THREE.LoadingManager();
  gerente.setURLModifier(u => u.endsWith("/Albedo.png") ? new URL("Texture/Base Map.png", raizKit).href : u);
  const loader = new FBXLoader(gerente), mapa = texKit(raizKit, "Base Map.png"), emissao = texKit(raizKit, "Emission Map.png");
  return async (arquivo, id, modelo) => {
    const raiz = await loader.loadAsync(new URL("Mesh/" + arquivo + ".fbx", raizKit).href);
    raiz.rotation.set(0, 0, 0);                           // o FBXLoader poe -90 graus em x; as malhas do kit ja vem com o y para cima
    raiz.updateMatrixWorld(true);
    const lod0: THREE.Mesh[] = [];
    raiz.traverse(o => { const m = o as THREE.Mesh; if (m.isMesh && m.name === "LOD0") lod0.push(m); });
    if (!lod0.length) throw new Error(`floresta: FBX sem LOD0: ${arquivo}`);
    const caixa = new THREE.Box3();
    for (const m of lod0) caixa.expandByObject(m);
    const tam = caixa.getSize(new THREE.Vector3()), centro = caixa.getCenter(new THREE.Vector3());
    if (!(tam.y > 0)) throw new Error(`floresta: peca sem altura: ${arquivo}`);
    const s = modelo.altura / tam.y;
    const norm = new THREE.Matrix4().makeScale(s, s, s).multiply(new THREE.Matrix4().makeTranslation(-centro.x, -caixa.min.y, -centro.z));
    /* a altura do degrade (0 no pe, 1 no topo) entra na geometria: o shader le position.y depois da normalizacao */
    const mat = materialKit(mapa, emissao, PECAS[id].degrade, modelo.vento);
    return {
      pecas: lod0.map(m => {
        const geo = m.geometry.clone().applyMatrix4(norm.clone().multiply(m.matrixWorld));
        geo.scale(1 / modelo.altura, 1 / modelo.altura, 1 / modelo.altura);
        return { geo, mat, local: new THREE.Matrix4().makeScale(modelo.altura, modelo.altura, modelo.altura) };
      }),
    };
  };
}
