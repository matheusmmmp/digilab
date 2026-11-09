// A luta da POC no motor sem DOM e atras da chave (docs/TAREFA_V3_LUTA_POC.md, LP1): o nucleo motor/arena/ nao toca em janela,
// documento, armazenamento, rede nem relogio; so importa de dentro de motor/arena/ e da RNG do motor; e, com a chave LUTA_POC_LIGADA
// desligada, nada do jogo importa dele (o motor/index.ts nao o reexporta, e nenhuma tela o le). A checagem de tipos usa a lib ES sem
// "dom" (tsconfig.json inclui motor/**), entao qualquer API do navegador tambem quebra `npm run tipos`.
import { test } from "vitest";
import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const DIR = fileURLToPath(new URL("../motor/arena/", import.meta.url));
const FONTES = readdirSync(DIR).filter(f => f.endsWith(".ts"));
const PROIBIDOS = ["window", "document", "localStorage", "sessionStorage", "indexedDB", "navigator", "fetch", "XMLHttpRequest",
  "requestAnimationFrame", "setTimeout", "setInterval", "HTMLElement", "HTMLCanvasElement", "Image", "location", "globalThis", "Date", "performance",
  "Math.random"];

/* tira comentarios e textos entre aspas para nao acusar palavra dentro de texto */
const codigo = s => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "").replace(/`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, '""');

test("o nucleo tem os modulos esperados", () => {
  for (const f of ["sim.ts", "rng.ts", "constantes.ts", "cenas.ts", "aritmetica.ts", "formas.ts", "luta.ts", "tipos.ts", "nucleo.ts", "index.ts"])
    assert.ok(FONTES.includes(f), f);
});

test("nenhuma API do navegador, relogio nem Math.random no nucleo", () => {
  const achados = [];
  for (const f of FONTES) {
    const c = codigo(readFileSync(DIR + f, "utf8"));
    for (const p of PROIBIDOS) if (new RegExp(`(?<![\\w.])${p.replace(".", "\\.")}(?![\\w])`).test(c)) achados.push(`${f}: ${p}`);
  }
  assert.deepEqual(achados, []);
});

test("o nucleo so importa de motor/arena/ e da RNG do motor", () => {
  const fora = [];
  for (const f of FONTES) for (const m of readFileSync(DIR + f, "utf8").matchAll(/from\s+"([^"]+)"/g))
    if (!m[1].startsWith("./") && !["../rng.ts", "../mundo.ts"].includes(m[1])) fora.push(`${f}: ${m[1]}`);
  assert.deepEqual(fora, []);
});

test("chave desligada: LUTA_POC_LIGADA e false; no motor, so o Motor (a luta dos pets v21), o luta_poc e o index leem o nucleo (LP2); nenhuma tela o importa direto", async () => {
  const A = await import("../motor/arena/index.ts");
  assert.equal(A.LUTA_POC_LIGADA, false);
  const APP = fileURLToPath(new URL("../", import.meta.url));
  const quem = [];
  const varrer = d => {
    for (const f of readdirSync(d)) {
      const p = join(d, f);
      if (statSync(p).isDirectory()) { if (p !== join(APP, "motor", "arena") && f !== "node_modules") varrer(p); continue; }
      if (/\.(ts|tsx|mjs|js)$/.test(f) && /from\s+"[^"]*\/arena\/(index|sim|luta|formas)\.ts"|from\s+"\.\/arena\//.test(readFileSync(p, "utf8"))) quem.push(p.slice(APP.length));
    }
  };
  for (const d of ["motor", "src"]) varrer(join(APP, d));
  assert.deepEqual(quem.map(p => p.split("\\").join("/")).sort(), ["motor/index.ts", "motor/luta_poc.ts", "motor/motor.ts"]);
});

test("o nucleo carrega e luta num contexto sem nada de navegador", async () => {
  const A = await import("../motor/arena/index.ts");
  assert.equal(typeof globalThis.window, "undefined");
  const st = { hp: 900, atk: 100, def: 50, vel: 70, cad: 2000, crit: 10, hcd: 8, hpot: 2, esquiva: 0, atordoa: 0, erro: 18 };
  const r = A.lutar({ cena: "coliseu", a: { forma: "cirro_crianca_arisco", stats: st }, b: { forma: "brasa_crianca_sereno", stats: st }, semente: 4242 });
  assert.ok(r.relogio > 0 && r.fim);
});
