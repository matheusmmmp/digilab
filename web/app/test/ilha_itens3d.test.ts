/* Os itens gerados da ilha (docs/TAREFA_V3_ITENS_3D.md, secao 4.2): a tabela ITENS_MODELOS contra a pasta public/itens/, com os gates
   G1 (triangulos abaixo do teto da categoria), G2 (caixa com altura e proporcao de bola), G3 (texturas PNG/JPG ate 1024 px, potencia de 2),
   G4 (nenhuma primitiva sem textura de cor, um material por primitiva), G5 (nenhum mapa normal, metalico, oclusao ou emissivo),
   G6 (o relatorio do glTF-Validator em docs/itens3d/<item>/validacao.json, com 0 erros e 0 avisos), G7 (bytes por item e da pasta) e
   G8 (o License.txt ao lado e a marca de IA no asset.extras). Os tetos sao as medianas dos kits CC0 (docs/itens3d/kits_cc0_medidas.json,
   D-I3). Tudo PROPOSTO, salvo os tetos, DECIDIDOS pelo Matheus em 2026-11-05. */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { ITENS_MODELOS, MODELOS } from "../src/telas/pet/ilha/modelos.ts";

const APP = join(__dirname, ".."), ITENS = join(APP, "public", "itens"), DOCS = join(APP, "..", "..", "docs", "itens3d");
/** o teto de triangulos por item (D-I3): os pequenos, a mediana dos kits baixos; o saco, a dos altos */
const TETO: Record<string, number> = { bola: 554 };
const LADO_MAX = 1024, BYTES_ITEM = 300 * 1024, BYTES_PASTA = 2 * 1024 * 1024;

type Gltf = {
  asset: { extras?: { gerado_por_ia?: boolean; gerador?: string } };
  buffers: { uri: string }[]; images?: { uri: string }[]; accessors: { count: number; min?: number[]; max?: number[] }[];
  meshes: { primitives: { attributes: Record<string, number>; indices?: number; material?: number; mode?: number }[] }[];
  materials?: { pbrMetallicRoughness?: { baseColorTexture?: unknown; metallicRoughnessTexture?: unknown }; normalTexture?: unknown;
    occlusionTexture?: unknown; emissiveTexture?: unknown }[];
};
const arquivosDe = (dir: string): string[] => readdirSync(dir).flatMap(n => statSync(join(dir, n)).isDirectory() ? arquivosDe(join(dir, n)) : [join(dir, n)]);
/** largura e altura de um PNG (cabecalho IHDR) ou de um JPG (o primeiro SOF) */
function tamanhoImagem(f: string): [number, number] {
  const b = readFileSync(f);
  if (b.readUInt32BE(0) === 0x89504e47) return [b.readUInt32BE(16), b.readUInt32BE(20)];
  if (b[0] === 0xff && b[1] === 0xd8) {
    for (let i = 2; i < b.length;) {
      const m = b[i + 1], n = b.readUInt16BE(i + 2);
      if (m >= 0xc0 && m <= 0xc3) return [b.readUInt16BE(i + 7), b.readUInt16BE(i + 5)];
      i += 2 + n;
    }
  }
  throw new Error("imagem que nao e PNG nem JPG: " + f);
}

describe("os itens gerados da ilha", () => {
  const nomes = Object.keys(ITENS_MODELOS) as (keyof typeof ITENS_MODELOS)[];

  test("a tabela e irma da dos kits: nenhum nome repetido, e cada item tem teto (D-I4, D-I3)", () => {
    for (const n of nomes) { expect(n in MODELOS, n).toBe(false); expect(TETO[n], n).toBeGreaterThan(0); }
  });

  for (const n of nomes) {
    const m = ITENS_MODELOS[n], f = join(ITENS, m.arquivos[0]), dir = join(f, "..");
    const g = JSON.parse(readFileSync(f, "utf8")) as Gltf;

    test(`${n}: G1 triangulos e G2 caixa`, () => {
      let tri = 0;
      for (const me of g.meshes) for (const p of me.primitives) {
        expect(p.mode ?? 4, "so triangulos").toBe(4);
        tri += (p.indices !== undefined ? g.accessors[p.indices].count : g.accessors[p.attributes.POSITION].count) / 3;
      }
      expect(tri).toBeLessThanOrEqual(TETO[n]);
      const pos = g.accessors[g.meshes[0].primitives[0].attributes.POSITION];
      const lado = [0, 1, 2].map(i => pos.max![i] - pos.min![i]);
      expect(lado[1]).toBeGreaterThan(0);
      /* a bola: as tres medidas iguais (+-5 %), para a normalizacao pela altura dar o diametro certo */
      for (const l of lado) expect(Math.abs(l / lado[1] - 1)).toBeLessThan(0.05);
    });

    test(`${n}: G3 texturas, G4 materiais e G5 sem mapas extras`, () => {
      for (const im of g.images ?? []) {
        const [w, h] = tamanhoImagem(join(dir, im.uri));
        expect(w).toBeLessThanOrEqual(LADO_MAX); expect(h).toBeLessThanOrEqual(LADO_MAX);
        expect(Math.log2(w) % 1).toBe(0); expect(Math.log2(h) % 1).toBe(0);
      }
      const mats = g.materials ?? [];
      for (const me of g.meshes) for (const p of me.primitives) {
        expect(p.material, "primitiva sem material").toBeDefined();
        expect(mats[p.material!].pbrMetallicRoughness?.baseColorTexture, "primitiva sem textura de cor").toBeDefined();
      }
      for (const ma of mats) {
        expect(ma.normalTexture ?? ma.occlusionTexture ?? ma.emissiveTexture ?? ma.pbrMetallicRoughness?.metallicRoughnessTexture).toBeUndefined();
      }
    });

    test(`${n}: G6 o validador, G7 bytes e G8 procedencia`, () => {
      const r = JSON.parse(readFileSync(join(DOCS, n, "validacao.json"), "utf8")) as { issues: { numErrors: number; numWarnings: number } };
      expect(r.issues.numErrors).toBe(0); expect(r.issues.numWarnings).toBe(0);
      const usados = [f, ...g.buffers.map(b => join(dir, b.uri)), ...(g.images ?? []).map(i => join(dir, i.uri))];
      for (const u of usados) expect(existsSync(u), u).toBe(true);
      expect(usados.reduce((s, u) => s + statSync(u).size, 0)).toBeLessThanOrEqual(BYTES_ITEM);
      /* a pasta do item so tem o que o glTF usa e a licenca */
      expect(arquivosDe(dir).filter(a => !usados.includes(a) && !/License\.txt$/.test(a))).toEqual([]);
      const lic = readFileSync(join(dir, "License.txt"), "utf8");
      expect(lic).toMatch(/Meshy/); expect(lic).toMatch(/gerado por IA/);
      expect(g.asset.extras?.gerado_por_ia).toBe(true); expect(g.asset.extras?.gerador).toMatch(/Meshy/);
    });
  }

  test("G7: a pasta public/itens inteira cabe em 2 MB", () => {
    expect(arquivosDe(ITENS).reduce((s, f) => s + statSync(f).size, 0)).toBeLessThanOrEqual(BYTES_PASTA);
  });
});
