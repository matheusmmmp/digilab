/* O cliente do save na nuvem (CN3; docs/PLANO_V3_CONTA.md, seção 5; a prancha docs/pranchas/ux-conta-nuvem/, UX-NV-1 a 6 APROVADAS em
   2026-11-20). Sem React e sem DOM: a tela (src/nuvem/NuvemRaiz.tsx) lê o estado por `ouvirNuvem`/`revisaoNuvem` e chama as funções daqui;
   os testes ligam o `fetch` ao servidor de verdade, no processo (servidor_web/test/nuvem_e2e.test.ts).

   A CHAVE: sem `ligarNuvem` (a raiz só liga com VITE_DIGILAB_API e VITE_DIGILAB_NUVEM=1 no build), nada daqui roda, nada se grava, e o save
   de hoje sai byte a byte (test/nuvem_desligada.test.ts, contra o gabarito gravado antes da CN3).

   A FONTE do aparelho continua o armazenamento do navegador (5.1): este cliente lê dele o pacote (o save do pet do jogador e as outras
   chaves da CN0) e grava nele o que vem da nuvem; depois pede ao jogo para reler (`aoMudarLocal`). A posição que a nuvem confirmou fica na
   chave CHAVE_NUVEM, que é deste aparelho e não sobe.

   A TRAVA DO "SÓ VER" (UX-NV-5): com outro aparelho na vez, com a escolha da história pendente (UX-NV-4) e enquanto o jogo ainda pergunta à
   nuvem na abertura, o cliente pede `travar(true)` ao jogo: nenhuma ação entra no registro (src/jogo.ts). Offline, o jogo segue (5.1). */
import { CHAVE, type Armazenamento } from "../chave.ts";
import {
  CHAVES_NUVEM, CHAVE_ANTERIOR, PREFIXO_GOSTO_TV, PROTOCOLO_NUVEM, ehChaveNuvem, idDoSave, textoExtras, type Base, type DivergenciaVista,
  type EventoNuvem, type Pacote, type PedidoSync, type RespostaSync, type SaveNuvem, type VezVista,
} from "./protocolo.ts";

/** a posição confirmada pela nuvem, neste aparelho (fica no aparelho: não está em CHAVES_NUVEM) */
export const CHAVE_NUVEM = CHAVE + "-nuvem";
/** de quanto em quanto tempo o aparelho sincroniza (PROPOSTO, SEM FONTE): o envio dos eventos e o sinal da vez (a vez expira em 10 min) */
export const INTERVALO_SYNC_MS = 20_000;
/** a espera de cada chamada (PROPOSTA, SEM FONTE; a mesma da conta) */
export const ESPERA_NUVEM_MS = 15_000;

export interface AmbienteNuvem {
  /** o endereço do servidor, sem a barra do fim */
  api: string;
  buscar: (url: string, init?: RequestInit) => Promise<Response>;
  armaz: Armazenamento & { removeItem(k: string): void };
  /** as chaves do armazenamento (o gosto da TV é uma chave por pet) */
  chaves: () => string[];
  agora: () => number;
  /** o jogo relê o save e o Tamer do armazenamento (depois de gravar o que veio da nuvem) */
  aoMudarLocal: () => void;
  /** liga ou desliga a trava do "só ver" no jogo */
  travar: (sim: boolean) => void;
}

/** o que a tela mostra (a tela 5 da prancha, os estados) */
export type EstadoNuvem =
  | "conferindo"   // a abertura: o jogo ainda pergunta à nuvem (travado)
  | "sem_conta"    // a conta não está aberta neste aparelho: o "salvo" de hoje
  | "sessao"       // a sessão acabou: "Entre de novo"
  | "sem_pet"      // a conta não tem pet: "Levar para a conta" (tela 3)
  | "ja_tem"       // a conta já tem pet e este aparelho ainda não escolheu (tela 3, "A conta já tem pets")
  | "ok"           // "Na nuvem"
  | "enviando"     // "Enviando"
  | "offline"      // "Offline", com a hora da última sincronização (UX-NV-6: o aviso aparece uma vez)
  | "outro"        // "Só ver": outro aparelho tem a vez (travado)
  | "divergiu"     // duas histórias, a escolha pendente (travado)
  | "atualize"     // "Atualize o jogo"
  | "recusado";    // a nuvem recusou o registro (não reproduz): o jogo segue aqui

