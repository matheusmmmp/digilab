/* A ilha de desenvolvimento (docs/TAREFA_V3_ILHA_AGUA.md, IA3): com ?ilha=agua no endereco, a vista desenha a ilha onde so a agua barra o
   pet (o layout `mvp_agua`), para ver o desenho antes de o motor ligar a agua (a IA4). So a vista troca: o motor continua no mundo de hoje,
   entao nesta previa o pet ainda anda em linha reta e passa por cima da agua. O jogador nao ve; fora do save, do registro e do replay. */
export const ILHA_DEV_AGUA = typeof location !== "undefined" && new URLSearchParams(location.search).get("ilha") === "agua";
/** ?ilha=grande: a previa da ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG3; o layout `grande`, 128 x 60), antes de a IG4 por um
    pet nela. So a vista troca: o motor continua no mundo do pet, entao nesta previa o pet anda nas coordenadas do mundo dele (o canto
    noroeste da ilha grande) e passa por cima da agua e das arvores */
export const ILHA_DEV_GRANDE = typeof location !== "undefined" && new URLSearchParams(location.search).get("ilha") === "grande";
/** ?foco=x,z (em celulas), so com ?ilha=grande: a camera olha para esse ponto em vez de seguir o pet, para ver qualquer parte da ilha
    grande na previa (o pet da previa fica no canto noroeste). Fora da previa nao vale */
export const FOCO_DEV: readonly [number, number] | null = (() => {
  if (!ILHA_DEV_GRANDE) return null;
  const p = (new URLSearchParams(location.search).get("foco") ?? "").split(",").map(Number);
  return p.length === 2 && p.every(Number.isFinite) ? [p[0], p[1]] : null;
})();
