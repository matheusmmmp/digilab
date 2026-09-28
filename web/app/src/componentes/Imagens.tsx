/* Imagens pequenas do atlas (emotes, icones) e das grades originais, em escala inteira, sem suavizar. */
import { imagemAtlas, useAtlas } from "../atlas.ts";
import { imagemGrade, type Paleta } from "../grades.ts";

/** peca ou sprite do atlas; sem atlas, o texto alternativo (ou nada) */
export function Peca({ nome, escala = 1, alt = "", reserva = "" }: { nome: string; escala?: number; alt?: string; reserva?: string }) {
  const a = useAtlas();
  if (a.tipo !== "ok") return reserva ? <>{reserva}</> : null;
  const { url, w, h } = imagemAtlas(a, nome, escala);
  return <img class="dl-pix" src={url} width={w} height={h} alt={alt} />;
}
export function Grade({ grade, escala, cores, alt }: { grade: string[]; escala: number; cores: Paleta; alt: string }) {
  const { url, w, h } = imagemGrade(grade, escala, cores);
  return <img class="dl-pix" src={url} width={w} height={h} alt={alt} />;
}
