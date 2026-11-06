/* A vista da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, H2): o modo mundo dos pets v12 numa ilha 3D no estilo Animal Crossing. So vista:
   le o Motor.mundo (jogoAtual), nunca escreve nele; a camera, a interpolacao, o vento e as animacoes ficam fora do log.
   - a ilha sai da grade (grade.ts) do layout do motor; a cena (cena.ts) a desenha, com o mundo curvo centrado no pet;
   - a camera em perspectiva segue a posicao desenhada do pet (o Seguidor de vistaMundo.ts) a uma distancia fixa (H-3); em retrato ela
     se afasta ate caber LARGURA_MIN celulas de lado a lado (constantes.ts);
   - o contrato CENA (cenaEstado.ts) fica igual: ret (o retangulo do pet em px de CSS, para o PalcoPet), medir (a M3), e mundo.paraMundo,
     paraTela e pet, que passam pela mesma dobra do shader (curva.ts, regra 6);
   - o dia e a noite do motor (eNoite) escurecem o ceu, a nevoa, a luz e a agua;
   - a camera solta (cameraLivre.ts, L1 de "Lugares da ilha"): a partir de 900 px e com o controle "Livre", a camera olha um ponto que
     pode sair do pet (o foco); a dobra e a camera centram nele, e a vista publica a cada quadro o que o minimapa e a HUD leem;
   - a viagem ao lugar (viagem.ts, L2 de "Lugares da ilha"): com Crescer aberto, a camera vai ao saco de pancada (deixando-o a esquerda do painel, no
     celular no alto, acima da folha) e o pet desenhado anda ate ele e fica; ao sair, os dois voltam. So o desenho, como a coreografia abaixo;
   - a coreografia (docs/TAREFA_V3_HABITAT_OBJETOS.md): pedido um treino (CENA.treino), o pet desenhado vai ao saco de pancada, bate e
     volta (TREINO_MS); quando o motor rola a bola (uma rolagem nova no Mundo), o pet da um golpe nela. So o desenho: a posicao do motor,
     o ganho do treino e o log nao mudam.
   Os kits carregam depois do terreno; se um modelo nao carrega, a cena cai na reserva (MundoReserva), com o erro no console. */
import * as THREE from "three";
import { TPD, eNoite, type Mundo } from "../../../../motor/index.ts";
import { habitatAtual, voltarParaIlha, type Habitat } from "../../../habitat.ts";
import { jogoAtual } from "../../../jogo.ts";
import { CENA, reservaDoPe } from "../cenaEstado.ts";
import { Seguidor, dentroDoMapa } from "../vistaMundo.ts";
import { velocidadeAtual } from "../../../tempo.ts";
import { AFASTAR_MAX, BATER_BOLA_MS, CAMERAS, COBERTO_MS, GOLPE_DIST, GOLPE_MS, KITS_COBERTO_MS, FPS_MIN, LARGURA_MIN, LONGE, NEVOA, PERTO, QUEDA_MS,
  RAZAO_MAX, TEXEL_ALVO, TREINO_MS, type CameraHabitat } from "./constantes.ts";
import { CURVA, type CenaIlha, type Objetos } from "./cena.ts";
import { estiloDe, type Estilo } from "./estilos.ts";
import { dobrarY, paraMundoCel, paraTelaNdc, type CameraLida, type Dobra } from "./curva.ts";
import { ilhaDe, type Ilha } from "./grade.ts";
import { Itens } from "./itens.ts";
import { Papel, type Ret } from "./papel.ts";
import { ORBITA, aplicarOrbita, ligarControles, recentrar } from "../orbita.ts";
import { CONSULTA_SOLTA, VISTA, despublicarVista, focoDoQuadro, ligarCameraLivre, publicarVista, type Limites, type MapaDaIlha } from "../cameraLivre.ts";
import { pixelsDoMapa } from "./minimapa.ts";
import { PRESETS, Pos } from "./pos.ts";
import { SACO_NA_TELA, ZOOM_LUGAR_MOVEL, lugarAberto, progressoViagem } from "../../../viagem.ts";

const movimentoReduzido = (): boolean => matchMedia("(prefers-reduced-motion: reduce)").matches;

