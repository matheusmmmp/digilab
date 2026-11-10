/* Os arquivos dos lugares da ilha (docs/TAREFA_V3_LUGARES_3D.md): os gates G1 a G8 dos itens (docs/TAREFA_V3_ITENS_3D.md), como em
   test/ilha_enfeites.test.ts, com o teto dos marcos (2 414 triangulos). Cada modelo de LUGARES_MODELOS: triangulos so, 1 no, a textura de
   cor em potencia de 2 ate 1024, nenhum mapa alem da cor no glTF (a mascara de luz fica ao lado), o validador sem erro nem aviso, ate
   300 KB, nenhum arquivo solto na pasta, e a procedencia (o License.txt e o asset.extras: a marca de IA da Meshy, ou o script do feito a mao). */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { PLANTA_ILHA } from "../src/telas/pet/ilha/constantes.ts";
import { FUNDO_AGUA, ilhaDe } from "../src/telas/pet/ilha/grade.ts";
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
    /* a procedencia, como nos enfeites (test/ilha_enfeites.test.ts): o gerado pela Meshy leva a marca de IA; o feito a mao por script (o cais,
       docs/TAREFA_V3_LUGARES_3D.md, secao 18) diz que nao e IA e aponta o script que o gera */
    const lic = readFileSync(join(dir, "License.txt"), "utf8"), ex = g.asset.extras;
    expect(typeof ex?.gerado_por_ia).toBe("boolean");
    if (ex?.gerado_por_ia) { expect(lic).toMatch(/Meshy/); expect(lic).toMatch(/gerado por IA/); expect(ex.gerador).toMatch(/Meshy/); }
    else {
      expect(lic).toMatch(/feito a mao por script/);
      const script = ex?.gerador?.match(/docs\/[\w/]+\.py/)?.[0];
      expect(script, "o gerador aponta o script").toBeDefined();
      expect(existsSync(join(APP, "..", "..", script!)), script).toBe(true);
    }
  });

  /* o cais feito a mao (secao 18): sai do script, sem IA, uma malha e uma textura; as medidas dele estao em celulas, entao a altura da
     tabela e a do modelo (escala 1) e o pe fica no fundo do mar (as estacas e o casco entram na agua) */
  /* o portao e a barraca em cartoon (docs/TAREFA_V3_LUGARES_3D.md, secao 19): saem dos scripts de docs/objetos3d/cartoon/, sem IA; o portao
     continua com a mascara do portal */
  for (const n of ["portao", "barraca"] as const) test(`${n} em cartoon: a procedencia e uma malha so`, () => {
    const g = JSON.parse(readFileSync(join(LUG, LUGARES_MODELOS[n].arquivos[0]), "utf8")) as Gltf;
    expect(g.asset.extras?.gerado_por_ia).toBe(false);
    expect(g.asset.extras?.gerador).toContain(`docs/objetos3d/cartoon/${n}.py`);
    expect(g.meshes.length).toBe(1); expect(g.meshes[0].primitives.length).toBe(1); expect(g.images?.length).toBe(1);
    expect(LUGARES_LUZ[n]).toBe(n === "portao" ? "portao/portao_luz.png" : undefined);
  });
  test("o cais feito a mao: a procedencia, a escala 1 e o pe no fundo do mar", () => {
    const g = JSON.parse(readFileSync(join(LUG, LUGARES_MODELOS.cais.arquivos[0]), "utf8")) as Gltf & { accessors: { min?: number[]; max?: number[] }[] };
    expect(g.asset.extras?.gerado_por_ia).toBe(false);
    expect(g.asset.extras?.gerador).toMatch(/docs\/objetos3d\/cais\/mao\/cais_mao\.py/);
    expect(g.meshes.length).toBe(1); expect(g.meshes[0].primitives.length).toBe(1); expect(g.images?.length).toBe(1);
    expect(LUGARES_LUZ.cais).toBeUndefined();
    const pos = g.accessors[0];
    expect(pos.min![1]).toBe(0);
    expect(Math.abs(LUGARES_MODELOS.cais.altura / pos.max![1] - 1)).toBeLessThan(0.01);
    for (const cm of [CMU_MVP, CMU]) {
      const ilha = ilhaDe(cm), l = ilha.lugares.find(l => l.nome === "cais")!;
      expect(l.y).toBe(FUNDO_AGUA);
      expect(l.z - Math.floor(l.z)).toBeCloseTo(PLANTA_ILHA.lugares.cais.mar);
    }
  });

  test.each(Object.entries(LUGARES_LUZ))("a mascara de luz do %s existe ao lado e nao esta vazia", (_nome, arq) => {
    const f = join(LUG, arq!), b = readFileSync(f);
    expect(b.subarray(1, 4).toString()).toBe("PNG");
    expect(statSync(f).size).toBeGreaterThan(1000);
  });
});
