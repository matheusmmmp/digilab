/* PI2 (docs/PLANO_V3_CONTA_PROTECAO.md, PI-4): confere o build do jogo. Falha se houver algum source map (um ".map" ou um
   "sourceMappingURL" no JS) e se algum JS nao comecar pelo aviso de autoria (scripts/autoria.ts). O "npm run build" roda isto
   depois do vite build, entao o CI (job web) reprova um build com mapa ou sem o aviso.
   Confere tambem o aviso de mineracao reservada (PI-6, o TDMRep; servidor_web/src/protecao/tdmrep.ts, D-CONTA-231 a 234): o
   .well-known/tdmrep.json, o _headers do Pages com o tdm-reservation e a meta no index.html, para o Vite nao deixar de copiar a pasta
   com ponto nem o _headers.
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

/** o aviso de mineracao reservada no build (PI-6): o que falta */
export function conferirTdm(pasta: string): string[] {
  const problemas: string[] = [];
  const ler = (c: string): string | null => (existsSync(join(pasta, c)) ? readFileSync(join(pasta, c), "utf8").replaceAll("\r\n", "\n") : null);
  const tdmrep = ler(".well-known/tdmrep.json");
  let regras: unknown = null;
  try { regras = tdmrep === null ? null : JSON.parse(tdmrep); } catch { /* cai no problema abaixo */ }
  const ok = Array.isArray(regras) && regras.some(r => typeof r === "object" && r !== null && (r as Record<string, unknown>).location === "/"
    && (r as Record<string, unknown>)["tdm-reservation"] === 1);
  if (!ok) problemas.push("sem o .well-known/tdmrep.json com {location: \"/\", tdm-reservation: 1} no build");
  if (!/^\/\*\n {2}tdm-reservation: 1$/m.test(ler("_headers") ?? "")) problemas.push("sem o tdm-reservation: 1 em /* no _headers do build");
  if (!(ler("index.html") ?? "").includes('<meta name="tdm-reservation" content="1">')) problemas.push("sem a meta tdm-reservation no index.html");
  return problemas;
}

/** os problemas do build em `pasta` (vazio = passou) */
export function conferirBuild(pasta: string): string[] {
  if (!existsSync(pasta)) return [`a pasta do build nao existe: ${pasta}`];
  const todos = arquivos(pasta);
  const problemas: string[] = conferirTdm(pasta);
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
  console.log(`conferir_build: ok (${pasta}): sem source map, todo JS com o aviso de autoria, com o aviso TDMRep`);
}
