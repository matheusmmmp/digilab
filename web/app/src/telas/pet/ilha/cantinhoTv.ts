/* O cantinho da TV na ilha (pedido do Matheus, 2026-11-11: "estou gerando uma tv 3d para o jogo, entao gere uma localidade onde o pet
   vai ficar assistindo a tv conosco"; o prototipo P0 do gosto visual, docs/futuro/gosto_visual_pet.md, secao 14). So vista e so com a
   chave `?gosto_visual=1` (gostoVisual/chave.ts): desligada, a vista nem monta o cantinho e a ilha fica a do #814. Fora do motor, do log
   e do save: a tela le o estado solto que o cartao do P0 escreve (gostoVisual/estadoTv.ts), e o pet que anda ate o cantinho e senta e o
   pet DESENHADO (como na viagem aos lugares, vista.ts): a posicao do motor nao muda.
   - a TV e a de tubo do #814 (MUNDO_ENFEITES: o enfeite "tv", public/enfeites/tv/tv.gltf, posto pela grade como um marco perto da barraca,
     e desenhado por enfeites.ts): o cantinho nao cria outra TV nem mexe nela. Em volta dela, na frente da tela, um tapete oval e duas
     almofadas (a do pet e a do dono, vazia), em terra plana da area (cantinhoTvConta.ts, pontosDoCantinho). A decoracao baixa sob o
     tapete some da vista;
   - o desenho do tapete e das almofadas: geometria three simples no padrao cartoon de 2026-11-10 (formas lisas, cores chapadas, o toon de
     tres tons de cena.ts), como os marcadores dos lugares (marcadoresLugar.ts) e a ponte (ponte.ts);
   - a tela: com a TV do P0 ligada, uma textura dinamica num plano de cantos arredondados um fio a frente da peca "tela" do modelo (a medida
     de docs/objetos3d/cartoon/tv.py, TELA_DO_MODELO; o plano passa pela mesma normalizacao do carregarVariante e pelo mesmo ponto e giro
     do enfeite). Com a captura, o video da tela compartilhada (o mesmo elemento que captura.ts ja usa para ler o quadro; nada e gravado);
     com a TV do jogo, um desenho dos programas sinteticos (tvDoJogo.ts) feito do vetor do segundo (a cor, o brilho, o movimento, o detalhe
     e o som mudam a imagem). Desligada, o plano some e fica o vidro pintado do modelo, como no #814. Se o modelo nao carrega aqui, o erro
     vai ao console e o cantinho fica sem a tela (a TV em si e a do enfeites.ts, que falha alto do jeito dela);
   - o pet: com a TV ligada ele vai ate a almofada (a rota em terra na ilha com agua, rotaConta.ts), senta (sobe a altura da almofada) e
     olha para a TV; as reacoes do P0 aparecem ali: inclina no "curioso", pula de leve no "adorando", vira para o outro lado no "nao curti"
     e no "enjoei". O sinal da reacao e um icone no lugar dos emotes do jogo (gostoVisual/sinalTv.ts; o PalcoPet pinta): o balao de texto
     em 3D saiu na etapa 2 do PLANO_UX_GOSTO_VISUAL (a UX-GV-10). Desligada, ele volta para onde o motor diz;
   - o toque e a camera (a etapa 2): `caixa` e a caixa da TV no mundo, para a vista dizer se um ponto da tela cai nela (o toque na TV abre o
     painel, a UX-GV-2); `centro` e o meio do cantinho, para onde a camera olha com o painel da TV aberto (`painelAberto`).
   Os numeros e as contas sem three ficam em cantinhoTvConta.ts. Todos os numeros (os tamanhos, as cores, as poses) sao do desenho:
   PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { carregarVariante, curvar, toon } from "./cena.ts";
import { CAIXA_TV, CANTINHO_TV, IdaAoCantinho, TELA_DO_MODELO, TELA_PASSO_MS, TELA_PX, poseNoCantinho, pontosDoCantinho, prepararChao,
  type PontosCantinho } from "./cantinhoTvConta.ts";
import type { Ilha } from "./grade.ts";
import { ENFEITES_MODELOS } from "./modelos.ts";
import type { Ponto } from "./rotaConta.ts";
import type { Suspenso } from "./papel.ts";
import { TV } from "../../../gostoVisual/estadoTv.ts";
import { painelTvAberto } from "../../../gostoVisual/painelTvEstado.ts";
import { marcarSentadoNaTv } from "../../../gostoVisual/sinalTv.ts";
import type { Sentido } from "../../../gostoVisual/gosto.ts";

export { cantinhoNaVista } from "./cantinhoTvConta.ts";

/* ---------- o desenho (three e canvas) ---------- */

