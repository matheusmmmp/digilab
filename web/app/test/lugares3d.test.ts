/* Os arquivos dos lugares da ilha (docs/TAREFA_V3_LUGARES_3D.md): os gates G1 a G8 dos itens (docs/TAREFA_V3_ITENS_3D.md), como em
   test/ilha_enfeites.test.ts, com o teto dos marcos (2 414 triangulos). Cada modelo de LUGARES_MODELOS: triangulos so, 1 no, a textura de
   cor em potencia de 2 ate 1024, nenhum mapa alem da cor no glTF (a mascara de luz fica ao lado), o validador sem erro nem aviso, ate
   300 KB, nenhum arquivo solto na pasta, e a procedencia da Meshy (o License.txt e a marca de IA no asset.extras). */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { LUGARES_LUZ, LUGARES_MODELOS, type NomeLugar } from "../src/telas/pet/ilha/modelos.ts";

const APP = join(__dirname, ".."), LUG = join(APP, "public", "lugares"), DOCS = join(APP, "..", "..", "docs", "lugares3d");
const TETO = 2414, LADO_MAX = 1024, BYTES = 300 * 1024;
type Gltf = {
  asset: { extras?: { gerado_por_ia?: boolean; gerador?: string } }; nodes: unknown[]; buffers: { uri: string }[]; images?: { uri: string }[];
  accessors: { count: number }[]; meshes: { primitives: { indices?: number; material?: number; mode?: number }[] }[];
  materials?: { pbrMetallicRoughness?: { baseColorTexture?: unknown; metallicRoughnessTexture?: unknown }; normalTexture?: unknown;
    occlusionTexture?: unknown; emissiveTexture?: unknown }[];
};
const ladoPng = (f: string): [number, number] => { const b = readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };

describe("os arquivos dos lugares (G1 a G8, teto dos marcos)", () => {
  for (const n of Object.keys(LUGARES_MODELOS) as NomeLugar[]) test(n, () => {
    const f = join(LUG, LUGARES_MODELOS[n].arquivos[0]), dir = join(f, ".."), g = JSON.parse(readFileSync(f, "utf8")) as Gltf;
    let tri = 0;
    for (const me of g.meshes) for (const p of me.primitives) { expect(p.mode ?? 4).toBe(4); tri += g.accessors[p.indices!].count / 3; }
    expect(tri).toBeLessThanOrEqual(TETO);
    expect(g.nodes.length).toBe(1);
    const luz = LUGARES_LUZ[n] ? join(LUG, LUGARES_LUZ[n]!) : null;
    for (const im of [...(g.images ?? []).map(i => join(dir, i.uri)), ...(luz ? [luz] : [])]) {
      const [w, h] = ladoPng(im);
      expect(w).toBeLessThanOrEqual(LADO_MAX); expect(Math.log2(w) % 1).toBe(0); expect(Math.log2(h) % 1).toBe(0);
    }
    const mats = g.materials ?? [];
    for (const me of g.meshes) for (const p of me.primitives) expect(mats[p.material!].pbrMetallicRoughness?.baseColorTexture).toBeDefined();
    for (const ma of mats) expect(ma.normalTexture ?? ma.occlusionTexture ?? ma.emissiveTexture ?? ma.pbrMetallicRoughness?.metallicRoughnessTexture).toBeUndefined();
    const r = JSON.parse(readFileSync(join(DOCS, n, "validacao.json"), "utf8")) as { issues: { numErrors: number; numWarnings: number } };
    expect(r.issues.numErrors).toBe(0); expect(r.issues.numWarnings).toBe(0);
    const usados = [f, ...g.buffers.map(b => join(dir, b.uri)), ...(g.images ?? []).map(i => join(dir, i.uri)), ...(luz ? [luz] : [])];
    for (const u of usados) expect(existsSync(u), u).toBe(true);
    expect(usados.reduce((s, u) => s + statSync(u).size, 0)).toBeLessThanOrEqual(BYTES);
    expect(readdirSync(dir).map(a => join(dir, a)).filter(a => !usados.includes(a) && !/License\.txt$/.test(a))).toEqual([]);
    const lic = readFileSync(join(dir, "License.txt"), "utf8");
    expect(lic).toMatch(/Meshy/); expect(lic).toMatch(/gerado por IA/);
    expect(g.asset.extras?.gerado_por_ia).toBe(true); expect(g.asset.extras?.gerador).toMatch(/Meshy/);
  });

  test.each(Object.entries(LUGARES_LUZ))("a mascara de luz do %s existe ao lado e nao esta vazia", (_nome, arq) => {
    const f = join(LUG, arq!), b = readFileSync(f);
    expect(b.subarray(1, 4).toString()).toBe("PNG");
    expect(statSync(f).size).toBeGreaterThan(1000);
  });
});
