/* O custo do replay da batalha em tempo real (docs/ESPEC_COMBATE_TR.md, item 4; COMBATE-TR, etapa R0), no Node do engines (24, que roda
   TypeScript sem dependencia nova) e no Chrome instalado (o @playwright/test do e2e, channel "chrome", headless). A mesma bancada
   (scripts/replay_tr_bancada.ts) roda nos dois; no Chrome, este script serve os .ts com os tipos apagados (node:module
   stripTypeScriptTypes) e os dados de D:\Trab\digilab\Assets\arena_up\dados (fora do git), so em 127.0.0.1. Grava
   scripts/medicoes/replay_tr.json.
     node scripts/medir_replay_tr.ts            # Node e Chrome
     node scripts/medir_replay_tr.ts --so-node  # so o Node
   Falha alto se os dados faltarem, se o Chrome nao abrir ou se o Node e o Chrome derem lutas diferentes (a impressao das lutas). */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createServer } from "node:http";
import { stripTypeScriptTypes } from "node:module";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import os from "node:os";
import { conferirDados, type DadosArena } from "../arena/index.ts";
import { bancada, type ResultadoBancada } from "./replay_tr_bancada.ts";

const soNode = process.argv.includes("--so-node");
const APP = new URL("../", import.meta.url);
const PASTA = new URL("../../../../Assets/arena_up/dados/", import.meta.url);
const NOMES = ["status", "golpes", "atributos", "atlas"] as const;
const brutos = Object.fromEntries(NOMES.map(n => [n, readFileSync(new URL(n + ".json", PASTA))])) as Record<typeof NOMES[number], Buffer>;
const dados = Object.fromEntries(NOMES.map(n => [n, JSON.parse(brutos[n].toString("utf8"))])) as unknown as DadosArena;
conferirDados(dados);

/* ---------------------------------------------------------------- Node */
console.log("Node: medindo...");
const node = bancada(dados, () => performance.now());
console.log(`Node: 1x1 ${node.luta1x1.msPorLuta} ms/luta, 3x3 ${node.luta3x3.msPorLuta} ms/luta`);

/* ---------------------------------------------------------------- Chrome */
async function noChrome(): Promise<{ versao: string; r: ResultadoBancada }> {
  const pagina = `<!doctype html><meta charset="utf-8"><title>bancada</title><script type="module">
    import { bancada } from "/scripts/replay_tr_bancada.ts";
    const ler = n => fetch("/dados/" + n + ".json").then(r => r.json());
    const [status, golpes, atributos, atlas] = await Promise.all(["status", "golpes", "atributos", "atlas"].map(ler));
    try { window.resultado = bancada({ status, golpes, atributos, atlas }, () => performance.now()); } catch (e) { window.erro = String(e && e.stack || e); }
  </script>`;
  const srv = createServer((req, res) => {
    const url = new URL(req.url ?? "/", "http://x");
    try {
      if (url.pathname === "/") { res.writeHead(200, { "content-type": "text/html; charset=utf-8" }); res.end(pagina); return; }
      const m = url.pathname.match(/^\/dados\/(status|golpes|atributos|atlas)\.json$/);
      if (m) { res.writeHead(200, { "content-type": "application/json" }); res.end(brutos[m[1] as typeof NOMES[number]]); return; }
      if (/^\/(arena|motor|scripts)\/[\w/]+\.ts$/.test(url.pathname)) {
        const js = stripTypeScriptTypes(readFileSync(new URL("." + url.pathname, APP), "utf8"));
        res.writeHead(200, { "content-type": "text/javascript; charset=utf-8" }); res.end(js); return;
      }
      if (/^\/motor\/[\w/]+\.json$/.test(url.pathname)) {
        res.writeHead(200, { "content-type": "application/json" }); res.end(readFileSync(new URL("." + url.pathname, APP))); return;
      }
      res.writeHead(404); res.end();
    } catch (e) { res.writeHead(500); res.end(String(e)); }
  });
  await new Promise<void>(ok => srv.listen(0, "127.0.0.1", ok));
  const porta = (srv.address() as { port: number }).port;
  const { chromium } = await import("@playwright/test");
  const nav = await chromium.launch({ channel: "chrome", headless: true });
  try {
    const p = await nav.newPage();
    const erros: string[] = [];
    p.on("pageerror", e => erros.push(String(e)));
    await p.goto(`http://127.0.0.1:${porta}/`);
    await p.waitForFunction(() => (window as any).resultado || (window as any).erro, null, { timeout: 600_000, polling: 1000 });
    const erro = await p.evaluate(() => (window as any).erro);
    if (erro || erros.length) throw new Error("Chrome: " + (erro ?? erros.join("\n")));
    return { versao: nav.version(), r: await p.evaluate(() => (window as any).resultado) };
  } finally { await nav.close(); srv.close(); }
}

let chrome: { versao: string; r: ResultadoBancada } | null = null;
if (!soNode) {
  console.log("Chrome: medindo...");
  chrome = await noChrome();
  console.log(`Chrome ${chrome.versao}: 1x1 ${chrome.r.luta1x1.msPorLuta} ms/luta, 3x3 ${chrome.r.luta3x3.msPorLuta} ms/luta`);
  for (const k of ["luta1x1", "luta3x3"] as const)
    if (chrome.r[k].impressao !== node[k].impressao) throw new Error(`${k}: o Chrome deu lutas diferentes do Node (${chrome.r[k].impressao} contra ${node[k].impressao})`);
}

/* ---------------------------------------------------------------- a vida: N lutas no replay */
/* o custo de refazer N lutas = N x (simulacao + controlador a cada R passos, os dois lados); R = 16 passos (256 ms), o ritmo PROPOSTO na espec */
const R_PASSOS = 16, NS = [10, 50, 100, 200, 500, 1000];
function vida(r: ResultadoBancada, passosPorLuta: number) {
  const msLuta = passosPorLuta * r.luta3x3.usPorPasso / 1000 + (passosPorLuta / R_PASSOS) * 2 * r.controlador.usPorChamada / 1000;
  return { passosPorLuta, msPorLuta: +msLuta.toFixed(2), segundos: Object.fromEntries(NS.map(n => [n, +(n * msLuta / 1000).toFixed(2)])),
    turnosSegundos: Object.fromEntries(NS.map(n => [n, +(n * r.turnos.msPorLuta / 1000).toFixed(3)])) };
}
const extrapolar = (r: ResultadoBancada) => ({
  "luta_100s_6250_passos": vida(r, 6250),
  "luta_1x1_natural": vida(r, r.luta1x1.passosMedio),
  "luta_300s_limite": vida(r, 18750),
});

const saida = {
  gerado_por: "web/app/scripts/medir_replay_tr.ts", data: new Date().toISOString().slice(0, 10),
  maquina: { cpu: os.cpus()[0]?.model ?? "?", nucleos: os.cpus().length, plataforma: `${os.platform()} ${os.release()}` },
  dados: Object.fromEntries(NOMES.map(n => [n + ".json", createHash("sha256").update(brutos[n]).digest("hex")])),
  ritmo_controlador_passos: R_PASSOS,
  node: { versao: process.version, ...node, vida: extrapolar(node) },
  chrome: chrome ? { versao: chrome.versao, ...chrome.r, vida: extrapolar(chrome.r) } : null,
  node_e_chrome_iguais: chrome ? true : null,
};
const DESTINO = fileURLToPath(new URL("./medicoes/", import.meta.url));
mkdirSync(DESTINO, { recursive: true });
writeFileSync(DESTINO + "replay_tr.json", JSON.stringify(saida, null, 1) + "\n");
console.log("replay_tr.json gravado");
