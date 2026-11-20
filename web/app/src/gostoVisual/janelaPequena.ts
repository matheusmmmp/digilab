import { useSyncExternalStore } from "react";

/* A janela pequena do protótipo P0: a Document Picture-in-Picture API (Chrome e Edge 116 ou mais novos), uma janela flutuante que fica
   por cima das outras. Sem a API, falha alto: o erro diz qual navegador tem. Desde a etapa 3 do docs/PLANO_UX_GOSTO_VISUAL.md o miolo é
   a JanelaTv.tsx, na pele dos menus: a janela leva as classes e os atributos do <html> da página (a pele fica em `data-pele`). */

interface DocumentPiP { requestWindow(op?: { width?: number; height?: number }): Promise<Window>; window: Window | null }

/** a janela: 360 x 620 (a do P0). O navegador pode abrir menor: o palco do pet encolhe, e os botões ficam no pé, sem rolagem.
    PROPOSTO, SEM FONTE */
export const LARGURA_JANELA = 360, ALTURA_JANELA = 620;

export const temJanelaPequena = (): boolean => typeof window !== "undefined" && "documentPictureInPicture" in window;

/** abre a janela flutuante (precisa vir de um clique) e copia para ela as folhas de estilo da página */
export async function abrirJanelaPequena(): Promise<Window> {
  if (!temJanelaPequena()) {
    throw new Error("este navegador não tem a janela flutuante (Document Picture-in-Picture). Ela existe no Chrome e no Edge 116 ou mais novos; aqui o pet assiste no cantinho da ilha.");
  }
  const api = (window as unknown as { documentPictureInPicture: DocumentPiP }).documentPictureInPicture;
  const jan = await api.requestWindow({ width: LARGURA_JANELA, height: ALTURA_JANELA });
  for (const folha of Array.from(document.styleSheets)) {
    let regras: string | null = null;
    try { regras = Array.from(folha.cssRules).map(r => r.cssText).join("\n"); } catch { regras = null; /* folha de outra origem: vai pelo link */ }
    if (regras !== null) { const s = jan.document.createElement("style"); s.textContent = regras; jan.document.head.append(s); }
    else if (folha.href) { const l = jan.document.createElement("link"); l.rel = "stylesheet"; l.href = folha.href; jan.document.head.append(l); }
  }
  levarRaiz(document.documentElement, jan.document.documentElement);
  jan.document.title = "O pet assistindo TV";
  return jan;
}

/** leva para a raiz da janela a língua, as classes e os atributos `data-*` da raiz da página (a pele e o tema moram neles) */
export function levarRaiz(de: { lang: string; className: string; dataset: Record<string, string | undefined> },
  para: { lang: string; className: string; dataset: Record<string, string | undefined> }): void {
  para.lang = de.lang; para.className = de.className;
  for (const [k, v] of Object.entries(de.dataset)) if (v !== undefined) para.dataset[k] = v;
}

/* --- a janela da TV: uma só, fora dos componentes, porque o painel que a abre pode fechar e ela continua (UX-GV-1) --- */
let janelaDaTv: Window | null = null;
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const f of ouvintes) f(); };
export const janelaDaTvAtual = (): Window | null => janelaDaTv;
export function useJanelaDaTv(): Window | null {
  return useSyncExternalStore(f => { ouvintes.add(f); return () => { ouvintes.delete(f); }; }, janelaDaTvAtual, () => null);
}
/** abre a janela pequena da TV (precisa vir de um clique); fechar a janela pelo próprio "x" dela também a solta */
export async function abrirJanelaDaTv(): Promise<void> {
  if (janelaDaTv) return;
  const j = await abrirJanelaPequena();
  janelaDaTv = j;
  j.addEventListener("pagehide", () => { if (janelaDaTv === j) { janelaDaTv = null; avisar(); } });
  avisar();
}
export function fecharJanelaDaTv(): void {
  const j = janelaDaTv;
  janelaDaTv = null;
  j?.close();
  avisar();
}
