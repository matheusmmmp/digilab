/* O pedido da semente da luta ranqueada (MMO4, docs/PLANO_V3_MMO.md secao 3; MMO-6): o que o jogo manda ao servidor antes da luta. O
   cliente se compromete com o registro do pet ate ali (o hash) antes de saber a semente; o servidor confere esse hash no envio
   (servidor_web/src/envio/conferir.ts). A luta ranqueada entra no registro exatamente na posicao `indice`, com a semente que o servidor
   devolveu (pontos.ts). Sem tela: a previa e o resultado na tela ficam para depois da prancha (secao 12 do plano MMO).

   O hash e o SHA-256 do JSON dos `indice` primeiros eventos do registro, como o jogo o grava (JSON.stringify do array; D-CONTA-83), em
   hexadecimal minusculo. Usa o crypto.subtle, que o navegador e o Node 24 tem. */
import type { EventoRegistro } from "../../motor/index.ts";

/** o corpo do POST /sementes */
export interface PedidoSemente { pet: { semente: number; versao: number }; indice: number; hash: string }

/** o SHA-256 do JSON dos `indice` primeiros eventos do registro */
export async function hashAte(log: readonly EventoRegistro[], indice: number): Promise<string> {
  if (!Number.isInteger(indice) || indice < 0 || indice > log.length) throw new Error(`indice fora do registro: ${indice} (o registro tem ${log.length})`);
  const bytes = new TextEncoder().encode(JSON.stringify(log.slice(0, indice)));
  const d = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  return Array.from(d, b => b.toString(16).padStart(2, "0")).join("");
}

/** o pedido para a proxima luta do pet: o indice e o fim do registro de agora */
export async function pedidoDaSemente(pet: { semente: number; versao: number; log: readonly EventoRegistro[] }): Promise<PedidoSemente> {
  return { pet: { semente: pet.semente, versao: pet.versao }, indice: pet.log.length, hash: await hashAte(pet.log, pet.log.length) };
}
