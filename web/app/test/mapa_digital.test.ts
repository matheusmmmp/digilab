/* O estilo Digital da ilha (docs/TAREFA_V3_MAPA_DIGITAL.md, D1): o ceu pintado em public/mapa_digital/ tem a procedencia (D-G2: o
   License.txt com a Meshy e a marca de IA) e cabe no orcamento de um item (300 KB); o estilo usa a mesma grade da ilha (o gate D-G0 e o
   E-G0 do test/ilha_enfeites.test.ts, que confere os objetos de hoje contra o gabarito). */
import { readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";

const PASTA = join(__dirname, "..", "public", "mapa_digital");

describe("o estilo Digital", () => {
  test("D-G2: o ceu pintado com a procedencia e no orcamento", () => {
    expect(statSync(join(PASTA, "ceu.jpg")).size).toBeLessThanOrEqual(300 * 1024);
    const lic = readFileSync(join(PASTA, "License.txt"), "utf8");
    expect(lic).toMatch(/Meshy/); expect(lic).toMatch(/gerada por IA/);
  });
});