export interface Meta { base: Base | null; extras_hash: string | null; ultima: number | null; divergencia: string | null; vez: boolean }
export interface ResumoNuvem { forma: string; tick: number; guardados: number; aparelho: string | null; versao: number }

export interface Nuvem {
  estado: EstadoNuvem;
  vez: VezVista | null;
  divergencia: DivergenciaVista | null;
  /** a hora da última sincronização que deu certo */
  ultima: number | null;
  /** o pet da nuvem (a tela "A conta já tem pets") */
  resumo: ResumoNuvem | null;
  /** o aviso "o servidor não respondeu" já apareceu nesta abertura (UX-NV-6) */
  avisoForaVisto: boolean;
  ocupado: boolean;
  detalhe: string | null;
}
export const NV: Nuvem = { estado: "conferindo", vez: null, divergencia: null, ultima: null, resumo: null, avisoForaVisto: false, ocupado: false, detalhe: null };

let amb: AmbienteNuvem | null = null, csrf: string | null = null, revisao = 0, emCurso: Promise<void> | null = null;
const ouvintes = new Set<() => void>();
const avisar = (): void => { revisao++; for (const f of ouvintes) f(); };
export const ouvirNuvem = (f: () => void): (() => void) => { ouvintes.add(f); return () => { ouvintes.delete(f); }; };
export const revisaoNuvem = (): number => revisao;
export const nuvemLigada = (): boolean => amb !== null;
function exigir(): AmbienteNuvem { if (!amb) throw new Error("a nuvem está desligada"); return amb; }

const TRAVADOS: readonly EstadoNuvem[] = ["conferindo", "outro", "divergiu"];
/** o pet fica só para ver (UX-NV-5) */
export const soVer = (): boolean => amb !== null && TRAVADOS.includes(NV.estado);
function por(estado: EstadoNuvem, detalhe: string | null = null): void {
  NV.estado = estado; NV.detalhe = detalhe;
  amb?.travar(TRAVADOS.includes(estado));
  avisar();
}

export function ligarNuvem(a: AmbienteNuvem): void {
  amb = { ...a, api: a.api.replace(/\/+$/, "") };
  Object.assign(NV, { estado: "conferindo", vez: null, divergencia: null, ultima: lerMeta().ultima, resumo: null, avisoForaVisto: false, ocupado: false, detalhe: null });
  csrf = null;
  amb.travar(true);
  avisar();
}
export function desligarNuvem(): void { amb?.travar(false); amb = null; csrf = null; NV.estado = "conferindo"; avisar(); }

/* ------------------------------------------------------------------------------------------------ o armazenamento deste aparelho */
const META_VAZIA: Meta = { base: null, extras_hash: null, ultima: null, divergencia: null, vez: false };
export function lerMeta(): Meta {
  const t = amb?.armaz.getItem(CHAVE_NUVEM) ?? null;
  if (t === null) return { ...META_VAZIA };
  const d = JSON.parse(t) as Partial<Meta>;
  return { ...META_VAZIA, ...d };
}
const gravarMeta = (m: Meta): void => { exigir().armaz.setItem(CHAVE_NUVEM, JSON.stringify(m)); };

/** a chave do save do pet do jogador: o `-anterior` enquanto um pet dos Cenários ocupa a CHAVE (D-CONTA-34) */
const chaveDoSave = (a: AmbienteNuvem): string => (a.armaz.getItem(CHAVE_ANTERIOR) !== null ? CHAVE_ANTERIOR : CHAVE);
/** o save do pet do jogador neste aparelho; null sem save (o pet de exemplo ainda não gravou) */
export function lerSaveLocal(): SaveNuvem | null {
  const a = exigir(), t = a.armaz.getItem(chaveDoSave(a));
  if (t === null) return null;
  const d = JSON.parse(t) as SaveNuvem | null;
  if (d === null) return null;
  if (!Number.isInteger(d.semente) || !Array.isArray(d.log)) throw new Error("o save deste aparelho não tem semente e registro");
  return d;
}
/** o texto do save, no MESMO formato e na mesma ordem de campos que o jogo grava (src/save.ts: textoSave e textoSaveGrupo) */
export const textoDoSave = (s: SaveNuvem): string =>
  JSON.stringify(s.grupo ? { semente: s.semente, log: s.log, versao: s.versao, grupo: true, foco: s.foco } : { semente: s.semente, log: s.log, versao: s.versao });
