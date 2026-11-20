/* Os instantes do jogo que tem som (SOM-UP, docs/TAREFA_V3_SOM_UP.md). Quem sabe do instante (a cena do pet, o treino, o nivel do Tamer,
   as medalhas, o painel, a luta) so emite; quem toca e a casca (src/somJogo.ts liga `ouvirSom` ao SOM). Assim os modulos de cena e de regra
   nao importam o audio, e o teste deles nao toca nem baixa nada. So apresentacao: nada daqui entra no motor, no log nem no save. */
import type { AlvoMusica, EventoSom, FonteMusica, TipoBipe } from "./som.ts";
import { HUMORES_VOZ, type HumorVoz } from "./somVoz.ts";

/** os efeitos do mapa de sons (Assets/sons/mapa.json, secao "efeitos"; o arquivo de cada um sai do Assets/gerar_sons_up.py) */
export const EFEITOS_SOM = [
  "ui_clique", "ui_abrir", "ui_fechar", "nivel", "medalha", "comer", "comer_fim",
  "treino_levantar_pedra", "treino_corrida", "treino_alvo", "treino_esquiva", "treino_meditar", "treino_resistencia",
  "luta_pronto", "luta_chefe", "luta_vitoria", "luta_derrota",
  /* HABITAT_REACOES, HR2: o som do gesto do dono no cuidado (o tom da voz muda no jogo, src/somVoz.ts) */
  "cuidado_toque", "cuidado_limpar", "cuidado_recusa", "fruta_boa", "fruta_podre", "chamado_atendido", "tratar", "nascer", "voz",
] as const;
export type EfeitoSom = (typeof EFEITOS_SOM)[number];

/** o que pode acontecer: um efeito, o golpe de uma forma (o mapa por Digimon) ou o pedido de musica de uma fonte */
export type InstanteSom =
  | { tipo: "efeito"; efeito: EfeitoSom }
  | { tipo: "golpe"; evento: EventoSom; sprite: string; habilidade: boolean }
  | { tipo: "musica"; fonte: FonteMusica; alvo: AlvoMusica | null }
  /* HR2 e HR3: a voz do pet (o tom sai da especie, do estagio e do humor, na casca) e o bipe do chamado */
  | { tipo: "voz"; humor: HumorVoz }
  | { tipo: "bipe"; bipe: TipoBipe };

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
/** o pet fala com este humor (a casca escolhe o tom e respeita a pausa entre duas falas) */
export function emitirVoz(humor: HumorVoz): void {
  if (!(HUMORES_VOZ as readonly string[]).includes(humor)) throw new Error("humor de voz desconhecido: " + humor);
  emitir({ tipo: "voz", humor });
}
/** o bipe do chamado do bebe (HR3) */
export function emitirBipe(bipe: TipoBipe): void { emitir({ tipo: "bipe", bipe }); }
/** a fonte pede a musica (null: larga) */
export function emitirMusica(fonte: FonteMusica, alvo: AlvoMusica | null): void { emitir({ tipo: "musica", fonte, alvo }); }
