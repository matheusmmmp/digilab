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
   - a viagem ao lugar (viagem.ts, L2 e L3 de "Lugares da ilha"): com Crescer, Lutar ou o Diario aberto, a camera vai ao saco de pancada, ao portao
     da arena ou a barraca do Tamer (lugares.ts; o portao e a barraca sao os modelos 3D da LUGARES_3D no ponto da grade, com o marcador provisorio de
     marcadoresLugar.ts ate o modelo carregar e nos estilos sem lugares), deixando-o a esquerda do painel
     (no celular no alto, acima da folha), e o pet desenhado anda ate ele e fica; ao sair, os dois voltam. So o desenho, como a coreografia abaixo;
   - a coreografia (docs/TAREFA_V3_HABITAT_OBJETOS.md): pedido um treino (CENA.treino), o pet desenhado vai ao saco de pancada, bate e
     volta (TREINO_MS); quando o motor rola a bola (uma rolagem nova no Mundo), o pet da um golpe nela. So o desenho: a posicao do motor,
     o ganho do treino e o log nao mudam.
   - o pet na mao (docs/TAREFA_V3_PEGAR_PET.md, P2; CENA.petNaMao, PegarPet.tsx): a camera e o foco da dobra param onde estavam (o
     paraMundo nao muda sob o dedo); o pet desenhado fica suspenso sobre o chao sob o dedo (pousoEm), balanca e faz careta (papel.ts,
     mao.ts), e a sombra fica onde ele vai cair, ja no mapa (noMapa, PP-4). Ao soltar, o desenho comeca onde o motor o pos (sem caminhar
     de volta: Seguidor.pular), com a queda e o quique, e o foco volta ao pet em ~MAO.focoTauMs.
   Os kits carregam depois do terreno; se um modelo nao carrega, a cena cai na reserva (MundoReserva), com o erro no console. */
import { comprimento, naRota, rotaEmTerra } from "./rotaConta.ts";
import { ILHA_DEV_AGUA } from "./ilhaDev.ts";
import { ponte } from "./ponte.ts";
import * as THREE from "three";
import { CMU_MVP_AGUA, TPD, eNoite, noMapa, type Mundo } from "../../../../motor/index.ts";
import { habitatAtual, voltarParaIlha, type Habitat } from "../../../habitat.ts";
import { jogoAtual } from "../../../jogo.ts";
import { CENA, reservaDoPe } from "../cenaEstado.ts";
import { Seguidor, dentroDoMapa } from "../vistaMundo.ts";
import { velocidadeAtual } from "../../../tempo.ts";
import { AFASTAR_MAX, BATER_BOLA_MS, duracaoPetViagem, CAMERAS, COBERTO_MS, GOLPE_DIST, GOLPE_MS, KITS_COBERTO_MS, FPS_MIN, LARGURA_MIN, LONGE, NEVOA, PERTO, QUEDA_MS,
  RAZAO_MAX, TEXEL_ALVO, TREINO_MS, type CameraHabitat } from "./constantes.ts";
import { CURVA, type CenaIlha, type Objetos, cobrirFundo } from "./cena.ts";
import { estiloDe, type Estilo } from "./estilos.ts";
import { dobrarY, lugarNoPonto, paraMundoCel, paraTelaNdc, type CameraLida, type Dobra } from "./curva.ts";
import { fimDaIlha, type FimDaIlha } from "./fimDaIlha.ts";
import { ilhaDe, type Ilha } from "./grade.ts";
import { Itens } from "./itens.ts";
import type { NomeLugar } from "./modelos.ts";
import { Papel, type Ret, type Suspenso } from "./papel.ts";
import { MAO, Pendulo, alturaDepoisDeSoltar, soltarAcabou, tremorAgora } from "./mao.ts";
import { ORBITA, aplicarOrbita, ligarControles, recentrar } from "../orbita.ts";
import { CONSULTA_SOLTA, TRANSICAO_MS, VISTA, despublicarVista, focoDoQuadro, ligarCameraLivre, publicarVista, type Limites, type MapaDaIlha, type Par } from "../cameraLivre.ts";
import { CAMERA_DEV, ligarCameraDev } from "../cameraDev.ts";
import { ABERTURA_PROPOSTA, inclinar, ligarAberturaDev, quadroDaAbertura, quadroDaSaida, tempoDaAbertura, zerarRelogioAbertura, type Ponto, type Proposta, type QuadroAbertura } from "./aberturaConta.ts";
import { PROPOSTA_ESCOLHIDA, aberturaPendente, marcarAberturaTocada } from "../../../abertura.ts";
import { PLANTA_ILHA } from "./constantes.ts";
import { pixelsDoMapa } from "./minimapa.ts";
import { PRESETS, Pos, SEM_CONTORNO } from "./pos.ts";
import { SACO_NA_TELA, VIAGEM, ZOOM_LUGAR_MOVEL, lugarAberto, progressoViagem, type Lugar } from "../../../viagem.ts";
import { LUGARES, ORDEM_LUGARES, chaoDoLugar, estadoDoLugar, gradeDosLugares, idaDoTreino, pontoDoLugar as pontoLugarDe, pontoDoPet, type BaseDoMundo } from "./lugares.ts";
import { Apagador, montarMarcadores, type Marcadores } from "./marcadoresLugar.ts";
import { TRANCAS } from "../../../trancas.ts";
import { mitologiaLigada } from "../../../mitologia.ts";
import { NuvemDoDia } from "./mitologia.ts";

const movimentoReduzido = (): boolean => matchMedia("(prefers-reduced-motion: reduce)").matches;

