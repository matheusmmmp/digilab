/* Diagnostico da fase 3 (P-3; docs/EQUILIBRIO_COMBATE_TR.md): a lista do pet tipico de uma forma do Ultimate (a candidata da fase 2) antes e
   depois de 4 series contra o rival sugerido do estagio (o mesmo caminho de fase3_estagio.ts), com a nota de cada regra. So diagnostico.
   uso (em web/app): npx tsx scripts/equilibrio_tr/diagnostico_ordem_f3.ts <forma> --saida <arquivo.json> */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { execSync } from "node:child_process";
import {
  CIT, CV21E_TR, GambitsPet, LINHA_DA_FORMA, LISTAS_V14, LUGARES_V6, RELOGIO_V14, STATS, arenaDaLuta, caraterCanonico, gambitsAdulto,
  hashSemente, jogarSerie, lutadorBot, perfilDe, regraDe, rotuloRegra, type FormaAdultaNormal,
} from "../../motor/index.ts";
import { ligarEscala } from "../../motor/catalogo.ts";

ligarEscala(true);
const R = { ...CV21E_TR, relogio: RELOGIO_V14 }, f = process.argv[2] as FormaAdultaNormal, i = process.argv.indexOf("--saida"), saida = i < 0 ? null : process.argv[i + 1];
if (!LINHA_DA_FORMA[f] || !saida) throw new Error("uso: <forma adulta> --saida <arquivo.json>");
const forma = { esp: "brasa", est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[f], adulta: f } as const;
const lista = LISTAS_V14[f] ?? gambitsAdulto(f, R), gp = new GambitsPet();
gp.chipsNoFim = true; gp.semear(forma, f, R, lista);
const tip = CIT.tipico.adulto!, cond = perfilDe(forma, caraterCanonico(f), 1, Object.fromEntries(STATS.map(k => [k, tip / STATS.length])) as never, true, 13);
const rival = LUGARES_V6.find(L => L.est === "adulto")!.rivais[0], arena = arenaDaLuta(rival, 13), B = lutadorBot(rival, R, arena);
const foto = () => gp.ativas.map(k => ({ nota: Math.round(gp.notas[k] * 1000) / 1000, regra: rotuloRegra(regraDe(k)) }));
const antes = foto(), resultados: number[] = [];
for (let ev = 0; ev < 4; ev++) {
  const u = gp.ativas.slice(), serie = jogarSerie({ nome: "pet", estilo: gp.estilo(), cond }, Array.from({ length: arena?.lutas ?? 1 }, () => B),
    hashSemente("equilibrio-tr-diagnostico", 68101, ev), R, 1, null);
  serie.forEach((r, j) => { gp.aprender(r, hashSemente("equilibrio-tr-diagnostico-aprender", ev, j), u); resultados.push(r.pontosA); });
}
const out = { gerado_por: "web/app/scripts/equilibrio_tr/diagnostico_ordem_f3.ts", commit: execSync("git rev-parse --short HEAD").toString().trim(),
  forma: f, rival, resultados, trocas: gp.mudancas.filter(x => x.texto.startsWith("trocou")).length, antes, depois: foto() };
mkdirSync(dirname(saida), { recursive: true });
writeFileSync(saida, JSON.stringify(out, null, 1) + "\n");
console.log(JSON.stringify(out, null, 1));
