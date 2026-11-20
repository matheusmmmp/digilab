/* O protocolo do save na nuvem (CN3; docs/PLANO_V3_CONTA.md, seção 5), dividido entre o jogo (src/nuvem/cliente.ts) e o servidor
   (servidor_web/src/nuvem/). Sem React e sem DOM: o servidor importa este arquivo no Node (a regra do servidor_web/CLAUDE.md).

   O que vai para a nuvem é o PACOTE da conta: o save do pet do jogador ({semente, log, versao}, ou o dos dois pets com grupo e foco) e as
   outras chaves do navegador que a CN0 mandou para a nuvem (docs/RESULTADO_V3_CONTA_CN0.md, seção 2; a tabela 5.4 do plano), cada uma como
   o texto que o jogo gravou. O save sincroniza por EVENTOS (5.1): o aparelho manda só os eventos depois da posição que a nuvem confirmou,
   com o hash do registro até ali. As outras chaves vão inteiras, só quando mudam (o hash delas).

   O hash do registro até a posição n é o SHA-256 de JSON.stringify(log.slice(0, n)): o mesmo do pedido da semente ranqueada (MMO4,
   src/ranking/pedido.ts) e do hashesAte do servidor. Como o SHA-256 corre o texto em ordem, ele é encadeado: o hash até n já carrega todos
   os eventos antes de n. */
import { CHAVE } from "../chave.ts";

/** a versão do protocolo: um aparelho com outra recebe "atualize o jogo" (5.5, MMO-14) */
export const PROTOCOLO_NUVEM = 1;
/** a vez expira sozinha depois deste tempo sem sinal do aparelho que a tem (5.2: PROPOSTO, 10 min) */
export const VEZ_EXPIRA_MS = 10 * 60_000;
/** as cópias ficam este tempo (CN-5: 30 dias) */
export const COPIAS_DIAS = 30;

/** as chaves do navegador que sobem junto do save (CN0, seção 2: "nuvem"). O `-anterior` não está aqui: ele sobe NO LUGAR do save
    (é o pet do jogador enquanto um pet dos Cenários ocupa a CHAVE; D-CONTA-34) */
export const CHAVES_NUVEM: readonly string[] = [
  "-guardados", "-geracoes", "-tamer", "-descarte", "-nivel", "-conclusao-liga", "-mitologia-ouvidas", "-descartados",
].map(s => CHAVE + s);
/** o gosto da TV por pet (D-CONTA-36): uma chave por semente */
export const PREFIXO_GOSTO_TV = "digilab-gosto-visual-p0:";
export const CHAVE_ANTERIOR = CHAVE + "-anterior";
export const ehChaveNuvem = (k: string): boolean => CHAVES_NUVEM.includes(k) || /^digilab-gosto-visual-p0:\d+$/.test(k);

/** um evento do registro (do pet ou do grupo): uma lista, como o motor grava */
export type EventoNuvem = unknown[];
export interface SaveNuvem { semente: number; versao: number; log: EventoNuvem[]; grupo?: true; foco?: string }
export interface Pacote { save: SaveNuvem; extras: Record<string, string> }

/** o pet de um save, para saber se dois saves são o mesmo pet (o mesmo ovo): a semente, a versão e o grupo */
export const idDoSave = (s: Pick<SaveNuvem, "semente" | "versao" | "grupo">): string => `${s.semente}:${s.versao}:${s.grupo ? 1 : 0}`;
/** a posição que a nuvem confirmou: o pet, quantos eventos e o hash do registro até ali */
export interface Base { id: string; eventos: number; hash: string }

/** o pedido de sincronização (POST /nuvem/sync) */
export interface PedidoSync {
  protocolo: number;
  /** a última posição que a nuvem confirmou a este aparelho; null se ainda nenhuma */
  base: Base | null;
  /** o pet do save deste aparelho agora */
  id: string;
  foco?: string;
  /** os eventos depois da base (o mesmo pet da base) */
  novos: EventoNuvem[];
  /** o save inteiro, quando os novos não bastam: o pet trocou (ovo novo, pet guardado) ou a nuvem pediu */
  completo?: SaveNuvem;
  /** as outras chaves, só quando mudaram desde o extras_hash confirmado */
  extras?: Record<string, string>;
  extras_hash: string | null;
}

