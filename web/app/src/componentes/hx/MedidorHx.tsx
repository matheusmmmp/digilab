/* Medidor segmentado da pele XCOM. role="meter" com valor e texto equivalente ("N de M"), alem do texto visivel opcional;
   o tom (ok, alerta, perigo) nunca e a unica informacao: o numero acompanha. */
import clsx from "clsx";

export function MedidorHx({ valor, max, rotulo, tom = "neutro", mostrarTexto = true, className }: {
  valor: number; max: number; rotulo: string; tom?: "neutro" | "ok" | "alerta" | "perigo"; mostrarTexto?: boolean; className?: string;
}) {
  if (!(max > 0) || !Number.isFinite(valor)) throw new Error(`MedidorHx: valor ${valor} e max ${max} invalidos`);
  const v = Math.min(max, Math.max(0, valor));
  const texto = `${Math.round(v)} de ${Math.round(max)}`;
  return (
    <div className={clsx("hx-medidor", tom !== "neutro" && `hx-medidor--${tom}`, className)}
      role="meter" aria-label={rotulo} aria-valuemin={0} aria-valuemax={max} aria-valuenow={v} aria-valuetext={texto}>
      <span className="hx-medidor__rot" aria-hidden="true">{rotulo}</span>
      <span className="hx-medidor__trilho" aria-hidden="true"><span className="hx-medidor__barra" style={{ display: "block", width: `${(v / max) * 100}%` }} /></span>
      {mostrarTexto && <span className="hx-medidor__txt" aria-hidden="true">{texto}</span>}
    </div>
  );
}
