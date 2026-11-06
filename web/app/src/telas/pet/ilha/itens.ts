/* Os itens do mundo na ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, secao 5 e H4): o ninho e o comedouro do layout, e a racao, a fruta e a
   bola onde o motor diz, entrando e saindo como no modo mundo de antes (cena3d.ts, sincronizarMundo). So vista: le o Motor.mundo.
     - o ninho: um ninho de folhas no chao, com uma luz fraca a noite (PROPOSTO);
     - o comedouro: uma tigela;
     - a racao: um montinho, madura e podre com cores diferentes;
     - a fruta no chao: uma fruta do tipo a, b ou c, cada uma com a sua cor;
     - a bola: a bola, que desliza ate onde o motor diz e gira ao rolar, e some enquanto o dono a arrasta (CENA.bolaNaMao);
     - o saco de pancada do treino (docs/TAREFA_V3_HABITAT_OBJETOS.md): um poste com o saco pendurado, perto do ninho, que balanca a cada
       golpe (baterNoSaco);
     - o kit medico: um caixote com a tampa branca e a cruz (o item gerado), ao lado do ninho, enquanto o pet esta lesionado;
     - o coco: um por unidade da sujeira do motor, no chao onde o pet estava quando ela subiu (cocos.ts; o item gerado);
   todos com a sombra redonda. As posicoes do motor sao em subunidades; aqui, em celulas. Os tamanhos e as cores sao do desenho:
   PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import type { Mundo } from "../../../../motor/index.ts";
import { ninhoDe } from "../vistaMundo.ts";
import { CENA } from "../cenaEstado.ts";
import { BOLA_SALTO, BOLA_TAU_MS, COCO, KIT_DESDE_NINHO, LUZ_NINHO, SACO_AMASSO, SACO_BALANCO, SACO_DESDE_NINHO, SACO_FOLGA_POSTE, SACO_GIRO } from "./constantes.ts";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { GEO_SOMBRA, carregarVariante, curvar, materialSombra, toon, type Variante } from "./cena.ts";
import { Cocos } from "./cocos.ts";
import { ITENS_MODELOS } from "./modelos.ts";

const COR_RACAO = { madura: [0x9b6a3c, 0xc08a55], podre: [0x6b6b3a, 0x85854a] } as const;
/** a cor de cada fruta do motor (os tipos de motor/mundo.ts, FRUTAS) */
const COR_FRUTA: Readonly<Record<string, number>> = { a: 0xe8533f, b: 0xf2b134, c: 0x8a5bd6 };
const R_BOLA = 0.36;
const CIMA = new THREE.Vector3(0, 1, 0);

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
/** a bola: o item gerado (docs/TAREFA_V3_ITENS_3D.md; public/itens/bola/), que entra depois por `carregarBola`. A `esfera` e o pivo no
    centro da bola, que gira ao rolar; as malhas do glTF entram nela descidas de meia altura (o carregador poe a base em y = 0) */
function bola(): { g: THREE.Group; esfera: THREE.Group } {
  const esfera = new THREE.Group();
  esfera.position.y = R_BOLA;
  const g = new THREE.Group();
  g.add(sombra(ITENS_MODELOS.bola.sombra), esfera);
  return { g, esfera };
}
/** poe as malhas do glTF da bola na `esfera`; falha alto se o arquivo nao carrega (a ilha cai na reserva, como sem os kits) */
async function carregarBola(esfera: THREE.Group, base: string): Promise<void> {
  const m = ITENS_MODELOS.bola;
  if (m.altura !== 2 * R_BOLA) throw new Error(`a altura da bola na tabela (${m.altura}) nao e o diametro da vista (${2 * R_BOLA})`);
  const v = await carregarVariante(new GLTFLoader(), new URL("itens/" + m.arquivos[0], base).href, m);
  const desce = new THREE.Matrix4().makeTranslation(0, -R_BOLA, 0);
  for (const p of v.pecas) {
    const malha = new THREE.Mesh(p.geo, p.mat);
    malha.applyMatrix4(desce.clone().multiply(p.local));
    esfera.add(malha);
  }
}
/** onde o saco fica pendurado no grupo do saco (celulas, x e z): o mesmo ponto do saco procedural de antes, para o treino (vista.ts) nao
    mudar; o poste fica do lado -x */
