/* MMO3: o tempo da conferência de uma vida no Node (src/envio/conferir.ts), sem a rota e sem o worker: o passe único do registro pela conta
   da MMO1 (refazerComLutas, D-CONTA-85) e o Tamer. Confere também, em cada vida, que esse passe dá o mesmo pet do Motor.reproduzir (a
   assinatura inteira) e mede o Motor.reproduzir sozinho, para comparar. As vidas são as roteirizadas da MMO0 (web/app/scripts/mmo0/vida.ts, as sementes
   101 a 110 com o DigiBrain modular, o dos ovos novos, e, para comparar, as 111 a 113 com o cérebro A, como na MMO0; o roteiro chega ao
   React pelo src/produto.ts, então precisa do node_modules do web/app). Cada vida é conferida REPETICOES vezes depois de uma de aquecimento; vale a mediana. Um processo só, a máquina sem outra run.
     cd servidor_web && node scripts/medir_conferencia.ts      ->  medicoes/mmo3_conferencia.json */
import { mkdirSync, writeFileSync } from "node:fs";
import { cpus } from "node:os";
import { Motor } from "../../web/app/motor/index.ts";
import { viver } from "../../web/app/scripts/mmo0/vida.ts";
import { refazerComLutas } from "../../web/app/src/ranking/pontos.ts";
import { VERSAO_TAMER } from "../../web/app/src/tamer.ts";
import { conferir, lerEnvio } from "../src/envio/conferir.ts";

const VIDAS: [number, "modular" | "a"][] = [
  ...[101, 102, 103, 104, 105, 106, 107, 108, 109, 110].map(s => [s, "modular"] as [number, "modular"]),
  ...[111, 112, 113].map(s => [s, "a"] as [number, "a"]),
];
const REPETICOES = 5;
const mediana = (xs: number[]): number => { const s = [...xs].sort((a, b) => a - b), k = s.length >> 1; return s.length % 2 ? s[k]! : (s[k - 1]! + s[k]!) / 2; };
const r2 = (v: number) => +v.toFixed(2);

const vidas = VIDAS.map(([semente, cerebro]) => {
  const v = viver(semente, cerebro);
  const envio = lerEnvio({ pet: { semente: v.semente, log: v.log, versao: v.versao }, tamer: { versao: VERSAO_TAMER, log: [] } });
  const bytes = Buffer.byteLength(JSON.stringify(envio), "utf8");
  const primeira = conferir(envio);
  if (primeira.resultado !== "aceito") throw new Error(`a vida ${semente} foi recusada: ${primeira.detalhe}`);
  const jogo = Motor.reproduzir(v.semente, v.log, v.versao);
  const mesmoPet = refazerComLutas(v.semente, v.versao, v.log, []).motor.assinatura() === jogo.assinatura();
  if (!mesmoPet) throw new Error(`a vida ${semente}: o passe único não dá o mesmo pet do Motor.reproduzir`);
  const medidas: { replay: number; tamer: number; total: number }[] = [], soReproduzir: number[] = [];
  for (let k = 0; k < REPETICOES; k++) {
    const r = conferir(envio);
    if (r.resultado !== "aceito") throw new Error(`a vida ${semente} foi recusada na repetição ${k}`);
    medidas.push(r.ms);
    const t0 = performance.now();
    Motor.reproduzir(v.semente, v.log, v.versao);
    soReproduzir.push(performance.now() - t0);
  }
  const de = (c: "replay" | "tamer" | "total") => r2(mediana(medidas.map(x => x[c])));
  const linha = { semente, cerebro, eventos: v.log.length, lutas: v.lutas.length, bytes, mesmo_pet: mesmoPet, ms_replay: de("replay"),
    ms_tamer: de("tamer"), ms_total: de("total"), ms_motor_reproduzir: r2(mediana(soReproduzir)) };
  console.log(JSON.stringify(linha));
  return linha;
});

const modular = vidas.filter(v => v.cerebro === "modular"), a = vidas.filter(v => v.cerebro === "a");
const resumo = (vs: typeof vidas) => {
  const totais = vs.map(v => v.ms_total);
  return { vidas: vs.length, ms_total_min: Math.min(...totais), ms_total_mediana: r2(mediana(totais)), ms_total_max: Math.max(...totais),
    ms_replay_mediana: r2(mediana(vs.map(v => v.ms_replay))), ms_motor_reproduzir_mediana: r2(mediana(vs.map(v => v.ms_motor_reproduzir))),
    ms_replay_por_evento_mediana: +mediana(vs.map(v => v.ms_replay / v.eventos)).toFixed(3), bytes_max: Math.max(...vs.map(v => v.bytes)) };
};
const saida = {
  medida: "MMO3: a conferência de uma vida no Node (conferir: o passe único com as lutas + o Tamer), mediana de " + REPETICOES + " repetições por vida",
  node: process.version, cpu: cpus()[0]?.model ?? "?", quando: new Date().toISOString(),
  resumo: { modular: resumo(modular), a: resumo(a) },
  vidas,
};
const pasta = new URL("../medicoes/", import.meta.url);
mkdirSync(pasta, { recursive: true });
writeFileSync(new URL("mmo3_conferencia.json", pasta), JSON.stringify(saida, null, 1) + "\n");
console.log(JSON.stringify(saida.resumo));
