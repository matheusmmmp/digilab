/* Icone rapido sobre o pet depois de uma acao do dono (1,4 s); so apresentacao. Modulo sem DOM para o caminho
   compartilhado das acoes (src/acoes.ts) nao puxar o palco. */
const FLASH_MS = 1400;
let flash: { icone: string; ate: number } | null = null;
export function mostrarFlash(icone: string): void { flash = { icone, ate: performance.now() + FLASH_MS }; }
/** o icone do flash se ainda vale, senao null */
export function flashAtual(): string | null { return flash && flash.ate > performance.now() ? flash.icone : null; }
/** quando o ultimo flash comecou (performance.now()), ou null se nao houve: a reacao do dono no corpo do pet (cenaAcao.ts, escolherComer) */
export function flashDesde(): number | null { return flash ? flash.ate - FLASH_MS : null; }
