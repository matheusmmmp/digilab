/* O estilo Digital da ilha (docs/TAREFA_V3_MAPA_DIGITAL.md, D1): o ceu pintado em public/mapa_digital/ tem a procedencia (D-G2: o
   License.txt com a Meshy e a marca de IA) e cabe no orcamento de um item (300 KB); o estilo usa a mesma grade da ilha (o gate D-G0 e o
   E-G0 do test/ilha_enfeites.test.ts, que confere os objetos de hoje contra o gabarito). */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { MODELOS } from "../src/telas/pet/ilha/modelos.ts";

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
});
