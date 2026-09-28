/* Luta em andamento (#/lutar/luta; DIRETRIZES_REPLICAR secao 7, pranchas UpLuta e BatDesktop): tela cheia, sem menu
   nem abas, rolagem do fundo travada. No fim, o modal Resultado; Continuar volta para a aba de origem (Arena ou
   Campanha) e Ver replay abre a luta no Diario. Desistir (botao ou o Voltar do navegador) pede confirmacao: a luta ja foi decidida e gravada no registro
   quando comecou, entao desistir so pula a animacao e sai. */
import { useEffect, useRef, useState } from "preact/hooks";
import { abrirModal } from "../../componentes/modal.ts";
import { useJogo } from "../../jogo.ts";
import { LUTA, previa, pularAnimacao, sparringTexto, useLuta, type Modo } from "../../luta.ts";
import { ModalResultado } from "./ModalResultado.tsx";
import { PalcoLuta } from "./PalcoLuta.tsx";

function ConfirmarDesistir({ ficar, desistir }: { ficar: () => void; desistir: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), saiu = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog class="modal-conf dl" ref={ref} aria-labelledby="des-tit" onClose={() => (saiu.current ? desistir() : ficar())}>
      <h2 id="des-tit">Desistir da luta?</h2>
      <p>A luta já foi decidida quando começou e fica no registro. Desistir só pula a animação e volta para a aba de onde você veio.</p>
      <div class="modal-bts">
        <button type="button" class="dl-btn dl-btn--sec" onClick={() => ref.current?.close()}>Continuar vendo</button>
        <button type="button" class="dl-btn dl-btn--perigo" onClick={() => { saiu.current = true; ref.current?.close(); }}>Desistir</button>
      </div>
    </dialog>
  );
}

export function TelaLuta({ sair, verReplay, pedidoDesistir, fecharPedido }: { sair: (modo: Modo) => void; verReplay: (modo: Modo, idx: number) => void; pedidoDesistir: boolean; fecharPedido: () => void }) {
  const luta = useLuta(), { motor: m } = useJogo(), p = luta.palco, [desistindo, setDesistindo] = useState(false);
  const modo: Modo = p?.modo ?? "arena";
  /* tela cheia: trava a rolagem do fundo enquanto a luta esta aberta */
  useEffect(() => { document.body.classList.add("tela-cheia"); scrollTo(0, 0); return () => document.body.classList.remove("tela-cheia"); }, []);
  useEffect(() => { if (pedidoDesistir) { setDesistindo(true); fecharPedido(); } }, [pedidoDesistir]);
  const voltar = () => { previa(modo); sair(modo); };
  if (!p) return (
    <section class="luta-tela dl">
      <div class="luta-topo dl-faixa"><h1 class="dl-num">Luta</h1></div>
      <p class="luta-vazia">Nenhuma luta em andamento.</p>
      <button type="button" class="dl-btn" onClick={() => sair("arena")}>Voltar para a Arena</button>
    </section>
  );
  const sp = sparringTexto(m);
  return (
    <section class="luta-tela dl" aria-labelledby="luta-tit">
      <div class="luta-topo dl-faixa">
        <h1 class="dl-num" id="luta-tit">Luta · {modo === "arena" ? "Arena" : "Campanha"}</h1>
        <span class="luta-topo-sub">{p.A.nomeTela} × {p.B.nomeTela}{sp && modo === "arena" && !LUTA.rivalFixo ? ` · treino ${sp}` : ""}</span>
        <button type="button" class="dl-btn dl-btn--sec luta-desistir" disabled={!luta.lutando} onClick={() => setDesistindo(true)}>Desistir</button>
      </div>
      <PalcoLuta />
      {p.resultado && !luta.lutando && <ModalResultado p={p} continuar={voltar} verReplay={idx => { previa(modo); verReplay(modo, idx); }} />}
      {desistindo && luta.lutando && <ConfirmarDesistir ficar={() => setDesistindo(false)} desistir={() => { setDesistindo(false); pularAnimacao(); voltar(); }} />}
    </section>
  );
}
