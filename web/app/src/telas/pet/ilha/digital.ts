/* O toque digital do estilo Digital (docs/TAREFA_V3_MAPA_DIGITAL.md, etapa D3): so vista, sobre a mesma grade.
     - as particulas de dados: pequenos cristais ciano flutuando sobre a area e a moldura perto dela, que sobem e descem devagar e giram
       (o movimento e do shader, pelo uTempo da curva: parado com movimento reduzido); mais fortes a noite. Um InstancedMesh so;
     - a grade no ceu: linhas ciano fracas, desenhadas por cima do ceu pintado (meridianos que saem de um ponto de fuga acima da imagem e
       arcos em volta dele), so de dia; a noite fica o degrade de sempre;
     - os fios entre os postes: cada poste ligado aos vizinhos mais perto (ate DIGITAL.fios.alcance celulas), um fio pendurado (uma
       parabola) do alto de um ao do outro. Uma malha de segmentos so.
   Tudo deterministico (a rng da grade com um sal proprio); as contas ficam em digitalConta.ts, sem DOM. Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { carregarVariante, curvar } from "./cena.ts";
import { DIGITAL, NUVENS_PINTADAS } from "./constantes.ts";
import { lugarDaLata, lugaresDasParticulas, segmentosDosFios } from "./digitalConta.ts";
import { rng, type Ilha } from "./grade.ts";

/** as particulas, e o que a vista chama quando a noite muda */
export function particulas(ilha: Ilha): { malha: THREE.InstancedMesh; noite: (n: boolean) => void } {
  const P = DIGITAL.particulas;
  const mat = curvar(new THREE.MeshBasicMaterial({
    color: new THREE.Color(P.cor), transparent: true, opacity: P.opacidade[0], depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
  }), 0, {
    nome: "particula",
    glsl: `
#ifdef USE_INSTANCING
  vec3 baseP = instanceMatrix[3].xyz;
#else
  vec3 baseP = vec3(0.0);
#endif
float faseP = baseP.x * 1.7 + baseP.z * 0.9;
float giroP = uTempo * ${P.giro.toFixed(2)} + faseP;
transformed.xz = mat2(cos(giroP), -sin(giroP), sin(giroP), cos(giroP)) * transformed.xz;
transformed.y += sin(uTempo * ${P.vel.toFixed(2)} + faseP) * ${P.sobe.toFixed(2)};`,
  });
  const lugares = lugaresDasParticulas(ilha), malha = new THREE.InstancedMesh(new THREE.OctahedronGeometry(P.tamanho, 0), mat, lugares.length);
  const m = new THREE.Matrix4();
  lugares.forEach(([x, y, z], i) => malha.setMatrixAt(i, m.makeTranslation(x, y, z)));
  malha.frustumCulled = false;
  malha.renderOrder = 3;
  return { malha, noite: noite => { mat.opacity = P.opacidade[noite ? 1 : 0]; } };
}

/** o ceu em pixel (CEU_SEM_PINTURA, modo "pixel"): o degrade das tres cores em faixas chapadas, como o ceu de um jogo em pixel; o canvas e
    pequeno e a textura amplia sem filtro */
export function ceuEmFaixas(cores: readonly string[], faixas: number, w: number, h: number): HTMLCanvasElement {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  const liso = g.createLinearGradient(0, 0, 0, h);
  liso.addColorStop(0, cores[0]); liso.addColorStop(0.55, cores[1]); liso.addColorStop(1, cores[2]);
  g.fillStyle = liso; g.fillRect(0, 0, w, h);
  /* cada faixa pega a cor do meio dela: o degrade vira degraus */
  const px = g.getImageData(0, 0, 1, h).data;
  for (let k = 0; k < faixas; k++) {
    const y0 = Math.round((k / faixas) * h), y1 = Math.round(((k + 1) / faixas) * h), m = Math.min(h - 1, Math.floor((y0 + y1) / 2)) * 4;
    g.fillStyle = `rgb(${px[m]},${px[m + 1]},${px[m + 2]})`; g.fillRect(0, y0, w, y1 - y0);
  }
  return c;
}

