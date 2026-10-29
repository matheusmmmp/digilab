/* A arena em tempo real (docs/TAREFA_V2_UP_ARENA.md): simulacao sem DOM, atras da chave ARENA_TEMPO_REAL na tela. */
export * from "./constantes.ts";
export * from "./tipos.ts";
export * from "./dados.ts";
export * from "./rng.ts";
export { CENAS, IDS_CENA, iniciarCena, type DefCena } from "./cenas.ts";
export { aplicarEntrada, ativo, criarLuta, outro, passo, statsDoMembro, trocar, vivos } from "./sim.ts";
export * from "./medicao.ts";
export * from "./rival.ts";
export * from "./pet.ts";
