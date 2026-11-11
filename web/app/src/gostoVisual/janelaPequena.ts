/* A janela pequena do protótipo P0: a Document Picture-in-Picture API (Chrome e Edge 116 ou mais novos), uma janela flutuante que fica
   por cima das outras. Sem a API, falha alto: o erro diz qual navegador tem, e o pet segue no cartão da própria página. */

interface DocumentPiP { requestWindow(op?: { width?: number; height?: number }): Promise<Window>; window: Window | null }

/** a janela: 360 x 620 cabe o pet, o balão, o painel e os botões (os 340 x 460 de antes abriam com 404 de altura útil e cortavam os
    botões). O navegador pode abrir menor: os botões ficam presos no pé da janela. PROPOSTO, SEM FONTE */
export const LARGURA_JANELA = 360, ALTURA_JANELA = 620;

export const temJanelaPequena = (): boolean => typeof window !== "undefined" && "documentPictureInPicture" in window;

/** abre a janela flutuante (precisa vir de um clique) e copia para ela as folhas de estilo da página */
export async function abrirJanelaPequena(): Promise<Window> {
  if (!temJanelaPequena()) {
    throw new Error("este navegador não tem a janela flutuante (Document Picture-in-Picture). Ela existe no Chrome e no Edge 116 ou mais novos; aqui o pet assiste no cartão da página.");
  }
  const api = (window as unknown as { documentPictureInPicture: DocumentPiP }).documentPictureInPicture;
  const jan = await api.requestWindow({ width: LARGURA_JANELA, height: ALTURA_JANELA });
  for (const folha of Array.from(document.styleSheets)) {
    let regras: string | null = null;
    try { regras = Array.from(folha.cssRules).map(r => r.cssText).join("\n"); } catch { regras = null; /* folha de outra origem: vai pelo link */ }
    if (regras !== null) { const s = jan.document.createElement("style"); s.textContent = regras; jan.document.head.append(s); }
    else if (folha.href) { const l = jan.document.createElement("link"); l.rel = "stylesheet"; l.href = folha.href; jan.document.head.append(l); }
  }
  jan.document.documentElement.className = document.documentElement.className;
  jan.document.title = "O pet assistindo";
  return jan;
}
