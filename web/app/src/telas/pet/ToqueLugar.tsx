/* O toque nos lugares da ilha (direcao B, "Lugares da ilha"; docs/TAREFA_V3_LUGARES_3D.md, secao 13): um clique ou tap no portao abre o
   Lutar e na barraca abre o Diario, como o trilho de icones (lugaresIlha.ts, LUGAR_DESTINO). So o lugar aberto (LUGAR_ABERTO) abre; o
   cais, trancado e ainda sem menu, nao faz nada (o cadeado e o "Nv" ficam para o nivel do Tamer, plano V da progressao). O mesmo gesto do
   toque no pet (ToquePet.tsx, TOQUE): um arrasto (a camera livre, a bola, pegar o pet) ou um toque longo nao conta, e o toque no sprite do
   pet e do pet. Com o mouse, o cursor vira a mao sobre um lugar que abre. */
import { useEffect, useRef, type RefObject } from "react";
import type { Destino } from "../../rotas.ts";
import { CENA } from "./cenaEstado.ts";
import { LUGAR_ABERTO, LUGAR_DESTINO } from "./lugaresIlha.ts";
import { TOQUE, noSprite } from "./ToquePet.tsx";

type Alvo = EventTarget & { getBoundingClientRect(): { left: number; top: number }; style?: { cursor: string } };

/** o destino do lugar aberto sob o ponto do cliente (px), ou null (fora dos lugares, num lugar trancado, sobre o pet) */
export function destinoNoPonto(el: Alvo, cx: number, cy: number): Destino | null {
  if (CENA.coberto || CENA.bolaNaMao || CENA.petNaMao) return null;
  if (noSprite(cx, cy, el.getBoundingClientRect(), CENA.ret)) return null;
  const l = CENA.mundo?.lugarEm?.(cx, cy) ?? null;
  return l && LUGAR_ABERTO[l] ? LUGAR_DESTINO[l] : null;
}

/** liga o toque nos lugares num alvo (a cena do habitat; nos testes, um EventTarget com o retangulo); devolve a funcao que desliga */
export function ligarToqueLugar(el: Alvo, ir: (d: Destino) => void): () => void {
  type P = Event & { pointerId: number; clientX: number; clientY: number; button: number; buttons: number; pointerType: string };
  let mao: { id: number; x: number; y: number; t: number } | null = null, mouseNaMao = false;
  const baixo = (ev: Event) => {
    const e = ev as P;
    if ((e.pointerType === "mouse" && e.button !== 0) || !destinoNoPonto(el, e.clientX, e.clientY)) return;
    mao = { id: e.pointerId, x: e.clientX, y: e.clientY, t: performance.now() };
  };
  const move = (ev: Event) => {
    const e = ev as P;
    if (mao && mao.id === e.pointerId && (CENA.petNaMao || Math.hypot(e.clientX - mao.x, e.clientY - mao.y) > TOQUE.andaMax)) mao = null;
    /* o cursor: so com o mouse parado (sem botao), e so quando muda */
    if (e.pointerType === "mouse" && e.buttons === 0 && el.style) {
      const sobre = !!destinoNoPonto(el, e.clientX, e.clientY);
      if (sobre !== mouseNaMao) { mouseNaMao = sobre; el.style.cursor = sobre ? "pointer" : ""; }
    }
  };
  const cima = (ev: Event) => {
    const e = ev as P, m = mao; mao = null;
    if (!m || m.id !== e.pointerId) return;
    if (performance.now() - m.t > TOQUE.duraMax || Math.hypot(e.clientX - m.x, e.clientY - m.y) > TOQUE.andaMax) return;
    const d = destinoNoPonto(el, e.clientX, e.clientY);
    if (d) ir(d);
  };
  const solta = () => { mao = null; };
  el.addEventListener("pointerdown", baixo); el.addEventListener("pointermove", move);
  el.addEventListener("pointerup", cima); el.addEventListener("pointercancel", solta);
  return () => {
    el.removeEventListener("pointerdown", baixo); el.removeEventListener("pointermove", move);
    el.removeEventListener("pointerup", cima); el.removeEventListener("pointercancel", solta);
    if (el.style && mouseNaMao) el.style.cursor = "";
  };
}

/** escuta o ponteiro na cena do habitat (`alvo`) */
export function ToqueLugar({ alvo, ir }: { alvo: RefObject<HTMLElement | null>; ir: (d: Destino) => void }) {
  /* o `ir` mais novo (o do App le a ultima aba de cada destino), sem religar o ponteiro a cada render */
  const irAgora = useRef(ir);
  irAgora.current = ir;
  useEffect(() => {
    const el = alvo.current;
    return el ? ligarToqueLugar(el, d => irAgora.current(d)) : undefined;
  }, [alvo]);
  return null;
}
