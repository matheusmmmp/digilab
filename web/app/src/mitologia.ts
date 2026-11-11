/* MITOLOGIA (docs/TAREFA_V3_MITOLOGIA.md, E0, E1 e E2): a chave `mitologia` (Ajustes; desligada por padrao) e o que o oraculo ja contou a cada
   pet. As lendas sao funcao pura do pet refeito do log (motor/lendas.ts, motor/lendas_e1.ts); aqui so fica a preferencia de tela, o "ja ouvi"
   e o enigma decifrado, fora do save (o enigma nao e evento do log: e conversa com o oraculo, como o "ja ouvi"; D-E1-4). */
import { useSyncExternalStore } from "react";
import {
  ENIGMA, FALA_DIA_RARO, FALA_MONTANHA_FECHADA, FALA_PEDRA, FALA_PEGADAS, FALA_PIEDMON_DERROTA, FALA_VITORIA_SEM_QUEDA, falaDoOraculo, hybrisDe,
  montanhaDe, pedraAchadaDe, pegadasDe, tickDoDiaRaro, type EventoLenda,
} from "../motor/index.ts";
import type { Motor } from "../motor/motor.ts";
import { CHAVE } from "./save.ts";

const CHAVE_MITOLOGIA = CHAVE + "-mitologia";
const CHAVE_OUVIDAS = CHAVE + "-mitologia-ouvidas";
const ouvintes = new Set<() => void>();
let versao = 0;
const avisar = () => { versao++; for (const o of ouvintes) o(); };
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

/* ---------- o que o oraculo ja contou a cada pet (pela semente). Na E0 era so o numero de hybris ouvidas; na E1 vira o registro abaixo (o
   numero antigo vira `h`). Um pet sem entrada comeca com as hybris que ja tem como ouvidas (D-E0-5); os segredos da E1 e as falas do Piedmon
   (E2) ele conta uma vez */
export interface Ouvidas {
  h: number; pedra: boolean; pegadas: boolean; diaRaro: boolean; enigma: number | null;
  /** E2: a derrota para o Piedmon, a vitoria sem queda e a montanha (a lenda fechada) */
  piedmon: boolean; semQueda: boolean; montanha: boolean;
}
const NOVA = (h: number): Ouvidas => ({ h, pedra: false, pegadas: false, diaRaro: false, enigma: null, piedmon: false, semQueda: false, montanha: false });
function lerTudo(): Record<string, Ouvidas> {
  let o: unknown;
  try { const t = localStorage.getItem(CHAVE_OUVIDAS); o = t ? JSON.parse(t) : {}; } catch { return {}; }
  if (!o || typeof o !== "object" || Array.isArray(o)) return {};
  const out: Record<string, Ouvidas> = {};
  for (const [k, v] of Object.entries(o as Record<string, unknown>)) {
    if (typeof v === "number") out[k] = NOVA(v);
    else if (v && typeof v === "object") {
      const x = v as Partial<Ouvidas>;
      out[k] = { h: typeof x.h === "number" ? x.h : 0, pedra: x.pedra === true, pegadas: x.pegadas === true, diaRaro: x.diaRaro === true,
                 enigma: typeof x.enigma === "number" ? x.enigma : null, piedmon: x.piedmon === true, semQueda: x.semQueda === true,
                 montanha: x.montanha === true };
    }
  }
  return out;
}
function gravarTudo(o: Record<string, Ouvidas>): void {
  try { localStorage.setItem(CHAVE_OUVIDAS, JSON.stringify(o)); } catch { /* preferencia de tela */ }
}
/** as ouvidas do pet, criando a entrada se faltar (sem avisar: e chamada no efeito do balao) */
export function ouvidasDe(m: Motor): Ouvidas {
  const tudo = lerTudo(), k = String(m.semente);
  if (!tudo[k]) { tudo[k] = NOVA(hybrisDe(m.forcaLutas).length); gravarTudo(tudo); }
  const o = tudo[k];
  if (!Number.isInteger(o.h) || o.h < 0) throw new Error(`mitologia: contagem do oraculo invalida para o pet ${k}: ${o.h}`);
  return o;
}
function mudar(m: Motor, f: (o: Ouvidas) => void): void {
  const tudo = lerTudo(), k = String(m.semente);
  const o = tudo[k] ?? ouvidasDe(m);
  f(o);
  tudo[k] = o;
  gravarTudo(tudo);
  avisar();
}
export function useVersaoOuvidas(): number {
  return useSyncExternalStore(assinar, () => versao, () => 0);
}

/* ---------- a fila do oraculo: a proxima coisa que ele ainda nao contou a este pet */
export type FalaOraculo =
  | { tipo: "hybris"; texto: string; e: Extract<EventoLenda, { tipo: "hybris" }> }
  | { tipo: "pedra" | "pegadas" | "diaRaro" | "piedmon" | "semQueda" | "montanha"; texto: string };

export function proximaFala(m: Motor): FalaOraculo | null {
  const o = ouvidasDe(m), h = hybrisDe(m.forcaLutas);
  if (o.h < h.length) return { tipo: "hybris", texto: falaDoOraculo(h[o.h]), e: h[o.h] };
  const pedra = pedraAchadaDe(m);
  if (!o.pedra && pedra !== null && pedra <= m.e.tick) return { tipo: "pedra", texto: FALA_PEDRA };
  const pegadas = pegadasDe(m);
  if (!o.pegadas && pegadas !== null && pegadas <= m.e.tick) return { tipo: "pegadas", texto: FALA_PEGADAS };
  if (!o.diaRaro && m.e.tick >= tickDoDiaRaro()) return { tipo: "diaRaro", texto: FALA_DIA_RARO };
  /* E2: Piedmon e a montanha */
  const mt = montanhaDe(m);
  if (!o.montanha && mt.fechada !== null) return { tipo: "montanha", texto: FALA_MONTANHA_FECHADA };
  if (!o.semQueda && mt.semQueda !== null) return { tipo: "semQueda", texto: FALA_VITORIA_SEM_QUEDA };
  if (!o.piedmon && mt.derrota !== null) return { tipo: "piedmon", texto: FALA_PIEDMON_DERROTA };
  return null;
}
export function ouvir(m: Motor, f: FalaOraculo): void {
  mudar(m, o => {
    if (f.tipo === "hybris") o.h = Math.max(o.h, f.e.parte + 1);
    else o[f.tipo] = true;
  });
}

/* ---------- o enigma do Jijimon (7 toques no retrato do Codice): resolvido no tick do pet; o pessego fica um dia na ilha */
export function enigmaResolvidoEm(m: Motor): number | null {
  return lerTudo()[String(m.semente)]?.enigma ?? null;
}
/** responde o enigma: true se acertou (e grava o tick, uma vez so) */
export function responderEnigma(m: Motor, opcao: number): boolean {
  if (!Number.isInteger(opcao) || opcao < 0 || opcao >= ENIGMA.opcoes.length) throw new Error(`opcao do enigma invalida: ${opcao}`);
  if (opcao !== ENIGMA.certa) return false;
  mudar(m, o => { if (o.enigma === null) o.enigma = m.e.tick; });
  return true;
}