class VistaIlha {
  readonly renderer: THREE.WebGLRenderer;
  readonly camera: THREE.PerspectiveCamera;
  private readonly ilha: Ilha;
  private readonly cenaIlha: CenaIlha;
  private readonly seguidor = new Seguidor();
  private readonly raio = new THREE.Raycaster();
  private readonly lida: CameraLida;
  private readonly papel = new Papel();
  private readonly itens: Itens;
  private objetos: Objetos | null = null;
  /** a qualidade caiu (regra 10): sem vento, metade da grama e pixelRatio 1 */
  private baixa = false;
  private ppu = 1;              // pixels do canvas por unidade do mundo na distancia do pet
  private pxPorTexel = 1;       // pixels do canvas por texel do sprite (inteiro, regra 8)
  private larguraCss = 1;
  private alturaCss = 1;
  /** a fracao da altura do canvas em que a camera enquadra a cena (1 de 900 px em diante; no celular, a altura menos o pe reservado, reservaDoPe) */
  private fracEnq = 1;
  private afast = 1;
  /** o afastamento do retrato sem o zoom do lugar (ajustar); `afast` e ele vezes o zoom da viagem (so abaixo de 900 px) */
  private afastBase = 1;
  /** a largura de 900 px em diante (lida em ajustar, nao a cada quadro) */
  private largo = true;
  private noite: boolean | null = null;
  private ultimo = performance.now();
  private petCel: [number, number] = [0, 0];
  /** o ponto que a camera olha (celulas): o pet, ou outro com a camera solta (cameraLivre.ts) */
  private foco: [number, number] = [0, 0];
  private readonly dirCam = new THREE.Vector3();
  /** a ilha vista de cima e os limites do foco, para o minimapa (feitos uma vez) */
  private readonly mapa: MapaDaIlha;
  private readonly limites: Limites;
  private readonly consultaSolta = typeof matchMedia === "function" ? matchMedia(CONSULTA_SOLTA) : null;
  /** o treino na ilha: o pedido (CENA.treino) que esta tocando, quando comecou, o ponto em que o pet para para bater (ao lado do saco
      na tela) e o ultimo golpe que balancou o saco */
  private treino: { pedido: number; desde: number; ponto: [number, number]; golpe: number } | null = null;
  private treinoVisto: number | null = CENA.treino;
  /** a batida na bola: quantas rolagens o motor ja tinha (null antes do primeiro quadro: as de antes de abrir a ilha nao contam) */
  private rolagens: number | null = null;
  private bateBola: { desde: number; alvo: [number, number] } | null = null;

  readonly canvas: HTMLCanvasElement;
  private readonly mu: Mundo;
  /** o estilo do mapa (estilos.ts) e a camera (constantes.ts, CAMERAS) do habitat escolhido */
  readonly estilo: Estilo;
  private readonly cam: CameraHabitat;
  /** o visual (GBA HD, HD-2D): lido a cada quadro de habitatAtual, sem religar a cena */
  private readonly pos: Pos;

  constructor(canvas: HTMLCanvasElement, mu: Mundo, habitat: Habitat) {
    this.canvas = canvas; this.mu = mu;
    this.estilo = estiloDe(habitat.mapa, document.baseURI);
    this.cam = CAMERAS[habitat.camera];
    this.camera = new THREE.PerspectiveCamera(this.cam.fov, 1, PERTO, LONGE);
    CURVA.uCurva.value = this.estilo.dobra;
    THREE.ColorManagement.enabled = true;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    /* com o visual, um quadro sao dois desenhos (a cena no alvo e o quadro na tela): a contagem de draw calls da M3 e zerada por quadro */
    this.renderer.info.autoReset = false;
    this.pos = new Pos(this.renderer);
    this.ilha = ilhaDe(mu.cm);
    this.cenaIlha = this.estilo.montar(this.ilha);
    const v = new THREE.Vector3();
    this.lida = {
      projetar: (x, y, z) => { v.set(x, y, z).project(this.camera); return [v.x, v.y]; },
      raio: (nx, ny) => {
        this.raio.setFromCamera(new THREE.Vector2(nx, ny), this.camera);
        const { origin: o, direction: d } = this.raio.ray;
        return { o: [o.x, o.y, o.z], d: [d.x, d.y, d.z] };
      },
    };
    /* o ninho, o comedouro, a racao, a fruta e a bola (itens.ts) e o pet em papel */
    this.itens = new Itens(mu);
    this.cenaIlha.cena.add(this.itens.raiz, this.papel.raiz);
    CURVA.uVento.value = 1;
    const il = this.ilha;
    this.mapa = { imagem: new ImageData(pixelsDoMapa(il, this.estilo.paleta), il.larg, il.prof), x0: il.x0, z0: il.z0, larg: il.larg, prof: il.prof, area: il.area };
    this.limites = { x0: il.x0, z0: il.z0, x1: il.x0 + il.larg, z1: il.z0 + il.prof };
  }

  /** a camera pode soltar agora: o controle "Livre" e a largura do desktop */
  get podeSoltar(): boolean { return habitatAtual().controle === "livre" && !!this.consultaSolta?.matches; }

