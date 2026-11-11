/* A chave da luta da POC no app (docs/TAREFA_V3_LUTA_POC.md, LP2): LUTA_POC_LIGADA (motor/arena/constantes.ts) fica DESLIGADA ate a tela da
   LP3; ?luta_poc=1 liga so naquela aba, para conferir e para o e2e (como o ?arena_tr=1 do #446). Ligada: os ovos novos nascem v21, so a v21
   abre (LP-6: os pets v13 a v19 saem, com aviso, no descarte 7) e a escada de exemplo nao e semeada. Desligada: o jogo de hoje, byte a byte. */
import { LUTA_POC_LIGADA, VERSAO_PET, VERSOES_PET, VERSOES_PET_POC } from "../motor/index.ts";

export const lutaPocLigada = (): boolean =>
  LUTA_POC_LIGADA || (typeof location !== "undefined" && new URLSearchParams(location.search).get("luta_poc") === "1");
/** a versao dos ovos novos: a de hoje (VERSAO_PET; desde a LP5-5 da LUTA_POC, a v23, a v22 com a luta da rodada de equilibrio) */
export const versaoDoOvo = (): number => VERSAO_PET;
/** as versoes que abrem pelo arquivo (Importar) */
export const versoesQueAbrem = (): readonly number[] => lutaPocLigada() ? VERSOES_PET_POC : VERSOES_PET;
