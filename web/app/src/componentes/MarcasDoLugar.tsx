/* O que fica a vista dentro do lugar a partir de 900 px (L2 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md, "Sempre visivel x por gesto"):
   o minimapa da L1 (so mostra: a camera esta no lugar), a placa "Saco de pancada" presa acima do saco e o conector tracejado do saco ate a borda do
   painel. A posicao do saco na tela sai da projecao que a vista publica (CENA.mundo.paraTela e VISTA.atual.saco), lida a cada quadro e escrita direto
   no estilo (sem setState por quadro). Placa e conector sao so desenho (aria-hidden): o nome do lugar ja esta no cabecalho do painel. So vista. */
import { useEffect, useRef } from "react";
import { Sprout } from "lucide-react";
import { useJogo } from "../jogo.ts";
import { VISTA } from "../telas/pet/cameraLivre.ts";
import { Minimapa } from "../telas/pet/Minimapa.tsx";
import { petChama } from "../telas/pet/CameraHud.tsx";

/** a altura da placa acima do pe do saco, em celulas na distancia do ponto olhado. PROPOSTO, SEM FONTE (numero de interface, nao de jogo) */
const PLACA_ALTURA_CELULAS = 2.5;

export function MarcasDoLugar() {
  const { motor: m, nascendo } = useJogo(), placa = useRef<HTMLSpanElement>(null), linha = useRef<SVGPathElement>(null), ponta = useRef<SVGCircleElement>(null);
  const vivo = nascendo === 0 && !m.morte;
  useEffect(() => {
    let pedido = 0, painel: Element | null = null, ultimo = "";
    const laco = () => {
      pedido = requestAnimationFrame(laco);
      /* a posicao do saco na tela vem pronta da vista, depois da camera do quadro (VISTA.atual.sacoTela): aqui so se le e se escreve o que mudou */
      const v = VISTA.atual, el = placa.current;
      if (!v?.sacoTela || !el || !linha.current || !ponta.current) return;
      if (!painel?.isConnected) painel = document.querySelector(".painel-tela--lugar-lado");
      if (!painel) return;
      const [sx, sy] = v.sacoTela, y = sy - v.pxPorCelula * PLACA_ALTURA_CELULAS, borda = painel.getBoundingClientRect();
      const chave = `${Math.round(sx)}|${Math.round(y)}|${Math.round(borda.left)}|${Math.round(borda.top)}|${Math.round(borda.bottom)}`;
      if (chave === ultimo) return;
      ultimo = chave;
      el.style.transform = `translate(${Math.round(sx - el.offsetWidth / 2)}px, ${Math.round(y - el.offsetHeight)}px)`;
      /* do centro do saco ate a borda esquerda do painel, na altura da placa (dentro do painel) */
      const yl = Math.min(borda.bottom - 24, Math.max(borda.top + 24, y));
      linha.current.setAttribute("d", `M${sx} ${y} L${sx} ${yl} L${borda.left} ${yl}`);
      ponta.current.setAttribute("cx", String(sx)); ponta.current.setAttribute("cy", String(y));
    };
    pedido = requestAnimationFrame(laco);
    return () => cancelAnimationFrame(pedido);
  }, []);
  return (
    <>
      <div className="lugar-mini" aria-hidden="true"><Minimapa soMostra chama={vivo && petChama(m)} /></div>
      <span className="lugar-placa" ref={placa} aria-hidden="true"><Sprout />Saco de pancada</span>
      <svg className="lugar-conector" aria-hidden="true"><path ref={linha} /><circle ref={ponta} r="3" /></svg>
    </>
  );
}
