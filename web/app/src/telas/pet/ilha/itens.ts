/* Os itens do mundo na ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, secao 5 e H4): o ninho e o comedouro do layout, e a racao, a fruta e a
   bola onde o motor diz, entrando e saindo como no modo mundo de antes (cena3d.ts, sincronizarMundo). So vista: le o Motor.mundo.
     - o ninho: um ninho de folhas no chao, com uma luz fraca a noite (PROPOSTO);
     - o comedouro: uma tigela;
     - a racao: um montinho, madura e podre com cores diferentes;
     - a fruta no chao: uma fruta do tipo a, b ou c, cada uma com a sua cor;
     - a bola: a bola, que desliza ate onde o motor diz e gira ao rolar, e some enquanto o dono a arrasta (CENA.bolaNaMao);
     - o saco de pancada do treino (docs/TAREFA_V3_HABITAT_OBJETOS.md): um poste com o saco pendurado, perto do ninho, que balanca a cada
       golpe (baterNoSaco);
     - o kit medico: uma maleta branca com a cruz, ao lado do ninho, enquanto o pet esta lesionado;
   todos com a sombra redonda. As posicoes do motor sao em subunidades; aqui, em celulas. Os tamanhos e as cores sao do desenho:
   PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import type { Mundo } from "../../../../motor/index.ts";
import { ninhoDe } from "../vistaMundo.ts";
import { CENA } from "../cenaEstado.ts";
import { BOLA_SALTO, BOLA_TAU_MS, KIT_DESDE_NINHO, LUZ_NINHO, SACO_BALANCO, SACO_DESDE_NINHO } from "./constantes.ts";
import { GEO_SOMBRA, curvar, materialSombra, toon } from "./cena.ts";

const COR_RACAO = { madura: [0x9b6a3c, 0xc08a55], podre: [0x6b6b3a, 0x85854a] } as const;
/** a cor de cada fruta do motor (os tipos de motor/mundo.ts, FRUTAS) */
const COR_FRUTA: Readonly<Record<string, number>> = { a: 0xe8533f, b: 0xf2b134, c: 0x8a5bd6 };
const R_BOLA = 0.36;

/** uma sombra redonda no chao, de raio r (celulas) */
function sombra(r: number): THREE.Mesh {
  const s = new THREE.Mesh(GEO_SOMBRA, materialSombra());
  s.scale.set(r * 2, 1, r * 2);
  s.position.y = 0.02;
  s.renderOrder = 1;
  return s;
}

