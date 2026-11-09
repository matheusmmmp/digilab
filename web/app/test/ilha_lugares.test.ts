/* Onde ficam os lugares na ilha (docs/TAREFA_V3_LUGARES_3D.md, secao 12; grade.ts, porLugares). LG-G1: um de cada, fora da area andavel.
   LG-G2: o portao e a barraca em grama plana ao norte, a distancia combinada da area, longe dos enfeites e um do outro, com a frente para a
   area. LG-G3: o cais na ultima linha de areia antes do mar, de frente para o norte. LG-G4: a clareira so esconde a decoracao (nunca uma
   arvore do motor) e so dentro do raio; os objetos em si nao mudam (o E-G0 de test/ilha_enfeites.test.ts confere contra o gabarito).
   LG-G5: a paleta da Ilha (docs/lugares3d/estilo_ilha.py) e a da textura publicada, nos lugares de cor chapada; os de textura pintada
   (TEXTURA_PINTADA, o retrabalho de docs/objetos3d/REFERENCIAS.md, secao 5) saem dele e passam pelo LG-G5b: a cor e um PNG de 512 a 1024 px,
   quadrado e com cor de verdade (nao as poucas cores lisas de antes), e a mascara de luz e quadrada, branca so numa parte e cobre o mesmo UV;
   na barraca, o chao de dentro, visto pela porta, e escuro (docs/objetos3d/barraca/retrabalho/chao_uv.json; D-LG-9).
   LG-G6: o toque nos lugares (ToqueLugar.tsx; secao 13): o retangulo projetado da caixa de cada lugar (lugarNoPonto) e o gesto, que abre
   o destino do lugar aberto e nada mais (o cais trancado, o arrasto, o toque longo, o sprite do pet, o painel por cima). */
import { readFileSync } from "node:fs";
import { inflateSync } from "node:zlib";
import { join } from "node:path";
import * as THREE from "three";
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import type { Destino } from "../src/rotas.ts";
import { CENA } from "../src/telas/pet/cenaEstado.ts";
import { PLANTA_ILHA } from "../src/telas/pet/ilha/constantes.ts";
import { LUGAR_ABERTO, LUGAR_DESTINO, NOMES_LUGARES } from "../src/telas/pet/lugaresIlha.ts";
import { lugarNoPonto } from "../src/telas/pet/ilha/curva.ts";
import { TOQUE } from "../src/telas/pet/ToquePet.tsx";
import { destinoNoPonto, ligarToqueLugar } from "../src/telas/pet/ToqueLugar.tsx";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { LUGARES_LUZ, LUGARES_MODELOS, type NomeLugar } from "../src/telas/pet/ilha/modelos.ts";

describe("onde ficam os lugares (LG-G1 a LG-G4, desde a planta A)", () => {
  for (const cm of [CMU_MVP, CMU]) test(`layout ${cm.layout.nome}`, () => {
    const ilha = ilhaDe(cm), nomes = Object.keys(LUGARES_MODELOS) as NomeLugar[], P = PLANTA_ILHA;
    expect(ilha.lugares.map(l => l.nome).sort()).toEqual([...nomes].sort());
    for (const l of ilha.lugares) {
      if (l.nome === "cais") {
        const c = ilha.cel(Math.floor(l.x), Math.floor(l.z) - 1)!, agua = ilha.cel(Math.floor(l.x), Math.floor(l.z))!;
        expect(c.tipo).toBe("areia"); expect(agua.tipo).toBe("agua"); expect(l.giro).toBeCloseTo(Math.PI);
        expect(l.x).toBe(P.lugares.cais.x);
        continue;
      }
      const G = P.lugares[l.nome], c = ilha.cel(Math.floor(l.x), Math.floor(l.z))!;
      expect(c.tipo).toBe("grama"); expect(c.cantos.every(h => h === c.cantos[0])).toBe(true);
      expect(Math.hypot(l.x - G.alvo[0], l.z - G.alvo[1])).toBeLessThanOrEqual(G.busca);
      expect(l.y).toBe(ilha.altura(l.x, l.z));
      /* a frente (+z do glTF girado): fora da area, para o ponto mais perto dela; dentro (a barraca), para a praca */
      const dentro = ilha.naArea(Math.floor(l.x), Math.floor(l.z));
      const ax = dentro ? P.praca.x : Math.min(Math.max(l.x, 0), ilha.area.w), az = dentro ? P.praca.z : Math.min(Math.max(l.z, 0), ilha.area.h);
      const dir = [Math.sin(l.giro), Math.cos(l.giro)], para = [ax - l.x, az - l.z], n = Math.hypot(para[0], para[1]);
      expect(dir[0] * para[0] / n + dir[1] * para[1] / n).toBeCloseTo(1);
    }
    /* o portao ao norte, no fim do caminho reto da praca; a barraca a leste da praca */
    const portao = ilha.lugares.find(l => l.nome === "portao")!, barraca = ilha.lugares.find(l => l.nome === "barraca")!;
    expect(portao.z).toBeLessThan(0); expect(Math.abs(portao.x - P.praca.x)).toBeLessThan(1);
    expect(barraca.x).toBeGreaterThan(P.praca.x + P.praca.raio);
    expect(Math.hypot(portao.x - barraca.x, portao.z - barraca.z)).toBeGreaterThanOrEqual(P.lugares.portao.clareira + P.lugares.barraca.clareira);
    /* a clareira so esconde a decoracao, nunca uma arvore do motor */
    for (const i of ilha.escondidos) expect(ilha.objetos[i].doMotor).toBeNull();
    ilha.objetos.forEach((o, i) => {
      if (o.doMotor !== null || ilha.escondidos.has(i)) return;
      for (const l of ilha.lugares) expect(Math.hypot(o.x - l.x, o.z - l.z)).toBeGreaterThanOrEqual(P.lugares[l.nome].clareira);
    });
  });
});

