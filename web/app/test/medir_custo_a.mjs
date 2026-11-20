// A medicao pontual do A v11 no navegador (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, etapa 1b; o G-CUSTO do
// docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secao 5.4, e o orcamento da docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 12; AF-4). So
// desempenho, uma vez, sem nenhuma medida comportamental (Matheus, 2026-10-25): o tempo por decisao (a decisao inteira e so o cerebro) e
// o do replay de 14 dias do pet v12 do jogo, que roda o A v11. E a referencia do orcamento: o cerebro modular <= 2x o cerebro do A; o
// replay de 14 dias da v13 <= 1,5x o da v12, no mesmo aparelho e no mesmo navegador.
//
//   node --experimental-strip-types test/medir_custo_a.mjs     # grava test/custo_a_v11_navegador.json
//
// A pagina (test/medir_custo_a_pagina.ts) e empacotada pelo Vite num modulo so e roda no Chrome instalado (o do e2e), sem janela, numa
// origem com isolamento (COOP e COEP), para o performance.now ter a resolucao fina. Nada do jogo muda: a pagina importa o motor.
import { writeFileSync } from "node:fs";
import { cpus, totalmem, release, platform } from "node:os";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";
import { build } from "vite";

const SEMENTE = 101, DIAS = 14, REPETICOES = 7;
const ENTRADA = fileURLToPath(new URL("./medir_custo_a_pagina.ts", import.meta.url));
const SAIDA = new URL("./custo_a_v11_navegador.json", import.meta.url);

const out = await build({
  configFile: false, logLevel: "silent",
  build: { write: false, minify: false, lib: { entry: ENTRADA, formats: ["es"], fileName: "medir" } },
});
const codigo = (Array.isArray(out) ? out[0] : out).output.find(o => o.type === "chunk").code;

const navegador = await chromium.launch({ channel: "chrome", headless: true });
const pagina = await navegador.newPage();
await pagina.route("http://medir.localhost/**", r => r.request().url().endsWith("/medir.js")
  ? r.fulfill({ contentType: "text/javascript", headers: { "Cross-Origin-Resource-Policy": "same-origin" }, body: codigo })
  : r.fulfill({ contentType: "text/html", headers: { "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp" },
                body: '<!doctype html><meta charset="utf-8"><script type="module" src="/medir.js"></script>' }));
await pagina.goto("http://medir.localhost/");
await pagina.waitForFunction(() => typeof globalThis.medirCustoA === "function");
const medida = await pagina.evaluate(([s, d, r]) => globalThis.medirCustoA(s, d, r), [SEMENTE, DIAS, REPETICOES]);
const versao = navegador.version();
await navegador.close();

/* a conferencia no Node desta maquina, com o relogio fino: cada chamada do cerebro dura poucos us, perto da resolucao de 5 us do
   performance.now do navegador isolado; a fracao do cerebro na decisao tem de sair parecida nos dois */
await import("./medir_custo_a_pagina.ts");
const node = globalThis.medirCustoA(SEMENTE, DIAS, REPETICOES);

const saida = {
  descricao: "a medicao pontual do A v11 no navegador (G-CUSTO, AF-4): so desempenho, uma vez; o pet v12 do jogo (o Motor, o mundo do "
    + "produto e o A v11), o dono do botao Alimentar; a decisao inteira (o avancar / as decisoes), o cerebro (o tempo dentro dos metodos do "
    + "braco do A, embrulhados so nesta medida) e o replay de 14 dias pelo log (Motor.reproduzir); as medianas de " + REPETICOES + " repeticoes",
  data: new Date().toISOString().slice(0, 10),
  aparelho: { cpu: cpus()[0]?.model ?? null, nucleos: cpus().length, memoria_gb: Math.round(totalmem() / 2 ** 30), sistema: `${platform()} ${release()}` },
  navegador: { nome: "Google Chrome (o instalado, sem janela, pelo Playwright)", versao },
  ...medida,
  conferencia_node: { versao: process.version, decisao_us: node.decisao_us.mediana, cerebro_us: node.cerebro_us.mediana,
                      replay_ms: node.replay_ms.mediana },
};
writeFileSync(SAIDA, JSON.stringify(saida, null, 1) + "\n");
console.log(JSON.stringify(saida, null, 1));
