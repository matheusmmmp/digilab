/* O visual do habitat (src/habitat.ts): o pos-processo do POC mapa_ac (poc/mapa_ac/pos.ts, #480), copiado e nao importado (a ilha nao
   importa o POC). A cena e desenhada num alvo menor (o "pixel", com filtro nearest na volta a tela) e um quadro de tela cheia aplica:
     - o tilt-shift: desfoque que cresce com a distancia vertical a faixa de foco, o jeito barato do HD-2D (sem mapa de profundidade);
       aqui a faixa segue o pet (foco, de 0 embaixo a 1 em cima), em vez de ficar fixa um pouco abaixo do meio como no POC;
     - a cor: saturacao e brilho (o "GBA HD" do Cassette Beasts e claro e saturado) e uma vinheta leve.
   No visual normal desenha direto na tela, como antes. So desenho: PROPOSTO, SEM FONTE (os valores sao os do POC).
   O contorno (o cel shading do estilo digital, docs/TAREFA_V3_MAPA_DIGITAL.md, D5): o estilo que o pede (Estilo.contorno) desenha a cena
   num alvo com a profundidade, e o quadro passa o traco de nanquim onde a profundidade quebra (o laplaciano da profundidade linear: zero
   num plano inclinado, grande na silhueta). Pega tudo de uma vez: as arvores, os kits, os lugares, os itens e o terreno; o traco some com
   a distancia, como a nevoa. Um desenho a mais (o quadro). O pet fica fora (SEM_CONTORNO). */
import * as THREE from "three";
import type { Visual } from "../../../habitat.ts";

export interface AjustePos { pixel: number; tilt: boolean; saturacao: number; brilho: number; vinheta: number }
export const PRESETS: Readonly<Record<Visual, AjustePos>> = {
  normal: { pixel: 1, tilt: false, saturacao: 1, brilho: 1, vinheta: 0 },
  "gba-hd": { pixel: 3, tilt: false, saturacao: 1.22, brilho: 1.06, vinheta: 0.12 },
  "hd-2d": { pixel: 2, tilt: true, saturacao: 1.1, brilho: 1.02, vinheta: 0.35 },
};

/** o traco de nanquim (Pos, o contorno): a cor, a forca, a largura (px de CSS), o limiar (fracao da profundidade do ponto) e onde ele some
    (celulas da camera). PROPOSTO, SEM FONTE */
export interface Contorno { tinta: number; forca: number; largura: number; limiar: number; some: readonly [number, number] }
/** a camada do three das coisas que ficam sem o traco (o pet em papel: so o mapa e cel shading, pedido do Matheus): desenhadas numa
    passada propria, depois do quadro, contra a profundidade da cena */
export const SEM_CONTORNO = 1;