export function lerExtrasLocais(): Record<string, string> {
  const a = exigir(), x: Record<string, string> = {};
  for (const k of [...CHAVES_NUVEM, ...a.chaves().filter(k => k.startsWith(PREFIXO_GOSTO_TV))]) {
    if (!ehChaveNuvem(k)) continue;
    const v = a.armaz.getItem(k);
    if (v !== null) x[k] = v;
  }
  return x;
}
export const lerPacoteLocal = (): Pacote | null => { const s = lerSaveLocal(); return s ? { save: s, extras: lerExtrasLocais() } : null; };

/** grava no aparelho o que veio da nuvem: o save e as outras chaves (as que a nuvem não tem saem daqui também) e pede ao jogo para reler */
function gravarLocal(save: SaveNuvem | null, extras: Record<string, string> | null): void {
  const a = exigir();
  if (save) a.armaz.setItem(chaveDoSave(a), textoDoSave(save));
  if (extras) {
    for (const k of [...CHAVES_NUVEM, ...a.chaves().filter(k => k.startsWith(PREFIXO_GOSTO_TV))]) if (!(k in extras)) a.armaz.removeItem(k);
    for (const [k, v] of Object.entries(extras)) if (ehChaveNuvem(k)) a.armaz.setItem(k, v);
  }
  if (save || extras) a.aoMudarLocal();
}

/* ------------------------------------------------------------------------------------------------ o hash */
async function sha256(texto: string): Promise<string> {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(texto));
  return [...new Uint8Array(d)].map(b => b.toString(16).padStart(2, "0")).join("");
}
/** o hash do registro até n: o SHA-256 de JSON.stringify(log.slice(0, n)) (o mesmo do servidor) */
export const hashAte = (log: readonly EventoNuvem[], n: number): Promise<string> => sha256(JSON.stringify(log.slice(0, n)));
export const hashExtras = (x: Record<string, string>): Promise<string> => sha256(textoExtras(x));

/* ------------------------------------------------------------------------------------------------ as chamadas */
class SemResposta extends Error {}
interface Resp { status: number; corpo: Record<string, unknown> }
async function chamar(metodo: string, caminho: string, corpo?: unknown): Promise<Resp> {
  const a = exigir(), controle = new AbortController(), relogio = setTimeout(() => controle.abort(), ESPERA_NUVEM_MS);
  const headers: Record<string, string> = {};
  if (metodo !== "GET") { if (csrf === null) await lerCsrf(); if (csrf !== null) headers["X-CSRF-Token"] = csrf; }
  if (corpo !== undefined) headers["Content-Type"] = "application/json";
  try {
    const r = await a.buscar(a.api + caminho, { method: metodo, headers, credentials: "include", signal: controle.signal, body: corpo === undefined ? undefined : JSON.stringify(corpo) });
    const t = await r.text();
    let d: unknown = {};
    if (t) { try { d = JSON.parse(t); } catch { throw new Error(`o servidor respondeu ${r.status} sem JSON em ${caminho}`); } }
    return { status: r.status, corpo: (typeof d === "object" && d !== null && !Array.isArray(d) ? d : { lista: d }) as Record<string, unknown> };
  } catch (err) {
    if (err instanceof TypeError || (err instanceof Error && err.name === "AbortError")) throw new SemResposta();
    throw err;
  } finally { clearTimeout(relogio); }
}
/** o csrf da sessão (o mesmo das rotas da conta, pelo GET /conta) */
async function lerCsrf(): Promise<void> {
  const a = exigir();
  const r = await a.buscar(a.api + "/conta", { method: "GET", credentials: "include" });
  if (r.status !== 200) { csrf = null; return; }
  const d = await r.json() as { csrf?: unknown };
  csrf = typeof d.csrf === "string" ? d.csrf : null;
}

