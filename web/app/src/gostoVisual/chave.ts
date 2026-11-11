/* A chave do protótipo P0 do gosto visual (docs/futuro/gosto_visual_pet.md, seção 14): DESLIGADA por padrão. `?gosto_visual=1` liga só
   naquela aba, como o `?luta_poc=1`. Desligada, o app não monta nada do protótipo e o jogo é o de hoje. */
export const GOSTO_VISUAL_LIGADO = false;

export const gostoVisualLigado = (busca: string = typeof location !== "undefined" ? location.search : ""): boolean =>
  GOSTO_VISUAL_LIGADO || new URLSearchParams(busca).get("gosto_visual") === "1";
