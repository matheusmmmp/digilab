/* MITOLOGIA, E1 (docs/TAREFA_V3_MITOLOGIA.md, secao 10): o Codice das lendas, no Diario (aba Registro). So com a chave `mitologia`. Mostra o
   que o par ja viveu e o oraculo ja contou: os pedacos da lenda ouvidos, os sinais dos deuses ja vistos e os segredos achados; o que falta
   fica como "???", para instigar a descoberta. O retrato do Jijimon no cabecalho guarda o enigma: 7 toques seguidos. */
import { useRef, useState } from "react";
import {
  CMIT_E1, DEUSES, ENIGMA, FALA_PESSEGO, LENDA_CONTADA, LENDA_DO_MACACO, NOME_DEUS, NOME_ORACULO, SINAL_DEUS, diaDeVida, myotismonJaApareceu,
  pedraAchadaDe, pegadasDe, sinaisDe, tickDoDiaRaro,
} from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import { enigmaResolvidoEm, ouvidasDe, responderEnigma, useMitologia, useVersaoOuvidas } from "../mitologia.ts";
import { RetratoOraculo } from "./BalaoOraculo.tsx";

const TOQUES = 7, JANELA_TOQUES_MS = 3000;
const OCULTO = "???";

export function Codice() {
  const ligada = useMitologia(), { motor: m } = useJogo();
  useVersaoOuvidas();
  const toques = useRef<number[]>([]);
  const [enigma, setEnigma] = useState<"fechado" | "aberto" | "errou" | "acertou">("fechado");
  if (!ligada) return null;
  const o = ouvidasDe(m), tick = m.e.tick;
  const sinais = sinaisDe(m), raroVivido = tick >= tickDoDiaRaro();
  const vezes = (d: (typeof DEUSES)[number]) => sinais.filter(s => s.deus === d && s.tick <= tick).length + (raroVivido ? 1 : 0);
  const pedra = pedraAchadaDe(m), pegadas = pegadasDe(m), resolvido = enigmaResolvidoEm(m);
  const myo = myotismonJaApareceu(m, tick);
  const tocar = () => {
    const agora = performance.now();
    toques.current = [...toques.current.filter(t => agora - t < JANELA_TOQUES_MS), agora];
    if (toques.current.length >= TOQUES) { toques.current = []; setEnigma("aberto"); }
  };
  const dia = (t: number) => `no dia ${diaDeVida(t)}`;
  return (
    <details className="lg-destaque codice" data-testid="codice">
      <summary className="codice-cab">
        <span className="codice-tit">Códice das lendas</span>
        <small>o que vocês dois já viveram, e o que ainda falta</small>
      </summary>
      <div className="codice-corpo">
        <button type="button" className="codice-oraculo" aria-label={`Retrato do ${NOME_ORACULO}`} data-testid="codice-oraculo" onClick={tocar}>
          <RetratoOraculo />
        </button>
        {enigma !== "fechado" && resolvido === null && (
          <section className="codice-enigma" data-testid="codice-enigma" aria-live="polite">
            <p><b>{NOME_ORACULO}:</b> {enigma === "errou" ? ENIGMA.erro : ENIGMA.pergunta}</p>
            <div className="codice-opcoes">
              {ENIGMA.opcoes.map((op, i) => (
                <button type="button" key={op} className="rg2-filtro" onClick={() => setEnigma(responderEnigma(m, i) ? "acertou" : "errou")}>{op}</button>
              ))}
            </div>
          </section>
        )}
        {(enigma === "acertou" || (enigma !== "fechado" && resolvido !== null)) && (
          <p className="codice-enigma" data-testid="codice-enigma" aria-live="polite"><b>{NOME_ORACULO}:</b> {ENIGMA.acerto}</p>
        )}

        <h4>A lenda do macaco</h4>
        <ol className="codice-lenda">
          {LENDA_DO_MACACO.map((t, i) => <li key={i} className={i < o.h ? "" : "codice-oculto"}>{i < o.h ? t : OCULTO}</li>)}
          {o.h > LENDA_DO_MACACO.length && <li className="codice-fecho">{LENDA_CONTADA}</li>}
        </ol>

        <h4>Os sinais dos deuses</h4>
        <ul className="codice-lista">
          {DEUSES.map(d => {
            const n = vezes(d);
            return <li key={d} data-deus={d} className={n ? "" : "codice-oculto"}>
              {n ? <><b>{NOME_DEUS[d]}</b>: {SINAL_DEUS[d]} <small>(visto {n} {n === 1 ? "vez" : "vezes"})</small></> : <>{OCULTO} <small>um deus que ainda não olhou para vocês</small></>}
            </li>;
          })}
        </ul>

        <h4>Os segredos</h4>
        <ul className="codice-lista">
          <li className={pedra !== null && pedra <= tick ? "" : "codice-oculto"}>
            {pedra !== null && pedra <= tick ? <><b>A pedra do macaco</b>: achada {dia(pedra)}, numa noite, na mata</> : <>{OCULTO} <small>algo na mata só se mostra no escuro</small></>}</li>
          <li className={pegadas !== null && pegadas <= tick ? "" : "codice-oculto"}>
            {pegadas !== null && pegadas <= tick ? <><b>As pegadas</b>: apareceram {dia(pegadas)}, de tanto explorar; levam do ninho até a mata</> : <>{OCULTO} <small>quem anda muito por um lugar acaba deixando marca</small></>}</li>
          <li className={resolvido !== null ? "" : "codice-oculto"}>
            {resolvido !== null ? <><b>O enigma</b>: decifrado {dia(resolvido)}; {FALA_PESSEGO}</> : <>{OCULTO} <small>o velho gosta de quem insiste</small></>}</li>
          <li className={raroVivido ? "" : "codice-oculto"}>
            {raroVivido ? <><b>O dia {CMIT_E1.diaRaro}</b>: os cinco olharam ao mesmo tempo</> : <>{OCULTO} <small>um dia que vale por muitos</small></>}</li>
          <li className={myo ? "" : "codice-oculto"}>
            {myo ? <><b>A sombra que gosta de repetição</b>: o Myotismon já escureceu a ilha; variar devolve a luz</> : <>{OCULTO} <small>nem todo deus mora na roda</small></>}</li>
        </ul>
      </div>
    </details>
  );
}