/** os lugares retrabalhados com a textura pintada da Meshy (sem achatar; docs/TAREFA_V3_LUGARES_3D.md, secoes 14 a 16). Quem retrabalhar outro lugar
    junta o nome aqui */
const TEXTURA_PINTADA: readonly NomeLugar[] = ["portao", "barraca", "cais"];

describe("a paleta da Ilha (LG-G5)", () => {
  const DOCS = join(__dirname, "..", "..", "..", "docs", "lugares3d");
  const chapados = (Object.keys(LUGARES_MODELOS) as NomeLugar[]).filter(l => !TEXTURA_PINTADA.includes(l));
  /* com o cais (secao 16), os tres lugares sairam para a textura pintada: o LG-G5 fica sem lugar, e o teste diz isso em vez de sumir */
  if (chapados.length === 0) test("nenhum lugar de cor chapada: todos no LG-G5b", () => {
    expect([...TEXTURA_PINTADA].sort()).toEqual((Object.keys(LUGARES_MODELOS) as NomeLugar[]).sort());
  });
  for (const n of chapados) test(n, () => {
    const p = JSON.parse(readFileSync(join(DOCS, n, "paleta.json"), "utf8")) as { paleta: number[][]; paleta_ilha: number[][] };
    expect(p.paleta_ilha.length).toBe(p.paleta.length);
    /* o PNG de paleta publicado: as cores do PLTE estao todas na paleta da Ilha */
    const b = readFileSync(join(__dirname, "..", "public", "lugares", n, `${n}_cor.png`));
    expect(b[25]).toBe(3);    // tipo de cor 3: paleta
    const i = b.indexOf("PLTE"), len = b.readUInt32BE(i - 4), ilha = p.paleta_ilha.map(c => c.join(","));
    for (let k = 0; k < len; k += 3) expect(ilha, n).toContain([b[i + 4 + k], b[i + 5 + k], b[i + 6 + k]].join(","));
  });
});

