/* Quem confere os envios (MMO3, D-CONTA-86). A rota pede a um Conferidor; o do servidor é o worker (ConferidorEmWorker): um só, com os
   envios em fila, para a conferência não prender o laço de eventos. O conferirAqui roda no mesmo processo (os testes que não medem o worker).
   O worker nasce no primeiro envio e não segura o processo (unref). Se ele cair, os envios em andamento falham alto, e o próximo envio
   abre outro. */
import { Worker } from "node:worker_threads";
import { conferir, type Conferencia, type EntregueComHash, type Envio } from "./conferir.ts";

/** confere um envio com as sementes ranqueadas entregues àquele pet (MMO4) */
export type Conferidor = (envio: Envio, entregues: readonly EntregueComHash[]) => Promise<Conferencia>;

/** no mesmo processo, sem worker */
export const conferirAqui: Conferidor = async (envio, entregues) => conferir(envio, entregues);

export class ConferidorEmWorker {
  private worker: Worker | null = null;
  private proximo = 0;
  private readonly pendentes = new Map<number, { aceitar: (r: Conferencia) => void; recusar: (e: Error) => void }>();

  /** o Conferidor deste worker, para passar à rota */
  readonly conferir: Conferidor = (envio, entregues) => new Promise<Conferencia>((aceitar, recusar) => {
    const id = ++this.proximo;
    this.pendentes.set(id, { aceitar, recusar });
    this.abrir().postMessage({ id, envio, entregues });
  });

  /** quantos envios estão na fila do worker */
  get naFila(): number { return this.pendentes.size; }

  private abrir(): Worker {
    if (this.worker) return this.worker;
    const w = new Worker(new URL("./trabalhador.ts", import.meta.url));
    w.unref();
    w.on("message", (m: { id: number; r?: Conferencia; erro?: string }) => {
      const p = this.pendentes.get(m.id);
      if (!p) return;
      this.pendentes.delete(m.id);
      if (m.erro !== undefined) p.recusar(new Error(`a conferência falhou no worker: ${m.erro}`));
      else p.aceitar(m.r!);
    });
    const cair = (motivo: string) => {
      if (this.worker === w) this.worker = null;
      for (const p of this.pendentes.values()) p.recusar(new Error(`o worker da conferência caiu: ${motivo}`));
      this.pendentes.clear();
    };
    w.on("error", err => cair(err.message));
    w.on("exit", codigo => cair(`saiu com o código ${codigo}`));
    this.worker = w;
    return w;
  }

  /** fecha o worker (os testes e o fim do servidor) */
  async fechar(): Promise<void> {
    const w = this.worker;
    this.worker = null;
    if (w) await w.terminate();
  }
}
