/* Professor Agumon, o mentor do tutorial (docs/JORNADA_JOGADOR.md; antes "Bit"): desde 2026-09-28 (pedido do Matheus) e o Agumon de capelo
   de professor do Digimon UP ("Agu", grupo B: falando e apontando a varinha), sprite "guia" do atlas. Sem o atlas,
   volta o robozinho desenhado em pixels aqui mesmo. A faixa da dica fica acima da barra, uma frase por vez. */
import { useEffect, useRef } from "react";
import { desenharSprite, dimSprite, escalaSprite, quadroAgora, useAtlas } from "../atlas.ts";
import { dispensarDica, DICAS, NOME_MENTOR, useDicaAtual } from "../dicas.ts";

/* 12 x 12: . vazio, n contorno, b corpo, c visor, o olho, a antena, y luz, w chave */
const GRADE = [
  ".....a......",
  ".....y......",
  "...nnnnnn...",
  "..nbbbbbbn..",
  "..nccccccn..",
  "..ncoccocn..",
  "..nccccccn..",
  "..nbbbbbbn.w",
  ".nbbnbbnbbnw",
  ".nb.nbbn.bw.",
  "..nnnnnnnn..",
  "...nn..nn...",
];
const COR: Record<string, string> = { n: "#173A8A", b: "#9FC2EF", c: "#0F2A66", o: "#6FE3FF", a: "#173A8A", y: "#FFD23F", w: "#8A98B8" };

export function RetratoBit({ tam = 40 }: { tam?: number }) {
  return (
    <svg className="bit" viewBox="0 0 12 12" width={tam} height={tam} aria-hidden="true" shapeRendering="crispEdges">
      {GRADE.flatMap((l, y) => [...l].map((c, x) => (COR[c] ? <rect key={`${x}-${y}`} x={x} y={y} width="1" height="1" fill={COR[c]} /> : null)))}
    </svg>
  );
}

/** o Agumon professor animado (canvas em escala inteira do aparelho); sem o atlas ou sem o sprite, o robozinho */
export function RetratoGuia() {
  const a = useAtlas(), ref = useRef<HTMLCanvasElement>(null);
  const ok = a.tipo === "ok" && !!a.dados.sprites.guia;
  useEffect(() => {
    if (a.tipo !== "ok" || !ok || !ref.current) return;
    const c = ref.current, esc = escalaSprite(), [w, h] = dimSprite(a.dados, "guia");
    c.width = w * esc; c.height = h * esc;
    const g = c.getContext("2d");
    if (!g) return;
    const passo = () => { g.clearRect(0, 0, c.width, c.height); desenharSprite(g, a, "guia", 0, 0, esc, quadroAgora(a, "guia")); };
    passo();
    const t = setInterval(passo, a.dados.ms_por_quadro);
    return () => clearInterval(t);
  }, [a, ok]);
  if (a.tipo !== "ok" || !ok) return <RetratoBit />;
  const [w, h] = dimSprite(a.dados, "guia");
  return <canvas ref={ref} className="bit bit-guia" style={{ width: `${w}px`, height: `${h}px` }} aria-hidden="true" />;
}

export function DicaBit() {
  const id = useDicaAtual();
  if (!id) return null;
  return (
    <aside className="dica-bit" role="status" aria-live="polite">
      <RetratoGuia />
      <p><b>{NOME_MENTOR}:</b> {DICAS[id]}</p>
      <button type="button" className="dl-btn dl-btn--sec dica-ok" onClick={() => dispensarDica(id)}>Entendi</button>
    </aside>
  );
}
