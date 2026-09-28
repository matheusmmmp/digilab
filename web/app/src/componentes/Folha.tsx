/* Folha (DIRETRIZES_REPLICAR secao 7): no celular sobe de baixo (maximo 85% da altura, alca), com x; tocar fora ou Esc
   fecha e o foco volta a quem abriu. No desktop nao e sobreposta: quem usa mostra o mesmo conteudo na coluna da direita
   da propria aba, e esta folha nao abre. */
import type { ComponentChildren } from "preact";
import { useEffect, useRef } from "preact/hooks";
import { abrirModal } from "./modal.ts";

export function Folha({ titulo, fechar, children }: { titulo: string; fechar: () => void; children: ComponentChildren }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog class="folha folha--info dl" ref={ref} aria-label={titulo} onClose={fechar}
      onClick={e => { if (e.target === ref.current) ref.current?.close(); }}>
      <span class="folha-alca" aria-hidden="true" />
      <div class="folha-topo"><b>{titulo}</b>
        <button type="button" class="folha-x" aria-label="Fechar" onClick={() => ref.current?.close()}>×</button></div>
      <div class="folha-conteudo">{children}</div>
    </dialog>
  );
}
