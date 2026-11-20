/* A conferência de um envio (MMO3, docs/PLANO_V3_MMO.md seção 3; MMO-5): o servidor refaz no Node o registro do pet com o motor do jogo
   (web/app/motor, o mesmo código, sem DOM), confere o marco do nível 10 no registro do Tamer (marcoConfere, MMO2) e calcula os pontos com a
   conta pura da MMO1 (web/app/src/ranking/pontos.ts), com as sementes ranqueadas que o servidor entregou (MMO4). O cliente nunca manda a pontuação: o número é o que sai daqui.

   O envio: {pet: {semente, log, versao}, tamer: {versao, log}}.
     - a versão do pet tem de ser uma das que o motor abre (VERSOES_PET; o pet de teste do laboratório não se envia);
     - a do Tamer, a de hoje (VERSAO_TAMER): o jogo grava sempre a de hoje, e um registro de antes vem de um cliente desatualizado
       ("atualize o jogo", MMO-14);
     - o save dos dois pets (grupo: true) ainda não se envia (D-CONTA-77).
   Um registro que não reproduz é recusado com o motivo: o motor falha alto no evento inválido, e o texto do erro vai na resposta.

   Um passe só (D-CONTA-85): o registro é refeito uma vez, pela conta da MMO1 (refazerComLutas), que refaz a luta pelo lutarPoc (confere se
   ela era possível) e o resto pelo aplicarEvento; o pet que sai dali é o mesmo do Motor.reproduzir (um teste confere a assinatura no Node).

   As sementes ranqueadas (MMO4, sementes.ts): cada semente entregue a este pet leva o hash do registro até o indice do pedido. Antes do
   replay, a conferência refaz esses hashes do registro enviado; um que não bate é o registro mudado depois do pedido (hash_nao_confere), e o
   envio inteiro é recusado. O pedido ainda à frente do registro (indice maior que ele) fica pendente, sem conferir.

   A conferência NÃO usa a assinatura do pet: ela difere entre o Chrome e o Node no último bit (MMO0). Só o que sai das lutas e do registro.

   As duas pontuações e o reset (MMO8, docs/PLANO_V3_MMO.md seções 8 e 9): o envio aceito diz também
     - o Digimon: os pontos da vida do pet (a soma das lutas ranqueadas), o maior estágio, a forma e o nível do reset refeito do registro;
     - os feitos do Tamer que este pet fez e o replay dele mostra: a 1ª medalha de cada líder (a vitória contra o líder na campanha do pet)
       e o título da Liga (o pet tem o título no Motor.liga). Uma medalha do Tamer que o pet não mostra não conta, sem recusar o envio;
     - o reset deste pet no registro do Tamer (versão 11): se o registro enviado é o do reset (o mesmo hash e o mesmo tamanho), o nível do
       reset tem de ser o que o registro dá (reset_nao_confere, senão); um registro de outro momento do pet não confere o reset (fica para o
       envio do registro final). */
import { createHash, type Hash } from "node:crypto";
import { MEDALHA_POR_ID, VERSOES_PET, nomeForma, type EventoRegistro, type Motor } from "../../../web/app/motor/index.ts";
import {
  estagioMaximo, linhasDaSemana, nivelDoReset, pontosDoDigimon, refazerComLutas, type LinhaSemana, type LutaRanqueada, type LutaSalaoVista, type NivelReset,
  type SementeEntregue,
} from "../../../web/app/src/ranking/pontos.ts";
import { marcosDoTamer } from "../../../web/app/src/marcosTamer.ts";
import { CHAVE_TAMER, lerTamer, MARCO_MEGA, marcoConfere, VERSAO_TAMER, VERSAO_TAMER_RESET, type EventoTamer, type Tamer } from "../../../web/app/src/tamer.ts";

/** as versões do registro do Tamer que o servidor confere: a 10 de hoje e a 11 do reset (MMO8, atrás da chave do jogo; D-CONTA-162) */
export const VERSOES_TAMER_CONFERIDAS: readonly number[] = [VERSAO_TAMER, VERSAO_TAMER_RESET];

