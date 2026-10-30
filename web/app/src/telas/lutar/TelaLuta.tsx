/* Luta em andamento (#/lutar/luta; DIRETRIZES_REPLICAR secao 7, pranchas UpLuta e BatDesktop): tela cheia, sem menu
   nem abas, rolagem do fundo travada. No fim, o modal Resultado; Continuar volta para a aba de origem (Arena ou
   Campanha) e Ver replay abre a luta no Diario. Desistir (botao ou o Voltar do navegador) pede confirmacao: a luta ja foi decidida e gravada no registro
   quando comecou, entao desistir so pula a animacao e sai. */
import { useEffect, useRef, useState } from "react";
import { abrirModal } from "../../componentes/modal.ts";
import { useJogo } from "../../jogo.ts";
import { LUTA, previa, pularAnimacao, reverLuta, sparringTexto, useLuta, type Modo, type Palco } from "../../luta.ts";
import { NOME_V2, cartaDe } from "../../../motor/index.ts";
import { ModalResultado } from "./ModalResultado.tsx";
import { PalcoTR } from "./palcoTR/PalcoTR.tsx";

function ConfirmarDesistir({ ficar, desistir }: { ficar: () => void; desistir: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), saiu = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog className="modal-conf dl" ref={ref} aria-labelledby="des-tit" onClose={() => (saiu.current ? desistir() : ficar())}>
      <h2 id="des-tit">Desistir da luta?</h2>
      <p>A luta já foi decidida quando começou e fica no registro. Desistir só pula a animação e volta para a aba de onde você veio.</p>
      <div className="modal-bts">
        <button type="button" className="dl-btn dl-btn--sec" onClick={() => ref.current?.close()}>Continuar vendo</button>
        <button type="button" className="dl-btn dl-btn--perigo" onClick={() => { saiu.current = true; ref.current?.close(); }}>Desistir</button>
      </div>
    </dialog>
  );
}

/** fim do replay animado: ver de novo ou voltar ao Diario (Esc volta) */
function FimReplay({ p, deNovo, voltar }: { p: Palco; deNovo: () => void; voltar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), outra = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog className="modal-conf dl" ref={ref} aria-labelledby="fim-rep-tit" onClose={() => (outra.current ? deNovo() : voltar())}>
      <h2 id="fim-rep-tit">Fim do replay</h2>
      <p>{p.texto.replace(/^Fim do replay: /, "")} A luta foi refeita do registro; nada foi gravado.</p>
      <div className="modal-bts">
        <button type="button" className="dl-btn dl-btn--sec" onClick={() => { outra.current = true; ref.current?.close(); }}>Ver de novo</button>
        <button type="button" className="dl-btn" data-autofocus onClick={() => ref.current?.close()}>Voltar ao Diário</button>
      </div>
    </dialog>
  );
}

