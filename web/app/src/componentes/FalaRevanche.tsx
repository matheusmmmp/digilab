/* A fala da revanche (pets v7, src/voz.ts) nas telas de luta: o pet fala diante do rival que o venceu, antes do Lutar ou
   Desafiar. A janela de fala (Acreditar, Petisco, É mentira) fica na tela do Pet, como as outras falas espontaneas. */
import { nomeForma } from "../../motor/index.ts";
import { falaVozRecente, iconeVerif, useFalaLivre } from "../falaLivre.ts";
import { useJogo } from "../jogo.ts";

export function FalaRevanche() {
  const { motor: m } = useJogo();
  useFalaLivre();
  const f = falaVozRecente(m);
  if (!f || f.voz?.gatilho !== "revanche") return null;
  return (
    <p className="dl-card fala-revanche" aria-live="polite">
      <b>{nomeForma(m.forma)}:</b> ✧ {f.fala}{iconeVerif(f.verificacao, f)}
      <span className="dl-apoio"> (julgue na tela do Pet)</span>
    </p>
  );
}
