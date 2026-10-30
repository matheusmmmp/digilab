/* Painel dos destinos que nao sao o Pet (docs/TAREFA_V2_LAYOUT_HABITAT.md, M2). Abre sobre o habitat, que fica escurecido:
   - a partir de 900 px, painel grande a direita (PainelHx, com as abas do destino no cabecalho) e o pet visivel a esquerda;
   - abaixo de 900 px, modal centralizado (<dialog> com showModal: foco preso e, ao fechar, de volta a quem abriu), com a barra de
     destinos dentro dele (`nav`), porque o resto da pagina fica inerte enquanto o modal esta aberto.
   O "x" (e o Esc) chamam `fechar`, que volta para o Pet. O conteudo entra como cada tela o desenha hoje, numa folha escura de uma coluna (estilo/painel-hx.css, M4); o painel tem no maximo 760 px. */
import { useEffect, useRef, type ReactNode } from "react";
import { AbasHx, PainelHx, type AbaHx } from "./hx/index.ts";
import { abrirModal } from "./modal.ts";
import "../estilo/painel-hx.css";

export interface DadosPainel {
  titulo: string; abas?: readonly AbaHx[]; aba?: string; irAba?: (id: string) => void; fechar: () => void; idBase: string;
}

function Conteudo({ d, fechar, children }: { d: DadosPainel; fechar: () => void; children: ReactNode }) {
  const temAbas = !!d.abas && d.abas.length > 1;
  const abas = temAbas ? <AbasHx abas={d.abas!} ativa={d.aba ?? ""} onMudar={id => d.irAba?.(id)} rotulo={`Abas de ${d.titulo}`} idBase={d.idBase} /> : undefined;
  return (
    <PainelHx titulo={d.titulo} onFechar={fechar} rotuloFechar="Fechar e voltar ao Pet" abas={abas} className="painel-tela__hx">
      <div className="painel-tela__folha dl" role={temAbas ? "tabpanel" : undefined} aria-labelledby={temAbas ? `${d.idBase}-${d.aba}` : undefined}>{children}</div>
    </PainelHx>
  );
}

export function PainelLado({ d, children }: { d: DadosPainel; children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => { ref.current?.focus(); }, []);
  return (
    <div className="painel-tela painel-tela--lado" ref={ref} tabIndex={-1} onKeyDown={e => { if (e.key === "Escape") d.fechar(); }}>
      <Conteudo d={d} fechar={d.fechar}>{children}</Conteudo>
    </div>
  );
}

export function PainelModal({ d, nav, children }: { d: DadosPainel; nav: ReactNode; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null), saindo = useRef(false);
  useEffect(() => {
    const dlg = ref.current; if (!dlg) return;
    saindo.current = false;
    abrirModal(dlg);
    return () => { saindo.current = true; if (dlg.open) dlg.close(); };
  }, []);
  return (
    <dialog className="painel-tela painel-tela--modal" ref={ref} aria-label={d.titulo}
      onClose={e => { if (e.target === e.currentTarget && !saindo.current) d.fechar(); }}
      onClick={e => { if (e.target === ref.current) ref.current?.close(); }}>
      <Conteudo d={d} fechar={() => ref.current?.close()}>{children}</Conteudo>
      {nav}
    </dialog>
  );
}
