/* Os textos e o selo do DigiBrain do A v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 4), usados pelo scan (ScanDigiBrain.tsx) e pela linha
   do agora (LinhaAgora.tsx). O painel de cartoes de antes (ConteudoDigiBrain) e o mapa de colunas (MapaPesos) sairam com o campo pequeno
   (D1c da UX_TELA_PET): o A v11 abre so no ScanDigiBrain. */
import type { AcaoPet, RegraLobos } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import { lutaSeguraTempo } from "../lutaPocTela.ts";
import { estadoSelo, type EstadoSelo } from "../seloDigiBrain.ts";
import { useTempo } from "../tempo.ts";

/** a regra do instinto que disparou, em texto do jogo */
export const REGRA_TXT: Record<RegraLobos, string> = {
  sono_exaustao: "Exausto", sono_continuar: "Ainda com sono", sono_noite: "De noite", pedido_necessidade: "Precisando de você",
  abandono: "Sem cuidado há muito tempo", fome_moderada: "Com fome", tempo_livre: "Tempo livre",
};
/** a acao como opcao (curta) */
export const ACAO_CURTA: Record<AcaoPet, string> = {
  ocioso: "à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar",
  ir_tv: "ir até a TV",
};

export const pct = (v: number, casas: number, sinal: boolean): string =>
  (sinal && v > 0 ? "+" : "") + (v * 100).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas }).replace("-", "−") + "%";

/** o selo (seloDigiBrain.ts): "replay" num replay, "ao vivo" so com o tempo do jogo andando, senao "pausado" */
export function useEstadoSelo(replay: boolean): EstadoSelo {
  const { motor: m, nascendo, erroSave } = useJogo(), { velocidade } = useTempo();
  return estadoSelo({ replay, velocidade, nascendo, erroSave: erroSave !== null, lutaSegura: lutaSeguraTempo(), morto: m.morte !== null });
}
