/* A chave do protótipo do gosto visual (docs/futuro/gosto_visual_pet.md, seção 14): LIGADA por padrão desde 2026-11-11 (decisão do
   Matheus, D-GV-PADRAO-1: "Quero que a opção da TV esteja padrão no jogo"). `?gosto_visual=0` desliga só naquela aba (os testes e o e2e
   que precisam da ilha de antes); `?gosto_visual=1` continua aceito. Ligada ou não, a captura da tela só começa com o clique do dono, o
   quadro é descartado, e nada entra no motor, no log ou no save. */
export const GOSTO_VISUAL_LIGADO = true;

export const gostoVisualLigado = (busca: string = typeof location !== "undefined" ? location.search : ""): boolean => {
  const valor = new URLSearchParams(busca).get("gosto_visual");
  if (valor === "0") return false;
  if (valor === "1") return true;
  return GOSTO_VISUAL_LIGADO;
};
