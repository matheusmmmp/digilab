/* A luta da POC no motor (docs/TAREFA_V3_LUTA_POC.md, LP1): a simulacao sem DOM, atras da chave LUTA_POC_LIGADA (desligada). Nada do
   jogo importa daqui ainda; o motor/index.ts nao reexporta esta pasta ate a LP2. */
export * from "./constantes.ts";
export * from "./tipos.ts";
export { dist, seno, PI, DOIS_PI } from "./aritmetica.ts";
export * from "./rng.ts";
export { CENAS, IDS_CENA, iniciarCena, type DefCena } from "./cenas.ts";
export { criarLuta, multAtr, passo, VENCE } from "./sim.ts";
export { FORMAS_ARENA, FORMAS_ARENA_POC, GOLPES_DA_POC } from "./formas.ts";
export * from "./luta.ts";
