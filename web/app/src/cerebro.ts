/* O cerebro primario do pet (docs/TAREFA_V3_CEREBRO_PRIMARIO.md; pedido do Matheus de 2026-11-04): o DigiBrain modular por padrao, com o
   cerebro A (os lobos, a linha de base) selecionavel em Ajustes > Laboratorio. Duas coisas:
     - a escolha dos ovos novos: uma preferencia de tela (CHAVE-cerebro, fora do save), lida quando o ovo nasce e gravada no registro dele
       (o evento "cb" logo depois das chaves do produto). O pet nunca le a preferencia de novo: o que vale e o registro;
     - a troca do pet ativo: um "cb" no registro dele, na hora. Um pet v15 passa a v17 antes (Motor.promoverV17: o mesmo registro, a
       mesma vida). Os pets v13 e v14 nao trocam (a luta e a bola deles sao outras). */
import { useEffect, useState } from "react";
import { VERSAO_V15, ehCerebroTrocavel, type Motor } from "../motor/index.ts";

export type Cerebro = "modular" | "a";
/** a chave da preferencia: a CHAVE do save (save.ts) com "-cerebro" (literal aqui para o save.ts poder importar daqui; um teste confere) */
export const CHAVE_CEREBRO = "digilab-web-v21-sprites-cerebro";
export const CEREBRO_PADRAO: Cerebro = "modular";
export const NOME_CEREBRO: Record<Cerebro, string> = { modular: "DigiBrain modular", a: "cérebro A" };

const ouvintes = new Set<() => void>();
/** hook: a tela redesenha quando a escolha dos ovos novos muda */
export function useCerebroDosOvos(): Cerebro {
  const [, t] = useState(0);
  useEffect(() => { const f = () => t(x => x + 1); ouvintes.add(f); return () => { ouvintes.delete(f); }; }, []);
  return cerebroDosOvos();
}
/** o cerebro com que os ovos novos nascem: o modular, se o jogador nao escolheu o A */
export function cerebroDosOvos(): Cerebro {
  try { return localStorage.getItem(CHAVE_CEREBRO) === "a" ? "a" : CEREBRO_PADRAO; } catch { return CEREBRO_PADRAO; }
}
export function escolherCerebroDosOvos(c: Cerebro): void {
  try { localStorage.setItem(CHAVE_CEREBRO, c); } catch { /* preferencia de tela: sem armazenamento, so nao lembra */ }
  for (const o of ouvintes) o();
}
/** grava no ovo novo (v17, logo depois das chaves do produto) o cerebro dos ovos novos. Os pets de outras versoes passam sem mudar */
export function nascerComCerebro(m: Motor): Motor {
  if (ehCerebroTrocavel(m.versao)) m.trocarCerebro(cerebroDosOvos());
  return m;
}
/** o pet troca de cerebro? v17 sim; v15 sim, passando a v17; as outras nao */
export const podeTrocarCerebro = (m: Motor): boolean => ehCerebroTrocavel(m.versao) || m.versao === VERSAO_V15;
