/* As recompensas e o mural no cais (MMO7, docs/PLANO_V3_MMO.md secao 7; MMO-12: o ranking paga prestigio, nao Bits): o que a conta
   ganhou (GET /premios: o titulo da semana, os selos "Top do dia", os enfeites da temporada, os recordes e o Respeito conferido) e o mural
   (GET /mural: os recordes de todos os tempos da Torre, da Fabrica e do Salao e os titulos das semanas), contra as rotas de
   servidor_web/src/premios/premios.ts. Sem React e sem DOM, como o cais.ts, de quem usa o ambiente e as chamadas.

   A prancha do mural e dos selos no perfil esta pendente com o Matheus: a tela (telas/cais/TelaCais.tsx) e so o minimo, nas pecas do cais.

   O que vem daqui so se le: os Bits, o motor, o registro e o save nao mudam. As tacas da temporada vao para a ilha pelo TACAS_DA_CONTA
   (trancas.ts), so vista. */
import { definirTacas } from "../trancas.ts";
import { caisLigado, chamar, hora, inteiro, objeto, SemResposta, texto } from "./cais.ts";

/** as instalacoes do mural, na ordem da tela, com o nome do jogo */
export const INSTALACOES_MURAL = [["torre", "Torre de Batalha"], ["fabrica", "Fábrica"], ["salao", "Salão"]] as const;
export type InstMural = typeof INSTALACOES_MURAL[number][0];

export interface Titulo { semana: string; numero: number; estagio: string; texto: string }
export interface Premios {
  /** o titulo da semana que ainda esta no perfil (uma semana depois do congelamento) */
  tituloAtual: (Titulo & { noPerfilAte: number })[];
  titulos: Titulo[];
  selos: { dia: string; posicao: number }[];
  enfeites: { temporada: number; de: string; ate: string }[];
  recordes: Record<InstMural, number | null>;
  respeito: number;
}
export interface LinhaMural { posicao: number; apelido: string; valor: number; voce: boolean }
export interface Mural { recordes: Record<InstMural, LinhaMural[]>; total: Record<InstMural, number>; titulos: (Titulo & { apelido: string; voce: boolean })[] }
export type EstadoMural =
  | { passo: "buscando" } | { passo: "sem_resposta" } | { passo: "sem_conta" }
  | { passo: "pronto"; premios: Premios; mural: Mural };

let estado: EstadoMural | null = null, revisao = 0, pedido = 0;
const ouvintes = new Set<() => void>();
const avisar = (): void => { revisao++; for (const f of ouvintes) f(); };
export const ouvirMural = (f: () => void): (() => void) => { ouvintes.add(f); return () => { ouvintes.delete(f); }; };
export const revisaoMural = (): number => revisao;
/** null: o mural esta fechado */
export const estadoMural = (): EstadoMural | null => estado;

const lista = (v: unknown, campo: string): unknown[] => { if (!Array.isArray(v)) throw new Error(`a resposta do servidor veio sem "${campo}"`); return v; };
const titulo = (o: Record<string, unknown>): Titulo =>
  ({ semana: texto(o.semana, "semana"), numero: inteiro(o.numero, "numero"), estagio: texto(o.estagio, "estagio"), texto: texto(o.texto, "texto") });

/** le a resposta do GET /premios */
export function lerPremios(corpo: unknown): Premios {
  const d = objeto(corpo), r = objeto(d.recordes), sel = objeto(d.selos), resp = objeto(d.respeito);
  const recordes = Object.fromEntries(INSTALACOES_MURAL.map(([id]) => {
    const x = r[id];
    return [id, x === null ? null : inteiro(objeto(x).valor, "valor")];
  })) as Record<InstMural, number | null>;
  return {
    tituloAtual: lista(d.titulo_atual, "titulo_atual").map(x => { const o = objeto(x); return { ...titulo(o), noPerfilAte: hora(o.no_perfil_ate, "no_perfil_ate") }; }),
    titulos: lista(d.titulos, "titulos").map(x => titulo(objeto(x))),
    selos: lista(sel.lista, "selos").map(x => { const o = objeto(x); return { dia: texto(o.dia, "dia"), posicao: inteiro(o.posicao, "posicao") }; }),
    enfeites: lista(d.enfeites, "enfeites").map(x => { const o = objeto(x); return { temporada: inteiro(o.temporada, "temporada"), de: texto(o.de, "de"), ate: texto(o.ate, "ate") }; }),
    recordes, respeito: inteiro(resp.conferido, "respeito"),
  };
}
/** le a resposta do GET /mural */
export function lerMural(corpo: unknown): Mural {
  const d = objeto(corpo), r = objeto(d.recordes), t = objeto(d.total);
  const recordes = {} as Record<InstMural, LinhaMural[]>, total = {} as Record<InstMural, number>;
  for (const [id] of INSTALACOES_MURAL) {
    recordes[id] = lista(r[id], id).map(x => {
      const o = objeto(x);
      return { posicao: inteiro(o.posicao, "posicao"), apelido: texto(o.apelido, "apelido"), valor: inteiro(o.valor, "valor"), voce: o.voce === true };
    });
    total[id] = inteiro(t[id], "total");
  }
  const titulos = lista(d.titulos, "titulos").map(x => { const o = objeto(x); return { ...titulo(o), apelido: texto(o.apelido, "apelido"), voce: o.voce === true }; });
  return { recordes, total, titulos };
}

/** busca os premios da conta (e poe as tacas na ilha). null sem a sessao (401) */
async function buscarPremios(): Promise<Premios | null> {
  const r = await chamar("/premios");
  if (r.status === 401) return null;
  if (r.status !== 200) throw new Error(`os prêmios não vieram (${r.status})`);
  const p = lerPremios(r.corpo);
  definirTacas(p.enfeites.map(e => e.temporada));
  return p;
}

/** "Mural e prêmios": abre e busca as duas rotas. Uma busca mais nova ganha da mais antiga */
export async function abrirMural(): Promise<void> {
  const meu = ++pedido;
  estado = { passo: "buscando" }; avisar();
  let fim: EstadoMural;
  try {
    const premios = await buscarPremios();
    if (premios === null) fim = { passo: "sem_conta" };
    else {
      const r = await chamar("/mural");
      if (r.status === 401) fim = { passo: "sem_conta" };
      else if (r.status !== 200) throw new Error(`o mural não veio (${r.status})`);
      else fim = { passo: "pronto", premios, mural: lerMural(r.corpo) };
    }
  } catch (err) {
    if (!(err instanceof SemResposta)) console.error(err);   /* a resposta que o jogo nao entende fica a vista no console */
    fim = { passo: "sem_resposta" };
  }
  if (meu !== pedido || estado === null) return;   /* fechou ou abriu de novo enquanto buscava */
  estado = fim; avisar();
}
export function fecharMural(): void { estado = null; pedido++; avisar(); }

/** so as tacas da ilha, sem abrir o mural (na abertura do cais e uma vez no comeco do jogo, com o cais ligado). Sem conta ou sem resposta,
    a ilha fica como esta */
export async function buscarTacas(): Promise<void> {
  if (!caisLigado()) return;
  try { await buscarPremios(); }
  catch (err) { if (!(err instanceof SemResposta)) console.error(err); }
}

/** "16/11" de um dia AAAA-MM-DD */
export const diaCurto = (dia: string): string => `${dia.slice(8, 10)}/${dia.slice(5, 7)}`;