  /** os modelos do estilo (na ilha, os kits de public/kits3d) entram depois do terreno */
  async carregarObjetos(): Promise<void> {
    THREE.ColorManagement.enabled = true;
    const o = await this.estilo.objetos(this.ilha);
    this.objetos = o;
    this.cenaIlha.cena.add(o.grupo);
    if (this.baixa) this.menosGrama();
  }

  /** a dobra de agora: centrada no ponto olhado (o pet desenhado, ou o foco da camera solta), ao longo da direcao em que a camera olha no chao */
  private get dobra(): Dobra { return { k: this.estilo.dobra, focoX: this.foco[0], focoZ: this.foco[1], dir: this.dirDobra }; }
  /** a camera com a orbita (orbita.ts): o deslocamento e o ponto olhado em relacao ao pet; a fixa e a do habitat */
  private orbitaVista = { desloc: [0, 0, 0] as [number, number, number], olhar: [0, 0, 0] as [number, number, number], elevacao0: 0 };
  private orbitaVersao = -1;
  private dirDobra: [number, number] = [0, 1];
  /** a elevacao da camera do habitat (para o limite da inclinacao) */
  get elevacao0(): number { return this.orbitaVista.elevacao0; }
  /** a orbita mudou (ou o controle): o deslocamento, a direcao da dobra, a nevoa e o tamanho do texel na distancia nova */
  private atualizarOrbita(): void {
    const livre = habitatAtual().controle === "livre";
    if (!livre && (ORBITA.giro || ORBITA.inclina || ORBITA.zoom !== 1)) recentrar();
    if (this.orbitaVersao === ORBITA.versao) return;
    this.orbitaVersao = ORBITA.versao;
    this.orbitaVista = aplicarOrbita(this.cam.desloc, this.cam.olhar);
    const [dx, , dz] = this.orbitaVista.desloc, h = Math.hypot(dx, dz);
    this.dirDobra = h > 1e-9 ? [-dx / h, -dz / h] : [0, 1];
    const nevoa = this.cenaIlha.cena.fog as THREE.Fog;
    nevoa.near = NEVOA[0] * this.afast * ORBITA.zoom; nevoa.far = NEVOA[1] * this.afast * ORBITA.zoom;
    /* o pet em papel: na distancia do foco, um texel do sprite vale um numero inteiro de pixels do canvas (regra 8) */
    this.ppu = this.renderer.domElement.height * this.fracEnq / 2 / (this.profundidadeDoPet(this.afast, this.orbitaVista) * Math.tan(THREE.MathUtils.degToRad(this.cam.fov / 2)));
    this.pxPorTexel = Math.max(1, Math.round(TEXEL_ALVO * this.ppu));
  }

  /** ajusta o canvas a caixa (px de CSS): a resolucao, a proporcao e o afastamento da camera em retrato */
  ajustar(larguraCss: number, alturaCss: number): void {
    this.larguraCss = Math.max(1, larguraCss); this.alturaCss = Math.max(1, alturaCss);
    this.largo = typeof matchMedia === "function" && matchMedia("(min-width: 900px)").matches;
    this.renderer.setPixelRatio(this.baixa ? 1 : Math.min(RAZAO_MAX, devicePixelRatio || 1));
    this.renderer.setSize(this.larguraCss, this.alturaCss, false);
    this.canvas.style.width = `${this.larguraCss}px`; this.canvas.style.height = `${this.alturaCss}px`;
    /* o enquadramento como se a caixa tivesse a altura de antes (a de hoje menos o pe que o dock e a barra reservavam): a camera enquadra essa altura e o
       quadro se estende para baixo (setViewOffset), entao o pet sai do mesmo tamanho em px e a cena segue visivel atras das acoes (so abaixo de 900 px) */
    const enq = Math.max(1, this.alturaCss - reservaDoPe());
    this.fracEnq = enq / this.alturaCss;
    this.camera.aspect = this.larguraCss / enq;
    if (enq < this.alturaCss) this.camera.setViewOffset(this.larguraCss, enq, 0, 0, this.larguraCss, this.alturaCss); else this.camera.clearViewOffset();
    /* a largura vista na altura do pet, com a camera do POC; em retrato, a camera se afasta ate caber LARGURA_MIN */
    /* o afastamento do retrato e o da camera do habitat (sem a orbita: o zoom nao se desfaz aqui) */
    const fundo = this.profundidadeDoPet(1, this.cam), larg = 2 * fundo * Math.tan(THREE.MathUtils.degToRad(this.cam.fov / 2)) * this.camera.aspect;
    this.afastBase = Math.min(AFASTAR_MAX, Math.max(1, LARGURA_MIN / larg));
    this.afast = this.afastBase;
    this.camera.updateProjectionMatrix();
    /* a nevoa e o texel dependem tambem da orbita */
    this.orbitaVersao = -1;
    this.atualizarOrbita();
  }
  /** a distancia do pet ao plano da camera (ao longo do eixo dela), com o afastamento `a`, para um deslocamento e um ponto olhado */
  private profundidadeDoPet(a: number, c: { desloc: readonly [number, number, number]; olhar: readonly [number, number, number] }): number {
    const d = new THREE.Vector3(...c.olhar).sub(new THREE.Vector3(...c.desloc)).normalize();
    return new THREE.Vector3(...c.desloc).multiplyScalar(-a).dot(d);
  }

