/* O pet como modelo 3D no mapa_ac: um .glb com esqueleto e clipes, em Assets/kits3d/ (fora do repositório). Hoje, o Mushnub do
   Quaternius (CC0) e um export local do dsts-extractor. Só para comparar com o papel; não vai para o jogo.
     - os materiais viram o toon do mapa (com a dobra do mundo), com o mapa de cor ou a cor do arquivo;
     - num export do DSTS (o .glb traz as rampas common_clut e clut001), o corpo e o rosto usam o cel do jogo como o porta o chr-cel do
       dsts-viewer (MIT, nuffle.me): ambiente em harmônicos esféricos, a luz direta pela rampa de toon do jogo (chave na rampa neutra,
       preenchimento na fria), a normal do a01n, sob a luz do preset Field Guide dele (calibrado contra capturas do jogo); sem o brilho
       de borda, a sombra projetada e a névoa;
     - a malha "outline" do export é o contorno inflado do jogo: sai escura, inchada pela normal, só com o lado que fica atrás do corpo;
     - o olho do DSTS: o rosto (as malhas com OverlayColorSampler3) compõe a pele (a01, UV1), a íris (p01, UV2) e a folha das pálpebras
       (b01, UV3), como o compositeEyePixel do dsts-viewer; a folha tem 4 linhas (aberto, fechado, sorriso, bravo), e piscar é ir à
       linha 1 por um instante; o domo do olho é o brilho somado (eye_shine);
     - o modelo gira para onde anda, e um clipe de animação para parado e outro para andando (escolhidos no painel); golpear() toca um
       clipe uma vez por cima e, nos golpes de fogo, avisa o instante do disparo e a posição da boca.
   Sem o arquivo na máquina, carregar() levanta erro. Só desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { GEO_SOMBRA, curvar, materialSombra, toon } from "./cena.ts";

const ALTURA = 1.0;                    // a altura do modelo no mundo, em células (o papel tem uns 0,9)
const GIRO_POR_S = 10;                 // a velocidade do giro para a direção de andar
const CONTORNO = 0.012;                // quanto a malha do contorno incha pela normal, em unidades do arquivo
const LINHAS_OLHO = 4;                 // as linhas da folha b01: aberto, fechado, sorriso, bravo
const PISCAR_ENTRE_S = [3.1, 4.4, 2.3, 5.2, 1.0, 3.7];  // os intervalos entre piscadas, em ciclo (o 1,0 é a piscada dupla)
const PISCAR_FECHADO_S = 0.12;         // quanto tempo a pálpebra fica fechada

/** os golpes do DSTS pelo código do clipe; `fogo` é o instante (s) em que a boca mais abre (o J_joe medido no clipe do Agumon) */
export const GOLPES = [
  { codigo: "ba01", nome: "garra" },
  { codigo: "ba02", nome: "mordida de fogo", fogo: 0.83 },
  { codigo: "bs01", nome: "Pepper Breath", fogo: 1.23 },
  { codigo: "bs02", nome: "Pepper Breath 2", fogo: 0.97 },
] as const;

/* ---------- o cel do DSTS (porte do core do chr-cel do dsts-viewer: core/constants.glsl, core/frag.head.glsl) ---------- */

