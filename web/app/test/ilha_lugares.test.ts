/* Onde ficam os lugares na ilha (docs/TAREFA_V3_LUGARES_3D.md, secao 12; grade.ts, porLugares). LG-G1: um de cada, fora da area andavel.
   LG-G2: o portao e a barraca em grama plana ao norte, a distancia combinada da area, longe dos enfeites e um do outro, com a frente para a
   area. LG-G3: o cais na ultima linha de areia antes do mar, de frente para o norte. LG-G4: a clareira so esconde a decoracao (nunca uma
   arvore do motor) e so dentro do raio; os objetos em si nao mudam (o E-G0 de test/ilha_enfeites.test.ts confere contra o gabarito).
   LG-G5: a paleta da Ilha (docs/lugares3d/estilo_ilha.py) e a da textura publicada; LG-G5b, no lugar dele para os lugares com a textura
   pintada (TEXTURA_PINTADA): o detalhe guardado e o chao de dentro escuro.
   LG-G6: o toque nos lugares (ToqueLugar.tsx; secao 13): o retangulo projetado da caixa de cada lugar (lugarNoPonto) e o gesto, que abre
   o destino do lugar aberto e nada mais (o cais trancado, o arrasto, o toque longo, o sprite do pet, o painel por cima). */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { inflateSync } from "node:zlib";
import * as THREE from "three";
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import type { Destino } from "../src/rotas.ts";
import { CENA } from "../src/telas/pet/cenaEstado.ts";
import { LUGARES_GRADE } from "../src/telas/pet/ilha/constantes.ts";
import { LUGAR_ABERTO, LUGAR_DESTINO, NOMES_LUGARES } from "../src/telas/pet/lugaresIlha.ts";
import { lugarNoPonto } from "../src/telas/pet/ilha/curva.ts";
import { TOQUE } from "../src/telas/pet/ToquePet.tsx";
import { destinoNoPonto, ligarToqueLugar } from "../src/telas/pet/ToqueLugar.tsx";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { LUGARES_MODELOS, type NomeLugar } from "../src/telas/pet/ilha/modelos.ts";

describe("onde ficam os lugares (LG-G1 a LG-G4)", () => {
  for (const cm of [CMU_MVP, CMU]) test(`layout ${cm.layout.nome}`, () => {
    const ilha = ilhaDe(cm), nomes = Object.keys(LUGARES_MODELOS) as NomeLugar[];
    expect(ilha.lugares.map(l => l.nome).sort()).toEqual([...nomes].sort());
    for (const l of ilha.lugares) {
      expect(ilha.naArea(Math.floor(l.x), Math.floor(l.z)), l.nome).toBe(false);
      if (l.nome === "cais") {
        const c = ilha.cel(Math.floor(l.x), Math.floor(l.z) - 1)!, agua = ilha.cel(Math.floor(l.x), Math.floor(l.z))!;
        expect(c.tipo).toBe("areia"); expect(agua.tipo).toBe("agua"); expect(l.giro).toBeCloseTo(Math.PI);
        continue;
      }
      const G = LUGARES_GRADE[l.nome], d = ilha.distanciaDaArea(l.x, l.z), c = ilha.cel(Math.floor(l.x), Math.floor(l.z))!;
      expect(c.tipo).toBe("grama"); expect(c.cantos.every(h => h === c.cantos[0])).toBe(true);
      expect(l.z).toBeLessThan(0); expect(d).toBeGreaterThanOrEqual(G.perto - 1e-9); expect(d).toBeLessThanOrEqual(G.longe + 1e-9);
      expect(l.y).toBe(ilha.altura(l.x, l.z));
      for (const e of ilha.enfeites) expect(Math.hypot(e.x - l.x, e.z - l.z), `${l.nome} e ${e.nome}`).toBeGreaterThanOrEqual(G.deEnfeite);
      /* a frente (+z do glTF girado) aponta para o ponto mais perto da area */
      const ax = Math.min(Math.max(l.x, 0), ilha.area.w), az = Math.min(Math.max(l.z, 0), ilha.area.h);
      const dir = [Math.sin(l.giro), Math.cos(l.giro)], para = [ax - l.x, az - l.z], n = Math.hypot(para[0], para[1]);
      expect(dir[0] * para[0] / n + dir[1] * para[1] / n).toBeCloseTo(1);
    }
    const [a, b] = ilha.lugares.filter(l => l.nome !== "cais");
    expect(Math.hypot(a.x - b.x, a.z - b.z)).toBeGreaterThanOrEqual(LUGARES_GRADE.portao.deEnfeite + LUGARES_GRADE.portao.clareira);
    for (const i of ilha.escondidos) {
      const o = ilha.objetos[i];
      expect(o.doMotor).toBeNull();
      expect(ilha.lugares.some(l => Math.hypot(o.x - l.x, o.z - l.z) < LUGARES_GRADE[l.nome].clareira)).toBe(true);
    }
    ilha.objetos.forEach((o, i) => {
      if (o.doMotor !== null || ilha.escondidos.has(i)) return;
      for (const l of ilha.lugares) expect(Math.hypot(o.x - l.x, o.z - l.z)).toBeGreaterThanOrEqual(LUGARES_GRADE[l.nome].clareira);
    });
  });
});

