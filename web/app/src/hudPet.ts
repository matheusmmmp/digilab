/* O HUD da tela Pet que aparece e some (o Matheus, 2026-11-04): o resumo do alto ("agora: à toa") e o balão da fala só ficam na tela
   por AVISO_MS depois de mudar, e os dois se arrastam pela tela (a posição fica gravada no navegador, fora do save). A fome: o pet só
   diz que está com fome abaixo de FOME_FALA; abaixo de FOME_EMOTE ele só mostra o emoji da carne sobre a cabeça; acima, nada (o dono
   percebe pelo pet). O "exibir" de cada janela (Estado, Evolução, Últimas ações, DigiBrain, Agora, Minimapa) saiu daqui para o
   janelasPet.ts (JN1, 2026-11-12), no lugar da chave única "Exibir detalhes do pet". Tudo só apresentação: o motor, o log, o chamado e o replay não mudam. PROPOSTO, SEM FONTE. */
import type { PointerEvent as PE, MouseEvent as ME, CSSProperties, RefObject } from "react";
import { useEffect, useRef, useState } from "react";
import type { Chamado, Motor } from "../motor/index.ts";
import { CHAVE } from "./save.ts";

/** quanto tempo o aviso fica na tela depois de mudar (o Matheus, 2026-11-04: 15 s) */
export const AVISO_MS = 15_000;
/** quanto tempo a faixa do resumo (a fome, o Estado) e a linha do agora ficam na tela depois de mudar; depois saem, mesmo com a fome critica
    (o Matheus, 2026-11-08: "quando notifica, deixa eles durante 5 segundos e daí eles saem"). PROPOSTO, SEM FONTE (numero de interface) */
export const NOTIFICA_MS = 5_000;
/** abaixo disso o pet diz que está com fome (texto); abaixo de FOME_EMOTE, só o emoji sobre a cabeça (o Matheus, 2026-11-04) */
export const FOME_FALA = 0.15;
export const FOME_EMOTE = 0.5;

/** os chamados que a tela mostra: o de fome só quando a comida está abaixo de FOME_FALA (o motor continua abrindo e fechando o chamado) */
export function chamadosVisiveis(m: Motor): Chamado[] {
  return m.chamadosAbertos().filter(c => c !== "fome" || m.e.fome < FOME_FALA);
}
/** o emoji da fome sobre a cabeça do pet: comida abaixo de FOME_EMOTE */
export const fomeNoEmote = (m: Motor): boolean => m.e.fome < FOME_EMOTE;

/** visível por `ms` (AVISO_MS) a cada mudança de `chave` (e ao montar); `fixo` deixa visível enquanto valer */
export function useAviso(chave: string, fixo = false, ms = AVISO_MS): boolean {
  const [vis, setVis] = useState(true);
  useEffect(() => {
    setVis(true);
    const t = setTimeout(() => setVis(false), ms);
    return () => clearTimeout(t);
  }, [chave, ms]);
  return vis || fixo;
}

/* ---------- arrastar */
const CHAVE_ARRASTE = CHAVE + "-hud-arraste";
type Desvio = { dx: number; dy: number };
function lerDesvios(): Record<string, Desvio> {
  try { return JSON.parse(localStorage.getItem(CHAVE_ARRASTE) ?? "{}") ?? {}; } catch { return {}; }    /* preferência de tela */
}
function gravarDesvio(id: string, d: Desvio): void {
  try { localStorage.setItem(CHAVE_ARRASTE, JSON.stringify({ ...lerDesvios(), [id]: d })); } catch { /* preferência de tela */ }
}
/** quantos px o ponteiro anda antes de virar arraste (abaixo disso é um toque e o clique passa) */
const LIMIAR_ARRASTE = 6;

