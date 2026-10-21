/* Cenario da tela Pet (docs/TAREFA_V2_TELA_PET.md). O cenario e a vista 3D do POC (cena3d.ts, decisao do Matheus de 2026-10-19,
   opcao b), carregada por import dinamico ao abrir a tela; sem WebGL, ou se ela falhar, fica a reserva: um quarto 2.5D claro em CSS e
   SVG (parede com janela, paredes laterais em fuga, chao em perspectiva, uma planta e um movel baixo em grade de pixels). Os dois sao
   so decoracao (aria-hidden): nenhum dado do jogo aqui, salvo o dia e a noite do motor e, na cena 3D, o pet. */
import { useEffect, useRef, useState } from "react";
import { CENA } from "./cenaEstado.ts";
import { temWebGL } from "../../webgl.ts";

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

/** a reserva: o quarto em CSS e SVG */
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

/** a M3 pela pagina do jogo: so com ?medir3d=1 no endereco; mede 10 s e mostra o JSON para copiar */
function MedirCena() {
  const [txt, setTxt] = useState<string | null>(null), [medindo, setMedindo] = useState(false);
  const medir = async () => {
    if (!CENA.medir) { setTxt("a cena 3D nao esta ligada (cenario de reserva)"); return; }
    setMedindo(true);
    const m = JSON.stringify(await CENA.medir());
    setMedindo(false); setTxt(m);
    try { await navigator.clipboard.writeText(m); } catch { /* sem area de transferencia: o texto fica na tela para copiar a mao */ }
  };
  return (
    <div className="cena3d-medir">
      <button type="button" className="dl-btn dl-btn--sec" disabled={medindo} onClick={medir}>{medindo ? "Medindo 10 s…" : "Medir 10 s (M3)"}</button>
      {txt && <textarea readOnly value={txt} aria-label="Medida M3" rows={4} />}
    </div>
  );
}
/** o cenario: a cena 3D (import dinamico) ou a reserva */
export function CenaPet({ noite }: { noite: boolean }) {
  const ref = useRef<HTMLCanvasElement>(null), [reserva, setReserva] = useState(() => !temWebGL());
  const medir = new URLSearchParams(location.search).get("medir3d") === "1";
  useEffect(() => {
    if (reserva) return;
    let vivo = true, parar: (() => void) | null = null;
    import("./cena3d.ts")
      .then(m => {
        if (!vivo || !ref.current) return;
        try { parar = m.iniciarCena3D(ref.current, () => setReserva(true)); }
        catch (err) { console.warn("cena 3D do Pet não subiu; fica o cenário de reserva:", err); setReserva(true); }
      })
      .catch(err => { console.warn("cena 3D do Pet não carregou; fica o cenário de reserva:", err); if (vivo) setReserva(true); });
    return () => { vivo = false; parar?.(); };
  }, [reserva]);
  if (reserva) return <CenarioPet noite={noite} />;
  return <>
    <div className={"cena3d" + (noite ? " cena3d--noite" : "")} aria-hidden="true"><canvas ref={ref} /></div>
    {medir && <MedirCena />}
  </>;
}