/** o ninho de folhas: um anel de folhas e o fundo de palha */
function ninho(): THREE.Group {
  const g = new THREE.Group();
  const fundo = new THREE.Mesh(new THREE.CircleGeometry(0.85, 20).rotateX(-Math.PI / 2), toon({ color: 0xc9a36a }));
  fundo.position.y = 0.04;
  const anel = new THREE.Mesh(new THREE.TorusGeometry(0.85, 0.24, 6, 18).rotateX(Math.PI / 2).scale(1, 0.7, 1), toon({ color: 0x6aa84f }));
  anel.position.y = 0.12;
  const folhas = new THREE.Group();
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * Math.PI * 2, f = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 4).scale(1.4, 0.5, 0.8), toon({ color: i % 2 ? 0x7cbf5a : 0x5e9a44 }));
    f.position.set(Math.cos(a) * 0.95, 0.2, Math.sin(a) * 0.95);
    f.rotation.y = -a;
    folhas.add(f);
  }
  g.add(sombra(1.25), fundo, anel, folhas);
  return g;
}
/** a tigela do comedouro */
function tigela(): THREE.Group {
  const perfil = [[0, 0], [0.42, 0], [0.5, 0.06], [0.56, 0.3], [0.5, 0.32], [0.44, 0.12], [0, 0.12]].map(([x, y]) => new THREE.Vector2(x, y));
  const g = new THREE.Group();
  g.add(sombra(0.7), new THREE.Mesh(new THREE.LatheGeometry(perfil, 20), toon({ color: 0xf4f7fb, side: THREE.DoubleSide })));
  const borda = new THREE.Mesh(new THREE.TorusGeometry(0.53, 0.035, 5, 20).rotateX(Math.PI / 2), toon({ color: 0x4f8fd6 }));
  borda.position.y = 0.31;
  g.add(borda);
  return g;
}
/** o montinho de racao: tres bolinhas achatadas */
function montinho(): THREE.Group {
  const g = new THREE.Group();
  g.add(sombra(0.4));
  for (const [x, z, r, y] of [[-0.12, 0.05, 0.17, 0.08], [0.12, 0.04, 0.16, 0.08], [0, -0.1, 0.15, 0.17]] as const) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(r, 8, 6).scale(1, 0.7, 1), toon({ color: COR_RACAO.madura[0] }));
    b.position.set(x, y, z);
    g.add(b);
  }
  return g;
}
/** a fruta no chao: uma esfera da cor do tipo, com o cabinho e a folha */
function fruta(tipo: string): THREE.Group {
  const cor = COR_FRUTA[tipo];
  if (cor === undefined) throw new Error("fruta sem cor na ilha: " + tipo);
  const g = new THREE.Group(), corpo = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 8), toon({ color: cor }));
  corpo.position.y = 0.2;
  const folha = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 4).scale(1.6, 0.4, 0.8), toon({ color: 0x4e9a3a }));
  folha.position.set(0.07, 0.41, 0);
  g.add(sombra(0.3), corpo, folha);
  return g;
}
/** a bola: branca com duas faixas azuis */
function bola(): { g: THREE.Group; esfera: THREE.Mesh } {
  const c = document.createElement("canvas");
  c.width = 64; c.height = 32;
  const x = c.getContext("2d");
  if (!x) throw new Error("canvas 2d indisponível");
  x.fillStyle = "#ffffff"; x.fillRect(0, 0, 64, 32);
  x.fillStyle = "#378add"; x.fillRect(0, 7, 64, 6); x.fillRect(0, 19, 64, 6);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  const esfera = new THREE.Mesh(new THREE.SphereGeometry(R_BOLA, 16, 12), toon({ map: t }));
  esfera.position.y = R_BOLA;
  const g = new THREE.Group();
  g.add(sombra(0.4), esfera);
  return { g, esfera };
}
/** o saco de pancada: a base, o poste, o braco e a corrente, e o saco (vermelho, com as faixas) pendurado no `pivo`, que balanca */
function saco(): { g: THREE.Group; pivo: THREE.Group } {
  const g = new THREE.Group(), madeira = toon({ color: 0x8a5a33 }), metal = toon({ color: 0x9aa4ad });
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.5, 0.12, 14), toon({ color: 0x6f6f78 }));
  base.position.set(-0.55, 0.06, 0);
  const poste = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 2.5, 8), madeira);
  poste.position.set(-0.55, 1.25, 0);
  const braco = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.12, 0.14), madeira);
  braco.position.set(-0.2, 2.42, 0);
  const pivo = new THREE.Group();
  pivo.position.set(0.1, 2.36, 0);
  const corrente = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.4, 5), metal);
  corrente.position.y = -0.2;
  const corpo = new THREE.Mesh(new THREE.CapsuleGeometry(0.3, 0.75, 4, 12), toon({ color: 0xc8432f }));
  corpo.position.y = -0.4 - 0.675;
  const tampa = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.26, 0.1, 12), toon({ color: 0x3a3a44 }));
  tampa.position.y = -0.44;
  pivo.add(corrente, tampa, corpo);
  for (const y of [-0.82, -1.33]) {
    const faixa = new THREE.Mesh(new THREE.CylinderGeometry(0.315, 0.315, 0.07, 14), toon({ color: 0xf4f7fb }));
    faixa.position.y = y;
    pivo.add(faixa);
  }
  g.add(sombra(0.7), base, poste, braco, pivo);
  return { g, pivo };
}
/** o kit medico: a maleta branca, a alca e a cruz vermelha em cima */
function kit(): THREE.Group {
  const g = new THREE.Group(), vermelho = toon({ color: 0xd8382f });
  const caixa = new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.36, 0.42), toon({ color: 0xf6f8fb }));
  caixa.position.y = 0.18;
  const alca = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.025, 5, 12, Math.PI), toon({ color: 0x3a3a44 }));
  alca.position.y = 0.36;
  const cruzA = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.02, 0.08), vermelho), cruzB = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.02, 0.26), vermelho);
  cruzA.position.set(0.12, 0.365, 0); cruzB.position.set(0.12, 0.365, 0);
  const frente = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.06, 0.02), vermelho), frenteV = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.2, 0.02), vermelho);
  frente.position.set(0, 0.18, 0.215); frenteV.position.set(0, 0.18, 0.215);
  g.add(sombra(0.45), caixa, alca, cruzA, cruzB, frente, frenteV);
  return g;
}
/** a luz fraca do ninho a noite: um brilho no chao, aditivo, que nao ilumina mais nada */
function brilho(): THREE.Mesh {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const x = c.getContext("2d");
  if (!x) throw new Error("canvas 2d indisponível");
  const gr = x.createRadialGradient(32, 32, 2, 32, 32, 31);
  gr.addColorStop(0, `rgba(${LUZ_NINHO.cor},0.55)`); gr.addColorStop(1, `rgba(${LUZ_NINHO.cor},0)`);
  x.fillStyle = gr; x.fillRect(0, 0, 64, 64);
  const m = new THREE.Mesh(GEO_SOMBRA, curvar(new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending })));
  m.scale.set(LUZ_NINHO.raio * 2, 1, LUZ_NINHO.raio * 2);
  m.position.y = 0.05;
  m.renderOrder = 1;
  return m;
}

