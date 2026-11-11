// A aritmetica da luta da POC pela fonte (a D-7; docs/TAREFA_V3_LUTA_POC.md, secao 3.2, mudanca 1): o nucleo motor/arena/ so faz + - x /
// e as funcoes de Math que o IEEE 754 arredonda exato (sqrt) ou que nao arredondam (min, max, floor, ceil, round, abs). Math.hypot,
// Math.sin, Math.pow, Math.exp e o ** podem sair diferentes entre motores de JavaScript: com eles, o mesmo log daria outra luta noutro
// navegador. O seno vem de um polinomio fixo (aritmetica.ts) e o fatorRitmo da POC vem pronto na tabela (fr, tools/gerar_tabela_arena.py).
import { test } from "vitest";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const DIR = fileURLToPath(new URL("../motor/arena/", import.meta.url));
const FONTES = readdirSync(DIR).filter(f => f.endsWith(".ts"));
const MATH_PERMITIDAS = ["sqrt", "min", "max", "floor", "ceil", "round", "abs"];
const codigo = s => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "").replace(/`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, '""');

test("pela fonte: so Math.sqrt, min, max, floor, ceil, round e abs; nada de ** nem de Math.<constante>", () => {
  const achados = [];
  for (const f of FONTES) {
    const c = codigo(readFileSync(DIR + f, "utf8"));
    for (const m of c.matchAll(/\bMath\s*\.\s*([A-Za-z0-9_]+)/g)) if (!MATH_PERMITIDAS.includes(m[1])) achados.push(`${f}: Math.${m[1]}`);
    if (/\*\*/.test(c)) achados.push(`${f}: **`);
    if (/\bMath\s*\[/.test(c)) achados.push(`${f}: Math[...]`);
  }
  assert.deepEqual(achados, []);
});

test("o teste pela fonte pega as funcoes de fora (controle)", () => {
  const c = codigo("const a = Math.hypot(1, 2); const b = Math.sin(x); /* Math.pow */ const s = \"Math.exp\"; const d = 2 ** 3;");
  const pegas = [...c.matchAll(/\bMath\s*\.\s*([A-Za-z0-9_]+)/g)].map(m => m[1]).filter(n => !MATH_PERMITIDAS.includes(n));
  assert.deepEqual(pegas, ["hypot", "sin"]);
  assert.ok(/\*\*/.test(c));
});

test("seno: perto do Math.sin em toda a faixa que a luta usa (fase da IA ate milhares de radianos, mare da Praia)", async () => {
  const { seno, dist } = await import("../motor/arena/aritmetica.ts");
  let pior = 0;
  for (let i = -20000; i <= 200000; i++) { const x = i * 0.0137; pior = Math.max(pior, Math.abs(seno(x) - Math.sin(x))); }
  assert.ok(pior < 1e-13, `pior diferenca ${pior}`);
  assert.equal(seno(0), 0);
  for (const x of [0.3, 1.2, 2.9, 40.7, 1234.5]) assert.equal(seno(-x), -seno(x));
  assert.ok(Math.abs(seno(3.141592653589793 / 6) - 0.5) < 1e-15);
  assert.equal(dist(3, 4), 5);
  assert.equal(dist(0, 0), 0);
});

test("a tabela: o fr de cada golpe e o fatorRitmo da POC com os kGolpe e kProj do EQ, e o gerador usa os mesmos", async () => {
  const { FORMAS_ARENA, EQ } = await import("../motor/arena/index.ts");
  const fr = g => Math.pow(Math.max(0.2, g.t) / 0.5, EQ.kGolpe) * (g.proj ? Math.pow(30 / (g.proj.vel || 30), EQ.kProj) : 1);
  for (const [k, f] of Object.entries(FORMAS_ARENA)) for (const g of [f.golpe, f.habilidade].filter(Boolean))
    assert.ok(Math.abs(g.fr - fr(g)) <= 1e-15 * fr(g), `${k}: fr ${g.fr} contra ${fr(g)}`);
  const py = readFileSync(fileURLToPath(new URL("../../../tools/gerar_tabela_arena.py", import.meta.url)), "utf8");
  assert.equal(Number(py.match(/^K_GOLPE = ([\d.]+)$/m)[1]), EQ.kGolpe);
  assert.equal(Number(py.match(/^K_PROJ = ([\d.]+)$/m)[1]), EQ.kProj);
});
