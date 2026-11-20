/* A fronteira da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, regras 3 e 4): o three so entra por import dinamico, num chunk proprio, e o
   bundle inicial nao cresce. Confere pelos imports: so as cenas 3D (cena3d.ts, a ilha e o mapa da Exploracao) importam o three; so o
   cena3d.ts importa a ilha (os modulos sem three dela, como a grade e a curva, tambem so os testes leem); ninguem importa o cena3d.ts
   de forma estatica (o CenarioPet o carrega por import()); a ilha nao importa o POC. */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, test } from "vitest";

const SRC = join(__dirname, "..", "src");
const arquivos = (dir: string): string[] => readdirSync(dir).flatMap(n => statSync(join(dir, n)).isDirectory() ? arquivos(join(dir, n)) : /\.tsx?$/.test(n) ? [join(dir, n)] : []);
const estaticos = (f: string) => [...readFileSync(f, "utf8").matchAll(/^\s*import\s[^;]*?from\s+["']([^"']+)["']/gm)].map(m => m[1]);
const rel = (f: string) => relative(SRC, f).replaceAll("\\", "/");

describe("a fronteira da ilha", () => {
  test("so as cenas 3D importam o three", () => {
    const com = arquivos(SRC).filter(f => estaticos(f).some(i => i === "three" || i.startsWith("three/"))).map(rel).sort();
    expect(com.every(f => f === "telas/pet/cena3d.ts" || f.startsWith("telas/pet/ilha/") || f === "telas/lutar/mapa3d.ts"), com.join(", ")).toBe(true);
  });

  test("so o cena3d.ts importa a ilha, e ninguem importa o cena3d.ts de forma estatica", () => {
    for (const f of arquivos(SRC)) {
      const r = rel(f), imps = estaticos(f);
      if (!r.startsWith("telas/pet/ilha/") && r !== "telas/pet/cena3d.ts") expect(imps.some(i => i.includes("ilha/")), r).toBe(false);
      expect(imps.some(i => /cena3d(\.ts)?$/.test(i)), r).toBe(false);
      if (r.startsWith("telas/pet/ilha/")) expect(imps.some(i => i.includes("poc/")), r).toBe(false);
    }
    expect(readFileSync(join(SRC, "telas", "pet", "CenarioPet.tsx"), "utf8")).toMatch(/import\("\.\/cena3d\.ts"\)/);
  });
});
