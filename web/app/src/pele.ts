/* Pele dos menus (docs/TAREFA_V2_TEMA_MENUS.md §4): Militar (id xcom) ou Sci-fi (id vidro, o padrao, TM1;
   "Holografico" ate 2026-10-31), e desde a PE1 das peles de rua (docs/PLANO_UX_PELES_RUA.md, 2026-11-20) a Estencil (id estencil), ainda
   em previa: so os tokens, a forma inteira vem na PE2. Vale so nos menus
   e e sempre escura; o tema claro/escuro (tema.ts) segue no habitat. A escolha e uma preferencia de tela, numa chave propria (a chave
   do save nao muda; fora do registro e do replay); ?pele=xcom|vidro|estencil no endereco sobrepoe sem gravar (conferencia e capturas).
   data-pele fica sempre no <html>, para o CSS nao depender de ausencia de atributo. */
import { useEffect, useState } from "react";
import { CHAVE } from "./save.ts";

export type Pele = "xcom" | "vidro" | "estencil";
/** as peles, na ordem dos cartoes de Ajustes > Visual: o padrao primeiro */
export const PELES: readonly Pele[] = ["vidro", "xcom", "estencil"];
/** as peles ainda sem a forma inteira: o cartao delas leva a etiqueta "prévia" */
export const PELES_EM_PREVIA: readonly Pele[] = ["estencil"];
export const CHAVE_PELE = CHAVE + "-pele";
export const PELE_PADRAO: Pele = "vidro";
export const NOME_PELE: Record<Pele, string> = { xcom: "Militar", vidro: "Sci-fi", estencil: "Estêncil" };
const ehPele = (v: string | null): v is Pele => v !== null && (PELES as readonly string[]).includes(v);

let pele: Pele = PELE_PADRAO;
const ouvintes = new Set<() => void>();
const aplicar = (): void => { document.documentElement.dataset.pele = pele; };
export function iniciarPele(): void {
  const doEndereco = new URLSearchParams(location.search).get("pele");
  let salvo: string | null = null;
  try { salvo = localStorage.getItem(CHAVE_PELE); } catch { /* sem armazenamento: o padrao */ }
  pele = ehPele(doEndereco) ? doEndereco : ehPele(salvo) ? salvo : PELE_PADRAO;
  aplicar();
}
/** pele escolhida (Ajustes > Aparencia, T2) */
export function escolherPele(p: Pele): void {
  pele = p;
  try { localStorage.setItem(CHAVE_PELE, pele); } catch { /* preferencia de tela */ }
  aplicar();
  for (const o of ouvintes) o();
}
export function peleAtual(): Pele { return pele; }
export function usePele(): Pele {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return pele;
}
