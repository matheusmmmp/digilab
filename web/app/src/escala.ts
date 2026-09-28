/* Escala do desktop (pedido do Matheus, 2026-09-28): as pranchas *Desktop tem 1280 px de largura; numa tela maior o app
   aumenta tudo (zoom no <html>) ate o layout caber nos mesmos 1280 px, no maximo 150% (1920 px de janela). Abaixo de
   1100 px (celular e barra lateral) fica em 100%. So apresentacao: nada do jogo muda. */
const LARGURA_PRANCHA = 1280, ZOOM_MAX = 1.5, DESDE = 1100;
let zoom = 1;

/** zoom atual do <html> (os canvas usam para desenhar nitidos: pixels do aparelho = CSS x zoom x devicePixelRatio) */
export const zoomAtual = (): number => zoom;

function aplicar(): void {
  const w = innerWidth;
  zoom = w >= DESDE ? Math.min(ZOOM_MAX, Math.max(1, w / LARGURA_PRANCHA)) : 1;
  zoom = Math.round(zoom * 100) / 100;
  document.documentElement.style.zoom = zoom === 1 ? "" : String(zoom);
  /* as telas do desktop medem a altura da janela (colunas ate o fundo): com zoom, 100dvh vale zoom x a janela */
  document.documentElement.style.setProperty("--zoom", String(zoom));
}
export function iniciarEscala(): void {
  aplicar();
  addEventListener("resize", aplicar);
}
