/* Cenario da tela Pet (docs/TAREFA_V2_TELA_PET.md): um quarto 2.5D claro, em CSS e SVG, atras do canvas do pet. Parede com janela,
   paredes laterais em fuga, chao em perspectiva, uma planta e um movel baixo. So decoracao: nenhum dado do jogo aqui, salvo o dia
   e a noite do motor. E um componente fechado de proposito: quando o habitat virar o mundo 3D (P4), a vista dele entra no lugar
   deste e o resto da tela nao muda. Os objetos sao desenhados em grade de pixels (image-rendering: pixelated), como o pet. */

/* planta e movel em pixel art: cada letra e uma cor, "." e transparente */
const PLANTA = [
  "....gg......",
  "...gGGg.gg..",
  "..gGGGggGGg.",
  ".gGGgGGGGGg.",
  ".gGg.gGGgGg.",
  "..g..gGg.g..",
  "......g.....",
  "...vvvvvv...",
  "...vVVVVv...",
  "...vVVVVv...",
  "....vVVv....",
  "....vvvv....",
];
const MOVEL = [
  "mmmmmmmmmmmmmmmm",
  "mMMMMMMMMMMMMMMm",
  "mMddddddMddddddm",
  "mMd....dMd....dm",
  "mMddddddMddddddm",
  "mMMMMMMMMMMMMMMm",
  "mm............mm",
];
const COR: Record<string, string> = {
  g: "#3E9A63", G: "#6CCB8B", v: "#7FA6DC", V: "#B9D3F2",
  m: "#9FC2EF", M: "#E3EEFB", d: "#C9DCF4",
};

function Pixels({ grade, className }: { grade: string[]; className: string }) {
  const w = Math.max(...grade.map(l => l.length)), h = grade.length;
  return (
    <svg className={className} viewBox={`0 0 ${w} ${h}`} shapeRendering="crispEdges" aria-hidden="true">
      {grade.flatMap((linha, y) => [...linha].map((c, x) => c === "." ? null : <rect key={`${x}-${y}`} x={x} y={y} width={1} height={1} fill={COR[c]} />))}
    </svg>
  );
}

export function CenarioPet({ noite }: { noite: boolean }) {
  return (
    <div className={"cena-sala" + (noite ? " cena-sala--noite" : "")} aria-hidden="true">
      <div className="cena-parede" />
      <div className="cena-janela">
        <span className="cena-ceu" />
        <span className="cena-nuvem cena-nuvem--1" /><span className="cena-nuvem cena-nuvem--2" /><span className="cena-nuvem cena-nuvem--3" />
        <span className="cena-colinas" />
        <span className="cena-caixilho" />
      </div>
      <div className="cena-lateral cena-lateral--esq" /><div className="cena-lateral cena-lateral--dir" />
      <div className="cena-chao"><div className="cena-piso" /></div>
      <div className="cena-rodape" />
      <Pixels grade={PLANTA} className="cena-planta" />
      <Pixels grade={MOVEL} className="cena-movel" />
    </div>
  );
}
