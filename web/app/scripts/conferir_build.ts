/* PI2 (docs/PLANO_V3_CONTA_PROTECAO.md, PI-4): confere o build do jogo. Falha se houver algum source map (um ".map" ou um
   "sourceMappingURL" no JS) e se algum JS nao comecar pelo aviso de autoria (scripts/autoria.ts). O "npm run build" roda isto
   depois do vite build, entao o CI (job web) reprova um build com mapa ou sem o aviso.
     node scripts/conferir_build.ts [pasta]      (padrao: ../dist, o outDir do vite.config.ts) */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { AVISO_AUTORIA } from "./autoria.ts";

function arquivos(pasta: string): string[] {
  const saida: string[] = [];
  for (const nome of readdirSync(pasta)) {
    const caminho = join(pasta, nome);
    if (statSync(caminho).isDirectory()) saida.push(...arquivos(caminho));
    else saida.push(caminho);
  }
  return saida;
}

/** os problemas do build em `pasta` (vazio = passou) */
export function conferirBuild(pasta: string): string[] {
  if (!existsSync(pasta)) return [`a pasta do build nao existe: ${pasta}`];
  const todos = arquivos(pasta);
  const problemas: string[] = [];
  const js = todos.filter(a => /\.(m?js)$/.test(a));
  if (js.length === 0) problemas.push(`nenhum JS no build: ${pasta}`);
  for (const a of todos) if (a.endsWith(".map")) problemas.push(`source map no build: ${relative(pasta, a)}`);
  for (const a of js) {
    const codigo = readFileSync(a, "utf8");
    if (!codigo.startsWith(AVISO_AUTORIA)) problemas.push(`JS sem o aviso de autoria no topo: ${relative(pasta, a)}`);
    if (/[#@]\s*sourceMappingURL=/.test(codigo)) problemas.push(`JS aponta para um source map: ${relative(pasta, a)}`);
  }
  return problemas;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const pasta = process.argv[2] ?? fileURLToPath(new URL("../../dist/", import.meta.url));
  const problemas = conferirBuild(pasta);
  if (problemas.length > 0) {
    console.error("conferir_build: o build reprovou (PI2)\n  " + problemas.join("\n  "));
    process.exit(1);
  }
  console.log(`conferir_build: ok (${pasta}): sem source map, todo JS com o aviso de autoria`);
}
