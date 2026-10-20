/* O quadro modular do desktop (docs/TAREFA_V2_PET_QUADRO.md; o quadro de modulos do prototipo da tela Pet): duas colunas de modulos,
   cada um com a alca de arrastar, o tracinho azul, o icone e o titulo, o que a tela poe a direita do titulo, o menu (mover para cima,
   para baixo e para a outra coluna) e o chevron de recolher. Os modulos se arrastam entre as colunas (arrastar e soltar do navegador,
   com a linha azul onde vai cair), e o menu faz o mesmo pelo teclado. A coluna da direita inteira tambem se recolhe.
   O arranjo e preferencia de quem joga, nao estado do jogo: fica no localStorage (com try/catch; sem ele, o arranjo padrao) e nao
   toca o motor, o save nem o replay. Este arquivo nao sabe nada do jogo: quem usa diz os modulos e desenha cada um. */
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type DragEvent, type ReactNode } from "react";
import { ArrowDown, ArrowLeftRight, ArrowUp, ChevronDown, EllipsisVertical, GripVertical, PanelRightClose, PanelRightOpen, type LucideIcon } from "lucide-react";

export type Coluna = "principal" | "lado";
export interface Arranjo { principal: string[]; lado: string[]; recolhidos: string[]; ladoRecolhido: boolean }
interface Alvo { coluna: Coluna; indice: number }
const NOME_COLUNA: Record<Coluna, string> = { principal: "coluna principal", lado: "coluna lateral" };

/** o arranjo salvo, se tiver exatamente os modulos de hoje; senao o padrao (falha de leitura tambem cai no padrao) */
function lerArranjo(chave: string, padrao: Arranjo): Arranjo {
  try {
    const raw = JSON.parse(localStorage.getItem(chave) ?? "null") as Partial<Arranjo> | null;
    if (!raw || !Array.isArray(raw.principal) || !Array.isArray(raw.lado)) return padrao;
    const ids = [...raw.principal, ...raw.lado], todos = [...padrao.principal, ...padrao.lado];
    if (ids.length !== todos.length || !todos.every(id => ids.includes(id))) return padrao;
    const recolhidos = Array.isArray(raw.recolhidos) ? raw.recolhidos.filter(id => todos.includes(id)) : padrao.recolhidos;
    return { principal: raw.principal, lado: raw.lado, recolhidos, ladoRecolhido: raw.ladoRecolhido === true };
  } catch {
    return padrao;
  }
}
const local = (a: Arranjo, id: string): Alvo => {
  const coluna: Coluna = a.principal.includes(id) ? "principal" : "lado";
  return { coluna, indice: a[coluna].indexOf(id) };
};

interface ContextoQuadro {
  arranjo: Arranjo; arrastando: string | null; alvo: Alvo | null;
  comecar: (id: string) => void; terminar: () => void; mirar: (a: Alvo) => void; soltar: () => void;
  mover: (id: string, a: Alvo) => void; alternar: (id: string) => void; alternarLado: () => void; abrir: (id: string) => void;
}
const Ctx = createContext<ContextoQuadro | null>(null);
interface Vaga { id: string; coluna: Coluna; indice: number; total: number }
const CtxVaga = createContext<Vaga | null>(null);
function useQuadro(): ContextoQuadro {
  const c = useContext(Ctx);
  if (!c) throw new Error("módulo fora do Quadro");
  return c;
}

/** o quadro: `render` desenha cada modulo (null: o modulo nao existe agora, por exemplo sem dado no motor, e nao aparece); `cresce`
 *  diz os modulos que ocupam a altura que sobra na coluna; `abrirRef` recebe a funcao que expande e mostra um modulo */
