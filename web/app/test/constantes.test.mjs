// Teste de constantes (TAREFA_FRONT_TS, Etapa 1): as constantes do motor web contra os parametros do
// Python (gabaritos/constantes_python.json, de experiments/exportar_constantes_web.py) e contra as
// configs de experimento que o web adota (V21C da validacao). Tabela em mapa_constantes.json.
//
// Roda contra as constantes do motor em TS (web/app/motor/constantes.ts) e, enquanto o HTML existir, contra
// as do motor extraido do HTML. Falha em qualquer diferenca e em qualquer folha numerica nova fora da tabela.
//
// uso: npm test (em web/app)
import { test } from "vitest";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { carregarMotor } from "./motor_html.mjs";
import * as MOTOR_TS from "../motor/index.ts";

const aqui = p => fileURLToPath(new URL(p, import.meta.url));
const lerJson = p => JSON.parse(readFileSync(p, "utf8"));
const RAIZ_REPO = aqui("../../../");

const MAPA = lerJson(aqui("./mapa_constantes.json"));
const PY = lerJson(aqui("./gabaritos/constantes_python.json"));
/* objetos de constantes do motor web cobertos pela tabela (todas as folhas numericas de cada um) */
const RAIZES = ["C", "CB", "CTP", "CDJ", "CME", "CEM", "CVI", "COB", "CTR", "APTIDAO", "CSO", "CCOND", "CD", "CT", "CA", "CE",
  "CV", "CV21", "CAT", "CCP", "GA", "DUR_EVO", "CHAMADO_BEBE", "BASE_CARATER", "DESLOC_CARATER", "CAMPANHA", "LUGARES"];
/* so no motor em TS: pets v4 (educacao-v1) e v5 (evolucao canonica) nao existem no HTML; conferidas so contra o
   Python (as v5 quase todas so_web) */
const RAIZES_V4 = ["CED", "CLE", "CHE", "DUR_CLASSICA", "CMG", "CAMPANHA_V5", "LUGARES_V5", "CCF"];
const FONTES = [["ts", MOTOR_TS], ["html", carregarMotor(RAIZES)]];
const raizDe = cam => cam.match(/^[^.[]+/)[0];

/** folhas numericas: lista so de numeros conta como uma folha; o resto desce com .campo ou [i] */
function folhas(o, cam, saida) {
  if (typeof o === "number") saida.set(cam, o);
  else if (Array.isArray(o)) {
    if (o.length && o.every(x => typeof x === "number")) saida.set(cam, o);
    else o.forEach((x, i) => folhas(x, `${cam}[${i}]`, saida));
  } else if (o && typeof o === "object") for (const [k, v] of Object.entries(o)) folhas(v, cam ? `${cam}.${k}` : k, saida);
  return saida;
}
function pegar(o, caminho) {
  for (const p of caminho.match(/[^.[\]]+/g)) {
    if (o === null || typeof o !== "object" || !(p in o)) throw new Error(`caminho inexistente: ${caminho} (parou em ${p})`);
    o = o[p];
  }
  return o;
}
/* mesma tolerancia do gerador da tabela: igualdade exata, ou 1e-12 relativo (conversoes por minuto do C) */
const igual = (a, b) => typeof a === "number" && typeof b === "number" ? a === b || Math.abs(a - b) <= 1e-12 * Math.max(Math.abs(a), Math.abs(b))
  : Array.isArray(a) && Array.isArray(b) && a.length === b.length && a.every((x, i) => igual(x, b[i]));

const LISTAS = ["pares", "convertidos", "experimento", "so_web"];
const folhasDe = (WEB, raizes = RAIZES) => { const f = new Map(); for (const r of raizes) { if (!(r in WEB)) throw new Error("constante ausente: " + r); folhas(WEB[r], r, f); } return f; };

test("ts = html: as mesmas folhas numericas, com os mesmos valores", () => {
  const [ts, html] = FONTES.map(([, W]) => folhasDe(W));
  assert.deepEqual([...ts.keys()], [...html.keys()]);
  /* JSON: as listas do HTML vem de outro realm (vm) e o deepEqual estrito compara o prototipo */
  for (const [k, v] of html) assert.equal(JSON.stringify(ts.get(k)), JSON.stringify(v), k);
});

for (const [fonte, WEB] of FONTES) {
  const soTs = fonte === "ts";
  const WEB_FOLHAS = folhasDe(WEB, soTs ? [...RAIZES, ...RAIZES_V4] : RAIZES);
  /* no HTML, as entradas das raizes v4 nao se aplicam */
  const aplica = e => soTs || !RAIZES_V4.includes(raizDe(e.web));

  test(`${fonte}: toda folha numerica do web aparece em exatamente uma lista da tabela`, () => {
    const vistos = new Map();
    for (const L of LISTAS) for (const e of MAPA[L].filter(aplica)) {
      assert.ok(!vistos.has(e.web), `${e.web} aparece em ${vistos.get(e.web)} e em ${L}`);
      vistos.set(e.web, L);
    }
    const semTabela = [...WEB_FOLHAS.keys()].filter(k => !vistos.has(k));
    const semWeb = [...vistos.keys()].filter(k => !WEB_FOLHAS.has(k));
    assert.deepEqual(semTabela, [], "constantes do web fora da tabela");
    assert.deepEqual(semWeb, [], "entradas da tabela que nao existem mais no web");
  });

  test(`${fonte}: pares: valor do web = padrao do Python`, () => {
    const erros = [];
    for (const e of MAPA.pares.filter(aplica)) {
      const w = WEB_FOLHAS.get(e.web), p = pegar(PY, e.py);
      if (!igual(w, p)) erros.push(`${e.web} = ${JSON.stringify(w)} × ${e.py} = ${JSON.stringify(p)}`);
    }
    assert.deepEqual(erros, []);
  });

  test(`${fonte}: convertidos: sinal e indice de lugar`, () => {
    const CONV = { sinal: p => ({ ">=0": 1, "<0": -1 })[p], indice_base0: p => p - 1 };
    const erros = [];
    for (const e of MAPA.convertidos) {
      const f = CONV[e.conversao];
      if (!f) throw new Error("conversao desconhecida: " + e.conversao);
      const w = WEB_FOLHAS.get(e.web), p = pegar(PY, e.py);
      if (!igual(w, f(p))) erros.push(`${e.web} = ${w} × ${e.py} = ${JSON.stringify(p)} (${e.conversao})`);
    }
    assert.deepEqual(erros, []);
  });

  test(`${fonte}: experimento: valor do web = config de experimento adotada`, () => {
    const erros = [];
    for (const e of MAPA.experimento) {
      const w = WEB_FOLHAS.get(e.web), p = pegar(lerJson(RAIZ_REPO + e.arquivo), e.chave);
      if (!igual(w, p)) erros.push(`${e.web} = ${w} × ${e.arquivo}:${e.chave} = ${p}`);
    }
    assert.deepEqual(erros, []);
  });

  test(`${fonte}: so_web: toda entrada explica por que nao tem par`, () => {
    for (const e of MAPA.so_web) assert.ok(typeof e.nota === "string" && e.nota.length > 10, `${e.web} sem nota`);
  });

}

test("o teste pega uma diferenca (controle negativo)", () => {
  const e = MAPA.pares[0], p = pegar(PY, e.py);
  assert.ok(!igual(folhasDe(MOTOR_TS).get(e.web) * (1 + 1e-9), p));
});
