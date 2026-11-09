/* Os enfeites da ilha (docs/TAREFA_V3_MUNDO_ENFEITES.md). E-G0: os objetos da grade de hoje nao mudam, item a item, contra o gabarito
   gravado antes dos enfeites (scripts/gabarito_ilha_objetos.ts, test/gabaritos/ilha_objetos.json). E-G10: onde os enfeites ficam. E-G1 a E-G8: os arquivos de public/enfeites/, como os itens (test/ilha_itens3d.test.ts), com o teto
   da categoria (D-I3: 554 para os repetidos) e a mascara da luz ao lado do glTF. */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { RIO, ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { ENFEITES_GRADE, PLANTA_ILHA } from "../src/telas/pet/ilha/constantes.ts";
import { ENFEITES_LUZ, ENFEITES_MODELOS } from "../src/telas/pet/ilha/modelos.ts";

const GABARITO: Record<string, unknown[]> = JSON.parse(readFileSync(join(__dirname, "gabaritos", "ilha_objetos.json"), "utf8"));

describe("os enfeites da ilha", () => {
  for (const cm of [CMU_MVP, CMU]) test(`E-G0: os objetos de hoje nao mudam (layout ${cm.layout.nome})`, () => {
    expect(JSON.parse(JSON.stringify(ilhaDe(cm).objetos))).toEqual(GABARITO[cm.layout.nome]);
  });
});

describe("onde ficam os enfeites (E-G10, desde a planta A)", () => {
  for (const cm of [CMU_MVP, CMU]) test(`os postes nos pontos da planta e os marcos espalhados pela moldura (layout ${cm.layout.nome})`, () => {
    const ilha = ilhaDe(cm), P = PLANTA_ILHA;
    for (const nome of Object.keys(ENFEITES_MODELOS) as (keyof typeof ENFEITES_MODELOS)[])
      expect(ilha.enfeites.filter(e => e.nome === nome).length, nome).toBe(ENFEITES_GRADE[nome].quantos);
    /* IL-3: os postes so na praca e no caminho do cais, em chao plano */
    const postes = ilha.enfeites.filter(e => e.nome === "poste");
    expect(postes.map(e => [e.x, e.z])).toEqual(P.postes.map(p => [p[0], p[1]]));
    for (const e of postes) expect(["grama", "caminho", "areia"]).toContain(ilha.cel(Math.floor(e.x), Math.floor(e.z))!.tipo);
    /* IL-4 revista: cada marco num canto da moldura (o carro a oeste, a geladeira na areia do sul, o trilho a leste do rio), no chao dele,
       perto do ponto da planta, fora dos caminhos e das clareiras dos lugares, e longe uns dos outros */
    const marcos = ilha.enfeites.filter(e => e.nome !== "poste"), marco = (n: string) => marcos.find(e => e.nome === n)!;
    expect(marco("carro").x).toBeLessThan(0);
    expect(marco("geladeira").z).toBeGreaterThanOrEqual(ilha.area.h);
    expect(marco("trilho").x).toBeGreaterThanOrEqual(ilha.rioX + RIO.largura);
    for (const n of ["carro", "geladeira", "trilho"] as const) {
      const e = marco(n), G = ENFEITES_GRADE[n], c = ilha.cel(Math.floor(e.x), Math.floor(e.z))!;
      expect(ilha.naArea(Math.floor(e.x), Math.floor(e.z)), n).toBe(false);
      expect(G.chao as readonly string[], n).toContain(c.tipo);
      expect(Math.hypot(e.x - P.marcos[n].ponto[0], e.z - P.marcos[n].ponto[1]), n).toBeLessThanOrEqual(P.marcos.busca);
      for (const l of ilha.lugares) expect(Math.hypot(l.x - e.x, l.z - e.z), `${n} e ${l.nome}`).toBeGreaterThanOrEqual(P.lugares[l.nome].clareira + G.clareira);
      for (const l of ilha.caminhos) for (let k = 1; k < l.length; k++) {
        const [ax, az] = l[k - 1], [bx, bz] = l[k], dx = bx - ax, dz = bz - az, q = dx * dx + dz * dz;
        const t = Math.max(0, Math.min(1, ((e.x - ax) * dx + (e.z - az) * dz) / q));
        expect(Math.hypot(ax + t * dx - e.x, az + t * dz - e.z), n).toBeGreaterThan(P.raioCaminho + G.clareira);
      }
    }
    for (let i = 0; i < marcos.length; i++) for (let j = i + 1; j < marcos.length; j++)
      expect(Math.hypot(marcos[i].x - marcos[j].x, marcos[i].z - marcos[j].z), `${marcos[i].nome} e ${marcos[j].nome}`).toBeGreaterThan(20);
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

/* o carro feito a mao (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 15): sai do script, sem IA, e continua um marco de um draw call so */
describe("o carro feito a mao por script", () => {
  test("a procedencia aponta o carro_mao.py e a malha e uma so, com uma textura", () => {
    const g = JSON.parse(readFileSync(join(ENF, ENFEITES_MODELOS.carro.arquivos[0]), "utf8")) as Gltf;
    expect(g.asset.extras?.gerado_por_ia).toBe(false);
    expect(g.asset.extras?.gerador).toMatch(/docs\/objetos3d\/carro\/mao\/carro_mao\.py/);
    expect(g.meshes.length).toBe(1); expect(g.meshes[0].primitives.length).toBe(1); expect(g.images?.length).toBe(1);
    expect(ENFEITES_LUZ.carro).toBeUndefined();
  });
});

/* a geladeira feita a mao (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 16): sai do script, sem IA, com os solidos e o atlas do carro */
describe("a geladeira feita a mao por script", () => {
  test("a procedencia aponta o geladeira_mao.py e a malha e uma so, com uma textura", () => {
    const g = JSON.parse(readFileSync(join(ENF, ENFEITES_MODELOS.geladeira.arquivos[0]), "utf8")) as Gltf;
    expect(g.asset.extras?.gerado_por_ia).toBe(false);
    expect(g.asset.extras?.gerador).toMatch(/docs\/objetos3d\/geladeira\/mao\/geladeira_mao\.py/);
    expect(g.meshes.length).toBe(1); expect(g.meshes[0].primitives.length).toBe(1); expect(g.images?.length).toBe(1);
    expect(ENFEITES_LUZ.geladeira).toBeUndefined();
  });
});