const SACO_PENDURADO: readonly [number, number] = [0.1, 0];
/** o saco de pancada: o item gerado (docs/TAREFA_V3_ITENS_3D.md; public/itens/saco/), que entra depois por `carregarSaco`, em duas pecas
    pelo nome do no do glTF: o `suporte` (a base, o poste e o braco), parado, e o `saco` (a corrente e o saco), no `pivo`, o alto da
    corrente, que balanca e gira; o `corpo` e o saco que amassa no golpe, em volta do centro dele (`meio`, a altura abaixo do pivo) */
interface Saco { g: THREE.Group; suporte: THREE.Group; pivo: THREE.Group; corpo: THREE.Group; meio: number }
function saco(): Saco {
  const g = new THREE.Group(), suporte = new THREE.Group(), pivo = new THREE.Group(), corpo = new THREE.Group();
  corpo.matrixAutoUpdate = false;
  pivo.add(corpo);
  g.add(sombra(ITENS_MODELOS.saco.sombra), suporte, pivo);
  return { g, suporte, pivo, corpo, meio: 0 };
}
/** poe as duas pecas do glTF do saco no lugar; falha alto se o arquivo nao carrega ou nao tem exatamente o `suporte` e o `saco` */
async function carregarSaco(s: Saco, base: string): Promise<void> {
  const m = ITENS_MODELOS.saco;
  const v = await carregarVariante(new GLTFLoader(), new URL("itens/" + m.arquivos[0], base).href, m);
  if (v.pecas.length !== 2) throw new Error("o saco devia ter duas pecas: " + v.pecas.length);
  const peca = (nome: string) => {
    const ps = v.pecas.filter(p => p.nome === nome);
    if (ps.length !== 1) throw new Error(`o saco devia ter uma peca "${nome}": ${ps.length}`);
    return ps[0];
  };
  const sup = peca("suporte"), sac = peca("saco");
  if (!sac.geo.boundingBox) sac.geo.computeBoundingBox();
  const caixa = sac.geo.boundingBox!.clone().applyMatrix4(sac.local);
  /* o pivo: o alto da corrente, no meio do saco em x e z, levado para SACO_PENDURADO */
  const topo = new THREE.Vector3((caixa.min.x + caixa.max.x) / 2, caixa.max.y, (caixa.min.z + caixa.max.z) / 2);
  const ms = new THREE.Mesh(sup.geo, sup.mat);
  ms.applyMatrix4(new THREE.Matrix4().makeTranslation(SACO_PENDURADO[0] - topo.x, 0, SACO_PENDURADO[1] - topo.z).multiply(sup.local));
  s.suporte.add(ms);
  s.pivo.position.set(SACO_PENDURADO[0], topo.y, SACO_PENDURADO[1]);
  const mc = new THREE.Mesh(sac.geo, sac.mat);
  mc.applyMatrix4(new THREE.Matrix4().makeTranslation(-topo.x, -topo.y, -topo.z).multiply(sac.local));
  s.corpo.add(mc);
  s.meio = (caixa.min.y + caixa.max.y) / 2 - topo.y;
}
/** o kit medico: o item gerado (docs/TAREFA_V3_ITENS_3D.md; public/itens/kit/), um caixote de madeira com a tampa branca e a cruz, que
    entra depois por `carregarSimples` no `corpo` */
