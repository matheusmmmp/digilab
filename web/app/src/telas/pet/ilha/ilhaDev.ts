/* A ilha de desenvolvimento (docs/TAREFA_V3_ILHA_AGUA.md, IA3): com ?ilha=agua no endereco, a vista desenha a ilha onde so a agua barra o
   pet (o layout `mvp_agua`), para ver o desenho antes de o motor ligar a agua (a IA4). So a vista troca: o motor continua no mundo de hoje,
   entao nesta previa o pet ainda anda em linha reta e passa por cima da agua. O jogador nao ve; fora do save, do registro e do replay. */
export const ILHA_DEV_AGUA = typeof location !== "undefined" && new URLSearchParams(location.search).get("ilha") === "agua";
