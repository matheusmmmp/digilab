/* Por a racao num lugar do mundo (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2; prancha docs/estilo_up/pranchas/MundoComida390.html): so
   nos pets v12, com o mundo fisico. Dois caminhos para o mesmo evento, Motor.deixarComida("racao", x, y) por mudarMotor():
   - o gesto: arrastar "Por racao" e soltar no chao da cena; o ponto vira a posicao do mapa pela vista (CENA.mundo.paraMundo, a cena 3D ou
     a reserva). Soltar fora do mapa (no ceu, fora da cena) nao gera evento: a tela confere antes, e o motor falha alto se passar;
   - o caminho acessivel (MV-4): tocar em "Por racao" abre a faixa; tocar no chao poe ali, ou um lugar nomeado (o comedouro, perto do pet,
     longe; vistaMundo.ts) pelo teclado. Esc ou Cancelar fecham sem por nada.
   O botao Alimentar continua como reserva temporaria (poe a racao no comedouro), descrito assim na tela. */
import { useEffect, useRef, useSyncExternalStore, type PointerEvent as ReactPointerEvent } from "react";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { CENA } from "./cenaEstado.ts";
import { NOME_LUGAR, dentroDoMapa, lugaresNomeados, naRegiao, type Lugar } from "./vistaMundo.ts";

/** o estado da interacao (so da tela; nada disso entra no log): escolhendo o lugar, o fantasma do arrasto e a ultima mensagem */
const ESTADO: { escolhendo: boolean; arrasto: { x: number; y: number } | null; mensagem: string } = { escolhendo: false, arrasto: null, mensagem: "" };
const ouvintes = new Set<() => void>();
let versao = 0;
const mudar = (f: () => void) => { f(); versao++; for (const o of ouvintes) o(); };
function useRacao(): typeof ESTADO {
  useSyncExternalStore(o => { ouvintes.add(o); return () => { ouvintes.delete(o); }; }, () => versao);
  return ESTADO;
}
/** o arrasto so comeca depois de 6 px: antes disso e um toque (abre a faixa) */
const LIMIAR_ARRASTO = 6;

/** poe a racao em (x, y) do mapa, se for uma posicao do mapa; a mensagem diz onde (a regiao do layout) */
export function porRacaoEm(x: number, y: number): boolean {
  let ok = false;
  mudar(() => {
    ESTADO.escolhendo = false;
    try {
      mudarMotor(m => {
        const mu = m.mundo;
        if (!mu) throw new Error("a ração num lugar do mundo é só de pets v12");
        if (!dentroDoMapa(mu.cm, x, y)) { ESTADO.mensagem = "Fora do mapa: nada foi posto."; return; }
        m.deixarComida("racao", x, y);
        ESTADO.mensagem = `Ração posta ${naRegiao(mu.cm, x)}.`;
        ok = true;
      });
    } catch (err) { ESTADO.mensagem = err instanceof Error ? err.message : String(err); }
  });
  return ok;
}
/** o ponto do cliente vira a posicao do mapa pela vista; fora do chao, nada */
function porRacaoNaTela(cx: number, cy: number): boolean {
  const p = CENA.mundo?.paraMundo(cx, cy) ?? null;
  if (!p) { mudar(() => { ESTADO.mensagem = "Solte a ração no chão da cena: fora do mapa nada é posto."; }); return false; }
  return porRacaoEm(p[0], p[1]);
}

/** o icone da racao (vetor original) */
const IconeRacao = ({ tam = 26 }: { tam?: number }) => (
  <svg viewBox="0 0 24 24" width={tam} height={tam} aria-hidden="true"><ellipse cx="12" cy="15" rx="9" ry="5" fill="#9B6A3C" /><ellipse cx="12" cy="12" rx="6" ry="3" fill="#C08A55" /></svg>
);