function kit(): { g: THREE.Group; corpo: THREE.Group } {
  const g = new THREE.Group(), corpo = new THREE.Group();
  g.add(sombra(ITENS_MODELOS.kit.sombra), corpo);
  return { g, corpo };
}
/** as pecas de um item gerado de uma peca so (o kit e o coco), normalizadas pela altura da tabela, com a base em y = 0 */
async function pecasDe(nome: "kit" | "coco", base: string): Promise<Variante["pecas"]> {
  const m = ITENS_MODELOS[nome];
  return (await carregarVariante(new GLTFLoader(), new URL("itens/" + m.arquivos[0], base).href, m)).pecas;
}
/** poe as pecas no grupo, cada uma como uma malha (a geometria e o material sao os mesmos em todos os grupos) */
function porPecas(g: THREE.Group, pecas: Variante["pecas"]): void {
  for (const p of pecas) {
    const m = new THREE.Mesh(p.geo, p.mat);
    m.applyMatrix4(p.local);
    g.add(m);
  }
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

/* o coco (cocos.ts): o item gerado (docs/TAREFA_V3_ITENS_3D.md; public/itens/coco/), o mesmo glTF para todos os cocos. Os cocos
   podem cair antes de o glTF chegar (um save com sujeira): o corpo deles fica vazio ate la e e preenchido quando ele chega */
let pecasCoco: Variante["pecas"] | null = null;
const cocosSemCorpo: THREE.Group[] = [];

/** um coco: o corpo (o glTF), girado para os cocos seguidos nao ficarem iguais, e a sombra redonda */
function coco(i: number): THREE.Group {
  const g = new THREE.Group(), corpo = new THREE.Group();
  corpo.rotation.y = i * 1.9;
  if (pecasCoco) porPecas(corpo, pecasCoco); else cocosSemCorpo.push(corpo);
  const s = new THREE.Mesh(GEO_SOMBRA, materialSombra());
  s.scale.set(ITENS_MODELOS.coco.sombra * 2, 1, ITENS_MODELOS.coco.sombra * 2);
  s.position.y = 0.02;
  s.renderOrder = 1;
  g.add(s, corpo);
  return g;
}
/** carrega o coco e preenche os que ja cairam */
async function carregarCoco(base: string): Promise<void> {
  pecasCoco = await pecasDe("coco", base);
  for (const corpo of cocosSemCorpo.splice(0)) porPecas(corpo, pecasCoco);
}

export class Itens {
  readonly raiz = new THREE.Group();
  private readonly comidas = new Map<number, { g: THREE.Group; podre: boolean | null }>();
  private readonly bola = bola();
  private readonly brilho = brilho();
  private readonly saco = saco();
  private readonly kit = kit();
  readonly cocos = new Cocos(coco);
  private readonly sub: number;
  /** onde a bola esta desenhada (celulas), indo ate a do motor sem pular; null antes do primeiro quadro */
  private bolaCel: [number, number] | null = null;
  /** a bola estava na mao do dono no quadro anterior: ao cair, ela aparece onde caiu (sem rolar do lugar antigo) */
  private naMaoAntes = false;
  private readonly giro = new THREE.Quaternion();
  /** o ultimo golpe no saco: quando (ms da vista), o eixo do balanco no chao (o saco vai para longe de quem bateu), o angulo da direcao
      do golpe no chao (o amassado) e o sentido do giro na corrente (+1 ou -1) */
  private golpeSaco: { em: number; eixo: THREE.Vector3; angulo: number; lado: number } | null = null;
  private readonly giroSaco = new THREE.Quaternion();
  private readonly amasso = { m: new THREE.Matrix4(), r: new THREE.Matrix4() };
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
    this.kit.g.position.set(nx / sub + KIT_DESDE_NINHO[0], 0, ny / sub + KIT_DESDE_NINHO[1]);
    this.kit.g.rotation.y = -0.4;
    this.kit.g.visible = false;
    this.raiz.add(n, t, this.bola.g, this.brilho, this.saco.g, this.kit.g, this.cocos.raiz);
  }

  /** os itens gerados (public/itens/): a bola, o saco, o kit e o coco; `base` e a URL da pagina */
  async carregar(base: string): Promise<void> {
    await Promise.all([carregarBola(this.bola.esfera, base), carregarSaco(this.saco, base),
      pecasDe("kit", base).then(ps => porPecas(this.kit.corpo, ps)), carregarCoco(base)]);
  }

  /** onde a bola esta desenhada (subunidades do mapa), para pegar a bola na cena (PorBola.tsx); null antes do primeiro quadro */
  get bolaDesenhada(): [number, number] | null { return this.bolaCel && [this.bolaCel[0] * this.sub, this.bolaCel[1] * this.sub]; }

  /** um golpe no saco de quem esta em `de` (celulas): o saco balanca para longe dele, no plano vertical que passa pelos dois. O eixo e
      d x cima (d, a direcao de quem bateu ate o saco): o angulo positivo leva a ponta do saco no sentido de d. O saco tambem amassa na
      direcao d e gira na corrente: o braco vai do poste (-x) ao saco (+x), e quem bate de um lado do braco (z < saco) o gira num
      sentido, do outro lado no outro */
  baterNoSaco(agora: number, de: readonly [number, number]): void {
    const dx = this.sacoEm[0] - de[0], dz = this.sacoEm[1] - de[1], d = Math.hypot(dx, dz) || 1;
    this.golpeSaco = { em: agora, eixo: new THREE.Vector3(-dz / d, 0, dx / d), angulo: Math.atan2(-dz, dx), lado: dz >= 0 ? 1 : -1 };
  }

  /** a racao e a fruta entram e saem e a podre muda de cor; a bola vai aonde o motor diz, girando; o saco balanca; o kit so com a lesao;
      a luz do ninho so a noite; os cocos da `sujeira`, caindo perto do pet (`pet`, celulas) */
  sincronizar(mu: Mundo, tick: number, noite: boolean, agora: number, dtMs: number, lesionado: boolean, reduzido: boolean, sujeira: number,
    pet: readonly [number, number]): void {
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
    this.kit.g.visible = lesionado;
    this.brilho.visible = noite;
    this.cocos.sincronizar(sujeira, pet, agora, reduzido);
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

  /** o saco reage ao golpe e amortece: balanca para longe de quem bateu (SACO_BALANCO), gira um pouco na corrente (SACO_GIRO) e amassa
      na direcao do golpe, achatando nela e alargando nas outras, como lona cheia (SACO_AMASSO); com movimento reduzido, fica parado */
  private balancarSaco(agora: number, reduzido: boolean): void {
    const g = this.golpeSaco, t = g && !reduzido ? agora - g.em : Infinity;
    const onda = (o: { amplitude: number; tau: number; periodo: number }, f: (x: number) => number) =>
      t > 6 * o.tau ? 0 : o.amplitude * Math.exp(-t / o.tau) * f((2 * Math.PI * t) / o.periodo);
    const b = onda(SACO_GIRO, Math.sin), k = onda(SACO_AMASSO, Math.cos);
    /* o balanco para o lado do poste (-x) para em SACO_FOLGA_POSTE: o fundo do saco anda d * a, e o poste esta a uma folga curta */
    let a = onda(SACO_BALANCO, Math.sin);
    const ax = g ? a * g.eixo.z : 0;
    if (g && ax < -SACO_FOLGA_POSTE) a = -SACO_FOLGA_POSTE / g.eixo.z;
    const p = this.saco.pivo, c = this.saco.corpo, am = this.amasso;
    if (!g) { p.quaternion.identity(); c.matrix.identity(); return; }
    p.quaternion.setFromAxisAngle(g.eixo, a).multiply(this.giroSaco.setFromAxisAngle(CIMA, g.lado * b));
    /* o amassado: T(meio) Ry(th) S(1-k, 1+k/2, 1+k/2) Ry(-th) T(-meio), com th a direcao do golpe no quadro do pivo (sem o giro) */
    const th = g.angulo - g.lado * b, meio = this.saco.meio;
    am.m.makeTranslation(0, meio, 0).multiply(am.r.makeRotationY(th)).multiply(am.r.makeScale(1 - k, 1 + k / 2, 1 + k / 2))
      .multiply(am.r.makeRotationY(-th)).multiply(am.r.makeTranslation(0, -meio, 0));
    c.matrix.copy(am.m);
    c.matrixWorldNeedsUpdate = true;
  }
}
