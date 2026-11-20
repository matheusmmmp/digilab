/* Medidor segmentado da pele XCOM. role="meter" com valor e texto equivalente ("N de M", ou "N%" com `porcento`), alem do texto
   visivel opcional; o tom (ok, alerta, perigo) nunca e a unica informacao: o numero acompanha. Com `porcento`, max e 100. */
import clsx from "clsx";

export function MedidorHx({ valor, max, rotulo, tom = "neutro", mostrarTexto = true, porcento = false, className }: {
  valor: number; max: number; rotulo: string; tom?: "neutro" | "ok" | "alerta" | "perigo"; mostrarTexto?: boolean; porcento?: boolean; className?: string;
}) {
  if (!(max > 0) || !Number.isFinite(valor)) throw new Error(`MedidorHx: valor ${valor} e max ${max} invalidos`);
  if (porcento && max !== 100) throw new Error(`MedidorHx: em porcento o max e 100, nao ${max}`);
  const v = Math.min(max, Math.max(0, valor));
  const texto = porcento ? `${Math.round(v)}%` : `${Math.round(v)} de ${Math.round(max)}`;
  return (
    <div className={clsx("hx-medidor", tom !== "neutro" && `hx-medidor--${tom}`, className)}
      role="meter" aria-label={rotulo} aria-valuemin={0} aria-valuemax={max} aria-valuenow={v} aria-valuetext={texto}>
      <span className="hx-medidor__rot" aria-hidden="true">{rotulo}</span>
      <span className="hx-medidor__trilho" aria-hidden="true"><span className="hx-medidor__barra" style={{ display: "block", width: `${(v / max) * 100}%` }} /></span>
      {mostrarTexto && <span className="hx-medidor__txt" aria-hidden="true">{texto}</span>}
    </div>
  );
}
