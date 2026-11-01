/* O visual do habitat (src/habitat.ts): o pos-processo do POC mapa_ac (poc/mapa_ac/pos.ts, #480), copiado e nao importado (a ilha nao
   importa o POC). A cena e desenhada num alvo menor (o "pixel", com filtro nearest na volta a tela) e um quadro de tela cheia aplica:
     - o tilt-shift: desfoque que cresce com a distancia vertical a faixa de foco, o jeito barato do HD-2D (sem mapa de profundidade);
       aqui a faixa segue o pet (foco, de 0 embaixo a 1 em cima), em vez de ficar fixa um pouco abaixo do meio como no POC;
     - a cor: saturacao e brilho (o "GBA HD" do Cassette Beasts e claro e saturado) e uma vinheta leve.
   No visual normal desenha direto na tela, como antes. So desenho: PROPOSTO, SEM FONTE (os valores sao os do POC). */
import * as THREE from "three";
import type { Visual } from "../../../habitat.ts";

export interface AjustePos { pixel: number; tilt: boolean; saturacao: number; brilho: number; vinheta: number }
export const PRESETS: Readonly<Record<Visual, AjustePos>> = {
  normal: { pixel: 1, tilt: false, saturacao: 1, brilho: 1, vinheta: 0 },
  "gba-hd": { pixel: 3, tilt: false, saturacao: 1.22, brilho: 1.06, vinheta: 0.12 },
  "hd-2d": { pixel: 2, tilt: true, saturacao: 1.1, brilho: 1.02, vinheta: 0.35 },
};

const VERT = `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;
const FRAG = `
uniform sampler2D tCena;
uniform vec2 uTexel;
uniform float uTilt, uFoco, uSat, uBrilho, uVinheta;
varying vec2 vUv;
void main() {
  vec3 c = texture2D(tCena, vUv).rgb;
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
      vertexShader: VERT, fragmentShader: FRAG, depthTest: false, depthWrite: false,
      uniforms: { tCena: { value: null }, uTexel: { value: new THREE.Vector2() }, uTilt: { value: 0 }, uFoco: { value: 0.44 },
        uSat: { value: 1 }, uBrilho: { value: 1 }, uVinheta: { value: 0 } },
    }));
    this.quadro.frustumCulled = false;
    this.cenaQuadro.add(this.quadro);
  }

  /** desenha a cena com o visual `a`; `foco` e a altura do pet na tela (0 embaixo, 1 em cima), o centro da faixa do tilt-shift */
  desenhar(cena: THREE.Scene, camera: THREE.Camera, a: AjustePos, foco: number): void {
    if (a.pixel <= 1 && !a.tilt && a.saturacao === 1 && a.brilho === 1 && a.vinheta === 0) {
      this.renderer.setRenderTarget(null);
      this.renderer.render(cena, camera);
      return;
    }
    const tam = this.renderer.getDrawingBufferSize(new THREE.Vector2());
    /* com pixel, o alvo tem 1/pixel do tamanho em pixels de CSS (o pixel do mundo nao depende da densidade da tela) */
    const div = a.pixel <= 1 ? 1 : a.pixel * this.renderer.getPixelRatio();
    const w = Math.max(1, Math.round(tam.x / div)), h = Math.max(1, Math.round(tam.y / div));
    const filtro = a.pixel <= 1 ? THREE.LinearFilter : THREE.NearestFilter;
    if (!this.alvo || this.alvo.width !== w || this.alvo.height !== h || this.alvo.texture.magFilter !== filtro) {
      this.alvo?.dispose();
      this.alvo = new THREE.WebGLRenderTarget(w, h, { minFilter: filtro, magFilter: filtro, depthBuffer: true, samples: a.pixel <= 1 ? 4 : 0 });
    }
    this.renderer.setRenderTarget(this.alvo);
    this.renderer.render(cena, camera);
    this.renderer.setRenderTarget(null);
    const u = this.quadro.material.uniforms;
    u.tCena.value = this.alvo.texture;
    u.uTexel.value.set(1 / w, 1 / h);
    u.uTilt.value = a.tilt ? 1 : 0;
    u.uFoco.value = Math.min(0.9, Math.max(0.1, foco));
    u.uSat.value = a.saturacao;
    u.uBrilho.value = a.brilho;
    u.uVinheta.value = a.vinheta;
    this.renderer.render(this.cenaQuadro, this.camQuadro);
  }

  dispose(): void { this.alvo?.dispose(); this.quadro.geometry.dispose(); this.quadro.material.dispose(); }
}
