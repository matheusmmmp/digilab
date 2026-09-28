/* Imagens pequenas do atlas (emotes, icones) e das grades originais, em escala inteira, sem suavizar. */
import { imagemAtlas, useAtlas } from "../atlas.ts";
import { imagemGrade, type Paleta } from "../grades.ts";
import { Deco } from "./Deco.tsx";

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

/** retrato de rival com a moldura da arena do UP por cima (sprite pixelado; a moldura e ilustracao); sem a moldura,
    so o sprite, como antes */
export function RetratoRival({ sprite, moldura, lado = 56 }: { sprite: string; moldura: string; lado?: number }) {
  const a = useAtlas();
  const img = a.tipo === "ok" ? imagemAtlas(a, sprite) : null;
  return (
    <span class="retrato-rival" style={{ width: `${lado}px`, height: `${lado}px` }}>
      <span class="retrato-rival-spr">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
      <Deco nome={moldura} class="retrato-rival-moldura" />
    </span>
  );
}