const VERT = `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;
const FRAG = `
uniform sampler2D tCena;
uniform vec2 uTexel;
uniform float uTilt, uFoco, uSat, uBrilho, uVinheta;
uniform sampler2D tProf;
uniform float uContorno, uPerto, uLonge, uForca, uLargura, uLimiar;
uniform vec2 uSome;
uniform vec3 uTinta;
varying vec2 vUv;
float linear(float z) { return (2.0 * uPerto * uLonge) / (uLonge + uPerto - (z * 2.0 - 1.0) * (uLonge - uPerto)); }
void main() {
  vec3 c = texture2D(tCena, vUv).rgb;
  if (uContorno > 0.0) {
    vec2 t = uTexel * uLargura;
    float d0 = linear(texture2D(tProf, vUv).x);
    float lap = linear(texture2D(tProf, vUv + vec2(t.x, 0.0)).x) + linear(texture2D(tProf, vUv - vec2(t.x, 0.0)).x)
      + linear(texture2D(tProf, vUv + vec2(0.0, t.y)).x) + linear(texture2D(tProf, vUv - vec2(0.0, t.y)).x) - 4.0 * d0;
    float e = smoothstep(uLimiar * d0, uLimiar * d0 * 2.0, lap) * (1.0 - smoothstep(uSome.x, uSome.y, d0));
    c = mix(c, uTinta, e * uForca);
  }
  if (uTilt > 0.0) {
    /* fora da faixa de foco (em volta do pet), um disco de 12 amostras que cresce ate ~6 texels */
    float r = 6.0 * smoothstep(0.1, 0.42, abs(vUv.y - uFoco));
    if (r > 0.3) {
      vec3 soma = c;
      for (int i = 0; i < 12; i++) {
        float a = float(i) * 2.39996;
        float k = sqrt((float(i) + 0.5) / 12.0);
        soma += texture2D(tCena, vUv + vec2(cos(a), sin(a)) * k * r * uTexel).rgb;
      }
      c = soma / 13.0;
    }
  }
  float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
  c = mix(vec3(l), c, uSat) * uBrilho;
  vec2 d = vUv - 0.5;
  c *= 1.0 - uVinheta * dot(d, d) * 2.0;
  gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
  /* com o contorno, o quadro deixa na tela a profundidade da cena: o pet (a camada SEM_CONTORNO) e desenhado depois, por cima, atras do
     que esta na frente dele */
  gl_FragDepth = uContorno > 0.0 ? texture2D(tProf, vUv).x : 1.0;
  #include <colorspace_fragment>
}`;

export class Pos {
  private alvo: THREE.WebGLRenderTarget | null = null;
  private readonly quadro: THREE.Mesh<THREE.PlaneGeometry, THREE.ShaderMaterial>;
  private readonly cenaQuadro = new THREE.Scene();
  private readonly camQuadro = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  private readonly renderer: THREE.WebGLRenderer;

  constructor(renderer: THREE.WebGLRenderer) {
    this.renderer = renderer;
    this.quadro = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
      vertexShader: VERT, fragmentShader: FRAG, depthTest: true, depthWrite: true, depthFunc: THREE.AlwaysDepth,
      uniforms: { tCena: { value: null }, uTexel: { value: new THREE.Vector2() }, uTilt: { value: 0 }, uFoco: { value: 0.44 },
        uSat: { value: 1 }, uBrilho: { value: 1 }, uVinheta: { value: 0 },
        tProf: { value: null }, uContorno: { value: 0 }, uPerto: { value: 0.1 }, uLonge: { value: 100 }, uForca: { value: 0 }, uLargura: { value: 1 },
        uLimiar: { value: 0.05 }, uSome: { value: new THREE.Vector2(40, 60) }, uTinta: { value: new THREE.Color() } },
    }));
    this.quadro.frustumCulled = false;
    this.cenaQuadro.add(this.quadro);
  }

  /** desenha a cena com o visual `a`; `foco` e a altura do pet na tela (0 embaixo, 1 em cima), o centro da faixa do tilt-shift; `contorno`:
      o traco de nanquim do estilo (null: sem) */
  desenhar(cena: THREE.Scene, camera: THREE.PerspectiveCamera, a: AjustePos, foco: number, contorno: Contorno | null = null): void {
    if (!contorno && a.pixel <= 1 && !a.tilt && a.saturacao === 1 && a.brilho === 1 && a.vinheta === 0) {
      this.renderer.setRenderTarget(null);
      this.renderer.render(cena, camera);
      return;
    }
    const tam = this.renderer.getDrawingBufferSize(new THREE.Vector2());
    /* com pixel, o alvo tem 1/pixel do tamanho em pixels de CSS (o pixel do mundo nao depende da densidade da tela) */
    const div = a.pixel <= 1 ? 1 : a.pixel * this.renderer.getPixelRatio();
    const w = Math.max(1, Math.round(tam.x / div)), h = Math.max(1, Math.round(tam.y / div));
    const filtro = a.pixel <= 1 ? THREE.LinearFilter : THREE.NearestFilter;
    const prof = !!contorno;
    if (!this.alvo || this.alvo.width !== w || this.alvo.height !== h || this.alvo.texture.magFilter !== filtro || !!this.alvo.depthTexture !== prof) {
      this.alvo?.depthTexture?.dispose();
      this.alvo?.dispose();
      this.alvo = new THREE.WebGLRenderTarget(w, h, { minFilter: filtro, magFilter: filtro, depthBuffer: true, samples: a.pixel <= 1 ? 4 : 0,
        depthTexture: prof ? new THREE.DepthTexture(w, h) : undefined });
    }
    this.renderer.setRenderTarget(this.alvo);
    if (contorno) camera.layers.disable(SEM_CONTORNO);
    this.renderer.render(cena, camera);
    camera.layers.enable(SEM_CONTORNO);
    this.renderer.setRenderTarget(null);
    const u = this.quadro.material.uniforms;
    u.tCena.value = this.alvo.texture;
    u.uTexel.value.set(1 / w, 1 / h);
    u.uTilt.value = a.tilt ? 1 : 0;
    u.uFoco.value = Math.min(0.9, Math.max(0.1, foco));
    u.uSat.value = a.saturacao;
    u.uBrilho.value = a.brilho;
    u.uVinheta.value = a.vinheta;
    u.uContorno.value = contorno ? 1 : 0;
    if (contorno) {
      u.tProf.value = this.alvo.depthTexture;
      u.uPerto.value = camera.near; u.uLonge.value = camera.far;
      u.uTinta.value.setHex(contorno.tinta); u.uForca.value = contorno.forca;
      /* a largura em px de CSS: no alvo, que ja tem 1/pixel do tamanho, vira texels */
      u.uLargura.value = Math.max(1, contorno.largura * this.renderer.getPixelRatio() / div);
      u.uLimiar.value = contorno.limiar; u.uSome.value.set(contorno.some[0], contorno.some[1]);
    }
    this.renderer.render(this.cenaQuadro, this.camQuadro);
    if (contorno) {
      /* a segunda passada: so a camada sem traco, sem o fundo e sem limpar a tela */
      const fundo = cena.background, limpa = this.renderer.autoClear;
      cena.background = null; this.renderer.autoClear = false;
      camera.layers.set(SEM_CONTORNO);
      this.renderer.render(cena, camera);
      camera.layers.set(0); camera.layers.enable(SEM_CONTORNO);
      cena.background = fundo; this.renderer.autoClear = limpa;
    }
  }

  dispose(): void { this.alvo?.depthTexture?.dispose(); this.alvo?.dispose(); this.quadro.geometry.dispose(); this.quadro.material.dispose(); }
}