/** o que uma resposta comum diz: a sessão, o "atualize" e o resto (true: tratada aqui, quem chamou para) */
function tratarComum(r: Resp): boolean {
  /* sem sessão: "Entre de novo" só se este aparelho já sincronizava; senão, ele nunca entrou, e é o "salvo" de sempre */
  if (r.status === 401) { csrf = null; por(lerMeta().base !== null ? "sessao" : "sem_conta"); return true; }
  if (r.status === 403) { csrf = null; return false; }
  if (r.status === 426) { por("atualize", String(r.corpo.detalhe ?? "")); return true; }
  if (r.status === 422) { por("recusado", String(r.corpo.detalhe ?? r.corpo.erro ?? "")); return true; }
  return false;
}
const resposta = (r: Resp): RespostaSync => r.corpo as unknown as RespostaSync;

/** o pet da nuvem foi aberto em outra versão do jogo (5.5): este aparelho não abre o pet dela */
const versaoDesconhecida = (versao: number | undefined, versoes: readonly number[]): boolean => versao !== undefined && !versoes.includes(versao);
let versoesDoJogo: readonly number[] = [];
/** as versões de pet que este jogo abre (o motor; a raiz passa VERSOES_PET) */
export const conhecerVersoes = (v: readonly number[]): void => { versoesDoJogo = v; };

/* ------------------------------------------------------------------------------------------------ o fluxo */
/** a abertura: pergunta à nuvem em que pé a conta está e põe o estado certo. Depois, `sincronizar` a cada INTERVALO_SYNC_MS */
export async function abrirNuvem(): Promise<void> {
  exigir();
  por("conferindo");
  try {
    const r = await chamar("GET", "/nuvem");
    if (tratarComum(r)) return;
    if (r.status !== 200) throw new Error(`o estado da nuvem não veio (${r.status})`);
    const d = resposta(r) as RespostaSync & { guardados?: number; atualizado_por?: string | null };
    const meta = lerMeta();
    NV.divergencia = d.divergencia ?? null; NV.vez = d.vez;
    if (d.situacao === "sem_pet") { gravarMeta({ ...meta, base: null, vez: false }); return por("sem_pet"); }
    if (versaoDesconhecida(d.versao, versoesDoJogo)) return por("atualize", `o pet da nuvem é da versão ${d.versao}`);
    NV.resumo = { forma: d.forma ?? "", tick: d.tick ?? 0, guardados: d.guardados ?? 0, aparelho: d.atualizado_por ?? null, versao: d.versao ?? 0 };
    /* este aparelho ainda não está ligado ao pet da nuvem: a escolha da tela 3 */
    if (meta.base === null) return por("ja_tem");
    await pedirVez(false);
  } catch (err) {
    /* a rede fora, ou uma resposta que o jogo não entende: nunca fica travado por isso (o jogo segue neste aparelho, 5.1) */
    if (!(err instanceof SemResposta)) console.error(err);
    return foraDoAr();
  }
}
function foraDoAr(): void { por("offline"); }
/** o aviso "o servidor não respondeu" já foi visto (UX-NV-6: depois, só o estado "Offline") */
export function verAvisoFora(): void { NV.avisoForaVisto = true; avisar(); }

/** pede a vez; com `jogarAqui`, toma a do outro aparelho. Depois, sincroniza (para jogar a partir da ponta da nuvem) */
export async function pedirVez(jogarAqui: boolean): Promise<void> {
  const r = await chamar("POST", "/nuvem/vez", { protocolo: PROTOCOLO_NUVEM, jogar_aqui: jogarAqui });
  if (tratarComum(r)) return;
  const d = resposta(r);
  NV.vez = d.vez; NV.divergencia = d.divergencia ?? null;
  const meta = lerMeta();
  if (r.status === 409 && d.situacao === "divergiu") { gravarMeta({ ...meta, divergencia: d.divergencia?.id ?? meta.divergencia }); await sincronizar(); return; }
  if (r.status === 409 && d.situacao === "outro") { gravarMeta({ ...meta, vez: false }); await sincronizar(); return; }
  if (r.status !== 200) throw new Error(`a vez não veio (${r.status})`);
  gravarMeta({ ...meta, vez: true });
  await sincronizar();
}
/** "Jogar aqui" (a tela "Outro aparelho"): toma a vez */
export async function jogarAqui(): Promise<void> {
  NV.ocupado = true; avisar();
  try { await pedirVez(true); } catch (err) { if (err instanceof SemResposta) foraDoAr(); else throw err; } finally { NV.ocupado = false; avisar(); }
}

