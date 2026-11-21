/* O endereco do servidor_web no build (VITE_DIGILAB_API). Vazio: a conta e a luta ranqueada ficam desligadas, e o jogo e o de sempre.
   Os enderecos dos Termos e da Privacidade (VITE_DIGILAB_TERMOS, VITE_DIGILAB_PRIVACIDADE) sao das paginas publicas da CN6: sem eles, a
   tela mostra os nomes sem o link. */
const ler = (nome: "VITE_DIGILAB_API" | "VITE_DIGILAB_TERMOS" | "VITE_DIGILAB_PRIVACIDADE" | "VITE_DIGILAB_NUVEM" | "VITE_DIGILAB_PROTECAO"): string => {
  try { return String(import.meta.env?.[nome] ?? "").trim(); } catch { return ""; }
};
export const apiDoBuild = (): string => ler("VITE_DIGILAB_API");
export const enderecoDosTermos = (): string => ler("VITE_DIGILAB_TERMOS");
export const enderecoDaPrivacidade = (): string => ler("VITE_DIGILAB_PRIVACIDADE");
/** a chave do save na nuvem (CN3): só com o servidor no build E VITE_DIGILAB_NUVEM=1. Desligada (o padrão), o save é o de sempre */
export const nuvemNoBuild = (): boolean => apiDoBuild() !== "" && ler("VITE_DIGILAB_NUVEM") === "1";
/** a chave da proteção (CN4): só com o servidor no build E VITE_DIGILAB_PROTECAO=1. Ligada, o atlas, os sons e os pacotes da evolução vêm
    por URL assinada (src/protecao/assets.ts) e a fala vai à API com o cookie (a cota por conta). Desligada (o padrão), tudo como antes */
export const protecaoNoBuild = (): boolean => apiDoBuild() !== "" && ler("VITE_DIGILAB_PROTECAO") === "1";
