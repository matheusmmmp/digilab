/* O sprite de reserva do WORLD-POC-01a (W-6): o pet sem o atlas do Digimon UP, que fica só local e não é versionado. Desenhado à mão,
   16 x 16, um caractere por pixel: "." é transparente, e as outras letras são as cores da paleta. A vista (etapa E3) o desenha com filtro
   nearest e escala inteira, como o atlas. */

export const PALETA_RESERVA: Readonly<Record<string, string>> = {
  k: "#1b1b2f",   // contorno
  l: "#f2a65a",   // corpo
  d: "#c8743a",   // sombra do corpo
  w: "#ffffff",   // brilho do olho
  b: "#3a2e5f",   // olho
  r: "#e2556a",   // bochecha
};

export const SPRITE_RESERVA: readonly string[] = [
  "................",
  ".....kkkkkk.....",
  "....kllllllk....",
  "...kllllllllk...",
  "..kllwbllwbllk..",
  "..kllbbllbbllk..",
  "..klrllllllrlk..",
  "..kllllkkllllk..",
  "..kdlllllllldk..",
  "...kdllllllldk..",
  "...kddllllddk...",
  "....kddddddk....",
  "....kdk..kdk....",
  "....kk....kk....",
  "................",
  "................",
];

/** confere o sprite: 16 linhas de 16 pixels, só com letras da paleta ou "." (falha alto) */
export function conferirSprite(linhas: readonly string[] = SPRITE_RESERVA, paleta: Readonly<Record<string, string>> = PALETA_RESERVA): void {
  if (linhas.length !== 16) throw new Error(`sprite com ${linhas.length} linhas`);
  for (const [i, l] of linhas.entries()) {
    if (l.length !== 16) throw new Error(`linha ${i} com ${l.length} pixels`);
    for (const c of l) if (c !== "." && !(c in paleta)) throw new Error(`cor desconhecida ${c} na linha ${i}`);
  }
}
