/* A tela Pet no celular (docs/PROPOSTAS_V3_UX_TELA_PET.md, "Mobile mínimo", M1; prancha em docs/pranchas/ux-mobile/): só apresentação. Aqui moram
   o estado do leque (o que está aberto no momento: o leque do retrato ou o Mais) e o tempo do toque longo. O estado é de tela, em memória: fora do save,
   do log e do replay (como o `mais` de antes, que era um useState). Um leque por vez: abrir um fecha o outro. */
import { useSyncExternalStore } from "react";

/** quanto tempo o dedo fica sobre um botão até o nome dele aparecer (M1-9). PROPOSTO, SEM FONTE (M1-9, 2026-11-06): número de interface, não de jogo */
export const SEGURAR_MS = 500;

export type Leque = "paineis" | "mais";
let atual: Leque | null = null;
const ouvintes = new Set<() => void>();

export function mudarLeque(l: Leque | null): void {
  if (l === atual) return;
  atual = l;
  for (const o of ouvintes) o();
}
/** abre `l`, ou fecha se já é ele o aberto (o segundo toque no mesmo botão fecha) */
export const alternarLeque = (l: Leque): void => mudarLeque(atual === l ? null : l);
/** fecha só se o aberto for `l` (fechar o Mais não derruba o leque do retrato) */
export const fecharLeque = (l: Leque): void => { if (atual === l) mudarLeque(null); };
export const lerLeque = (): Leque | null => atual;
export function useLeque(): Leque | null {
  return useSyncExternalStore(o => { ouvintes.add(o); return () => { ouvintes.delete(o); }; }, lerLeque, () => null);
}

/** o toque longo que mostra o nome do botao (M1-9): arma so com o dedo (pointerType "touch"); com o mouse e a caneta o nome vem do hover e do foco. E
    so informativo: nao suprime nem adia a acao do botao em caso nenhum (o clique sai igual, de 0 ms ou de 2 s, por toque, mouse ou teclado) */
export class Segurador {
  segurando = false;
  private timer: ReturnType<typeof setTimeout> | undefined;
  private readonly mudou: (segurando: boolean) => void;
  constructor(mudou: (segurando: boolean) => void) { this.mudou = mudou; }
  baixo(tipo: string): void {
    this.parar();
    if (tipo !== "touch") return;
    this.timer = setTimeout(() => { this.timer = undefined; this.segurando = true; this.mudou(true); }, SEGURAR_MS);
  }
  parar(): void {
    clearTimeout(this.timer); this.timer = undefined;
    if (this.segurando) { this.segurando = false; this.mudou(false); }
  }
}
