/* O estado da TV do protótipo P0 que a ilha 3D lê (o cantinho da TV, ilha/cantinhoTv.ts; docs/futuro/gosto_visual_pet.md, seção 14). O
   cartão do P0 (GostoVisual.tsx) escreve aqui quando a TV liga, desliga e a cada segundo sentido; a cena só lê. É um objeto solto na
   memória da aba: fora do motor, do log e do save do pet, e nada daqui é gravado (nem o vídeo: o elemento é o mesmo que a captura já usa
   para ler o quadro, e some quando ela para). Sem DOM em tempo de execução (o tipo do vídeo é só tipo), para o teste ler no node. */
import type { Reacao, Sentido } from "./gosto.ts";

/** o balão de cada reação (o mesmo no cartão e no cantinho da ilha) */
export const BALAO: Record<Reacao, string> = {
  adorando: "♥ adorando!", olhando: "olhando…", enjoou: "enjoei disso", nao_gosta: "não curti", curioso: "? o que é isso", distraido: "…",
};

export interface EstadoTv {
  /** a TV está ligada: a captura da tela ou a TV do jogo */
  ligada: boolean;
  /** de onde vem a imagem: a tela do dono ("tela") ou os programas sintéticos ("jogo"); null desligada */
  origem: "tela" | "jogo" | null;
  /** o programa da TV do jogo de agora (tvDoJogo.ts); null fora dela */
  programa: string | null;
  /** o último segundo sentido e a reação a ele; null antes do primeiro */
  sentido: Sentido | null;
  reacao: Reacao | null;
  /** o vídeo da captura (o mesmo elemento que captura.ts lê uma vez por segundo); null na TV do jogo ou desligada */
  video: HTMLVideoElement | null;
  /** sobe a cada mudança (a cena compara para saber se algo mudou) */
  versao: number;
}

export const TV: EstadoTv = { ligada: false, origem: null, programa: null, sentido: null, reacao: null, video: null, versao: 0 };

/** muda o estado da TV (só o cartão do P0 chama) */
export function publicarTv(m: Partial<Omit<EstadoTv, "versao">>): void {
  Object.assign(TV, m);
  TV.versao++;
}

/** desliga a TV: tudo volta ao estado de partida */
export function desligarTv(): void {
  publicarTv({ ligada: false, origem: null, programa: null, sentido: null, reacao: null, video: null });
}
