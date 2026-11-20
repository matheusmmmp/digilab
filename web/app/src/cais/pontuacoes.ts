/* As duas pontuacoes no jogo (MMO8; docs/PLANO_V3_MMO.md secao 8; MMO-15 e MMO-16; a prancha docs/pranchas/ux-reset/, UX-RS-1 a 7
   APROVADAS em 2026-11-19): o Respeito conferido da conta (GET /premios, o campo respeito), o ranking dos Tamers (GET /tamers) e o maximo
   historico dos Digimon (GET /digimons), contra as rotas de servidor_web/src/premios/rankings.ts. Sem React e sem DOM, como o premios.ts,
   de quem usa o ambiente e as chamadas (cais.ts).

   O que vem daqui so se le: os Bits, o motor, o registro e o save nao mudam. O ranking conta so o que o servidor viu; o Respeito do jogo
   (respeitoLocal, pontos.ts) fica ao lado, menor (UX-RS-5). */
import { chamar, inteiro, numero, objeto, SemResposta, texto } from "./cais.ts";

/** o Respeito conferido da conta, por feito (o campo respeito do GET /premios) */
export interface RespeitoConferido {
  conferido: number; lideres: number; liga: number; resets: number; titulos: number; selos: number;
  contagem: { lideres: number; liga: boolean; resets: number; titulos: number; selos: number };
  /** o nivel do Tamer pelo Respeito; null sem o marco 10 conferido (o servidor nao ve os marcos 1 a 9) */
  nivel: number | null;
  /** "Tamer Lendário" a partir de 10 000; null antes */
  titulo: string | null;
}
export interface LinhaTamer { posicao: number; apelido: string; respeito: number; nivel: number | null; titulo: string | null; voce: boolean }
export interface LinhaDigimon {
  posicao: number; apelido: string; forma: string; estagio: string; pontos: number; aposentado: boolean; voce: boolean;
  /** a semente do pet, so nas linhas da conta */
  pet: number | null;
}
export interface Ranking<L> { linhas: L[]; total: number }

const lista = (v: unknown, campo: string): unknown[] => { if (!Array.isArray(v)) throw new Error(`a resposta do servidor veio sem "${campo}"`); return v; };
const ouNulo = <T,>(v: unknown, f: (x: unknown) => T): T | null => (v === null || v === undefined ? null : f(v));
const logico = (v: unknown, campo: string): boolean => { if (typeof v !== "boolean") throw new Error(`"${campo}" não é sim ou não: ${String(v)}`); return v; };

/** le o campo respeito do GET /premios */
export function lerRespeito(v: unknown): RespeitoConferido {
  const o = objeto(v), c = objeto(o.contagem);
  return {
    conferido: inteiro(o.conferido, "conferido"), lideres: inteiro(o.lideres, "lideres"), liga: inteiro(o.liga, "liga"), resets: inteiro(o.resets, "resets"),
    titulos: inteiro(o.titulos, "titulos"), selos: inteiro(o.selos, "selos"),
    contagem: { lideres: inteiro(c.lideres, "lideres"), liga: logico(c.liga, "liga"), resets: inteiro(c.resets, "resets"), titulos: inteiro(c.titulos, "titulos"), selos: inteiro(c.selos, "selos") },
    nivel: ouNulo(o.nivel, x => inteiro(x, "nivel")), titulo: ouNulo(o.titulo, x => texto(x, "titulo")),
  };
}
/** le o GET /tamers */
export function lerTamers(corpo: unknown): Ranking<LinhaTamer> {
  const d = objeto(corpo);
  return {
    linhas: lista(d.linhas, "linhas").map(x => {
      const o = objeto(x);
      return { posicao: inteiro(o.posicao, "posicao"), apelido: texto(o.apelido, "apelido"), respeito: inteiro(o.respeito, "respeito"),
        nivel: ouNulo(o.nivel, y => inteiro(y, "nivel")), titulo: ouNulo(o.titulo, y => texto(y, "titulo")), voce: o.voce === true };
    }),
    total: inteiro(d.total, "total"),
  };
}
/** le o GET /digimons */
export function lerDigimons(corpo: unknown): Ranking<LinhaDigimon> {
  const d = objeto(corpo);
  return {
    linhas: lista(d.linhas, "linhas").map(x => {
      const o = objeto(x);
      return { posicao: inteiro(o.posicao, "posicao"), apelido: texto(o.apelido, "apelido"), forma: texto(o.forma, "forma"), estagio: texto(o.estagio, "estagio"),
        pontos: numero(o.pontos, "pontos"), aposentado: logico(o.aposentado, "aposentado"), voce: o.voce === true, pet: ouNulo(o.pet, y => inteiro(y, "pet")) };
    }),
    total: inteiro(d.total, "total"),
  };
}

