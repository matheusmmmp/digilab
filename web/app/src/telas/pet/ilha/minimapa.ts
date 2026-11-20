/* O fundo do minimapa (L1 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md): a grade da ilha (grade.ts) vista de cima, uma celula
   por pixel, nas cores que a cena ja pinta: a primeira cor da grama de cada regiao, do caminho e da areia da paleta do estilo
   (PaletaTerreno, cena.ts) e a agua com a cor de base do shader dela (cena.ts, aguaMaterial: vec3(0.55, 0.88, 0.97)). O planalto e o
   morro ficam ESCURECE_NIVEL mais escuros por nivel, para ler o relevo. Nenhuma cor nova. Sem three e sem DOM: devolve os bytes RGBA, e
   a vista (vista.ts) faz o ImageData. Os numeros sao PROPOSTO, SEM FONTE. */
import type { PaletaTerreno } from "./cena.ts";
import type { Ilha } from "./grade.ts";

/** a agua do minimapa: a cor de base do shader da agua (cena.ts), em 0-255 */
export const AGUA_MAPA: readonly [number, number, number] = [Math.round(0.55 * 255), Math.round(0.88 * 255), Math.round(0.97 * 255)];
/** o quanto cada nivel acima do chao escurece (0,07 = 7 %) */
export const ESCURECE_NIVEL = 0.07;

const rgb = (h: number): [number, number, number] => [(h >> 16) & 255, (h >> 8) & 255, h & 255];

/** os bytes RGBA da ilha vista de cima: `ilha.larg` x `ilha.prof` pixels, a linha z de cima para baixo (o norte em cima) */
export function pixelsDoMapa(ilha: Ilha, paleta: PaletaTerreno): Uint8ClampedArray<ArrayBuffer> {
  const px = new Uint8ClampedArray(new ArrayBuffer(ilha.larg * ilha.prof * 4));
  ilha.celulas.forEach((c, i) => {
    let cor: readonly number[];
    if (c.tipo === "agua") cor = AGUA_MAPA;
    else if (c.tipo === "areia") cor = rgb(paleta.areia[0]);
    else if (c.tipo === "caminho") cor = rgb(paleta.caminho[0]);
    else {
      const g = paleta.grama[c.regiao];
      if (!g) throw new Error("minimapa: regiao sem cor de grama: " + c.regiao);
      cor = rgb(g[0]);
    }
    const f = 1 - ESCURECE_NIVEL * Math.max(0, c.nivel);
    px[i * 4] = cor[0] * f; px[i * 4 + 1] = cor[1] * f; px[i * 4 + 2] = cor[2] * f; px[i * 4 + 3] = 255;
  });
  return px;
}