  /** o modo mundo: o ponto do cliente (px) no chao dobrado, em subunidades inteiras do mapa (null fora do mapa ou fora do chao) */
  paraMundo(cx: number, cy: number): [number, number] | null {
    const r = this.canvas.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return null;
    /* fora da cena nada e chao: o raio de um ponto abaixo do canvas ainda tocaria a ilha perto da camera */
    if (cx < r.left || cx > r.right || cy < r.top || cy > r.bottom) return null;
    const p = paraMundoCel(this.lida, this.dobra, ((cx - r.left) / r.width) * 2 - 1, 1 - ((cy - r.top) / r.height) * 2);
    if (!p) return null;
    const sub = this.mu.cm.sub, x = Math.round(p[0] * sub), y = Math.round(p[1] * sub);
    return dentroDoMapa(this.mu.cm, x, y) ? [x, y] : null;
  }
  /** o modo mundo: o ponto do mapa (subunidades) no cliente (px), pela mesma dobra */
  paraTela(x: number, y: number): [number, number] {
    const r = this.canvas.getBoundingClientRect(), sub = this.mu.cm.sub, [nx, ny] = paraTelaNdc(this.lida, this.dobra, x / sub, y / sub);
    return [r.left + ((nx + 1) / 2) * r.width, r.top + ((1 - ny) / 2) * r.height];
  }
  /** onde o pet esta desenhado (subunidades) */
  get petDesenhado(): [number, number] | null { return this.seguidor.pos; }
  /** onde a bola esta desenhada (subunidades) */
  get bolaDesenhada(): [number, number] | null { return this.itens.bolaDesenhada; }

  /** a coreografia sobre a posicao do motor (`motorCel`, celulas): o treino no saco e a batida na bola. Devolve onde desenhar o pet, o
      golpe e se a vista o esta movendo */
  private coreografia(mu: Mundo, agora: number, motorCel0: [number, number], reduzido: boolean, viagem: number)
      : { cel: [number, number]; golpe: { desde: number; alvo: [number, number] } | null; andando: boolean } {
    /* a batida na bola: uma rolagem nova; o pet olha para onde a bola vai (parada, para onde ela esta) */
    const n = mu.rolagens.length, sub = mu.cm.sub;
    if (this.rolagens !== null && n > this.rolagens) {
      const r = mu.rolagens[n - 1] as { de: [number, number]; para: [number, number] }, parou = r.para[0] === r.de[0] && r.para[1] === r.de[1];
      this.bateBola = { desde: agora, alvo: parou ? [r.de[0] / sub, r.de[1] / sub] : [r.para[0] / sub, r.para[1] / sub] };
    }
    this.rolagens = n;
    if (this.bateBola && agora - this.bateBola.desde >= BATER_BOLA_MS) this.bateBola = null;
    /* o treino: um pedido novo comeca do lugar em que o pet esta; ele para a GOLPE_DIST do saco, ao lado dele na tela (ao longo da
       direita da camera no chao, que gira com a camera livre), do lado em que o pet ja esta: nem na frente do saco, nem atras */
    const [sx, sz] = this.itens.sacoEm;
    /* a viagem ao lugar: o pet anda do que o motor diz ate o lado esquerdo do saco na tela (o painel abre a direita) e fica; o treino parte
       dai e volta para ca. `motorCel` e, daqui para baixo, onde o pet estaria sem o treino */
    const motorCel: [number, number] = viagem > 0 ? this.entre(motorCel0, this.pontoDoLugar(), reduzido ? 1 : this.suave(viagem)) : motorCel0;
    const emViagem = viagem > 0 && viagem < 1 && !reduzido;
    if (CENA.treino !== null && CENA.treino !== this.treinoVisto) {
      this.treinoVisto = CENA.treino;
      const dir = new THREE.Vector3(1, 0, 0).applyQuaternion(this.camera.quaternion), h = Math.hypot(dir.x, dir.z) || 1;
      const [rx, rz] = [dir.x / h, dir.z / h], lado = viagem > 0 ? -1 : (motorCel[0] - sx) * rx + (motorCel[1] - sz) * rz >= 0 ? 1 : -1;
      this.treino = { pedido: CENA.treino, desde: agora, ponto: [sx + lado * rx * GOLPE_DIST, sz + lado * rz * GOLPE_DIST], golpe: -1 };
    }
    const t = this.treino;
    const caminhando = viagem <= 0 && this.seguidor.caminhando;
    if (!t) return { cel: motorCel, golpe: this.bateBola, andando: emViagem || caminhando };
    const dt = agora - t.desde, { ida, golpes, volta } = TREINO_MS, ponto = t.ponto;
    const suave = (f: number) => (reduzido ? 1 : this.suave(f)), entre = (a: [number, number], b: [number, number], f: number) => this.entre(a, b, f);
    if (dt < ida) return { cel: entre(motorCel, ponto, suave(dt / ida)), golpe: null, andando: !reduzido };
    if (dt < ida + golpes) {
      const k = Math.floor((dt - ida) / GOLPE_MS), desde = t.desde + ida + k * GOLPE_MS;
      /* o saco balanca no meio do golpe, quando o braco chega */
      if (k !== t.golpe && agora - desde >= GOLPE_MS * 0.3) { t.golpe = k; this.itens.baterNoSaco(agora, ponto); }
      return { cel: ponto, golpe: { desde, alvo: [sx, sz] }, andando: false };
    }
    if (dt < ida + golpes + volta) return { cel: entre(ponto, motorCel, suave((dt - ida - golpes) / volta)), golpe: null, andando: !reduzido };
    this.treino = null;
    return { cel: motorCel, golpe: this.bateBola, andando: emViagem || caminhando };
  }

