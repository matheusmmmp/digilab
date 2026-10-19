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
