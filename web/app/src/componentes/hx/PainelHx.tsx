/* Painel da pele XCOM (TAREFA_V2_LAYOUT_HABITAT, M1): titulo condensado em caixa alta com faixa de hachura e, se houver
   onFechar, o botao quadrado "×". As abas (AbasHx) entram em `abas`, no cabecalho. */
import { useId, type ReactNode } from "react";
import clsx from "clsx";

export function PainelHx({ titulo, onFechar, rotuloFechar = "Fechar", abas, className, children }: {
  titulo: string; onFechar?: () => void; rotuloFechar?: string; abas?: ReactNode; className?: string; children?: ReactNode;
}) {
  const id = useId();
  return (
    <section className={clsx("hx-painel", className)} aria-labelledby={id}>
      <header className="hx-painel__cab">
        <h2 id={id} className="hx-painel__titulo">{titulo}</h2>
        {abas}
        {onFechar && (
          <button type="button" className="hx-quad" aria-label={rotuloFechar} onClick={onFechar}>
            <span aria-hidden="true">×</span>
          </button>
        )}
      </header>
      <div className="hx-painel__corpo">{children}</div>
    </section>
  );
}
