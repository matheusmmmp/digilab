/* O painel de um lugar da ilha (L2 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md; prancha em docs/pranchas/ux-lugares-menus/): hoje so
   Crescer, no saco de pancada. A ilha segue viva em volta (sem veu):
   - a partir de 900 px, o painel fica ao lado do saco (a direita dele), entrando em PAINEL_MS;
   - abaixo de 900 px, uma folha que sobe da base (<dialog>: foco preso, Esc e toque fora fecham), com a alca, o icone e o nome do menu, o lugar e o
     "x" "Fechar e voltar ao Pet"; o corpo rola.
   As abas sao em icone (so a escolhida mostra o rotulo; o nome vai no aria-label e numa dica no foco e no hover). O corpo de cada aba e o mesmo
   nas duas larguras. Os outros destinos seguem no PainelTela.tsx, sem mudar. */
import { useEffect, useRef, type ReactNode } from "react";
import { AbasHx, PainelHx, type AbaHx } from "./hx/index.ts";
import { abrirModal } from "./modal.ts";
import "../estilo/lugar.css";

export interface DadosLugar {
  titulo: string; sub: string; icone: ReactNode; abas: readonly AbaHx[]; aba: string; irAba: (id: string) => void; fechar: () => void; idBase: string;
}

function Conteudo({ d, fechar, folha, children }: { d: DadosLugar; fechar: () => void; folha: boolean; children: ReactNode }) {
  const abas = <AbasHx abas={d.abas} ativa={d.aba} onMudar={d.irAba} rotulo={`Abas de ${d.titulo}`} idBase={d.idBase} className="lugar-abas" />;
  return (
    <>
      {folha && <span className="lugar-alca" aria-hidden="true" />}
      <PainelHx titulo={d.titulo} sub={d.sub} icone={d.icone} onFechar={fechar} rotuloFechar="Fechar e voltar ao Pet" abas={abas} className="painel-tela__hx lugar__hx">
        <div className="painel-tela__folha dl" role="tabpanel" aria-labelledby={`${d.idBase}-${d.aba}`}>{children}</div>
      </PainelHx>
    </>
  );
}

/** de 900 px em diante: o painel ao lado do saco */
export function LugarLado({ d, children }: { d: DadosLugar; children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  /* ao fechar, o foco volta a quem abriu o lugar (se ainda estiver na pagina; depois do foco que o App poe no trilho) */
  useEffect(() => {
    const antes = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    ref.current?.focus({ preventScroll: true });
    return () => { setTimeout(() => { if (antes && antes !== document.body && antes.isConnected) antes.focus(); }, 90); };
  }, []);
  return (
    <div className="painel-tela painel-tela--lugar painel-tela--lugar-lado" ref={ref} tabIndex={-1} onKeyDown={e => { if (e.key === "Escape" && !e.defaultPrevented && !(e.target instanceof Element && e.target.closest("dialog"))) d.fechar(); }}>
      <Conteudo d={d} fechar={d.fechar} folha={false}>{children}</Conteudo>
    </div>
  );
}

/** abaixo de 900 px: a folha que sobe da base */
export function LugarFolha({ d, children }: { d: DadosLugar; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null), saindo = useRef(false);
  useEffect(() => {
    const dlg = ref.current; if (!dlg) return;
    saindo.current = false;
    abrirModal(dlg);
    /* o foco inicial vai para a aba escolhida (o showModal poria na primeira, e a dica dela cobriria o corpo) */
    dlg.querySelector<HTMLElement>('[role="tab"][aria-selected="true"]')?.focus({ preventScroll: true });
    return () => { saindo.current = true; if (dlg.open) dlg.close(); };
  }, []);
  return (
    <dialog className="painel-tela painel-tela--lugar painel-tela--lugar-folha" ref={ref} aria-label={d.titulo}
      onClose={e => { if (e.target === e.currentTarget && !saindo.current) d.fechar(); }}
      onClick={e => { if (e.target === ref.current) ref.current?.close(); }}>
      <Conteudo d={d} fechar={() => ref.current?.close()} folha>{children}</Conteudo>
    </dialog>
  );
}
