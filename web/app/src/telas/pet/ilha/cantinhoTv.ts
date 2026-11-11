/* O cantinho da TV na ilha (pedido do Matheus, 2026-11-11: "estou gerando uma tv 3d para o jogo, entao gere uma localidade onde o pet
   vai ficar assistindo a tv conosco"; o prototipo P0 do gosto visual, docs/futuro/gosto_visual_pet.md, secao 14). So vista e so com a
   chave `?gosto_visual=1` (gostoVisual/chave.ts): desligada, a vista nem monta o cantinho e a ilha fica a de hoje. Fora do motor, do log
   e do save: a TV le o estado solto que o cartao do P0 escreve (gostoVisual/estadoTv.ts), e o pet que anda ate o cantinho e senta e o
   pet DESENHADO (como na viagem aos lugares, vista.ts): a posicao do motor nao muda.
   - o lugar: um tapete oval, duas almofadas (a do pet e a do dono, vazia) e a TV sobre um movel baixo, em terra, num ponto livre da area
     andavel a sudeste do comedouro (CANTINHO_TV). A decoracao baixa sob o tapete some da vista (Ilha.escondidos, como as clareiras dos
     lugares); um ponto em agua, fora da area, fora do nivel 0 ou com um objeto do motor por perto falha alto;
   - o desenho: geometria three simples no padrao cartoon de 2026-11-10 (formas lisas, cores chapadas, o toon de tres tons de cena.ts),
     como os marcadores dos lugares (marcadoresLugar.ts) e a ponte (ponte.ts);
   - a tela: uma textura dinamica no plano da tela. Com a captura do P0, o video da tela compartilhada (o mesmo elemento que captura.ts ja
     usa para ler o quadro; nada e gravado); com a TV do jogo, um desenho dos programas sinteticos (tvDoJogo.ts) feito do vetor do segundo
     (a cor, o brilho, o movimento, o detalhe e o som mudam a imagem); desligada, a tela escura;
   - o pet: com a TV ligada ele vai ate a almofada (a rota em terra na ilha com agua, rotaConta.ts), senta (sobe a altura da almofada) e
     olha para a TV; as reacoes do P0 aparecem ali: inclina no "curioso", pula de leve no "adorando", vira para o outro lado no "nao curti"
     e no "enjoei", e o balao da reacao fica sobre ele. Desligada, ele volta para onde o motor diz.

   O MODELO DA TV DO MATHEUS (a troca do marcador): o arquivo esperado e `web/app/public/enfeites/tv/tv.gltf` (MODELO_TV, com o .bin e as
   texturas ao lado, como os outros enfeites). O carregador e o carregarVariante dos kits (cena.ts): ele recentra o modelo em x e z, poe a
   base em y = 0 e normaliza a ALTURA para ALTURA_TV (2,2 celulas; o pet tem cerca de 1, e os objetos da ilha sao grandes perto dele), entao a escala e a origem do arquivo nao importam,
   so a proporcao. A FRENTE da TV (a tela) olha para +z do glTF (como os outros modelos da ilha); o cantinho gira a TV para o pet e a camera.
   O modelo e SO a TV: ela fica em cima do movel do cantinho (a ALTURA_MOVEL). A TELA: uma malha com "tela" ou "screen" no nome, com os UVs
   de 0 a 1 cobrindo a tela, recebe a textura dinamica; sem ela, o cantinho poe um plano na face da frente (62 % da largura e 55 % da
   altura da caixa, no meio). Sem o arquivo, fica o marcador cartoon, com um aviso no console (console.warn) e `data-tv-modelo="marcador"`
   na caixa da cena; com ele, `data-tv-modelo="gltf"`. Um arquivo que existe e nao carrega e um erro no console (console.error) e o
   marcador fica.
   Os numeros e as contas sem three ficam em cantinhoTvConta.ts. Todos os numeros (o ponto, os tamanhos, as cores, as poses) sao do
   desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { GEO_SOMBRA, carregarVariante, curvar, materialSombra, toon } from "./cena.ts";
import { ALTURA_MOVEL, ALTURA_TV, CANTINHO_TV, IdaAoCantinho, MODELO_TV, MODELO_TV_TABELA, TELA_PASSO_MS, TELA_PX, poseNoCantinho, pontosDoCantinho,
  prepararChao } from "./cantinhoTvConta.ts";
import { dobrarY, type Dobra } from "./curva.ts";
import type { Ilha } from "./grade.ts";
import type { Ponto } from "./rotaConta.ts";
import type { Suspenso } from "./papel.ts";
import { BALAO, TV } from "../../../gostoVisual/estadoTv.ts";
import type { Sentido } from "../../../gostoVisual/gosto.ts";

export { cantinhoNaVista } from "./cantinhoTvConta.ts";

/* ---------- o desenho (three e canvas) ---------- */

