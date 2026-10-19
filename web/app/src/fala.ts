/* Fala do pet na tela (so exibicao; espelho do HTML). O texto vem das tabelas de expressao do motor; a fala por
   LLM (moldura, servidor local /api/fala) so troca o TEXTO do adolescente e do adulto e e validada no servidor
   contra o motivo. Nada disso entra no registro nem nas decisoes. Sem servidor: so template. */
import { useEffect, useState } from "react";
import { NOME_ESTAGIO_FALA, expressar, type Estagio, type Motivo, type MotivoVida, type Motor } from "../motor/index.ts";
import { CHAVE } from "./save.ts";

export const CHAVE_FALA_LLM = CHAVE + "-fala-llm";
export interface RespostaFala { texto: string | null; fonte: string; detalhe?: string }
export const FALA_LLM = {
  on: false, ativo: false, provedor: null as string | null, modelo: null as string | null, semCusto: false, motivo: "",
  gasto: null as { gasto_usd: number; limite_usd: number } | null, cache: new Map<string, RespostaFala>(), pendentes: new Set<string>(),
};
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
try { FALA_LLM.on = localStorage.getItem(CHAVE_FALA_LLM) === "1"; } catch { /* sem armazenamento: desligada */ }

export async function verificarLLM(): Promise<void> {
  try {
    const r = await fetch("/api/fala/status", { cache: "no-store" }); if (!r.ok) throw new Error(String(r.status));
    const d = await r.json();
    FALA_LLM.ativo = !!d.ativo; FALA_LLM.provedor = d.provedor; FALA_LLM.modelo = d.modelo;
    FALA_LLM.semCusto = !!d.sem_custo; FALA_LLM.motivo = d.motivo || ""; FALA_LLM.gasto = d.gasto;
  } catch {
    FALA_LLM.ativo = false; FALA_LLM.motivo = "servidor sem a rota de fala (rode python servidor/servidor_local.py)";
  }
  avisar();
}
/** o Ollama pode ser ligado com a pagina aberta: reconsulta enquanto estiver indisponivel */
export function iniciarFalaLLM(): () => void {
  verificarLLM();
  const t = setInterval(() => { if (!FALA_LLM.ativo) verificarLLM(); }, 15000);
  return () => clearInterval(t);
}
export function ligarFalaLLM(on: boolean): void {
  FALA_LLM.on = on;
  try { localStorage.setItem(CHAVE_FALA_LLM, on ? "1" : "0"); } catch { /* preferencia de tela */ }
  avisar();
}
export function useFalaLLM(): typeof FALA_LLM {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return FALA_LLM;
}
/** faixa de status da fala (guia 10: indisponivel = faixa discreta, sem erro assustador) */
export function rotuloLLM(): { texto: string; titulo: string; estado: "off" | "ok" | "pronto" } {
  const g = FALA_LLM.gasto, dec = (v: number) => v.toFixed(2).replace(".", ",");
  const texto = !FALA_LLM.ativo ? "falando por frases prontas"
    : !FALA_LLM.on ? (FALA_LLM.semCusto ? "modelo local pronto · desligado" : "modelo pronto · desligado")
    : FALA_LLM.semCusto ? "modelo local · sem custo"
    : `Claude · US$ ${g ? dec(g.gasto_usd) : "?"} de US$ ${g ? dec(g.limite_usd) : "?"}`;
  const titulo = !FALA_LLM.ativo ? (FALA_LLM.motivo || "rode python servidor/servidor_local.py") : `${FALA_LLM.provedor || ""} ${FALA_LLM.modelo || ""}`.trim();
  return { texto, titulo, estado: !FALA_LLM.ativo ? "off" : FALA_LLM.on ? "ok" : "pronto" };
}

export function motivoParaApi(mot: Motivo, refs: number[]): Record<string, unknown> {
  return mot.origem === "vida"
    ? { origem: "vida", acao: mot.acao, fatores: mot.fatores, evento_ref: refs, intensidade: mot.intensidade, exploracao: mot.exploracao, tick: mot.tick }
    : { origem: "combate", acao: mot.acao, fatores: mot.fatores, evento_ref: mot.refs, exploracao: mot.exploracao, turno: mot.turno };
}
/** a resposta da LLM se ja chegou; senao pede (uma vez) e devolve null */
export function falaLLM(motApi: Record<string, unknown>, est: Estagio, humor: number | null): RespostaFala | null {
  if (!FALA_LLM.on || !FALA_LLM.ativo || !["adolescente", "adulto", "mega"].includes(est)) return null;
  const faixa = humor == null ? null : humor >= .66 ? 2 : humor >= .33 ? 1 : 0;
  const chave = JSON.stringify([motApi, est, faixa]);
  const pronta = FALA_LLM.cache.get(chave);
  if (pronta) return pronta;
  if (!FALA_LLM.pendentes.has(chave)) {
    FALA_LLM.pendentes.add(chave);
    fetch("/api/fala", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ motivo: motApi, estagio: est, humor }) })
      .then(r => r.ok ? r.json() : Promise.reject(new Error("HTTP " + r.status)))
      .then(d => { FALA_LLM.cache.set(chave, d); if (d.gasto) FALA_LLM.gasto = d.gasto; })
      .catch((err: Error) => { FALA_LLM.cache.set(chave, { texto: null, fonte: "template", detalhe: "servidor: " + err.message }); })
      .finally(() => { FALA_LLM.pendentes.delete(chave); avisar(); });
  }
  return null;
}

/** indice no registro da k-esima acao do dono (o motivo guarda ordinais; a fala cita o evento) */
export function idxDoOrdinal(m: Motor, k: number): number | null {
  let n = 0;
  for (let i = 0; i < m.log.length; i++) if (m.log[i][1] === "d" && ++n === k) return i;
  return null;
}
export const refsDoMotivo = (m: Motor, mot: MotivoVida): number[] => mot.refsOrd.map(k => idxDoOrdinal(m, k)).filter((x): x is number => x !== null);
/** texto do template; fala fria (sobrecarga no aviso ou forma sombria): so o tom muda, o conteudo e o mesmo */
export function falaDe(m: Motor, mot: MotivoVida): string {
  const est = m.estagioAtual, txt = expressar(mot, est, refsDoMotivo(m, mot));
  if (!(m.falaFria || m.sombria)) return txt;
  return est === "bebe" ? "(-_-)" : est === "adulto" || est === "mega" ? "Hm. " + txt : "... " + txt;
}
export function detalheMotivo(mot: Motivo, est: Estagio): string {
  const dec = (v: number) => v.toFixed(2).replace(".", ",");
  const fat = mot.exploracao ? "exploração" : (mot.fatores.join(", ") || "nenhum");
  const extra = mot.origem === "vida" && mot.recusa ? ` · você pediu ${mot.recusa.acaoDono}; chance de obedecer ${(mot.recusa.p * 100).toFixed(0)}%`
    : mot.origem === "vida" ? ` · o aprendido decidiu: ${mot.valorDecidiu ? "sim" : "não (instinto + acaso)"} · intensidade ${dec(mot.intensidade)}`
    : ` · regra ${typeof mot.regra === "number" ? "#" + (mot.regra + 1) : mot.regra}`;
  return `fatores: ${fat}${extra} · fala de ${NOME_ESTAGIO_FALA[est]}`;
}