export class Itens {
  readonly raiz = new THREE.Group();
  private readonly comidas = new Map<number, { g: THREE.Group; podre: boolean | null }>();
  private readonly bola = bola();
  private readonly brilho = brilho();
  private readonly saco = saco();
  private readonly kit = kit();
  private readonly sub: number;
  /** onde a bola esta desenhada (celulas), indo ate a do motor sem pular; null antes do primeiro quadro */
  private bolaCel: [number, number] | null = null;
  /** a bola estava na mao do dono no quadro anterior: ao cair, ela aparece onde caiu (sem rolar do lugar antigo) */
  private naMaoAntes = false;
  private readonly giro = new THREE.Quaternion();
  /** o ultimo golpe no saco: quando (ms da vista) e o eixo do balanco no chao (o saco vai para longe de quem bateu) */
  private golpeSaco: { em: number; eixo: THREE.Vector3 } | null = null;
  /** onde fica o saco de pancada (celulas) */
  readonly sacoEm: [number, number];

  constructor(mu: Mundo) {
    const sub = (this.sub = mu.cm.sub), [nx, ny] = ninhoDe(mu.cm), n = ninho(), t = tigela();
    n.position.set(nx / sub, 0, ny / sub);
    t.position.set(mu.comedouro[0] / sub, 0, mu.comedouro[1] / sub);
    this.brilho.position.set(nx / sub, 0.05, ny / sub);
    this.brilho.visible = false;
    this.sacoEm = [nx / sub + SACO_DESDE_NINHO[0], ny / sub + SACO_DESDE_NINHO[1]];
    this.saco.g.position.set(this.sacoEm[0], 0, this.sacoEm[1]);
    this.kit.position.set(nx / sub + KIT_DESDE_NINHO[0], 0, ny / sub + KIT_DESDE_NINHO[1]);
    this.kit.rotation.y = -0.4;
    this.kit.visible = false;
    this.raiz.add(n, t, this.bola.g, this.brilho, this.saco.g, this.kit);
  }

  /** onde a bola esta desenhada (subunidades do mapa), para pegar a bola na cena (PorBola.tsx); null antes do primeiro quadro */
  get bolaDesenhada(): [number, number] | null { return this.bolaCel && [this.bolaCel[0] * this.sub, this.bolaCel[1] * this.sub]; }