/** as cores chapadas do cantinho. PROPOSTO, SEM FONTE */
const COR = {
  tapete: "#e9846b", borda: "#f6c77c", movel: "#b97d4b", gaveta: "#8e5a33", corpo: "#f08a4b", moldura: "#2f3640",
  botao: "#f6d55c", antena: "#9aa3ab", ponta: "#e2574c", almofada: "#f6c945", almofadaDono: "#5cc2b5", balao: "#fffaf0", tinta: "#2f3640",
} as const;

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

/** a tela desligada: o vidro escuro com um reflexo */
function pintarDesligada(g: CanvasRenderingContext2D, w: number, h: number): void {
  g.fillStyle = "#1f2b31"; g.fillRect(0, 0, w, h);
  g.fillStyle = "rgba(255,255,255,0.08)";
  g.beginPath(); g.moveTo(w * 0.12, 0); g.lineTo(w * 0.4, 0); g.lineTo(w * 0.18, h); g.lineTo(-w * 0.1, h); g.closePath(); g.fill();
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
  agora: number; reduzido: boolean; dobra: Dobra;
  /** o pet chegou e esta sentado na almofada (o balao aparece) */
  sentado: boolean;
  /** a altura do alto do pet desenhado sobre o chao no pe dele (celulas, medida na tela), para o balao ficar sobre a cabeca */
  alturaPet: number;
}

export interface Cantinho {
  grupo: THREE.Group;
  ida: IdaAoCantinho;
  /** a TV do P0 esta ligada (a captura ou a TV do jogo; estadoTv.ts) */
  ligada: () => boolean;
  pontos: ReturnType<typeof pontosDoCantinho>;
  /** a pose do pet sentado (o suspenso do papel, papel.ts) e o ponto para onde ele olha */
  pose: (agora: number, reduzido: boolean) => { suspenso: Suspenso; olharPara: Ponto | null };
  quadro: (q: QuadroCantinho) => void;
  /** troca o marcador pelo modelo do Matheus, se o arquivo existir (MODELO_TV); devolve o que ficou */
  carregarModelo: (base: string) => Promise<"gltf" | "marcador">;
  dispose: () => void;
}

