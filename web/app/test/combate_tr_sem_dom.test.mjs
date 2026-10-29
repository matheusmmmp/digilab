// A luta em tempo real sem DOM e com a aritmetica restrita (docs/ESPEC_COMBATE_TR.md, item 4 e D-7): o nucleo motor/combate_tr/ nao toca
// em janela, documento, armazenamento, rede nem relogio, nem no Math.random; so importa do motor; e so faz + - x / e as funcoes de Math
// que o IEEE 754 arredonda exato (sqrt) ou que nao arredondam (min, max, floor, ceil, abs). Math.hypot, Math.sin, Math.pow, Math.exp e o
// ** podem sair diferentes entre motores de JavaScript: com eles, o mesmo log daria outra luta no Safari ou no Firefox.
import { test } from "vitest";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const DIR = fileURLToPath(new URL("../motor/combate_tr/", import.meta.url));
const FONTES = readdirSync(DIR).filter(f => f.endsWith(".ts"));
const PROIBIDOS = ["window", "document", "localStorage", "sessionStorage", "indexedDB", "navigator", "fetch", "XMLHttpRequest",
  "requestAnimationFrame", "setTimeout", "setInterval", "HTMLElement", "HTMLCanvasElement", "Image", "location", "globalThis", "Date", "performance"];
const MATH_PERMITIDAS = ["sqrt", "min", "max", "floor", "ceil", "abs"];

/* tira comentarios e textos entre aspas para nao acusar palavra dentro de texto */
const codigo = s => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "").replace(/`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, '""');

test("o nucleo tem os modulos esperados", () => {
  for (const f of ["luta.ts", "controlador.ts", "constantes_tr.ts", "index.ts"]) assert.ok(FONTES.includes(f), f);
});

test("nenhuma API do navegador nem relogio no nucleo", () => {
  const achados = [];
  for (const f of FONTES) {
    const c = codigo(readFileSync(DIR + f, "utf8"));
    for (const p of PROIBIDOS) if (new RegExp(`(?<![\\w.])${p}(?![\\w])`).test(c)) achados.push(`${f}: ${p}`);
  }
  assert.deepEqual(achados, []);
});

test("D-7: so + - x / e as funcoes exatas de Math; nada de **, Math.random nem Math.hypot/sin/pow/exp/log", () => {
  const achados = [];
  for (const f of FONTES) {
    const c = codigo(readFileSync(DIR + f, "utf8"));
    for (const m of c.matchAll(/\bMath\s*\.\s*(\w+)/g)) if (!MATH_PERMITIDAS.includes(m[1])) achados.push(`${f}: Math.${m[1]}`);
    if (/\*\*/.test(c)) achados.push(`${f}: **`);
  }
  assert.deepEqual(achados, []);
});

test("o nucleo so importa de dentro do motor, e a arena do UP nunca", () => {
  const fora = [];
  for (const f of FONTES) for (const m of readFileSync(DIR + f, "utf8").matchAll(/from\s+"([^"]+)"/g)) {
    const caminho = m[1];
    const ok = caminho.startsWith("./") || (/^\.\.\/[\w]+\.ts$/.test(caminho));
    if (!ok) fora.push(`${f}: ${caminho}`);
  }
  assert.deepEqual(fora, []);
});
