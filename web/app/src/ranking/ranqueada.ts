/* O cliente da luta ranqueada (MMO4; docs/PLANO_UX_LUTA_RANQUEADA.md, UX-LR-1 a 6 APROVADAS em 2026-11-17): o pedido da semente, a
   previa, o envio depois da luta e o reenvio. Sem React e sem DOM: a tela (TelaLugaresPoc.tsx) le o estado por `useRanqueada` e chama as
   funcoes daqui; os testes ligam um `fetch` e um armazenamento falsos (test/ranqueada.test.ts).

   A chave: sem `ligarRanqueada` (a tela so liga com VITE_DIGILAB_API no build), nada daqui roda e a Arena e a de sempre.

   O que o servidor decide (MMO-5): os pontos, o limite do dia e a trava do nivel. O que fica aqui e a previa (o que o jogo viu) e a lista
   das lutas pedidas neste aparelho, guardada em CHAVE-ranqueada para o resultado e o reenvio sobreviverem a um recarregar. Essa lista nao e
   o save do pet: apaga-la so perde a previa; o servidor devolve as lutas do pet de novo em cada envio aceito.

   O motor nao muda: a luta ranqueada e o `lutarPoc` de sempre, com a semente que o servidor entregou, na posicao `indice` do registro. */
import { DIGIMON_DA_FORMA, type EventoRegistro } from "../../motor/index.ts";
import { CHAVE, type Armazenamento } from "../chave.ts";
import { pedidoDaSemente } from "./pedido.ts";
import { LUTAS_POR_DIA, PONTOS_FAIXA, diaDe, semanaDe, type LutaRanqueada, type Situacao } from "./pontos.ts";

export const CHAVE_RANQUEADA = CHAVE + "-ranqueada";
/** a espera do pedido da semente e do envio, em milissegundos (PROPOSTOS, SEM FONTE): o envio refaz a vida no servidor (~0,4 s por vida) */
export const ESPERA_PEDIDO_MS = 15_000;
export const ESPERA_ENVIO_MS = 60_000;

export interface AmbienteRanqueada {
  /** o endereco do servidor, sem a barra do fim */
  api: string;
  buscar: (url: string, init?: RequestInit) => Promise<Response>;
  armaz: Armazenamento;
  agora: () => number;
}

/** o pet como o envio o leva */
export interface PetDoEnvio { semente: number; versao: number; log: readonly EventoRegistro[] }
export interface TamerDoEnvio { versao: number; log: readonly unknown[] }

/** uma luta pedida neste aparelho */
export interface LutaGuardada {
  numero: number; semente: number; indice: number;
  /** a hora do servidor, em ms UTC, com o dia e a semana de Brasilia que ele deu */
  hora: number; dia: string; semana: string;
  /** a ordem da luta no dia (1 a LUTAS_POR_DIA), pelo `restam_hoje` do servidor */
  doDia: number;
  pet: number; versao: number;
  rival: string | null; mapa: string | null;
  /** o que o jogo viu; null enquanto a luta nao entrou no registro */
  previa: { venceu: boolean; pontos: number } | null;
  /** o que o servidor contou; null ate o envio ser conferido */
  servidor: { situacao: Situacao; pontos: number } | null;
  /** pendente: ainda nao chegou ao servidor; conferido: o servidor respondeu; recusado: o servidor recusou o envio (o motivo em `motivo`) */
  envio: "pendente" | "conferido" | "recusado";
  motivo?: string;
}

export type EstadoPedido =
  | { tipo: "parado" }
  | { tipo: "pedindo" }
  | { tipo: "sem_resposta" }
  | { tipo: "limite"; reabreEm: number }
  | { tipo: "trancada"; marco: number | null }
  | { tipo: "sem_conta" }
  | { tipo: "versao" }
  /** o servidor recusou por outro motivo (a ordem do registro); `gasta`: a luta pedida ja contou */
  | { tipo: "recusado"; motivo: string; gasta: boolean };

