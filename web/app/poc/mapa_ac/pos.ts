/* O pós-processo do mapa_ac, para comparar os visuais 2.5D do mapeamento (docs/MAPEAMENTO_2_5D.md): a cena é desenhada num alvo menor
   (o "pixel", com filtro nearest na volta à tela), e um quadro de tela cheia aplica:
     - o tilt-shift: desfoque que cresce com a distância vertical à faixa de foco (o jeito barato do HD-2D, sem mapa de profundidade);
     - a cor: saturação e brilho (o "GBA HD" do Cassette Beasts é claro e saturado) e uma vinheta leve.
   Com pixel 1, sem tilt e cor neutra, desenha direto na tela, como antes. Só desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";

export interface AjustePos { pixel: number; tilt: boolean; saturacao: number; brilho: number; vinheta: number }
export const PRESETS: Record<string, AjustePos> = {
  neutro: { pixel: 1, tilt: false, saturacao: 1, brilho: 1, vinheta: 0 },
  "gba-hd": { pixel: 3, tilt: false, saturacao: 1.22, brilho: 1.06, vinheta: 0.12 },
  "hd-2d": { pixel: 2, tilt: true, saturacao: 1.1, brilho: 1.02, vinheta: 0.35 },
};

const VERT = `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;
const FRAG = `
uniform sampler2D tCena;
uniform vec2 uTexel;
uniform float uTilt, uSat, uBrilho, uVinheta;
varying vec2 vUv;
void main() {
  vec3 c = texture2D(tCena, vUv).rgb;
  if (uTilt > 0.0) {
    /* a faixa de foco um pouco abaixo do meio (onde fica o pet); fora dela, um disco de 12 amostras que cresce até ~6 texels */
    float r = 6.0 * smoothstep(0.1, 0.42, abs(vUv.y - 0.44));
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
  ajuste: AjustePos = { ...PRESETS.neutro };
  private alvo: THREE.WebGLRenderTarget | null = null;
  private readonly quadro: THREE.Mesh<THREE.PlaneGeometry, THREE.ShaderMaterial>;
  private readonly cenaQuadro = new THREE.Scene();
  private readonly camQuadro = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  constructor(private readonly renderer: THREE.WebGLRenderer) {
    this.quadro = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
      vertexShader: VERT, fragmentShader: FRAG, depthTest: false, depthWrite: false,
      uniforms: { tCena: { value: null }, uTexel: { value: new THREE.Vector2() }, uTilt: { value: 0 }, uSat: { value: 1 }, uBrilho: { value: 1 },
        uVinheta: { value: 0 } },
    }));
    this.quadro.frustumCulled = false;
    this.cenaQuadro.add(this.quadro);
  }

  private neutro(): boolean {
    const a = this.ajuste;
    return a.pixel <= 1 && !a.tilt && a.saturacao === 1 && a.brilho === 1 && a.vinheta === 0;
  }

  desenhar(cena: THREE.Scene, camera: THREE.Camera): void {
    if (this.neutro()) { this.renderer.setRenderTarget(null); this.renderer.render(cena, camera); return; }
    const a = this.ajuste, tam = this.renderer.getDrawingBufferSize(new THREE.Vector2());
    /* com pixel, o alvo tem 1/pixel do tamanho em pixels de CSS (o pixel do sprite não depende da densidade da tela) */
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
    u.uSat.value = a.saturacao;
    u.uBrilho.value = a.brilho;
    u.uVinheta.value = a.vinheta;
    this.renderer.render(this.cenaQuadro, this.camQuadro);
  }
}
