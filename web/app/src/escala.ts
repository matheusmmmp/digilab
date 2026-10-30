/* Escala do desktop. Ate a M1 do layout habitat o app dava zoom no <html> (de 1100 px a 1.5x) para as pranchas *Desktop de 1280 px
   caberem numa janela maior. Com o habitat em tela cheia (docs/TAREFA_V2_LAYOUT_HABITAT.md, M2) nao ha mais prancha de largura fixa:
   o habitat ocupa a janela inteira e o painel tem largura propria (min(.., vw)). O zoom saiu; o gancho fica, sempre 1, porque os
   canvas (palco do Pet, luta) multiplicam o backing store por ele. */
export const zoomAtual = (): number => 1;

export function iniciarEscala(): void {
  document.documentElement.style.zoom = "";
  document.documentElement.style.setProperty("--zoom", "1");
}
