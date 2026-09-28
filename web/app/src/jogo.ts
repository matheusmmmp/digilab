/* Estado da interface: UM motor, uma fonte. Nenhuma tela guarda copia do estado do pet (revisao da interface,
   item 1): as telas leem o motor pelo useJogo() e so mudam o motor por aqui, que avisa todo mundo e grava o
   save. No esqueleto (Etapa 3) nada muda o motor: o tempo e as acoes chegam com a tela Pet (Etapa 4). */
import { useEffect, useState } from "preact/hooks";
import type { Motor } from "../motor/index.ts";
import { gravarSave, lerSave, petExemplo, type Armazenamento } from "./save.ts";

export type Origem = "save" | "exemplo";
export interface Jogo {
  motor: Motor;
  origem: Origem;
  /** save que existe e nao abriu: o app mostra o erro e nao grava por cima */
  erroSave: { erro: string; bruto: string } | null;
  /** muda a cada alteracao do motor (as telas rederivam tudo dele) */
  revisao: number;
}

let jogo: Jogo | null = null;
const ouvintes = new Set<() => void>();
let armazenamento: Armazenamento | null = null;

export function iniciarJogo(armaz: Armazenamento): Jogo {
  armazenamento = armaz;
  const l = lerSave(armaz);
  if (l.tipo === "ok") jogo = { motor: l.motor, origem: "save", erroSave: null, revisao: 0 };
  else jogo = { motor: petExemplo(), origem: "exemplo", erroSave: l.tipo === "erro" ? { erro: l.erro, bruto: l.bruto } : null, revisao: 0 };
  return jogo;
}
export function jogoAtual(): Jogo {
  if (!jogo) throw new Error("jogo nao iniciado");
  return jogo;
}
/** a unica porta de mudanca: aplica no motor, grava (se o save abriu ou nao existia) e avisa as telas */
export function mudarMotor(f: (m: Motor) => void): void {
  const j = jogoAtual();
  f(j.motor);
  j.revisao++;
  if (!j.erroSave && armazenamento) gravarSave(armazenamento, j.motor);
  for (const o of ouvintes) o();
}
/** hook: a tela redesenha quando o motor muda */
export function useJogo(): Jogo {
  const [, setRev] = useState(0);
  useEffect(() => {
    const o = () => setRev(r => r + 1);
    ouvintes.add(o);
    return () => { ouvintes.delete(o); };
  }, []);
  return jogoAtual();
}