/** uma sincronização (5.1): manda os eventos depois da base (ou o save inteiro) e grava o que a nuvem mandou. Uma de cada vez */
export function sincronizar(): Promise<void> {
  if (!amb) return Promise.resolve();
  if (["sem_conta", "sessao", "sem_pet", "ja_tem", "atualize"].includes(NV.estado)) return Promise.resolve();
  emCurso ??= rodarSync().catch((err: unknown) => {
    /* a resposta que o jogo não entende: o erro vai ao console, e o estado fica "offline" se ele ainda travava na abertura */
    console.error(err);
    if (NV.estado === "conferindo") foraDoAr();
  }).finally(() => { emCurso = null; });
  return emCurso;
}
async function rodarSync(reenviarCompleto = false): Promise<void> {
  const meta = lerMeta(), save = lerSaveLocal();
  if (!save) return;
  const trava = soVer() && NV.estado !== "conferindo";
  /* o que este aparelho tem depois da base: os novos, ou o save inteiro (o pet trocou, ou o começo do registro não é o da base) */
  const id = idDoSave(save), b = meta.base;
  let novos: EventoNuvem[] = [], completo: SaveNuvem | undefined;
  if (b && b.id === id && save.log.length >= b.eventos && (await hashAte(save.log, b.eventos)) === b.hash) novos = save.log.slice(b.eventos);
  else completo = save;
  if (reenviarCompleto) { completo = save; novos = []; }
  /* a divergência resolvida: a história deste aparelho já está guardada na nuvem (Gerações e cópias); o aparelho passa a ter a da nuvem */
  if (meta.divergencia !== null && NV.divergencia === null && NV.estado !== "divergiu") { await puxarTudo(); return; }
  const extras = lerExtrasLocais(), hx = await hashExtras(extras);
  const pedido: PedidoSync = { protocolo: PROTOCOLO_NUVEM, base: b, id, novos, extras_hash: meta.extras_hash };
  if (save.grupo && save.foco) pedido.foco = save.foco;
  if (completo) pedido.completo = completo;
  /* travado, as outras chaves não sobem (o que mudou aqui sem a vez não é do pet) */
  if (hx !== meta.extras_hash && !trava) pedido.extras = extras;
  const temNovo = novos.some(e => e[1] !== "t") || completo !== undefined || pedido.extras !== undefined;
  if (temNovo && NV.estado === "ok") { NV.estado = "enviando"; avisar(); }
  let r: Resp;
  try { r = await chamar("POST", "/nuvem/sync", pedido); } catch (err) { if (err instanceof SemResposta) return foraDoAr(); throw err; }
  if (tratarComum(r)) return;
  if (r.status !== 200) throw new Error(`a sincronização falhou (${r.status}): ${JSON.stringify(r.corpo)}`);
  const d = resposta(r);
  NV.vez = d.vez; NV.divergencia = d.divergencia ?? null;
  const t = exigir().agora();
  if (d.situacao === "sem_pet") { gravarMeta({ ...meta, base: null }); return por("sem_pet"); }
  if (d.situacao === "divergiu") {
    gravarMeta({ ...meta, divergencia: d.divergencia?.id ?? meta.divergencia, ultima: t });
    NV.ultima = t;
    return por("divergiu");
  }
  if (versaoDesconhecida(d.versao, versoesDoJogo)) return por("atualize", `o pet da nuvem é da versão ${d.versao}`);
  /* a nuvem pediu o save inteiro (a base deste aparelho não é um começo do registro dela): manda de novo, uma vez */
  if (d.detalhe && d.completo && !reenviarCompleto && temNovo) return rodarSync(true);
  let novoSave: SaveNuvem | null = null;
  if (d.completo) novoSave = d.completo;
  else if (d.novos) {
    /* os novos da nuvem depois da base: o registro daqui até a base, mais eles (mesmo vazios: o que este aparelho tinha a mais sai) */
    const log = [...save.log.slice(0, b?.eventos ?? 0), ...d.novos];
    if (JSON.stringify(log) !== JSON.stringify(save.log) || (d.foco && d.foco !== save.foco)) novoSave = { ...save, log, ...(d.foco ? { foco: d.foco } : {}) };
  }
  if (novoSave || d.extras) gravarLocal(novoSave, d.extras ?? null);
  /* o que a nuvem confirmou: a posição dela e o hash das outras chaves (o que este aparelho mandou, ou o que acabou de gravar) */
  const hxNovo = d.extras ? await hashExtras(lerExtrasLocais()) : pedido.extras ? hx : meta.extras_hash;
  gravarMeta({ base: d.base, extras_hash: d.extras_hash === hxNovo ? hxNovo : d.extras_hash, ultima: t, divergencia: null, vez: d.vez.minha });
  NV.ultima = t;
  por(d.situacao === "outro" ? "outro" : "ok");
}
/** baixa o pacote inteiro da nuvem e grava aqui (a divergência resolvida, ou "ficar com os da nuvem") */
async function puxarTudo(): Promise<void> {
  const r = await chamar("GET", "/nuvem/pacote");
  if (tratarComum(r)) return;
  if (r.status !== 200) throw new Error(`o pacote da nuvem não veio (${r.status})`);
  const d = r.corpo as unknown as RespostaSync & { pacote: Pacote };
  gravarLocal(d.pacote.save, d.pacote.extras);
  const t = exigir().agora();
  gravarMeta({ base: d.base, extras_hash: d.extras_hash, ultima: t, divergencia: null, vez: d.vez.minha });
  NV.ultima = t; NV.vez = d.vez; NV.divergencia = d.divergencia ?? null;
  por(d.vez.minha || d.vez.aparelho === null ? "ok" : "outro");
}