  private suave(f: number): number { return f * f * (3 - 2 * f); }
  private entre(a: [number, number], b: [number, number], f: number): [number, number] { return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]; }
  /** a direita da camera no chao (unitaria): a direita da direcao em que ela olha */
  private get direita(): [number, number] { return [-this.dirDobra[1], this.dirDobra[0]]; }
  /** onde o pet fica no lugar: a GOLPE_DIST do saco, a esquerda dele na tela (o painel abre a direita) */
  private pontoDoLugar(): [number, number] {
    const [sx, sz] = this.itens.sacoEm, [rx, rz] = this.direita;
    return [sx - rx * GOLPE_DIST, sz - rz * GOLPE_DIST];
  }
  /** o ponto olhado com a viagem: do que a camera olharia sem ela ate o saco, deslocado para o saco ficar onde o painel deixa (a esquerda dele
      de 900 px em diante; no alto, acima da folha, abaixo). `p` e o progresso (0 a 1) */
  private focoDaViagem(base: [number, number], p: number, reduzido: boolean): [number, number] {
    const [sx, sz] = this.itens.sacoEm, [rx, rz] = this.direita, [fx, fz] = this.dirDobra;
    const ppc = Math.max(1e-6, this.ppu / this.renderer.getPixelRatio());      // px de CSS por celula na distancia do ponto olhado
    let ax = sx, az = sz;
    if (this.largo) {
      /* o saco a esquerda do centro: o foco fica a direita dele */
      const k = (0.5 - SACO_NA_TELA.largo) * this.larguraCss / ppc;
      ax += rx * k; az += rz * k;
    } else {
      /* o saco acima do centro do quadro da camera: o foco fica antes dele, no chao (a distancia na tela encurta pelo seno da elevacao) */
      const seno = Math.max(0.2, Math.abs(this.orbitaVista.desloc[1]) / (Math.hypot(...this.orbitaVista.desloc) || 1));
      const k = (this.alturaCss * this.fracEnq / 2 - SACO_NA_TELA.movel * this.alturaCss) / ppc / seno;
      ax -= fx * k; az -= fz * k;
    }
    const s = reduzido ? 1 : this.suave(p);
    return this.entre(base, [ax, az], s);
  }

  /** um quadro: o pet onde o motor diz (interpolado), a camera atras dele, a racao e a bola, o dia ou a noite; devolve o retangulo do pet */
  desenhar(agora: number, quadro: number): Ret {
    /* o ColorManagement do three e um global que as outras vistas (a sala e o mapa da Exploracao) desligam: sem repor aqui, a cor da nevoa
       e das luzes dependia de qual import dinamico subia por ultimo */
    THREE.ColorManagement.enabled = true;
    CURVA.uCurva.value = this.estilo.dobra;
    const { motor: m } = jogoAtual(), mu = m.mundo ?? this.mu, cm = mu.cm, sub = cm.sub;
    const dtMs = agora - this.ultimo, reduzido = movimentoReduzido(), jg = jogoAtual();
    const pos = this.seguidor.seguir(mu.pet, dtMs, cm, { velJogo: velocidadeAtual(), acao: m.acao, dorme: jg.nascendo > 0 || m.acao === "dormir", reduzido });
    this.ultimo = agora;
    const viagem = progressoViagem(agora);
    const cor = this.coreografia(mu, agora, [pos[0] / sub, pos[1] / sub], reduzido, viagem);
    this.petCel = cor.cel;
    /* o zoom do lugar: abaixo de 900 px a camera se aproxima do saco com a viagem (o saco e o pet ficam grandes no terco de cima) e volta ao sair */
    const zoom = viagem > 0 && !this.largo
      ? 1 - (1 - ZOOM_LUGAR_MOVEL) * (reduzido ? 1 : this.suave(viagem)) : 1;
    if (this.afastBase * zoom !== this.afast) { this.afast = this.afastBase * zoom; this.orbitaVersao = -1; }
    this.atualizarOrbita();
    const pode = this.podeSoltar;
    this.foco = focoDoQuadro(this.petCel, agora, dtMs, this.dirDobra, this.limites, pode);
    if (viagem > 0) this.foco = this.focoDaViagem(this.foco, viagem, reduzido);
    const [px, pz] = this.foco, a = this.afast;
    const { desloc, olhar } = this.orbitaVista;
    this.camera.position.set(px + desloc[0] * a, desloc[1] * a, pz + desloc[2] * a);
    this.camera.lookAt(px + olhar[0] * a, olhar[1] * a, pz + olhar[2] * a);
    this.camera.updateMatrixWorld();
    CURVA.uFocoX.value = px; CURVA.uFocoZ.value = pz;
    CURVA.uDirX.value = this.dirDobra[0]; CURVA.uDirZ.value = this.dirDobra[1];
    CURVA.uTempo.value = reduzido ? 0 : agora / 1000;
    const noite = eNoite(m.e.tick % TPD);
    if (noite !== this.noite) { this.noite = noite; this.cenaIlha.aplicarNoite(noite); }
    this.itens.sincronizar(mu, m.e.tick, noite, agora, dtMs, m.lesionadoDesde !== null, reduzido, m.e.sujeira, this.petCel);
    /* com a camera solta, o pet fica longe do foco: o chao sob ele desce pela dobra, e o tamanho do papel vale na distancia dele (senao o
       texel deixa de ser inteiro e o pet cresce ou encolhe com a distancia ao foco) */
    let ppu = this.ppu, pxPorTexel = this.pxPorTexel, yChao = 0;
    if (this.petCel[0] !== px || this.petCel[1] !== pz) {
      yChao = dobrarY(0, this.petCel[1], this.dobra, this.petCel[0]);
      const dir = this.camera.getWorldDirection(this.dirCam), prof = (this.petCel[0] - this.camera.position.x) * dir.x
        + (yChao - this.camera.position.y) * dir.y + (this.petCel[1] - this.camera.position.z) * dir.z;
      if (prof > 1e-3) {
        ppu = this.renderer.domElement.height / 2 / (prof * Math.tan(THREE.MathUtils.degToRad(this.cam.fov / 2)));
        pxPorTexel = Math.max(1, Math.round(TEXEL_ALVO * ppu));
      }
    }
    const ret = this.papel.atualizar({
      agora, dt: Math.min(0.05, dtMs / 1000), quadro, cel: this.petCel, motor: mu.pet, camera: this.camera,
      ppu, pxPorTexel, yChao, canvas: [this.renderer.domElement.width, this.renderer.domElement.height],
      razao: this.renderer.getPixelRatio(), reduzido, noite, golpe: cor.golpe, andandoVista: cor.andando,
    });
    /* o foco do HD-2D: a altura do pet na tela (0 embaixo, 1 em cima) */
    this.renderer.info.reset();
    this.pos.desenhar(this.cenaIlha.cena, this.camera, PRESETS[habitatAtual().visual], 1 - (ret.y + ret.h * 0.6) / this.alturaCss);
    this.publicar(mu, m.e.tick, ret, pode);
    return ret;
  }

  /** o que o minimapa e a HUD leem (cameraLivre.ts): o foco, o pet, a vista, os lugares, a comida, e se o pet saiu da tela e para que lado */
  private publicar(mu: Mundo, tick: number, ret: Ret, pode: boolean): void {
    /* abaixo de 900 px nada le o minimapa nem o resumo: sem alocar por quadro (o celular), e o que estava publicado sai uma vez */
    if (!this.consultaSolta?.matches) { if (VISTA.atual) despublicarVista(); return; }
    const [fx, fz] = this.dirDobra, [ox, oz] = this.foco, [px, pz] = this.petCel, sub = mu.cm.sub;
    const { desloc } = this.orbitaVista, a = this.afast;
    /* o pet atras da camera (no chao) ou com o desenho fora do canvas: fora da tela */
    const atras = (px - (ox + desloc[0] * a)) * fx + (pz - (oz + desloc[2] * a)) * fz < 0;
    const cx = ret.x + ret.w / 2, cy = ret.y + ret.h / 2;
    const fora = atras || cx < 0 || cx > this.larguraCss || cy < 0 || cy > this.alturaCss;
    /* o lado: o pet no plano da vista (a direita e a frente girada 90 graus) */
    const dx = px - ox, dz = pz - oz, lado = dx * -fz + dz * fx, frente = dx * fx + dz * fz;
    const meia = Math.atan(Math.tan(THREE.MathUtils.degToRad(this.cam.fov / 2)) * this.camera.aspect);
    publicarVista({
      foco: [ox, oz], pet: [px, pz], bola: this.itens.bolaCelula, frente: [fx, fz], meiaAbertura: meia,
      comidas: this.itens.comidasNoMapa(mu, tick), ninho: this.itens.ninhoEm, comedouro: [mu.comedouro[0] / sub, mu.comedouro[1] / sub], saco: this.itens.sacoEm,
      /* as arvores de fruta do motor (o layout MVP dos pets v13+ nao tem nenhuma; as arvores da ilha sao enfeite da vista) */
      arvores: mu.arvores.map(t => [t.x / sub, t.y / sub] as [number, number]),
      petFora: fora, lado: Math.abs(lado) >= Math.abs(frente) ? (lado > 0 ? "direita" : "esquerda") : (frente > 0 ? "cima" : "baixo"),
      pxPorCelula: this.ppu / this.renderer.getPixelRatio(), senoElevacao: Math.abs(desloc[1]) / (Math.hypot(desloc[0], desloc[1], desloc[2]) || 1),
      mapa: this.mapa, limites: this.limites,
      sacoTela: lugarAberto() ? this.paraTela(this.itens.sacoEm[0] * sub, this.itens.sacoEm[1] * sub) : undefined,
    }, true, pode);
  }

  dispose(): void { this.papel.dispose(); this.pos.dispose(); this.renderer.dispose(); }

  /** a queda de qualidade (regra 10, PROPOSTO): sem vento, metade da grama e pixelRatio 1; so uma vez */
  baixarQualidade(): void {
    if (this.baixa) return;
    this.baixa = true;
    CURVA.uVento.value = 0;
    this.menosGrama();
    console.info("ilha: a média ficou abaixo de", FPS_MIN, "fps; a qualidade caiu (sem vento, menos grama, pixelRatio 1)");
  }
  get qualidadeBaixa(): boolean { return this.baixa; }
  private menosGrama(): void { for (const g of this.objetos?.grama ?? []) g.count = Math.floor(g.count / 2); }
}