/** quem esta montado e arrastavel: "voltar os paineis ao lugar" (Ajustes) zera todos de uma vez */
const ouvintesArraste = new Set<() => void>();
/** os paineis e avisos voltam ao lugar de sempre (apaga as posicoes gravadas no navegador; nada do save) */
export function voltarPaineis(): void {
  try { localStorage.removeItem(CHAVE_ARRASTE); } catch { /* preferência de tela */ }
  for (const o of ouvintesArraste) o();
}
/** ha algum painel ou aviso fora do lugar de sempre */
export function temPainelMovido(): boolean { return Object.values(lerDesvios()).some(d => d.dx || d.dy); }

/** o arraste de `id` sobre o elemento de `ref`; com `alca` (um seletor), so comeca num ponteiro sobre ela (o cabecalho do painel), e o resto do
    painel continua a clicar e a rolar. Um arraste nao vira clique */
function useArraste<T extends HTMLElement>(id: string, ref: RefObject<T | null>, alca?: string, porTranslate = false) {
  const [d, setD] = useState<Desvio>(() => lerDesvios()[id] ?? { dx: 0, dy: 0 });
  useEffect(() => { const o = () => setD({ dx: 0, dy: 0 }); ouvintesArraste.add(o); return () => { ouvintesArraste.delete(o); }; }, []);
  const arr = useRef<{ x: number; y: number; base: Desvio; ret: DOMRect; moveu: boolean; id: number } | null>(null);
  const moveuAgora = useRef(false);
  const onPointerDown = (e: PE<T>) => {
    if (e.button !== 0 || !ref.current) return;
    if (alca && !(e.target instanceof Element && e.target.closest(alca))) return;
    arr.current = { x: e.clientX, y: e.clientY, base: d, ret: ref.current.getBoundingClientRect(), moveu: false, id: e.pointerId };
  };
  const onPointerMove = (e: PE<T>) => {
    const a = arr.current; if (!a || a.id !== e.pointerId) return;
    let mx = e.clientX - a.x, my = e.clientY - a.y;
    if (!a.moveu) {
      if (Math.hypot(mx, my) < LIMIAR_ARRASTE) return;
      a.moveu = true; ref.current?.setPointerCapture(e.pointerId);
    }
    /* não sai da janela */
    mx = Math.min(Math.max(mx, -a.ret.left), innerWidth - a.ret.right);
    my = Math.min(Math.max(my, -a.ret.top), innerHeight - a.ret.bottom);
    setD({ dx: a.base.dx + mx, dy: a.base.dy + my });
  };
  const soltar = (e: PE<T>) => {
    const a = arr.current; if (!a || a.id !== e.pointerId) return;
    arr.current = null;
    if (a.moveu) { moveuAgora.current = true; setD(x => { gravarDesvio(id, x); return x; }); }
  };
  const onClickCapture = (e: ME<T>) => { if (moveuAgora.current) { moveuAgora.current = false; e.preventDefault(); e.stopPropagation(); } };
  /* os paineis usam a propriedade `translate`, que soma com a animacao de entrada (transform) em vez de brigar com ela */
  const style: CSSProperties = !(d.dx || d.dy) ? {} : porTranslate ? { translate: `${Math.round(d.dx)}px ${Math.round(d.dy)}px` }
    : { transform: `translate(${Math.round(d.dx)}px, ${Math.round(d.dy)}px)` };
  return { style, onPointerDown, onPointerMove, onPointerUp: soltar, onPointerCancel: soltar, onClickCapture, "data-arrastavel": "" };
}

/** arrastar o elemento pela tela (o balao da fala, o alerta): devolve o ref, o estilo (translate) e os eventos; um arraste nao vira clique */
export function useArrastavel<T extends HTMLElement>(id: string) {
  const ref = useRef<T>(null);
  return { ref, ...useArraste(id, ref) };
}
/** arrastar um painel pelo cabecalho (`alca`, um seletor dentro dele), com o ref que o painel ja tem (o Matheus, 2026-11-08: "desde que o usuário consiga
    arrastar ou arrumar o layout desses menus"). Devolve o estilo e os eventos para o elemento do painel */
export function useArrastavelPorAlca<T extends HTMLElement>(id: string, ref: RefObject<T | null>, alca: string) {
  return useArraste(id, ref, alca, true);
}
