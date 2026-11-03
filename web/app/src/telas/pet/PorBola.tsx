/* Por a bola num lugar do mundo (docs/TAREFA_V3_HABITAT_OBJETOS.md), como a racao (PorRacao.tsx): em qualquer pet com o mundo fisico,
   pelo evento Motor.deixarBola(x, y) (o "db" do registro) por mudarMotor(). Tres caminhos para o mesmo evento:
   - pegar a bola na cena: o toque em cima dela (a ate RAIO_PEGAR_PX do centro dela na tela) a pega, o arrasto a leva e soltar no chao a
     poe ali; a vista a esconde enquanto ela esta na mao (CENA.bolaNaMao). Um toque sem arrasto nao faz nada;
   - arrastar "Por bola", no menu Mais, ate o chao da cena;
   - o caminho acessivel: tocar ou Enter em "Por bola" a poe perto do pet (o lugar nomeado "perto", vistaMundo.ts).
   Soltar fora do mapa (no ceu, fora da cena) nao gera evento: a tela confere antes, e o motor falha alto se passar. O raio de pegar e do
   desenho: PROPOSTO, SEM FONTE. */
import { useEffect, useRef, useSyncExternalStore, type PointerEvent as ReactPointerEvent, type RefObject } from "react";
import { jogoAtual, mudarMotor } from "../../jogo.ts";
import { CENA } from "./cenaEstado.ts";
import { LIMIAR_ARRASTO, avisarNoDock } from "./PorRacao.tsx";
import { dentroDoMapa, lugaresNomeados, naRegiao } from "./vistaMundo.ts";

/** a distancia do toque ao centro da bola na tela (px de CSS) que ainda a pega */
const RAIO_PEGAR_PX = 34;

/** o fantasma do arrasto (so da tela; nada disso entra no log) */
const ESTADO: { arrasto: { x: number; y: number } | null } = { arrasto: null };
const ouvintes = new Set<() => void>();
let versao = 0;
const mudar = (f: () => void) => { f(); versao++; for (const o of ouvintes) o(); };
function useBola(): typeof ESTADO {
  useSyncExternalStore(o => { ouvintes.add(o); return () => { ouvintes.delete(o); }; }, () => versao);
  return ESTADO;
}

/** poe a bola em (x, y) do mapa, se for uma posicao do mapa; o aviso diz onde (a regiao do layout) */
export function porBolaEm(x: number, y: number): boolean {
  let ok = false;
  try {
    mudarMotor(m => {
      const mu = m.mundo;
      if (!mu) throw new Error("a bola num lugar do mundo é só de pets com o mundo");
      if (!dentroDoMapa(mu.cm, x, y)) { avisarNoDock("Fora do mapa: a bola não foi posta."); return; }
      m.deixarBola(x, y);
      avisarNoDock(`Bola posta ${naRegiao(mu.cm, x)}.`);
      ok = true;
    });
  } catch (err) { avisarNoDock(err instanceof Error ? err.message : String(err)); }
  return ok;
}
/** o ponto do cliente vira a posicao do mapa pela vista; fora do chao, nada */
function porBolaNaTela(cx: number, cy: number): boolean {
  const p = CENA.mundo?.paraMundo(cx, cy) ?? null;
  if (!p) { avisarNoDock("Solte a bola no chão da cena: fora do mapa nada é posto."); return false; }
  return porBolaEm(p[0], p[1]);
}
/** a bola esta sob o ponto do cliente? (o centro dela na tela, pela vista) */
function naBola(cx: number, cy: number): boolean {
  const v = CENA.mundo, { motor: m } = jogoAtual(), mu = m.mundo;
  if (!v || !mu) return false;
  const [bx, by] = v.bola ?? mu.bolaEm(m.e.tick), [tx, ty] = v.paraTela(bx, by);
  return Math.hypot(cx - tx, cy - ty) <= RAIO_PEGAR_PX;
}

/** o icone da bola (vetor original): branca com as duas faixas azuis da bola da ilha */
const IconeBola = ({ tam = 26 }: { tam?: number }) => (
  <svg viewBox="0 0 24 24" width={tam} height={tam} aria-hidden="true">
    <circle cx="12" cy="12" r="9" fill="#fff" stroke="#0F2A66" strokeWidth="1.2" />
    <path d="M3.6 9.5h16.8M3.6 14.5h16.8" stroke="#378ADD" strokeWidth="2.4" />
  </svg>
);
const Fantasma = () => {
  const est = useBola();
  return est.arrasto && <span className="racao-fantasma" style={{ left: est.arrasto.x, top: est.arrasto.y }} aria-hidden="true"><IconeBola tam={34} /></span>;
};