const mediana = (v: number[]): number => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const p95 = (v: number[]): number => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.min(s.length - 1, Math.floor(s.length * 0.95))] : 0; };

/** liga a ilha num canvas; devolve a funcao que desliga. Falha alto (a tela cai na reserva) se o WebGL nao subir ou um modelo faltar */
export function iniciarIlha(canvas: HTMLCanvasElement, mundo: Mundo, aoPerder: () => void, habitat: Habitat): () => void {
  /* antes da vista: os campos dela (o papel) ja criam cores */
  THREE.ColorManagement.enabled = true;
  const vista = new VistaIlha(canvas, mundo, habitat), caixa = canvas.parentElement;
  if (!caixa) throw new Error("cena 3D sem caixa");
  const perdeu = (ev: Event) => { ev.preventDefault(); aoPerder(); };
  canvas.addEventListener("webglcontextlost", perdeu);
  /* a camera livre (orbita.ts): a roda, o arrasto e a pinca na cena, com a opcao ligada em Ajustes */
  const soltarControles = ligarControles(() => habitatAtual().controle === "livre", () => vista.elevacao0);
  /* a camera solta (cameraLivre.ts): o teclado e o arrasto direito/do meio, so no desktop com o controle "Livre" */
  const soltarLivre = ligarCameraLivre(() => vista.podeSoltar, () => vista.elevacao0);
  let vivo = true, quadro = 0, pedido = 0;
  /* os kits: na hora, ou, se a ilha abriu coberta pelo veu, quando ela ficar a vista (no maximo KITS_COBERTO_MS) */
  let kitsPedidos = false;
  const carregarKits = () => {
    if (kitsPedidos) return;
    kitsPedidos = true;
    vista.carregarObjetos().catch(err => {
      if (!vivo) return;
      /* um mapa do dev sem os assets nesta maquina: volta para a ilha (a escolha gravada fica); a ilha sem os kits cai na reserva */
      if (vista.estilo.id !== "ilha") { console.error(`habitat: o mapa ${vista.estilo.id} não carregou; volta para a ilha:`, err); voltarParaIlha(vista.estilo.id); return; }
      console.error("ilha: os modelos dos kits não carregaram; fica a reserva do mundo:", err); aoPerder();
    });
  };
  const esperaKits = CENA.coberto ? setTimeout(carregarKits, KITS_COBERTO_MS) : null;
  if (!esperaKits) carregarKits();
  /* medir (a M3): os intervalos entre quadros do navegador */
  let medida: number[] | null = null, ultimoQuadro = performance.now();
  /* a queda de qualidade: a media de quadros em janelas de QUEDA_MS (a pagina escondida nao conta: o navegador para o laco) */
  let janela = { inicio: performance.now(), quadros: 0 };
  const laco = (agora: number) => {
    if (!vivo) return;
    /* coberta pelo veu: um quadro a cada COBERTO_MS, sem contar para a queda de qualidade */
    if (CENA.coberto && !medida) {
      if (agora - ultimoQuadro >= COBERTO_MS) { ultimoQuadro = agora; CENA.ret = vista.desenhar(agora, quadro++); }
      janela = { inicio: agora, quadros: 0 };
      pedido = requestAnimationFrame(laco);
      return;
    }
    carregarKits();
    if (medida) medida.push(agora - ultimoQuadro);
    if (agora - ultimoQuadro > 500) janela = { inicio: agora, quadros: 0 };
    ultimoQuadro = agora;
    /* com um lugar aberto (Crescer) o tempo nao conta: o painel de vidro sobre a cena nao pode degradar a ilha de vez */
    if (lugarAberto()) janela = { inicio: agora, quadros: 0 };
    janela.quadros++;
    if (agora - janela.inicio >= QUEDA_MS) {
      if (!vista.qualidadeBaixa && (janela.quadros * 1000) / (agora - janela.inicio) < FPS_MIN) { vista.baixarQualidade(); ajustar(); }
      janela = { inicio: agora, quadros: 0 };
    }
    CENA.ret = vista.desenhar(agora, quadro++);
    pedido = requestAnimationFrame(laco);
  };
  const ajustar = () => {
    vista.ajustar(caixa.clientWidth, caixa.clientHeight);
    if (caixa.clientWidth > 0 && caixa.clientHeight > 0) CENA.ret = vista.desenhar(performance.now(), quadro);
  };
  ajustar();
  const obs = new ResizeObserver(ajustar); obs.observe(caixa);
  pedido = requestAnimationFrame(laco);
  CENA.medir = () => new Promise(resolve => {
    medida = [];
    setTimeout(() => {
      const deltas = medida ?? [];
      medida = null;
      const total = deltas.reduce((a, b) => a + b, 0);
      resolve({
        medida: `M3 (tela Pet, ${vista.estilo.id}, câmera ${habitat.camera}, visual ${habitatAtual().visual})`, data: new Date().toISOString(), userAgent: navigator.userAgent, devicePixelRatio,
        tela_css: [innerWidth, innerHeight], canvas_px: [canvas.width, canvas.height],
        duracao_s: +(total / 1000).toFixed(3), quadros: deltas.length, fps_media: +((deltas.length * 1000) / total).toFixed(2),
        quadro_mediana_ms: +mediana(deltas).toFixed(2), quadro_p95_ms: +p95(deltas).toFixed(2),
        draw_calls: vista.renderer.info.render.calls, qualidade_baixa: vista.qualidadeBaixa,
      });
    }, 10_000);
  });
  CENA.modo3d = true;
  CENA.cocoNoChao = true;
  CENA.mundo = {
    paraMundo: (cx, cy) => vista.paraMundo(cx, cy),
    paraTela: (x, y) => vista.paraTela(x, y),
    get pet() { const p = vista.petDesenhado; if (!p) throw new Error("a cena do mundo ainda nao desenhou o pet"); return p; },
    get bola() { return vista.bolaDesenhada ?? undefined; },
  };
  return () => {
    vivo = false;
    cancelAnimationFrame(pedido); obs.disconnect(); if (esperaKits) clearTimeout(esperaKits); canvas.removeEventListener("webglcontextlost", perdeu);
    soltarControles(); soltarLivre(); despublicarVista();
    CENA.modo3d = false; CENA.cocoNoChao = false; CENA.ret = null; CENA.medir = null; CENA.mundo = null;
    vista.dispose();
  };
}
