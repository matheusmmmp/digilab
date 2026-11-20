/* O botão só de ícone da tela Pet no celular (docs/PROPOSTAS_V3_UX_TELA_PET.md, "Mobile mínimo", M1-9): o nome dele aparece num balão ao segurar o dedo
   (SEGURAR_MS, movel.ts; só com o toque), ao passar o mouse ou a caneta (hover) e no foco do teclado (:focus-visible); some ao soltar, sair ou desfocar.
   O balão é só desenho (aria-hidden): o nome acessível continua o de sempre (aria-label, ou o texto em sr-only). É só informativo: nenhum clique é
   suprimido, o toque longo também dispara a ação (como o Pôr ração e a bola). */
import { forwardRef, useEffect, useMemo, useRef, useState, type ButtonHTMLAttributes, type FocusEvent, type MouseEvent, type PointerEvent, type ReactNode } from "react";
import { Segurador } from "../movel.ts";

export type LadoRotulo = "cima" | "baixo" | "esq" | "dir";

/** o toque longo, o hover (mouse, caneta) e o foco do teclado de um elemento; `props` vai no elemento */
export function useSegurar() {
  const [segurando, setSegurando] = useState(false), [foco, setFoco] = useState(false), [hover, setHover] = useState(false);
  const seg = useMemo(() => new Segurador(setSegurando), []), tipo = useRef("mouse");
  useEffect(() => () => seg.parar(), [seg]);
  const props = {
    onPointerDown: (e: PointerEvent<HTMLElement>) => { tipo.current = e.pointerType; if (e.button === 0) seg.baixo(e.pointerType); },
    onPointerUp: () => seg.parar(), onPointerCancel: () => seg.parar(),
    onPointerEnter: (e: PointerEvent<HTMLElement>) => { if (e.pointerType !== "touch") setHover(true); },
    onPointerLeave: () => { seg.parar(); setHover(false); },
    /* o menu de contexto do toque longo do celular (e da caneta) nao abre: so o mouse tem o botao direito de verdade */
    onContextMenu: (e: MouseEvent<HTMLElement>) => { if (tipo.current !== "mouse") e.preventDefault(); },
    onFocus: (e: FocusEvent<HTMLElement>) => { setFoco(e.currentTarget.matches(":focus-visible")); },
    onBlur: () => setFoco(false),
  };
  return { visivel: segurando || foco || hover, props };
}

export const Rotulo = ({ texto, lado }: { texto: string; lado: LadoRotulo }) => (
  <span className="mm-rotulo" data-lado={lado} aria-hidden="true">{texto}</span>
);

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** o nome que o balão mostra; sem `aria-label`, ele é também o nome acessível (em sr-only) */
  rotulo: string;
  lado?: LadoRotulo;
  children?: ReactNode;
}
export const BotaoMovel = forwardRef<HTMLButtonElement, Props>(function BotaoMovel({ rotulo, lado = "cima", className, children, ...resto }, ref) {
  const s = useSegurar();
  return (
    <button type="button" ref={ref} className={className} {...s.props} {...resto}>
      {children}
      {resto["aria-label"] === undefined && <span className="sr-only">{rotulo}</span>}
      {s.visivel && <Rotulo texto={rotulo} lado={lado} />}
    </button>
  );
});

/** um grupo que não é um botão (a barra do Pôr ração e do Pôr a bola, que tratam o ponteiro por conta própria): só mostra o nome */
export function Segura({ rotulo, lado = "cima", className, children }: { rotulo: string; lado?: LadoRotulo; className?: string; children: ReactNode }) {
  const s = useSegurar();
  return <div className={className} {...s.props}>{children}{s.visivel && <Rotulo texto={rotulo} lado={lado} />}</div>;
}
