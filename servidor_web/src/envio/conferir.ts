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

   A conferência NÃO usa a assinatura do pet: ela difere entre o Chrome e o Node no último bit (MMO0). Só o que sai das lutas e do registro. */
import { createHash, type Hash } from "node:crypto";
import { VERSOES_PET, type EventoRegistro, type Motor } from "../../../web/app/motor/index.ts";
import { linhasDaSemana, refazerComLutas, type LinhaSemana, type LutaRanqueada, type SementeEntregue } from "../../../web/app/src/ranking/pontos.ts";
import { marcosDoTamer } from "../../../web/app/src/marcosTamer.ts";
import { CHAVE_TAMER, lerTamer, MARCO_MEGA, marcoConfere, VERSAO_TAMER, type EventoTamer } from "../../../web/app/src/tamer.ts";

/** por que um envio foi recusado (o código vai na resposta e no banco; o detalhe é o texto do erro) */
export type MotivoRecusa =
  | "versao_pet_desconhecida"    // a versão do pet não é uma das que o motor abre
  | "versao_tamer_desconhecida"  // o registro do Tamer não é da versão de hoje: atualize o jogo
  | "pet_nao_reproduz"           // o motor recusou um evento do registro do pet
  | "tamer_nao_reproduz"         // o registro do Tamer não se refaz
  | "hash_nao_confere"           // o registro até o indice de uma semente pedida não é o do pedido (mudou depois da semente)
  | "marco_nao_confere";         // o Tamer diz que este pet chegou ao Mega, e o registro do pet não mostra a evolução no tick e na forma

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

export interface Aceito {
  resultado: "aceito";
  marco10: SituacaoMarco;
  /** os marcos que o registro do Tamer cumpre (marcosDoTamer: 5, 7, 8, 9, 10); a trava do pedido da semente os lê */
  marcosTamer: number[];
  lutas: LutaRanqueada[];
  semanas: LinhaSemana[];
  pontos: number;
  /** o tempo de cada parte, em milissegundos (o replay do pet com as lutas, o Tamer e o marco) */
  ms: { replay: number; tamer: number; total: number };
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
  if (tamer.versao !== VERSAO_TAMER)
    return recusar("versao_tamer_desconhecida", `o registro do Tamer é da versão ${tamer.versao}, e o servidor confere a ${VERSAO_TAMER}: atualize o jogo`);

  /* 0. o compromisso de cada semente pedida: o registro até o indice do pedido é o mesmo */
  const hashes = hashesAte(pet.log, entregues.map(x => x.indice));
  for (const x of entregues) {
    const h = hashes.get(x.indice);
    if (h !== undefined && h !== x.hash)
      return recusar("hash_nao_confere", `o registro até o evento ${x.indice} não é o do pedido da semente ${x.numero}: ele mudou depois do pedido`);
  }

  /* 1. o pet e as lutas: um passe só pela conta da MMO1; o evento inválido (e a luta que não era possível) falha alto */
  let m: Motor, lutas: LutaRanqueada[];
  const sementes: SementeEntregue[] = entregues.map(x => ({ semente: x.semente, indice: x.indice, hora: x.hora,
    ...(x.rival === undefined ? {} : { rival: x.rival, mapa: x.mapa ?? null }) }));
  try { ({ motor: m, lutas } = refazerComLutas(pet.semente, pet.versao, pet.log, sementes)); }
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
  const t2 = performance.now();

  const r2 = (v: number) => +v.toFixed(2);
  return { resultado: "aceito", marco10, marcosTamer: marcosDoTamer(t), lutas, semanas: linhasDaSemana(lutas), pontos: lutas.reduce((s, l) => s + l.pontos, 0),
    ms: { replay: r2(t1 - t0), tamer: r2(t2 - t1), total: r2(performance.now() - t0) } };
}
