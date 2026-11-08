/* O cartao de destrave e o cartao do motivo (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.4 e 4.1; prancha docs/pranchas/ux-lugares-menus/lugar_destravado_*):
   - o DESTRAVE (tipo A): no marco que sobe o nivel, o icone do lugar (lucide), o titulo (ate 3 palavras), a frase (ate 8) e Ir (a camera vai ao lugar) e Depois.
     Entra na fila das dicas (dicas.ts), antes da dica do mesmo momento, so fora da luta e de outra tela cheia; uma vez por nivel. O Esc fecha como o Depois;
   - o MOTIVO: a tecla, a rota ou o toque num lugar trancado abrem este cartao no lugar do painel: o icone, o nome, o "Nv N" com o cadeado e o marco que
     falta ("Abre quando ele virar Rookie"). So o Entendi (e o Esc) o fecha. Nao depende de "Mostrar dicas": quem tocou quer saber.
   So tokens; o visual e o do .dica-bit.ab-hx (abertas.css) com o destaque do --hx-alerta (estilo/nivel.css). So vista. */
import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { Dumbbell, Flag, Heart, Lock, Medal, Package, Shield, Swords, Tent, Trophy, type LucideIcon } from "lucide-react";
import { BotaoContinuar, BotaoHx } from "./hx/index.ts";
import { cartaoDe, nivelDaPeca, PECAS, type IconeNivel } from "../nivel.ts";
import { cartaoVisto, fecharMotivo, useAnuncioNivel, useMotivo } from "../nivelTela.ts";
import { numeroDoCartao, type IdCartao } from "../dicas.ts";
import { ICONE_PECA } from "./iconesNivel.ts";
import type { Rota } from "../rotas.ts";
import "../estilo/nivel.css";

export const ICONE_NIVEL: Record<IconeNivel, LucideIcon> = {
  heart: Heart, tent: Tent, dumbbell: Dumbbell, swords: Swords, package: Package, shield: Shield, medal: Medal, flag: Flag, trophy: Trophy,
};

/** o Esc fecha o cartao (como o Depois) enquanto `ativo`; nao quando outro tratador ja usou a tecla (um balao, o leque do retrato: o dele para a propagacao, entao um Esc
    fecha so o de cima) nem com um dialogo aberto que nao e o dele; o cartao do motivo, mais novo, fecha antes do destrave */
function useEsc(ativo: boolean, fechar: () => void, ref: { current: HTMLElement | null }, motivo = false): void {
  const f = useRef(fechar);
  f.current = fechar;
  useEffect(() => {
    if (!ativo) return;
    const t = (e: KeyboardEvent) => {
      if (e.code !== "Escape" || e.defaultPrevented) return;
      const dlg = document.querySelector("dialog[open]");
      if (dlg && !(ref.current && dlg.contains(ref.current))) return;
      if (!motivo && document.querySelector(".cartao-motivo")) return;
      e.preventDefault(); f.current();
    };
    addEventListener("keydown", t);
    return () => removeEventListener("keydown", t);
  }, [ativo, motivo, ref]);
}

/** o cartao de destrave do marco `id`; `ir` leva a camera ao lugar (a casca navega) */
export function CartaoDestrave({ id, ir }: { id: IdCartao; ir: (r: Rota) => void }) {
  const n = numeroDoCartao(id), c = cartaoDe(n);
  const ref = useRef<HTMLElement>(null), anterior = useRef<HTMLElement | null>(null);
  /* ao fechar pelo teclado o foco volta a quem o tinha antes de entrar no cartao (e nao ao body); o cartao nao rouba o foco ao aparecer */
  const devolver = () => { if (ref.current?.contains(document.activeElement) && anterior.current?.isConnected) anterior.current.focus({ preventScroll: true }); };
  const depois = () => { devolver(); cartaoVisto(n); };
  useEsc(true, depois, ref);
  if (!c) throw new Error("cartao de destrave desconhecido: " + id);
  const I = ICONE_NIVEL[c.icone], titulo = `cd-tit-${n}`;
  return (
    <aside className="dica-bit cartao-destrave ab-hx" role="status" aria-live="polite" aria-labelledby={titulo} data-nivel={n} ref={ref}
      onFocus={e => { if (!e.currentTarget.contains(e.relatedTarget as Node | null)) anterior.current = e.relatedTarget instanceof HTMLElement ? e.relatedTarget : null; }}>
      <span className="cd-ic" aria-hidden="true"><I /></span>
      <div className="cd-txt">
        <span className="cd-nv">Nv {n}</span>
        <b id={titulo}>{c.titulo}</b>
        <span id={`cd-txt-${n}`}>{c.frase}</span>
        <span className="cd-bts">
          {c.rota && <BotaoContinuar className="cd-ir" onClick={() => { cartaoVisto(n); ir(c.rota!); }}>Ir</BotaoContinuar>}
          <BotaoHx className="cd-depois" onClick={depois}>{c.rota ? "Depois" : "Entendi"}</BotaoHx>
        </span>
      </div>
    </aside>
  );
}

/** o aviso de leitor de tela de um lugar que abriu ("Diario aberto"), sempre montado e invisivel; vale tambem sem o cartao (dicas desligadas) */
export function AnuncioNivel() {
  return <div className="sr-only" role="status" aria-live="polite">{useAnuncioNivel()}</div>;
}

/** o cartao do motivo da peca trancada que a tecla, a rota ou o toque tentaram abrir. Com um dialogo aberto (a folha do celular) ele entra DENTRO dele: fora, o dialogo
    modal o deixaria inerte e escondido */
export function CartaoMotivo() {
  const p = useMotivo(), ref = useRef<HTMLElement>(null), opener = useRef<HTMLElement | null>(null), aberto = p !== null;
  /* o foco vai ao Entendi e, so na volta para fechado, volta a quem o tinha (o opener se guarda so na passagem de fechado para aberto) */
  useEffect(() => {
    if (!aberto) return;
    opener.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    ref.current?.querySelector<HTMLElement>("button")?.focus({ preventScroll: true });
    return () => { const o = opener.current; setTimeout(() => { if (o && o.isConnected && o !== document.body) o.focus({ preventScroll: true }); }, 0); };
  }, [aberto]);
  useEsc(aberto, fecharMotivo, ref, true);
  if (!p) return null;
  const d = PECAS[p], I = ICONE_PECA[p];
  const cartao = (
    <aside className="dica-bit cartao-destrave cartao-motivo ab-hx" role="dialog" aria-labelledby="cm-tit" aria-describedby="cm-txt" ref={ref} data-trancado={p}>
      <span className="cd-ic" aria-hidden="true"><I /></span>
      <div className="cd-txt">
        <span className="cd-nv"><Lock aria-hidden="true" />Nv {nivelDaPeca(p)}</span>
        <b id="cm-tit">{d.nome}</b>
        <span id="cm-txt">{d.motivo}.</span>
        <span className="cd-bts"><BotaoHx className="cd-depois" onClick={fecharMotivo}>Entendi</BotaoHx></span>
      </div>
    </aside>
  );
  const dlg = typeof document !== "undefined" ? document.querySelector("dialog[open]") : null;
  return dlg ? createPortal(cartao, dlg) : cartao;
}