/** o ceu pintado com o azul suavizado (CEU_SEM_PINTURA.pintura): cada pixel perde parte da saturacao (vai para o cinza da propria luminancia) e
    puxa um pouco para o branco */
export function suavizarPintura(img: HTMLImageElement | ImageBitmap | HTMLCanvasElement, saturacao: number, clarear: number): HTMLCanvasElement {
  const c = document.createElement("canvas");
  c.width = img.width; c.height = img.height;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  g.drawImage(img, 0, 0);
  const dados = g.getImageData(0, 0, c.width, c.height), d = dados.data;
  for (let k = 0; k < d.length; k += 4) {
    const l = 0.2126 * d[k] + 0.7152 * d[k + 1] + 0.0722 * d[k + 2];
    for (let i = 0; i < 3; i++) d[k + i] = Math.round((l + (d[k + i] - l) * saturacao) * (1 - clarear) + 255 * clarear);
  }
  g.putImageData(dados, 0, 0);
  return c;
}

/** o ceu pintado em duas partes (NUVENS_PINTADAS): `ceu`, o degrade sem nuvens (cada linha com a cor do ceu dela: a do pixel mais saturado da linha,
    suavizada entre as linhas), e `nuvens`, so as nuvens, com o alfa pela saturacao (a nuvem e branca, o ceu e azul) e a cor sem o ceu misturado na
    borda */
export function separarNuvens(img: HTMLImageElement | ImageBitmap | HTMLCanvasElement): { ceu: HTMLCanvasElement; nuvens: HTMLCanvasElement } {
  const w = img.width, h = img.height, N = NUVENS_PINTADAS;
  const fonte = document.createElement("canvas");
  fonte.width = w; fonte.height = h;
  const gf = fonte.getContext("2d");
  if (!gf) throw new Error("canvas 2d indisponível");
  gf.drawImage(img, 0, 0);
  const d = gf.getImageData(0, 0, w, h).data, sat = (k: number) => { const mx = Math.max(d[k], d[k + 1], d[k + 2]); return mx ? (mx - Math.min(d[k], d[k + 1], d[k + 2])) / mx : 0; };
  /* a cor do ceu de cada linha: o pixel mais saturado; depois a media de 31 linhas, para nenhuma linha toda de nuvem estragar o degrade */
  const bruta: [number, number, number][] = [];
  for (let y = 0; y < h; y++) {
    let melhor = -1, km = 0;
    for (let x = 0; x < w; x++) { const k = (y * w + x) * 4, s = sat(k); if (s > melhor) { melhor = s; km = k; } }
    bruta.push([d[km], d[km + 1], d[km + 2]]);
  }
  const linha = bruta.map((_, y) => {
    const a = Math.max(0, y - 15), b = Math.min(h - 1, y + 15), soma = [0, 0, 0];
    for (let i = a; i <= b; i++) for (let c = 0; c < 3; c++) soma[c] += bruta[i][c];
    return soma.map(v => v / (b - a + 1));
  });
  const ceu = document.createElement("canvas"), nuvens = document.createElement("canvas");
  ceu.width = nuvens.width = w; ceu.height = nuvens.height = h;
  const gc = ceu.getContext("2d"), gn = nuvens.getContext("2d");
  if (!gc || !gn) throw new Error("canvas 2d indisponível");
  for (let y = 0; y < h; y++) { const [r, g, b] = linha[y]; gc.fillStyle = `rgb(${r | 0},${g | 0},${b | 0})`; gc.fillRect(0, y, w, 1); }
  const saida = gn.createImageData(w, h), o = saida.data;
  for (let y = 0; y < h; y++) {
    const [r, g, b] = linha[y], mx = Math.max(r, g, b), sCeu = mx ? (mx - Math.min(r, g, b)) / mx : 1;
    for (let x = 0; x < w; x++) {
      const k = (y * w + x) * 4, f = sat(k) / (sCeu || 1);
      const a = Math.min(1, Math.max(0, (1 - f - N.nuvem) / N.borda + 1));
      if (a <= 0) continue;
      /* tira o ceu da cor da borda: c = (p - (1 - a) ceu) / a */
      const cor = [r, g, b];
      for (let c = 0; c < 3; c++) o[k + c] = Math.min(255, Math.max(0, Math.round((d[k + c] - (1 - a) * cor[c]) / a)));
      o[k + 3] = Math.round(a * 255);
    }
  }
  gn.putImageData(saida, 0, 0);
  return { ceu, nuvens };
}

