/* Os instantes do jogo que tem som (SOM-UP, docs/TAREFA_V3_SOM_UP.md). Quem sabe do instante (a cena do pet, o treino, o nivel do Tamer,
   as medalhas, o painel, a luta) so emite; quem toca e a casca (src/somJogo.ts liga `ouvirSom` ao SOM). Assim os modulos de cena e de regra
   nao importam o audio, e o teste deles nao toca nem baixa nada. So apresentacao: nada daqui entra no motor, no log nem no save. */
import type { AlvoMusica, EventoSom, FonteMusica } from "./som.ts";

/** os efeitos do mapa de sons (Assets/sons/mapa.json, secao "efeitos"; o arquivo de cada um sai do Assets/gerar_sons_up.py) */
export const EFEITOS_SOM = [
  "ui_clique", "ui_abrir", "ui_fechar", "nivel", "medalha", "comer", "comer_fim",
  "treino_levantar_pedra", "treino_corrida", "treino_alvo", "treino_esquiva", "treino_meditar", "treino_resistencia",
  "luta_pronto", "luta_chefe", "luta_vitoria", "luta_derrota",
] as const;
export type EfeitoSom = (typeof EFEITOS_SOM)[number];

/** o que pode acontecer: um efeito, o golpe de uma forma (o mapa por Digimon) ou o pedido de musica de uma fonte */
export type InstanteSom =
  | { tipo: "efeito"; efeito: EfeitoSom }
  | { tipo: "golpe"; evento: EventoSom; sprite: string; habilidade: boolean }
  | { tipo: "musica"; fonte: FonteMusica; alvo: AlvoMusica | null };

const ouvintes = new Set<(i: InstanteSom) => void>();
const emitir = (i: InstanteSom): void => { for (const o of ouvintes) o(i); };
export function ouvirSom(o: (i: InstanteSom) => void): () => void { ouvintes.add(o); return () => { ouvintes.delete(o); }; }

/** o instante aconteceu: quem ouve toca (sem ouvinte, nada) */
export function emitirSom(e: EfeitoSom): void {
  if (!(EFEITOS_SOM as readonly string[]).includes(e)) throw new Error("efeito de som desconhecido: " + e);
  emitir({ tipo: "efeito", efeito: e });
}
/** o golpe, o acerto ou o fim de uma forma da luta (a chave de sprite do mapa de sons) */
export function emitirGolpe(evento: EventoSom, sprite: string, habilidade: boolean): void { emitir({ tipo: "golpe", evento, sprite, habilidade }); }
/** a fonte pede a musica (null: larga) */
export function emitirMusica(fonte: FonteMusica, alvo: AlvoMusica | null): void { emitir({ tipo: "musica", fonte, alvo }); }
