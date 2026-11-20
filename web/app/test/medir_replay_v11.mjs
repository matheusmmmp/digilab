// O replay de uma vida longa do v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 6: "o tamanho do save e do replay"; etapa 4, item 7).
// Mede o tempo que o laco do corpo em TS (motor/motor_corpo.ts) leva para refazer, pelo log, uma vida do v11 de DIAS dias, e o tamanho do
// log em JSON. So descritivo: nao e paridade nem run de pesquisa (o pet e o do ponto do v11; o dono e um roteiro fixo, sem rng).
//
//   node test/medir_replay_v11.mjs          # grava artifacts_v2_w_porte/replay_v11.json (na raiz do repositorio)
//
// O dono do roteiro: 16 contatos por dia (o orcamento das vidas do gabarito), um a cada 90 minutos, na ordem alimentar, limpar, brincar,
// acariciar, com um tapa a cada oito contatos no lugar do acariciar. O tempo e o do Node nesta maquina; o celular fica para o e2e da
// etapa 5 (o Chrome difere do Node so no ultimo bit de exp e log, que o nucleo nao usa, mas o tempo depende do aparelho).
import { writeFileSync, mkdirSync } from "node:fs";
import { cpus } from "node:os";
import { CLB, CLB_V11 } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { BracoConsequencia, CerebroA } from "../motor/lobos.ts";
import { MotorCorpo } from "../motor/motor_corpo.ts";

const DIAS = 60;
const SEMENTE = 101;          // uma semente dos testes
const REPETICOES = 5;
const PASSO = 15;             // o avanco de cada evento, o intervalo da decisao
const CONTATO_A_CADA = 90;    // minutos: 16 contatos por dia
const ROTEIRO = ["alimentar", "limpar", "brincar", "acariciar"];

function braco() {
  const co = CCO_CORPO_V11;
  const cerebro = new CerebroA({
    aprendizadoLigado: true, ...CLB,
    aprendiz: { passo: CLB_V11.passo, teto: CLB_V11.teto, piso: CLB_V11.piso, recompensaTapa: CLB_V11.recompensaTapa },
    corpo: { ligada: co.ligada, drives_novos: co.drives_novos, gestos: co.gestos, banheiro: co.banheiro, escala_receptor: co.escala_receptor },
  });
  return new BracoConsequencia(cerebro, { drives: CLB_V11.drives, ganho: CLB_V11.ganho, canais: CLB_V11.canais, pesosDrivesCorpo: CLB_V11.pesosDrivesCorpo });
}

/** a vida ao vivo, pelo roteiro: devolve o log */
function viverAoVivo() {
  const m = new MotorCorpo(braco(), SEMENTE);
  let contatos = 0;
  while (m.estado.tick < DIAS * 1440) {
    if (m.estado.tick % CONTATO_A_CADA === 0 && m.estado.tick > 0) {
      const a = (contatos + 1) % 8 === 0 ? "tapa" : ROTEIRO[contatos % ROTEIRO.length];
      m.observar(a);
      contatos += 1;
    }
    m.avancar(PASSO);
  }
  return m;
}

const aoVivo = viverAoVivo();
const log = aoVivo.log;
const fim = JSON.stringify(aoVivo.estadoDict());
const tempos = [];
for (let r = 0; r < REPETICOES; r++) {
  const t0 = performance.now();
  const m = new MotorCorpo(braco(), SEMENTE);
  for (const e of log) m.aplicarEvento(e);
  tempos.push(performance.now() - t0);
  if (JSON.stringify(m.estadoDict()) !== fim) throw new Error("o replay nao refez a vida ao vivo");
}
tempos.sort((a, b) => a - b);
const mediana = tempos[Math.floor(REPETICOES / 2)];
const bytes = Buffer.byteLength(JSON.stringify(log), "utf8");
const saida = {
  descricao: "replay de uma vida longa do v11 pelo laco do corpo em TS (etapa 4, item 7); descritivo, so o Node desta maquina",
  dias: DIAS, semente: SEMENTE, repeticoes: REPETICOES, eventos: log.length,
  decisoes: aoVivo.acoesPet.length, contatos: log.filter((e) => e.tipo === "acao_usuario").length,
  log_json_bytes: bytes, replay_ms: tempos.map((t) => Math.round(t)), replay_ms_mediana: Math.round(mediana),
  replay_ms_por_dia: Math.round((mediana / DIAS) * 10) / 10,
  node: process.version, cpu: cpus()[0]?.model ?? null,
};
const pasta = new URL("../../../artifacts_v2_w_porte/", import.meta.url);
mkdirSync(pasta, { recursive: true });
writeFileSync(new URL("replay_v11.json", pasta), JSON.stringify(saida, null, 2) + "\n");
console.log(saida);
