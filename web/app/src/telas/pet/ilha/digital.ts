/* O toque digital do estilo Digital (docs/TAREFA_V3_MAPA_DIGITAL.md, etapa D3): so vista, sobre a mesma grade.
     - as particulas de dados: pequenos cristais ciano flutuando sobre a area e a moldura perto dela, que sobem e descem devagar e giram
       (o movimento e do shader, pelo uTempo da curva: parado com movimento reduzido); mais fortes a noite. Um InstancedMesh so;
     - o portal no ceu (2026-11-11, no lugar da grade pintada, que era parada): os aneis concentricos girando ao norte da ilha, a coluna
       de luz e os arcos grandes em volta da ilha inteira (portalDoCeu); de dia e de noite;
     - os fios entre os postes: cada poste ligado aos vizinhos mais perto (ate DIGITAL.fios.alcance celulas), um fio pendurado (uma
       parabola) do alto de um ao do outro. Uma malha de segmentos so.
   Tudo deterministico (a rng da grade com um sal proprio); as contas ficam em digitalConta.ts, sem DOM. Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { CURVA, curvar } from "./cena.ts";
import { DIGITAL, NUVENS_PINTADAS } from "./constantes.ts";
import { aneisDoPortal, lugaresDasParticulas, segmentosDosFios, type AnelDoPortal } from "./digitalConta.ts";
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

/** uma nuvem de bolhas (o desenho "3d" e o "chapada"): os centros e os raios de `n` bolhas lado a lado, a maior no meio, com a base em y = 0 */
function bolhasDaNuvem(r: () => number, n: number): [number, number, number][] {
  const b: [number, number, number][] = [];
  for (let k = 0; k < n; k++) {
    const t = n === 1 ? 0 : (k / (n - 1)) * 2 - 1, raio = 0.55 + (1 - Math.abs(t)) * 0.55 + r() * 0.15;
    b.push([t * 1.6 + (r() - 0.5) * 0.3, raio * 0.55, raio]);
  }
  return b;
}

/** as nuvens "3d" (NUVENS_PINTADAS.desenho): bolhas de pouco poligono juntas numa malha, com a base cortada reta e dois tons chapados pela altura
    (branco em cima, a sombra azulada na faixa de baixo), sem luz e sem nevoa; o contorno do estilo as desenha como o resto da ilha */
function nuvem3d(r: () => number): THREE.BufferGeometry {
  const N = NUVENS_PINTADAS, n = N.bolhas[0] + Math.floor(r() * (N.bolhas[1] - N.bolhas[0] + 1)), partes: THREE.BufferGeometry[] = [];
  for (const [x, y, raio] of bolhasDaNuvem(r, n)) {
    const g = new THREE.IcosahedronGeometry(raio, 1);
    g.translate(x, y, (r() - 0.5) * 0.4);
    partes.push(g.index ? g.toNonIndexed() : g);
  }
  const geo = mergeGeometries(partes);
  if (!geo) throw new Error("nuvem 3d: as bolhas nao juntaram");
  const pos = geo.getAttribute("position"), cores: number[] = [], branco = new THREE.Color("#ffffff"), sombra = new THREE.Color(N.sombra);
  let topo = 0;
  for (let i = 0; i < pos.count; i++) topo = Math.max(topo, pos.getY(i));
  for (let i = 0; i < pos.count; i += 3) {
    /* a base reta: o que desce abaixo de 0 fica em 0; e o tom do triangulo inteiro pela altura do meio dele (chapado, sem degrade) */
    let ym = 0;
    for (let j = 0; j < 3; j++) { const y = Math.max(0, pos.getY(i + j)); pos.setY(i + j, y); ym += y / 3; }
    const c = ym < topo * N.faixa ? sombra : branco;
    for (let j = 0; j < 3; j++) cores.push(c.r, c.g, c.b);
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(cores, 3));
  geo.computeVertexNormals();
  return geo;
}

