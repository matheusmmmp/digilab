/* A chave do save e o armazenamento, num modulo sem dependencias (MMO3): o src/tamer.ts le daqui, e o servidor (servidor_web/) importa o
   tamer.ts no Node sem puxar o React (o save.ts chega ao React pelo produto.ts e o cerebro.ts). O save.ts reexporta os dois. */
export const CHAVE = "digilab-web-v21-sprites";

/** o armazenamento que o save usa (localStorage no navegador; um Map nos testes) */
export interface Armazenamento { getItem(k: string): string | null; setItem(k: string, v: string): void }