/** uma rota de leitura que pede a sessao: null sem ela (401) */
async function ler<T>(caminho: string, f: (corpo: unknown) => T): Promise<T | null> {
  const r = await chamar(caminho);
  if (r.status === 401) return null;
  if (r.status !== 200) throw new Error(`${caminho} não veio (${r.status})`);
  return f(r.corpo);
}
export const buscarRespeito = (): Promise<RespeitoConferido | null> => ler("/premios", c => lerRespeito(objeto(c).respeito));
export const buscarTamers = (): Promise<Ranking<LinhaTamer> | null> => ler("/tamers", lerTamers);
export const buscarDigimons = (): Promise<Ranking<LinhaDigimon> | null> => ler("/digimons", lerDigimons);

/** as linhas da conta no ranking dos Digimon: o melhor pet (o de mais pontos) e a linha de um pet pela semente */
export const melhorDigimon = (r: Ranking<LinhaDigimon>): LinhaDigimon | null => r.linhas.filter(l => l.voce).sort((a, b) => b.pontos - a.pontos || a.posicao - b.posicao)[0] ?? null;
export const linhaDoPet = (r: Ranking<LinhaDigimon>, pet: number): LinhaDigimon | null => r.linhas.find(l => l.voce && l.pet === pet) ?? null;

/* ------------------------------------------------------------ os estados das telas (o perfil e as abas do cais) */
export type Estado<T> = { passo: "buscando" } | { passo: "sem_resposta" } | { passo: "sem_conta" } | { passo: "pronto"; dados: T };

let revisao = 0;
const ouvintes = new Set<() => void>();
const avisar = (): void => { revisao++; for (const f of ouvintes) f(); };
export const ouvirPontuacoes = (f: () => void): (() => void) => { ouvintes.add(f); return () => { ouvintes.delete(f); }; };
export const revisaoPontuacoes = (): number => revisao;

/** um estado que busca de novo a cada abertura; a busca mais nova ganha da mais antiga */
function estadoDe<T>(buscar: () => Promise<T | null>) {
  let e: Estado<T> | null = null, pedido = 0;
  return {
    atual: (): Estado<T> | null => e,
    async abrir(): Promise<void> {
      const meu = ++pedido;
      e = { passo: "buscando" }; avisar();
      let fim: Estado<T>;
      try { const d = await buscar(); fim = d === null ? { passo: "sem_conta" } : { passo: "pronto", dados: d }; }
      catch (err) {
        if (!(err instanceof SemResposta)) console.error(err);   /* a resposta que o jogo nao entende fica a vista no console */
        fim = { passo: "sem_resposta" };
      }
      if (meu !== pedido || e === null) return;
      e = fim; avisar();
    },
    fechar(): void { e = null; pedido++; avisar(); },
  };
}

/** o perfil: o Respeito conferido e o ranking dos Digimon (o melhor pet da conta e o ativo) */
export interface DadosPerfil { respeito: RespeitoConferido; digimons: Ranking<LinhaDigimon> }
export const perfil = estadoDe<DadosPerfil>(async () => {
  const respeito = await buscarRespeito();
  if (respeito === null) return null;
  const digimons = await buscarDigimons();
  return digimons === null ? null : { respeito, digimons };
});
/** as abas Tamers e Digimon do cais */
export const abaTamers = estadoDe(buscarTamers);
export const abaDigimons = estadoDe(buscarDigimons);

/** "2 340": o numero com o espaco dos milhares, como na prancha */
export const milhares = (n: number): string => Math.round(n).toLocaleString("pt-BR").replace(/\./g, " ");
