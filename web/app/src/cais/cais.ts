/* O cliente do cais (MMO5 no jogo; docs/PLANO_UX_CAIS.md, UX-CA-1 a 7 APROVADAS em 2026-11-17): a semana, as tabelas por estagio e o
   segredo publicado, contra as rotas do servidor_web (servidor_web/src/envio/semanas.ts). Sem React e sem DOM: a tela
   (telas/cais/TelaCais.tsx) le o estado por `ouvirCais`/`revisaoCais` e chama as funcoes daqui; os testes ligam um `fetch` falso
   (test/cais.test.ts).

   A chave: sem `ligarCais` (a tela so liga com VITE_DIGILAB_API no build), nada daqui roda e o cais continua sem menu.

   O cais so le o servidor: nada aqui toca o motor, o registro nem o save, e nada se guarda no navegador. */
import { FUSO_BRASILIA_MS, PONTOS_FAIXA } from "../ranking/pontos.ts";

/** a espera de cada chamada, em milissegundos (PROPOSTA, SEM FONTE; a mesma da conta) */
export const ESPERA_CAIS_MS = 15_000;
/** as linhas de cima que a tabela mostra antes de "Ver todas": 8 de 900 px em diante, 6 abaixo (UX-CA-3; PROPOSTO, SEM FONTE) */
export const LINHAS_LADO = 8, LINHAS_FOLHA = 6;
/** o marco do Tamer que abre o cais quando o build nao diz outro: o 10, o primeiro Mega (MMO-13) */
export const MARCO_DO_CAIS_PADRAO = 10;
/** os estagios das tabelas, na ordem (MMO-9): os das faixas que valem ponto */
export const ESTAGIOS: readonly string[] = Object.keys(PONTOS_FAIXA);

export interface AmbienteCais {
  /** o endereco do servidor, sem a barra do fim */
  api: string;
  buscar: (url: string, init?: RequestInit) => Promise<Response>;
  agora: () => number;
}

/** uma linha da tabela, como o servidor a entrega */
export interface Linha { posicao: number; apelido: string; pontos: number; rivaisVencidos: number; lutasUsadas: number; voce: boolean }
export interface Semanas { atual: string; fechaEm: number; congelaEm: number; fechadas: { semana: string; publicadoEm: number }[] }
export interface Tabelas { semana: string; estado: "aberta" | "fechada"; congelaEm: number; estagios: Record<string, Linha[]>; total: Record<string, number> }
export type Segredo =
  | { tipo: "buscando" }
  | { tipo: "sem_resposta" }
  /** a semana nao teve luta ranqueada: nao ha segredo */
  | { tipo: "sem_segredo" }
  | { tipo: "pronto"; segredo: string; publicadoEm: number };
/** o que o corpo do cais mostra */
export type Passo = "buscando" | "sem_resposta" | "sem_conta" | "pronto";

export interface EstadoCais {
  /** null: o cais ainda nao foi aberto */
  passo: Passo | null;
  semanas: Semanas | null;
  /** a semana escolhida (a segunda-feira que a abre, AAAA-MM-DD) */
  semana: string | null;
  tabelas: Tabelas | null;
  estagio: string;
  /** "Ver todas" aberta */
  todas: boolean;
  /** "Conferir a semana" aberta: o segredo da semana escolhida; null fechada */
  segredo: Segredo | null;
}

export const CA: EstadoCais = { passo: null, semanas: null, semana: null, tabelas: null, estagio: ESTAGIOS[0], todas: false, segredo: null };
let amb: AmbienteCais | null = null, revisao = 0, pedido = 0;
const ouvintes = new Set<() => void>();
const avisar = (): void => { revisao++; for (const f of ouvintes) f(); };
function zerar(): void { CA.passo = null; CA.semanas = null; CA.semana = null; CA.tabelas = null; CA.estagio = ESTAGIOS[0]; CA.todas = false; CA.segredo = null; pedido++; }

export function ligarCais(a: AmbienteCais): void { amb = { ...a, api: a.api.replace(/\/+$/, "") }; zerar(); avisar(); }
export function desligarCais(): void { amb = null; zerar(); avisar(); }
/** o relogio do ambiente do cais (as recompensas o leem: o titulo no perfil por uma semana) */
export const agoraDoCais = (): number => exigir().agora();
export const caisLigado = (): boolean => amb !== null;
export const ouvirCais = (f: () => void): (() => void) => { ouvintes.add(f); return () => { ouvintes.delete(f); }; };
export const revisaoCais = (): number => revisao;

