/* O toque no pet (docs/registro/2026-11.md, a seção "VIDA DO PET, a cena e o toque", o passo 2 da "Vida do pet"): um clique ou tap no sprite dispara o `acariciar` que ja existe
   (acoes.ts, agir: o MESMO evento do botao Carinho, sem posicao; o treino nunca e o dono clicando carinho ou tapa como recompensa ou
   punicao). A reacao mostrada sai do corpo: le a solidao, o estresse e o susto antes e depois (cenaAcao.ts, reacaoDoCorpo). O tapa nao vem
   pelo toque (fica so no botao). Um arrasto (a camera livre, a bola, pegar o pet) ou um toque longo nao conta. */
import { useEffect, type RefObject } from "react";
import { momentoDoCarinho } from "./momentos.ts";
import type { Motor } from "../../../motor/index.ts";
import { agir } from "../../acoes.ts";
import { jogoAtual } from "../../jogo.ts";
import { lugarAberto } from "../../viagem.ts";
import { CENA } from "./cenaEstado.ts";
import { mostrarReacao, reacaoDoCorpo, type LeituraCorpo } from "./cenaAcao.ts";

/** o toque no pet nao vale: um painel cobre a cena, a bola ou o pet esta na mao (PegarPet.tsx) ou um lugar esta aberto (Crescer, L2: a
    ilha fica viva, mas clicar nela nao grava) */
export const toqueIgnorado = (): boolean => CENA.coberto || CENA.bolaNaMao || CENA.petNaMao || lugarAberto();

/** o toque: quanto o ponteiro pode andar (px) e quanto pode demorar (ms) para ainda ser um toque; a folga em volta do sprite (px, para o dedo).
    PROPOSTO, SEM FONTE */
export const TOQUE = { andaMax: 10, duraMax: 600, folga: 8 } as const;

/** o que o corpo do pet diz agora (o laco do v11 em diante); falha alto num pet sem corpo */
export function lerCorpo(m: Motor): LeituraCorpo {
  const laco = m.v11?.laco;
  if (!laco) throw new Error("o toque no pet precisa do corpo (pets v11 em diante)");
  const { q, C, cc } = laco.corpo;
  for (const k of ["solidao", "estresse", "susto"]) if (typeof q[k] !== "number") throw new Error("o corpo nao tem o quimico " + k);
  return { solidao: q.solidao, estresse: q.estresse, susto: q.susto, C, medo: cc.gestos ? cc.medo_da_mao : 0 };
}

/** o ponto do cliente cai no sprite do pet? (`cena`: o retangulo do cliente da cena; CENA.ret e relativo a ela) */
export function noSprite(cx: number, cy: number, cena: { left: number; top: number }, ret: { x: number; y: number; w: number; h: number } | null): boolean {
  if (!ret) return false;
  const f = TOQUE.folga, x = cx - cena.left, y = cy - cena.top;
  return x >= ret.x - f && x <= ret.x + ret.w + f && y >= ret.y - f && y <= ret.y + ret.h + f;
}

/** o toque no pet: o mesmo `acariciar` do botao, e a reacao do corpo na vista. Devolve false se o pet nao pode receber carinho */
export function tocarNoPet(agora: number): boolean {
  const antes = lerCorpo(jogoAtual().motor);
  if (!agir("acariciar")) return false;
  const r = reacaoDoCorpo(antes, lerCorpo(jogoAtual().motor), agora);
  mostrarReacao(r);
  if (r.tipo === "relaxou") momentoDoCarinho(agora);   /* o Feliz quando o pulinho acaba (momentos.ts, HR1) */
  return true;
}

/** liga o toque num alvo (a cena do habitat; nos testes, um EventTarget com o retangulo); devolve a funcao que desliga. Com o pet na mao
    (PegarPet.tsx, ligado depois deste no mesmo alvo) o toque e largado: o arrasto que pega o pet nunca vira carinho */
export function ligarToquePet(el: EventTarget & { getBoundingClientRect(): { left: number; top: number } }): () => void {
  type P = Event & { pointerId: number; clientX: number; clientY: number; button: number; pointerType: string };
  let mao: { id: number; x: number; y: number; t: number } | null = null;
  const baixo = (ev: Event) => {
    const e = ev as P;
    if ((e.pointerType === "mouse" && e.button !== 0) || toqueIgnorado()) return;
    if (!noSprite(e.clientX, e.clientY, el.getBoundingClientRect(), CENA.ret)) return;
    mao = { id: e.pointerId, x: e.clientX, y: e.clientY, t: performance.now() };
  };
  const move = (ev: Event) => {
    const e = ev as P;
    if (mao && mao.id === e.pointerId && (CENA.petNaMao || Math.hypot(e.clientX - mao.x, e.clientY - mao.y) > TOQUE.andaMax)) mao = null;
  };
  const cima = (ev: Event) => {
    const e = ev as P, m = mao; mao = null;
    if (!m || m.id !== e.pointerId || toqueIgnorado()) return;
    const agora = performance.now();
    if (agora - m.t <= TOQUE.duraMax && Math.hypot(e.clientX - m.x, e.clientY - m.y) <= TOQUE.andaMax) tocarNoPet(agora);
  };
  const solta = () => { mao = null; };
  el.addEventListener("pointerdown", baixo); el.addEventListener("pointermove", move);
  el.addEventListener("pointerup", cima); el.addEventListener("pointercancel", solta);
  return () => {
    el.removeEventListener("pointerdown", baixo); el.removeEventListener("pointermove", move);
    el.removeEventListener("pointerup", cima); el.removeEventListener("pointercancel", solta);
  };
}

/** escuta o ponteiro na cena do habitat (`alvo`) */
export function ToquePet({ alvo }: { alvo: RefObject<HTMLElement | null> }) {
  useEffect(() => {
    const el = alvo.current;
    return el ? ligarToquePet(el) : undefined;
  }, [alvo]);
  return null;
}