/** a barra da racao, acima das acoes: o botao que se arrasta ou se toca, e a mensagem do ultimo lugar */
export function BarraRacao() {
  const est = useRacao(), inicio = useRef<{ x: number; y: number; id: number } | null>(null);
  const baixo = (e: ReactPointerEvent<HTMLButtonElement>) => {
    if (e.button !== 0) return;
    inicio.current = { x: e.clientX, y: e.clientY, id: e.pointerId };
    e.currentTarget.setPointerCapture(e.pointerId);
  };
  const move = (e: ReactPointerEvent<HTMLButtonElement>) => {
    const i = inicio.current;
    if (!i || i.id !== e.pointerId) return;
    if (!est.arrasto && Math.hypot(e.clientX - i.x, e.clientY - i.y) < LIMIAR_ARRASTO) return;
    mudar(() => { ESTADO.arrasto = { x: e.clientX, y: e.clientY }; ESTADO.escolhendo = false; });
  };
  const cima = (e: ReactPointerEvent<HTMLButtonElement>) => {
    const i = inicio.current;
    inicio.current = null;
    if (!i || i.id !== e.pointerId) return;
    if (est.arrasto) { mudar(() => { ESTADO.arrasto = null; }); porRacaoNaTela(e.clientX, e.clientY); return; }
    mudar(() => { ESTADO.escolhendo = !ESTADO.escolhendo; ESTADO.mensagem = ""; });
  };
  const cancelar = () => { inicio.current = null; mudar(() => { ESTADO.arrasto = null; }); };
  return (
    <div className="racao-barra">
      <button type="button" className={`dl-btn dl-btn--sec racao-bt${est.escolhendo ? " racao-bt--ativo" : ""}`} aria-pressed={est.escolhendo}
        aria-label="Pôr ração: arraste até o chão da cena, ou toque e escolha o lugar"
        onPointerDown={baixo} onPointerMove={move} onPointerUp={cima} onPointerCancel={cancelar}
        onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); mudar(() => { ESTADO.escolhendo = !ESTADO.escolhendo; ESTADO.mensagem = ""; }); } }}>
        <IconeRacao /><span>Pôr ração</span>
      </button>
      <span className="racao-dica" aria-live="polite">{est.mensagem || "Arraste até o chão, ou toque e escolha o lugar. Alimentar é a reserva: põe no comedouro."}</span>
      {est.arrasto && <span className="racao-fantasma" style={{ left: est.arrasto.x, top: est.arrasto.y }} aria-hidden="true"><IconeRacao tam={34} /></span>}
    </div>
  );
}

/** por cima da cena, enquanto se escolhe o lugar: a faixa com os lugares nomeados e o toque no chao */
export function FaixaRacao() {
  const est = useRacao(), { motor: m } = useJogo(), primeiro = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!est.escolhendo) return;
    primeiro.current?.focus();
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") mudar(() => { ESTADO.escolhendo = false; }); };
    document.addEventListener("keydown", esc);
    return () => document.removeEventListener("keydown", esc);
  }, [est.escolhendo]);
  const mu = m.mundo;
  if (!est.escolhendo || !mu) return null;
  const lugares = lugaresNomeados(mu);
  return (
    <>
      <span className="racao-toque" aria-hidden="true" onPointerUp={e => porRacaoNaTela(e.clientX, e.clientY)} />
      <div className="racao-faixa" role="group" aria-label="Pôr a ração">
        <b>Toque no chão para pôr a ração</b>
        <div className="racao-lugares">
          {(Object.keys(lugares) as Lugar[]).map((l, i) => (
            <button type="button" key={l} ref={i === 0 ? primeiro : undefined} className="dl-btn dl-btn--sec racao-lugar" data-lugar={l}
              onClick={() => porRacaoEm(...lugares[l])}>{NOME_LUGAR[l]}</button>
          ))}
          <button type="button" className="dl-btn dl-btn--sec racao-lugar" onClick={() => mudar(() => { ESTADO.escolhendo = false; })}>Cancelar</button>
        </div>
      </div>
    </>
  );
}

/** o que o motor diz do mundo, no canto da cena: a regiao do pet e quanta racao ha no chao */
export function InfoMundo() {
  const { motor: m } = useJogo(), mu = m.mundo;
  if (!mu) return null;
  const n = [...mu.comidas.values()].filter(c => mu.situacao(c, m.e.tick) !== null).length;
  return <span className="mundo-info">{naRegiao(mu.cm, mu.pet[0])} · {n === 0 ? "nenhuma ração no chão" : n === 1 ? "1 ração no chão" : `${n} rações no chão`}</span>;
}
