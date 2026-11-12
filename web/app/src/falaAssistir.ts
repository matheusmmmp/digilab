/* A fala do assistir (docs/futuro/fala_do_assistir.md; FA-2 a FA-7 DECIDIDAS pelo Matheus em 2026-11-12, pela recomendacao). Enquanto o pet
   olha a TV, ele as vezes diz uma frase curta sobre o que viu, pelo que o cerebro dele calculou: o `dec-v4` (Motor.conceitosAssistir) da a
   intencao do assistir (gostei, susto, chato, o_que_e), e uma frase de TEMPLATE por conceito a poe em palavras (FA-7: sem LLM, ate a DC5c
   aprovar uma voz). So APRESENTACAO:
     - le o pet (motor), nunca escreve nele; o texto nunca volta ao pet;
     - a linha vai para o log de apresentacao da fala (localStorage <CHAVE>.fala.jsonl, o mesmo da fala livre; FA-6), com o conceito, o valor,
       a confianca, o tick, a decisao e as versoes. O conceito se refaz do registro do pet pelo replay (test/fala_assistir.test.ts confere);
     - o limite da FA-5, em tempo real: um comentario a cada 5 min e um susto a cada 1 min (o susto fura o limite dos 5 min), so enquanto o pet
       olha (o `dec-v4` so tem o assistir quando o pet olhava a TV no intervalo que acabou). PROPOSTOS, SEM FONTE (ConfigFalaAssistir).
   A chave "Fala do assistir (teste)" fica DESLIGADA por padrao (preferencia de tela, fora do registro do pet). Desligada, nada daqui roda: nenhum
   decodificador, nenhuma linha no log, nenhum balao; o jogo e o de hoje. */
import { useEffect, useState } from "react";
import { CATALOGO_ASSISTIR, VERSAO_DECODIFICADOR_V4, type Motor, type NomeAssistir } from "../motor/index.ts";
import { CONFIG_FALA_ASSISTIR, type ConfigFalaAssistir } from "../motor/digibrain/constantes.ts";
import { LOG_FALA } from "./falaLivre.ts";
import { CHAVE } from "./save.ts";

const PREF = CHAVE + "-fala-assistir";
/** a versao da linha do log de apresentacao do assistir e a das frases de template (FA-7) */
export const VERSAO_LOG_ASSISTIR = 1;
export const VERSAO_TEMPLATE_ASSISTIR = "template-assistir-v1";

/** as frases de template (PROPOSTAS, SEM FONTE): uma por conceito, e a de duvida para a confianca abaixo do limiar (como na DC: "acho que") */
export const FRASES_ASSISTIR: Record<NomeAssistir, { certo: string; duvida: string }> = {
  gostei: { certo: "Gostei disso!", duvida: "Acho que gostei disso." },
  susto: { certo: "Ai! Que susto!", duvida: "Ai… acho que me assustei." },
  chato: { certo: "Que chato…", duvida: "Acho que isso tá ficando chato…" },
  o_que_e: { certo: "O que é isso?", duvida: "Acho que não sei o que é isso…" },
};

export interface RegistroAssistir {
  versao: number; situacao: "assistir"; t: number; k: number; olhava: number; conceito: NomeAssistir; valor: number; confianca: number;
  fala: string; versao_dec: string; versao_voz: string; modelo: "template"; semente: null;
}

/** a frase do conceito: a de duvida com a confianca abaixo do limiar */
export function fraseAssistir(conceito: NomeAssistir, confianca: number, cfg: ConfigFalaAssistir = CONFIG_FALA_ASSISTIR): string {
  const f = FRASES_ASSISTIR[conceito];
  if (f === undefined) throw new Error("conceito do assistir desconhecido: " + String(conceito));
  return confianca < cfg.limiar_confianca ? f.duvida : f.certo;
}

/** o limite da FA-5: `ultimoMs` e o ultimo comentario (qualquer um), `ultimoSustoMs` o ultimo susto (null: nenhum ainda) */
export function podeComentar(conceito: NomeAssistir, agoraMs: number, ultimoMs: number | null, ultimoSustoMs: number | null,
                             cfg: ConfigFalaAssistir = CONFIG_FALA_ASSISTIR): boolean {
  if (conceito === "susto") return ultimoSustoMs === null || agoraMs - ultimoSustoMs >= cfg.intervalo_susto_s * 1000;
  return ultimoMs === null || agoraMs - ultimoMs >= cfg.intervalo_comentario_s * 1000;
}