export interface EstadoRanqueada {
  pedido: EstadoPedido;
  lutas: LutaGuardada[];
  /** as lutas de hoje ja pedidas, pelo servidor; null ate a primeira resposta */
  hoje: number | null;
  /** o numero da luta que o resultado mostra; null fora do resultado */
  resultado: number | null;
  /** um envio esta a caminho */
  enviando: boolean;
  /** o marco que tranca a luta, quando o servidor ja disse (o cadeado na escolha) */
  trancada: number | null;
}

export const RQ: EstadoRanqueada = { pedido: { tipo: "parado" }, lutas: [], hoje: null, resultado: null, enviando: false, trancada: null };
let amb: AmbienteRanqueada | null = null;
let csrf: string | null = null;
let revisao = 0;
const ouvintes = new Set<() => void>();
function avisar(): void { revisao++; for (const f of ouvintes) f(); }
export const ouvirRanqueada = (f: () => void): (() => void) => { ouvintes.add(f); return () => { ouvintes.delete(f); }; };
export const revisaoRanqueada = (): number => revisao;

export const ranqueadaLigada = (): boolean => amb !== null;
/** o endereco do servidor, para o Entrar no local; null com a chave desligada */
export const apiRanqueada = (): string | null => amb?.api ?? null;

/* ---------------------------------------------------------------- o que fica guardado */
interface Guardado { versao: 1; lutas: LutaGuardada[] }
const inteiro = (x: unknown): x is number => typeof x === "number" && Number.isInteger(x);

/** le a lista guardada; o que nao e a lista deste formato levanta (falhar alto: a tela mostra o erro e nao grava por cima) */
export function lerGuardado(texto: string | null): LutaGuardada[] {
  if (texto === null) return [];
  const d = JSON.parse(texto) as Guardado;
  if (typeof d !== "object" || d === null || d.versao !== 1 || !Array.isArray(d.lutas)) throw new Error("lutas ranqueadas guardadas num formato desconhecido");
  for (const l of d.lutas)
    if (!inteiro(l.numero) || !inteiro(l.semente) || !inteiro(l.indice) || !inteiro(l.pet) || typeof l.semana !== "string" || !["pendente", "conferido", "recusado"].includes(l.envio))
      throw new Error(`luta ranqueada guardada inválida: ${JSON.stringify(l)}`);
  return d.lutas;
}
function gravar(): void {
  if (!amb) return;
  /* ficam as lutas da semana de agora e as que ainda nao chegaram ao servidor */
  const semana = semanaDe(amb.agora());
  RQ.lutas = RQ.lutas.filter(l => l.semana === semana || l.envio === "pendente");
  amb.armaz.setItem(CHAVE_RANQUEADA, JSON.stringify({ versao: 1, lutas: RQ.lutas } satisfies Guardado));
}

/** liga a luta ranqueada neste ambiente e le o que estava guardado */
export function ligarRanqueada(a: AmbienteRanqueada): void {
  amb = { ...a, api: a.api.replace(/\/+$/, "") };
  csrf = null;
  Object.assign(RQ, { pedido: { tipo: "parado" }, lutas: lerGuardado(a.armaz.getItem(CHAVE_RANQUEADA)), hoje: null, resultado: null, enviando: false, trancada: null });
  avisar();
}
/** desliga (os testes) */
export function desligarRanqueada(): void {
  amb = null; csrf = null;
  Object.assign(RQ, { pedido: { tipo: "parado" }, lutas: [], hoje: null, resultado: null, enviando: false, trancada: null });
  avisar();
}

/* ---------------------------------------------------------------- a conversa com o servidor */
class SemResposta extends Error {}
class SemConta extends Error {}