/** a vez vista por um aparelho */
export interface VezVista { minha: boolean; aparelho: string | null; desde: number | null; ate: number | null }
/** um lado de uma divergência, para a tela "Duas histórias" */
export interface LadoHistoria { aparelho: string; tick: number; forma: string; eventos_novos: number; ultimo: string | null }
export interface DivergenciaVista { id: string; criada_em: number; nuvem: LadoHistoria; outra: LadoHistoria }

export type Situacao =
  | "ok"          // a nuvem tem o que este aparelho tem
  | "atras"       // a nuvem anda à frente: os novos (ou o save inteiro) vêm na resposta
  | "sem_pet"     // a conta ainda não tem pet na nuvem (a tela "Levar o pet para a conta")
  | "outro"       // outro aparelho tem a vez: este fica só para ver
  | "divergiu"    // duas histórias: a escolha está pendente (o pet fica só para ver nos dois aparelhos, UX-NV-4)
  | "atualize";   // o protocolo ou a versão do pet é de outro jogo (5.5)

export interface RespostaSync {
  situacao: Situacao;
  /** a posição da nuvem depois deste pedido */
  base: Base | null;
  foco?: string | null;
  vez: VezVista;
  extras_hash: string | null;
  /** com "atras": os eventos depois da base deste aparelho, ou o save inteiro quando a base não é um começo do registro da nuvem */
  novos?: EventoNuvem[];
  completo?: SaveNuvem;
  /** as outras chaves da nuvem, quando o extras_hash deste aparelho não bate */
  extras?: Record<string, string>;
  divergencia?: DivergenciaVista | null;
  /** o resumo do pet da nuvem (a tela) */
  forma?: string;
  tick?: number;
  versao?: number;
  /** com "atualize": por quê */
  detalhe?: string;
}

/* O registro quase só cresce: o avanço do tempo junta-se ao "t" do fim quando ele termina no tick de agora (o _registrarAvanco do motor e o
   avancar do GrupoDoJogo: o valor do "t" do fim aumenta no lugar). Por isso a posição que a nuvem confirma é a PONTA FIRME: o registro sem
   o "t" do fim, que ainda pode crescer. E "a é um começo de b" aceita que o "t" do fim de a tenha crescido em b (o mesmo tick, o mesmo pet,
   mais minutos). Sem isso, todo avanço do tempo pareceria uma divergência (D-CONTA-182). */
const ehT = (e: EventoNuvem | undefined): boolean => e !== undefined && e[1] === "t";
/** quantos eventos do registro já não mudam: todos, menos o "t" do fim */
export const pontaFirme = (log: readonly EventoNuvem[]): number => (ehT(log[log.length - 1]) ? log.length - 1 : log.length);
/** `a` é um começo de `b` (os dois já iguais antes de `de`), contando o "t" do fim de `a` que cresceu em `b` */
export function ehComeco(a: readonly EventoNuvem[], b: readonly EventoNuvem[], de = 0): boolean {
  if (a.length > b.length) return false;
  for (let i = de; i < a.length; i++) {
    const x = a[i]!, y = b[i]!;
    if (JSON.stringify(x) === JSON.stringify(y)) continue;
    const cresceu = i === a.length - 1 && ehT(x) && ehT(y) && x[0] === y[0] && (x[3] ?? null) === (y[3] ?? null) && x.length === y.length
      && typeof x[2] === "number" && typeof y[2] === "number" && y[2] > x[2];
    if (!cresceu) return false;
  }
  return true;
}

/** o hash das outras chaves: o SHA-256 do JSON delas em ordem de chave (o mesmo texto no jogo e no servidor) */
export const textoExtras = (x: Record<string, string>): string => JSON.stringify(Object.keys(x).sort().map(k => [k, x[k]]));
