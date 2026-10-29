// Arena sem DOM (docs/TAREFA_V2_UP_ARENA.md, secao 10.4): a simulacao nao toca em janela, documento, armazenamento, rede nem relogio,
// nem no Math.random (todo sorteio vem dos fluxos com semente), e so importa de dentro de arena/ e do motor/ (a RNG). A checagem de
// tipos usa a lib ES sem "dom" (tsconfig.json inclui arena/), entao qualquer API do navegador tambem quebra `npm run tipos`.
import { test } from "vitest";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const DIR = fileURLToPath(new URL("../arena/", import.meta.url));
const FONTES = readdirSync(DIR).filter(f => f.endsWith(".ts"));
const PROIBIDOS = ["window", "document", "localStorage", "sessionStorage", "indexedDB", "navigator", "fetch", "XMLHttpRequest",
  "requestAnimationFrame", "setTimeout", "setInterval", "HTMLElement", "HTMLCanvasElement", "Image", "location", "globalThis", "Date", "performance",
  "Math.random"];

/* tira comentarios e textos entre aspas para nao acusar palavra dentro de texto */
const codigo = s => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "").replace(/`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, '""');

test("a arena tem os modulos esperados", () => {
  for (const f of ["sim.ts", "rng.ts", "constantes.ts", "cenas.ts", "dados.ts", "tipos.ts", "index.ts"]) assert.ok(FONTES.includes(f), f);
});

test("nenhuma API do navegador, relogio nem Math.random na arena", () => {
  const achados = [];
  for (const f of FONTES) {
    const c = codigo(readFileSync(DIR + f, "utf8"));
    for (const p of PROIBIDOS) if (new RegExp(`(?<![\\w.])${p.replace(".", "\\.")}(?![\\w])`).test(c)) achados.push(`${f}: ${p}`);
  }
  assert.deepEqual(achados, []);
});

test("a arena so importa de arena/ e da RNG do motor; o motor nao importa da arena", () => {
  const fora = [];
  for (const f of FONTES) for (const m of readFileSync(DIR + f, "utf8").matchAll(/from\s+"([^"]+)"/g))
    if (!m[1].startsWith("./") && !["../motor/rng.ts", "../motor/mundo.ts"].includes(m[1])) fora.push(`${f}: ${m[1]}`);
  assert.deepEqual(fora, []);
  const MOTOR = fileURLToPath(new URL("../motor/", import.meta.url));
  for (const f of readdirSync(MOTOR).filter(f => f.endsWith(".ts"))) assert.ok(!/from\s+"\.\.\/arena\//.test(readFileSync(MOTOR + f, "utf8")), f);
});

test("a arena carrega e luta num contexto sem nada de navegador", async () => {
  const A = await import("../arena/index.ts");
  assert.equal(typeof globalThis.window, "undefined");
  const d = JSON.parse(readFileSync(new URL("./arena_sintetico.json", import.meta.url), "utf8"));
  const r = A.lutarAteOFim(A.configCpu("coliseu", ["Alfa", "Beta", "Gama"], ["Delta", "Alfa", "Beta"]), d, A.sorteiosPorFluxo(4242));
  assert.ok(r.relogio > 0);
});
