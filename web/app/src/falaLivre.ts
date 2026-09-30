/* Fala livre por LLM local (porte de web/modulos/fala_livre.js; docs/PLANO_VERSAO_FALA_LIVRE.md).
   So APRESENTACAO: le o pet (motor), nunca escreve nele. As falas e a conversa vao para o log de apresentacao
   (localStorage CHAVE + ".fala.jsonl"), nunca para o registro do pet. O que o jogador escreve nao ensina o pet.
   Mesmas chaves, mesmo formato de log e mesmas rotas do servidor que a versao do HTML.
   Pets v7 (voz propria, src/voz.ts): a fala espontanea vem dos gatilhos novos, entra no registro do pet pelo evento
   "fl" (abre a janela de fala, pode ser mentira) e o texto vem do servidor com voz: true ou, sem ele, do molde. A
   conversa manda a historia do pet. O registro de apresentacao ganha o campo `voz` (a verdade fica guardada ali). */
import { useEffect, useState } from "preact/hooks";
import { CMEN, FATORES_TXT, TICK_INICIAL, TPD, hashSemente, nomeForma, type FatoHistoria, type Janela, type Motor } from "../motor/index.ts";
import { FALA_LLM, ligarFalaLLM } from "./fala.ts";
import { jogoAtual, mudarMotor } from "./jogo.ts";
import { CHAVE } from "./save.ts";
import { TEXTO_GATILHO, assuntoDaFala, gatilhoDe, historiaDaConversa, internetLigada, podeFalar, revancheContra } from "./voz.ts";

const LOG = CHAVE + ".fala.jsonl", MODO = CHAVE + "-modo-fala";
const VERSAO_LOG = 1, MAX_TROCAS = 10, INTERVALO_ESPONTANEA_MS = 20000;
export type ModoFala = "template" | "moldura" | "livre";
export interface Verificacao { nao_suportadas?: number; manipulacao?: boolean; afirmacoes?: { trecho: string; sustentada: boolean | null }[]; erro?: string }
/** pets v7: o que so a apresentacao guarda sobre a fala espontanea (a mentira fica marcada, com a verdade) */
export interface VozRegistro {
  gatilho: string | null; fonte: "llm" | "molde"; chaves: string[]; invencoes: string[];
  janela: { inicio: number; falso: boolean; tema: string } | null; verdade: string | null;
}
export interface RegistroFala {
  versao: number; t: number; situacao: "espontanea" | "conversa"; fala_jogador: string | null; fala: string; fatos_citados: string[];
  fatos: unknown; estagio: string; modelo: string; versao_prompt: string; semente: number; latencia_s?: number; erro?: string; verificacao: Verificacao | null; voz?: VozRegistro;
}
export const FL = {
  modo: "template" as ModoFala, ultimo: null as RegistroFala | null, pendente: false, sessao: [] as [string, string][],
  ultMotivo: null as unknown, ultForma: null as string | null, ultLutas: 0, ultDesejo: "", tEspontanea: 0,
  status: null as { modelo: string } | null, statusErro: false, erro: null as string | null, fila: [] as [string, string | null, string | undefined][],
};
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
try { FL.modo = (localStorage.getItem(MODO) as ModoFala) || (FALA_LLM.on ? "moldura" : "template"); } catch { /* sem armazenamento */ }

/* ------------------------------------------------ log de apresentacao (separado do registro do pet) */
export function lerLog(): RegistroFala[] {
  let txt = ""; try { txt = localStorage.getItem(LOG) || ""; } catch { return []; }
  return txt.split("\n").filter(Boolean).map((l, i) => {
    const r = JSON.parse(l);
    if (r.versao !== VERSAO_LOG || typeof r.fala !== "string") throw new Error(`log de fala invalido (linha ${i + 1})`);
    return r as RegistroFala;
  });
}
function anexar(reg: RegistroFala): void {
  try { localStorage.setItem(LOG, (localStorage.getItem(LOG) || "") + JSON.stringify(reg) + "\n"); } catch { /* sem armazenamento */ }
}