/** a tela 3: levar o pet para a conta. `escolha`: "levar" (a conta sem pet), "aparelho", "nuvem" ou "os_dois" (UX-NV-1: a marcada) */
export type EscolhaLevar = "levar" | "aparelho" | "nuvem" | "os_dois";
export async function levarParaConta(escolha: EscolhaLevar): Promise<void> {
  const a = exigir();
  NV.ocupado = true; avisar();
  try {
    let pacote = lerPacoteLocal();
    if (!pacote) throw new Error("este aparelho ainda não tem pet para levar");
    if (escolha === "os_dois") pacote = await juntarOsDois(pacote);
    const r = await chamar("POST", "/nuvem/levar", { protocolo: PROTOCOLO_NUVEM, escolha, pacote });
    if (tratarComum(r)) return;
    if (r.status === 409 && r.corpo.ja_tem) { const d = resposta(r) as RespostaSync & { guardados?: number }; NV.resumo = { forma: d.forma ?? "", tick: d.tick ?? 0, guardados: d.guardados ?? 0, aparelho: null, versao: d.versao ?? 0 }; return por("ja_tem"); }
    if (r.status !== 200 && r.status !== 201) throw new Error(`levar o pet não deu (${r.status}): ${JSON.stringify(r.corpo)}`);
    const d = resposta(r);
    if (escolha === "nuvem") { await puxarTudo(); return; }
    /* "os_dois" gravou aqui também o guardado novo (o pet da nuvem) */
    if (escolha === "os_dois") gravarLocal(null, pacote.extras);
    const t = a.agora();
    gravarMeta({ base: d.base, extras_hash: d.extras_hash, ultima: t, divergencia: null, vez: true });
    NV.vez = d.vez; NV.ultima = t;
    por("ok");
  } catch (err) {
    if (err instanceof SemResposta) return foraDoAr();
    throw err;
  } finally { NV.ocupado = false; avisar(); }
}
/** "Guardar os dois" (UX-NV-1): o pet deste aparelho segue ativo; o pet ativo da nuvem e os guardados dela entram nos guardados daqui.
    O pacote inteiro da nuvem vai também para as cópias, no servidor (o Tamer e Gerações dela não se juntam) */
