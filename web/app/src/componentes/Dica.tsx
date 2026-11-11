/* Pecas da regra do texto da L2 (docs/PROPOSTAS_V3_UX_TELA_PET.md, "A regra do texto"): a frase sai da vista e fica num balao que aparece no foco e no
   hover (estilo/lugar.css, .balao) e e lida pelo leitor de tela (aria-describedby); o "Como funciona" fica fechado. O balao esta sempre no DOM
   (display:none): o texto continua no textContent, mas nao conta como texto a vista (innerText).
   - o balao nunca sai do painel: ao aparecer, `ajustarBalao` o empurra para dentro (de lado) ou o vira para cima (embaixo);
   - o Esc com um balao a vista fecha so ele (atalhosLugar.ts poe data-oculto no alvo; ele volta quando o ponteiro ou o foco saem);
   - no toque, o clique no alvo alterna o balao (o primeiro toque o mostra pelo foco, o segundo o esconde). */
import { useId, type FocusEvent, type MouseEvent, type PointerEvent, type ReactNode } from "react";
import { ChevronRight, Info } from "lucide-react";

/** o balao em si; `lado` ajusta de que borda ele sai */
export function Balao({ id, children, lado }: { id: string; children: ReactNode; lado?: "dir" | "cima" }) {
  return <span className={"balao" + (lado ? ` balao--${lado}` : "")} role="tooltip" id={id}>{children}</span>;
}

/** empurra o balao do alvo para dentro do corpo do painel (ou da janela): de lado, e para cima se nao couber embaixo */
export function ajustarBalao(alvo: HTMLElement): void {
  const b = alvo.querySelector<HTMLElement>(":scope > .balao");
  if (!b || getComputedStyle(b).display === "none") return;
  const c = (alvo.closest(".hx-painel__corpo") ?? document.documentElement).getBoundingClientRect();
  const esq = Math.max(c.left, 0), dir = Math.min(c.right, innerWidth), topo = Math.max(c.top, 0), baixo = Math.min(c.bottom, innerHeight);
  b.style.maxWidth = `${Math.max(120, Math.min(300, dir - esq - 24))}px`; b.style.transform = ""; b.style.top = ""; b.style.bottom = "";
  let r = b.getBoundingClientRect();
  if (r.bottom > baixo - 4 && alvo.getBoundingClientRect().top - r.height - 6 >= topo) { b.style.top = "auto"; b.style.bottom = "calc(100% + 6px)"; r = b.getBoundingClientRect(); }
  const dx = r.left < esq + 8 ? esq + 8 - r.left : r.right > dir - 8 ? dir - 8 - r.right : 0;
  if (dx) b.style.transform = `translateX(${Math.round(dx)}px)`;
}
const visivel = (alvo: HTMLElement): boolean => { const b = alvo.querySelector<HTMLElement>(":scope > .balao"); return !!b && getComputedStyle(b).display !== "none"; };

/** os ouvintes do alvo de um balao; `toque`: o clique alterna o balao (nao nos itens, onde o clique equipa) */
export const propsBalao = (toque = true) => ({
  onMouseEnter: (e: MouseEvent<HTMLElement>) => ajustarBalao(e.currentTarget),
  onFocus: (e: FocusEvent<HTMLElement>) => ajustarBalao(e.currentTarget),
  onMouseLeave: (e: MouseEvent<HTMLElement>) => e.currentTarget.removeAttribute("data-oculto"),
  onBlur: (e: FocusEvent<HTMLElement>) => { e.currentTarget.removeAttribute("data-oculto"); e.currentTarget.removeAttribute("data-antes"); },
  ...(toque ? {
    onPointerDown: (e: PointerEvent<HTMLElement>) => { if (e.pointerType === "touch") e.currentTarget.setAttribute("data-antes", visivel(e.currentTarget) ? "1" : "0"); },
    onClick: (e: MouseEvent<HTMLElement>) => {
      const a = e.currentTarget;
      if (a.getAttribute("data-antes") === "1") a.setAttribute("data-oculto", "1");
      a.removeAttribute("data-antes");
    },
  } : {}),
});

/** um alvo focavel (icone, numero, rotulo curto) com a frase no balao; `rotulo` e o que o leitor de tela le no lugar da frase inteira.
    `foco` falso: so o contorno que mostra o balao no hover (o alvo de verdade e um filho, que leva o aria-describedby; `idBalao` e o id dele) */
export function ComDica({ rotulo, dica, lado, className, papel = "group", foco = true, idBalao, children }: {
  rotulo?: string; dica: ReactNode; lado?: "dir" | "cima"; className?: string; papel?: "img" | "group"; foco?: boolean; idBalao?: string; children: ReactNode;
}) {
  const proprio = useId(), id = idBalao ?? proprio;
  return (
    <span className={"dica-alvo" + (foco ? "" : " dica-alvo--sem-foco") + (className ? " " + className : "")} {...(foco ? { tabIndex: 0, role: papel, "aria-label": rotulo, "aria-describedby": id } : {})} {...propsBalao(foco)}>
      {children}<Balao id={id} lado={lado}>{dica}</Balao>
    </span>
  );
}

/** "Como funciona", sempre fechado ao abrir a aba */
export function ComoFunciona({ children }: { children: ReactNode }) {
  return <details className="lg-como"><summary><Info aria-hidden="true" />Como funciona<ChevronRight className="lg-seta" aria-hidden="true" /></summary><p>{children}</p></details>;
}
