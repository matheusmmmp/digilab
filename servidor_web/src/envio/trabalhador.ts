/* O worker da conferência (MMO3, D-CONTA-86): roda o conferir() fora do laço de eventos do servidor, que fica livre para os outros pedidos
   enquanto um envio é refeito (perto de 1 s por vida, D-CONTA-84). Recebe {id, envio} e devolve {id, r} ou, num erro que não é recusa
   (um defeito do servidor, não do envio), {id, erro}: quem pediu levanta. */
import { parentPort } from "node:worker_threads";
import { conferir, type Envio } from "./conferir.ts";

if (!parentPort) throw new Error("o trabalhador.ts roda só como worker (conferidor.ts)");
const porta = parentPort;
porta.on("message", ({ id, envio }: { id: number; envio: Envio }) => {
  try { porta.postMessage({ id, r: conferir(envio) }); }
  catch (err) { porta.postMessage({ id, erro: err instanceof Error ? err.stack ?? err.message : String(err) }); }
});