/** por que um envio foi recusado (o código vai na resposta e no banco; o detalhe é o texto do erro) */
export type MotivoRecusa =
  | "versao_pet_desconhecida"    // a versão do pet não é uma das que o motor abre
  | "versao_tamer_desconhecida"  // o registro do Tamer não é da versão de hoje: atualize o jogo
  | "pet_nao_reproduz"           // o motor recusou um evento do registro do pet
  | "tamer_nao_reproduz"         // o registro do Tamer não se refaz
  | "hash_nao_confere"           // o registro até o indice de uma semente pedida não é o do pedido (mudou depois da semente)
  | "marco_nao_confere"          // o Tamer diz que este pet chegou ao Mega, e o registro do pet não mostra a evolução no tick e na forma
  | "reset_nao_confere";         // o registro enviado é o do reset deste pet, e o nível do reset não é o que o registro dá (MMO8)

/** o marco do nível 10 visto deste envio */
export type SituacaoMarco =
  | "confere"        // o marco é deste pet, e o registro dele mostra a evolução a Mega no tick e na forma do marco
  | "de_outro_pet"   // o marco é de outro pet do jogador: este envio não o confere (o envio daquele pet confere)
  | "sem_marco";     // o Tamer ainda não tem o marco 10

/** um envio já lido do corpo (a forma conferida; o conteúdo, a conferência confere) */
export interface Envio { pet: { semente: number; log: EventoRegistro[]; versao: number }; tamer: { versao: number; log: EventoTamer[] } }

export class EnvioMalformado extends Error {}

/** uma semente que o servidor entregou a este pet, com o número dela na conta e o hash do registro até o indice do pedido */
export interface EntregueComHash extends SementeEntregue { numero: number; hash: string }

/** o pet deste envio, para o máximo histórico dos Digimon (MMO8): os pontos da vida, o maior estágio, a forma e o nível do reset */
export interface DigimonVisto { pontos: number; estagio: string; forma: string; nivelReset: NivelReset }
/** os feitos do Tamer que este pet fez e o replay dele mostra (MMO8): as medalhas (os ids) e o título da Liga */
export interface FeitosVistos { medalhas: string[]; liga: boolean }
/** o reset deste pet visto neste envio (MMO8): "confere" (o registro é o do reset, e o nível bate), "outro_registro" (o Tamer tem o reset,
    e o registro enviado é de outro momento do pet) ou "sem_reset" */
export interface ResetVisto { situacao: "confere" | "outro_registro" | "sem_reset"; nivel: NivelReset | null; hash: string | null; por: string | null }

export interface Aceito {
  resultado: "aceito";
  marco10: SituacaoMarco;
  /** as duas pontuações e o reset (MMO8) */
  digimon: DigimonVisto;
  feitos: FeitosVistos;
  reset: ResetVisto;
  /** o que o mural pode contar (MMO7) */
  fronteira: FronteiraVista;
  /** os marcos que o registro do Tamer cumpre (marcosDoTamer: 5, 7, 8, 9, 10); a trava do pedido da semente os lê */
  marcosTamer: number[];
  lutas: LutaRanqueada[];
  semanas: LinhaSemana[];
  pontos: number;
  /** o tempo de cada parte, em milissegundos (o replay do pet com as lutas, o Tamer e o marco) */
  ms: { replay: number; tamer: number; total: number };
}
/** o que o mural (MMO7, servidor_web/src/premios/) pode contar deste envio: só o que a conferência refez.
    - a Torre: o recorde do pet deste envio na Torre de Batalha, das lutas que o replay do pet refez (Motor.instalacoes);
    - a Fábrica: o recorde do Tamer, da Fábrica que o replay do Tamer refaz luta por luta (Tamer.recordeFabrica);
    - o Salão: as lutas do Salão que o replay deste pet refez (com o resultado), e as tentativas do Tamer (que pet lutou em que estágio,
      com qual semente). A tentativa só conta no mural até onde cada luta dela foi vista no replay do pet que lutou (de um envio deste ou
      de outro pet da conta). */
export interface FronteiraVista {
  torre: number;
  fabrica: number;
  salao: LutaSalaoVista[];
  tentativasSalao: { n: number; lutas: { pet: number; s: number; venceu: boolean }[] }[];
}

export interface Recusado { resultado: "recusado"; motivo: MotivoRecusa; detalhe: string; ms: { total: number } }
export type Conferencia = Aceito | Recusado;

/** o hash de um registro: SHA-256 do JSON dele, como o jogo o grava (JSON.stringify do array) */
export const hashRegistro = (log: unknown): string => createHash("sha256").update(JSON.stringify(log)).digest("hex");

