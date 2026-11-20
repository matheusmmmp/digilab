/* Barras do guia (secao 7.4 e 7.5) e formatos de numero (virgula, pt-BR). */
import { CDJ } from "../../motor/index.ts";

export const blocos = (v: number, m: number): number => Math.max(0, Math.min(m, Math.round(v * m)));
export const dec = (v: number, d: number): string => v.toFixed(d).replace(".", ",");
export const comSinal = (v: number, d: number): string => (v >= 0 ? "+" : "") + dec(v, d);
/** rotulo relativo ao pet comum (guia 7.5): so fora da faixa comum */
export const rotuloRel = (v: number): string => Math.abs(v) < CDJ.limiarTom ? "na faixa comum" : v >= .6 ? "muito acima" : v > 0 ? "acima" : v <= -.6 ? "muito abaixo" : "abaixo";

/** barra segmentada: n de m blocos; marca opcional (limite ou inicio da faixa) */
export function Seg({ n, m, cls = "", marca }: { n: number; m: number; cls?: string; marca?: number | number[] }) {
  return (
    <span className={`dl-seg ${cls}`} role="img" aria-label={`${n} de ${m}`}>
      {Array.from({ length: m }, (_, i) => <i key={i} className={i < n ? "on" : ""} />)}
      {marca !== undefined && ([] as number[]).concat(marca).map(x => <b key={x} style={{ left: `${x / m * 100}%` }} />)}
    </span>
  );
}
/** barra relativa ao pet comum: v em [-1, 1], 0 = pet comum; rotulo so fora da faixa comum */
export function BarraCarater({ eixo, v }: { eixo: string; v: number }) {
  const rot = Math.abs(v) < CDJ.limiarTom ? "" : rotuloRel(v), f = (Math.max(-1, Math.min(1, v)) + 1) / 2;
  return (
    <div className="dl-rel">
      <span style={{ minWidth: "6.5em" }}>{eixo}</span>
      <span className="dl-rel-trilho" role="img" aria-label={`${eixo}: ${rot || "na faixa comum"}`}><i style={{ width: `${f * 100}%` }} /><b /></span>
      <span className="dl-rel-rotulo">{rot}</span>
    </div>
  );
}
/** numeros em blocos: valor em cima, rotulo embaixo (como o HTML); itens sao [rotulo, valor] */
export function Numeros({ itens }: { itens: [string, string | number][] }) {
  return <div className="kv">{itens.map(([k, v]) => <div key={k}><b>{v}</b><span>{k}</span></div>)}</div>;
}