/** monta o cantinho na ilha (a vista so chama com a chave ligada, cantinhoNaVista); confere o chao e esconde a decoracao sob o tapete */
export function montarCantinho(ilha: Ilha, rota: (de: Ponto, para: Ponto) => Ponto[] | null): Cantinho {
  prepararChao(ilha);
  const p = pontosDoCantinho(), T = CANTINHO_TV, grupo = new THREE.Group(), y0 = ilha.altura(p.centro[0], p.centro[1]);
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
  /* o tapete oval com a borda */
  const ovo = new THREE.CylinderGeometry(1, 1, 1, 48);
  const borda = malha(ovo, mat(COR.borda), p.centro[0], y0 + T.tapete.alto * 0.4, p.centro[1], grupo);
  borda.scale.set(T.tapete.larg / 2 + T.tapete.borda, T.tapete.alto * 0.8, T.tapete.prof / 2 + T.tapete.borda);
  const tapete = malha(ovo.clone(), mat(COR.tapete), p.centro[0], y0 + T.tapete.alto * 0.5 + 0.01, p.centro[1], grupo);
  tapete.scale.set(T.tapete.larg / 2, T.tapete.alto, T.tapete.prof / 2);
  /* as almofadas: esferas achatadas */
  const bola = new THREE.SphereGeometry(1, 24, 14), topoTapete = y0 + T.tapete.alto + 0.01;
  const alm = malha(bola, mat(COR.almofada), p.assento[0], topoTapete + T.almofada.alto / 2, p.assento[1], grupo);
  alm.scale.set(T.almofada.raio, T.almofada.alto / 2, T.almofada.raio);
  const almDono = malha(bola.clone(), mat(COR.almofadaDono), p.dono[0], topoTapete + T.almofada.alto / 2, p.dono[1], grupo);
  almDono.scale.set(T.almofada.raioDono, T.almofada.alto / 2, T.almofada.raioDono);
  /* a TV: o movel baixo e, em cima, a caixa arredondada com a tela, os botoes e a antena (a frente em +z, girada para o pet e a camera) */
  const tv = new THREE.Group();
  tv.position.set(p.tv[0], topoTapete, p.tv[1]); tv.rotation.y = T.tv.giro;
  grupo.add(tv);
  malha(new RoundedBoxGeometry(2.1, ALTURA_MOVEL, 1.1, 3, 0.08), mat(COR.movel), 0, ALTURA_MOVEL / 2, 0, tv);
  malha(new RoundedBoxGeometry(1.6, 0.16, 0.04, 2, 0.02), mat(COR.gaveta), 0, ALTURA_MOVEL * 0.5, 0.56, tv);
  const sombra = new THREE.Mesh(GEO_SOMBRA, materialSombra());
  mats.push(sombra.material as THREE.Material);
  sombra.scale.set(2.8, 1, 1.8); sombra.position.set(0, 0.012, 0); sombra.renderOrder = 1; sombra.frustumCulled = false;
  tv.add(sombra);
  /* o marcador da TV (sai quando o modelo do Matheus chega): o corpo tem ALTURA_TV com a antena */
  const marcador = new THREE.Group(), CORPO = { w: 1.95, h: 1.4, d: 1.05 };
  marcador.position.y = ALTURA_MOVEL;
  tv.add(marcador);
  malha(new RoundedBoxGeometry(CORPO.w, CORPO.h, CORPO.d, 4, 0.22), mat(COR.corpo), 0, CORPO.h / 2, 0, marcador);
  malha(new RoundedBoxGeometry(1.42, 1.1, 0.06, 3, 0.07), mat(COR.moldura), -0.2, CORPO.h / 2, CORPO.d / 2, marcador);
  const cil = new THREE.CylinderGeometry(0.1, 0.1, 0.09, 16).rotateX(Math.PI / 2);
  malha(cil, mat(COR.botao), 0.72, CORPO.h * 0.64, CORPO.d / 2 + 0.02, marcador);
  malha(cil.clone(), mat(COR.botao), 0.72, CORPO.h * 0.38, CORPO.d / 2 + 0.02, marcador);
  const haste = ALTURA_TV - CORPO.h - 0.06, matAntena = mat(COR.antena), matPonta = mat(COR.ponta);
  for (const lado of [-1, 1]) {
    const a = lado * 0.42, braco = new THREE.Group();
    braco.position.set(0, CORPO.h - 0.02, 0); braco.rotation.z = a;
    marcador.add(braco);
    malha(new THREE.CylinderGeometry(0.03, 0.03, haste / Math.cos(a), 8), matAntena, 0, haste / Math.cos(a) / 2, 0, braco);
    malha(new THREE.SphereGeometry(0.075, 12, 8), matPonta, 0, haste / Math.cos(a), 0, braco);
  }
  /* a tela: a textura dinamica (o desenho da TV do jogo, ou o video da captura) num plano sem luz */
  const { c: telaC, g: telaG } = canvas2d(TELA_PX[0], TELA_PX[1]);
  const texDesenho = new THREE.CanvasTexture(telaC);
  texDesenho.colorSpace = THREE.SRGBColorSpace;
  texs.push(texDesenho);
  pintarDesligada(telaG, TELA_PX[0], TELA_PX[1]);
  const matTela = curvar(new THREE.MeshBasicMaterial({ map: texDesenho, toneMapped: false }));
  mats.push(matTela);
  const tela = malha(new THREE.PlaneGeometry(1.28, 0.96), matTela, -0.2, CORPO.h / 2, CORPO.d / 2 + 0.035, marcador);
  tela.renderOrder = 1;
  /* o balao da reacao: um sprite sobre o pet sentado (o sprite nao passa pela dobra do shader: a altura dele desconta a dobra, como o papel) */
  const { c: balaoC, g: balaoG } = canvas2d(256, 96);
  const texBalao = new THREE.CanvasTexture(balaoC);
  texBalao.colorSpace = THREE.SRGBColorSpace;
  texs.push(texBalao);
  const matBalao = new THREE.SpriteMaterial({ map: texBalao, depthTest: false, depthWrite: false, fog: false, transparent: true });
  mats.push(matBalao);
  const balao = new THREE.Sprite(matBalao);
  balao.scale.set(1.5, 0.56, 1); balao.renderOrder = 10; balao.visible = false; balao.frustumCulled = false;
  grupo.add(balao);
  let textoBalao = "";
  const desenharBalao = (t: string) => {
    const w = balaoC.width, h = balaoC.height;
    balaoG.clearRect(0, 0, w, h);
    balaoG.fillStyle = COR.balao; balaoG.strokeStyle = COR.tinta; balaoG.lineWidth = 5;
    balaoG.beginPath(); balaoG.roundRect(6, 6, w - 12, h - 30, 22); balaoG.fill(); balaoG.stroke();
    balaoG.beginPath(); balaoG.moveTo(w / 2 - 14, h - 26); balaoG.lineTo(w / 2, h - 6); balaoG.lineTo(w / 2 + 14, h - 26); balaoG.closePath(); balaoG.fill();
    balaoG.beginPath(); balaoG.moveTo(w / 2 - 14, h - 25); balaoG.lineTo(w / 2, h - 6); balaoG.lineTo(w / 2 + 14, h - 25); balaoG.stroke();
    balaoG.fillStyle = COR.tinta; balaoG.font = "bold 34px system-ui, sans-serif"; balaoG.textAlign = "center"; balaoG.textBaseline = "middle";
    balaoG.fillText(t, w / 2, (h - 24) / 2 + 3);
    texBalao.needsUpdate = true;
  };

  let video: HTMLVideoElement | null = null, texVideo: THREE.VideoTexture | null = null, pintadoEm = -1e9, ligadaAntes = false;
  const quadro = (q: QuadroCantinho) => {
    /* a tela: o video da captura, o desenho do programa, ou desligada (pintada uma vez) */
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
      } else if (!TV.ligada && ligadaAntes) { pintarDesligada(telaG, TELA_PX[0], TELA_PX[1]); texDesenho.needsUpdate = true; }
    }
    ligadaAntes = TV.ligada;
    /* o balao: so com o pet sentado e uma reacao */
    const texto = q.sentado && TV.ligada && TV.reacao ? BALAO[TV.reacao] : "";
    if (texto !== textoBalao) { textoBalao = texto; if (texto) desenharBalao(texto); }
    balao.visible = texto !== "";
    if (balao.visible) {
      const [x, z] = p.assento, y = y0 + q.alturaPet + 0.3;
      balao.position.set(x, dobrarY(y, z, q.dobra, x), z);
    }
  };

  const ida = new IdaAoCantinho(p.assento, rota);
  const pose = (agora: number, reduzido: boolean) => {
    const r = poseNoCantinho(TV.reacao, agora, reduzido);
    const olharPara: Ponto | null = r.olhar === "tv" ? p.tv : r.olhar === "fora" ? [2 * p.assento[0] - p.tv[0], 2 * p.assento[1] - p.tv[1]] : null;
    return { suspenso: { naMao: false, altura: r.altura, angulo: r.angulo, tremor: 0, sombra: null }, olharPara };
  };

  const carregarModelo = async (base: string): Promise<"gltf" | "marcador"> => {
    const url = new URL(MODELO_TV, base).href, r = await fetch(url, { method: "HEAD" }), tipo = r.headers.get("content-type") ?? "";
    /* o servidor de desenvolvimento responde a pagina (text/html) para um arquivo que nao existe */
    if (!r.ok || tipo.includes("text/html")) {
      console.warn(`cantinho da TV: o modelo ${MODELO_TV} não existe (HTTP ${r.status}${tipo ? ", " + tipo : ""}); fica o marcador cartoon. ` +
        `Para trocar: ponha o glTF em web/app/public/${MODELO_TV} (frente em +z, a malha da tela com "tela" no nome; a altura vira ${ALTURA_TV} células).`);
      return "marcador";
    }
    const { pecas } = await carregarVariante(new GLTFLoader(), url, MODELO_TV_TABELA);
    const modelo = new THREE.Group(), caixa = new THREE.Box3();
    modelo.position.y = ALTURA_MOVEL;
    let temTela = false;
    for (const pc of pecas) {
      const eTela = /tela|screen/i.test(pc.nome ?? "");
      temTela ||= eTela;
      const m = new THREE.Mesh(pc.geo, eTela ? matTela : pc.mat);
      m.matrixAutoUpdate = false; m.matrix.copy(pc.local); m.frustumCulled = false;
      if (!eTela) mats.push(pc.mat);
      modelo.add(m);
      if (!pc.geo.boundingBox) pc.geo.computeBoundingBox();
      caixa.union(pc.geo.boundingBox!.clone().applyMatrix4(pc.local));
    }
    if (!temTela) {
      /* sem a malha da tela: um plano na face da frente, no meio da caixa */
      const tam = caixa.getSize(new THREE.Vector3());
      malha(new THREE.PlaneGeometry(tam.x * 0.62, tam.y * 0.55), matTela, (caixa.min.x + caixa.max.x) / 2, caixa.min.y + tam.y * 0.5, caixa.max.z + 0.01, modelo).renderOrder = 1;
    }
    tv.remove(marcador);
    tv.add(modelo);
    return "gltf";
  };

  const dispose = () => {
    for (const g of geos) g.dispose();
    for (const m of mats) m.dispose();
    for (const t of texs) t.dispose();
    texVideo?.dispose();
    grupo.clear();
  };
  return { grupo, ida, ligada: () => TV.ligada, pontos: p, pose, quadro, carregarModelo, dispose };
}