/* a luz Field Guide do dsts-viewer (modelViewer/lighting.ts), passada a harmônicos esféricos como o inputs/lightingRig.ts */
const LUZ = (() => {
  const Y00 = 0.2820947918, Y1 = 0.4886025119, Y2_2 = 1.0925484306, Y20 = 0.3153915652, Y22 = 0.5462742153;
  const sh = Array.from({ length: 9 }, () => new THREE.Vector3());
  const dirs: THREE.Vector3[] = [], cores: THREE.Vector3[] = [];
  /* o hemisfério: céu e chão */
  const ceu = new THREE.Color(0xd2def0).multiplyScalar(0.62), chao = new THREE.Color(0x39322a).multiplyScalar(0.62);
  const cDC = 4 * Math.PI * Y00, cY = -Y1 * (4 * Math.PI) / 3;
  sh[0].add(new THREE.Vector3(ceu.r + chao.r, ceu.g + chao.g, ceu.b + chao.b).multiplyScalar(cDC / 2));
  sh[1].add(new THREE.Vector3(ceu.r - chao.r, ceu.g - chao.g, ceu.b - chao.b).multiplyScalar(cY / 2));
  /* a chave e o preenchimento (a direção é a da posição da luz, da superfície para a luz) */
  for (const [hex, int, pos] of [[0xfff5e6, 0.62, [2, 2.5, 3]], [0xe6eeff, 0.22, [-3, 1, -2]]] as const) {
    const d = new THREE.Vector3(...pos).normalize(), c = new THREE.Color(hex).multiplyScalar(int);
    const y = [Y00, -Y1 * d.y, -Y1 * d.z, -Y1 * d.x, Y2_2 * d.x * d.y, Y2_2 * d.y * d.z, Y20 * (3 * d.z * d.z - 1), Y2_2 * d.x * d.z,
      Y22 * (d.x * d.x - d.y * d.y)];
    y.forEach((k, i) => sh[i].add(new THREE.Vector3(c.r, c.g, c.b).multiplyScalar(k)));
    dirs.push(d);
    cores.push(new THREE.Vector3(c.r, c.g, c.b));
  }
  return { sh, dirs, cores };
})();

const GLSL_CEL_VERT_PARS = `
attribute vec4 tanCel;
varying vec3 vNormalCel;
varying vec3 vPosCel;
varying vec3 vTanCel;
varying float vTanW;
`;
/* depois do worldpos_vertex: a normal e a tangente já com o esqueleto (o skinMatrix vem do skinnormal_vertex) */
const GLSL_CEL_VERT = `
#if defined( USE_ENVMAP ) || defined( USE_SKINNING )
  vec3 nCel = objectNormal;
#else
  vec3 nCel = normal;
#endif
  vec3 tCel = tanCel.xyz;
#ifdef USE_SKINNING
  tCel = (skinMatrix * vec4(tCel, 0.0)).xyz;
#endif
  vNormalCel = normalize(mat3(modelMatrix) * nCel);
  vTanCel = normalize(mat3(modelMatrix) * tCel);
  vTanW = tanCel.w;
  vPosCel = (modelMatrix * vec4(transformed, 1.0)).xyz;
`;
const GLSL_CEL_FRAG_PARS = `
uniform sampler2D uCLUT;
uniform sampler2D uCLUTFill;
uniform sampler2D uNormalCel;
uniform float uTemNormal;
uniform vec3 uSH[9];
uniform vec3 uLightDirs[2];
uniform vec3 uLightColors[2];
varying vec3 vNormalCel;
varying vec3 vPosCel;
varying vec3 vTanCel;
varying float vTanW;
float acosApprox(float x) {
  float ax = abs(x);
  float s = sqrt(max(0.0, 1.0 - ax));
  float p = ((-0.0187293 * ax + 0.0742611) * ax - 0.2121144) * ax + 1.5707288;
  float q = s * p;
  return x < 0.0 ? (3.14159265 - q) : q;
}
float toonRampU(float ndotl) {
  float wrap = 1.0 - acosApprox(clamp(ndotl, -1.0, 1.0)) * 0.6366197724;
  return clamp(wrap * 0.495 + 0.5, 0.0, 1.0);
}
vec3 evalSH9(vec3 n) {
  vec3 L1 = -(n.x * uSH[3] + n.y * uSH[1] + n.z * uSH[2]);
  vec3 cruz = n.x * n.y * uSH[4] + n.y * n.z * uSH[5] + n.x * n.z * uSH[7];
  return 0.8862269254 * uSH[0] + 1.0233267546 * L1 + 0.8580855131 * cruz
       + 0.247707963 * (3.0 * n.z * n.z - 1.0) * uSH[6] + 0.4290427567 * (n.x * n.x - n.y * n.y) * uSH[8];
}
vec3 celLuz(vec3 albedo, vec2 uvN) {
  vec3 N = normalize(vNormalCel);
  if (!gl_FrontFacing) N = -N;
  if (uTemNormal > 0.5) {
    vec3 mapN = texture2D(uNormalCel, uvN).xyz * 2.0 - 1.0;
    vec3 T = normalize(vTanCel - dot(vTanCel, N) * N);
    vec3 B = cross(N, T) * vTanW;
    N = normalize(mat3(T, B, N) * mapN);
  }
  vec3 ambiente = max(evalSH9(N), vec3(0.0)) * albedo * 0.3183098862;
  vec3 luz = uLightColors[0] * texture2D(uCLUT, vec2(toonRampU(dot(N, normalize(uLightDirs[0]))), 0.5)).rgb
           + uLightColors[1] * texture2D(uCLUTFill, vec2(toonRampU(dot(N, normalize(uLightDirs[1]))), 0.5)).rgb;
  return ambiente + albedo * luz;
}
`;

