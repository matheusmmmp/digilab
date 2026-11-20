/* O custo do replay de uma vida com muitas lutas da POC (docs/TAREFA_V3_LUTA_POC.md, LP2, item 7): pets v21 que cuidam e lutam sem parar
   (a Arena, uma forma do estagio por vez, os 8 mapas em rodizio), ate MAX_LUTAS lutas ou ate o pet morrer (20 lesoes num estagio matam:
   CLE.lesoesMorte). Para cada vida: o tempo de Motor.reproduzir do registro inteiro, o de uma vida igual sem as lutas (o mesmo cuidado), e a
   diferenca por luta. No Node do engines, um processo. So engenharia, nenhuma run de pesquisa.
     node scripts/medir_replay_lp2.ts     # grava scripts/medicoes/replay_lp2.json */
import { mkdirSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { IDS_CENA, Motor, PetMorto, VERSAO_V21, hashSemente, type EventoRegistro } from "../motor/index.ts";

const SEMENTES = [101, 202, 303], MAX_LUTAS = 1000, REPETICOES = 3;
const PRODUTO = { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true };

/** a vida: cuidado a cada passo de 10 ticks e, ja Rookie, uma luta por passo; `comLutas` falso: o mesmo cuidado, sem lutar */
function viver(semente: number, comLutas: boolean, passos: number | null): { log: EventoRegistro[]; lutas: number; passos: number; morreu: boolean } {
  const m = new Motor(semente, VERSAO_V21);
  m.ligarProduto(PRODUTO); m.trocarCerebro("modular"); m.ligarPonteLuta(true);
  let lutas = 0, p = 0;
  for (; passos === null ? lutas < MAX_LUTAS && !m.morte : p < passos; p++) {
    m.avancar(10);
    try {
      if (m.e.fome < .6) m.deixarComida("racao", Math.max(0, Math.min(1023, m.mundo!.pet[0] + 24)), m.mundo!.pet[1]);
      if (m.e.sujeira >= 2) m.observar("limpar");
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
      if (comLutas && m.estagioAtual !== "bebe" && !m.morte) {
        const rv = m.rivaisArenaPoc();
        m.lutarPoc(rv[lutas % rv.length], hashSemente("medir-replay-lp2", semente, lutas), IDS_CENA[lutas % IDS_CENA.length]);
        lutas++;
      }
    } catch (err) { if (err instanceof PetMorto) break; /* o motor recusou (dormindo, por exemplo): segue */ }
    if (m.morte) break;
  }
  return { log: JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], lutas, passos: p, morreu: !!m.morte };
}
function tempoReplay(semente: number, log: EventoRegistro[]): number {
  Motor.reproduzir(semente, log, VERSAO_V21);   // aquecimento
  const ts: number[] = [];
  for (let k = 0; k < REPETICOES; k++) { const t = performance.now(); Motor.reproduzir(semente, log, VERSAO_V21); ts.push(performance.now() - t); }
  return ts.sort((a, b) => a - b)[Math.floor(ts.length / 2)];
}

const vidas = SEMENTES.map(s => {
  const com = viver(s, true, null), sem = viver(s, false, com.passos);
  const msCom = tempoReplay(s, com.log), msSem = tempoReplay(s, sem.log);
  const r = { semente: s, lutas: com.lutas, passos: com.passos, morreu: com.morreu, eventos: com.log.length,
    msReplayComLutas: +msCom.toFixed(1), msReplaySemLutas: +msSem.toFixed(1), msPorLuta: +((msCom - msSem) / com.lutas).toFixed(3) };
  console.log(JSON.stringify(r));
  return r;
});
const saida = {
  gerado_por: "web/app/scripts/medir_replay_lp2.ts", commit: execSync("git rev-parse --short HEAD").toString().trim(), data: new Date().toISOString().slice(0, 10),
  maquina: { cpu: os.cpus()[0]?.model ?? "?", nucleos: os.cpus().length, plataforma: `${process.platform} ${os.release()}` }, node: process.version,
  maxLutas: MAX_LUTAS, repeticoes: REPETICOES, vidas,
  msPorLutaMedia: +(vidas.reduce((a, v) => a + v.msPorLuta, 0) / vidas.length).toFixed(3),
  nota: "a mediana de 3 replays; msPorLuta = (replay com as lutas - replay da mesma vida sem elas) / lutas, o custo que a luta acrescenta ao replay (o nucleo, os numeros e a ponte). As vidas acabam pela morte por lesao (20 lesoes num estagio, CLE.lesoesMorte) antes das MAX_LUTAS. O celular segue SEM FONTE",
};
const DEST = fileURLToPath(new URL("./medicoes/", import.meta.url));
mkdirSync(DEST, { recursive: true });
writeFileSync(DEST + "replay_lp2.json", JSON.stringify(saida, null, 1) + "\n");
console.log(`replay_lp2.json: ${saida.msPorLutaMedia} ms por luta no replay`);
