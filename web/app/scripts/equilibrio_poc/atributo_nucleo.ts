/* LUTA_POC, a investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 1.2): a classe do par pelo atributo, pelo triangulo de
   motor/arena/sim.ts (VENCE: o Vaccine vence o Virus, o Virus o Data, o Data o Vaccine; o Free e o None ficam fora).
   "+" = o lado x tem a vantagem; "-" = a desvantagem; "0" = nenhum dos dois. Usado pela leitura (N1) e pelas lutas fixas (N2). */
import { FORMAS_ARENA } from "../../motor/index.ts";
import { VENCE } from "../../motor/arena/index.ts";

export const atributoDe = (chave: string): string => { const f = FORMAS_ARENA[chave]; if (!f) throw new Error(`atributo: ${chave} fora da tabela`); return f.atributo; };
export function catAtr(x: string, y: string): "+" | "-" | "0" {
  const a = atributoDe(x), b = atributoDe(y);
  if (VENCE[a as keyof typeof VENCE] === b) return "+";
  if (VENCE[b as keyof typeof VENCE] === a) return "-";
  return "0";
}