/** as nuvens da pintura no mundo (NUVENS_PINTADAS): os pedacos recortados num anel em volta da ilha, virados para o centro, sem nevoa; o anel gira
    devagar. Entram no `grupo` (o da cena, que a noite apaga como as outras nuvens) quando a imagem chega */
export function nuvensDaPintura(grupo: THREE.Group, nuvens: HTMLCanvasElement, ilha: Ilha, parado: boolean): void {
  const N = NUVENS_PINTADAS, r = rng(23), cx = ilha.x0 + ilha.larg / 2, cz = ilha.z0 + ilha.prof / 2;
  const anel = new THREE.Group();
  anel.position.set(cx, 0, cz);
  const texturas = N.pedacos.map(([x, y, w, h]) => {
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    const g = c.getContext("2d");
    if (!g) throw new Error("canvas 2d indisponível");
    g.drawImage(nuvens, x, y, w, h, 0, 0, w, h);
    /* as bordas do recorte somem aos poucos (`esfumar`, a fracao do lado), para o pedaco nao ficar com cara de retangulo */
    g.globalCompositeOperation = "destination-in";
    for (const [x0, y0, x1, y1] of [[0, 0, w, 0], [0, 0, 0, h]] as const) {
      const m = g.createLinearGradient(x0, y0, x1, y1), f = N.esfumar;
      m.addColorStop(0, "rgba(0,0,0,0)"); m.addColorStop(f, "rgba(0,0,0,1)"); m.addColorStop(1 - f, "rgba(0,0,0,1)"); m.addColorStop(1, "rgba(0,0,0,0)");
      g.fillStyle = m; g.fillRect(0, 0, w, h);
    }
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return { t, w, h };
  });
  for (let i = 0; i < N.n; i++) {
    const { t, w, h } = texturas[i % texturas.length], e = N.escala * (0.8 + r() * 0.4);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w * e, h * e), new THREE.MeshBasicMaterial({ map: t, fog: false, depthWrite: false, transparent: true, opacity: grupo.userData.opacidade ?? 1 }));
    const ang = (i / N.n) * Math.PI * 2 + (r() - 0.5) * 0.4, raio = N.raio[0] + r() * (N.raio[1] - N.raio[0]);
    m.position.set(Math.sin(ang) * raio, N.altura[0] + r() * (N.altura[1] - N.altura[0]), -Math.cos(ang) * raio);
    m.lookAt(0, m.position.y, 0);
    if (r() < 0.5) m.scale.x = -1;
    m.frustumCulled = false;
    anel.add(m);
  }
  grupo.add(anel);
  if (!parado) {
    let antes = performance.now();
    anel.children[0].onBeforeRender = () => { const agora = performance.now(); anel.rotation.y += ((agora - antes) / 1000) * (Math.PI * 2 / N.volta); antes = agora; };
  }
}

/** o ceu com a grade digital por cima: um canvas desenhado sobre a imagem (a pintada ou a das faixas), que vira a imagem da textura do ceu.
    A grade cobre o ceu todo e fica mais fraca no alto (DIGITAL.grade.topo) */
