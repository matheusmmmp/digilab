/* O reset do pet (docs/PLANO_V3_MMO.md, etapa MMO8, secao 9; MMO-17 a MMO-19 APROVADAS em 2026-11-11; a tela pela prancha
   docs/pranchas/ux-reset/, UX-RS-1 a 7 APROVADAS em 2026-11-19). O reset e do pet, nao do Tamer: o pet ativo se aposenta em Diario ›
   Geracoes (o heranca.ts, CHAVE_GERACOES) e um ovo do brasao escolhido choca (o jornada.ts, chocarDoBrasao). O Tamer fica com tudo. Se o
   pet chegou ao Ultimate, o reset da bonus: o Respeito (pontos.ts, respeitoDoReset) e os Bits (tamer.ts, pagarReset; um reset pago por
   semana de relogio). Sem heranca de stats: o ovo novo e um Motor novo, e nada do motor nem do save do pet muda. O cruzamento tambem conta
   como reset do pai ativo que se aposenta (registrarResetDoCruzamento).

   O passo a passo da tela (telas/pet/Aposentar.tsx): aposentarPorReset grava o reset e poe o pet em Geracoes; o ovo novo vem da escolha
   do brasao, que fica sem "Voltar" enquanto o reset espera o ovo (CHAVE_RESET_PENDENTE, para sobreviver a um recarregar). Depois, o
   registro do aposentado vai sozinho ao servidor, com a conta (UX-RS-4, enviarAposentados): sem o envio, o servidor nao ve o reset.

   Atras da chave RESET_LIGADO (tamer.ts). Os dois pets (o grupo, DOIS_OVOS_LIGADO): os dois se aposentam juntos, num reset so, com o
   bonus do pet de nivel mais alto (Matheus, 2026-11-19, "Bonus do mais alto"; D-CONTA-161 e D-CONTA-179). O par vai inteiro para Geracoes,
   e o reset no Tamer e o do pet mais alto. O servidor ainda nao confere o envio do grupo (D-CONTA-77): o Respeito do reset do par fica so
   no jogo. O pet de exemplo e o laboratorio nao resetam. */
import { useEffect, useState } from "react";
import type { Especie, GrupoDoJogo, Motor, Ritmo } from "../motor/index.ts";
import { nomeForma } from "../motor/index.ts";
import { apiDoBuild } from "./conta/apiDoBuild.ts";
import { aposentar, aposentarPar, lerAposentados } from "./heranca.ts";
import { jogoAtual, mudarTamer, tamerAtual, type Jogo } from "./jogo.ts";
import { chocarDoBrasao } from "./jornada.ts";
import { hashAte } from "./ranking/pedido.ts";
import { BONUS_RESET, nivelDoReset, type NivelReset } from "./ranking/pontos.ts";
import { enviarRegistro, ligarRanqueada, ranqueadaLigada } from "./ranking/ranqueada.ts";
import { CHAVE, textoSave, textoSaveGrupo } from "./save.ts";
import { RESET_LIGADO, pagarReset, versaoTamerDe, type BitsGanhos, type ResetPet, type Tamer } from "./tamer.ts";

/** a semente do pet que se aposentou pelo reset e ainda espera o ovo novo (a escolha do brasao sem "Voltar") */
export const CHAVE_RESET_PENDENTE = CHAVE + "-reset-pendente";
/** as sementes dos aposentados cujo registro o servidor ja recebeu (UX-RS-4); so do aparelho: apagar so manda de novo */
export const CHAVE_RESETS_ENVIADOS = CHAVE + "-resets-enviados";

/** o que o reset do pet daria agora (a previa da tela): o nivel, o bonus e se os Bits desta semana ja foram pagos */
export interface PreviaReset { nivel: NivelReset; respeito: number; bits: number; bitsDaSemanaPagos: boolean }
export function previaDoReset(m: Motor, t: Tamer, quando: number = Date.now()): PreviaReset {
  const nivel = nivelDoReset(m), b = BONUS_RESET[nivel], pagos = t.semanaDoResetPago(quando);
  return { nivel, respeito: b.respeito, bits: pagos ? 0 : b.bits, bitsDaSemanaPagos: pagos };
}