export function Quadro({ chave, padrao, render, cresce, abrirRef }: {
  chave: string; padrao: Arranjo; render: (id: string) => ReactNode | null; cresce: readonly string[];
  abrirRef?: { current: ((id: string) => void) | null };
}) {
  const [arranjo, setArranjo] = useState<Arranjo>(() => lerArranjo(chave, padrao));
  const [arrastando, setArrastando] = useState<string | null>(null), [alvo, setAlvo] = useState<Alvo | null>(null);
  useEffect(() => { try { localStorage.setItem(chave, JSON.stringify(arranjo)); } catch { /* sem armazenamento: o arranjo vale so nesta aba */ } }, [chave, arranjo]);
  const mover = useCallback((id: string, a: Alvo) => setArranjo(ant => {
    const de = local(ant, id), nov: Arranjo = { ...ant, principal: [...ant.principal], lado: [...ant.lado] };
    nov[de.coluna].splice(de.indice, 1);
    const i = de.coluna === a.coluna && de.indice < a.indice ? a.indice - 1 : a.indice;
    nov[a.coluna].splice(Math.max(0, Math.min(i, nov[a.coluna].length)), 0, id);
    return nov;
  }), []);
  const terminar = useCallback(() => { setArrastando(null); setAlvo(null); }, []);
  const abrir = useCallback((id: string) => {
    setArranjo(ant => ({ ...ant, ladoRecolhido: ant.lado.includes(id) ? false : ant.ladoRecolhido, recolhidos: ant.recolhidos.filter(r => r !== id) }));
    requestAnimationFrame(() => document.getElementById(`mod-${id}`)?.scrollIntoView({ block: "nearest" }));
  }, []);
  if (abrirRef) abrirRef.current = abrir;
  const valor = useMemo<ContextoQuadro>(() => ({
    arranjo, arrastando, alvo, comecar: setArrastando, terminar, mover, abrir,
    mirar: a => setAlvo(p => p?.coluna === a.coluna && p.indice === a.indice ? p : a),
    soltar: () => { if (arrastando && alvo) mover(arrastando, alvo); terminar(); },
    alternar: id => setArranjo(p => ({ ...p, recolhidos: p.recolhidos.includes(id) ? p.recolhidos.filter(r => r !== id) : [...p.recolhidos, id] })),
    alternarLado: () => setArranjo(p => ({ ...p, ladoRecolhido: !p.ladoRecolhido })),
  }), [arranjo, arrastando, alvo, terminar, mover, abrir]);
  return (
    <Ctx.Provider value={valor}>
      <div className={"quadro" + (arranjo.ladoRecolhido ? " quadro--lado-recolhido" : "")}>
        <ColunaQuadro coluna="principal" render={render} cresce={cresce} />
        <ColunaQuadro coluna="lado" render={render} cresce={cresce} />
      </div>
    </Ctx.Provider>
  );
}

function ColunaQuadro({ coluna, render, cresce }: { coluna: Coluna; render: (id: string) => ReactNode | null; cresce: readonly string[] }) {
  const q = useQuadro(), ids = q.arranjo[coluna], visiveis = ids.map(id => [id, render(id)] as const).filter(([, n]) => n !== null);
  if (coluna === "lado" && q.arranjo.ladoRecolhido) return (
    <div className="quadro-col quadro-col--lado quadro-col--recolhida" role="region" aria-label={NOME_COLUNA.lado}>
      <button type="button" className="quadro-lado-bt" aria-expanded={false} aria-label="Mostrar a coluna lateral" onClick={q.alternarLado}><PanelRightOpen size={20} aria-hidden="true" /></button>
    </div>
  );
  const sobre = (e: DragEvent<HTMLDivElement>) => {
    if (!q.arrastando) return;
    e.preventDefault();
    if (e.target === e.currentTarget) q.mirar({ coluna, indice: ids.length });
  };
  return (
    <div className={`quadro-col quadro-col--${coluna}`} role="region" aria-label={NOME_COLUNA[coluna]} onDragOver={sobre} onDrop={e => { e.preventDefault(); q.soltar(); }}>
      {coluna === "lado" && <button type="button" className="quadro-lado-bt quadro-lado-bt--fechar" aria-expanded={true} aria-label="Recolher a coluna lateral" onClick={q.alternarLado}><PanelRightClose size={18} aria-hidden="true" /></button>}
      {visiveis.map(([id, no]) => {
        const indice = ids.indexOf(id), recolhido = q.arranjo.recolhidos.includes(id);
        const alvo = q.arrastando && q.arrastando !== id ? q.alvo : null;
        const linhaCima = alvo?.coluna === coluna && alvo.indice === indice;
        const linhaBaixo = alvo?.coluna === coluna && alvo.indice === indice + 1 && indice === ids.length - 1;
        return (
          <CtxVaga.Provider key={id} value={{ id, coluna, indice, total: ids.length }}>
            <div className={"quadro-vaga" + (cresce.includes(id) && !recolhido ? " quadro-vaga--cresce" : "")} data-modulo={id}
              onDragOver={e => {
                if (!q.arrastando) return;
                e.preventDefault(); e.stopPropagation();
                const r = e.currentTarget.getBoundingClientRect();
                q.mirar({ coluna, indice: e.clientY < r.top + r.height / 2 ? indice : indice + 1 });
              }}>
              {linhaCima && <span className="quadro-linha quadro-linha--cima" aria-hidden="true" />}
              {no}
              {linhaBaixo && <span className="quadro-linha quadro-linha--baixo" aria-hidden="true" />}
            </div>
          </CtxVaga.Provider>
        );
      })}
      {visiveis.length === 0 && <div className={"quadro-vazio" + (q.arrastando ? " quadro-vazio--alvo" : "")}>Arraste um quadro para cá</div>}
    </div>
  );
}

