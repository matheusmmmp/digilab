/* A camera livre do habitat (o Matheus, 2026-11-01: "como nas POCs dos mapas 3D", poc/mapa_ac e poc/cassette): com a opcao ligada em
   Ajustes > Visual (habitat.ts, controle "livre"), a roda do mouse aproxima e afasta, Shift + roda gira em volta do pet, e arrastar na
   cena gira (de lado) e inclina (para cima e para baixo); no toque, um dedo arrasta e dois dedos aproximam. A camera continua seguindo o
   pet. So vista: fora do save, do registro e do replay; o giro, a inclinacao e o zoom ficam so nesta pagina. Os numeros sao PROPOSTO,
   SEM FONTE (os limites do zoom e da inclinacao e a sensibilidade, perto dos do POC). */
import { CENA } from "./cenaEstado.ts";

/** o giro em volta do pet (rad, 0 = a camera do habitat), a inclinacao somada a dela (rad) e o zoom (fator da distancia: < 1 aproxima) */
export const ORBITA = { giro: 0, inclina: 0, zoom: 1, versao: 0 };
export const ZOOM_MIN = 0.45, ZOOM_MAX = 2.4;
/** a elevacao da camera sobre o chao fica entre estes angulos (rad), qualquer que seja a de partida */
export const ELEVACAO_MIN = 0.12, ELEVACAO_MAX = 1.35;
/** rad por px arrastado, o zoom por unidade de deltaY da roda e o giro por unidade de deltaY com Shift */
const GIRO_POR_PX = 0.008, ZOOM_POR_ROLAGEM = 0.0012, GIRO_POR_ROLAGEM = 0.004;
/** o arrasto so vira giro depois de ARRASTO_MIN px (um toque curto continua sendo toque) */
const ARRASTO_MIN = 6;

const mudou = () => { ORBITA.versao++; };
/** de volta a camera do habitat */
export function recentrar(): void { ORBITA.giro = 0; ORBITA.inclina = 0; ORBITA.zoom = 1; mudou(); }
export function aproximar(fator: number): void { ORBITA.zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, ORBITA.zoom * fator)); mudou(); }
/** gira e inclina; `elevacao0` e a elevacao da camera de partida, para o limite valer na elevacao final */
export function girar(dGiro: number, dInclina: number, elevacao0: number): void {
  ORBITA.giro += dGiro;
  ORBITA.inclina = Math.min(ELEVACAO_MAX - elevacao0, Math.max(ELEVACAO_MIN - elevacao0, ORBITA.inclina + dInclina));
  mudou();
}

/** o deslocamento e o ponto olhado em relacao ao pet, com a orbita aplicada (sem ela, iguais aos da camera do habitat) */
export function aplicarOrbita(desloc: readonly [number, number, number], olhar: readonly [number, number, number]): {
  desloc: [number, number, number]; olhar: [number, number, number]; elevacao0: number;
} {
  const [dx, dy, dz] = desloc, plano = Math.hypot(dx, dz), r = Math.hypot(plano, dy) * ORBITA.zoom;
  const elevacao0 = Math.atan2(dy, plano), e = elevacao0 + ORBITA.inclina, g = Math.atan2(dx, dz) + ORBITA.giro;
  const c = Math.cos(ORBITA.giro), s = Math.sin(ORBITA.giro), [ox, oy, oz] = olhar;
  return {
    desloc: [r * Math.cos(e) * Math.sin(g), r * Math.sin(e), r * Math.cos(e) * Math.cos(g)],
    olhar: [ox * c + oz * s, oy, -ox * s + oz * c],
    elevacao0,
  };
}

/** liga a roda, o arrasto e a pinca na cena (o que cai dentro de .habitat, sem painel por cima); `ativo` diz se a opcao esta ligada.
    Devolve a funcao que desliga */
export function ligarControles(ativo: () => boolean, elevacao0: () => number): () => void {
  const naCena = (e: Event) => ativo() && !CENA.coberto && e.target instanceof Element && !!e.target.closest(".habitat");
  const roda = (e: WheelEvent) => {
    if (!naCena(e)) return;
    e.preventDefault();
    /* Shift + roda: o navegador pode trocar o deltaY pelo deltaX */
    if (e.shiftKey) girar((e.deltaY || e.deltaX) * GIRO_POR_ROLAGEM, 0, elevacao0());
    else aproximar(Math.exp(e.deltaY * ZOOM_POR_ROLAGEM));
  };
  const toques = new Map<number, { x: number; y: number }>();
  let arrasto: { x: number; y: number; andou: boolean } | null = null, pinca: number | null = null;
  const baixo = (e: PointerEvent) => {
    if (!naCena(e) || (e.pointerType === "mouse" && e.button !== 0)) return;
    toques.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (toques.size === 1) arrasto = { x: e.clientX, y: e.clientY, andou: false };
    if (toques.size === 2) { const [a, b] = [...toques.values()]; pinca = Math.hypot(a.x - b.x, a.y - b.y); arrasto = null; }
  };
  const move = (e: PointerEvent) => {
    if (!toques.has(e.pointerId)) return;
    toques.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinca !== null && toques.size === 2) {
      const [a, b] = [...toques.values()], d = Math.hypot(a.x - b.x, a.y - b.y);
      if (d > 0 && pinca > 0) aproximar(pinca / d);
      pinca = d;
      return;
    }
    if (!arrasto) return;
    const dx = e.clientX - arrasto.x, dy = e.clientY - arrasto.y;
    if (!arrasto.andou && Math.hypot(dx, dy) < ARRASTO_MIN) return;
    arrasto.andou = true;
    girar(-dx * GIRO_POR_PX, dy * GIRO_POR_PX, elevacao0());
    arrasto.x = e.clientX; arrasto.y = e.clientY;
  };
  const cima = (e: PointerEvent) => {
    toques.delete(e.pointerId);
    if (toques.size < 2) pinca = null;
    if (toques.size === 0) arrasto = null;
  };
  addEventListener("wheel", roda, { passive: false });
  addEventListener("pointerdown", baixo);
  addEventListener("pointermove", move);
  addEventListener("pointerup", cima);
  addEventListener("pointercancel", cima);
  return () => {
    removeEventListener("wheel", roda);
    removeEventListener("pointerdown", baixo);
    removeEventListener("pointermove", move);
    removeEventListener("pointerup", cima);
    removeEventListener("pointercancel", cima);
  };
}
