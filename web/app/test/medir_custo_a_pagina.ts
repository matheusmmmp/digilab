/* A pagina da medicao do custo do A v11 no navegador (test/medir_custo_a.mjs; o G-CUSTO, AF-4). So desempenho: nao le nem grava nada do
   comportamento, e nao muda o laco. O pet e o v12 do jogo (o Motor, o mundo do produto e o A v11), com o dono do botao Alimentar do
   gabarito das vidas v12 (test/v12_jogo_ts.test.ts). Duas medidas:
     - o tempo por decisao: numa vida de DIAS dias ao vivo, o tempo do avancar dividido pelas decisoes (a decisao inteira: o motor, o
       mundo, o corpo e o cerebro) e, so nesta vida, o tempo dentro dos metodos do braco do A (o cerebro), cronometrados por um embrulho
       na instancia; a vida embrulhada e conferida contra uma sem embrulho (a mesma assinatura);
     - o tempo do replay: refazer pelo log a vida de DIAS dias (Motor.reproduzir), sem embrulho, conferido pela assinatura. */
import { TPD } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";

const METODOS = ["agir", "observar", "consequenciaCorpo", "receberAcaoDono", "mudancaNoCorpo"] as const;

function viver(m: Motor, dias: number): void {
  const passos = Math.round(dias * TPD / 30);
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e;
    if (e.fome < .6 && p % 2 === 0) m.observar("alimentar");
    if (e.sujeira >= 2) m.observar("limpar");
    if (e.humor < .5 && !e.dormindo) m.observar("brincar");
    if (p % 5 === 0) m.observar("acariciar");
  }
}

/** embrulha os metodos do braco do A nesta instancia: soma o tempo dentro deles (o embrulho so cronometra) */
function cronometrarCerebro(m: Motor): { ms: number; chamadas: Record<string, number> } {
  const braco = m.v11!.braco as unknown as Record<string, (...a: unknown[]) => unknown>;
  const conta = { ms: 0, chamadas: Object.fromEntries(METODOS.map(k => [k, 0])) as Record<string, number> };
  let dentro = 0;
  for (const k of METODOS) {
    const original = braco[k].bind(braco);
    braco[k] = (...a: unknown[]) => {
      conta.chamadas[k]++;
      if (dentro++) { try { return original(...a); } finally { dentro--; } }
      const t0 = performance.now();
      try { return original(...a); } finally { conta.ms += performance.now() - t0; dentro--; }
    };
  }
  return conta;
}

const mediana = (xs: number[]) => [...xs].sort((a, b) => a - b)[Math.floor(xs.length / 2)];

function medir(semente: number, dias: number, repeticoes: number) {
  const referencia = new Motor(semente, 12);
  viver(referencia, dias);
  const assinatura = referencia.assinatura(), log = referencia.log;
  const decisaoUs: number[] = [], cerebroUs: number[] = [], replayMs: number[] = [];
  let decisoes = 0, chamadas: Record<string, number> = {};
  for (let r = 0; r < repeticoes; r++) {
    /* a decisao: a vida ao vivo, com o cerebro cronometrado (o avancar inteiro dividido pelas decisoes) */
    const m = new Motor(semente, 12), conta = cronometrarCerebro(m);
    const t0 = performance.now();
    viver(m, dias);
    const total = performance.now() - t0;
    if (m.assinatura() !== assinatura) throw new Error("a vida cronometrada saiu diferente da de referencia");
    decisoes = m.nDecisoes;
    chamadas = conta.chamadas;
    decisaoUs.push(total * 1000 / decisoes);
    cerebroUs.push(conta.ms * 1000 / decisoes);
    /* o replay, sem embrulho */
    const t1 = performance.now();
    const refeito = Motor.reproduzir(semente, log, 12);
    replayMs.push(performance.now() - t1);
    if (refeito.assinatura() !== assinatura) throw new Error("o replay nao refez a vida");
  }
  const r2 = (x: number) => Math.round(x * 100) / 100;
  return {
    semente, dias, repeticoes, decisoes, eventos: log.length, log_json_bytes: new TextEncoder().encode(JSON.stringify(log)).length,
    chamadas_do_cerebro: chamadas,
    decisao_us: { mediana: r2(mediana(decisaoUs)), todas: decisaoUs.map(r2) },
    cerebro_us: { mediana: r2(mediana(cerebroUs)), todas: cerebroUs.map(r2) },
    replay_ms: { mediana: r2(mediana(replayMs)), todas: replayMs.map(r2) },
    crossOriginIsolated: globalThis.crossOriginIsolated === true, agente: navigator.userAgent,
  };
}

(globalThis as unknown as { medirCustoA: typeof medir }).medirCustoA = medir;