const msg = (err: unknown): string => err instanceof Error ? err.message : String(err);
const objeto = (x: unknown): x is Record<string, unknown> => typeof x === "object" && x !== null && !Array.isArray(x);

/** os hashes do registro até cada indice pedido: o SHA-256 de JSON.stringify(log.slice(0, i)), sem montar cada prefixo. O JSON de um
    array é "[" + os elementos separados por "," + "]", então um hash só corre o registro, e cada indice copia o estado e fecha o "]" */
export function hashesAte(log: readonly unknown[], indices: Iterable<number>): Map<number, string> {
  const quer = new Set([...indices].filter(i => i <= log.length)), out = new Map<number, string>();
  if (!quer.size) return out;
  const fim = Math.max(...quer), h: Hash = createHash("sha256").update("[");
  for (let i = 0; i <= fim; i++) {
    if (quer.has(i)) out.set(i, h.copy().update("]").digest("hex"));
    if (i < fim) h.update((i > 0 ? "," : "") + JSON.stringify(log[i]));
  }
  return out;
}

/** confere a forma do corpo do envio (sem refazer nada): o que falta ou tem o tipo errado levanta EnvioMalformado (400) */
export function lerEnvio(d: unknown): Envio {
  if (!objeto(d)) throw new EnvioMalformado("o envio é um objeto {pet, tamer}");
  const pet = d.pet, tamer = d.tamer;
  if (!objeto(pet)) throw new EnvioMalformado("'pet' é o save {semente, log, versao}");
  if (pet.grupo !== undefined) throw new EnvioMalformado("o save dos dois pets (grupo) ainda não se envia");
  if (!Number.isSafeInteger(pet.semente)) throw new EnvioMalformado("'pet.semente' é um inteiro");
  if (!Number.isSafeInteger(pet.versao)) throw new EnvioMalformado("'pet.versao' é um inteiro");
  if (!Array.isArray(pet.log) || !pet.log.every(Array.isArray)) throw new EnvioMalformado("'pet.log' é uma lista de eventos");
  if (!objeto(tamer)) throw new EnvioMalformado("'tamer' é o registro {versao, log}");
  if (!Number.isSafeInteger(tamer.versao)) throw new EnvioMalformado("'tamer.versao' é um inteiro");
  if (!Array.isArray(tamer.log) || !tamer.log.every(Array.isArray)) throw new EnvioMalformado("'tamer.log' é uma lista de eventos");
  const extra = Object.keys(d).filter(k => k !== "pet" && k !== "tamer");
  if (extra.length) throw new EnvioMalformado(`campo desconhecido no envio: ${extra.join(", ")} (a pontuação nunca vem do cliente)`);
  return { pet: { semente: pet.semente as number, log: pet.log as EventoRegistro[], versao: pet.versao as number },
    tamer: { versao: tamer.versao as number, log: tamer.log as EventoTamer[] } };
}

/** a conferência: refaz o pet e o Tamer, confere o marco e calcula os pontos. `entregues` são as sementes ranqueadas que o servidor
    entregou a este pet (a MMO4; até lá, nenhuma, e os pontos são 0) */
