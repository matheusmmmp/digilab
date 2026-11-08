/* Os enfeites da ilha (docs/TAREFA_V3_MUNDO_ENFEITES.md). E-G0: os objetos da grade de hoje nao mudam, item a item, contra o gabarito
   gravado antes dos enfeites (scripts/gabarito_ilha_objetos.ts, test/gabaritos/ilha_objetos.json). E-G10: onde os enfeites ficam. E-G1 a E-G8: os arquivos de public/enfeites/, como os itens (test/ilha_itens3d.test.ts), com o teto
   da categoria (D-I3: 554 para os repetidos) e a mascara da luz ao lado do glTF. */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { ENFEITES_GRADE } from "../src/telas/pet/ilha/constantes.ts";
import { ENFEITES_LUZ, ENFEITES_MODELOS, MODELOS } from "../src/telas/pet/ilha/modelos.ts";

const GABARITO: Record<string, unknown[]> = JSON.parse(readFileSync(join(__dirname, "gabaritos", "ilha_objetos.json"), "utf8"));

describe("os enfeites da ilha", () => {
  for (const cm of [CMU_MVP, CMU]) test(`E-G0: os objetos de hoje nao mudam (layout ${cm.layout.nome})`, () => {
    expect(JSON.parse(JSON.stringify(ilhaDe(cm).objetos))).toEqual(GABARITO[cm.layout.nome]);
  });
});

describe("onde ficam os enfeites (E-G10)", () => {
  for (const cm of [CMU_MVP, CMU]) test(`na moldura, em grama plana, longe da area, das coisas altas e uns dos outros (layout ${cm.layout.nome})`, () => {
    const ilha = ilhaDe(cm);
    for (const nome of Object.keys(ENFEITES_MODELOS) as (keyof typeof ENFEITES_MODELOS)[])
      expect(ilha.enfeites.filter(e => e.nome === nome).length, nome).toBe(ENFEITES_GRADE[nome].quantos);
    const altos = ilha.objetos.filter(o => !MODELOS[o.modelo].baixo);
    for (const e of ilha.enfeites) {
      const G = ENFEITES_GRADE[e.nome], c = ilha.cel(Math.floor(e.x), Math.floor(e.z))!, d = ilha.distanciaDaArea(e.x, e.z);
      expect(ilha.naArea(Math.floor(e.x), Math.floor(e.z))).toBe(false);
      expect(c.tipo).toBe("grama");
      expect(d).toBeGreaterThanOrEqual(G.perto); expect(d).toBeLessThanOrEqual(G.longe);
      if (G.norte) {
        const dx = e.x - (cm.layout.ninho[0] + 0.5);
        expect(e.z).toBeLessThan(0);
        if ("faixa" in G) { expect(dx).toBeGreaterThanOrEqual(G.faixa[0]); expect(dx).toBeLessThanOrEqual(G.faixa[1]); }
        else expect(Math.abs(dx)).toBeLessThanOrEqual(G.casa);
      }
      for (const o of altos) expect(Math.hypot(o.x - e.x, o.z - e.z)).toBeGreaterThanOrEqual(G.deAlto);
      /* a distancia de quem chega depois (a ordem da lista) */
      for (const f of ilha.enfeites.slice(0, ilha.enfeites.indexOf(e))) expect(Math.hypot(f.x - e.x, f.z - e.z)).toBeGreaterThanOrEqual(G.entreSi);
    }
  });
});

const APP = join(__dirname, ".."), ENF = join(APP, "public", "enfeites"), DOCS = join(APP, "..", "..", "docs", "enfeites");
/* o teto da categoria (D-I3): 554 para os repetidos, 2 414 para os marcos */
const TETO: Record<string, number> = { poste: 554, carro: 2414, geladeira: 2414, trilho: 2414 }, LADO_MAX = 1024, BYTES = 300 * 1024;
type Gltf = {
  asset: { extras?: { gerado_por_ia?: boolean; gerador?: string } }; nodes: { name?: string }[]; buffers: { uri: string }[];
  images?: { uri: string }[]; accessors: { count: number }[];
  meshes: { primitives: { attributes: Record<string, number>; indices?: number; material?: number; mode?: number }[] }[];
  materials?: { pbrMetallicRoughness?: { baseColorTexture?: unknown; metallicRoughnessTexture?: unknown }; normalTexture?: unknown;
    occlusionTexture?: unknown; emissiveTexture?: unknown }[];
};
const ladoPng = (f: string): [number, number] => { const b = readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };

describe("os arquivos dos enfeites (E-G1 a E-G8)", () => {
  for (const n of Object.keys(ENFEITES_MODELOS) as (keyof typeof ENFEITES_MODELOS)[]) test(n, () => {
    const f = join(ENF, ENFEITES_MODELOS[n].arquivos[0]), dir = join(f, ".."), g = JSON.parse(readFileSync(f, "utf8")) as Gltf;
    let tri = 0;
    for (const me of g.meshes) for (const p of me.primitives) { expect(p.mode ?? 4).toBe(4); tri += g.accessors[p.indices!].count / 3; }
    expect(tri).toBeLessThanOrEqual(TETO[n]);
    expect(g.nodes.length).toBe(1);
    const luz = ENFEITES_LUZ[n] ? join(ENF, ENFEITES_LUZ[n]!) : null;
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
    /* a procedencia: o gerado pela Meshy leva a marca de IA (os termos dela, secao 2.4); o feito a mao por script (o poste em blocos,
       docs/TAREFA_V3_MUNDO_ENFEITES.md secao 14) diz que nao e IA e aponta o script que o gera, no License e no asset.extras */
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
});
