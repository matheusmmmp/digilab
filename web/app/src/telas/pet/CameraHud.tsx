/* O que a HUD mostra da camera solta (L1 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md), so a partir de 900 px:
   - o "seguir o pet": so o icone e a tecla F, em cima do minimapa, quando a camera esta solta e longe do pet (cameraLivre.ts, SEGUIR_DIST)
     ou o pet saiu da tela;
   - o aviso na borda: o pet fora da tela e chamando (os mesmos casos do cartao do chamado: um chamado aberto do In-Training ou o pet
     chamando voce), do lado em que ele esta; clicar volta a camera para ele, como o F.
   So vista: le o resumo da camera (useCameraLivre) e o motor por useJogo, nunca escreve no motor. */
import { ChevronDown, ChevronLeft, ChevronRight, ChevronUp, LocateFixed } from "lucide-react";
import type { Motor } from "../../../motor/index.ts";
import { chamadosVisiveis } from "../../hudPet.ts";
import { useJogo } from "../../jogo.ts";
import { seguirPet, useCameraLivre } from "./cameraLivre.ts";
import { Retrato } from "./TelaPet.tsx";

/** o pet chama: um chamado aberto do In-Training ou o pet chamando voce (TelaPet.tsx, Chamados) */
export const petChama = (m: Motor): boolean => chamadosVisiveis(m).length > 0 || m.acao === "chamar_atencao";

const SETA = { esquerda: ChevronLeft, direita: ChevronRight, cima: ChevronUp, baixo: ChevronDown } as const;
const ONDE = { esquerda: "a oeste da vista", direita: "a leste da vista", cima: "adiante", baixo: "atrás da câmera" } as const;

export function CameraHud() {
  const { motor: m, nascendo } = useJogo(), c = useCameraLivre();
  const chama = nascendo === 0 && !m.morte && petChama(m), S = SETA[c.lado], avisa = c.ativa && c.solta && c.petFora && chama;
  return (
    <>
      {/* a regiao viva fica sempre no DOM (a partir de 900 px), para o leitor de tela anunciar quando o pet chama fora da vista */}
      <span className="pet-camera-viva" role="status">{avisa ? `O pet está chamando, ${ONDE[c.lado]}. Aperte F para segui-lo.` : ""}</span>
      {c.ativa && c.solta && <>
      {c.longe && (
        <button type="button" className="hud-caixa pet-seguir" aria-label="Seguir o pet" aria-keyshortcuts="F" title="Seguir o pet (F)" onClick={() => seguirPet()}>
          <LocateFixed aria-hidden="true" /><kbd aria-hidden="true">F</kbd></button>
      )}
      {avisa && (
        <button type="button" className="hud-caixa pet-borda" data-lado={c.lado} aria-keyshortcuts="F"
          aria-label={`O pet está chamando, ${ONDE[c.lado]}. Seguir o pet`} onClick={() => seguirPet()}>
          <span className="pet-borda__exc" aria-hidden="true">!</span>
          <span className="pet-borda__retrato" aria-hidden="true"><Retrato m={m} ovo={false} /></span>
          <S className="pet-borda__seta" aria-hidden="true" /></button>
      )}
      </>}
    </>
  );
}
