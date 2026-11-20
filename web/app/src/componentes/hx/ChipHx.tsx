/* Chip da pele XCOM. O tom segue o UI_GUIDELINES §3 e carrega sentido tambem pela forma: aprendido = tracejado, necessidade =
   cheio, alerta = borda dupla, perigo = borda grossa, ok = fina; rotulo e neutro com texto ciano. */
import type { ReactNode } from "react";
import clsx from "clsx";

export type TomChipHx = "neutro" | "rotulo" | "aprendido" | "necessidade" | "ok" | "alerta" | "perigo";

export function ChipHx({ tom = "neutro", className, children }: { tom?: TomChipHx; className?: string; children: ReactNode }) {
  return <span className={clsx("hx-chip", tom !== "neutro" && `hx-chip--${tom}`, className)}>{children}</span>;
}
