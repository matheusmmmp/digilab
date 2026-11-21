/* PI2 (docs/PLANO_V3_CONTA_PROTECAO.md, PI-4): o conferidor do build (scripts/conferir_build.ts) reprova um ".map" no dist/, um JS
   que aponta para um source map e um JS sem o aviso de autoria; o "npm run build" roda o conferidor no dist/ de verdade. */
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import { AVISO_AUTORIA } from "../scripts/autoria.ts";
import { conferirBuild, conferirTdm } from "../scripts/conferir_build.ts";

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
/* o aviso de mineracao reservada (PI-6), como o build de verdade o traz de public/ e do index.html */
const TDM = {
  ".well-known/tdmrep.json": '[\n  {\n    "location": "/",\n    "tdm-reservation": 1\n  }\n]\n',
  "_headers": "# comentario\n/*\n  tdm-reservation: 1\n",
  "index.html": '<html><head><meta name="tdm-reservation" content="1"></head></html>',
};
afterEach(() => { for (const p of pastas.splice(0)) rmSync(p, { recursive: true, force: true }); });

describe("PI2: o conferidor do build", () => {
  it("passa num build com o aviso e sem mapa", () => {
    expect(conferirBuild(dist({ ...TDM, "assets/index-a1.js": AVISO_AUTORIA + "\nvar a=1;" }))).toEqual([]);
  });

  it("PI-6: reprova o build sem o tdmrep.json, com a reserva em 0, sem o _headers ou sem a meta", () => {
    expect(conferirTdm(dist(TDM))).toEqual([]);
    const sem = (tira: keyof typeof TDM) => conferirTdm(dist(Object.fromEntries(Object.entries(TDM).filter(([k]) => k !== tira))));
    expect(sem(".well-known/tdmrep.json")).toEqual([expect.stringContaining("tdmrep.json")]);
    expect(sem("_headers")).toEqual([expect.stringContaining("_headers")]);
    expect(sem("index.html")).toEqual([expect.stringContaining("meta")]);
    const zero = conferirTdm(dist({ ...TDM, ".well-known/tdmrep.json": '[{"location": "/", "tdm-reservation": 0}]' }));
    expect(zero).toEqual([expect.stringContaining("tdmrep.json")]);
    expect(conferirTdm(dist({ ...TDM, ".well-known/tdmrep.json": '{"location": "/", "tdm-reservation": 1}' })).length).toBe(1);
  });

  it("PI-6: o public/ e o index.html do jogo trazem o aviso (o servidor_web/scripts/gerar_robots.ts os grava)", () => {
    const publico = fileURLToPath(new URL("../public/", import.meta.url));
    const pasta = dist({});
    mkdirSync(join(pasta, ".well-known"), { recursive: true });
    for (const c of [".well-known/tdmrep.json", "_headers"]) writeFileSync(join(pasta, c), readFileSync(join(publico, c)));
    writeFileSync(join(pasta, "index.html"), readFileSync(new URL("../index.html", import.meta.url)));
    expect(conferirTdm(pasta)).toEqual([]);
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
