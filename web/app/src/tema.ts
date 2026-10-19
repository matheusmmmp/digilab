/* Tema da tela: o do sistema (prefers-color-scheme) ou escolhido pelo jogador (claro, escuro). A escolha e uma
   preferencia de tela, numa chave propria (a chave do save nao muda); ?tema=claro|escuro no endereco sobrepoe
   sem gravar (conferencia e screenshots). */
import { useEffect, useState } from "react";
import { CHAVE } from "./save.ts";

export type Tema = "sistema" | "claro" | "escuro";
export const CHAVE_TEMA = CHAVE + "-tema";
export const PROXIMO_TEMA: Record<Tema, Tema> = { sistema: "claro", claro: "escuro", escuro: "sistema" };
export const NOME_TEMA: Record<Tema, string> = { sistema: "Auto", claro: "Claro", escuro: "Escuro" };

let tema: Tema = "sistema";
const ouvintes = new Set<() => void>();
const aplicar = (): void => {
  if (tema === "sistema") delete document.documentElement.dataset.tema;
  else document.documentElement.dataset.tema = tema;
};
export function iniciarTema(): void {
  const doEndereco = new URLSearchParams(location.search).get("tema");
  let salvo: string | null = null;
  try { salvo = localStorage.getItem(CHAVE_TEMA); } catch { /* sem armazenamento: o do sistema */ }
  tema = doEndereco === "claro" || doEndereco === "escuro" ? doEndereco : salvo === "claro" || salvo === "escuro" ? salvo : "sistema";
  aplicar();
}
export function trocarTema(): void { escolherTema(PROXIMO_TEMA[tema]); }
/** tema escolhido (Configuracoes > Aparencia) */
export function escolherTema(t: Tema): void {
  tema = t;
  try { if (tema === "sistema") localStorage.removeItem(CHAVE_TEMA); else localStorage.setItem(CHAVE_TEMA, tema); } catch { /* preferencia de tela */ }
  aplicar();
  for (const o of ouvintes) o();
}
export function useTema(): Tema {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return tema;
}
