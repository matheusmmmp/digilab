/* MMO0, a medida Chrome x Node (docs/PLANO_V3_MMO.md, secao 12; decide a regra da MMO-5): vidas roteirizadas gravadas no Chrome instalado
   (o mesmo canal do e2e) e conferidas no Node (scripts/mmo0/conferir.ts). Sem servidor e sem tela: o motor roda numa pagina em branco.
   Metade das vidas com o DigiBrain modular (o padrao dos ovos novos) e metade com o cerebro A (a escolha de Ajustes). So engenharia: um
   processo do Node e um Chrome, nenhuma run de pesquisa.
     node scripts/medir_mmo0.ts          # grava scripts/medicoes/mmo0_chrome_node.json */
import { mkdirSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";
import { empacotar } from "./mmo0/empacotar.ts";
import { conferir } from "./mmo0/conferir.ts";
import { MARCO_A_CADA, PASSOS_MAX, type Vida } from "./mmo0/vida.ts";

/** 20 vidas: as sementes 101 a 110 com o modular e 111 a 120 com o A (PROPOSTO, SEM FONTE; as sementes sao as dos testes) */
const VIDAS: { semente: number; cerebro: "modular" | "a" }[] = Array.from({ length: 20 }, (_, i) => ({ semente: 101 + i, cerebro: i < 10 ? "modular" : "a" }));

const pacote = await empacotar();
const navegador = await chromium.launch({ channel: "chrome", headless: true });
const pagina = await navegador.newPage();
await pagina.goto("about:blank");
await pagina.addScriptTag({ path: pacote });
const versaoChrome = navegador.version();
const resultados = [];
for (const x of VIDAS) {
  const v = await pagina.evaluate(([s, c]) => (globalThis as unknown as { MMO0: { viver: (s: number, c: string) => unknown } }).MMO0.viver(s, c),
    [x.semente, x.cerebro] as const) as Vida;
  const r = { ...conferir(v), msChrome: v.ms };
  console.log(JSON.stringify(r));
  resultados.push(r);
}
await navegador.close();

const soma = (f: (r: typeof resultados[number]) => boolean) => resultados.filter(f).length;
const saida = {
  gerado_por: "web/app/scripts/medir_mmo0.ts", commit: execSync("git rev-parse --short HEAD").toString().trim(), data: new Date().toISOString().slice(0, 10),
  maquina: { cpu: os.cpus()[0]?.model ?? "?", nucleos: os.cpus().length, plataforma: `${process.platform} ${os.release()}` },
  node: process.version, chrome: versaoChrome, passosMax: PASSOS_MAX, marcoACada: MARCO_A_CADA,
  total: {
    vidas: resultados.length, eventos: resultados.reduce((a, r) => a + r.eventos, 0), lutas: resultados.reduce((a, r) => a + r.lutas, 0),
    aceitas: soma(r => r.aceito), mesmaAssinatura: soma(r => r.mesmaAssinatura), mesmoRegistro: soma(r => r.mesmoRegistro),
    lutasIguais: resultados.reduce((a, r) => a + r.lutasIguais, 0), lutasDiferentes: resultados.reduce((a, r) => a + r.lutasDiferentes, 0),
    vidasComNumerosDiferentesNoEstado: soma(r => r.numerosDiferentes > 0),
    vidasComNaoNumericosDiferentes: soma(r => r.assinaturaNaoNumericos > 0),
    maiorDiferencaRelativaNaAssinatura: Math.max(...resultados.map(r => r.assinaturaMaiorDiferencaRelativa)),
  },
  vidas: resultados,
  nota: "a vida e gravada no Chrome (pacote do Vite numa pagina em branco) e conferida no Node: o replay oficial (Motor.reproduzir), a assinatura no fim e a cada 50 passos, o resultado de cada luta e o registro que o Node grava vivendo o mesmo roteiro. numerosDiferentes: os numeros do estado do pet (m.e) que diferem no fim; maiorDiferencaRelativa = |a-b| / max(|a|,|b|). O roteiro nao e um jogador: sem o tempo real, o pular uma hora, a bola, levar o pet nem a troca de ilha",
};
const DEST = fileURLToPath(new URL("./medicoes/", import.meta.url));
mkdirSync(DEST, { recursive: true });
writeFileSync(DEST + "mmo0_chrome_node.json", JSON.stringify(saida, null, 1) + "\n");
console.log(JSON.stringify(saida.total));