  /** um golpe no saco de quem esta em `de` (celulas): o saco balanca para longe dele, no plano vertical que passa pelos dois. O eixo e
      d x cima (d, a direcao de quem bateu ate o saco): o angulo positivo leva a ponta do saco no sentido de d */
  baterNoSaco(agora: number, de: readonly [number, number]): void {
    const dx = this.sacoEm[0] - de[0], dz = this.sacoEm[1] - de[1], d = Math.hypot(dx, dz) || 1;
    this.golpeSaco = { em: agora, eixo: new THREE.Vector3(-dz / d, 0, dx / d) };
  }

  /** a racao e a fruta entram e saem e a podre muda de cor; a bola vai aonde o motor diz, girando; o saco balanca; o kit so com a lesao;
      a luz do ninho so a noite */
  sincronizar(mu: Mundo, tick: number, noite: boolean, agora: number, dtMs: number, lesionado: boolean, reduzido: boolean): void {
    const vistas = new Set<number>(), sub = this.sub;
    for (const c of mu.comidas.values()) {
      const sit = mu.situacao(c, tick);
      if (sit === null) continue;
      vistas.add(c.id);
      let item = this.comidas.get(c.id);
      if (!item) {
        const g = c.tipo === "racao" ? montinho() : fruta(c.tipo);
        g.position.set(c.x / sub, 0, c.y / sub);
        g.rotation.y = (c.id * 1.7) % (Math.PI * 2);
        this.raiz.add(g);
        item = { g, podre: null };
        this.comidas.set(c.id, item);
      }
      const podre = sit === "podre";
      if (c.tipo === "racao" && item.podre !== podre) {
        const [base, topo] = podre ? COR_RACAO.podre : COR_RACAO.madura;
        item.g.children.slice(1).forEach((b, i) => ((b as THREE.Mesh).material as THREE.MeshToonMaterial).color.setHex(i === 2 ? topo : base));
      }
      item.podre = podre;
    }
    for (const [id, item] of this.comidas) if (!vistas.has(id)) { this.raiz.remove(item.g); this.comidas.delete(id); }
    this.moverBola(mu.bolaEm(tick), dtMs, reduzido || this.naMaoAntes);
    this.naMaoAntes = CENA.bolaNaMao;
    this.bola.g.visible = !CENA.bolaNaMao;
    this.balancarSaco(agora, reduzido);
    this.kit.visible = lesionado;
    this.brilho.visible = noite;
  }

  /** a bola desenhada vai ate a do motor (constante BOLA_TAU_MS; salta longe ou com movimento reduzido) e gira em volta do eixo do chao
      perpendicular ao caminho, o que ela andou sobre o raio */
  private moverBola([bx, by]: readonly [number, number], dtMs: number, saltar: boolean): void {
    const alvo: [number, number] = [bx / this.sub, by / this.sub], p = this.bolaCel;
    if (!p || saltar || Math.hypot(alvo[0] - p[0], alvo[1] - p[1]) > BOLA_SALTO) { this.bolaCel = alvo; }
    else {
      const k = 1 - Math.exp(-Math.max(0, dtMs) / BOLA_TAU_MS), dx = (alvo[0] - p[0]) * k, dz = (alvo[1] - p[1]) * k, d = Math.hypot(dx, dz);
      this.bolaCel = [p[0] + dx, p[1] + dz];
      if (d > 1e-5) this.bola.esfera.quaternion.premultiply(this.giro.setFromAxisAngle(new THREE.Vector3(dz / d, 0, -dx / d), d / R_BOLA));
    }
    this.bola.g.position.set(this.bolaCel[0], 0, this.bolaCel[1]);
  }

  /** o saco balanca para longe de quem bateu e amortece */
  private balancarSaco(agora: number, reduzido: boolean): void {
    const g = this.golpeSaco, t = g ? agora - g.em : Infinity;
    const { amplitude, tau, periodo } = SACO_BALANCO;
    const a = !g || reduzido || t > 6 * tau ? 0 : amplitude * Math.exp(-t / tau) * Math.sin((2 * Math.PI * t) / periodo);
    if (g) this.saco.pivo.quaternion.setFromAxisAngle(g.eixo, a); else this.saco.pivo.quaternion.identity();
  }
}
