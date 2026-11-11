/* O estilo Digital da ilha (docs/TAREFA_V3_MAPA_DIGITAL.md, D1): o ceu pintado em public/mapa_digital/ tem a procedencia (D-G2: o
   License.txt com a Meshy e a marca de IA) e cabe no orcamento de um item (300 KB); o estilo usa a mesma grade da ilha (o gate D-G0 e o
   E-G0 do test/ilha_enfeites.test.ts, que confere os objetos de hoje contra o gabarito). */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { ENFEITES_MODELOS, MODELOS } from "../src/telas/pet/ilha/modelos.ts";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { DIGITAL } from "../src/telas/pet/ilha/constantes.ts";
import { lugaresDasParticulas, paresDosFios, segmentosDosFios } from "../src/telas/pet/ilha/digitalConta.ts";
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

  /* D4 revista (2026-11-10, docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 17): a lata gigante saiu do horizonte do Digital e virou um marco da
     grade (ENFEITES_MODELOS.lata; os gates do arquivo e do lugar em test/ilha_enfeites.test.ts). Aqui: o estilo nao tem mais a lata propria */
  test("D4 revista: o Digital nao tem mais a lata do horizonte", () => {
    expect("lata" in DIGITAL).toBe(false);
    expect(existsSync(join(PASTA, "lata"))).toBe(false);
    expect(ENFEITES_MODELOS.lata.arquivos[0]).toBe("lata/lata.gltf");
  });
});