describe("a textura pintada (LG-G5b)", () => {
  /* o PNG decodificado sem dependencia nova: zlib do Node e os filtros do PNG (so profundidade 8, sem entrelacar) */
  const png = (f: string): { w: number; h: number; px: (x: number, y: number) => number[] } => {
    const b = readFileSync(f), w = b.readUInt32BE(16), h = b.readUInt32BE(20), prof = b[24], tipo = b[25];
    expect(prof).toBe(8); expect(b[28]).toBe(0);
    let i = 8, pal: number[][] = []; const dados: Buffer[] = [];
    while (i < b.length) {
      const len = b.readUInt32BE(i), nome = b.toString("latin1", i + 4, i + 8), c = b.subarray(i + 8, i + 8 + len);
      if (nome === "PLTE") for (let k = 0; k < len; k += 3) pal.push([c[k], c[k + 1], c[k + 2]]);
      if (nome === "IDAT") dados.push(c);
      i += 12 + len;
    }
    const can = ({ 0: 1, 2: 3, 3: 1, 4: 2, 6: 4 } as Record<number, number>)[tipo], lin = w * can, cru = inflateSync(Buffer.concat(dados));
    const out = Buffer.alloc(lin * h);
    for (let y = 0; y < h; y++) {
      const f0 = cru[y * (lin + 1)];
      for (let x = 0; x < lin; x++) {
        const v = cru[y * (lin + 1) + 1 + x], a = x >= can ? out[y * lin + x - can] : 0, c = y > 0 ? out[(y - 1) * lin + x] : 0;
        const d = y > 0 && x >= can ? out[(y - 1) * lin + x - can] : 0, p = a + c - d;
        const pa = Math.abs(p - a), pb = Math.abs(p - c), pc = Math.abs(p - d);
        out[y * lin + x] = (v + [0, a, c, (a + c) >> 1, pa <= pb && pa <= pc ? a : pb <= pc ? c : d][f0]) & 255;
      }
    }
    return { w, h, px: (x, y) => { const o = y * lin + x * can; return tipo === 3 ? pal[out[o]] : [...out.subarray(o, o + can)]; } };
  };
  for (const n of TEXTURA_PINTADA) test(n, () => {
    const dir = join(__dirname, "..", "public", "lugares", n), cor = png(join(dir, `${n}_cor.png`));
    expect(cor.w).toBe(cor.h); expect(cor.w).toBeGreaterThanOrEqual(512); expect(cor.w).toBeLessThanOrEqual(1024);
    const cores = new Set<string>();
    for (let y = 0; y < cor.h; y += 4) for (let x = 0; x < cor.w; x += 4) cores.add(cor.px(x, y).slice(0, 3).join(","));
    expect(cores.size, "a textura pintada tem mais que as poucas cores lisas de antes").toBeGreaterThan(64);
    const arq = LUGARES_LUZ[n];
    if (!arq) return;
    const luz = png(join(__dirname, "..", "public", "lugares", arq));
    expect(luz.w).toBe(luz.h);
    /* a mascara cobre o mesmo UV: o branco cai onde a cor e o ciano do portal, e o preto onde a cor nao e */
    let branco = 0, certo = 0;
    for (let y = 0; y < luz.h; y++) for (let x = 0; x < luz.w; x++) {
      const m = luz.px(x, y)[0], c = cor.px(Math.floor(x * cor.w / luz.w), Math.floor(y * cor.h / luz.h));
      const ciano = c[2] > 120 && c[1] > 120 && c[0] < c[1] - 40;
      if (m > 128) { branco++; if (ciano) certo++; }
    }
    expect(branco / (luz.w * luz.h)).toBeGreaterThan(0.01); expect(branco / (luz.w * luz.h)).toBeLessThan(0.5);
    expect(certo / branco, "o branco da mascara cai no ciano da textura").toBeGreaterThan(0.8);
  });
  /* a barraca: o chao de dentro, visto pela porta, e escuro. A Meshy nao fez chao e deixou o fundo claro (D-LG-9): o pixel publicado no
     centro das UVs dele (docs/objetos3d/barraca/retrabalho/chao_uv.json; u, v do Blender, a linha da imagem e 1 - v) fica abaixo de 45 %
     de luminancia */
  test("barraca: o chao de dentro escuro", () => {
    const chao = JSON.parse(readFileSync(join(__dirname, "..", "..", "..", "docs", "objetos3d", "barraca", "retrabalho", "chao_uv.json"), "utf8")) as { cantos: number[][] };
    expect(chao.cantos.length).toBe(4);
    const cor = png(join(__dirname, "..", "public", "lugares", "barraca", "barraca_cor.png"));
    const u = chao.cantos.reduce((s, c) => s + c[0], 0) / 4, v = chao.cantos.reduce((s, c) => s + c[1], 0) / 4;
    const [r, g, b] = cor.px(Math.floor(u * cor.w), Math.floor((1 - v) * cor.h));
    expect((0.2126 * r + 0.7152 * g + 0.0722 * b) / 255).toBeLessThan(0.45);
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
