/* Os atalhos diretos do lugar (L2 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md, "Sempre visivel x por gesto"): C abre Crescer, 1 a 4 trocam
   a aba de Crescer quando ele esta aberto, Esc sai (volta ao Pet). L e D sao da L3 e nao existem aqui. So fora de campo de texto, respeitando
   defaultPrevented e os modificadores (Ctrl, Alt, Meta), como as teclas da camera solta (cameraLivre.ts). Clicar ou Esc durante a viagem da camera pula
   para o fim (viagem.ts) e consome o Esc. So vista: nada disto entra no registro. */
import { pularViagem, viajando } from "./viagem.ts";

export interface AcoesLugar {
  /** as teclas valem agora (nenhuma tela cheia, boas-vindas, luta, aviso ou folha por cima) */
  ativo: () => boolean;
  /** Crescer esta aberto */
  emCrescer: () => boolean;
  abrirCrescer: () => void;
  /** troca a aba de Crescer pelo indice (0 a 3) */
  irAba: (i: number) => void;
  sair: () => void;
}

/** um campo de texto com o foco: as teclas ficam com ele */
export function emCampoDeTexto(alvo: EventTarget | null): boolean {
  return alvo instanceof Element && !!alvo.closest("input, textarea, select, [contenteditable=''], [contenteditable='true']");
}
/** ha um dialogo aberto que nao e o painel do lugar (a confirmacao do Forcar, uma folha de dentro de uma tela): ele cuida das proprias teclas */
const outroDialogo = (): boolean => !!document.querySelector("dialog[open]:not(.painel-tela--lugar)");

/** esconde os baloes que estao a vista (data-oculto no alvo, ate o ponteiro ou o foco sair); devolve se havia algum */
export function esconderBaloes(): boolean {
  let achou = false;
  for (const b of document.querySelectorAll<HTMLElement>(".dica-alvo > .balao")) {
    if (getComputedStyle(b).display === "none") continue;
    b.parentElement?.setAttribute("data-oculto", "1"); achou = true;
  }
  return achou;
}

/** a tecla (KeyboardEvent.code) e o que ela faz: "c", "1" a "4" ou "esc"; null se nao e atalho */
export function atalhoDaTecla(code: string): "c" | "esc" | "1" | "2" | "3" | "4" | null {
  switch (code) {
    case "KeyC": return "c";
    case "Escape": return "esc";
    case "Digit1": case "Numpad1": return "1";
    case "Digit2": case "Numpad2": return "2";
    case "Digit3": case "Numpad3": return "3";
    case "Digit4": case "Numpad4": return "4";
    default: return null;
  }
}

/** liga o teclado e o clique; devolve a funcao que desliga */
export function ligarAtalhosLugar(a: AcoesLugar): () => void {
  /* na captura, antes dos componentes: o Esc da viagem nao pode fechar o painel tambem */
  const baixo = (e: KeyboardEvent) => {
    /* o Esc da viagem so vale com o lugar ativo e sem outro dialogo por cima */
    if (e.code === "Escape" && !e.repeat && viajando() && a.ativo() && a.emCrescer() && !outroDialogo()) { pularViagem(); e.preventDefault(); e.stopPropagation(); return; }
    /* um balao visivel: o Esc fecha so ele */
    if (e.code === "Escape" && !outroDialogo() && esconderBaloes()) { e.preventDefault(); e.stopPropagation(); return; }
    if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || e.shiftKey || emCampoDeTexto(e.target)) return;
    const k = atalhoDaTecla(e.code);
    if (!k || !a.ativo() || outroDialogo()) return;
    if (k === "c") { if (!a.emCrescer()) { e.preventDefault(); a.abrirCrescer(); } return; }
    if (!a.emCrescer()) return;
    if (k === "esc") { e.preventDefault(); a.sair(); return; }
    e.preventDefault(); a.irAba(Number(k) - 1);
  };
  const clique = (e: Event) => { if (viajando() && a.emCrescer()) { pularViagem(); e.stopPropagation(); } };
  addEventListener("keydown", baixo, true);
  addEventListener("pointerdown", clique, true);
  return () => { removeEventListener("keydown", baixo, true); removeEventListener("pointerdown", clique, true); };
}
