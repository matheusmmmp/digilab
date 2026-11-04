/* Luta em andamento (#/lutar/luta; B3, docs/TAREFA_V3_LUTA_LAYOUT.md e docs/pranchas/b3/): a cena a tela inteira, o HUD em caixas (as
   plaquinhas, o relogio, o cartao da regra), a etiqueta do modo e o cartao de contexto no alto, e o dock no rodape (Pausar, x2 e
   Desistir). Sem menu nem abas, rolagem do fundo travada. No fim, o modal Resultado; Continuar volta para a aba de origem (Arena ou
   Campanha) e Ver replay abre a luta no Diario. Desistir (botao ou o Voltar do navegador) pede confirmacao: a luta ja foi decidida e gravada no registro
   quando comecou, entao desistir so pula a animacao e sai. */
import { useEffect, useRef, useState } from "react";
import { abrirModal } from "../../componentes/modal.ts";
import { useJogo } from "../../jogo.ts";
import { LUTA, alternarPausa, alternarRapido, previa, pularAnimacao, reverLuta, sparringTexto, useLuta, type Modo, type Palco } from "../../luta.ts";
import { cartaDe } from "../../../motor/index.ts";
import { ModalResultado } from "./ModalResultado.tsx";
import { PalcoTR } from "./palcoTR/PalcoTR.tsx";
import { BotaoContinuar, BotaoHx } from "../../componentes/hx/index.ts";
import "../../estilo/abertas.css";
import "../../estilo/luta_hud.css";

function ConfirmarDesistir({ ficar, desistir }: { ficar: () => void; desistir: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), saiu = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog className="modal-conf ab-hx dl" ref={ref} aria-labelledby="des-tit" onClose={() => (saiu.current ? desistir() : ficar())}>
      <h2 id="des-tit">Desistir da luta?</h2>
      <p>A luta já foi decidida quando começou e fica no registro. Desistir só pula a animação e volta para a aba de onde você veio.</p>
      <div className="modal-bts">
        <BotaoContinuar data-autofocus onClick={() => ref.current?.close()}>Continuar vendo</BotaoContinuar>
        <BotaoHx tom="perigo" onClick={() => { saiu.current = true; ref.current?.close(); }}>Desistir</BotaoHx>
      </div>
    </dialog>
  );
}

/** fim do replay animado: ver de novo ou voltar ao Diario (Esc volta) */
function FimReplay({ p, deNovo, voltar }: { p: Palco; deNovo: () => void; voltar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), outra = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog className="modal-conf ab-hx dl" ref={ref} aria-labelledby="fim-rep-tit" onClose={() => (outra.current ? deNovo() : voltar())}>
      <h2 id="fim-rep-tit">Fim do replay</h2>
      <p>{p.texto.replace(/^Fim do replay: /, "")} A luta foi refeita do registro; nada foi gravado.</p>
      <div className="modal-bts">
        <BotaoHx onClick={() => { outra.current = true; ref.current?.close(); }}>Ver de novo</BotaoHx>
        <BotaoContinuar data-autofocus onClick={() => ref.current?.close()}>Voltar ao Diário</BotaoContinuar>
      </div>
    </dialog>
  );
}

/** a etiqueta do modo, sob o relogio (no lugar da faixa "Luta · Arena" de antes); o contexto longo vai no cartao ao lado */
export function etiquetaModo(p: Palco, modo: Modo, replay: boolean, sparring: string | null, rivalFixo: boolean): string {
  const base = modo === "arena" ? `Arena · ${rivalFixo ? "cenário" : "treino"}${sparring && !rivalFixo ? ` ${sparring}` : ""}` : modo === "fronteira" ? "Fronteira" : "Campanha";
  const k = p.serie ? ` · Luta ${p.serie.k} de ${p.serie.n}` : p.sequencia ? ` · vitória ${p.sequencia.k}` : "";
  return `${replay ? "Replay · " : ""}${base}${k}${replay ? " · refeita do registro" : ""}`;
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
    <section className="luta-tela ab-hx dl">
      <div className="luta-contexto hud-caixa"><h1 className="luta-modo">Luta</h1></div>
      <div className="luta-vazio hud-caixa">
        <p className="luta-vazia">Nenhuma luta em andamento.</p>
        <BotaoContinuar onClick={() => sair("arena")}>Voltar para a Arena</BotaoContinuar>
      </div>
    </section>
  );
  const sp = sparringTexto(m), rep = luta.replay;
  return (
    <section className="luta-tela ab-hx dl" aria-labelledby="luta-tit">
      <PalcoTR />
      <div className="luta-contexto hud-caixa">
        <h1 className="luta-modo" id="luta-tit">{etiquetaModo(p, modo, rep !== null, sp, LUTA.rivalFixo !== null)}</h1>
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
      </div>
      <div className="luta-dock hud-caixa" role="group" aria-label="Controles da luta">
        {luta.lutando && <>
          <button type="button" className="luta-ctl" aria-label={luta.pausado ? "Continuar a animação" : "Pausar a animação"} aria-pressed={luta.pausado} onClick={alternarPausa}>
            {luta.pausado ? <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3l9 5-9 5z" /></svg> : <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z" /></svg>}</button>
          <button type="button" className="luta-ctl luta-ctl--x2" aria-label="Velocidade dobrada" aria-pressed={luta.rapido} onClick={alternarRapido}>×2</button>
          <span className="luta-dock-sep" aria-hidden="true" /></>}
        {rep !== null
          ? <BotaoHx className="luta-desistir" onClick={() => { pularAnimacao(); sairReplay(rep); }}>Sair do replay</BotaoHx>
          : <BotaoHx tom="perigo" className="luta-desistir" disabled={!luta.lutando} onClick={() => setDesistindo(true)}>Desistir</BotaoHx>}
      </div>
      {rep !== null && p.fimReplay && !luta.lutando && <FimReplay p={p} deNovo={() => reverLuta(rep)} voltar={() => sairReplay(rep)} />}
      {rep === null && p.resultado && !luta.lutando && <ModalResultado p={p} continuar={voltar} verReplay={idx => { previa(modo); verReplay(modo, idx); }} />}
      {desistindo && luta.lutando && <ConfirmarDesistir ficar={() => setDesistindo(false)} desistir={() => { setDesistindo(false); pularAnimacao(); voltar(); }} />}
    </section>
  );
}
