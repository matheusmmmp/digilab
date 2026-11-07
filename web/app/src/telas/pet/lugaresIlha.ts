/* Os lugares da ilha fora da cena 3D (docs/TAREFA_V3_LUGARES_3D.md, secoes 12 e 13): os nomes, o estado e o menu de cada um. Sem three e
   fora de ilha/ (test/ilha_fronteira.test.ts): o toque (ToqueLugar.tsx) e o contrato da cena (cenaEstado.ts) ficam no pacote principal, e
   a cena 3D chega por import dinamico. PROPOSTO, SEM FONTE. */
import type { Destino } from "../../rotas.ts";

/** os lugares (ilha/modelos.ts, LUGARES_MODELOS, tem um modelo para cada) */
export const NOMES_LUGARES = ["portao", "barraca", "cais"] as const;
export type NomeLugar = (typeof NOMES_LUGARES)[number];

/** o estado de cada lugar enquanto nao ha o nivel do Tamer (ilha/lugares.ts acende a mascara do aberto; ToqueLugar.tsx so abre o aberto) */
export const LUGAR_ABERTO: Record<NomeLugar, boolean> = { portao: true, barraca: true, cais: false };
/** o menu que cada lugar abre quando se toca nele (direcao B, "Lugares da ilha"): o portao de arena e o Lutar, a barraca do Tamer e o
    Diario; o cais ainda nao tem menu (o multiplayer e futuro) */
export const LUGAR_DESTINO: Record<NomeLugar, Destino | null> = { portao: "lutar", barraca: "diario", cais: null };