interface Rampas { chave: THREE.Texture; fria: THREE.Texture }

/** o material cel do DSTS sobre o básico do three (que traz o esqueleto e a dobra do mundo); `rosto` troca o map_fragment */
function cel(map: THREE.Texture, normal: THREE.Texture | null, rampas: Rampas, chave: string, rosto?: (s: THREE.WebGLProgramParametersWithUniforms) => void): THREE.MeshBasicMaterial {
  map.colorSpace = THREE.SRGBColorSpace;
  const m = curvar(new THREE.MeshBasicMaterial({ map }));
  const curva = m.onBeforeCompile;
  m.onBeforeCompile = (s, r) => {
    curva(s, r);
    Object.assign(s.uniforms, {
      uCLUT: { value: rampas.chave }, uCLUTFill: { value: rampas.fria }, uNormalCel: { value: normal }, uTemNormal: { value: normal ? 1 : 0 },
      uSH: { value: LUZ.sh }, uLightDirs: { value: LUZ.dirs }, uLightColors: { value: LUZ.cores },
    });
    s.vertexShader = GLSL_CEL_VERT_PARS + s.vertexShader.replace("#include <worldpos_vertex>", "#include <worldpos_vertex>\n" + GLSL_CEL_VERT);
    s.fragmentShader = GLSL_CEL_FRAG_PARS + s.fragmentShader.replace("vec3 outgoingLight = reflectedLight.indirectDiffuse;",
      "vec3 outgoingLight = celLuz(diffuseColor.rgb, vMapUv);");
    rosto?.(s);
  };
  m.customProgramCacheKey = () => "curva-cel-" + chave;
  return m;
}

/* as rampas são dados, não cor: sem espaço de cor, presas na borda, sem mipmap (como o inputs/celClut.ts do dsts-viewer) */
function rampa(t: THREE.Texture): THREE.Texture {
  t.colorSpace = THREE.NoColorSpace;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.minFilter = t.magFilter = THREE.LinearFilter;
  t.generateMipmaps = false;
  t.needsUpdate = true;
  return t;
}

/* o rosto do DSTS: pele, íris e pálpebra numa passada só, com a linha da folha num uniforme (o piscar) */
function rosto(a01: THREE.Texture, p01: THREE.Texture, b01: THREE.Texture, linha: { value: number }, rampas: Rampas | null): THREE.Material {
  for (const t of [a01, p01, b01]) { t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.needsUpdate = true; }
  const compor = (s: THREE.WebGLProgramParametersWithUniforms) => {
    Object.assign(s.uniforms, { texIris: { value: p01 }, texPalp: { value: b01 }, linhaOlho: linha });
    s.vertexShader = "attribute vec2 uvIris;\nattribute vec2 uvPalp;\nvarying vec2 vIris;\nvarying vec2 vPalp;\n" +
      s.vertexShader.replace("#include <uv_vertex>", "#include <uv_vertex>\nvIris = uvIris;\nvPalp = uvPalp;");
    s.fragmentShader = "uniform sampler2D texIris;\nuniform sampler2D texPalp;\nuniform float linhaOlho;\nvarying vec2 vIris;\nvarying vec2 vPalp;\n" +
      s.fragmentShader.replace("#include <map_fragment>", `
        vec2 desl = vec2(0.0, linhaOlho / ${LINHAS_OLHO.toFixed(1)});
        vec4 pele = texture2D(map, vMapUv);
        vec4 iris = texture2D(texIris, vIris + desl);
        vec4 palp = texture2D(texPalp, vPalp + desl);
        diffuseColor.rgb *= mix(mix(pele.rgb, iris.rgb, iris.a), palp.rgb, palp.a);`);
  };
  if (rampas) return cel(a01, null, rampas, "rosto", compor);
  const m = toon({ map: a01 });
  const curva = m.onBeforeCompile;
  m.onBeforeCompile = (s, r) => { curva(s, r); compor(s); };
  m.customProgramCacheKey = () => "curva-rosto";
  return m;
}

