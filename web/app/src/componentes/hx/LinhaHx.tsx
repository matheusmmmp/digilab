/* Linha de lista da pele XCOM: caixa de borda fina. Sem onClick e um <div>; com onClick, um <button> (aria-pressed se `escolhida`
   for dada). `secundario` e o texto do canto direito (valor, estado). */
import type { ReactNode } from "react";
import clsx from "clsx";

export function LinhaHx({ children, secundario, onClick, escolhida, className }: {
  children: ReactNode; secundario?: ReactNode; onClick?: () => void; escolhida?: boolean; className?: string;
}) {
  const miolo = <>{children}{secundario !== undefined && <span className="hx-linha__sec">{secundario}</span>}</>;
  if (!onClick) return <div className={clsx("hx-linha", className)} aria-current={escolhida ? "true" : undefined}>{miolo}</div>;
  return (
    <button type="button" className={clsx("hx-linha", className)} onClick={onClick} aria-pressed={escolhida === undefined ? undefined : escolhida}>
      {miolo}
    </button>
  );
}