/** pegar a bola na cena: escuta o ponteiro na cena do habitat (`alvo`); so com o pet no mundo */
export function ArrastoBola({ alvo }: { alvo: RefObject<HTMLElement | null> }) {
  useEffect(() => {
    const el = alvo.current;
    if (!el) return;
    let mao: { id: number; x: number; y: number } | null = null;
    const solta = () => { mao = null; CENA.bolaNaMao = false; mudar(() => { ESTADO.arrasto = null; }); };
    const baixo = (e: PointerEvent) => {
      const { motor: m, nascendo } = jogoAtual();
      if (e.button !== 0 || !m.mundo || nascendo > 0 || m.morte || !naBola(e.clientX, e.clientY)) return;
      mao = { id: e.pointerId, x: e.clientX, y: e.clientY };
      el.setPointerCapture(e.pointerId);
      e.preventDefault();
    };
    const move = (e: PointerEvent) => {
      if (!mao || mao.id !== e.pointerId) return;
      if (!ESTADO.arrasto && Math.hypot(e.clientX - mao.x, e.clientY - mao.y) < LIMIAR_ARRASTO) return;
      CENA.bolaNaMao = true;
      mudar(() => { ESTADO.arrasto = { x: e.clientX, y: e.clientY }; });
    };
    const cima = (e: PointerEvent) => {
      if (!mao || mao.id !== e.pointerId) return;
      const arrastou = !!ESTADO.arrasto;
      solta();
      if (arrastou) porBolaNaTela(e.clientX, e.clientY);
    };
    el.addEventListener("pointerdown", baixo); el.addEventListener("pointermove", move);
    el.addEventListener("pointerup", cima); el.addEventListener("pointercancel", solta);
    return () => {
      el.removeEventListener("pointerdown", baixo); el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerup", cima); el.removeEventListener("pointercancel", solta);
      CENA.bolaNaMao = false;
    };
  }, [alvo]);
  return <Fantasma />;
}

/** a barra da bola, no menu Mais: o botao que se arrasta ate o chao, ou que se toca para por a bola perto do pet */
export function BarraBola({ aoUsar }: { aoUsar?: () => void } = {}) {
  const est = useBola(), inicio = useRef<{ x: number; y: number; id: number } | null>(null);
  const perto = () => { const mu = jogoAtual().motor.mundo; if (mu) porBolaEm(...lugaresNomeados(mu).perto); aoUsar?.(); };
  const baixo = (e: ReactPointerEvent<HTMLButtonElement>) => {
    if (e.button !== 0) return;
    inicio.current = { x: e.clientX, y: e.clientY, id: e.pointerId };
    e.currentTarget.setPointerCapture(e.pointerId);
  };
  const move = (e: ReactPointerEvent<HTMLButtonElement>) => {
    const i = inicio.current;
    if (!i || i.id !== e.pointerId) return;
    if (!est.arrasto && Math.hypot(e.clientX - i.x, e.clientY - i.y) < LIMIAR_ARRASTO) return;
    mudar(() => { ESTADO.arrasto = { x: e.clientX, y: e.clientY }; });
  };
  const cima = (e: ReactPointerEvent<HTMLButtonElement>) => {
    const i = inicio.current;
    inicio.current = null;
    if (!i || i.id !== e.pointerId) return;
    if (est.arrasto) { mudar(() => { ESTADO.arrasto = null; }); porBolaNaTela(e.clientX, e.clientY); aoUsar?.(); return; }
    perto();
  };
  const cancelar = () => { inicio.current = null; mudar(() => { ESTADO.arrasto = null; }); };
  return (
    <div className="racao-barra">
      <button type="button" className="hx-btn dock-bt racao-bt bola-bt"
        aria-label="Pôr a bola: arraste até o chão da cena, ou toque para pôr perto do pet"
        onPointerDown={baixo} onPointerMove={move} onPointerUp={cima} onPointerCancel={cancelar}
        onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); perto(); } }}>
        <IconeBola /><span>Pôr bola</span>
      </button>
      <Fantasma />
    </div>
  );
}
