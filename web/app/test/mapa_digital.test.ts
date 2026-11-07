/* O estilo Digital da ilha (docs/TAREFA_V3_MAPA_DIGITAL.md, D1): o ceu pintado em public/mapa_digital/ tem a procedencia (D-G2: o
   License.txt com a Meshy e a marca de IA) e cabe no orcamento de um item (300 KB); o estilo usa a mesma grade da ilha (o gate D-G0 e o
   E-G0 do test/ilha_enfeites.test.ts, que confere os objetos de hoje contra o gabarito). */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { MODELOS } from "../src/telas/pet/ilha/modelos.ts";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { DIGITAL } from "../src/telas/pet/ilha/constantes.ts";
import { lugarDaLata, lugaresDasParticulas, paresDosFios, segmentosDosFios } from "../src/telas/pet/ilha/digitalConta.ts";
import { DOBRA_K } from "../src/telas/pet/ilha/constantes.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";

const PASTA = join(__dirname, "..", "public", "mapa_digital"), KITS = join(__dirname, "..", "public", "kits3d_digital");

describe("o estilo Digital", () => {
  test("D-G2: o ceu pintado com a procedencia e no orcamento", () => {
    expect(statSync(join(PASTA, "ceu.jpg")).size).toBeLessThanOrEqual(300 * 1024);
    const lic = readFileSync(join(PASTA, "License.txt"), "utf8");
    expect(lic).toMatch(/Meshy/); expect(lic).toMatch(/gerada por IA/);
  });

  test("D-G2: os kits do Digital (D2): cada modelo da tabela com a textura recolorida, o .bin de sempre e a licenca do kit", () => {
    const arquivos = [...new Set(Object.values(MODELOS).flatMap(m => m.arquivos))];
    for (const a of arquivos) {
      const f = join(KITS, a), g = JSON.parse(readFileSync(f, "utf8")) as { buffers: { uri: string }[]; images?: { uri: string }[] };
      for (const b of g.buffers) { expect(b.uri.startsWith("../../kits3d/"), a).toBe(true); expect(existsSync(join(f, "..", b.uri)), a).toBe(true); }
      for (const i of g.images ?? []) expect(existsSync(join(f, "..", i.uri)), `${a}: ${i.uri}`).toBe(true);
    }
    for (const kit of readdirSync(KITS)) expect(readdirSync(join(KITS, kit)).some(n => /^License.*\.txt$/.test(n)), kit).toBe(true);
    const total = readdirSync(KITS).flatMap(k => readdirSync(join(KITS, k)).map(n => statSync(join(KITS, k, n)).size)).reduce((x, y) => x + y, 0);
    expect(total).toBeLessThanOrEqual(2 * 1024 * 1024);
  });

  /* D3 (docs/TAREFA_V3_MAPA_DIGITAL.md, secao 11): o toque digital, deterministico e no lugar */
  for (const cm of [CMU_MVP, CMU]) test(`D3: as particulas e os fios (layout ${cm.layout.nome})`, () => {
    const ilha = ilhaDe(cm), P = DIGITAL.particulas, F = DIGITAL.fios;
    const ps = lugaresDasParticulas(ilha);
    expect(ps).toHaveLength(P.quantas);
    expect(lugaresDasParticulas(ilhaDe(cm))).toEqual(ps);
    for (const [x, y, z] of ps) {
      expect(x).toBeGreaterThanOrEqual(-P.margem); expect(x).toBeLessThanOrEqual(ilha.area.w + P.margem);
      expect(z).toBeGreaterThanOrEqual(-P.margem); expect(z).toBeLessThanOrEqual(ilha.area.h + P.margem);
      const h = y - ilha.altura(x, z);
      expect(h).toBeGreaterThanOrEqual(P.altura[0]); expect(h).toBeLessThanOrEqual(P.altura[1]);
    }
    const postes = ilha.enfeites.filter(e => e.nome === "poste"), pares = paresDosFios(ilha);
    expect(pares.length).toBeGreaterThan(0);
    const chaves = new Set(pares.map(p => `${p.a}-${p.b}`));
    expect(chaves.size).toBe(pares.length);
    for (const { a, b, vao } of pares) {
      expect(a).toBeLessThan(b);
      expect(vao).toBeLessThanOrEqual(F.alcance);
      expect(vao).toBeCloseTo(Math.hypot(postes[a].x - postes[b].x, postes[a].z - postes[b].z), 9);
    }
    const seg = segmentosDosFios(ilha);
    expect(seg).toHaveLength(pares.length * F.segmentos * 6);
    /* o fio cai abaixo da reta entre os topos e volta a ela nas pontas */
    for (const v of seg) expect(Number.isFinite(v)).toBe(true);
  });

  /* D4 (docs/TAREFA_V3_MAPA_DIGITAL.md, secao 12): a lata gigante, o arquivo com os gates dos marcos (G1 a G8 da ITENS_3D, teto 2 414)
     e o lugar no horizonte */
  test("D4: o arquivo da lata (G1 a G8, teto dos marcos)", () => {
    const f = join(__dirname, "..", "public", DIGITAL.lata.arquivo), dir = join(f, "..");
    const g = JSON.parse(readFileSync(f, "utf8")) as {
      asset: { extras?: { gerado_por_ia?: boolean; gerador?: string } }; nodes: unknown[]; buffers: { uri: string }[]; images?: { uri: string }[];
      accessors: { count: number }[]; meshes: { primitives: { indices?: number; mode?: number; material?: number }[] }[];
      materials?: { pbrMetallicRoughness?: { baseColorTexture?: unknown; metallicRoughnessTexture?: unknown }; normalTexture?: unknown;
        occlusionTexture?: unknown; emissiveTexture?: unknown }[];
    };
    let tri = 0;
    for (const me of g.meshes) for (const p of me.primitives) { expect(p.mode ?? 4).toBe(4); tri += g.accessors[p.indices!].count / 3; }
    expect(tri).toBeLessThanOrEqual(2414);
    expect(g.nodes.length).toBe(1);
    for (const im of g.images ?? []) {
      const b = readFileSync(join(dir, im.uri)), w = b.readUInt32BE(16), h = b.readUInt32BE(20);
      expect(w).toBeLessThanOrEqual(1024); expect(Math.log2(w) % 1).toBe(0); expect(Math.log2(h) % 1).toBe(0);
    }
    for (const ma of g.materials ?? []) {
      expect(ma.pbrMetallicRoughness?.baseColorTexture).toBeDefined();
      expect(ma.normalTexture ?? ma.occlusionTexture ?? ma.emissiveTexture ?? ma.pbrMetallicRoughness?.metallicRoughnessTexture).toBeUndefined();
    }
    const usados = [f, ...g.buffers.map(b => join(dir, b.uri)), ...(g.images ?? []).map(i => join(dir, i.uri))];
    expect(usados.reduce((s, u) => s + statSync(u).size, 0)).toBeLessThanOrEqual(300 * 1024);
    expect(readdirSync(dir).map(a => join(dir, a)).filter(a => !usados.includes(a) && !/License\.txt$/.test(a))).toEqual([]);
    const lic = readFileSync(join(dir, "License.txt"), "utf8");
    expect(lic).toMatch(/Meshy/); expect(lic).toMatch(/gerado por IA/);
    expect(g.asset.extras?.gerado_por_ia).toBe(true); expect(g.asset.extras?.gerador).toMatch(/Meshy/);
    const r = JSON.parse(readFileSync(join(__dirname, "..", "..", "..", "docs", "mapa_digital", "lata", "validacao.json"), "utf8")) as
      { issues: { numErrors: number; numWarnings: number } };
    expect(r.issues.numErrors).toBe(0); expect(r.issues.numWarnings).toBe(0);
  });

  for (const cm of [CMU_MVP, CMU]) test(`D4: a lata no horizonte (layout ${cm.layout.nome})`, () => {
    const ilha = ilhaDe(cm), L = DIGITAL.lata, dir: [number, number] = [0, -1], meia = 0.5;
    const ninho: [number, number] = [cm.layout.ninho[0] + 0.5, cm.layout.ninho[1] + 0.5];
    const a = lugarDaLata(ilha, ninho, DOBRA_K, dir, meia);
    expect(lugarDaLata(ilha, ninho, DOBRA_K, dir, meia)).toEqual(a);
    /* sempre `longe` ao norte do pet, e com a dobra descontada: o pe fica a `base` do chao do pet, onde quer que ele esteja */
    for (const foco of [ninho, [1.5, 1.5], [ilha.area.w - 1.5, ilha.area.h - 1.5]] as [number, number][]) {
      const l = lugarDaLata(ilha, foco, DOBRA_K, dir, meia), dz = (l.x - foco[0]) * dir[0] + (l.z - foco[1]) * dir[1];
      expect(l.z).toBeCloseTo(foco[1] - L.longe, 9);
      expect(l.y - DOBRA_K * dz * dz).toBeCloseTo(ilha.altura(foco[0], foco[1]) + L.base, 9);
      expect(l.giro).toBe(L.giro);
    }
    /* a paralaxe: o pet anda 10 celulas para o leste e a lata so 10 * (1 - paralaxe) */
    const b = lugarDaLata(ilha, [ninho[0] + 10, ninho[1]], DOBRA_K, dir, meia);
    expect(b.x - a.x).toBeCloseTo(10 * (1 - L.paralaxe), 9);
    /* o lado acompanha a largura da tela (a mesma fracao no celular e no desktop) */
    const c = lugarDaLata(ilha, ninho, DOBRA_K, dir, 2 * meia);
    expect(c.x - a.x).toBeCloseTo(L.lado * (L.longe + 14.5) * meia, 9);
  });
});
