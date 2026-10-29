/* A medicao de equilibrio da arena em tempo real (docs/TAREFA_V2_UP_ARENA.md, item 4), no Node do engines (24, que roda TypeScript sem
   dependencia nova). Le os dados do jogo de D:\Trab\digilab\Assets\arena_up\dados (fora do git; Assets\gerar_arena_up.py) e grava as
   tabelas em scripts/medicoes/arena_<modo>.json.
     node scripts/medir_arena.ts --modo unico    # passo A (P1): a sequencia unica do prototipo; confere com o gabarito e sai com 1 se diferir
     node scripts/medir_arena.ts --modo fluxos   # passo B: os fluxos do jogo; so grava (comparacao em distribuicao, sem calibrar: D5)
   O metodo e as sementes sao os do arena_equilibrio.md (o harness recuperado na etapa 0). A rodada inteira nao roda no CI. */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import {
  IDS_CENA, PARES_ESTAGIOS, conferirDados, cruzar, medirArenas, rodizio, type DadosArena, type ModoSorteio,
} from "../arena/index.ts";

const args = process.argv.slice(2);
const modo = (args[args.indexOf("--modo") + 1] ?? "") as ModoSorteio;
if (!["unico", "fluxos"].includes(modo)) throw new Error("uso: node scripts/medir_arena.ts --modo unico|fluxos");
const PASTA = new URL("../../../../Assets/arena_up/dados/", import.meta.url);
const ler = (n: string) => { const b = readFileSync(new URL(n + ".json", PASTA)); return { j: JSON.parse(b.toString("utf8")), sha: createHash("sha256").update(b).digest("hex") }; };
const arqs = Object.fromEntries(["status", "golpes", "atributos", "atlas"].map(n => [n, ler(n)]));
const dados = { status: arqs.status.j, golpes: arqs.golpes.j, atributos: arqs.atributos.j, atlas: arqs.atlas.j } as DadosArena;
const recuos = conferirDados(dados);

const t0 = Date.now();
const estagios = ["InTraining2", "Rookie", "Champion", "Ultimate", "Mega"];
const saida = {
  modo, gerado_por: "web/app/scripts/medir_arena.ts", node: process.version,
  dados: Object.fromEntries(Object.entries(arqs).map(([n, a]) => [n + ".json", a.sha])),
  recuos: { tag: recuos.tag.length, semGolpe: recuos.semGolpe.length, semStatus: recuos.semStatus.length },
  arenas_semente_7: medirArenas(dados, IDS_CENA, 10, 7, modo),
  arenas_semente_42: medirArenas(dados, IDS_CENA, 10, 42, modo),
  campo_por_semente: Object.fromEntries([42, 99, 123].map(sd => { const r = medirArenas(dados, ["campo"], 10, sd, modo).campo; return [sd, { azul: r.azul, dur: r.dur }]; })),
  rodizio_sementes_7_8: Object.fromEntries(estagios.map(e => [e, rodizio(dados, e, [7, 8], modo)])),
  estagios: Object.fromEntries(PARES_ESTAGIOS.map(([a, b]) => [`${b}>${a}`, cruzar(dados, a, b, modo)])),
  niveis_champion_nv1_contra_rookie: Object.fromEntries([2, 3, 5].map(nv => [nv, cruzar(dados, "Rookie", "Champion", modo, nv, 1)])),
  segundos: 0,
};
saida.segundos = Math.round((Date.now() - t0) / 1000);
const DESTINO = fileURLToPath(new URL("./medicoes/", import.meta.url));
mkdirSync(DESTINO, { recursive: true });
writeFileSync(DESTINO + `arena_${modo}.json`, JSON.stringify(saida, null, 1) + "\n");
console.log(`arena_${modo}.json gravado (${saida.segundos} s)`);

if (modo === "unico") {
  /* passo A: tudo o que o gabarito tem tem de sair igual */
  const gab = JSON.parse(readFileSync(new URL("./arena_gabarito_prototipo.json", import.meta.url), "utf8"));
  const dif: string[] = [];
  const comparar = (onde: string, esperado: unknown, obtido: unknown) => {
    if (esperado !== null && typeof esperado === "object") { for (const k of Object.keys(esperado)) comparar(`${onde}.${k}`, (esperado as any)[k], (obtido as any)?.[k]); return; }
    if (esperado !== obtido) dif.push(`${onde}: prototipo ${JSON.stringify(esperado)}, porte ${JSON.stringify(obtido)}`);
  };
  for (const k of Object.keys(gab)) if (k !== "fonte") comparar(k, gab[k], (saida as any)[k]);
  if (dif.length) { console.error(`PARIDADE FALHOU (${dif.length}):\n` + dif.join("\n")); process.exit(1); }
  console.log("paridade com o prototipo: tudo igual ao gabarito");
}
