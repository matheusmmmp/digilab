/* O que a cena 3D da tela Pet (cena3d.ts, carregada por import dinamico) conta ao resto da tela: se esta ligada, onde o pet esta na
   tela (em px de CSS, para o PalcoPet desenhar por cima a sujeira, o icone rapido e a marca de saude) e a medida M3. */
export const CENA: {
  modo3d: boolean;
  ret: { x: number; y: number; w: number; h: number } | null;
  medir: null | (() => Promise<Record<string, unknown>>);
} = { modo3d: false, ret: null, medir: null };
