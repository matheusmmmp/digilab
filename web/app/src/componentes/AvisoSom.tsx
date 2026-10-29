/* Aviso visivel de som que nao carregou (src/som.ts): aparece uma vez, o jogo segue sem aquele som. */
import { useSom } from "../som.ts";

export function AvisoSom() {
  const { aviso } = useSom();
  if (!aviso) return null;
  return <div className="aviso" role="alert" data-testid="aviso-som">Som com problema: {aviso}</div>;
}
