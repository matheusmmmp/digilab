/* A passagem dos pets vivos para a ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA4; a IA-4 e "Migram por evento", decisoes
   do Matheus de 2026-11-10): o pet v21 que abre no jogo (o save, um pet guardado, um arquivo importado) ganha o evento "mi" no registro,
   uma vez, e o mundo dele passa a ter a agua. O que estava na agua (a racao, a bola, o pet) vai para a terra mais perto. Os ovos novos ja
   nascem na ilha com agua (a v22). O pet de teste (v16), o pet morto e o que ja passou ficam como estao. */
import type { Motor } from "../motor/index.ts";

/* Desde a IG4 (docs/TAREFA_V3_ILHA_AGUA.md, secao 12; 2026-11-11) o destino e a ilha grande (128 x 60): passam os pets v21 (os que
   nunca passaram para a agua e os que ja tinham passado) e os v22, com o lar de la virando o lar de ca e tudo deslocado junto (IG-7).
   Os ovos novos ja nascem nela (a v23). */
/** passa o pet para a ilha grande, se ele pode; devolve se passou (quem chama grava o save) */
export function passarParaIlhaComAgua(m: Motor): boolean {
  if (!m.podeMudarIlha) return false;
  m.mudarIlha();
  return true;
}
