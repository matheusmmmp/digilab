/* Abas da pele XCOM (padrao WAI-ARIA tablist): setas, Home e End movem e escolhem; so a aba escolhida entra na ordem de Tab.
   O painel da aba fica a cargo de quem usa (role="tabpanel", aria-labelledby = `${idBase}-${id}`). */
import { useRef, type KeyboardEvent } from "react";
import clsx from "clsx";

export interface AbaHx { id: string; rotulo: string }

/** Indice da aba para onde a tecla leva, ou null se a tecla nao navega. Circular nas setas. */
export function indiceAbaPorTecla(tecla: string, atual: number, total: number): number | null {
  if (total <= 0) return null;
  if (tecla === "ArrowRight" || tecla === "ArrowDown") return (atual + 1) % total;
  if (tecla === "ArrowLeft" || tecla === "ArrowUp") return (atual - 1 + total) % total;
  if (tecla === "Home") return 0;
  if (tecla === "End") return total - 1;
  return null;
}

export function AbasHx({ abas, ativa, onMudar, rotulo, idBase = "hx-aba", className }: {
  abas: readonly AbaHx[]; ativa: string; onMudar: (id: string) => void; rotulo: string; idBase?: string; className?: string;
}) {
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  const atual = Math.max(0, abas.findIndex((a) => a.id === ativa));
  function aoTecla(e: KeyboardEvent<HTMLButtonElement>, i: number) {
    const alvo = indiceAbaPorTecla(e.key, i, abas.length);
    if (alvo === null) return;
    e.preventDefault();
    onMudar(abas[alvo].id);
    refs.current[alvo]?.focus();
  }
  return (
    <div className={clsx("hx-abas", className)} role="tablist" aria-label={rotulo}>
      {abas.map((a, i) => (
        <button
          key={a.id} id={`${idBase}-${a.id}`} ref={(el) => { refs.current[i] = el; }} type="button" role="tab" className="hx-aba"
          aria-selected={i === atual} tabIndex={i === atual ? 0 : -1} onClick={() => onMudar(a.id)} onKeyDown={(e) => aoTecla(e, i)}
        >{a.rotulo}</button>
      ))}
    </div>
  );
}