/** o evento do reset do pet (sem a hora): a semente, o hash do registro inteiro, os eventos, o estagio e a forma, o nivel e o tick. Tudo
    e lido na hora da chamada (o hash, de uma copia do registro): o pet que anda durante a conta do hash nao muda o evento */
export async function eventoDoReset(m: Motor, por: ResetPet["por"]): Promise<Omit<ResetPet, "quando">> {
  const log = m.log.slice();
  const base = { pet: m.semente, eventos: log.length, est: m.estagioAtual, forma: nomeForma(m.forma), nivel: nivelDoReset(m), tick: m.e.tick, por };
  return { ...base, hash: await hashAte(log, log.length) };
}

/** grava o reset no Tamer e paga os Bits (se o nivel da bonus e a semana ainda nao tem um reset pago). Devolve os dois */
export function aplicarReset(t: Tamer, x: Omit<ResetPet, "quando">, quando: number = Date.now()): { reset: ResetPet; bits: BitsGanhos | null } {
  const reset = t.resetar(x, quando);
  return { reset, bits: pagarReset(t, reset, quando) };
}

/** o pet do par que da o bonus: o de nivel do reset mais alto; no empate, o primeiro do grupo (D-CONTA-179) */
export function petDoBonus(g: GrupoDoJogo): Motor {
  return g.ids.map(i => g.motor(i)).reduce((a, b) => (nivelDoReset(b) > nivelDoReset(a) ? b : a));
}
/** o pet cujo reset conta: o ativo, ou, com os dois pets, o do bonus */
export const petDoReset = (j: Jogo): Motor => (j.grupo ? petDoBonus(j.grupo) : j.motor);

/** por que o pet ativo (ou o par) nao pode se aposentar pelo reset agora; null se pode */
export function semReset(j: Jogo): string | null {
  if (!RESET_LIGADO) return "o reset está desligado (RESET_LIGADO)";
  if (j.emLab) return "o pet de teste do laboratório não se aposenta";
  if (j.origem === "exemplo") return "o pet de exemplo não se aposenta";
  if (j.erroSave || j.erroTamer) return "o save ou o registro do Tamer não abriu";
  if (j.nascendo > 0) return "o ovo ainda não chocou";
  if (ovoDoResetPendente(j)) return "este pet já se aposentou: falta escolher o brasão";
  return null;
}

/** o pet ativo se aposenta pelo reset: o save dele vai para Geracoes, o reset entra no Tamer (com os Bits, se for o caso) e o reset passa
    a esperar o ovo novo. Com os dois pets, o par inteiro vai para Geracoes e o reset e o do pet do bonus. Falha alto com a chave desligada,
    com o pet de exemplo e no laboratorio */
export async function aposentarPorReset(): Promise<{ reset: ResetPet; bits: BitsGanhos | null }> {
  const j = jogoAtual(), nao = semReset(j);
  if (nao) throw new Error(nao);
  const g = j.grupo, m = petDoReset(j), eventos = m.log.length;
  const salvo = g ? textoSaveGrupo(g, j.foco) : textoSave(m), x = await eventoDoReset(m, "reset");
  if (jogoAtual().motor !== j.motor || jogoAtual().grupo !== g) throw new Error("o pet ativo mudou durante o reset");
  if (x.eventos !== eventos || (!g && JSON.parse(salvo).log.length !== x.eventos)) throw new Error("o save e o evento do reset não têm o mesmo registro");
  if (g) aposentarPar(g, salvo); else aposentar(m, 0, salvo);
  const r = mudarTamer(t => aplicarReset(t, x));
  try { localStorage.setItem(CHAVE_RESET_PENDENTE, String(m.semente)); } catch { /* sem o armazenamento, a tela abre a escolha do brasao igual */ }
  void enviarAposentados().catch((err: unknown) => console.error(err));
  return r;
}

/** o pet ativo (ou o par) ja se aposentou pelo reset e espera o ovo novo */
export function ovoDoResetPendente(j: Jogo): boolean {
  if (!RESET_LIGADO) return false;
  let s: string | null = null;
  try { s = localStorage.getItem(CHAVE_RESET_PENDENTE); } catch { return false; }
  if (s === null) return false;
  const pets = j.grupo ? j.grupo.ids.map(i => j.grupo!.motor(i)) : [j.motor];
  return pets.some(m => Number(s) === m.semente && tamerAtual().resetDe(m.semente) !== null);
}

