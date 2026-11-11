/* A ligação entre a ilha e o painel da TV (docs/PLANO_UX_GOSTO_VISUAL.md, a UX-GV-2 e a seção 6; a etapa 2 do código), fora dos componentes:
   - o toque na TV da ilha pede o painel (ToqueTv.tsx), e a tela Pet, que é dona dos painéis, atende (TelaPet.tsx);
   - a tela Pet diz quando o painel da TV está aberto, e a câmera da ilha vai ao cantinho (ilha/cantinhoTv.ts lê).
   Só existe com `?gosto_visual=1`. Sem DOM. Fora do motor, do log e do save. */
const ESTADO = { aberto: false };
let atender: (() => void) | null = null;

/** a tela Pet marca se o painel da TV está aberto */
export const marcarPainelTv = (aberto: boolean): void => { ESTADO.aberto = aberto; };
/** o painel da TV está aberto agora? (a câmera da ilha lê a cada quadro) */
export const painelTvAberto = (): boolean => ESTADO.aberto;

/** a tela Pet se inscreve para atender o pedido do toque na TV; devolve a função que desinscreve */
export function aoPedirPainelTv(f: () => void): () => void {
  atender = f;
  return () => { if (atender === f) atender = null; };
}
/** o toque na TV da ilha pede o painel; devolve se alguém atendeu (fora da tela Pet, ninguém) */
export function pedirPainelTv(): boolean {
  if (!atender) return false;
  atender();
  return true;
}