export const FA = {
  ligada: false,
  /** o ultimo comentario desta sessao da pagina (o balao o mostra so na decisao em que ele nasceu) */
  ultimo: null as RegistroAssistir | null,
  /** a ultima decisao ja lida (cada decisao e lida uma vez so) e o pet dela */
  ultK: -1, ultSemente: null as number | null,
  ultimoMs: null as number | null, ultimoSustoMs: null as number | null,
};
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
try { FA.ligada = localStorage.getItem(PREF) === "1"; } catch { /* sem armazenamento */ }

function anexar(reg: RegistroAssistir): void {
  try { localStorage.setItem(LOG_FALA, (localStorage.getItem(LOG_FALA) || "") + JSON.stringify(reg) + "\n"); } catch { /* sem armazenamento */ }
}
/** as linhas do assistir do log de apresentacao, conferidas (falha alto numa linha mal formada) */
export function lerLogAssistir(): RegistroAssistir[] {
  let txt = ""; try { txt = localStorage.getItem(LOG_FALA) || ""; } catch { return []; }
  return txt.split("\n").filter(Boolean).map(l => JSON.parse(l) as Record<string, unknown>).filter(r => r["situacao"] === "assistir").map((r, i) => {
    if (r["versao"] !== VERSAO_LOG_ASSISTIR || typeof r["fala"] !== "string" || !(CATALOGO_ASSISTIR as readonly unknown[]).includes(r["conceito"])
        || !Number.isInteger(r["k"]) || !Number.isInteger(r["t"])) throw new Error(`linha do assistir invalida no log de fala (${i + 1}a do assistir)`);
    return r as unknown as RegistroAssistir;
  });
}

/** a cada mudanca do pet: com a chave ligada, le a decisao nova do modular (uma vez) e, se o dec-v4 tem uma intencao do assistir e o limite
    deixa, grava a linha no log de apresentacao e devolve o comentario; senao null. `agoraMs`: o relogio real (Date.now) */
export function comentarioDoAssistir(m: Motor, agoraMs: number, cfg: ConfigFalaAssistir = CONFIG_FALA_ASSISTIR): RegistroAssistir | null {
  if (!FA.ligada) return null;
  const n = m.lab === null ? 0 : m.lab.motivos.length;
  if (FA.ultSemente !== m.semente) { FA.ultSemente = m.semente; FA.ultK = -1; FA.ultimo = null; }
  if (n === 0 || n - 1 === FA.ultK) return null;
  FA.ultK = n - 1;
  const d = m.conceitosAssistir();
  if (d === null || d.assistir === null || d.assistir.intencao === null) return null;
  const a = d.assistir, conceito = a.intencao!, c = a.conceitos.find(x => x.nome === conceito)!;
  if (!podeComentar(conceito, agoraMs, FA.ultimoMs, FA.ultimoSustoMs, cfg)) return null;
  const reg: RegistroAssistir = {
    versao: VERSAO_LOG_ASSISTIR, situacao: "assistir", t: m.e.tick, k: d.k, olhava: a.olhava, conceito, valor: c.valor, confianca: c.confianca,
    fala: fraseAssistir(conceito, c.confianca, cfg), versao_dec: VERSAO_DECODIFICADOR_V4, versao_voz: VERSAO_TEMPLATE_ASSISTIR, modelo: "template", semente: null,
  };
  FA.ultimoMs = agoraMs;
  if (conceito === "susto") FA.ultimoSustoMs = agoraMs;
  FA.ultimo = reg;
  anexar(reg);
  avisar();
  return reg;
}
/** o comentario a mostrar agora: so o da ultima decisao do pet de agora (depois dela, o balao volta ao de sempre) */
export function comentarioAtual(m: Motor): RegistroAssistir | null {
  const r = FA.ultimo, n = m.lab === null ? 0 : m.lab.motivos.length;
  return FA.ligada && r !== null && FA.ultSemente === m.semente && r.k === n - 1 ? r : null;
}
export function detalheAssistir(r: RegistroAssistir): string {
  return `fala do assistir (template, ${r.versao_dec}) · conceito: ${r.conceito.replace(/_/g, " ")} · confiança ${r.confianca < CONFIG_FALA_ASSISTIR.limiar_confianca ? "baixa" : "alta"}`;
}
export function escolherFalaAssistir(on: boolean): void {
  FA.ligada = on; try { localStorage.setItem(PREF, on ? "1" : "0"); } catch { /* preferencia de tela */ }
  if (!on) FA.ultimo = null;
  avisar();
}
export function useFalaAssistir(): typeof FA {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return FA;
}
