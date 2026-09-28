/* O motor roda sem DOM (lib ES2023, sem "dom"): so o console.warn do replay e declarado aqui. Qualquer uso de
   window, document, localStorage ou fetch no motor falha na checagem de tipos. */
declare const console: { warn(...dados: unknown[]): void };