class VistaIlha {
  readonly renderer: THREE.WebGLRenderer;
  readonly camera: THREE.PerspectiveCamera;
  private readonly ilha: Ilha;
  private readonly cenaIlha: CenaIlha;
  /** o fim da ilha (fimDaIlha.ts): o mar em volta, ate o horizonte */
  private readonly fim: FimDaIlha;
  private readonly seguidor = new Seguidor();
  private readonly raio = new THREE.Raycaster();
  private readonly lida: CameraLida;
  private readonly papel = new Papel();
  private readonly itens: Itens;
  /** MITOLOGIA, E0: a nuvem do dia da brincadeira variada (so com a chave `mitologia`) */
  private readonly nuvem: NuvemDoDia;
  /** o ponto de cada lugar da ilha (celulas; lugares.ts) e a altura do chao no pe dele (celulas; o portao e a barraca ficam na moldura) */
  private readonly pontos: Record<Lugar, [number, number]>;
  private readonly chaoLugar: Record<Lugar, number>;
  /** os marcadores provisorios do portao e da barraca (marcadoresLugar.ts), soltos no dispose */
  private readonly marcadores: Marcadores;
  /** os lugares trancados (nivel do Tamer, trancas.ts) saem apagados: a versao da tabela de trancas que a cena ja aplicou */
  private readonly apagador = new Apagador();
  private versaoTrancas = -1;
  /** onde cada lugar cai na tela (o pe em px de CSS e a altura em px), reaproveitado a cada quadro; o retangulo do canvas e lido so em `ajustar` */
  private readonly lugaresTela: Record<Lugar, [number, number, number]> = { saco: [0, 0, 0], portao: [0, 0, 0], barraca: [0, 0, 0] };
  private readonly vLugar = new THREE.Vector3();
  private rectCanvas = { left: 0, top: 0, width: 1, height: 1 };
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
  /** o ponto que a camera e a dobra olham (celulas): o pet desenhado; outro com a camera solta (cameraLivre.ts) ou na viagem a um lugar (viagem.ts);
      com o pet na mao, fica onde estava, e logo depois de soltar volta a ele (focoVoltando) */
  private foco: [number, number] = [0, 0];
  private focoVoltando = false;
  private readonly dirCam = new THREE.Vector3();
  /** a ilha vista de cima e os limites do foco, para o minimapa (feitos uma vez) */
  private readonly mapa: MapaDaIlha;
  private readonly limites: Limites;
  private readonly consultaSolta = typeof matchMedia === "function" ? matchMedia(CONSULTA_SOLTA) : null;
  /** o pet na mao: se esta, o pendulo do papel, o ultimo ponto do chao sob o pe (celulas) e quando ele foi solto (para a queda) */
  private naMao = false;
  private readonly pendulo = new Pendulo();
  private chaoMao: [number, number] | null = null;
  private soltouEm: number | null = null;
  /** o treino na ilha: o pedido (CENA.treino) que esta tocando, quando comecou, o ponto em que o pet para para bater (ao lado do saco
      na tela) e o ultimo golpe que balancou o saco */
  private treino: { pedido: number; desde: number; ponto: [number, number]; golpe: number; ida: number } | null = null;
  private treinoVisto: number | null = CENA.treino;
  /** a batida na bola: quantas rolagens o motor ja tinha (null antes do primeiro quadro: as de antes de abrir a ilha nao contam) */
  private rolagens: number | null = null;
  private bateBola: { desde: number; alvo: [number, number] } | null = null;
  /* a camera do primeiro dia (aberturaConta.ts e src/abertura.ts): `semente` null e a do ?abertura= (as capturas da prancha: nao grava, nao
     acaba nem se interrompe); `saida` e a volta pelo toque (AB-3). `visto` guarda o pet e o ovo da ultima consulta ao pedido */
  private ab: { p: Proposta; semente: number | null; saida: { desde: number; de: QuadroAbertura } | null; ultimo: QuadroAbertura | null } | null =
    ABERTURA_PROPOSTA ? { p: ABERTURA_PROPOSTA, semente: null, saida: null, ultimo: null } : null;
  private abVisto = "";
  private abInterromper = false;
  private abMarca: string | null = null;
  /** a ida do pet ao lugar aberto (ou a volta), separada da camera: a chave da viagem ("1:<lugar>" ou "0"), de onde partiu, quando e quanto dura;
      null fora da viagem (constantes.ts, PET_VIAGEM_CEL_MS) */
  private andaPet: { chave: string; de: [number, number]; desde: number; dur: number; rota: [number, number][] | null } | null = null;

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
    this.camera.layers.enable(SEM_CONTORNO);
    CURVA.uCurva.value = this.estilo.dobra;
    THREE.ColorManagement.enabled = true;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    /* com o visual, um quadro sao dois desenhos (a cena no alvo e o quadro na tela): a contagem de draw calls da M3 e zerada por quadro */
    this.renderer.info.autoReset = false;
    this.pos = new Pos(this.renderer);
    /* ?ilha=agua (ilhaDev.ts): so a vista troca de ilha, para ver o desenho antes de o motor ligar a agua (a IA4) */
    this.ilha = ilhaDe(ILHA_DEV_AGUA ? CMU_MVP_AGUA : mu.cm);
    this.cenaIlha = this.estilo.montar(this.ilha);
    this.fim = fimDaIlha(this.ilha);
    this.cenaIlha.cena.add(this.fim.grupo);
    /* a ilha com agua (docs/TAREFA_V3_ILHA_AGUA.md, IA3): as pontes do mapa do motor */
    if (this.ilha.pontes.length) this.cenaIlha.cena.add(ponte(this.ilha));
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
    /* o portao e a barraca onde a grade da ilha os poe (grade.ts, porLugares; a planta A), o saco perto da praca (lugares.ts) */
    const base: BaseDoMundo = { ninho: this.itens.ninhoEm, comedouro: [mu.comedouro[0] / mu.cm.sub, mu.comedouro[1] / mu.cm.sub], area: this.ilha.area,
      grade: gradeDosLugares(this.ilha) };
    this.pontos = Object.fromEntries(ORDEM_LUGARES.map(id => [id, [...pontoLugarDe(id, base)]])) as Record<Lugar, [number, number]>;
    this.chaoLugar = Object.fromEntries(ORDEM_LUGARES.map(id => [id, chaoDoLugar(id, base)])) as Record<Lugar, number>;
    /* o portao e a barraca: marcadores provisorios no ponto de cada um, ate o modelo 3D chegar (carregarObjetos); nos estilos sem lugares, ficam */
    this.marcadores = montarMarcadores(base);
    this.nuvem = new NuvemDoDia(this.itens.ninhoEm);
    this.cenaIlha.cena.add(this.itens.raiz, this.papel.raiz, this.marcadores.raiz, this.nuvem.raiz);
    CURVA.uVento.value = 1;
    const il = this.ilha;
    this.mapa = { imagem: new ImageData(pixelsDoMapa(il, this.estilo.paleta), il.larg, il.prof), x0: il.x0, z0: il.z0, larg: il.larg, prof: il.prof, area: il.area };
    this.limites = { x0: il.x0, z0: il.z0, x1: il.x0 + il.larg, z1: il.z0 + il.prof };
  }

  /** a camera pode soltar agora: o controle "Livre" e a largura do desktop */
  /* com a camera de desenvolvimento (cameraDev.ts) a camera solta vale em qualquer largura e controle */
  get podeSoltar(): boolean { return CAMERA_DEV || (habitatAtual().controle === "livre" && !!this.consultaSolta?.matches); }
  /** os alvos da camera de desenvolvimento (cameraDev.ts), em celulas: os lugares da viagem, os modelos dos lugares, cada enfeite (o nome,
      e o numero a partir do segundo do mesmo nome), o ninho, o comedouro e o pet */
  alvosDev(): Record<string, Par> {
    const a: Record<string, Par> = {};
    for (const [id, p] of Object.entries(this.pontos)) a[id] = [p[0], p[1]];
    for (const l of this.ilha.lugares) a[l.nome] = [l.x, l.z];
    const vistos = new Map<string, number>();
    for (const e of this.ilha.enfeites) {
      const n = (vistos.get(e.nome) ?? 0) + 1;
      vistos.set(e.nome, n);
      a[n === 1 ? e.nome : `${e.nome}_${n}`] = [e.x, e.z];
    }
    const sub = this.mu.cm.sub;
    a.ninho = [...this.itens.ninhoEm] as Par;
    a.comedouro = [this.mu.comedouro[0] / sub, this.mu.comedouro[1] / sub];
    a.pet = [this.petCel[0], this.petCel[1]];
    return a;
  }

  /** os modelos do estilo (na ilha, os kits de public/kits3d) entram depois do terreno */
  async carregarObjetos(): Promise<void> {
    THREE.ColorManagement.enabled = true;
    /* os itens gerados (a bola, public/itens/) entram junto e falham do mesmo jeito: em todos os mapas, porque os itens sao os mesmos */
    const [o] = await Promise.all([this.estilo.objetos(this.ilha), this.itens.carregar(document.baseURI)]);
    this.objetos = o;
    this.cenaIlha.cena.add(o.grupo);
    /* os modelos 3D dos lugares (lugares.ts) chegaram: o marcador provisorio de cada um sai, e as trancas se aplicam de novo (aos modelos e ao saco
       gerado, que entrou agora) */
    for (const id of o.lugaresRaiz?.keys() ?? []) if (id === "portao" || id === "barraca") this.marcadores.tirar(id);
    this.versaoTrancas = -1;
    /* data-objetos: os kits e os itens ja estao na cena (as capturas dos itens esperam por ele, como o data-pronto) */
    this.renderer.domElement.parentElement?.setAttribute("data-objetos", "1");
    if (this.baixa) this.menosGrama();
  }

  /** a dobra de agora: centrada no ponto olhado (o foco: o pet desenhado, o foco da camera solta, o lugar da viagem ou, com o pet na mao, onde estava),
      ao longo da direcao em que a camera olha no chao */
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
    /* a nevoa do estilo (cena.userData.nevoa, o digital) ou a da ilha */
    const [perto, longe] = (this.cenaIlha.cena.userData.nevoa as readonly [number, number] | undefined) ?? NEVOA;
    nevoa.near = perto * this.afast * ORBITA.zoom; nevoa.far = longe * this.afast * ORBITA.zoom;
    /* o pet em papel: na distancia do foco, um texel do sprite vale um numero inteiro de pixels do canvas (regra 8) */
    this.ppu = this.renderer.domElement.height * this.fracEnq / 2 / (this.profundidadeDoPet(this.afast, this.orbitaVista) * Math.tan(THREE.MathUtils.degToRad(this.cam.fov / 2)));
    this.pxPorTexel = Math.max(1, Math.round(TEXEL_ALVO * this.ppu));
  }

  /** ajusta o canvas a caixa (px de CSS): a resolucao, a proporcao e o afastamento da camera em retrato */
  ajustar(larguraCss: number, alturaCss: number): void {
    this.larguraCss = Math.max(1, larguraCss); this.alturaCss = Math.max(1, alturaCss);
    { const r = this.canvas.getBoundingClientRect(); this.rectCanvas = { left: r.left, top: r.top, width: r.width || this.larguraCss, height: r.height || this.alturaCss }; }
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
  /** o pet na mao: o ponto do chao dobrado (celulas, sem limitar ao mapa) sob o pe desenhado em (peX, peY) do cliente, que fica
      MAO.alturaTexels acima do chao; null fora da cena ou fora do chao */
  private chaoSob(peX: number, peY: number): [number, number] | null {
    const r = this.canvas.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return null;
    const y = peY + (MAO.alturaTexels * this.pxPorTexel) / this.renderer.getPixelRatio();
    if (peX < r.left || peX > r.right || y < r.top || y > r.bottom) return null;
    return paraMundoCel(this.lida, this.dobra, ((peX - r.left) / r.width) * 2 - 1, 1 - ((y - r.top) / r.height) * 2);
  }
  /** o mesmo ponto em subunidades inteiras do mapa (o que o "levar pet" grava; o motor o limita ao mapa) */
  pousoEm(peX: number, peY: number): [number, number] | null {
    const p = this.chaoSob(peX, peY), sub = this.mu.cm.sub;
    return p ? [Math.round(p[0] * sub), Math.round(p[1] * sub)] : null;
  }
  /** o lugar da ilha (lugares.ts) sob o ponto do cliente (px), pela mesma dobra; null fora da cena, antes dos modelos ou num estilo sem lugares */
  lugarEm(cx: number, cy: number): NomeLugar | null {
    const caixas = this.objetos?.lugares, r = this.canvas.getBoundingClientRect();
    if (!caixas || !(r.width > 0 && r.height > 0) || cx < r.left || cx > r.right || cy < r.top || cy > r.bottom) return null;
    return lugarNoPonto(caixas, (x, y, z) => paraTelaNdc(this.lida, this.dobra, x, z, y), ((cx - r.left) / r.width) * 2 - 1, 1 - ((cy - r.top) / r.height) * 2);
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
    const { cel: motorCel, andando: emViagem } = this.petNaViagem(agora, motorCel0, reduzido);
    if (CENA.treino !== null && CENA.treino !== this.treinoVisto) {
      this.treinoVisto = CENA.treino;
      const dir = new THREE.Vector3(1, 0, 0).applyQuaternion(this.camera.quaternion), h = Math.hypot(dir.x, dir.z) || 1;
      const [rx, rz] = [dir.x / h, dir.z / h], lado = viagem > 0 ? -1 : (motorCel[0] - sx) * rx + (motorCel[1] - sz) * rz >= 0 ? 1 : -1;
      const ponto: [number, number] = [sx + lado * rx * GOLPE_DIST, sz + lado * rz * GOLPE_DIST];
      this.treino = { pedido: CENA.treino, desde: agora, ponto, golpe: -1, ida: idaDoTreino(Math.hypot(ponto[0] - motorCel[0], ponto[1] - motorCel[1])) };
    }
    const t = this.treino;
    const caminhando = this.andaPet === null && this.seguidor.caminhando;
    if (!t) return { cel: motorCel, golpe: this.bateBola, andando: emViagem || caminhando };
    /* a ida e a volta pela distancia (PA-3; idaDoTreino), os golpes pelo TREINO_MS */
    const dt = agora - t.desde, { golpes } = TREINO_MS, ida = t.ida, volta = t.ida, ponto = t.ponto;
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

  /** onde o pet esta na ida ao lugar aberto (ou na volta): ele anda do ponto em que estava desenhado ate o lugar (ou de volta ate o motor) em
      velocidade constante, PET_VIAGEM_CEL_MS, sem passar de PET_VIAGEM_MAX_MS; a camera e o painel seguem o tempo da viagem (VIAGEM_MS) e chegam antes.
      Com "reduzir movimento", chega na hora. Fora da viagem, o que o motor diz */
  private petNaViagem(agora: number, motorCel0: [number, number], reduzido: boolean): { cel: [number, number]; andando: boolean } {
    const chave = VIAGEM.alvo === 1 ? "1:" + VIAGEM.lugar : "0";
    if (chave !== (this.andaPet?.chave ?? "0")) {
      const de: [number, number] = [this.petCel[0], this.petCel[1]], para = chave === "0" ? motorCel0 : this.pontoDoPetNo(VIAGEM.lugar);
      /* na ilha com agua o pet contorna a agua pelo caminho em terra (rotaConta.ts; IA4); sem agua, a reta de sempre */
      const rota = this.ilha.comAgua ? rotaEmTerra(this.ilha.cm, de, [para[0], para[1]]) : null;
      const dur = duracaoPetViagem(rota ? comprimento(rota) : Math.hypot(para[0] - de[0], para[1] - de[1]), reduzido);
      this.andaPet = { chave, de, desde: agora, dur, rota };
    }
    const a = this.andaPet;
    if (!a) return { cel: motorCel0, andando: false };
    const para = a.chave === "0" ? motorCel0 : this.pontoDoPetNo(VIAGEM.lugar);
    const f = a.dur > 0 ? Math.min(1, (agora - a.desde) / a.dur) : 1;
    if (f >= 1 && a.chave === "0") { this.andaPet = null; return { cel: motorCel0, andando: false }; }
    if (a.rota && f < 1) {
      /* a volta segue o pet do motor, que pode ter andado desde a partida: o desvio do fim da rota entra aos poucos, sem salto na chegada */
      const [x, z] = naRota(a.rota, f), u = a.rota[a.rota.length - 1];
      return { cel: [x + (para[0] - u[0]) * f, z + (para[1] - u[1]) * f], andando: true };
    }
    return { cel: f >= 1 ? para : this.entre(a.de, para, f), andando: f < 1 };
  }
  /** a abertura deste quadro, ou null (a camera de sempre). Comeca quando o ovo do pet de agora chocou e ela ainda nao tocou (AB-2), com o ovo
      fora da tela, sem o pet na mao, sem lugar aberto e sem o veu; com "reduzir movimento" ela e pulada (AB-5). Um toque, uma tecla ou a roda
      (AB-3), o pet na mao ou um lugar aberto encerram: a camera volta a de sempre em TRANSICAO_MS. Acabou, interrompida ou pulada, ela fica
      marcada (src/abertura.ts) e nao volta */
  private quadroDaAbertura(agora: number, reduzido: boolean, viagem: number, zoomDeSempre: number): QuadroAbertura | null {
    const jg = jogoAtual(), m = jg.motor, livre = !this.naMao && viagem === 0 && !CENA.coberto;
    if (!this.ab && !ABERTURA_PROPOSTA && jg.nascendo === 0 && !m.morte) {
      const visto = `${m.semente}/${jg.nascendo}`;
      if (visto !== this.abVisto) {
        if (!aberturaPendente(m.semente)) this.abVisto = visto;
        else if (reduzido) { marcarAberturaTocada(m.semente); this.abVisto = visto; }
        else if (livre) {
          this.abVisto = visto; this.abInterromper = false; zerarRelogioAbertura();
          this.ab = { p: PROPOSTA_ESCOLHIDA, semente: m.semente, saida: null, ultimo: null };
        }
      }
    }
    const ab = this.ab;
    let q: QuadroAbertura | null = null;
    if (ab && ab.semente === null) {
      /* ?abertura=: como na prancha, so com a ilha livre; depois do fim, a camera de sempre */
      const r = livre && !reduzido ? quadroDaAbertura(ab.p, tempoDaAbertura(agora), this.pontosDaAbertura()) : null;
      q = r && !r.acabou ? r : null;
    } else if (ab && ab.semente !== null) {
      if (reduzido) { this.encerrarAbertura(); }
      else if (ab.saida) {
        const r = quadroDaSaida(ab.saida.de, agora - ab.saida.desde, this.petCel, zoomDeSempre, TRANSICAO_MS);
        if (r.acabou) this.ab = null; else q = r;
      } else {
        const r = quadroDaAbertura(ab.p, tempoDaAbertura(agora), this.pontosDaAbertura());
        if (r.acabou) { marcarAberturaTocada(ab.semente); this.ab = null; }
        else if (this.abInterromper || !livre) {
          marcarAberturaTocada(ab.semente);
          const de = ab.ultimo ?? r;
          ab.saida = { desde: agora, de };
          q = quadroDaSaida(de, 0, this.petCel, zoomDeSempre, TRANSICAO_MS);
        } else { ab.ultimo = r; q = r; }
      }
      this.abInterromper = false;
    }
    /* data-abertura: "tocando" ou "saindo" enquanto a camera do primeiro dia manda (os testes e2e esperam por ele) */
    const marca = q === null ? null : this.ab?.saida ? "saindo" : "tocando";
    if (marca !== this.abMarca) {
      this.abMarca = marca;
      const el = this.renderer.domElement.parentElement;
      if (marca) el?.setAttribute("data-abertura", marca); else el?.removeAttribute("data-abertura");
    }
    return q;
  }
  /** onde fica cada ponto olhado pela abertura agora (celulas) */
  private pontosDaAbertura(): Record<Ponto, [number, number]> {
    return {
      pet: this.petCel, ninho: this.itens.ninhoEm, praca: [PLANTA_ILHA.praca.x, PLANTA_ILHA.praca.z], portao: this.pontos.portao, barraca: this.pontos.barraca,
      meio: [(this.petCel[0] + PLANTA_ILHA.praca.x) / 2, (this.petCel[1] + PLANTA_ILHA.praca.z) / 2],
    };
  }
  /** um toque, uma tecla ou a roda: a abertura que toca volta ao pet (AB-3); a do ?abertura= nao se interrompe */
  interromperAbertura(): void { if (this.ab && this.ab.semente !== null && !this.ab.saida) this.abInterromper = true; }
  /** a abertura de verdade sai agora (a tela fechou no meio, ou o "reduzir movimento" ligou): fica marcada e nao volta */
  encerrarAbertura(): void {
    if (this.ab && this.ab.semente !== null) marcarAberturaTocada(this.ab.semente);
    if (this.ab?.semente !== null) this.ab = null;
  }

  private suave(f: number): number { return f * f * (3 - 2 * f); }
  private entre(a: [number, number], b: [number, number], f: number): [number, number] { return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]; }
  /** a direita da camera no chao (unitaria): a direita da direcao em que ela olha */
  private get direita(): [number, number] { return [-this.dirDobra[1], this.dirDobra[0]]; }
  /** onde o pet fica no lugar `l`: o saco, a esquerda dele na tela a GOLPE_DIST (a conta da L2); os grandes, na frente deles, do lado da camera,
      alem do raio da base (lugares.ts, pontoDoPet) */
  private pontoDoPetNo(l: Lugar): [number, number] {
    const [sx, sz] = this.pontos[l], [rx, rz] = this.direita;
    if (l === "saco") return [sx - rx * GOLPE_DIST, sz - rz * GOLPE_DIST];
    return pontoDoPet([sx, sz], LUGARES[l].raio, this.dirDobra, [rx, rz]);
  }
  /** o cos da elevacao da camera: quanto de uma altura vertical aparece na tela (a conta de um objeto de pe) */
  private get cosElevacao(): number {
    const [dx, dy, dz] = this.orbitaVista.desloc, h = Math.hypot(dx, dy, dz) || 1;
    return Math.sqrt(Math.max(0, 1 - (dy / h) ** 2));
  }
  /** onde o lugar `l` fica na tela com o painel aberto: a fracao da largura (de 900 px em diante) e da altura (do pe do lugar, a partir do alto; so nos
      grandes a 1920, que se enquadram inteiros; o saco nao mexe na vertical, como na L2). O saco fica a 0,41 da largura (a esquerda do painel); os
      grandes mais a esquerda, para a largura deles caber antes do painel, e a 0,26 (saco) ou 0,40 (grandes) da altura abaixo de 900 px, para o objeto
      todo ficar acima da folha. PROPOSTO, SEM FONTE (numero de interface, nao de jogo) */
  private naTela(l: Lugar): { largo: number; movel: number; vLargo: number | null } {
    if (l === "saco") return { largo: SACO_NA_TELA.largo, movel: SACO_NA_TELA.movel, vLargo: null };
    return { largo: 0.3, movel: 0.4, vLargo: 0.62 };
  }
  /** o zoom final do lugar `l` (a distancia da camera vira esta fracao da de antes; < 1 aproxima): o saco, o de sempre (1 de 900 px em diante); os
      grandes, o que faz o objeto inteiro ocupar a fracao da altura da tela (43 % a 1920, 30 % no celular, onde sobra o alto acima da folha) */
  private zoomFinal(l: Lugar): number {
    if (l === "saco") return this.largo ? 1 : ZOOM_LUGAR_MOVEL;
    return this.resolverLugar(l).zoom;
  }
  /** a camera de teste: a mesma lente da principal, para simular um enquadramento sem mexer nela */
  private camTeste: THREE.PerspectiveCamera | null = null;
  private readonly vTeste = new THREE.Vector3();
  /** o ponto (x, y, z) do mundo em px de CSS na tela, vista de `cam` com a dobra `dobra` */
  private pxDe(cam: THREE.Camera, dobra: Dobra, x: number, y: number, z: number): [number, number] {
    this.vTeste.set(x, dobrarY(y, z, dobra, x), z).project(cam);
    return [(this.vTeste.x + 1) / 2 * this.larguraCss, (1 - this.vTeste.y) / 2 * this.alturaCss];
  }
  /** onde o lugar `l` (o pe e o topo) cai na tela com a camera a `afast` olhando `foco`: o pe (x, y) e a altura (px) */
  private medirLugar(l: Lugar, afast: number, foco: [number, number]): { x: number; y: number; h: number } {
    const cam = this.camTeste ??= new THREE.PerspectiveCamera();
    cam.copy(this.camera, false); cam.updateProjectionMatrix();
    const { desloc, olhar } = this.orbitaVista;
    cam.position.set(foco[0] + desloc[0] * afast, desloc[1] * afast, foco[1] + desloc[2] * afast);
    cam.lookAt(foco[0] + olhar[0] * afast, olhar[1] * afast, foco[1] + olhar[2] * afast);
    cam.updateMatrixWorld();
    const dobra: Dobra = { k: this.estilo.dobra, focoX: foco[0], focoZ: foco[1], dir: this.dirDobra }, [px, pz] = this.pontos[l];
    const y0 = this.chaoLugar[l], [bx, by] = this.pxDe(cam, dobra, px, y0, pz), [, ty] = this.pxDe(cam, dobra, px, y0 + LUGARES[l].altura, pz);
    return { x: bx, y: by, h: by - ty };
  }
  /** o enquadramento final dos lugares grandes (o portao e a barraca): o zoom e o ponto olhado que deixam o objeto INTEIRO na tela, com um pouco de ceu
      acima, de 37 % da altura medida no eixo a 1920 (cerca de 45 % na tela, pela perspectiva) (o pe a 62 % da altura e a 30 % da largura, a esquerda do painel) e de 30 % no celular (o pe a 40 % da altura,
      centrado, acima da folha). Resolvido por simulacao (perspectiva e dobra incluidas): a cada passo o afastamento muda pela razao entre a altura medida
      e a desejada, e o ponto olhado anda pelo erro do pe na tela. Guardado ate a janela, a orbita ou o lugar mudarem. PROPOSTO, SEM FONTE (numero de
      interface, nao de jogo) */
  private enquadrados = new Map<string, { zoom: number; foco: [number, number] }>();
  private resolverLugar(l: Lugar): { zoom: number; foco: [number, number] } {
    if (this.enquadrados.size > 24) this.enquadrados.clear();
    const chave = `${l}|${this.larguraCss}|${this.alturaCss}|${ORBITA.versao}|${this.afastBase}|${this.largo}|${this.fracEnq}`, guardado = this.enquadrados.get(chave);
    if (guardado) return guardado;
    const W = this.larguraCss, H = this.alturaCss, alvoH = (this.largo ? 0.37 : 0.3) * H, alvoX = (this.largo ? 0.3 : 0.5) * W, alvoY = (this.largo ? 0.62 : 0.4) * H;
    const [rx, rz] = this.direita, [fx, fz] = this.dirDobra, [dx, dy, dz] = this.orbitaVista.desloc, hip = Math.hypot(dx, dy, dz) || 1, seno = Math.max(0.2, Math.abs(dy) / hip);
    const cos = Math.sqrt(Math.max(0.04, 1 - seno * seno));
    let afast = this.afastBase, foco: [number, number] = [...this.pontos[l]];
    for (let i = 0; i < 10; i++) {
      const m = this.medirLugar(l, afast, foco);
      if (!(m.h > 1e-3)) break;
      const ppc = m.h / (LUGARES[l].altura * cos);
      afast = Math.min(this.afastBase * 6, Math.max(this.afastBase * 0.3, afast * (m.h / alvoH)));
      /* o pe a direita do alvo: o foco anda para a direita; o pe abaixo do alvo: o foco anda para tras (o objeto sobe na tela) */
      const ex = (m.x - alvoX) / ppc, ey = (m.y - alvoY) / (ppc * seno);
      foco = [foco[0] + rx * ex - fx * ey, foco[1] + rz * ex - fz * ey];
    }
    const r = { zoom: afast / this.afastBase, foco };
    this.enquadrados.set(chave, r);
    return r;
  }
  /** o zoom da viagem: de 1 (ou do zoom do lugar de origem, numa troca direta) ate o zoom final do lugar */
  private zoomDaViagem(p: number, reduzido: boolean): number {
    const s = reduzido ? 1 : this.suave(p), z0 = VIAGEM.origem ? this.zoomFinal(VIAGEM.origem) : 1;
    return z0 + (this.zoomFinal(VIAGEM.lugar) - z0) * s;
  }
  /** a altura do lugar aberto na tela (px): a placa fica acima dela. O saco mantem a conta da L2 (altura x px por celula); os grandes, a medida com a
      camera de agora (o topo projetado) mais uma folga */
  private alturaDoLugarNaTela(): number {
    const l = VIAGEM.lugar, alt = LUGARES[l].altura;
    if (l === "saco") return alt * (this.ppu / this.renderer.getPixelRatio());
    const [px, pz] = this.pontos[l], y0 = this.chaoLugar[l], dobra = this.dobra, [, by] = this.pxDe(this.camera, dobra, px, y0, pz), [, ty] = this.pxDe(this.camera, dobra, px, y0 + alt, pz);
    return by - ty + 8;
  }
  /** o ponto olhado no lugar `l`: o ponto do lugar deslocado para ele ficar onde o painel deixa (a esquerda dele de 900 px em diante; no alto,
      acima da folha, abaixo) */
  private ancoraDoLugar(l: Lugar): [number, number] {
    if (l !== "saco") return this.resolverLugar(l).foco;
    const [sx, sz] = this.pontos[l], [rx, rz] = this.direita, [fx, fz] = this.dirDobra, t = this.naTela(l);
    const ppc = Math.max(1e-6, this.ppu / this.renderer.getPixelRatio());      // px de CSS por celula na distancia do ponto olhado
    const seno = Math.max(0.2, Math.abs(this.orbitaVista.desloc[1]) / (Math.hypot(...this.orbitaVista.desloc) || 1));
    let ax = sx, az = sz;
    /* o pe do lugar acima do centro do quadro da camera (fracao < 0,5): o foco fica antes dele, no chao (a distancia na tela encurta pelo seno da
       elevacao); abaixo do centro, depois dele */
    const vertical = (frac: number) => {
      const k = (this.alturaCss * this.fracEnq / 2 - frac * this.alturaCss) / ppc / seno;
      ax -= fx * k; az -= fz * k;
    };
    if (this.largo) {
      /* o lugar a esquerda do centro: o foco fica a direita dele */
      const k = (0.5 - t.largo) * this.larguraCss / ppc;
      ax += rx * k; az += rz * k;
      if (t.vLargo !== null) vertical(t.vLargo);
    } else vertical(t.movel);
    return [ax, az];
  }
  /** o ponto olhado com a viagem: do que a camera olharia sem ela (ou do lugar de onde veio, numa troca direta) ate o lugar. `p` e o progresso (0 a 1) */
  private focoDaViagem(base: [number, number], p: number, reduzido: boolean): [number, number] {
    const s = reduzido ? 1 : this.suave(p);
    return this.entre(VIAGEM.origem ? this.ancoraDoLugar(VIAGEM.origem) : base, this.ancoraDoLugar(VIAGEM.lugar), s);
  }

  /** um quadro: o pet onde o motor diz (interpolado), a camera atras dele, a racao e a bola, o dia ou a noite; devolve o retangulo do pet */
  desenhar(agora: number, quadro: number): Ret {
    /* o ColorManagement do three e um global que as outras vistas (a sala e o mapa da Exploracao) desligam: sem repor aqui, a cor da nevoa
       e das luzes dependia de qual import dinamico subia por ultimo */
    THREE.ColorManagement.enabled = true;
    CURVA.uCurva.value = this.estilo.dobra;
    const { motor: m } = jogoAtual(), mu = m.mundo ?? this.mu, cm = mu.cm, sub = cm.sub;
    const dtMs = agora - this.ultimo, reduzido = movimentoReduzido(), jg = jogoAtual();
    /* o pet na mao (CENA.petNaMao): entrou, o pendulo parte do zero; saiu, o desenho comeca onde o motor o pos (o "levar pet" ja foi
       gravado no pointerup, antes da marca cair), sem caminhar de volta */
    const mao = CENA.petNaMao ? CENA.maoPet : null;
    if (mao && !this.naMao) {
      this.naMao = true; this.pendulo.zerar(); this.soltouEm = null; this.focoVoltando = false; this.chaoMao = null;
      this.treino = null; this.bateBola = null;
    }
    if (!mao && this.naMao) { this.naMao = false; this.seguidor.pular(mu.pet); this.soltouEm = agora; this.focoVoltando = true; }
    const pos = this.naMao ? (this.seguidor.pos ?? [mu.pet[0], mu.pet[1]])
      : this.seguidor.seguir(mu.pet, dtMs, cm, { velJogo: velocidadeAtual(), acao: m.acao, dorme: jg.nascendo > 0 || m.acao === "dormir", reduzido });
    this.ultimo = agora;
    const viagem = progressoViagem(agora);
    const motorCel: [number, number] = [pos[0] / sub, pos[1] / sub];
    let cor: { cel: [number, number]; golpe: { desde: number; alvo: [number, number] } | null; andando: boolean };
    let suspenso: Suspenso | null = null;
    if (mao) {
      /* suspenso sobre o chao sob o pe; fora do chao, o ultimo ponto dele (ou onde estava) */
      this.chaoMao = this.chaoSob(mao.x, mao.y) ?? this.chaoMao ?? [this.petCel[0], this.petCel[1]];
      const [lx, lz] = noMapa(Math.round(this.chaoMao[0] * sub), Math.round(this.chaoMao[1] * sub), cm);
      cor = { cel: this.chaoMao, golpe: null, andando: false };
      suspenso = { naMao: true, altura: MAO.alturaTexels, angulo: this.pendulo.passo(dtMs, mao.x, agora, reduzido),
        tremor: tremorAgora(agora, reduzido), sombra: [lx / sub, lz / sub] };
    } else {
      cor = this.coreografia(mu, agora, motorCel, reduzido, viagem);
      if (this.soltouEm !== null) {
        const ms = agora - this.soltouEm;
        if (soltarAcabou(ms, reduzido)) this.soltouEm = null;
        else suspenso = { naMao: false, altura: alturaDepoisDeSoltar(ms, reduzido), angulo: 0, tremor: 0, sombra: null };
      }
    }
    this.petCel = cor.cel;
    /* o zoom do lugar: abaixo de 900 px a camera se aproxima do saco com a viagem (o saco e o pet ficam grandes no terco de cima) e volta ao sair */
    /* a camera do primeiro dia: o ponto olhado, o zoom e a inclinacao saem da abertura enquanto ela toca, e da volta ao pet depois de um toque */
    const zoomDeSempre = viagem > 0 ? this.zoomDaViagem(viagem, reduzido) : 1;
    const aberta = this.quadroDaAbertura(agora, reduzido, viagem, zoomDeSempre);
    const zoom = aberta ? aberta.zoom : zoomDeSempre;
    if (this.afastBase * zoom !== this.afast) { this.afast = this.afastBase * zoom; this.orbitaVersao = -1; }
    this.atualizarOrbita();
    const pode = this.podeSoltar;
    /* o foco: preso com o pet na mao (PEGAR_PET; nem a camera solta anda); fora disso, o da camera solta (o pet, ou o ponto solto; cameraLivre.ts), ao
       qual ele volta suave logo depois de soltar o pet; e, com um lugar aberto, o da viagem (viagem.ts) */
    if (!this.naMao) {
      const alvo = focoDoQuadro(this.petCel, agora, dtMs, this.dirDobra, this.limites, pode);
      const dx = alvo[0] - this.foco[0], dz = alvo[1] - this.foco[1];
      if (this.focoVoltando && !reduzido && Math.hypot(dx, dz) > 0.01) {
        const k = 1 - Math.exp(-Math.max(0, dtMs) / MAO.focoTauMs);
        this.foco = [this.foco[0] + dx * k, this.foco[1] + dz * k];
      } else { this.foco = [alvo[0], alvo[1]]; this.focoVoltando = false; }
      if (viagem > 0) this.foco = this.focoDaViagem(this.foco, viagem, reduzido);
      if (aberta) this.foco = this.ab?.saida ? quadroDaSaida(this.ab.saida.de, agora - this.ab.saida.desde, this.foco, zoomDeSempre, TRANSICAO_MS).foco : aberta.foco;
    }
    const [px, pz] = this.foco, a = this.afast;
    const { olhar } = this.orbitaVista, desloc = aberta?.inclina ? inclinar(this.orbitaVista.desloc, aberta.inclina) : this.orbitaVista.desloc;
    this.camera.position.set(px + desloc[0] * a, desloc[1] * a, pz + desloc[2] * a);
    this.camera.lookAt(px + olhar[0] * a, olhar[1] * a, pz + olhar[2] * a);
    this.camera.updateMatrixWorld();
    CURVA.uFocoX.value = px; CURVA.uFocoZ.value = pz;
    CURVA.uDirX.value = this.dirDobra[0]; CURVA.uDirZ.value = this.dirDobra[1];
    CURVA.uTempo.value = reduzido ? 0 : agora / 1000;
    const noite = eNoite(m.e.tick % TPD);
    if (noite !== this.noite) { this.noite = noite; this.cenaIlha.aplicarNoite(noite); }
    cobrirFundo(this.cenaIlha.cena.background, this.camera.aspect);
    this.objetos?.noite?.(noite);
    this.objetos?.quadro?.(this.foco, this.estilo.dobra, this.dirDobra, Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2)) * this.camera.aspect);
    this.aplicarTrancas();
    this.itens.sincronizar(mu, m.e.tick, noite, agora, dtMs, m.lesionadoDesde !== null, reduzido, m.e.sujeira, this.naMao ? motorCel : this.petCel);
    this.nuvem.sincronizar(m, mitologiaLigada(), agora, reduzido);
    /* o pet longe do foco (a camera solta, a viagem, a volta depois de soltar o pet): o chao sob ele desce pela dobra (yPe), e o tamanho do papel vale
       na distancia dele (senao o texel deixa de ser inteiro e o pet cresce ou encolhe com a distancia ao foco). Com o pet na mao o tamanho fica o do
       foco, como na P2 da PEGAR_PET (o chaoSob conta a altura da mao com ele) */
    const yPe = dobrarY(0, this.petCel[1], this.dobra, this.petCel[0]);
    let ppu = this.ppu, pxPorTexel = this.pxPorTexel;
    if (!this.naMao && (this.petCel[0] !== px || this.petCel[1] !== pz)) {
      const dir = this.camera.getWorldDirection(this.dirCam), prof = (this.petCel[0] - this.camera.position.x) * dir.x
        + (yPe - this.camera.position.y) * dir.y + (this.petCel[1] - this.camera.position.z) * dir.z;
      if (prof > 1e-3) {
        ppu = this.renderer.domElement.height / 2 / (prof * Math.tan(THREE.MathUtils.degToRad(this.cam.fov / 2)));
        pxPorTexel = Math.max(1, Math.round(TEXEL_ALVO * ppu));
      }
    }
    const ret = this.papel.atualizar({
      agora, dt: Math.min(0.05, dtMs / 1000), quadro, cel: this.petCel, motor: mu.pet, camera: this.camera,
      ppu, pxPorTexel, yPe, canvas: [this.renderer.domElement.width, this.renderer.domElement.height],
      razao: this.renderer.getPixelRatio(), reduzido, noite, golpe: cor.golpe, andandoVista: cor.andando, suspenso,
    });
    /* o foco do HD-2D: a altura do pet na tela (0 embaixo, 1 em cima) */
    this.renderer.info.reset();
    /* o pet em papel fica sem o traco do estilo (pos.ts, SEM_CONTORNO): os filhos dele mudam, entao a camada e posta a cada quadro */
    if (this.estilo.contorno) this.papel.raiz.traverse(o => o.layers.set(SEM_CONTORNO));
    this.pos.desenhar(this.cenaIlha.cena, this.camera, PRESETS[habitatAtual().visual], 1 - (ret.y + ret.h * 0.6) / this.alturaCss, this.estilo.contorno ?? null);
    this.publicar(mu, m.e.tick, ret, pode);
    this.publicarLugaresTela();
    return ret;
  }

  /** o lugar trancado fica apagado e o destrancado volta ao normal; so quando a tabela de trancas mudou (trancas.ts, escrita pelo nivel do Tamer) */
  private aplicarTrancas(): void {
    if (this.versaoTrancas === TRANCAS.versao) return;
    this.versaoTrancas = TRANCAS.versao;
    for (const id of ORDEM_LUGARES) {
      const trancado = estadoDoLugar(id) === "trancado";
      /* o portao e a barraca: o modelo 3D (lugares.ts) quando ja chegou, senao o marcador provisorio; a mascara de luz acende so no aberto */
      const raiz = id === "saco" ? this.itens.sacoRaiz : this.objetos?.lugaresRaiz?.get(id) ?? this.marcadores.porLugar.get(id);
      if (raiz) this.apagador.aplicar(raiz, trancado);
      if (id !== "saco") this.objetos?.abrirLugar?.(id, !trancado);
    }
  }
  /** onde cada lugar cai na tela (o pe, em px de CSS, e a altura dele em px): o cadeado com o "Nv N" (CadeadosDaIlha.tsx) fica sobre ele, e os selos e as
      etiquetas dos objetos que falam (ObjetosDaIlha.tsx) tambem. Em qualquer largura */
  private publicarLugaresTela(): void {
    const cb = CENA.aoLugares, cbObjetos = CENA.aoObjetos;
    if (!cb && !cbObjetos) return;                      // sem consumidor (nenhum cadeado, brilho ou objeto que fala na tela): nao calcula
    const ppc = this.ppu / this.renderer.getPixelRatio(), r = this.rectCanvas, v = this.vLugar, alvo = this.lugaresTela;
    for (const id of ORDEM_LUGARES) {
      const x = this.pontos[id][0], z = this.pontos[id][1];
      const y0 = this.chaoLugar[id];
      v.set(x, dobrarY(y0, z, this.dobra, x), z).project(this.camera);
      const a = alvo[id];
      a[0] = r.left + ((v.x + 1) / 2) * r.width; a[1] = r.top + ((1 - v.y) / 2) * r.height;
      /* a altura na tela: o saco (perto do pet) pela conta da L2, altura x px por celula na distancia do foco; o portao e a barraca (na moldura, longe
         do foco: a px por celula do foco os aumentava e o cadeado subia acima do modelo) pelo topo projetado, como em alturaDoLugarNaTela */
      if (id === "saco") a[2] = LUGARES[id].altura * ppc;
      else { v.set(x, dobrarY(y0 + LUGARES[id].altura, z, this.dobra, x), z).project(this.camera); a[2] = a[1] - (r.top + ((1 - v.y) / 2) * r.height); }
    }
    cb?.(alvo);
    cbObjetos?.(alvo, ppc);
  }

  /** o que o minimapa e a HUD leem (cameraLivre.ts): o foco, o pet, a vista, os lugares, a comida, e se o pet saiu da tela e para que lado */
  private publicar(mu: Mundo, tick: number, ret: Ret, pode: boolean): void {
    /* abaixo de 900 px nada le o minimapa nem o resumo: sem alocar por quadro (o celular), e o que estava publicado sai uma vez */
    if (!CAMERA_DEV && !this.consultaSolta?.matches) { if (VISTA.atual) despublicarVista(); return; }
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
      comidas: this.itens.comidasNoMapa(mu, tick), ninho: this.itens.ninhoEm, comedouro: [mu.comedouro[0] / sub, mu.comedouro[1] / sub], saco: this.itens.sacoEm, portao: this.pontos.portao, barraca: this.pontos.barraca,
      /* as arvores de fruta do motor (o layout MVP dos pets v13+ nao tem nenhuma; as arvores da ilha sao enfeite da vista) */
      arvores: mu.arvores.map(t => [t.x / sub, t.y / sub] as [number, number]),
      petFora: fora, lado: Math.abs(lado) >= Math.abs(frente) ? (lado > 0 ? "direita" : "esquerda") : (frente > 0 ? "cima" : "baixo"),
      pxPorCelula: this.ppu / this.renderer.getPixelRatio(), senoElevacao: Math.abs(desloc[1]) / (Math.hypot(desloc[0], desloc[1], desloc[2]) || 1),
      mapa: this.mapa, limites: this.limites,
      /* a altura do lugar aberto na tela (px): a placa fica acima dela. O saco mantem a conta da L2 (altura x px por celula); os grandes contam o cos da elevacao */
      lugarAltPx: lugarAberto() ? this.alturaDoLugarNaTela() : undefined,
      lugarTela: lugarAberto() ? this.paraTela(this.pontos[VIAGEM.lugar][0] * sub, this.pontos[VIAGEM.lugar][1] * sub) : undefined,
    }, true, pode);
  }

  dispose(): void { this.marcadores.dispose(); this.papel.dispose(); this.pos.dispose(); this.renderer.dispose(); }

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
  /* a camera de desenvolvimento (?cameradev=1): window.__camera para as ferramentas */
  const soltarDev = ligarCameraDev(() => vista.alvosDev());
  /* o prototipo da camera do primeiro dia (?abertura=): window.__abertura para as capturas da prancha */
  const soltarAbertura = ligarAberturaDev();
  /* a camera do primeiro dia: um toque, uma tecla ou a roda em qualquer lugar da pagina a encerra (AB-3) */
  const interromper = () => vista.interromperAbertura(), EV_ABERTURA = ["pointerdown", "keydown", "wheel"] as const;
  for (const ev of EV_ABERTURA) window.addEventListener(ev, interromper, { capture: true, passive: true });
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
    pousoEm: (x, y) => vista.pousoEm(x, y),
    lugarEm: (x, y) => vista.lugarEm(x, y),
    get pet() { const p = vista.petDesenhado; if (!p) throw new Error("a cena do mundo ainda nao desenhou o pet"); return p; },
    get bola() { return vista.bolaDesenhada ?? undefined; },
  };
  return () => {
    vivo = false;
    cancelAnimationFrame(pedido); obs.disconnect(); if (esperaKits) clearTimeout(esperaKits); canvas.removeEventListener("webglcontextlost", perdeu);
    soltarControles(); soltarDev(); soltarAbertura(); soltarLivre(); despublicarVista();
    for (const ev of EV_ABERTURA) window.removeEventListener(ev, interromper, { capture: true });
    vista.encerrarAbertura();
    CENA.modo3d = false; CENA.cocoNoChao = false; CENA.ret = null; CENA.medir = null; CENA.mundo = null;
    vista.dispose();
  };
}