/** as cores chapadas do cantinho (o tapete azul, para nao sumir sob a casca laranja da TV). PROPOSTO, SEM FONTE */
const COR = { tapete: "#6fb3c4", borda: "#f6e2b3", almofada: "#f6c945", almofadaDono: "#e9846b" } as const;

/** um numero de 0 a 359 do nome do programa (o tom de partida do desenho dele) */
function tomDoTexto(t: string): number {
  let h = 0;
  for (let i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) % 360;
  return h;
}

/** o desenho da TV do jogo num instante: o fundo pela cor e pelo brilho, as formas pelo detalhe (quantas) e pelo movimento (quao rapido),
    as barras do som pelo volume e pelo ritmo, e as linhas de varredura da TV antiga. Sem o sentido ainda, um fundo calmo */
export function pintarPrograma(g: CanvasRenderingContext2D, w: number, h: number, s: Sentido | null, programa: string | null, t: number): void {
  const v = s?.visao ?? { cor: 0.3, brilho: 0.35, movimento: 0.15, complexidade: 0.2 };
  const tom = (tomDoTexto(programa ?? "") + t * 18 * (0.2 + v.movimento)) % 360, sat = Math.round(v.cor * 90), luz = Math.round(12 + v.brilho * 55);
  g.fillStyle = `hsl(${tom.toFixed(1)} ${sat}% ${luz}%)`;
  g.fillRect(0, 0, w, h);
  const n = 2 + Math.round(v.complexidade * 14), vel = 0.3 + v.movimento * 2.4;
  for (let i = 0; i < n; i++) {
    const fase = i * 2.399, x = w * (0.5 + 0.42 * Math.sin(t * vel * (1 + (i % 3) * 0.3) + fase)), y = h * (0.5 + 0.36 * Math.cos(t * vel * 0.8 + fase * 1.3));
    const r = ((h * 0.24) / (1 + v.complexidade * 2)) * (0.6 + 0.4 * (((i * 37) % 10) / 10));
    g.fillStyle = `hsl(${((tom + 40 + i * 47) % 360).toFixed(1)} ${Math.min(100, sat + 10)}% ${Math.min(90, luz + 18)}%)`;
    if (i % 2) { g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); } else g.fillRect(x - r, y - r * 0.7, r * 2, r * 1.4);
  }
  if (s?.som) {
    const nb = 8, lb = w / nb;
    g.fillStyle = "rgba(255,255,255,0.55)";
    for (let k = 0; k < nb; k++) {
      const a = h * 0.3 * s.som.volume * (0.35 + 0.65 * Math.abs(Math.sin(t * (2 + s.som.variacao * 9) + k * 1.7)));
      g.fillRect(k * lb + lb * 0.2, h - a, lb * 0.6, a);
    }
  }
  g.fillStyle = "rgba(0,0,0,0.13)";
  for (let y = 0; y < h; y += 3) g.fillRect(0, y, w, 1);
}

function canvas2d(w: number, h: number): { c: HTMLCanvasElement; g: CanvasRenderingContext2D } {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível para a tela da TV do cantinho");
  return { c, g };
}

/** o que a vista passa ao cantinho a cada quadro */
export interface QuadroCantinho {
  agora: number; reduzido: boolean;
  /** o pet chegou e esta sentado na almofada (o sinal da reacao aparece; gostoVisual/sinalTv.ts) */
  sentado: boolean;
}

export interface Cantinho {
  grupo: THREE.Group;
  ida: IdaAoCantinho;
  /** a TV do P0 esta ligada (a captura ou a TV do jogo; estadoTv.ts) */
  ligada: () => boolean;
  pontos: PontosCantinho;
  /** a caixa da TV no mundo (celulas; o chao no pe dela e a altura do modelo), para o toque na TV */
  caixa: { min: readonly [number, number, number]; max: readonly [number, number, number] };
  /** o meio do cantinho (celulas): para onde a camera olha com o painel da TV aberto */
  centro: Ponto;
  /** o painel da TV esta aberto (gostoVisual/painelTvEstado.ts) */
  painelAberto: () => boolean;
  /** a pose do pet sentado (o suspenso do papel, papel.ts) e o ponto para onde ele olha */
  pose: (agora: number, reduzido: boolean) => { suspenso: Suspenso; olharPara: Ponto | null };
  quadro: (q: QuadroCantinho) => void;
  /** poe o plano da tela na TV do #814: carrega o mesmo glTF pelo carregarVariante, para o plano seguir a mesma normalizacao */
  carregarTela: (base: string) => Promise<void>;
  dispose: () => void;
}