/** o menu do modulo: mover para cima, para baixo e para a outra coluna (o arrastar pelo teclado) */
function MenuModulo({ titulo }: { titulo: string }) {
  const q = useQuadro(), v = useContext(CtxVaga)!, [aberto, setAberto] = useState(false), ref = useRef<HTMLDivElement>(null);
  const outra: Coluna = v.coluna === "principal" ? "lado" : "principal";
  useEffect(() => {
    if (!aberto) return;
    const fora = (e: Event) => { if (!ref.current?.contains(e.target as Node)) setAberto(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setAberto(false); };
    addEventListener("pointerdown", fora); addEventListener("keydown", esc);
    return () => { removeEventListener("pointerdown", fora); removeEventListener("keydown", esc); };
  }, [aberto]);
  const fazer = (a: Alvo) => { q.mover(v.id, a); setAberto(false); };
  return (
    <div className="mod-menu" ref={ref}>
      <button type="button" className="mod-bt" aria-haspopup="menu" aria-expanded={aberto} aria-label={`Opções do quadro ${titulo}`} onClick={() => setAberto(!aberto)}>
        <EllipsisVertical size={16} aria-hidden="true" /></button>
      {aberto && <div className="mod-menu-lista" role="menu" aria-label={`Mover ${titulo}`}>
        <button type="button" role="menuitem" disabled={v.indice === 0} onClick={() => fazer({ coluna: v.coluna, indice: v.indice - 1 })}><ArrowUp size={16} aria-hidden="true" />Mover para cima</button>
        <button type="button" role="menuitem" disabled={v.indice === v.total - 1} onClick={() => fazer({ coluna: v.coluna, indice: v.indice + 2 })}><ArrowDown size={16} aria-hidden="true" />Mover para baixo</button>
        <button type="button" role="menuitem" onClick={() => fazer({ coluna: outra, indice: q.arranjo[outra].length })}><ArrowLeftRight size={16} aria-hidden="true" />Mover para a {NOME_COLUNA[outra]}</button>
      </div>}
    </div>
  );
}

/** a moldura de um modulo; o cabecalho e a alca de arrastar */
export function Modulo({ icone: Icone, titulo, aside, children }: { icone: LucideIcon; titulo: string; aside?: ReactNode; children: ReactNode }) {
  const q = useQuadro(), v = useContext(CtxVaga);
  if (!v) throw new Error("Modulo fora de uma coluna do Quadro");
  const recolhido = q.arranjo.recolhidos.includes(v.id), corpo = `mod-${v.id}-corpo`, tit = `mod-${v.id}-tit`;
  return (
    <section id={`mod-${v.id}`} className={"mod" + (q.arrastando === v.id ? " mod--arrastando" : "") + (recolhido ? " mod--recolhido" : "")} aria-labelledby={tit}>
      <header className="mod-cab" draggable title="Arraste para reorganizar"
        onDragStart={e => { e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", v.id); q.comecar(v.id); }}
        onDragEnd={q.terminar}>
        <GripVertical className="mod-alca" size={16} aria-hidden="true" />
        <span className="mod-tr" aria-hidden="true" />
        <Icone className="mod-ic" size={20} aria-hidden="true" />
        <h2 id={tit} className="mod-tit">{titulo}</h2>
        <div className="mod-dir">
          {!recolhido && aside}
          <MenuModulo titulo={titulo} />
          <button type="button" className="mod-bt" aria-expanded={!recolhido} aria-controls={corpo} aria-label={recolhido ? `Expandir ${titulo}` : `Recolher ${titulo}`}
            onClick={() => q.alternar(v.id)}><ChevronDown className={"mod-chevron" + (recolhido ? " mod-chevron--fechado" : "")} size={16} aria-hidden="true" /></button>
        </div>
      </header>
      {!recolhido && <div className="mod-corpo" id={corpo}>{children}</div>}
    </section>
  );
}
