/* Bit, o zelador do laboratorio (mentor original do tutorial, docs/JORNADA_JOGADOR.md): um robozinho de manutencao
   desenhado em pixels aqui mesmo (nao e sprite da franquia). A faixa da dica fica acima da barra, uma frase por vez. */
import { dispensarDica, DICAS, useDicaAtual } from "../dicas.ts";

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
    <svg class="bit" viewBox="0 0 12 12" width={tam} height={tam} aria-hidden="true" shape-rendering="crispEdges">
      {GRADE.flatMap((l, y) => [...l].map((c, x) => (COR[c] ? <rect key={`${x}-${y}`} x={x} y={y} width="1" height="1" fill={COR[c]} /> : null)))}
    </svg>
  );
}

export function DicaBit() {
  const id = useDicaAtual();
  if (!id) return null;
  return (
    <aside class="dica-bit" role="status" aria-live="polite">
      <RetratoBit />
      <p><b>Bit:</b> {DICAS[id]}</p>
      <button type="button" class="dl-btn dl-btn--sec dica-ok" onClick={() => dispensarDica(id)}>Entendi</button>
    </aside>
  );
}