export function TelaLuta({ sair, verReplay, sairReplay, pedidoDesistir, fecharPedido }: {
  sair: (modo: Modo) => void; verReplay: (modo: Modo, idx: number) => void; sairReplay: (idx: number) => void; pedidoDesistir: boolean; fecharPedido: () => void;
}) {
  const luta = useLuta(), { motor: m } = useJogo(), p = luta.palco, [desistindo, setDesistindo] = useState(false);
  const modo: Modo = p?.modo ?? "arena";
  /* tela cheia: trava a rolagem do fundo enquanto a luta esta aberta */
  useEffect(() => { document.body.classList.add("tela-cheia"); scrollTo(0, 0); return () => document.body.classList.remove("tela-cheia"); }, []);
  useEffect(() => { if (pedidoDesistir) { setDesistindo(true); fecharPedido(); } }, [pedidoDesistir]);
  const voltar = () => { previa(modo); sair(modo); };
  if (!p) return (
    <section className="luta-tela dl">
      <div className="luta-topo dl-faixa"><h1 className="dl-num">Luta</h1></div>
      <p className="luta-vazia">Nenhuma luta em andamento.</p>
      <button type="button" className="dl-btn" onClick={() => sair("arena")}>Voltar para a Arena</button>
    </section>
  );
  const sp = sparringTexto(m), rep = luta.replay;
  return (
    <section className="luta-tela dl" aria-labelledby="luta-tit">
      <div className="luta-topo dl-faixa">
        <h1 className="dl-num" id="luta-tit">{rep !== null ? "Replay" : "Luta"} · {modo === "arena" ? "Arena" : modo === "fronteira" ? "Fronteira" : "Campanha"}</h1>
        <span className="luta-topo-sub">{p.A.nomeTela} × {p.B.nomeTela}{p.serie ? ` · luta ${p.serie.k} de ${p.serie.n}` : p.sequencia ? ` · vitória ${p.sequencia.k}` : ""}{rep !== null ? " · refeita do registro" : sp && modo === "arena" && !LUTA.rivalFixo ? ` · treino ${sp}` : ""}</span>
        {rep !== null
          ? <button type="button" className="dl-btn dl-btn--sec luta-desistir" onClick={() => { pularAnimacao(); sairReplay(rep); }}>Sair do replay</button>
          : <button type="button" className="dl-btn dl-btn--sec luta-desistir" disabled={!luta.lutando} onClick={() => setDesistindo(true)}>Desistir</button>}
      </div>
      {p.sequencia && <p className="luta-arena-aviso luta-serie luta-liga luta-inst" role="status">
        <b>{p.sequencia.inst.nome} · vitória {p.sequencia.k}</b>: {p.B.nomeTela} ({p.B.estiloTela}). {p.sequencia.k - 1} vitória{p.sequencia.k === 2 ? "" : "s"} seguida{p.sequencia.k === 2 ? "" : "s"} até aqui;
        {p.sequencia.k > 1 ? ` sem cura, seu pet começou esta luta com ${Math.round(p.sequencia.vida * 100)}% da vida.` : " sem cura entre as lutas; as cartas não valem."}
        {p.sequencia.inst.regra === "sozinho" ? " No Palácio as suas travas, vetos e chips de regra não valem: o pet decide sozinho." : ""}</p>}
      {p.carta && <p className="luta-arena-aviso luta-carta" role="note" data-testid="luta-carta"><b>{cartaDe(p.carta).nome}</b> em jogo: {cartaDe(p.carta).efeito}</p>}
      {p.serie && p.avisoSerie && <p className="luta-arena-aviso luta-serie" role="status">{p.avisoSerie}</p>}
      {p.serie && !p.avisoSerie && (p.liga
        ? <p className="luta-arena-aviso luta-serie luta-liga" role="status"><b>Liga dos Líderes · luta {p.serie.k} de {p.serie.n}</b>: {p.B.nomeTela}, o Mega de {p.B.estiloTela?.replace(/^.* de /, "")}. Sem cura entre as lutas; as cartas não valem.</p>
        : <p className="luta-arena-aviso luta-serie" role="status"><b>Luta {p.serie.k} de {p.serie.n}</b> · Cidadela: sem cura entre as lutas; a medalha só vem com as {p.serie.n} vitórias.</p>)}
      {p.arena?.regra === "vinculo" && <p className="luta-arena-aviso" role="note"><b>Arena do Lago:</b> aqui as suas travas e vetos não valem. {p.A.nomeTela} decide sozinho, com as regras que ele aprendeu.</p>}
      <PalcoTR />
      {rep !== null && p.fimReplay && !luta.lutando && <FimReplay p={p} deNovo={() => reverLuta(rep)} voltar={() => sairReplay(rep)} />}
      {rep === null && p.resultado && !luta.lutando && <ModalResultado p={p} continuar={voltar} verReplay={idx => { previa(modo); verReplay(modo, idx); }} />}
      {desistindo && luta.lutando && <ConfirmarDesistir ficar={() => setDesistindo(false)} desistir={() => { setDesistindo(false); pularAnimacao(); voltar(); }} />}
    </section>
  );
}
