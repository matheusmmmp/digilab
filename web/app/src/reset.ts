/* O reset do pet (docs/PLANO_V3_MMO.md, etapa MMO8, secao 9; MMO-17 a MMO-19 APROVADAS em 2026-11-11). O reset e do pet, nao do Tamer: o
   pet ativo se aposenta em Diario › Geracoes (o heranca.ts, CHAVE_GERACOES) e um ovo do brasao escolhido choca (o jornada.ts,
   chocarDoBrasao). O Tamer fica com tudo. Se o pet chegou ao Ultimate, o reset da bonus: o Respeito (pontos.ts, respeitoDoReset) e os Bits
   (tamer.ts, pagarReset; um reset pago por semana de relogio). Sem heranca de stats: o ovo novo e um Motor novo, e nada do motor nem do
   save do pet muda. O cruzamento tambem conta como reset do pai ativo que se aposenta (registrarResetDoCruzamento).

   Atras da chave RESET_LIGADO (tamer.ts), desligada: a tela espera a prancha (docs/PLANO_UX_RESET.md). Com ela desligada, nada aqui roda
   no jogo (o heranca.ts so chama com a chave ligada).

   Os dois pets (o grupo, DOIS_OVOS_LIGADO): o reset do par ainda nao existe e falha alto (D-CONTA-161), como o envio do grupo (D-CONTA-77).
   O pet de exemplo e o laboratorio tambem nao resetam. */
import type { Especie, Motor } from "../motor/index.ts";
import { nomeForma } from "../motor/index.ts";
import { hashAte } from "./ranking/pedido.ts";
import { BONUS_RESET, nivelDoReset, type NivelReset } from "./ranking/pontos.ts";
import { RESET_LIGADO, pagarReset, type BitsGanhos, type ResetPet, type Tamer } from "./tamer.ts";

/** o que o reset do pet daria agora (a previa da tela): o nivel, o bonus e se os Bits desta semana ja foram pagos */
export interface PreviaReset { nivel: NivelReset; respeito: number; bits: number; bitsDaSemanaPagos: boolean }
export function previaDoReset(m: Motor, t: Tamer, quando: number = Date.now()): PreviaReset {
  const nivel = nivelDoReset(m), b = BONUS_RESET[nivel], pagos = t.semanaDoResetPago(quando);
  return { nivel, respeito: b.respeito, bits: pagos ? 0 : b.bits, bitsDaSemanaPagos: pagos };
}

/** o evento do reset do pet (sem a hora): a semente, o hash do registro inteiro, os eventos, o estagio e a forma, o nivel e o tick */
export async function eventoDoReset(m: Motor, por: ResetPet["por"]): Promise<Omit<ResetPet, "quando">> {
  return { pet: m.semente, hash: await hashAte(m.log, m.log.length), eventos: m.log.length, est: m.estagioAtual, forma: nomeForma(m.forma),
    nivel: nivelDoReset(m), tick: m.e.tick, por };
}

/** grava o reset no Tamer e paga os Bits (se o nivel da bonus e a semana ainda nao tem um reset pago). Devolve os dois */
export function aplicarReset(t: Tamer, x: Omit<ResetPet, "quando">, quando: number = Date.now()): { reset: ResetPet; bits: BitsGanhos | null } {
  const reset = t.resetar(x, quando);
  return { reset, bits: pagarReset(t, reset, quando) };
}

/** o reset do pet ativo pela tela (que espera a prancha): aposenta em Geracoes, grava o reset no Tamer e choca o ovo do brasao. Falha alto
    com a chave desligada, com o par, com o pet de exemplo e no laboratorio */
export async function resetar(esp: Especie): Promise<{ reset: ResetPet; bits: BitsGanhos | null }> {
  if (!RESET_LIGADO) throw new Error("o reset está desligado (RESET_LIGADO): a tela espera a prancha");
  const { jogoAtual, mudarTamer } = await import("./jogo.ts");
  const { chocarDoBrasao } = await import("./jornada.ts");
  const { aposentar } = await import("./heranca.ts");
  const j = jogoAtual();
  if (j.emLab) throw new Error("o pet de teste do laboratório não se aposenta");
  if (j.grupo) throw new Error("o reset dos dois pets ainda não existe (D-CONTA-161)");
  if (j.origem === "exemplo") throw new Error("o pet de exemplo não se aposenta");
  const m = j.motor, x = await eventoDoReset(m, "reset");
  aposentar(m, 0);
  const r = mudarTamer(t => aplicarReset(t, x));
  chocarDoBrasao(esp, false);
  return r;
}

/** o cruzamento conta como reset do pai ativo que se aposenta (MMO-17): grava o reset dele com o nivel dele. O heranca.ts chama depois do
    cruzar, com a copia do pai, so com a chave ligada */
export async function registrarResetDoCruzamento(pai: Motor): Promise<{ reset: ResetPet; bits: BitsGanhos | null }> {
  if (!RESET_LIGADO) throw new Error("o reset está desligado (RESET_LIGADO)");
  const { mudarTamer } = await import("./jogo.ts");
  const x = await eventoDoReset(pai, "cruzamento");
  return mudarTamer(t => aplicarReset(t, x));
}