/** o marco que abre o cais, do texto do build (VITE_DIGILAB_MARCO_RANQUEADA, o mesmo numero do DIGILAB_MARCO_RANQUEADA do servidor): vazio
    da o 10; outra coisa que nao um inteiro de 1 a 10 falha alto */
export function marcoDoCais(texto: string): number {
  if (texto === "") return MARCO_DO_CAIS_PADRAO;
  const n = Number(texto);
  if (!Number.isInteger(n) || n < 1 || n > MARCO_DO_CAIS_PADRAO) throw new Error(`VITE_DIGILAB_MARCO_RANQUEADA não é um marco de 1 a ${MARCO_DO_CAIS_PADRAO}: "${texto}"`);
  return n;
}

/* ------------------------------------------------------------ as contas da tela (puras) */
const MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const DIA_MS = 86_400_000;
function diaDaSemana(semana: string, mais: number): { dia: number; mes: number } {
  const t = Date.parse(semana + "T00:00:00Z");
  if (!Number.isFinite(t)) throw new Error(`a semana não é uma data AAAA-MM-DD: "${semana}"`);
  const d = new Date(t + mais * DIA_MS);
  return { dia: d.getUTCDate(), mes: d.getUTCMonth() };
}
/** "16 a 22 de novembro"; virando o mes, "30 de novembro a 6 de dezembro" */
export function textoDaSemana(semana: string): string {
  const a = diaDaSemana(semana, 0), b = diaDaSemana(semana, 6);
  return a.mes === b.mes ? `${a.dia} a ${b.dia} de ${MESES[b.mes]}` : `${a.dia} de ${MESES[a.mes]} a ${b.dia} de ${MESES[b.mes]}`;
}
/** quanto falta, em duas unidades: "2 d 4 h", "3 h 12 min", "8 min"; "" quando ja passou */
export function faltaAte(ate: number, agora: number): string {
  const min = Math.ceil((ate - agora) / 60_000);
  if (min <= 0) return "";
  const d = Math.floor(min / 1440), h = Math.floor((min % 1440) / 60), m = min % 60;
  return d > 0 ? `${d} d ${h} h` : h > 0 ? `${h} h ${m} min` : `${m} min`;
}
/** a hora de Brasilia de um instante: "16/11, à 1h" ou "16/11, às 13h05" */
export function horaDeBrasilia(t: number): string {
  const d = new Date(t + FUSO_BRASILIA_MS), h = d.getUTCHours(), m = d.getUTCMinutes();
  return `${String(d.getUTCDate()).padStart(2, "0")}/${String(d.getUTCMonth() + 1).padStart(2, "0")}, ${h === 1 ? "à" : "às"} ${h}h${m ? String(m).padStart(2, "0") : ""}`;
}
/** o estado da semana em texto. "fechando" e so da tela (entre o fim da semana e o congelamento, a folga do servidor): a resposta ainda diz
    "aberta" */
export type EstadoDaSemana = "aberta" | "fechando" | "fechada";
export function estadoDaSemana(s: Semanas, semana: string, agora: number): EstadoDaSemana {
  if (s.fechadas.some(f => f.semana === semana)) return "fechada";
  if (semana !== s.atual) return "fechando";   /* a semana de antes, ainda dentro da folga */
  return agora >= s.fechaEm ? "fechando" : "aberta";
}
/** as semanas por onde as setas andam, da mais antiga a de agora. A de antes da atual entra enquanto ainda nao congelou */
export function semanasDoCais(s: Semanas, agora: number): string[] {
  const antes = new Date(Date.parse(s.atual + "T00:00:00Z") - 7 * DIA_MS).toISOString().slice(0, 10);
  const lista = s.fechadas.map(f => f.semana).sort();
  if (!lista.includes(antes) && agora < s.congelaEm - 7 * DIA_MS) lista.push(antes);
  return [...lista, s.atual];
}
/** as linhas que a tabela mostra: as `n` de cima e, se quem olha esta abaixo delas, a dele depois do salto (UX-CA-3) */
export function linhasDaTela(linhas: readonly Linha[], n: number, todas: boolean): { topo: Linha[]; voce: Linha | null } {
  if (todas) return { topo: [...linhas], voce: null };
  const topo = linhas.slice(0, n), eu = linhas.find(l => l.voce) ?? null;
  return { topo, voce: eu && !topo.includes(eu) ? eu : null };
}