async function chamar(caminho: string, espera: number, init: RequestInit = {}): Promise<{ status: number; corpo: Record<string, unknown> | unknown[] }> {
  if (!amb) throw new Error("a luta ranqueada está desligada");
  let r: Response;
  try {
    r = await amb.buscar(amb.api + caminho, { ...init, credentials: "include", cache: "no-store", signal: AbortSignal.timeout(espera) });
  } catch (err) { throw new SemResposta(err instanceof Error ? err.message : String(err)); }
  let corpo: unknown;
  try { corpo = await r.json(); } catch (err) { throw new SemResposta(`resposta sem JSON (${r.status}): ${err instanceof Error ? err.message : String(err)}`); }
  if (typeof corpo !== "object" || corpo === null) throw new SemResposta(`resposta inesperada (${r.status})`);
  return { status: r.status, corpo: corpo as Record<string, unknown> };
}
/** o csrf da sessao (GET /conta); sem sessao, levanta SemConta */
async function pegarCsrf(): Promise<string> {
  if (csrf) return csrf;
  const { status, corpo } = await chamar("/conta", ESPERA_PEDIDO_MS);
  if (status === 401) throw new SemConta();
  const c = (corpo as Record<string, unknown>).csrf;
  if (status !== 200 || typeof c !== "string") throw new SemResposta(`/conta respondeu ${status}`);
  return csrf = c;
}
async function postar(caminho: string, dados: unknown, espera: number): Promise<{ status: number; corpo: Record<string, unknown> }> {
  const r = await chamar(caminho, espera, { method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": await pegarCsrf() }, body: JSON.stringify(dados) });
  if (r.status === 401) { csrf = null; throw new SemConta(); }
  return r as { status: number; corpo: Record<string, unknown> };
}

/** as lutas de hoje, pelas sementes que o servidor ja entregou a conta (GET /sementes); calado se nao der */
export async function atualizarHoje(): Promise<void> {
  if (!amb) return;
  try {
    const { status, corpo } = await chamar("/sementes", ESPERA_PEDIDO_MS);
    if (status !== 200 || !Array.isArray(corpo)) return;
    const hoje = diaDe(amb.agora());
    RQ.hoje = (corpo as { dia?: unknown }[]).filter(s => s.dia === hoje).length;
    avisar();
  } catch (err) { if (!(err instanceof SemResposta)) throw err; }
}

/* ---------------------------------------------------------------- o pedido */
/** pede a semente da proxima luta do pet. Devolve a luta guardada, ou null com o motivo em RQ.pedido. Quem chama segura o tempo do jogo
    ate a luta entrar no registro: o `indice` do pedido e o fim do registro de agora */
export async function pedirSemente(pet: PetDoEnvio, rival: string, mapa: string | null): Promise<LutaGuardada | null> {
  if (!amb) throw new Error("a luta ranqueada está desligada");
  if (RQ.pedido.tipo === "pedindo") throw new Error("já há um pedido de luta ranqueada a caminho");
  RQ.pedido = { tipo: "pedindo" }; avisar();
  const fim = (e: EstadoPedido): null => { RQ.pedido = e; avisar(); return null; };
  try {
    const pedido = await pedidoDaSemente(pet, rival, mapa);
    const { status, corpo } = await postar("/sementes", pedido, ESPERA_PEDIDO_MS);
    const motivo = typeof corpo.motivo === "string" ? corpo.motivo : "";
    if (status === 201) {
      const { numero, semente, indice, hora, dia, semana, restam_hoje: restam } = corpo;
      const ms = typeof hora === "string" ? Date.parse(hora) : NaN;
      if (!inteiro(numero) || !inteiro(semente) || indice !== pedido.indice || !Number.isFinite(ms) || typeof dia !== "string" || typeof semana !== "string" || !inteiro(restam))
        throw new Error(`o servidor entregou uma semente que o jogo não entende: ${JSON.stringify(corpo)}`);
      const luta: LutaGuardada = { numero, semente, indice, hora: ms, dia, semana, doDia: LUTAS_POR_DIA - restam, pet: pet.semente, versao: pet.versao,
        rival, mapa, previa: null, servidor: null, envio: "pendente" };
      RQ.lutas.push(luta); RQ.hoje = luta.doDia; RQ.trancada = null; RQ.pedido = { tipo: "parado" };
      gravar(); avisar();
      return luta;
    }
    if (status === 429 && motivo === "limite_do_dia") {
      const t = typeof corpo.reabre_em === "string" ? Date.parse(corpo.reabre_em) : NaN;
      if (!Number.isFinite(t)) throw new Error(`limite do dia sem a hora de volta: ${JSON.stringify(corpo)}`);
      RQ.hoje = LUTAS_POR_DIA;
      return fim({ tipo: "limite", reabreEm: t });
    }
    if (status === 403 && motivo === "nivel_insuficiente") {
      RQ.trancada = inteiro(corpo.marco) ? corpo.marco : null;
      return fim({ tipo: "trancada", marco: RQ.trancada });
    }
    if (status === 422 && motivo === "versao_pet_desconhecida") return fim({ tipo: "versao" });
    if (status === 409) return fim({ tipo: "recusado", motivo, gasta: false });
    throw new Error(`o pedido da luta foi recusado (${status}): ${typeof corpo.erro === "string" ? corpo.erro : JSON.stringify(corpo)}`);
  } catch (err) {
    if (err instanceof SemConta) return fim({ tipo: "sem_conta" });
    if (err instanceof SemResposta) return fim({ tipo: "sem_resposta" });
    RQ.pedido = { tipo: "parado" }; avisar();
    throw err;
  }
}
/** volta a escolha (Tentar de novo, Lutar de treino, Agora nao) */
export function fecharEstado(): void { if (RQ.pedido.tipo !== "pedindo") { RQ.pedido = { tipo: "parado" }; avisar(); } }

/** a luta pedida nao entrou no registro (o registro mudou durante o pedido, ou o motor recusou a luta): ela ja contou no servidor */
export function lutaPerdida(numero: number, motivo: string): void {
  RQ.pedido = { tipo: "recusado", motivo, gasta: true };
  const l = RQ.lutas.find(x => x.numero === numero);
  if (l) l.motivo = motivo;
  gravar(); avisar();
}

/* ---------------------------------------------------------------- a previa */
const faixaDe = (rival: string): string | null => DIGIMON_DA_FORMA[rival]?.[1] ?? null;
/** a luta valeu vitoria, pelo que se sabe: a palavra do servidor, ou a previa enquanto ele nao respondeu */
const venceu = (l: LutaGuardada): boolean => (l.servidor ? l.servidor.situacao === "vitoria" : l.previa?.venceu === true);

/** quanto vale a vitoria contra o rival agora (a previa da conta da MMO1): a faixa dele, pela metade a cada vitoria na semana. 0: o rival
    nao vale ponto (fora das faixas do PONTOS_FAIXA) */
export function valorDoRival(rival: string, pet: number, agora: number): { pontos: number; vencido: number } {
  const base = PONTOS_FAIXA[faixaDe(rival) ?? ""] ?? 0, semana = semanaDe(agora);
  const vencido = RQ.lutas.filter(l => l.pet === pet && l.semana === semana && l.rival === rival && venceu(l)).length;
  return { pontos: base / 2 ** vencido, vencido };
}
/** o placar do pet: as lutas de hoje e os pontos e os rivais da semana. Os pontos sao so os conferidos pelo servidor (UX-LR-3: a previa
    nunca soma) */
export function placarDoPet(pet: number, agora: number): { hoje: number; pontos: number; rivais: number } {
  const semana = semanaDe(agora), dia = diaDe(agora);
  const daSemana = RQ.lutas.filter(l => l.pet === pet && l.semana === semana && l.servidor);
  return {
    hoje: RQ.hoje ?? RQ.lutas.filter(l => l.dia === dia).length,
    pontos: daSemana.reduce((s, l) => s + l.servidor!.pontos, 0),
    rivais: new Set(daSemana.filter(l => l.servidor!.situacao === "vitoria").map(l => l.rival)).size,
  };
}

/** a luta entrou no registro: guarda o que o jogo viu e abre o resultado dela */
export function registrarPrevia(numero: number, rival: string, mapa: string | null, ganhou: boolean, agora: number): void {
  const l = RQ.lutas.find(x => x.numero === numero);
  if (!l) throw new Error(`luta ranqueada desconhecida: ${numero}`);
  const pontos = ganhou ? valorDoRival(rival, l.pet, agora).pontos : 0;   // antes de marcar a previa: a vitoria desta luta nao conta na metade dela
  Object.assign(l, { rival, mapa, previa: { venceu: ganhou, pontos } });
  RQ.resultado = numero;
  gravar(); avisar();
}
export function fecharResultado(): void { RQ.resultado = null; avisar(); }

/** o servidor contou outra coisa que a previa (MMO-5: vale a dele) */
export function divergiu(l: LutaGuardada): boolean {
  if (!l.servidor || !l.previa) return false;
  return (l.servidor.situacao === "vitoria") !== l.previa.venceu || l.servidor.pontos !== l.previa.pontos;
}

/* ---------------------------------------------------------------- o envio */
export const temPendente = (pet: number): boolean => RQ.lutas.some(l => l.pet === pet && l.envio === "pendente" && l.previa !== null);

/** envia o registro do pet e o do Tamer; o servidor confere e devolve as lutas do pet. Sem resposta, as lutas ficam pendentes (o reenvio
    tenta de novo). Devolve se o servidor respondeu */
export async function enviarRegistro(pet: PetDoEnvio, tamer: TamerDoEnvio): Promise<boolean> {
  if (!amb) throw new Error("a luta ranqueada está desligada");
  if (RQ.enviando) return false;
  RQ.enviando = true; avisar();
  try {
    const { status, corpo } = await postar("/envios", { pet: { semente: pet.semente, log: pet.log, versao: pet.versao }, tamer }, ESPERA_ENVIO_MS);
    const doPet = RQ.lutas.filter(l => l.pet === pet.semente && l.versao === pet.versao);
    if (status === 201 || status === 200) {
      if (Array.isArray(corpo.lutas)) {
        for (const s of corpo.lutas as LutaRanqueada[]) {
          let l = doPet.find(x => x.semente === s.semente);
          /* uma luta deste pet pedida em outro aparelho: entra na lista pelo que o servidor contou */
          if (!l) {
            l = { numero: -s.semente, semente: s.semente, indice: s.indice, hora: s.hora, dia: s.dia, semana: s.semana, doDia: 0, pet: pet.semente, versao: pet.versao,
              rival: s.rival, mapa: null, previa: null, servidor: null, envio: "conferido" };
            RQ.lutas.push(l);
          }
          /* a pendente e a que o registro ainda nao alcancou: continua a espera */
          if (s.situacao === "pendente") continue;
          Object.assign(l, { servidor: { situacao: s.situacao, pontos: s.pontos }, envio: "conferido", rival: l.rival ?? s.rival });
        }
      } else {
        /* o mesmo envio de novo (a resposta de antes se perdeu): o servidor so devolve a linha, sem as lutas. Fica a previa como conferida */
        for (const l of doPet) if (l.envio === "pendente" && l.previa) Object.assign(l, { servidor: { situacao: l.previa.venceu ? "vitoria" : "derrota", pontos: l.previa.pontos }, envio: "conferido" });
      }
      gravar();
      return true;
    }
    if (status === 422) {
      const motivo = typeof corpo.motivo === "string" ? corpo.motivo : "recusado";
      for (const l of doPet) if (l.envio === "pendente") Object.assign(l, { envio: "recusado", motivo });
      if (motivo === "versao_pet_desconhecida" || motivo === "versao_tamer_desconhecida") RQ.pedido = { tipo: "versao" };
      gravar();
      return true;
    }
    throw new Error(`o envio foi recusado (${status}): ${typeof corpo.erro === "string" ? corpo.erro : JSON.stringify(corpo)}`);
  } catch (err) {
    if (err instanceof SemConta) { RQ.pedido = { tipo: "sem_conta" }; return false; }
    if (err instanceof SemResposta) return false;
    throw err;
  } finally { RQ.enviando = false; avisar(); }
}