/* os lugares refeitos com a textura pintada da Meshy (docs/objetos3d/REFERENCIAS.md, secao 5: nao achatar), fora do LG-G5; o desvio no
   docs/registro/2026-11.md. Quem mesclar o retrabalho de outro lugar junta os nomes. */
const TEXTURA_PINTADA: NomeLugar[] = ["barraca"];

describe("a paleta da Ilha (LG-G5)", () => {
  const DOCS = join(__dirname, "..", "..", "..", "docs", "lugares3d");
  for (const n of (Object.keys(LUGARES_MODELOS) as NomeLugar[]).filter(n => !TEXTURA_PINTADA.includes(n))) test(n, () => {
    const p = JSON.parse(readFileSync(join(DOCS, n, "paleta.json"), "utf8")) as { paleta: number[][]; paleta_ilha: number[][] };
    expect(p.paleta_ilha.length).toBe(p.paleta.length);
    /* o PNG de paleta publicado: as cores do PLTE estao todas na paleta da Ilha */
    const b = readFileSync(join(__dirname, "..", "public", "lugares", n, `${n}_cor.png`));
    expect(b[25]).toBe(3);    // tipo de cor 3: paleta
    const i = b.indexOf("PLTE"), len = b.readUInt32BE(i - 4), ilha = p.paleta_ilha.map(c => c.join(","));
    for (let k = 0; k < len; k += 3) expect(ilha, n).toContain([b[i + 4 + k], b[i + 5 + k], b[i + 6 + k]].join(","));
  });
});

/* LG-G5b, a textura pintada (no lugar do LG-G5 para os de TEXTURA_PINTADA): o PNG publicado guarda o detalhe, isto e, nao foi achatado
   em poucas cores lisas (o achatamento antigo deixava de 3 a 12; aqui sao pelo menos 64 cores distintas), e o chao de dentro, visto pela
   porta, e escuro: o pixel publicado no centro das UVs dele (docs/objetos3d/<lugar>/retrabalho/chao_uv.json) fica abaixo de 45 % de
   luminancia (a Meshy nao fez chao e deixou o fundo claro; D-LG-9). */
