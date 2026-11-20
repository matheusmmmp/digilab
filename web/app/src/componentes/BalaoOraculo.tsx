/* MITOLOGIA (docs/TAREFA_V3_MITOLOGIA.md, E0 e E1): o oraculo Jijimon fala. So com a chave `mitologia` ligada (Ajustes), fora da luta e das
   telas cheias, e so o que ele ainda nao contou a este pet (src/mitologia.ts, proximaFala): um pedaco da lenda depois de uma hybris, e uma
   vez cada um dos segredos da E1 (a pedra achada, as pegadas, o dia 81). Na faixa das dicas do Professor Agumon (a mesma pele), com o retrato
   do bot_oraculo do atlas. Some no "Entendi". */
import { useEffect, useRef, useState } from "react";
import { desenharSprite, dimSprite, escalaSprite, quadroAgora, useAtlas } from "../atlas.ts";
import { NOME_ORACULO } from "../../motor/index.ts";
import { useDicaAtual } from "../dicas.ts";
import { useJogo } from "../jogo.ts";
import { ouvir, proximaFala, useMitologia, useVersaoOuvidas, type FalaOraculo } from "../mitologia.ts";
import { BotaoContinuar } from "./hx/index.ts";
import "../estilo/abertas.css";

const SPRITE = "bot_oraculo";

/** o retrato animado do Jijimon (canvas em escala inteira); sem o atlas, nada */
export function RetratoOraculo() {
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
  const ligada = useMitologia(), { motor: m, revisao } = useJogo(), versao = useVersaoOuvidas(), dica = useDicaAtual();
  const [f, setF] = useState<FalaOraculo | null>(null);
  /* a faixa e a mesma das dicas: com uma dica do Professor Agumon na frente, o oraculo espera */
  useEffect(() => { setF(ligada && livre && !dica ? proximaFala(m) : null); }, [ligada, livre, dica, m, revisao, versao]);
  if (!f) return null;
  return (
    <aside className="dica-bit ab-hx oraculo-bit" role="status" aria-live="polite" data-testid="oraculo-balao" data-fala={f.tipo}>
      <RetratoOraculo />
      <p><b>{NOME_ORACULO}:</b> {f.texto}</p>
      <BotaoContinuar className="dica-ok" onClick={() => ouvir(m, f)}>Entendi</BotaoContinuar>
    </aside>
  );
}