/** as nuvens "chapada": o mesmo desenho de bolhas num canvas, branco com a faixa de sombra embaixo e a borda limpa (sem pintura), num quadro */
function nuvemChapada(r: () => number): THREE.CanvasTexture {
  const N = NUVENS_PINTADAS, n = N.bolhas[0] + Math.floor(r() * (N.bolhas[1] - N.bolhas[0] + 1)), b = bolhasDaNuvem(r, n);
  const c = document.createElement("canvas"), W = 512, H = 256, esc = W / 5.2, x0 = W / 2, y0 = H - 24;
  c.width = W; c.height = H;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  const forma = () => { g.beginPath(); for (const [x, y, raio] of b) { g.moveTo(x0 + x * esc + raio * esc, y0 - y * esc); g.arc(x0 + x * esc, y0 - y * esc, raio * esc, 0, Math.PI * 2); } };
  g.fillStyle = "#ffffff"; forma(); g.fill();
  /* a sombra: a faixa de baixo, recortada pela forma; a base reta */
  let topo = H;
  for (const [, y, raio] of b) topo = Math.min(topo, y0 - (y + raio) * esc);
  g.save(); forma(); g.clip();
  g.fillStyle = N.sombra; g.fillRect(0, y0 - (y0 - topo) * N.faixa, W, H);
  g.restore();
  g.clearRect(0, y0, W, H - y0);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** as nuvens do anel no desenho "3d" ou "chapada" (o recorte da pintura fica em nuvensDaPintura): as mesmas posicoes, o mesmo giro */
export function nuvensDesenhadas(grupo: THREE.Group, ilha: Ilha, desenho: "3d" | "chapada", parado: boolean): void {
  const N = NUVENS_PINTADAS, r = rng(29), cx = ilha.x0 + ilha.larg / 2, cz = ilha.z0 + ilha.prof / 2, anel = new THREE.Group();
  anel.position.set(cx, 0, cz);
  for (let i = 0; i < N.n; i++) {
    const tam = N.tam[0] + r() * (N.tam[1] - N.tam[0]);
    let m: THREE.Mesh;
    if (desenho === "3d") {
      m = new THREE.Mesh(nuvem3d(r), new THREE.MeshBasicMaterial({ vertexColors: true, fog: false, transparent: true, opacity: grupo.userData.opacidade ?? 1 }));
      m.scale.setScalar(tam / 5.2);
    } else {
      const geo = new THREE.PlaneGeometry(tam, tam / 2);
      geo.translate(0, tam / 4, 0);
      m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: nuvemChapada(r), fog: false, depthWrite: false, transparent: true, opacity: grupo.userData.opacidade ?? 1 }));
    }
    const ang = (i / N.n) * Math.PI * 2 + (r() - 0.5) * 0.4, raio = N.raio[0] + r() * (N.raio[1] - N.raio[0]);
    m.position.set(Math.sin(ang) * raio, N.altura[0] - N.baixa + r() * (N.altura[1] - N.altura[0]), -Math.cos(ang) * raio);
    m.lookAt(0, m.position.y, 0);
    m.frustumCulled = false;
    anel.add(m);
  }
  grupo.add(anel);
  if (!parado) {
    let antes = performance.now();
    anel.children[0].onBeforeRender = () => { const agora = performance.now(); anel.rotation.y += ((agora - antes) / 1000) * (Math.PI * 2 / N.volta); antes = agora; };
  }
}

/** os fios entre os postes: uma malha de segmentos (digitalConta.ts, segmentosDosFios) */
export function fios(ilha: Ilha): THREE.LineSegments {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(segmentosDosFios(ilha), 3));
  const l = new THREE.LineSegments(g, curvar(new THREE.LineBasicMaterial({ color: DIGITAL.fios.cor })));
  l.frustumCulled = false;
  return l;
}

