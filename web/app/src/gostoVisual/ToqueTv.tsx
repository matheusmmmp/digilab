/* O toque na TV da ilha abre o painel da TV (docs/PLANO_UX_GOSTO_VISUAL.md, a UX-GV-2; a etapa 2 do código): a TV vira um lugar da ilha, como
   o portão e a barraca (telas/pet/ToqueLugar.tsx, o mesmo gesto: um arrasto ou um toque longo não conta, e o toque no sprite do pet é do
   pet). A cena diz se o ponto cai na TV (CENA.mundo.tvEm, que só existe com o cantinho) e a tela Pet atende o pedido (painelTvEstado.ts);
   fora da tela Pet, ou com um painel por cima da cena, o toque não faz nada. Com o mouse, o cursor vira a mão sobre a TV. O teclado chega ao
   painel pela linha "TV" da pilha. Só com `?gosto_visual=1`. */
import { useEffect } from "react";
import { objetoNoPonto } from "../componentes/ObjetosDaIlha.tsx";
import { CENA } from "../telas/pet/cenaEstado.ts";
import { TOQUE, noSprite } from "../telas/pet/ToquePet.tsx";
import { pedirPainelTv } from "./painelTvEstado.ts";

type Alvo = EventTarget & { getBoundingClientRect(): { left: number; top: number }; style?: { cursor: string } };

/** a TV está sob o ponto do cliente (px) e o toque é dela? (não com a cena coberta, a bola ou o pet na mão, nem sobre o pet, a bola ou a
    tigela: o objeto na frente da TV fica com o toque, como em ObjetosDaIlha.tsx) */
export function tvNoPonto(el: Alvo, cx: number, cy: number): boolean {
  if (CENA.coberto || CENA.bolaNaMao || CENA.petNaMao) return false;
  if (noSprite(cx, cy, el.getBoundingClientRect(), CENA.ret)) return false;
  if (!(CENA.mundo?.tvEm?.(cx, cy) ?? false)) return false;
  return objetoNoPonto(el, cx, cy) === null;
}

/** liga o toque na TV num alvo (a cena do habitat; nos testes, um EventTarget com o retângulo); devolve a função que desliga */
export function ligarToqueTv(el: Alvo, pedir: () => void): () => void {
  type P = Event & { pointerId: number; clientX: number; clientY: number; button: number; buttons: number; pointerType: string };
  let mao: { id: number; x: number; y: number; t: number } | null = null, mouseNaMao = false;
  const baixo = (ev: Event) => {
    const e = ev as P;
    if ((e.pointerType === "mouse" && e.button !== 0) || !tvNoPonto(el, e.clientX, e.clientY)) return;
    mao = { id: e.pointerId, x: e.clientX, y: e.clientY, t: performance.now() };
  };
  const move = (ev: Event) => {
    const e = ev as P;
    if (mao && mao.id === e.pointerId && (CENA.petNaMao || Math.hypot(e.clientX - mao.x, e.clientY - mao.y) > TOQUE.andaMax)) mao = null;
    if (e.pointerType === "mouse" && e.buttons === 0 && el.style) {
      const sobre = tvNoPonto(el, e.clientX, e.clientY);
      if (sobre !== mouseNaMao) { mouseNaMao = sobre; el.style.cursor = sobre ? "pointer" : ""; }
    }
  };
  const cima = (ev: Event) => {
    const e = ev as P, m = mao; mao = null;
    if (!m || m.id !== e.pointerId) return;
    if (performance.now() - m.t > TOQUE.duraMax || Math.hypot(e.clientX - m.x, e.clientY - m.y) > TOQUE.andaMax) return;
    if (tvNoPonto(el, e.clientX, e.clientY)) pedir();
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

/** escuta o ponteiro na cena do habitat (a `.pet-cena`, montada em todas as rotas) */
export function ToqueTv() {
  useEffect(() => {
    const el = document.querySelector<HTMLElement>(".pet-cena");
    return el ? ligarToqueTv(el, () => { pedirPainelTv(); }) : undefined;
  }, []);
  return null;
}