export function ceuComGrade(img: HTMLImageElement | ImageBitmap | HTMLCanvasElement): HTMLCanvasElement {
  const G = DIGITAL.grade, c = document.createElement("canvas");
  c.width = img.width; c.height = img.height;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  g.imageSmoothingEnabled = false;
  g.drawImage(img, 0, 0);
  /* as linhas num canvas a parte, apagadas para cima por uma mascara, e so depois sobre o ceu */
  const l = document.createElement("canvas");
  l.width = c.width; l.height = c.height;
  const gl = l.getContext("2d");
  if (!gl) throw new Error("canvas 2d indisponível");
  const w = c.width, h = c.height, cx = w / 2, cy = -h * G.fuga;
  /* a espessura vale para a imagem pintada (1376 px de largura); num ceu menor, proporcional, com pelo menos 1 px */
  gl.strokeStyle = G.cor; gl.lineWidth = Math.max(1, G.espessura * (w / 1376));
  /* os meridianos: do ponto de fuga (acima da imagem) para baixo, em leque */
  for (let k = -G.meridianos; k <= G.meridianos; k++) {
    gl.beginPath(); gl.moveTo(cx, cy); gl.lineTo(cx + k * (w / G.meridianos) * 1.4, h); gl.stroke();
  }
  /* os paralelos: arcos em volta do ponto de fuga, mais juntos perto dele */
  for (let k = 1; k <= G.paralelos; k++) {
    const raio = (h - cy) * Math.pow(k / G.paralelos, 1.6);
    gl.beginPath(); gl.arc(cx, cy, raio, 0, Math.PI); gl.stroke();
  }
  const mascara = gl.createLinearGradient(0, 0, 0, h);
  mascara.addColorStop(0, `rgba(0,0,0,${G.topo})`); mascara.addColorStop(1, "rgba(0,0,0,1)");
  gl.globalCompositeOperation = "destination-in"; gl.fillStyle = mascara; gl.fillRect(0, 0, w, h);
  g.globalAlpha = G.alfa; g.drawImage(l, 0, 0);
  return c;
}

/** a lata gigante (D4): o glTF de public/mapa_digital/lata/ (gerado pela Meshy, License.txt ao lado), na altura de DIGITAL.lata, sem sombra
    no chao; o `quadro` a poe no horizonte a cada quadro, pelo foco da camera (digitalConta.ts, lugarDaLata) */
export async function lata(ilha: Ilha, base: string):
    Promise<{ grupo: THREE.Group; quadro: (foco: readonly [number, number], dobra: number, dir: readonly [number, number], meiaLargura: number) => void }> {
  const L = DIGITAL.lata, { pecas } = await carregarVariante(new GLTFLoader(), new URL(L.arquivo, base).href,
    { arquivos: [L.arquivo], altura: L.altura, vento: 0, sombra: 0, baixo: false });
  const grupo = new THREE.Group();
  for (const p of pecas) {
    const m = new THREE.Mesh(p.geo, p.mat);
    (p.mat as THREE.MeshToonMaterial).fog = false;   /* longe, a nevoa do estilo a apagaria; o marco fica com as cores da maquete */
    m.matrixAutoUpdate = false;
    m.matrix.copy(p.local);
    m.frustumCulled = false;   /* o mundo curvo desce o que esta longe no shader: a caixa da malha nao vale */
    grupo.add(m);
  }
  grupo.rotation.y = L.giro;
  return {
    grupo,
    quadro: (foco, dobra, dir, meiaLargura) => { const { x, y, z } = lugarDaLata(ilha, foco, dobra, dir, meiaLargura); grupo.position.set(x, y, z); },
  };
}

/** os fios entre os postes: uma malha de segmentos (digitalConta.ts, segmentosDosFios) */
export function fios(ilha: Ilha): THREE.LineSegments {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(segmentosDosFios(ilha), 3));
  const l = new THREE.LineSegments(g, curvar(new THREE.LineBasicMaterial({ color: DIGITAL.fios.cor })));
  l.frustumCulled = false;
  return l;
}
