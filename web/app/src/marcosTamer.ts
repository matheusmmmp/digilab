/* Os marcos que o registro do Tamer cumpre sozinho (o nivel do Tamer, src/nivel.ts). Ficam aqui, sem nada que chegue ao React, porque o
   servidor (servidor_web, MMO4) le estes marcos do envio conferido para abrir o pedido da semente ranqueada; o nivel.ts os reexporta. */
import { MARCO_MEGA, type Tamer } from "./tamer.ts";

/** as medalhas dos marcos 5, 7 e 8 (a ultima e MEDALHAS_LIGA, a trava de hoje da Fronteira) */
export const MEDALHAS_MARCO = { primeira: 1, tres: 3, seis: 6 } as const;

/** os marcos que o registro do Tamer cumpre: as medalhas (5, 7, 8), o titulo da Liga (9) e o marco 10 gravado (MMO2; o pet que o fez pode
    ter saido) */
export function marcosDoTamer(t: Tamer): number[] {
  const out: number[] = [], n = t.medalhas.length;
  if (n >= MEDALHAS_MARCO.primeira) out.push(5);
  if (n >= MEDALHAS_MARCO.tres) out.push(7);
  if (n >= MEDALHAS_MARCO.seis) out.push(8);
  if (t.titulo) out.push(9);
  if (t.marco(MARCO_MEGA)) out.push(MARCO_MEGA);
  return out;
}
