/* PI2 (docs/PLANO_V3_CONTA_PROTECAO.md, PI-4): o conferidor do build (scripts/conferir_build.ts) reprova um ".map" no dist/, um JS
   que aponta para um source map e um JS sem o aviso de autoria; o "npm run build" roda o conferidor no dist/ de verdade. */
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { AVISO_AUTORIA } from "../scripts/autoria.ts";
import { conferirBuild } from "../scripts/conferir_build.ts";

const pastas: string[] = [];
function dist(arquivos: Record<string, string>): string {
  const pasta = mkdtempSync(join(tmpdir(), "digilab-dist-"));
  pastas.push(pasta);
  for (const [nome, texto] of Object.entries(arquivos)) {
    mkdirSync(join(pasta, nome, ".."), { recursive: true });
    writeFileSync(join(pasta, nome), texto);
  }
  return pasta;
}
afterEach(() => { for (const p of pastas.splice(0)) rmSync(p, { recursive: true, force: true }); });

describe("PI2: o conferidor do build", () => {
  it("passa num build com o aviso e sem mapa", () => {
    expect(conferirBuild(dist({ "index.html": "<html></html>", "assets/index-a1.js": AVISO_AUTORIA + "\nvar a=1;" }))).toEqual([]);
  });

  it("reprova um .map no dist/", () => {
    const p = conferirBuild(dist({ "assets/index-a1.js": AVISO_AUTORIA + "\nvar a=1;", "assets/index-a1.js.map": "{}" }));
    expect(p.some(x => x.startsWith("source map no build"))).toBe(true);
  });

  it("reprova um JS que aponta para um source map", () => {
    const p = conferirBuild(dist({ "assets/x.js": AVISO_AUTORIA + "\nvar a=1;\n//# sourceMappingURL=x.js.map" }));
    expect(p.some(x => x.startsWith("JS aponta para um source map"))).toBe(true);
  });

  it("reprova um JS sem o aviso no topo", () => {
    const p = conferirBuild(dist({ "assets/x.js": "var a=1;\n" + AVISO_AUTORIA }));
    expect(p.some(x => x.startsWith("JS sem o aviso de autoria"))).toBe(true);
  });

  it("reprova um dist/ sem JS ou que nao existe", () => {
    expect(conferirBuild(dist({ "index.html": "" })).length).toBeGreaterThan(0);
    expect(conferirBuild(join(tmpdir(), "digilab-dist-nao-existe-pi2")).length).toBeGreaterThan(0);
  });

  it("o vite.config segue sem source map, com o aviso e o conferidor no npm run build", () => {
    const config = readFileSync(new URL("../vite.config.ts", import.meta.url), "utf8");
    expect(config).toMatch(/sourcemap:\s*false/);
    expect(config).toContain("avisoAutoria()");
    const pacote = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8"));
    expect(pacote.scripts.build).toBe("vite build && node scripts/conferir_build.ts");
    expect(AVISO_AUTORIA.startsWith("/*!")).toBe(true);
    expect(AVISO_AUTORIA.endsWith("*/")).toBe(true);
    expect(AVISO_AUTORIA).toContain("Matheus de Medeiros Pereira");
  });
});