describe("a textura pintada (LG-G5b)", () => {
  const OBJ = join(__dirname, "..", "..", "..", "docs", "objetos3d");
  const plte = (b: Buffer): number[][] => {
    const i = b.indexOf("PLTE"), len = b.readUInt32BE(i - 4), cores: number[][] = [];
    for (let k = 0; k < len; k += 3) cores.push([b[i + 4 + k], b[i + 5 + k], b[i + 6 + k]]);
    return cores;
  };
  /** os indices de um PNG de paleta de 8 bits sem entrelacamento (o que publicar_barraca.py grava): junta os IDAT, infla e desfaz os filtros */
  const indices = (b: Buffer): { w: number; h: number; px: Uint8Array } => {
    const w = b.readUInt32BE(16), h = b.readUInt32BE(20);
    expect(b[24]).toBe(8); expect(b[28]).toBe(0);
    const partes: Buffer[] = [];
    for (let o = 8; o < b.length;) {
      const len = b.readUInt32BE(o), tipo = b.subarray(o + 4, o + 8).toString();
      if (tipo === "IDAT") partes.push(b.subarray(o + 8, o + 8 + len));
      o += 12 + len;
    }
    const z = inflateSync(Buffer.concat(partes)), px = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) {
      const f = z[y * (w + 1)], lin = z.subarray(y * (w + 1) + 1, (y + 1) * (w + 1));
      for (let x = 0; x < w; x++) {
        const a = x > 0 ? px[y * w + x - 1] : 0, c = y > 0 ? px[(y - 1) * w + x] : 0, d = x > 0 && y > 0 ? px[(y - 1) * w + x - 1] : 0;
        const pa = Math.abs(c - d), pb = Math.abs(a - d), pc = Math.abs(a + c - 2 * d);
        const pred = [0, a, c, (a + c) >> 1, pa <= pb && pa <= pc ? a : pb <= pc ? c : d][f];
        if (pred === undefined) throw new Error("filtro PNG desconhecido: " + f);
        px[y * w + x] = (lin[x] + pred) & 255;
      }
    }
    return { w, h, px };
  };
  for (const n of TEXTURA_PINTADA) test(n, () => {
    const b = readFileSync(join(__dirname, "..", "public", "lugares", n, `${n}_cor.png`));
    expect(b.subarray(1, 4).toString()).toBe("PNG");
    expect(b[25]).toBe(3);                                   // paleta (para caber nos 300 KB de test/lugares3d.test.ts)
    const cores = plte(b);
    expect(new Set(cores.map(c => c.join(","))).size).toBeGreaterThanOrEqual(64);
    /* o chao de dentro: o pixel publicado no centro dos quatro cantos (u, v do Blender: a linha da imagem e 1 - v) e escuro */
    const chao = JSON.parse(readFileSync(join(OBJ, n, "retrabalho", "chao_uv.json"), "utf8")) as { cantos: number[][] };
    expect(chao.cantos.length).toBe(4);
    const { w, h, px } = indices(b);
    const u = chao.cantos.reduce((s, c) => s + c[0], 0) / 4, v = chao.cantos.reduce((s, c) => s + c[1], 0) / 4;
    const [r, g, bl] = cores[px[Math.floor((1 - v) * h) * w + Math.floor(u * w)]];
    expect((0.2126 * r + 0.7152 * g + 0.0722 * bl) / 255).toBeLessThan(0.45);
  });
});

