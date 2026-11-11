/* MITOLOGIA, E0 (docs/TAREFA_V3_MITOLOGIA.md): o oraculo Jijimon fala. So com a chave `mitologia` ligada (Ajustes), fora da luta e das
   telas cheias, e so depois de uma hybris que ele ainda nao contou a este pet: um pedaco da lenda do macaco sob a montanha (motor/lendas.ts),
   na faixa das dicas do Professor Agumon (a mesma pele), com o retrato do bot_oraculo do atlas. Some no "Entendi". */
import { useEffect, useRef, useState } from "react";
import { desenharSprite, dimSprite, escalaSprite, quadroAgora, useAtlas } from "../atlas.ts";
import { falaDoOraculo, NOME_ORACULO, type EventoLenda } from "../../motor/index.ts";
import { useDicaAtual } from "../dicas.ts";
import { useJogo } from "../jogo.ts";
import { hybrisNaoOuvida, ouvirHybris, useMitologia, useOuvidas } from "../mitologia.ts";
import { BotaoContinuar } from "./hx/index.ts";
import "../estilo/abertas.css";

const SPRITE = "bot_oraculo";

function RetratoOraculo() {
  const a = useAtlas(), ref = useRef<HTMLCanvasElement>(null);
  const ok = a.tipo === "ok" && !!a.dados.sprites[SPRITE];
  useEffect(() => {
    if (a.tipo !== "ok" || !ok || !ref.current) return;
    const c = ref.current, esc = escalaSprite(), [w, h] = dimSprite(a.dados, SPRITE);
    c.width = w * esc; c.height = h * esc;
    const g = c.getContext("2d");
    if (!g) return;
    const passo = () => { g.clearRect(0, 0, c.width, c.height); desenharSprite(g, a, SPRITE, 0, 0, esc, quadroAgora(a, SPRITE)); };
    passo();
    const t = setInterval(passo, a.dados.ms_por_quadro);
    return () => clearInterval(t);
  }, [a, ok]);
  if (a.tipo !== "ok" || !ok) return null;
  const [w, h] = dimSprite(a.dados, SPRITE);
  return <canvas ref={ref} className="bit bit-guia" style={{ width: `${w}px`, height: `${h}px` }} aria-hidden="true" />;
}

/** `livre`: a tela Pet esta a vista (fora da luta e das telas cheias) */
export function BalaoOraculo({ livre }: { livre: boolean }) {
  const ligada = useMitologia(), { motor: m, revisao } = useJogo(), ouvidas = useOuvidas(), dica = useDicaAtual();
  const [e, setE] = useState<Extract<EventoLenda, { tipo: "hybris" }> | null>(null);
  /* a faixa e a mesma das dicas: com uma dica do Professor Agumon na frente, o oraculo espera */
  useEffect(() => { setE(ligada && livre && !dica ? hybrisNaoOuvida(m) : null); }, [ligada, livre, dica, m, revisao, ouvidas]);
  if (!e) return null;
  return (
    <aside className="dica-bit ab-hx oraculo-bit" role="status" aria-live="polite" data-testid="oraculo-balao">
      <RetratoOraculo />
      <p><b>{NOME_ORACULO}:</b> {falaDoOraculo(e)}</p>
      <BotaoContinuar className="dica-ok" onClick={() => ouvirHybris(m, e)}>Entendi</BotaoContinuar>
    </aside>
  );
}
