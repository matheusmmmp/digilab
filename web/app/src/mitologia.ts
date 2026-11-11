/* MITOLOGIA, E0 (docs/TAREFA_V3_MITOLOGIA.md): a chave `mitologia` (Ajustes; desligada por padrao) e o que o oraculo ja contou a cada pet.
   As lendas sao funcao pura do pet refeito do log (motor/lendas.ts); aqui so fica a preferencia de tela e o "ja ouvi", fora do save. */
import { useSyncExternalStore } from "react";
import { hybrisDe, type EventoLenda } from "../motor/index.ts";
import type { Motor } from "../motor/motor.ts";
import { CHAVE } from "./save.ts";

const CHAVE_MITOLOGIA = CHAVE + "-mitologia";
const CHAVE_OUVIDAS = CHAVE + "-mitologia-ouvidas";
const ouvintes = new Set<() => void>();
const avisar = () => { for (const o of ouvintes) o(); };
const assinar = (o: () => void) => { ouvintes.add(o); return () => { ouvintes.delete(o); }; };

/** padrao: desligada (o jogo de hoje); so "1" liga. Lida uma vez e guardada (a cena le a cada quadro) */
let ligada: boolean | null = null;
export function mitologiaLigada(): boolean {
  if (ligada === null) { try { ligada = localStorage.getItem(CHAVE_MITOLOGIA) === "1"; } catch { ligada = false; } }
  return ligada;
}
export function ligarMitologia(v: boolean): void {
  ligada = v;
  try { localStorage.setItem(CHAVE_MITOLOGIA, v ? "1" : "0"); } catch { /* preferencia de tela */ }
  avisar();
}
export function useMitologia(): boolean {
  return useSyncExternalStore(assinar, mitologiaLigada, () => false);
}

/* ---------- o que o oraculo ja contou: {semente do pet: quantas hybris ele ja ouviu}. Um pet sem entrada comeca do que ja tem (as lutas
   de antes de ligar a chave ficam caladas); o pedaco da lenda e o `parte` do evento, que so depende do log */
function lerOuvidas(): Record<string, number> {
  try {
    const t = localStorage.getItem(CHAVE_OUVIDAS);
    const o: unknown = t ? JSON.parse(t) : {};
    return o && typeof o === "object" && !Array.isArray(o) ? o as Record<string, number> : {};
  } catch { return {}; }
}
function gravarOuvidas(o: Record<string, number>): void {
  try { localStorage.setItem(CHAVE_OUVIDAS, JSON.stringify(o)); } catch { /* preferencia de tela */ }
}

/** a proxima hybris que o oraculo ainda nao contou a este pet (null: nenhuma) */
export function hybrisNaoOuvida(m: Motor): Extract<EventoLenda, { tipo: "hybris" }> | null {
  const h = hybrisDe(m.forcaLutas), o = lerOuvidas(), k = String(m.semente);
  if (!(k in o)) { o[k] = h.length; gravarOuvidas(o); return null; }
  const n = o[k];
  if (!Number.isInteger(n) || n < 0) throw new Error(`mitologia: contagem do oraculo invalida para o pet ${k}: ${n}`);
  return n < h.length ? h[n] : null;
}
export function ouvirHybris(m: Motor, e: Extract<EventoLenda, { tipo: "hybris" }>): void {
  const o = lerOuvidas(), k = String(m.semente);
  o[k] = Math.max(o[k] ?? 0, e.parte + 1);
  gravarOuvidas(o);
  avisar();
}
export function useOuvidas(): number {
  return useSyncExternalStore(assinar, () => Object.values(lerOuvidas()).reduce((t, n) => t + n, 0), () => 0);
}