export function conferir(envio: Envio, entregues: readonly EntregueComHash[] = []): Conferencia {
  const t0 = performance.now();
  const recusar = (motivo: MotivoRecusa, detalhe: string): Recusado =>
    ({ resultado: "recusado", motivo, detalhe, ms: { total: +(performance.now() - t0).toFixed(2) } });
  const { pet, tamer } = envio;
  if (!VERSOES_PET.includes(pet.versao))
    return recusar("versao_pet_desconhecida", `versão de pet desconhecida: ${pet.versao} (o servidor confere a ${VERSOES_PET.join(", ")})`);
  if (!VERSOES_TAMER_CONFERIDAS.includes(tamer.versao))
    return recusar("versao_tamer_desconhecida", `o registro do Tamer é da versão ${tamer.versao}, e o servidor confere a ${VERSOES_TAMER_CONFERIDAS.join(" e a ")}: atualize o jogo`);

  /* 0. o compromisso de cada semente pedida: o registro até o indice do pedido é o mesmo */
  const hashes = hashesAte(pet.log, entregues.map(x => x.indice));
  for (const x of entregues) {
    const h = hashes.get(x.indice);
    if (h !== undefined && h !== x.hash)
      return recusar("hash_nao_confere", `o registro até o evento ${x.indice} não é o do pedido da semente ${x.numero}: ele mudou depois do pedido`);
  }

  /* 1. o pet e as lutas: um passe só pela conta da MMO1; o evento inválido (e a luta que não era possível) falha alto */
  let m: Motor, lutas: LutaRanqueada[], salao: LutaSalaoVista[];
  const sementes: SementeEntregue[] = entregues.map(x => ({ semente: x.semente, indice: x.indice, hora: x.hora,
    ...(x.rival === undefined ? {} : { rival: x.rival, mapa: x.mapa ?? null }) }));
  try { ({ motor: m, lutas, salao } = refazerComLutas(pet.semente, pet.versao, pet.log, sementes)); }
  catch (err) { return recusar("pet_nao_reproduz", `o registro do pet não reproduz: ${msg(err)}`); }
  const t1 = performance.now();

  /* 2. o Tamer: o mesmo lerTamer do jogo, por um armazenamento de uma chave só */
  let t;
  try {
    const texto = JSON.stringify({ versao: tamer.versao, log: tamer.log });
    t = lerTamer({ getItem: k => (k === CHAVE_TAMER ? texto : null), setItem: () => { throw new Error("a conferência não grava"); } });
  } catch (err) { return recusar("tamer_nao_reproduz", `o registro do Tamer não reproduz: ${msg(err)}`); }
  const x = t.marco(MARCO_MEGA);
  let marco10: SituacaoMarco = "sem_marco";
  if (x) {
    if (x.pet !== pet.semente) marco10 = "de_outro_pet";
    else if (marcoConfere(x, m)) marco10 = "confere";
    else return recusar("marco_nao_confere", `o marco ${MARCO_MEGA} do Tamer diz que o pet ${x.pet} chegou ao Mega (${x.forma}) no tick ${x.tick}, e o registro do pet não mostra essa evolução`);
  }
  /* o reset deste pet (MMO8): o registro enviado é o do reset? Então o nível tem de bater */
  const rs = t.resetDe(pet.semente), nivelPet = nivelDoReset(m);
  let reset: ResetVisto = { situacao: "sem_reset", nivel: null, hash: null, por: null };
  if (rs) {
    const final = rs.eventos === pet.log.length && rs.hash === hashRegistro(pet.log);
    if (final && rs.nivel !== nivelPet)
      return recusar("reset_nao_confere", `o Tamer diz que o pet ${pet.semente} se aposentou no nível ${rs.nivel} do reset, e o registro dele dá o nível ${nivelPet}`);
    reset = { situacao: final ? "confere" : "outro_registro", nivel: rs.nivel, hash: rs.hash, por: rs.por };
  }
  const t2 = performance.now();

  const r2 = (v: number) => +v.toFixed(2);
  const fronteira: FronteiraVista = {
    torre: m.instalacoes?.torre_batalha?.recorde ?? 0, fabrica: t.recordeFabrica?.valor ?? 0, salao,
    tentativasSalao: t.salao.map(x => ({ n: x.n, lutas: x.lutas.map(l => ({ pet: l.pet, s: l.s, venceu: l.venceu })) })),
  };
  const digimon: DigimonVisto = { pontos: pontosDoDigimon(lutas), estagio: estagioMaximo(m), forma: nomeForma(m.forma), nivelReset: nivelPet };
  return { resultado: "aceito", marco10, digimon, feitos: feitosVistos(t, m), reset, fronteira, marcosTamer: marcosDoTamer(t), lutas, semanas: linhasDaSemana(lutas), pontos: lutas.reduce((s, l) => s + l.pontos, 0),
    ms: { replay: r2(t1 - t0), tamer: r2(t2 - t1), total: r2(performance.now() - t0) } };
}

/** os feitos do Tamer que o pet m fez e o replay dele mostra (MMO8): a medalha do registro do Tamer ganha por este pet conta se a campanha
    do pet tem a vitória contra o líder dela; o título da Liga, se o título do Tamer deste pet tem o título no Motor.liga do pet */
export function feitosVistos(t: Tamer, m: Motor): FeitosVistos {
  const medalhas = t.medalhas.filter(g => g.pet === m.semente && (m.campanha[MEDALHA_POR_ID[g.id]!.lider] ?? 0) > 0).map(g => g.id);
  return { medalhas, liga: !!t.tituloDe(m.semente) && m.liga.titulos > 0 };
}
