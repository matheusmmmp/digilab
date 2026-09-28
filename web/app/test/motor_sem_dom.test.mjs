// Motor sem DOM (TAREFA_FRONT_TS, Etapa 2): o motor nao toca em janela, documento, armazenamento nem rede, e
// nao importa nada de fora de web/app/motor. A checagem de tipos usa lib ES sem "dom" (tsconfig.json), entao
// qualquer uso de API do navegador tambem quebra `npm run tipos`.
import { test } from "vitest";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const DIR = fileURLToPath(new URL("../motor/", import.meta.url));
const FONTES = readdirSync(DIR).filter(f => f.endsWith(".ts"));
const PROIBIDOS = ["window", "document", "localStorage", "sessionStorage", "indexedDB", "navigator", "fetch", "XMLHttpRequest",
  "requestAnimationFrame", "setTimeout", "setInterval", "HTMLElement", "HTMLCanvasElement", "Image", "location", "globalThis", "Date", "performance"];

/* tira comentarios e textos entre aspas para nao acusar palavra dentro de texto */
const codigo = s => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "").replace(/`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, '""');

test("o motor tem os modulos esperados", () => {
  for (const f of ["motor.ts", "rng.ts", "constantes.ts", "combate.ts", "gambits_pet.ts", "index.ts"]) assert.ok(FONTES.includes(f), f);
});

test("nenhuma API do navegador nem relogio no motor", () => {
  const achados = [];
  for (const f of FONTES) {
    const c = codigo(readFileSync(DIR + f, "utf8"));
    for (const p of PROIBIDOS) if (new RegExp(`(?<![\\w.])${p}(?![\\w])`).test(c)) achados.push(`${f}: ${p}`);
  }
  assert.deepEqual(achados, []);
});

test("o motor so importa de dentro de motor/", () => {
  const fora = [];
  for (const f of FONTES) for (const m of readFileSync(DIR + f, "utf8").matchAll(/from\s+"([^"]+)"/g)) if (!m[1].startsWith("./")) fora.push(`${f}: ${m[1]}`);
  assert.deepEqual(fora, []);
});

test("o motor carrega e joga num contexto sem nada de navegador", async () => {
  const M = await import("../motor/index.ts");
  assert.equal(typeof globalThis.window, "undefined");
  const m = new M.Motor(4242);
  m.avancar(200);
  m.observar("alimentar");
  assert.equal(M.Motor.reproduzir(4242, m.log).assinatura(), m.assinatura());
});
