/* Icone rapido sobre o pet depois de uma acao do dono (1,4 s); so apresentacao. Modulo sem DOM para o caminho
   compartilhado das acoes (src/acoes.ts) nao puxar o palco. */
let flash: { icone: string; ate: number } | null = null;
export function mostrarFlash(icone: string): void { flash = { icone, ate: performance.now() + 1400 }; }
/** o icone do flash se ainda vale, senao null */
export function flashAtual(): string | null { return flash && flash.ate > performance.now() ? flash.icone : null; }
