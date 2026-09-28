/* Sprite do UP num canvas: escala inteira de pixel do aparelho (UI_GUIDELINES secao 5), idle a ms_por_quadro;
   com prefers-reduced-motion, o primeiro quadro parado. */
import { useEffect, useRef } from "preact/hooks";
import { desenharSprite, dimSprite, useAtlas } from "../atlas.ts";

export function Sprite({ nome, rotulo }: { nome: string; rotulo: string }) {
  const atlas = useAtlas(), ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const cv = ref.current;
    if (!cv || atlas.tipo !== "ok") return;
    const esc = Math.max(1, Math.floor(devicePixelRatio || 1)), [w, h] = dimSprite(atlas.dados, nome);
    cv.width = w * esc; cv.height = h * esc;
    cv.style.width = cv.width / (devicePixelRatio || 1) + "px"; cv.style.height = cv.height / (devicePixelRatio || 1) + "px";
    const ctx = cv.getContext("2d");
    if (!ctx) throw new Error("canvas 2d indisponível");
    const parado = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let i = 0;
    const desenha = () => { ctx.clearRect(0, 0, cv.width, cv.height); desenharSprite(ctx, atlas, nome, 0, 0, esc, i++); };
    desenha();
    if (parado) return;
    const t = setInterval(desenha, atlas.dados.ms_por_quadro);
    return () => clearInterval(t);
  }, [atlas, nome]);
  if (atlas.tipo !== "ok") return <span class="sr-only">{rotulo}</span>;
  return <canvas ref={ref} class="dl-pix" role="img" aria-label={rotulo} />;
}