/* o domo do olho (role eye_shine): um brilho somado, matcap do alfa do e01h, recortado pelo verde do b01m na mesma linha da folha
   (as linhas fechadas são zero, então o brilho some no piscar); como o eye_shine.frag.glsl do dsts-viewer, sem o recorte do COLOR_0 */
function brilhoOlho(e01h: THREE.Texture, b01m: THREE.Texture, linha: { value: number }): THREE.MeshMatcapMaterial {
  b01m.wrapS = b01m.wrapT = THREE.RepeatWrapping;
  b01m.needsUpdate = true;
  const m = curvar(new THREE.MeshMatcapMaterial({ matcap: e01h, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
  const curva = m.onBeforeCompile;
  m.onBeforeCompile = (s, r) => {
    curva(s, r);
    Object.assign(s.uniforms, { texMascara: { value: b01m }, linhaOlho: linha });
    s.vertexShader = "attribute vec2 uvOlho;\nvarying vec2 vOlho;\n" +
      s.vertexShader.replace("#include <begin_vertex>", "#include <begin_vertex>\nvOlho = uvOlho;");
    s.fragmentShader = "uniform sampler2D texMascara;\nuniform float linhaOlho;\nvarying vec2 vOlho;\n" +
      s.fragmentShader.replace("vec4 matcapColor = texture2D( matcap, uv );", `
        float recorte = texture2D(texMascara, vOlho + vec2(0.0, linhaOlho / ${LINHAS_OLHO.toFixed(1)})).g;
        vec4 matcapColor = vec4(vec3(texture2D(matcap, uv).a * recorte), 1.0);`);
  };
  m.customProgramCacheKey = () => "curva-brilho";
  return m;
}

/* o contorno: no jogo um shader incha a malha "outline" pela normal; aqui o mesmo, com as faces de trás em escuro */
function contorno(): THREE.MeshBasicMaterial {
  /* a malha do export vem com as faces viradas para dentro (o casco do contorno), então o lado que se esconde atrás do corpo é o da frente */
  const m = curvar(new THREE.MeshBasicMaterial({ color: 0x1b1b2f, side: THREE.FrontSide }));
  const curva = m.onBeforeCompile;
  m.onBeforeCompile = (s, r) => {
    curva(s, r);
    s.vertexShader = s.vertexShader.replace("#include <skinning_vertex>", `#include <skinning_vertex>\ntransformed += normalize(objectNormal) * ${CONTORNO.toFixed(4)};`);
  };
  m.customProgramCacheKey = () => "curva-contorno";
  return m;
}

export class Pet3D {
  readonly raiz = new THREE.Group();
  private readonly corpo = new THREE.Group();
  private mixer: THREE.AnimationMixer | null = null;
  private acoes = new Map<string, THREE.AnimationAction>();
  private atual: THREE.AnimationAction | null = null;
  private angulo = 0;
  private readonly linhaOlho = { value: 0 };
  private temRosto = false;
  private relogioPiscar = 0;
  private piscada = 0;
  private boca: THREE.Object3D | null = null;
  private golpe: { acao: THREE.AnimationAction; fogo: number | null } | null = null;
  clipeParado = "";
  clipeAndando = "";
  /** chamado no instante do disparo de um golpe de fogo: a posição da boca e a direção para onde o pet olha (no chão) */
  aoDisparar: ((boca: THREE.Vector3, frente: THREE.Vector3) => void) | null = null;

  constructor() {
    const sombra = new THREE.Mesh(GEO_SOMBRA, materialSombra());
    sombra.scale.set(0.8, 1, 0.55);
    sombra.position.y = 0.03;
    sombra.renderOrder = 1;
    this.raiz.add(this.corpo, sombra);
  }

  /** carrega o .glb e devolve os nomes dos clipes */
  async carregar(url: string): Promise<string[]> {
    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    const gltf = await loader.loadAsync(url);
    const cena = gltf.scene;
    const textura = (i: number) => gltf.parser.getDependency("texture", i) as Promise<THREE.Texture>;
    /* as rampas de toon do jogo, embutidas pelo extrator em todo .glb do DSTS */
    const json = gltf.parser.json as { textures?: { source: number }[]; images?: { name?: string }[] };
    const porImagem = (nome: string) => (json.textures ?? []).findIndex(t => json.images?.[t.source]?.name === nome);
    const iChave = porImagem("common_clut"), iFria = porImagem("clut001");
    const rampas: Rampas | null = iChave >= 0 && iFria >= 0
      ? { chave: rampa(await textura(iChave)), fria: rampa(await textura(iFria)) } : null;
    const malhas: THREE.SkinnedMesh[] = [];
    cena.traverse(o => { if ((o as THREE.Mesh).isMesh) malhas.push(o as THREE.SkinnedMesh); });
    for (const m of malhas) {
      m.frustumCulled = false;         // a dobra tira a malha da caixa que o three calcula
      const orig = m.material as THREE.MeshStandardMaterial;
      const idx = (orig.userData.dsts?.texture_indices ?? {}) as Record<string, number>;
      const g = m.geometry;
      if (g.getAttribute("tangent")) g.setAttribute("tanCel", g.getAttribute("tangent"));
      else g.setAttribute("tanCel", new THREE.Float32BufferAttribute(new Float32Array(g.getAttribute("position").count * 4), 4));
      if (idx.OverlayColorSampler3 !== undefined && idx.OverlayNormalSampler !== undefined && g.getAttribute("uv2")) {
        /* o rosto: a íris pelo UV2 e a folha das pálpebras pelo UV3 (TEXCOORD_1 e TEXCOORD_2 viram uv1 e uv2 no three) */
        g.setAttribute("uvIris", g.getAttribute("uv1"));
        g.setAttribute("uvPalp", g.getAttribute("uv2"));
        const [a01, p01, b01] = await Promise.all([idx.DiffuseColor, idx.OverlayNormalSampler, idx.OverlayColorSampler3].map(textura));
        m.material = rosto(a01, p01, b01, this.linhaOlho, rampas);
        this.temRosto = true;
      } else if (orig.userData.dsts_render?.role === "eye_shine" && idx.InnerGrowAValue !== undefined && idx.OverlayMaskSampler !== undefined) {
        g.setAttribute("uvOlho", g.getAttribute("uv"));
        const [e01h, b01m] = await Promise.all([idx.InnerGrowAValue, idx.OverlayMaskSampler].map(textura));
        m.material = brilhoOlho(e01h, b01m, this.linhaOlho);
        m.renderOrder = 2;               // o brilho somado depois do rosto
      } else if (orig.name === "outline") {
        m.material = contorno();
      } else if (rampas && orig.map) {
        const normal = idx.Bumpiness !== undefined && g.getAttribute("tangent") ? await textura(idx.Bumpiness) : null;
        m.material = cel(orig.map, normal, rampas, normal ? "normal" : "liso");
      } else {
        m.material = toon({ map: orig.map, color: orig.map ? 0xffffff : orig.color });
      }
    }
    this.boca = cena.getObjectByName("J_joe") ?? cena.getObjectByName("J_head") ?? null;
    /* a escala: a altura do modelo na pose de repouso vai para ALTURA, o pé no chão */
    cena.updateMatrixWorld(true);
    const caixa = new THREE.Box3().setFromObject(cena, true);
    const s = ALTURA / caixa.getSize(new THREE.Vector3()).y;
    cena.scale.setScalar(s);
    cena.position.y = -caixa.min.y * s;
    this.corpo.add(cena);
    this.mixer = new THREE.AnimationMixer(cena);
    for (const c of gltf.animations) this.acoes.set(c.name, this.mixer.clipAction(c));
    return gltf.animations.map(c => c.name);
  }

  /** os golpes que este modelo tem (pelo código do clipe) */
  golpesDisponiveis(): (typeof GOLPES)[number][] {
    return GOLPES.filter(g => [...this.acoes.keys()].some(n => n.endsWith("_" + g.codigo)));
  }

  get golpeando(): boolean { return this.golpe !== null; }

  /** toca o golpe uma vez por cima do parado/andando; false se o modelo não o tem ou já está golpeando */
  golpear(codigo: string): boolean {
    if (this.golpe) return false;
    const nome = [...this.acoes.keys()].find(n => n.endsWith("_" + codigo));
    const def = GOLPES.find(g => g.codigo === codigo);
    if (!nome || !def) return false;
    const a = this.acoes.get(nome)!;
    a.setLoop(THREE.LoopOnce, 1);
    a.clampWhenFinished = true;
    a.timeScale = 1;
    a.reset().fadeIn(0.1).play();
    this.atual?.fadeOut(0.1);
    this.atual = a;
    this.golpe = { acao: a, fogo: "fogo" in def ? def.fogo : null };
    return true;
  }

  private tocar(nome: string): void {
    const a = this.acoes.get(nome) ?? null;
    if (a === this.atual) return;
    a?.reset().fadeIn(0.15).play();
    this.atual?.fadeOut(0.15);
    this.atual = a;
  }

  /** a pálpebra: fechada por PISCAR_FECHADO_S ao fim de cada intervalo de PISCAR_ENTRE_S */
  private piscar(dt: number): void {
    this.relogioPiscar += dt;
    const entre = PISCAR_ENTRE_S[this.piscada % PISCAR_ENTRE_S.length];
    if (this.relogioPiscar >= entre + PISCAR_FECHADO_S) { this.relogioPiscar = 0; this.piscada++; }
    this.linhaOlho.value = this.relogioPiscar >= entre ? 1 : 0;
  }

  /** o golpe em curso: dispara o fogo quando o clipe passa do instante dele, e solta o golpe quando o clipe acaba */
  private seguirGolpe(): void {
    const g = this.golpe;
    if (!g) return;
    if (g.fogo !== null && g.acao.time >= g.fogo) {
      g.fogo = null;
      if (this.boca && this.aoDisparar) {
        this.raiz.updateMatrixWorld(true);
        const frente = new THREE.Vector3(Math.sin(this.angulo), 0, Math.cos(this.angulo));
        this.aoDisparar(this.boca.getWorldPosition(new THREE.Vector3()).addScaledVector(frente, 0.15), frente);
      }
    }
    if (!g.acao.isRunning()) this.golpe = null;
  }

  /** um passo de desenho: a posição no chão, a direção de andar (dx, dz), o intervalo em s */
  atualizar(x: number, y: number, z: number, dx: number, dz: number, andando: boolean, dt: number, correndo: boolean): void {
    if (!this.golpe) {
      this.tocar(andando ? this.clipeAndando : this.clipeParado);
      if (this.atual) this.atual.timeScale = andando && correndo ? 1.5 : 1;
    }
    this.mixer?.update(dt);
    this.raiz.position.set(x, y, z);
    this.seguirGolpe();
    if (this.temRosto) this.piscar(dt);
    if (andando && !this.golpe) {
      /* o modelo olha para +z na pose de repouso */
      const alvo = Math.atan2(dx, dz);
      let d = alvo - this.angulo;
      d = Math.atan2(Math.sin(d), Math.cos(d));
      this.angulo += Math.sign(d) * Math.min(Math.abs(d), GIRO_POR_S * dt);
    }
    this.corpo.rotation.y = this.angulo;
  }
}
