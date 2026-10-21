/** o navegador desenha WebGL? Sem isso, as vistas 3D (a cena da tela Pet, o mapa da Exploracao) ficam com a reserva delas */
export function temWebGL(): boolean {
  try { const c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); } catch { return false; }
}