/** a imagem de um anel do portal: branco no transparente, o circulo quase na borda do quadro; a cor e a opacidade sao do material */
function imagemDoAnel(a: AnelDoPortal, lado: number): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = c.height = lado;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  const m = lado / 2, R = m * 0.94, fino = Math.max(1.5, lado / 340), passo = (Math.PI * 2) / a.partes;
  g.strokeStyle = g.fillStyle = "#ffffff"; g.lineCap = "butt";
  const circulo = (raio: number, largura: number, de = 0, ate = Math.PI * 2) => { g.lineWidth = largura; g.beginPath(); g.arc(m, m, raio, de, ate); g.stroke(); };
  if (a.desenho === "linha") circulo(R, fino * 1.3);
  else if (a.desenho === "dupla") { circulo(R, fino); circulo(R * 0.955, fino * 0.7); }
  else if (a.desenho === "tracos") {
    /* tracos longos e curtos alternados, com vaos */
    for (let k = 0; k < a.partes; k++) circulo(R, fino * 2.2, k * passo, k * passo + passo * (k % 3 === 0 ? 0.82 : 0.4));
    circulo(R * 0.93, fino * 0.6);
  } else if (a.desenho === "marcas") {
    circulo(R * 0.9, fino);
    for (let k = 0; k < a.partes * 2; k++) {
      const ang = k * passo / 2, longo = k % 4 === 0 ? 0.1 : 0.045;
      g.lineWidth = fino; g.beginPath();
      g.moveTo(m + Math.cos(ang) * R * 0.9, m + Math.sin(ang) * R * 0.9); g.lineTo(m + Math.cos(ang) * R * (0.9 + longo), m + Math.sin(ang) * R * (0.9 + longo)); g.stroke();
    }
  } else {
    /* os blocos: quadradinhos de dados sobre a linha, uns cheios e outros so o contorno, com falhas */
    circulo(R * 0.9, fino * 0.6);
    const q = R * 0.07;
    for (let k = 0; k < a.partes; k++) {
      if (k % 5 === 3) continue;
      g.save(); g.translate(m + Math.cos(k * passo) * R * 0.955, m + Math.sin(k * passo) * R * 0.955); g.rotate(k * passo);
      if (k % 2) g.fillRect(-q / 2, -q / 2, q, q); else { g.lineWidth = fino * 0.8; g.strokeRect(-q / 2, -q / 2, q, q); }
      g.restore();
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** o portal no ceu (DIGITAL.portal), no lugar da grade pintada: ao norte da ilha, os aneis concentricos girando cada um para um lado, a
    coluna de luz com aneis deitados em volta, e os arcos grandes que cruzam o ceu em volta da ilha inteira. So vista, sem nevoa e sem
    escrever profundidade; anda pelo uTempo da curva (parado com "reduzir movimento") */
export function portalDoCeu(ilha: Ilha): { grupo: THREE.Group; noite: (n: boolean) => void } {
  const P = DIGITAL.portal, grupo = new THREE.Group(), cx = ilha.x0 + ilha.larg / 2, cz = ilha.z0 + ilha.prof / 2, cor = new THREE.Color(P.cor);
  const materiais: THREE.MeshBasicMaterial[] = [], giram: { o: THREE.Object3D; eixo: "y" | "z"; volta: number; fase: number }[] = [];
  const material = (mapa: THREE.Texture | null, forca = 1) => {
    const m = new THREE.MeshBasicMaterial({ color: cor, map: mapa, transparent: true, opacity: P.opacidade[0] * forca, depthWrite: false, fog: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending });
    m.userData.forca = forca;
    materiais.push(m);
    return m;
  };
  /* os aneis concentricos, de pe, virados para a ilha */
  const portal = new THREE.Group(), aneis = aneisDoPortal();
  portal.position.set(cx, P.altura, cz - P.longe);
  aneis.forEach((a, k) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(a.raio * 2 / 0.94, a.raio * 2 / 0.94), material(imagemDoAnel(a, a.raio > 16 ? 1024 : 512)));
    m.position.z = -k * 0.05;
    portal.add(m);
    giram.push({ o: m, eixo: "z", volta: a.volta, fase: a.fase });
  });
  /* a coluna de luz: dois planos cruzados com o degrade (forte no meio, some para os lados e para cima) */
  const C = P.coluna, cl = document.createElement("canvas");
  cl.width = 64; cl.height = 256;
  const gc = cl.getContext("2d");
  if (!gc) throw new Error("canvas 2d indisponível");
  const lados = gc.createLinearGradient(0, 0, 64, 0);
  lados.addColorStop(0, "rgba(255,255,255,0)"); lados.addColorStop(0.42, "rgba(255,255,255,0.35)"); lados.addColorStop(0.5, "rgba(255,255,255,1)");
  lados.addColorStop(0.58, "rgba(255,255,255,0.35)"); lados.addColorStop(1, "rgba(255,255,255,0)");
  gc.fillStyle = lados; gc.fillRect(0, 0, 64, 256);
  const sobe = gc.createLinearGradient(0, 0, 0, 256);
  sobe.addColorStop(0, "rgba(0,0,0,0)"); sobe.addColorStop(0.35, "rgba(0,0,0,0.8)"); sobe.addColorStop(1, "rgba(0,0,0,1)");
  gc.globalCompositeOperation = "destination-in"; gc.fillStyle = sobe; gc.fillRect(0, 0, 64, 256);
  const luz = new THREE.CanvasTexture(cl);
  luz.colorSpace = THREE.SRGBColorSpace;
  for (const giro of [0, Math.PI / 2]) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(C.largura, C.altura), material(luz, 0.75));
    m.position.y = C.altura / 2 - P.altura; m.rotation.y = giro;
    portal.add(m);
  }
  /* os aneis deitados em volta da coluna, cada vez menores para cima */
  for (let k = 0; k < C.aneis; k++) {
    const u = k / Math.max(1, C.aneis - 1), raio = C.raio[0] + (C.raio[1] - C.raio[0]) * u, a = aneis[(k + 1) % aneis.length];
    const m = new THREE.Mesh(new THREE.PlaneGeometry(raio * 2, raio * 2), material(imagemDoAnel({ ...a, raio, partes: 16 }, 256)));
    m.rotation.x = -Math.PI / 2;
    const eixo = new THREE.Group().add(m);
    eixo.position.y = (u * 0.6 + 0.12) * C.altura - P.altura;
    portal.add(eixo);
    giram.push({ o: eixo, eixo: "y", volta: (k % 2 ? -1 : 1) * (18 + 9 * k), fase: a.fase });
  }
  grupo.add(portal);
  /* os arcos grandes: circulos finos em volta da ilha inteira, inclinados, girando devagar em torno do eixo de pe */
  const A = P.arcos, orbitas = new THREE.Group();
  orbitas.position.set(cx, 0, cz);
  A.inclina.forEach((graus, k) => {
    const m = new THREE.Mesh(new THREE.TorusGeometry(A.raio + k * 3, A.espessura, 5, 220), material(null, 0.8));
    m.rotation.set(THREE.MathUtils.degToRad(graus), 0, 0);
    const eixo = new THREE.Group().add(m);
    orbitas.add(eixo);
    giram.push({ o: eixo, eixo: "y", volta: (k % 2 ? -1 : 1) * A.volta * (1 + k * 0.3), fase: k * 2.1 });
  });
  grupo.add(orbitas);
  grupo.traverse(o => { o.frustumCulled = false; o.renderOrder = -1; });
  let noite = false;
  const quadro = () => {
    const t = CURVA.uTempo.value, pulso = 1 + P.pulso[0] * Math.sin((t * Math.PI * 2) / P.pulso[1]), base = P.opacidade[noite ? 1 : 0] * pulso;
    for (const g of giram) g.o.rotation[g.eixo] = g.fase + (t * Math.PI * 2) / g.volta;
    for (const m of materiais) m.opacity = base * (m.userData.forca as number);
  };
  (portal.children[0] as THREE.Mesh).onBeforeRender = quadro;
  quadro();
  return { grupo, noite: n => { noite = n; } };
}
