/* A partir de 1100 px o app usa os layouts das pranchas *Desktop (DIRETRIZES_REPLICAR secao 6). Para o que o CSS nao
   resolve sozinho (quantos itens mostrar, qual componente usar), as telas perguntam por este gancho. */
import { useEffect, useState } from "react";

const CONSULTA = "(min-width: 1100px)";
export const ehDesktop = (): boolean => typeof matchMedia === "function" && matchMedia(CONSULTA).matches;
export function useDesktop(): boolean {
  const [d, setD] = useState(ehDesktop);
  useEffect(() => {
    if (typeof matchMedia !== "function") return;
    const mq = matchMedia(CONSULTA), mudou = () => setD(mq.matches);
    mq.addEventListener("change", mudou); mudou();
    return () => mq.removeEventListener("change", mudou);
  }, []);
  return d;
}

/* A partir de 900 px os destinos fora do Pet abrem num painel grande a direita do habitat (trilho de icones a esquerda); abaixo, num
   modal centralizado e a barra fica embaixo. */
const CONSULTA_LADO = "(min-width: 900px)";
export const ehPainelLado = (): boolean => typeof matchMedia === "function" && matchMedia(CONSULTA_LADO).matches;
export function usePainelLado(): boolean {
  const [d, setD] = useState(ehPainelLado);
  useEffect(() => {
    if (typeof matchMedia !== "function") return;
    const mq = matchMedia(CONSULTA_LADO), mudou = () => setD(mq.matches);
    mq.addEventListener("change", mudou); mudou();
    return () => mq.removeEventListener("change", mudou);
  }, []);
  return d;
}
