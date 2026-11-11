/* A passagem dos pets vivos para a ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA4; a IA-4 e "Migram por evento", decisoes
   do Matheus de 2026-11-10): o pet v21 que abre no jogo (o save, um pet guardado, um arquivo importado) ganha o evento "mi" no registro,
   uma vez, e o mundo dele passa a ter a agua. O que estava na agua (a racao, a bola, o pet) vai para a terra mais perto. Os ovos novos ja
   nascem na ilha com agua (a v22). O pet de teste (v16), o pet morto e o que ja passou ficam como estao. */
import type { Motor } from "../motor/index.ts";

/** passa o pet para a ilha com agua, se ele pode; devolve se passou (quem chama grava o save) */
export function passarParaIlhaComAgua(m: Motor): boolean {
  if (!m.podeMudarIlha) return false;
  m.mudarIlha();
  return true;
}