describe("o toque nos lugares (LG-G6)", () => {
  /* uma projecao de cima, sem perspectiva: (x, z) do mundo em celulas vira (x/10, -z/10) da tela */
  const ndc = (x: number, _y: number, z: number): [number, number] => [x / 10, -z / 10];
  const caixa = (x0: number, z0: number, x1: number, z1: number) => new THREE.Box3(new THREE.Vector3(x0, 0, z0), new THREE.Vector3(x1, 3, z1));
  test("lugarNoPonto: dentro, fora e o menor quando dois cobrem o ponto", () => {
    const c = new Map([["portao", caixa(0, 0, 2, 2)], ["barraca", caixa(1, 1, 6, 6)]] as const);
    expect(lugarNoPonto(c, ndc, 0.05, -0.05)).toBe("portao");
    expect(lugarNoPonto(c, ndc, 0.15, -0.15)).toBe("portao");      // nos dois: o retangulo menor
    expect(lugarNoPonto(c, ndc, 0.4, -0.4)).toBe("barraca");
    expect(lugarNoPonto(c, ndc, 0.9, -0.9)).toBeNull();
  });
  test("cada lugar aberto tem um destino; o cais trancado nao abre", () => {
    for (const n of Object.keys(LUGAR_ABERTO) as (keyof typeof LUGAR_ABERTO)[]) if (LUGAR_ABERTO[n]) expect(LUGAR_DESTINO[n], n).not.toBeNull();
    expect(LUGAR_DESTINO).toEqual({ portao: "lutar", barraca: "diario", cais: null });
    expect([...NOMES_LUGARES].sort()).toEqual(Object.keys(LUGARES_MODELOS).sort());
  });

  /* a cena falsa: o portao em x 0..100, a barraca em 200..300, o cais em 400..500 (y qualquer); o pet em (210..240, 0..60) */
  const alvo = () => Object.assign(new EventTarget(), { getBoundingClientRect: () => ({ left: 0, top: 0 }), style: { cursor: "" } });
  const ev = (tipo: string, x: number, y = 50, extra: Record<string, unknown> = {}) =>
    Object.assign(new Event(tipo), { pointerId: 1, clientX: x, clientY: y, button: 0, buttons: tipo === "pointermove" ? 0 : 1, pointerType: "mouse", ...extra });
  let fora: (() => void) | null = null;
  const idas: Destino[] = [];
  beforeEach(() => {
    CENA.coberto = false; CENA.bolaNaMao = false; CENA.petNaMao = false;
    CENA.ret = { x: 210, y: 0, w: 30, h: 60 };
    CENA.mundo = {
      paraMundo: () => null, paraTela: () => [0, 0], get pet(): [number, number] { return [0, 0]; },
      lugarEm: x => (x < 100 ? "portao" : x >= 200 && x < 300 ? "barraca" : x >= 400 && x < 500 ? "cais" : null),
    };
    idas.length = 0;
  });
  afterEach(() => { fora?.(); fora = null; CENA.ret = null; CENA.mundo = null; CENA.coberto = false; });
  const toque = (el: EventTarget, x: number, y = 50) => { el.dispatchEvent(ev("pointerdown", x, y)); el.dispatchEvent(ev("pointerup", x, y)); };

  test("o portao abre o Lutar e a barraca o Diario; o cais, o chao e o pet nao", () => {
    const el = alvo(); fora = ligarToqueLugar(el, d => idas.push(d));
    toque(el, 50); toque(el, 280); toque(el, 450); toque(el, 150); toque(el, 220);
    expect(idas).toEqual(["lutar", "diario"]);
  });
  test("o arrasto, o toque longo e o painel por cima nao abrem", () => {
    const el = alvo(); fora = ligarToqueLugar(el, d => idas.push(d));
    el.dispatchEvent(ev("pointerdown", 50)); el.dispatchEvent(ev("pointermove", 50 + TOQUE.andaMax + 1, 50, { buttons: 1 })); el.dispatchEvent(ev("pointerup", 50));
    const agora = performance.now, t0 = agora.call(performance);
    el.dispatchEvent(ev("pointerdown", 50));
    performance.now = () => t0 + TOQUE.duraMax + 50;
    try { el.dispatchEvent(ev("pointerup", 50)); } finally { performance.now = agora; }
    CENA.coberto = true; toque(el, 50);
    expect(idas).toEqual([]);
  });
  test("o cursor vira a mao so sobre um lugar que abre", () => {
    const el = alvo(); fora = ligarToqueLugar(el, d => idas.push(d));
    el.dispatchEvent(ev("pointermove", 50)); expect(el.style.cursor).toBe("pointer");
    el.dispatchEvent(ev("pointermove", 450)); expect(el.style.cursor).toBe("");
    el.dispatchEvent(ev("pointermove", 280)); expect(el.style.cursor).toBe("pointer");
    expect(destinoNoPonto(el, 225, 30)).toBeNull();    // o sprite do pet, na frente da barraca
  });
});