/** o ovo novo do reset: o pet aposentado nao vai para os guardados (ele ja esta em Geracoes) */
export function chocarDoReset(esp: Especie, ritmo: Ritmo = "rapida"): void {
  chocarDoBrasao(esp, false, ritmo);
  try { localStorage.removeItem(CHAVE_RESET_PENDENTE); } catch { /* ja chocou */ }
}

/** o reset inteiro de uma vez (os testes e quem ja sabe o brasao): aposenta e choca o ovo do brasao */
export async function resetar(esp: Especie): Promise<{ reset: ResetPet; bits: BitsGanhos | null }> {
  const r = await aposentarPorReset();
  chocarDoReset(esp);
  return r;
}

/** o cruzamento conta como reset do pai ativo que se aposenta (MMO-17): grava o reset dele com o nivel dele. O heranca.ts chama depois do
    cruzar, com a copia do pai, so com a chave ligada */
export async function registrarResetDoCruzamento(pai: Motor): Promise<{ reset: ResetPet; bits: BitsGanhos | null }> {
  if (!RESET_LIGADO) throw new Error("o reset está desligado (RESET_LIGADO)");
  const x = await eventoDoReset(pai, "cruzamento");
  const r = mudarTamer(t => aplicarReset(t, x));
  void enviarAposentados().catch((err: unknown) => console.error(err));
  return r;
}

/* ------------------------------------------------------------ o envio do aposentado (UX-RS-4) */
const lerEnviados = (): number[] => { try { return JSON.parse(localStorage.getItem(CHAVE_RESETS_ENVIADOS) || "[]") as number[]; } catch { return []; } };

/** os resets do Tamer cujo registro final ainda nao chegou ao servidor e que este aparelho tem em Geracoes (o mesmo numero de eventos) */
export function aposentadosParaEnviar(t: Tamer = tamerAtual()): { semente: number; versao: number; log: Motor["log"] }[] {
  const enviados = lerEnviados(), ap = lerAposentados();
  return t.resets.filter(r => !enviados.includes(r.pet)).flatMap(r => {
    const a = ap.find(x => x.semente === r.pet && x.log.length === r.eventos);
    return a ? [{ semente: a.semente, versao: a.versao, log: a.log }] : [];
  });
}

/** manda ao servidor o registro final de cada aposentado que falta, com o do Tamer (POST /envios, o mesmo envio da luta ranqueada): o
    servidor confere o reset pelo hash e pelo tamanho do registro. Sem o servidor no build, nao faz nada; sem conta ou sem resposta, para e
    tenta de novo na proxima (o reset seguinte e a abertura do cais). Devolve quantos o servidor recebeu */
export async function enviarAposentados(): Promise<number> {
  if (!RESET_LIGADO) return 0;
  const api = apiDoBuild();
  if (!api) return 0;
  if (!ranqueadaLigada()) ligarRanqueada({ api, buscar: (u, i) => fetch(u, i), armaz: localStorage, agora: () => Date.now() });
  let n = 0;
  for (const pet of aposentadosParaEnviar()) {
    const t = tamerAtual();
    if (!(await enviarRegistro(pet, { versao: versaoTamerDe(t.log), log: t.log }))) break;
    try { localStorage.setItem(CHAVE_RESETS_ENVIADOS, JSON.stringify([...new Set([...lerEnviados(), pet.semente])])); } catch { /* manda de novo depois */ }
    n++;
  }
  return n;
}

/* ------------------------------------------------------------ a tela (aberta de Meus pets) */
let aberta = false;
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
export function abrirAposentar(): void { aberta = true; avisar(); }
export function fecharAposentar(): void { aberta = false; avisar(); }
export function useAposentar(): boolean {
  const [, t] = useState(0);
  useEffect(() => { const f = () => t(x => x + 1); ouvintes.add(f); return () => { ouvintes.delete(f); }; }, []);
  return aberta;
}