async function juntarOsDois(p: Pacote): Promise<Pacote> {
  const r = await chamar("GET", "/nuvem/pacote");
  if (r.status !== 200) throw new Error(`o pacote da nuvem não veio (${r.status})`);
  const nuvem = (r.corpo as unknown as { pacote: Pacote }).pacote, k = CHAVE + "-guardados";
  const daqui = JSON.parse(p.extras[k] ?? "[]") as unknown[], dela = JSON.parse(nuvem.extras[k] ?? "[]") as unknown[];
  const s = nuvem.save, ativo = s.grupo ? { semente: s.semente, log: s.log, versao: s.versao, grupo: true, foco: s.foco } : { semente: s.semente, log: s.log, versao: s.versao };
  return { save: p.save, extras: { ...p.extras, [k]: JSON.stringify([...daqui, ativo, ...dela]) } };
}

/** "Agora não" na tela 3: o pet fica só neste aparelho, sem sincronizar (a oferta fica em Ajustes › Conta) */
export function agoraNao(): void { por("sem_conta"); }

/** a escolha da história (5.3): "nuvem" (a que está na nuvem) ou "outra" (a do aparelho que divergiu). "Decidir depois" não chama nada */
export async function escolherHistoria(fica: "nuvem" | "outra"): Promise<void> {
  const d0 = NV.divergencia;
  if (!d0) throw new Error("não há escolha pendente");
  NV.ocupado = true; avisar();
  try {
    const r = await chamar("POST", "/nuvem/divergencia", { protocolo: PROTOCOLO_NUVEM, id: d0.id, fica });
    if (tratarComum(r)) return;
    if (r.status !== 200) throw new Error(`a escolha não deu (${r.status}): ${JSON.stringify(r.corpo)}`);
    NV.divergencia = null;
    await puxarTudo();
    await pedirVez(false);
  } catch (err) {
    if (err instanceof SemResposta) return foraDoAr();
    throw err;
  } finally { NV.ocupado = false; avisar(); }
}

export interface Copia { id: string; feitaEm: number; motivo: string; eventos: number; forma: string; tick: number; apagarEm: number }
export async function listarCopias(): Promise<Copia[]> {
  const r = await chamar("GET", "/nuvem/copias");
  if (r.status !== 200) throw new Error(`as cópias não vieram (${r.status})`);
  return (r.corpo.lista as Record<string, unknown>[]).map(c => ({ id: String(c.id), feitaEm: Number(c.feita_em), motivo: String(c.motivo), eventos: Number(c.eventos),
    forma: String(c.forma), tick: Number(c.tick), apagarEm: Number(c.apagar_em) }));
}
/** restaurar uma cópia (5.6): o de agora vira uma cópia, e a restaurada vale para todos os aparelhos */
export async function restaurarCopia(id: string): Promise<void> {
  NV.ocupado = true; avisar();
  try {
    const r = await chamar("POST", `/nuvem/copias/${encodeURIComponent(id)}/restaurar`, { protocolo: PROTOCOLO_NUVEM });
    if (tratarComum(r)) return;
    if (r.status !== 200) throw new Error(`restaurar não deu (${r.status}): ${JSON.stringify(r.corpo)}`);
    await puxarTudo();
  } catch (err) {
    if (err instanceof SemResposta) return foraDoAr();
    throw err;
  } finally { NV.ocupado = false; avisar(); }
}
export interface Historia { id: string; criadaEm: number; aparelho: string; eventos: number; forma: string; tick: number }
/** as histórias não escolhidas (Gerações, só para ver) */
export async function listarHistorias(): Promise<Historia[]> {
  const r = await chamar("GET", "/nuvem/historias");
  if (r.status !== 200) throw new Error(`as histórias não vieram (${r.status})`);
  return (r.corpo.lista as Record<string, unknown>[]).map(h => ({ id: String(h.id), criadaEm: Number(h.criada_em), aparelho: String(h.aparelho_nome),
    eventos: Number(h.eventos), forma: String(h.forma), tick: Number(h.tick) }));
}
/** o save de uma história, para abrir só para ver */
export async function saveDaHistoria(id: string): Promise<SaveNuvem> {
  const r = await chamar("GET", `/nuvem/historias/${encodeURIComponent(id)}`);
  if (r.status !== 200) throw new Error(`a história não veio (${r.status})`);
  return r.corpo.save as SaveNuvem;
}