/** a mascara da tela: um retangulo de cantos arredondados (o vidro da TV de tubo), branco no fundo preto */
function mascaraTela(): THREE.CanvasTexture {
  const { c, g } = canvas2d(64, 48);
  g.fillStyle = "#000"; g.fillRect(0, 0, 64, 48);
  g.fillStyle = "#fff"; g.beginPath(); g.roundRect(1, 1, 62, 46, 14); g.fill();
  return new THREE.CanvasTexture(c);
}

/** monta o cantinho em volta da TV da ilha (a vista so chama com a chave ligada, cantinhoNaVista); esconde a decoracao sob o tapete */
export function montarCantinho(ilha: Ilha, rota: (de: Ponto, para: Ponto) => Ponto[] | null): Cantinho {
  const p = pontosDoCantinho(ilha), T = CANTINHO_TV, grupo = new THREE.Group(), y0 = ilha.altura(p.assento[0], p.assento[1]);
  prepararChao(ilha, p);
  grupo.name = "cantinho-tv";
  const geos: THREE.BufferGeometry[] = [], mats: THREE.Material[] = [], texs: THREE.Texture[] = [];
  const mat = (cor: string): THREE.Material => { const m = toon({ color: new THREE.Color(cor) }); mats.push(m); return m; };
  const malha = (geo: THREE.BufferGeometry, m: THREE.Material, x: number, y: number, z: number, pai: THREE.Object3D): THREE.Mesh => {
    geos.push(geo);
    const o = new THREE.Mesh(geo, m);
    o.position.set(x, y, z);
    o.frustumCulled = false;     // a dobra muda onde a peca aparece; o volume do three nao sabe disso
    pai.add(o);
    return o;
  };
  /* o tapete oval com a borda, girado com a TV (a largura ao longo do lado dela) */
  const ovo = new THREE.CylinderGeometry(1, 1, 1, 48);
  const borda = malha(ovo, mat(COR.borda), p.tapete[0], y0 + T.tapete.alto * 0.4, p.tapete[1], grupo);
  borda.scale.set(T.tapete.larg / 2 + T.tapete.borda, T.tapete.alto * 0.8, T.tapete.prof / 2 + T.tapete.borda); borda.rotation.y = p.giro;
  const tapete = malha(ovo.clone(), mat(COR.tapete), p.tapete[0], y0 + T.tapete.alto * 0.5 + 0.01, p.tapete[1], grupo);
  tapete.scale.set(T.tapete.larg / 2, T.tapete.alto, T.tapete.prof / 2); tapete.rotation.y = p.giro;
  /* as almofadas: esferas achatadas */
  const bola = new THREE.SphereGeometry(1, 24, 14), topoTapete = y0 + T.tapete.alto + 0.01;
  const alm = malha(bola, mat(COR.almofada), p.assento[0], topoTapete + T.almofada.alto / 2, p.assento[1], grupo);
  alm.scale.set(T.almofada.raio, T.almofada.alto / 2, T.almofada.raio);
  const almDono = malha(bola.clone(), mat(COR.almofadaDono), p.dono[0], topoTapete + T.almofada.alto / 2, p.dono[1], grupo);
  almDono.scale.set(T.almofada.raioDono, T.almofada.alto / 2, T.almofada.raioDono);
  /* a tela: a textura dinamica (o desenho da TV do jogo, ou o video da captura) num plano sem luz, que entra quando o glTF da TV chega */
  const { c: telaC, g: telaG } = canvas2d(TELA_PX[0], TELA_PX[1]);
  const texDesenho = new THREE.CanvasTexture(telaC), mascara = mascaraTela();
  texDesenho.colorSpace = THREE.SRGBColorSpace;
  texs.push(texDesenho, mascara);
  const matTela = curvar(new THREE.MeshBasicMaterial({ map: texDesenho, alphaMap: mascara, alphaTest: 0.5, toneMapped: false }));
  mats.push(matTela);
  let tela: THREE.Mesh | null = null;
  let video: HTMLVideoElement | null = null, texVideo: THREE.VideoTexture | null = null, pintadoEm = -1e9;
  const quadro = (q: QuadroCantinho) => {
    /* a tela: o video da captura ou o desenho do programa */
    if (TV.ligada && TV.origem === "tela" && TV.video) {
      if (video !== TV.video) { texVideo?.dispose(); video = TV.video; texVideo = new THREE.VideoTexture(video); texVideo.colorSpace = THREE.SRGBColorSpace; }
      if (matTela.map !== texVideo) { matTela.map = texVideo; matTela.needsUpdate = true; }
    } else {
      if (texVideo) { texVideo.dispose(); texVideo = null; video = null; }
      if (matTela.map !== texDesenho) { matTela.map = texDesenho; matTela.needsUpdate = true; }
      if (TV.ligada && q.agora - pintadoEm >= TELA_PASSO_MS) {
        /* com "reduzir movimento", o desenho muda so a cada segundo sentido, sem as formas andarem */
        pintarPrograma(telaG, TELA_PX[0], TELA_PX[1], TV.sentido, TV.programa, q.reduzido ? 0 : q.agora / 1000);
        texDesenho.needsUpdate = true; pintadoEm = q.agora;
      }
    }
    /* desligada, o plano some e fica o vidro pintado do modelo (o #814) */
    if (tela) tela.visible = TV.ligada;
    marcarSentadoNaTv(q.sentado && TV.ligada);
  };

  const ida = new IdaAoCantinho(p.assento, rota);
  const pose = (agora: number, reduzido: boolean) => {
    const r = poseNoCantinho(TV.reacao, agora, reduzido);
    const olharPara: Ponto | null = r.olhar === "tv" ? p.tv : r.olhar === "fora" ? [2 * p.assento[0] - p.tv[0], 2 * p.assento[1] - p.tv[1]] : null;
    return { suspenso: { naMao: false, altura: r.altura, angulo: r.angulo, tremor: 0, sombra: null }, olharPara };
  };

  const carregarTela = async (base: string): Promise<void> => {
    const m = ENFEITES_MODELOS.tv, { pecas } = await carregarVariante(new GLTFLoader(), new URL("enfeites/" + m.arquivos[0], base).href, m);
    if (pecas.length !== 1) throw new Error(`a TV do #814 tem ${pecas.length} malhas; o cantinho espera uma (a tela pintada nela)`);
    /* so a matriz da normalizacao interessa; a TV desenhada e a do enfeites.ts (o material toon desta copia sai na hora) */
    for (const pc of pecas) pc.mat.dispose();
    /* a mesma matriz do enfeite (enfeites.ts: o ponto, a altura do chao e o giro da grade; a TV nao tem lado de lampada) vezes a da normalizacao */
    const M = new THREE.Matrix4().compose(new THREE.Vector3(p.tv[0], ilha.altura(p.tv[0], p.tv[1]), p.tv[1]),
      new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), p.giro), new THREE.Vector3(1, 1, 1)).multiply(pecas[0]!.local);
    const S = TELA_DO_MODELO, geo = new THREE.PlaneGeometry(2 * S.rx, 2 * S.ry).translate(S.x, S.y, S.z + S.folga);
    geos.push(geo);
    tela = new THREE.Mesh(geo, matTela);
    tela.matrixAutoUpdate = false; tela.matrix.copy(M); tela.frustumCulled = false; tela.visible = TV.ligada; tela.renderOrder = 1;
    grupo.add(tela);
  };

  const dispose = () => {
    marcarSentadoNaTv(false);
    for (const g of geos) g.dispose();
    for (const m of mats) m.dispose();
    for (const t of texs) t.dispose();
    texVideo?.dispose();
    grupo.clear();
  };
  const yTv = ilha.altura(p.tv[0], p.tv[1]), R = CAIXA_TV.raio;
  const caixa = { min: [p.tv[0] - R, yTv, p.tv[1] - R], max: [p.tv[0] + R, yTv + ENFEITES_MODELOS.tv.altura, p.tv[1] + R] } as const;
  const centro: Ponto = [(p.tv[0] + p.assento[0]) / 2, (p.tv[1] + p.assento[1]) / 2];
  return { grupo, ida, ligada: () => TV.ligada && TV.petVai, pontos: p, caixa, centro, painelAberto: painelTvAberto, pose, quadro, carregarTela, dispose };
}
