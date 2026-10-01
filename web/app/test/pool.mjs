// Pool de workers dos scripts de calibracao da fase 3 (test/conferir_liga.mjs, test/conferir_fabrica_salao.mjs): o mesmo arquivo do script
// roda como worker (isMainThread falso) e responde {i, t} com {i, r}. No maximo 8 workers por padrao (com 18 o Node caiu com falha de
// segmentacao no Windows, test/medir_itens.mjs); DIGILAB_WORKERS muda. Deterministico: a ordem das respostas nao muda o resultado.
import { Worker, parentPort } from "node:worker_threads";
import { availableParallelism } from "node:os";

/** o lado do worker: cada mensagem {i, t} vira {i, r: trabalhos[t.tipo](t)} */
export function servir(trabalhos) {
  parentPort.on("message", ({ i, t }) => {
    const f = trabalhos[t.tipo];
    if (!f) throw new Error("tarefa desconhecida: " + t.tipo);
    parentPort.postMessage({ i, r: f(t) });
  });
}

/** o lado principal: executar(tarefas) -> Promise dos resultados, na ordem; fechar() encerra os workers */
export function criarPool(url, workerData = {}) {
  const W = Number(process.env.DIGILAB_WORKERS ?? Math.min(8, Math.max(1, availableParallelism() - 2))), pool = [];
  let ocupado = null;
  const executar = tarefas => new Promise((ok, falha) => {
    const out = new Array(tarefas.length);
    if (!tarefas.length) { ok(out); return; }
    while (pool.length < Math.min(W, tarefas.length)) {
      const w = new Worker(url, { workerData });
      w.on("message", m => ocupado.aoReceber(w, m));
      w.on("error", err => ocupado.aoFalhar(err));
      pool.push(w);
    }
    let feitas = 0, envio = 0;
    const mandar = w => { if (envio < tarefas.length) { const i = envio++; w.postMessage({ i, t: tarefas[i] }); } };
    ocupado = {
      aoReceber: (w, { i, r }) => { out[i] = r; if (++feitas === tarefas.length) ok(out); else mandar(w); },
      aoFalhar: err => falha(err),
    };
    for (const w of pool) mandar(w);
  });
  return { executar, fechar: () => Promise.all(pool.map(w => w.terminate())) };
}
