/* O endereco do servidor_web no build (VITE_DIGILAB_API). Vazio: a conta e a luta ranqueada ficam desligadas, e o jogo e o de sempre.
   Os enderecos dos Termos e da Privacidade (VITE_DIGILAB_TERMOS, VITE_DIGILAB_PRIVACIDADE) sao das paginas publicas da CN6: sem eles, a
   tela mostra os nomes sem o link. */
const ler = (nome: "VITE_DIGILAB_API" | "VITE_DIGILAB_TERMOS" | "VITE_DIGILAB_PRIVACIDADE"): string => {
  try { return String(import.meta.env?.[nome] ?? "").trim(); } catch { return ""; }
};
export const apiDoBuild = (): string => ler("VITE_DIGILAB_API");
export const enderecoDosTermos = (): string => ler("VITE_DIGILAB_TERMOS");
export const enderecoDaPrivacidade = (): string => ler("VITE_DIGILAB_PRIVACIDADE");
