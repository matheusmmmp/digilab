/* Os textos curtos e o tipo do mapa dos pesos (Motor.digibrain().mapa), usados pelo desenho do scan (ScanDigiBrain.tsx). O mapa de colunas de
   antes saiu com o campo pequeno (D1c da UX_TELA_PET). */
import type { AcaoPet, ArestaMapa, MapaDecisao, RegraLobos } from "../../motor/index.ts";

export const TXT_ENTRADA: Record<string, string> = {
  vies: "viés", fome: "comida", higiene: "higiene", energia: "energia", humor: "humor", saude: "saúde", sujeira: "sujeira",
  dormindo: "dormindo", hora: "hora", ticks_sem_cuidado: "sem cuidado", tedio: "tédio", curiosidade: "curiosidade", solidao: "solidão",
  estresse: "estresse", dor: "dor", susto: "susto", vontade: "vontade", conforto: "conforto",
};
export const TXT_REGRA: Record<RegraLobos, string> = {
  sono_exaustao: "exausto", sono_continuar: "sono", sono_noite: "noite", pedido_necessidade: "precisando", abandono: "sem cuidado",
  fome_moderada: "fome", tempo_livre: "tempo livre",
};
export const TXT_ACAO: Record<AcaoPet, string> = {
  ocioso: "à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar",
};

export interface DadosMapa { receptores: readonly string[]; arestas: ArestaMapa[]; acesas: MapaDecisao | null }
