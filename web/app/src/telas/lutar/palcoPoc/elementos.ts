/* O elemento de cada lutador na luta em tempo real (LUTA_EFEITOS, etapa E2; docs/TAREFA_V3_LUTA_EFEITOS.md, D-LE-1, ACEITA pelo Matheus em
   2026-11-06). So da vista: o motor da luta nao tem elemento, e nada aqui muda a luta, o log, o replay nem o ResultadoLutaTR. Puro (sem DOM).
   - O pet, os rivais adultos, os lideres da Liga e os rivais da Fronteira tem o sprite com a especie na frente (motor/nomes.ts, chaveSprite):
     o elemento sai da linhagem (brasa fogo, cirro gelo e vento, ferrugem raio e metal, limo agua e planta).
   - Os bots classicos e os NPCs da campanha nao tem linhagem: cada um ganha um elemento na tabela ELEMENTO_SEM_LINHAGEM.
   - Uma excecao por Digimon (a chave do sprite) passa por cima dos dois (ELEMENTO_EXCECAO; vazia nesta etapa).
   Sprite sem elemento falha alto.
   Portado do palcoTR/ (o palco 1D do combate por turnos) na LUTA_POC, LP4: ficaram so os geradores de pixel que o palco 2D usa
   (desenhoPoc.ts, visualPoc.ts); o que lia o estado da luta 1D saiu com ela. */
import type { Especie } from "../../../../motor/index.ts";
export type ElementoTR = Especie;

/** As cores de cada elemento (D-LE-1). PROPOSTO, SEM FONTE: ajustar nas capturas da E2.
    - nucleo, meio e borda: o projetil de dentro para fora; halo: a luz em volta (somada ao fundo); rastro: as particulas que ficam para tras.
    - forma: a silhueta do projetil (bola de fogo, lasca de gelo, faisca de raio, gota) */
export const ELEMENTO: Record<ElementoTR, { nome: string; forma: "bola" | "lasca" | "raio" | "gota"; nucleo: string; meio: string; borda: string; halo: string; rastro: readonly string[] }> = {
  brasa: { nome: "fogo", forma: "bola", nucleo: "#fff6c2", meio: "#ffb02e", borda: "#f0471f", halo: "#ff6a1f", rastro: ["#ffd23f", "#ff8a2b", "#e03a1e"] },
  cirro: { nome: "gelo e vento", forma: "lasca", nucleo: "#ffffff", meio: "#bfeaff", borda: "#5cc4f2", halo: "#8fdcff", rastro: ["#ffffff", "#bfeaff", "#7fd0f5"] },
  ferrugem: { nome: "raio e metal", forma: "raio", nucleo: "#fffbd6", meio: "#ffe14a", borda: "#f0a800", halo: "#ffd400", rastro: ["#ffe14a", "#c9d0d6", "#9aa3ad"] },
  limo: { nome: "agua e planta", forma: "gota", nucleo: "#e6fff6", meio: "#3fd6c0", borda: "#2f9e5a", halo: "#2fd0a8", rastro: ["#8ff0de", "#3fd6c0", "#58c24a"] },
};

/** Os lutadores sem linhagem (os bots classicos e os NPCs da campanha), pela chave do sprite. PROPOSTO, SEM FONTE: pelo golpe mais conhecido
    do Digimon no anime, quando ha um que caia num dos quatro; senao, pelo que mais combina com a cor do sprite. */
export const ELEMENTO_SEM_LINHAGEM: Readonly<Record<string, ElementoTR>> = {
  bot_aleatorio: "ferrugem",      /* Kuramon */
  bot_agressivo: "brasa",         /* Monochromon (Volcanic Strike) */
  bot_tartaruga: "ferrugem",      /* Golemon (pedra e metal) */
  bot_atirador: "ferrugem",       /* Tankmon (canhao) */
  bot_contragolpe: "brasa",       /* Leomon (Fist of the Beast King) */
  bot_adaptativo: "cirro",        /* Devimon (as asas, o vento) */
  bot_oraculo: "limo",            /* Jijimon */
  npc_tier1_brutamontes: "ferrugem",  /* Gazimon (Electric Stun Blast) */
  npc_tier2_sentinela: "brasa",       /* Tortomon */
  npc_tier2_carcereiro: "ferrugem",   /* Guardromon (metal) */
  npc_tier2_porteiro: "brasa",        /* Devidramon (Crimson Claw) */
  npc_tier3_soberano: "cirro",        /* Piedmon (as espadas no ar) */
  npc_v5_myotismon: "cirro",          /* Myotismon (os morcegos, o vento) */
  npc_v5_puppetmon: "limo",           /* Puppetmon (madeira, planta) */
  npc_v5_machinedramon: "ferrugem",   /* Machinedramon (metal) */
  npc_v6_youkomon: "brasa",           /* Youkomon (fogo de raposa) */
  npc_v6_marinbullmon: "limo",        /* MarinBullmon (mar) */
};

/** A excecao por Digimon (chave do sprite), por cima da linhagem e da tabela acima. Vazia nesta etapa: o Matheus pode pedir uma (o Patamon,
    por exemplo, nao e de gelo no anime). */
export const ELEMENTO_EXCECAO: Readonly<Record<string, ElementoTR>> = {};

const ESPECIES: readonly ElementoTR[] = ["brasa", "cirro", "ferrugem", "limo"];

/** o elemento do lutador pela chave do sprite; falha alto se nao houver */
export function elementoDoSprite(sprite: string): ElementoTR {
  const exc = ELEMENTO_EXCECAO[sprite]; if (exc) return exc;
  const esp = ESPECIES.find(e => sprite.startsWith(e + "_")); if (esp) return esp;
  const t = ELEMENTO_SEM_LINHAGEM[sprite]; if (t) return t;
  throw new Error(`sem elemento para o sprite ${sprite} (elementosTR.ts: ELEMENTO_SEM_LINHAGEM)`);
}