/* ------------------------------------------------------------ o servidor */
/** a rede caiu, o servidor esta fora ou a espera acabou (a tela diz "nao veio", sem erro alto) */
export class SemResposta extends Error {}
function exigir(): AmbienteCais { if (!amb) throw new Error("o cais está desligado"); return amb; }
export async function chamar(caminho: string): Promise<{ status: number; corpo: unknown }> {
  const a = exigir(), controle = new AbortController(), relogio = setTimeout(() => controle.abort(), ESPERA_CAIS_MS);
  try {
    const r = await a.buscar(a.api + caminho, { method: "GET", credentials: "include", signal: controle.signal });
    const texto = await r.text();
    let dados: unknown = null;
    if (texto) { try { dados = JSON.parse(texto); } catch { throw new Error(`o servidor respondeu ${r.status} sem JSON em ${caminho}`); } }
    return { status: r.status, corpo: dados };
  } catch (err) {
    /* a rede caiu, o servidor esta fora ou a espera acabou: nada de erro alto, a tela diz "a tabela nao veio" */
    if (err instanceof TypeError || (err instanceof Error && err.name === "AbortError")) throw new SemResposta();
    throw err;
  } finally { clearTimeout(relogio); }
}
export const objeto = (v: unknown): Record<string, unknown> => {
  if (typeof v !== "object" || v === null || Array.isArray(v)) throw new Error(`o servidor respondeu algo que o jogo não entende: ${JSON.stringify(v)}`);
  return v as Record<string, unknown>;
};
export const texto = (v: unknown, campo: string): string => { if (typeof v !== "string" || !v) throw new Error(`a resposta do servidor veio sem "${campo}"`); return v; };
export const hora = (v: unknown, campo: string): number => { const t = Date.parse(texto(v, campo)); if (!Number.isFinite(t)) throw new Error(`"${campo}" não é uma data: ${String(v)}`); return t; };
export const inteiro = (v: unknown, campo: string): number => { if (typeof v !== "number" || !Number.isInteger(v) || v < 0) throw new Error(`"${campo}" não é um inteiro: ${String(v)}`); return v; };
export const numero = (v: unknown, campo: string): number => { if (typeof v !== "number" || !Number.isFinite(v) || v < 0) throw new Error(`"${campo}" não é um número: ${String(v)}`); return v; };

async function lerSemanas(): Promise<Semanas> {
  const r = await chamar("/semanas");
  if (r.status !== 200) throw new Error(`as semanas não vieram (${r.status})`);
  const d = objeto(r.corpo);
  if (!Array.isArray(d.fechadas)) throw new Error('a resposta do servidor veio sem "fechadas"');
  return { atual: texto(d.atual, "atual"), fechaEm: hora(d.fecha_em, "fecha_em"), congelaEm: hora(d.congela_em, "congela_em"),
    fechadas: d.fechadas.map(x => { const o = objeto(x); return { semana: texto(o.semana, "semana"), publicadoEm: hora(o.publicado_em, "publicado_em") }; }) };
}
/** as tabelas de uma semana; null sem a sessao (401) */
async function lerTabelas(semana: string): Promise<Tabelas | null> {
  const r = await chamar(`/semanas/${semana}/tabelas`);
  if (r.status === 401) return null;
  if (r.status !== 200) throw new Error(`as tabelas da semana ${semana} não vieram (${r.status})`);
  const d = objeto(r.corpo), e = objeto(d.estagios), t = objeto(d.total);
  if (d.estado !== "aberta" && d.estado !== "fechada") throw new Error(`estado de semana desconhecido: ${String(d.estado)}`);
  const estagios: Record<string, Linha[]> = {}, total: Record<string, number> = {};
  for (const nome of ESTAGIOS) {
    const linhas = e[nome];
    if (!Array.isArray(linhas)) throw new Error(`a tabela ${nome} não veio`);
    estagios[nome] = linhas.map(x => {
      const o = objeto(x);
      return { posicao: inteiro(o.posicao, "posicao"), apelido: texto(o.apelido, "apelido"), pontos: numero(o.pontos, "pontos"),
        rivaisVencidos: inteiro(o.rivais_vencidos, "rivais_vencidos"), lutasUsadas: inteiro(o.lutas_usadas, "lutas_usadas"), voce: o.voce === true };
    });
    total[nome] = inteiro(t[nome], "total");
  }
  return { semana: texto(d.semana, "semana"), estado: d.estado, congelaEm: hora(d.congela_em, "congela_em"), estagios, total };
}

