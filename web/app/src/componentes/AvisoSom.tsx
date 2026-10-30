/* Aviso visivel de som (pele hx, M5) que nao carregou (src/som.ts): aparece uma vez, o jogo segue sem aquele som. */
import "../estilo/menus_config.css";
import { useSom } from "../som.ts";

export function AvisoSom() {
  const { aviso } = useSom();
  if (!aviso) return null;
  return <div className="aviso mc-aviso" role="alert" data-testid="aviso-som">Som com problema: {aviso}</div>;
}