/* ------------------------------------------------ fatos do pet (mesmo formato que digilab_fala_livre/fatos.py) */
const NOME_MEM: Record<string, string> = { demora: "Você me deixou esperando", bronca: "Broncas", elogio: "Elogios", carinho: "Carinho" };
const hhmm = (t: number): string => { const m = t % TPD; return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"); };
const diaDe = (t: number): number => Math.floor((t - TICK_INICIAL) / TPD) + 1;
const fatoresTxt = (f: string[]): string[] => f.map(x => (FATORES_TXT[x] && FATORES_TXT[x].marcador) || x.replace(/_/g, " ")).slice(0, 4);
export function estadoDoPet(m: Motor, gatilho?: string | null): Record<string, unknown> {
  const f = m.forma, e = m.e, est = f.est;
  const ident: Record<string, unknown> = { estagio: est, especie: f.esp };
  ident.forma = nomeForma(f).slice(0, 60);          /* o Digimon de agora, em todo estagio (o corpus da especie vem dele) */
  if (f.linha) ident.linha = f.linha;
  const estado: Record<string, unknown> = { fome: 1 - e.fome, higiene: e.higiene, energia: e.energia, humor: e.humor, saude: e.saude };
  const mem = m.pol.mem as unknown as { emocoes: { emocao?: string; nome: string }[]; curto: { cat: string; criada: number }[]; longo: { cat: string; criada: number }[] };
  if (m.versao >= 2 && mem.emocoes.length) estado.emocao = mem.emocoes[mem.emocoes.length - 1].emocao;
  estado.fadiga = Math.round(m.treino.fadiga); estado.sobrecarga = Math.round(m.treino.sobrecarga);
  if (e.sujeira > 0) estado.sujo = true;
  const s: Record<string, unknown> = { identidade: ident, estado };
  if (m.versao >= 2) {
    s.temperamento = Object.fromEntries((["curiosidade", "teimosia", "sensibilidade", "rancor"] as const).map(k => [k, m.temp[k]]));
    try {
      const c = m.carater();
      s.carater = Object.fromEntries(Object.entries(c as object).filter(([k]) => ["impetuoso", "paciente", "atento", "resistente"].includes(k))
        .map(([k, v]) => [k, Math.max(-1, Math.min(1, v as number))]));
    } catch { /* sem carater travado ainda */ }
    s.memorias = [...mem.curto.map(x => ["curto", x] as const), ...mem.longo.map(x => ["longo", x] as const)].slice(0, 8)
      .map(([esp, x]) => ({ espaco: esp, categoria: x.cat, evento: (NOME_MEM[x.cat] || x.cat).toLowerCase().slice(0, 80), ha_min: Math.max(0, m.e.tick - x.criada) }));
    const d = m.dz && m.dz.atual;
    if (d) s.desejo = { tipo: d.tipo, alvo: String(d.alvo).replace(/_/g, " ") };
    if (m.vinc) s.vinculo = Math.max(0, Math.min(1, m.vinc.valor));
  }
  s.motivos = m.motivos.slice(-3).reverse().map(x => ({
    acao: (x.recusa ? "recusei " + x.recusa.acaoDono : String(x.acao)).replace(/_/g, " ").slice(0, 80),
    fatores: fatoresTxt(x.exploracao ? [] : x.fatores), ...(x.tick != null ? { evento_ref: `dia ${diaDe(x.tick)} ${hhmm(x.tick)}` } : {}),
  }));
  if (gatilho) s.gatilho = gatilho.slice(0, 80);
  return s;
}

/* ------------------------------------------------ chamadas (so o servidor local; a pagina nao fala com a LLM) */
async function post(rota: string, corpo: unknown): Promise<Record<string, unknown>> {
  const r = await fetch(rota, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
  const d = await r.json(); if (!r.ok) throw new Error(d.erro || ("HTTP " + r.status)); return d;
}
/* uma chamada por vez (uma GPU): a conversa espera na fila; fala espontanea com chamada em curso e descartada */
async function falar(situacao: "espontanea" | "conversa", gatilho: string | null, falaJogador?: string): Promise<void> {
  if (FL.pendente) { if (situacao === "conversa") FL.fila.push([situacao, gatilho, falaJogador]); return; }
  FL.pendente = true; avisar();
  const motor = jogoAtual().motor;
  const semente = hashSemente("fala-livre", motor.semente, motor.log.length, FL.sessao.length) >>> 1;
  const t = motor.e.tick;
  try {
    const voz = motor.versao >= 7;
    const estado = estadoDoPet(motor, gatilho);
    if (voz) estado.historia = historiaDaConversa(motor, assuntosRecentes());
    const d = await post("/api/fala-livre", { estado, situacao, fala_jogador: falaJogador, historico: FL.sessao.slice(-MAX_TROCAS), semente,
      ...(voz ? { voz: true } : {}) });
    const reg: RegistroFala = {
      versao: VERSAO_LOG, t, situacao, fala_jogador: falaJogador || null, fala: d.fala as string, fatos_citados: d.fatos_citados as string[],
      fatos: d.fatos, estagio: d.estagio as string, modelo: d.modelo as string, versao_prompt: d.versao_prompt as string, semente,
      latencia_s: d.latencia_s as number | undefined, erro: d.erro as string | undefined, verificacao: null,
    };
    if (situacao === "conversa") FL.sessao.push([falaJogador!, reg.fala]);
    FL.ultimo = reg; avisar();
    if (voz) {                                     /* a voz ja volta verificada (autocorrecao no servidor) */
      reg.verificacao = (d.verificacao as Verificacao) ?? null;
      reg.voz = { gatilho: null, fonte: "llm", chaves: chavesDe(d.fatos), invencoes: (d.invencoes as string[]) ?? [], janela: null, verdade: null };
      anexar(reg); return;
    }
    /* a verificacao vem depois: a fala aparece na hora e o icone chega quando ela terminar */
    if (!reg.erro) post("/api/fala-livre/verificar", { fala: reg.fala, fatos_citados: reg.fatos_citados, fatos: reg.fatos, semente })
      .then(v => { reg.verificacao = v as Verificacao; anexar(reg); avisar(); })
      .catch((err: Error) => { reg.verificacao = { erro: String(err.message) }; anexar(reg); avisar(); });
    else anexar(reg);
  } catch (err) { FL.erro = err instanceof Error ? err.message : String(err); }
  finally {
    FL.pendente = false; avisar();
    const prox = FL.fila.shift();
    if (prox) falar(prox[0] as "conversa", prox[1], prox[2]);
  }
}

/* ------------------------------------------------ pets v7: fala espontanea da voz propria */
const chavesDe = (fatos: unknown): string[] =>
  (Array.isArray(fatos) ? fatos : []).filter((f: { chave?: string }) => typeof f.chave === "string").map((f: { chave: string }) => f.chave);
/** os assuntos das ultimas falas (o rodizio manda para o fim o que acabou de ser assunto) */
function assuntosRecentes(): string[][] {
  try { return lerLog().filter(r => r.voz).slice(-5).map(r => r.voz!.chaves); } catch { return []; }
}
function falaVoz(m: Motor, gatilho: string, foco: FatoHistoria | null = null): void {
  let j: Janela | null = null;
  mudarMotor(mm => { j = mm.falar(gatilho); });
  if (!j) return;
  const jan = j as Janela, as = assuntoDaFala(m, jan, assuntosRecentes(), foco), t = m.e.tick;
  const semente = hashSemente("voz", m.semente, m.log.length) >>> 1;
  const base: RegistroFala = {
    versao: VERSAO_LOG, t, situacao: "espontanea", fala_jogador: null, fala: as.molde, fatos_citados: [], fatos: as.historia,
    estagio: m.estagioAtual, modelo: "molde", versao_prompt: "molde", semente, verificacao: null,
    voz: { gatilho, fonte: "molde", chaves: as.chaves, invencoes: [], janela: { inicio: jan.inicio, falso: jan.falso, tema: String(jan.pedido) },
      verdade: as.verdade },
  };
  FL.ultimo = base; avisar();
  if (FL.modo !== "livre" || !FL.status || FL.pendente) { anexar(base); return; }
  FL.pendente = true; avisar();
  const estado: Record<string, unknown> = { ...estadoDoPet(m, TEXTO_GATILHO[gatilho] ?? gatilho), historia: as.historia };
  if (as.mentira) estado.mentira = as.mentira;
  post("/api/fala-livre", { estado, situacao: "espontanea", semente, voz: true, internet: internetLigada() && !as.mentira })
    .then(d => {
      const reg: RegistroFala = { ...base, fala: d.fala as string, fatos_citados: d.fatos_citados as string[], fatos: d.fatos,
        modelo: d.modelo as string, versao_prompt: d.versao_prompt as string, latencia_s: d.latencia_s as number | undefined,
        erro: d.erro as string | undefined, verificacao: (d.verificacao as Verificacao) ?? null,
        voz: { ...base.voz!, fonte: "llm", chaves: chavesDe(d.fatos), invencoes: (d.invencoes as string[]) ?? [] } };
      FL.ultimo = reg; anexar(reg);
    })
    .catch((err: Error) => { FL.erro = err.message; anexar(base); })
    .finally(() => { FL.pendente = false; avisar(); });
}
/** pets v7: o dono escolheu (Arena ou Campanha) o rival que venceu o pet e ainda nao foi vencido: ele fala antes da luta */
export function falaRevanche(m: Motor, rival: string): void {
  if (m.versao < 7 || !podeFalar(m)) return;
  const f = revancheContra(m, rival);
  if (f) falaVoz(m, "revanche", f);
}
/** a fala da voz ainda vale no balao (a janela de fala dura CMEN.janela minutos de jogo) */
export function falaVozRecente(m: Motor): RegistroFala | null {
  const u = FL.ultimo;
  return u && u.voz && u.situacao === "espontanea" && m.e.tick - u.t <= CMEN.janela ? u : null;
}

/** gatilho (a cada mudanca do pet): fala espontanea quando ele decide, recusa, evolui, luta ou tem vontade nova.
    Pets v7: os gatilhos da voz propria, em todos os modos (o texto so vem da LLM no modo livre).
    Devolve true quando o balao e da fala livre (a tela nao mostra o template). */
export function gatilhoFalaLivre(m: Motor): boolean {
  if (m.versao >= 7) {
    const g = gatilhoDe(m);
    if (g && podeFalar(m)) falaVoz(m, g);
    return !!falaVozRecente(m);
  }
  if (FL.modo !== "livre") return false;
  let g: string | null = null;
  if (m.motivo && m.motivo !== FL.ultMotivo) { FL.ultMotivo = m.motivo; g = m.motivo.recusa ? "recusei o que o dono pediu" : "acabei de decidir o que fazer"; }
  const forma = JSON.stringify(m.forma); if (FL.ultForma && forma !== FL.ultForma) g = "acabei de evoluir"; FL.ultForma = forma;
  const lutas = m.log.reduce((n, x) => n + (x[1] === "l" ? 1 : 0), 0); if (lutas > FL.ultLutas && FL.ultLutas) g = "acabei de lutar"; FL.ultLutas = lutas;
  const d = m.dz && m.dz.atual, dz = d ? d.tipo + ":" + d.alvo : ""; if (dz && dz !== FL.ultDesejo) g = g || "tive uma vontade nova"; FL.ultDesejo = dz;
  const agora = Date.now();
  if (g && agora - FL.tEspontanea >= INTERVALO_ESPONTANEA_MS) { FL.tEspontanea = agora; falar("espontanea", g); }
  return !!FL.ultimo;
}
export function iconeVerif(v: Verificacao | null, r?: RegistroFala): string {
  if (r?.voz) return r.voz.invencoes.length ? " ✎" : "";      /* voz: inventar pode; o lapis marca o que ele inventou */
  if (!v) return "";
  if (v.erro) return " ·?";
  return ((v.nao_suportadas ?? 0) > 0 || v.manipulacao) ? " ⚠" : "";
}
export function detalheFalaLivre(r: RegistroFala): string {
  const v = r.verificacao;
  if (r.voz) return `${r.voz.fonte === "llm" ? `voz própria (${r.modelo}${r.latencia_s ? ", " + r.latencia_s.toFixed(1) + " s" : ""})` : "voz própria (sem o modelo: o fato dito do jeito dele)"}`
    + (r.voz.gatilho ? ` · por quê: ${TEXTO_GATILHO[r.voz.gatilho] ?? r.voz.gatilho}` : "")
    + (r.voz.invencoes.length ? ` · inventou: ${r.voz.invencoes.map(x => `«${x}»`).join(" ")}` : "")
    + (r.erro ? ` · erro: ${r.erro}` : "");
  return `fala livre (${r.modelo}${r.latencia_s ? ", " + r.latencia_s.toFixed(1) + " s" : ""}) · fatos citados: ${r.fatos_citados.join(", ") || "nenhum"}`
    + (v && !v.erro ? ` · verificador: ${v.nao_suportadas} sem fato` + (v.afirmacoes || []).filter(a => !a.sustentada).map(a => ` «${a.trecho}»`).join("") : "")
    + (r.erro ? ` · erro: ${r.erro}` : "");
}
export function tituloFalaLivre(r: RegistroFala): string {
  const v = r.verificacao;
  if (r.voz) return r.voz.invencoes.length ? `ele inventou ${r.voz.invencoes.length} coisa(s) nesta fala` : "voz própria";
  return v && ((v.nao_suportadas ?? 0) > 0 || v.manipulacao) ? `verificador: ${v.nao_suportadas} afirmação(ões) sem fato${v.manipulacao ? ", possível manipulação" : ""}` : "fala livre";
}

export function escolherModo(modo: ModoFala): void {
  FL.modo = modo; try { localStorage.setItem(MODO, modo); } catch { /* preferencia de tela */ }
  ligarFalaLLM(modo === "moldura");
  avisar();
}
export function enviarConversa(txt: string): void { if (txt.trim() && FL.modo === "livre") falar("conversa", null, txt.trim()); }
export function conversaGravada(): RegistroFala[] {
  try { return lerLog().filter(r => r.situacao === "conversa").slice(-MAX_TROCAS); } catch { return []; }
}
/** carga: status do servidor e replay das falas do log (sem chamar a LLM) */
export function iniciarFalaLivre(): void {
  fetch("/api/fala-livre/status").then(r => r.json()).then(d => { FL.status = d; avisar(); }).catch(() => { FL.statusErro = true; avisar(); });
  try {
    const regs = lerLog(); FL.ultimo = regs[regs.length - 1] || null;
    FL.sessao = regs.filter(r => r.situacao === "conversa").slice(-MAX_TROCAS).map(r => [r.fala_jogador ?? "", r.fala]);
  } catch (e) { FL.erro = e instanceof Error ? e.message : String(e); }
  avisar();
}
export function useFalaLivre(): typeof FL {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return FL;
}