/** busca a semana escolhida (ou a de agora) e as tabelas dela. Uma busca mais nova ganha da mais antiga */
async function buscar(semana: string | null): Promise<void> {
  const meu = ++pedido;
  CA.passo = "buscando"; CA.tabelas = null; CA.todas = false; CA.segredo = null; avisar();
  try {
    const s = await lerSemanas();
    if (meu !== pedido) return;
    const lista = semanasDoCais(s, exigir().agora()), alvo = semana !== null && lista.includes(semana) ? semana : s.atual;
    CA.semanas = s; CA.semana = alvo; avisar();
    const t = await lerTabelas(alvo);
    if (meu !== pedido) return;
    CA.tabelas = t; CA.passo = t === null ? "sem_conta" : "pronto";
  } catch (err) {
    if (meu !== pedido) return;
    if (!(err instanceof SemResposta)) console.error(err);   /* a resposta que o jogo nao entende fica a vista no console */
    CA.passo = "sem_resposta";
  }
  avisar();
}

/** abre o cais na semana de agora, na tabela do estagio do pet (se ele tem tabela) */
export function abrirCais(estagioDoPet: string | null): Promise<void> {
  CA.estagio = estagioDoPet !== null && ESTAGIOS.includes(estagioDoPet) ? estagioDoPet : ESTAGIOS[0];
  return buscar(null);
}
/** "Atualizar" e "Tentar de novo": a mesma semana, de novo */
export const atualizarCais = (): Promise<void> => buscar(CA.semana);
/** as setas: a semana de antes (-1) ou a seguinte (+1); fora da lista, nada */
export function andarSemana(passo: -1 | 1): Promise<void> {
  if (!CA.semanas || CA.semana === null) return Promise.resolve();
  const lista = semanasDoCais(CA.semanas, exigir().agora()), alvo = lista[lista.indexOf(CA.semana) + passo];
  return alvo === undefined ? Promise.resolve() : buscar(alvo);
}
/** ha semana para a seta levar */
export function temSemana(passo: -1 | 1): boolean {
  if (!amb || !CA.semanas || CA.semana === null) return false;
  const lista = semanasDoCais(CA.semanas, amb.agora());
  return lista[lista.indexOf(CA.semana) + passo] !== undefined;
}
export function escolherEstagio(e: string): void {
  if (!ESTAGIOS.includes(e)) throw new Error(`estágio sem tabela: ${e}`);
  CA.estagio = e; CA.todas = false; avisar();
}
export function verTodas(): void { CA.todas = true; avisar(); }

/** "Conferir a semana": busca o segredo publicado da semana escolhida (a rota nao pede a sessao) */
export async function abrirSegredo(): Promise<void> {
  const semana = CA.semana;
  if (semana === null) throw new Error("o cais não tem semana escolhida");
  const meu = pedido;
  CA.segredo = { tipo: "buscando" }; avisar();
  let fim: Segredo;
  try {
    const r = await chamar(`/semanas/${semana}/segredo`);
    if (r.status === 404 && objeto(r.corpo).motivo === "sem_segredo") fim = { tipo: "sem_segredo" };
    else if (r.status !== 200) throw new Error(`o segredo da semana ${semana} não veio (${r.status})`);
    else { const d = objeto(r.corpo); fim = { tipo: "pronto", segredo: texto(d.segredo, "segredo"), publicadoEm: hora(d.publicado_em, "publicado_em") }; }
  } catch (err) {
    if (!(err instanceof SemResposta)) console.error(err);
    fim = { tipo: "sem_resposta" };
  }
  if (meu !== pedido || CA.segredo === null) return;   /* trocou de semana ou voltou a tabela enquanto buscava */
  CA.segredo = fim; avisar();
}
export function fecharSegredo(): void { CA.segredo = null; avisar(); }
