/* A tela da luta da POC (LUTA_POC, LP3): a luta em tempo real na tela inteira, com o palco 2D (desenhoPoc.ts), o HUD das peles de hoje (as
   plaquinhas com a vida e o dano atrasado da E5, a carga da habilidade, o relogio) e o cartao do mapa com a regra dele. O pet luta sozinho;
   no rodape, o dock da tela de antes (TelaLuta.tsx; decisao do Matheus de 2026-11-09): Pausar, x2 e Desistir (com a confirmacao), ou Sair
   do replay. No fim, o resultado com Ver replay e Continuar; no fim do replay, Ver de novo e Continuar. */
import { useEffect, useReducer, useRef, useState } from "react";
import { CENAS, LIMITE_POC_MS } from "../../../../motor/index.ts";
import { atlasAtual, imagemAtlas, useAtlas } from "../../../atlas.ts";
import { abrirModal } from "../../../componentes/modal.ts";
import { BotaoContinuar, BotaoHx } from "../../../componentes/hx/index.ts";
import {
  LUTA_POC, alternarPausaPoc, alternarRapidoPoc, fecharPalcoPoc, pularAnimacaoPoc, useLutaPoc, verReplayPoc, type PalcoPoc,
} from "../../../lutaPocTela.ts";
import { falhasMapa, ouvirMapas } from "../palcoTR/cenasTR.ts";
import { relogio } from "../palcoTR/PalcoTR.tsx";
import { arquivosPoc, desenharLutaPoc, type LadoDesenhoPoc } from "./desenhoPoc.ts";
import { efeitosAtuais, falhasEfeito, ouvirEfeitos } from "./efeitosJogo.ts";
import { barraDoPasso, passoDe, type LadoN } from "./visualPoc.ts";
import "../../../estilo/abertas.css";
import "../../../estilo/luta_hud.css";
import "../../../estilo/luta_poc.css";

/** um lado do HUD: o retrato, o nome, a vida (com o pedaco atrasado da E5) e a carga da habilidade */
function Lado({ p, i }: { p: PalcoPoc; i: LadoN }) {
  const a = useAtlas(), D: LadoDesenhoPoc = i ? p.B : p.A, u = i ? p.L.b : p.L.a, img = a.tipo === "ok" ? imagemAtlas(a, D.sprite) : null;
  const passoV = passoDe(p.L) + p.v.extra, at = barraDoPasso(p.v.vidas[i], passoV), hp = Math.max(0, u.hp);
  const carga = Math.max(0, Math.min(1, 1 - u.recSk / (u.st.hcd * 1000))), rot = i ? "do rival" : "do seu pet";
  return (
    <div className={`hud-lado hud-caixa${i ? " hud-lado--rival" : ""}`} title={D.nomeTela} data-testid={`poc-lado-${i}`}>
      <span className="hud-ret">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
      <span className="hud-txt">
        <span className="hud-nome">{D.nomeTela}<span className="sr-only"> {hp} de {u.st.hp} de vida</span></span>
        <span className="hud-vida" role="img" aria-label={`vida ${rot}`}>
          {at && at.rastro > hp && <b className={`hud-vida-atraso${at.branco ? " hud-vida-atraso--branco" : ""}`} data-testid={`poc-atraso-${i}`}
            style={{ width: `${Math.max(0, Math.min(1, at.rastro / u.st.hp)) * 100}%` }} />}
          <i style={{ width: `${Math.max(0, hp / u.st.hp * 100)}%` }} /></span>
        <span className="hud-guts" role="img" aria-label={`habilidade ${rot}: ${carga >= 1 ? "pronta" : `${Math.round(carga * 100)}%`}`}><i style={{ width: `${carga * 100}%` }} /></span>
      </span>
    </div>
  );
}

/** a confirmacao do Desistir, a mesma da tela de antes (TelaLuta.tsx) */
function ConfirmarDesistir({ ficar, desistir }: { ficar: () => void; desistir: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), saiu = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog className="modal-conf ab-hx dl" ref={ref} aria-labelledby="poc-des-tit" onClose={() => (saiu.current ? desistir() : ficar())} data-testid="poc-desistir-conf">
      <h2 id="poc-des-tit">Desistir da luta?</h2>
      <p>A luta já foi decidida quando começou e fica no registro. Desistir só pula a animação e volta para a aba de onde você veio.</p>
      <div className="modal-bts">
        <BotaoContinuar data-autofocus onClick={() => ref.current?.close()}>Continuar vendo</BotaoContinuar>
        <BotaoHx tom="perigo" onClick={() => { saiu.current = true; ref.current?.close(); }}>Desistir</BotaoHx>
      </div>
    </dialog>
  );
}

/** o resultado: so depois da luta. Ver replay mostra a mesma luta de novo; Continuar fecha a tela. No fim de um replay: Ver de novo */
function Resultado({ p, replay, continuar }: { p: PalcoPoc; replay: boolean; continuar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), rever = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  if (!p.fim) return null;
  const fechar = () => { if (rever.current) { rever.current = false; verReplayPoc(); } else continuar(); };
  return (
    <dialog className="modal-conf ab-hx dl poc-resultado" ref={ref} aria-labelledby="poc-res-tit" onClose={fechar} data-testid="poc-resultado">
      <h2 id="poc-res-tit">{replay ? "Fim do replay" : p.fim.titulo}</h2>
      <p>{replay ? `${p.fim.texto} ${/nada foi gravado/.test(p.fim.texto) ? "A luta foi refeita da mesma entrada." : "A luta foi refeita do registro; nada foi gravado."}` : p.fim.texto}</p>
      <div className="modal-bts">
        <BotaoHx className="res-replay" data-testid="poc-ver-replay" onClick={() => { rever.current = true; ref.current?.close(); }}>{replay ? "Ver de novo" : "Ver replay"}</BotaoHx>
        <BotaoContinuar data-autofocus onClick={() => { ref.current?.close(); continuar(); }}>Continuar</BotaoContinuar>
      </div>
    </dialog>
  );
}

/** o palco: o canvas a tela inteira, desenhado a cada quadro do navegador a partir do estado de agora (a luta anda no lutaPocTela.ts) */
function Palco() {
  const ref = useRef<HTMLCanvasElement>(null), a = useAtlas(), [, redesenhar] = useReducer((x: number) => x + 1, 0);
  useEffect(() => { const s = [ouvirMapas(redesenhar), ouvirEfeitos(redesenhar)]; return () => s.forEach(f => f()); }, []);
  useEffect(() => {
    const cv = ref.current; if (!cv) return;
    let id = 0;
    const quadro = () => {
      const p = LUTA_POC.palco, at = atlasAtual();
      if (p) desenharLutaPoc(cv, { L: p.L, v: p.v, A: p.A, B: p.B }, at.tipo === "ok" ? at : null);
      id = requestAnimationFrame(quadro);
    };
    quadro();
    return () => cancelAnimationFrame(id);
  }, [a.tipo]);
  const p = LUTA_POC.palco!;
  return <canvas ref={ref} className="arena-cv" width={96} height={48} role="img" aria-label={`Luta: ${p.A.nomeTela} contra ${p.B.nomeTela}, no ${CENAS[p.cena].nome}`} data-testid="poc-canvas" />;
}

export function TelaLutaPoc({ sair }: { sair: () => void }) {
  const luta = useLutaPoc(), p = luta.palco, a = useAtlas(), [desistindo, setDesistindo] = useState(false);
  useEffect(() => { document.body.classList.add("tela-cheia"); scrollTo(0, 0); return () => document.body.classList.remove("tela-cheia"); }, []);
  if (!p) return null;
  const cena = CENAS[p.cena], faltamMapa = arquivosPoc(p.cena).filter(x => falhasMapa.has(x)), ef = efeitosAtuais();
  const seg = Math.floor(p.L.relogio / 1000), aviso = p.v.avisos[p.v.avisos.length - 1];
  const continuar = () => { fecharPalcoPoc(); sair(); };
  return (
    <section className="luta-tela luta-tela--poc ab-hx dl" aria-labelledby="poc-tit" data-testid="luta-poc" data-lutando={luta.lutando ? "1" : "0"}>
      <div className="palco-luta dl">
        <section className="luta-arena luta-arena--poc" aria-label="Palco da luta" data-cena={p.cena}>
          <Palco />
          <div className="luta-hud">
            <Lado p={p} i={0} />
            <div className="hud-meio hud-caixa">
              <div className="turno-hex" aria-label="tempo da luta"><small>TEMPO</small><b className="dl-num" data-testid="poc-relogio">{relogio(seg)}</b></div>
              <span className="luta-dist">até {relogio(Math.round(LIMITE_POC_MS / 1000))}</span>
            </div>
            <Lado p={p} i={1} />
          </div>
          {p.L.fim && (p.L.a.morto || p.L.b.morto) && <span className="sr-only" role="status">Nocaute!</span>}
          {a.tipo === "erro" && <p className="luta-aviso-asset" role="alert">O atlas dos sprites não carregou ({a.erro}): a luta aparece com marcadores no lugar dos Digimon.</p>}
          {faltamMapa.length > 0 && <p className="luta-aviso-asset" role="alert">O mapa não carregou ({faltamMapa.join(", ")}): a luta aparece no chão liso.</p>}
          {(ef.tipo === "erro" || falhasEfeito.size > 0) && <p className="luta-aviso-asset" role="alert">Os efeitos do jogo não carregaram ({ef.tipo === "erro" ? ef.erro : [...falhasEfeito].slice(0, 3).join(", ")}): os golpes aparecem só com o brilho do elemento.</p>}
        </section>
        <div className="palco-luta-baixo">
          <section className="hud-caixa luta-card" aria-live="polite"><h2>O mapa</h2>
            <div className="luta-regra-card dl-malha">
              <span className="luta-regra-topo"><span className="luta-regra-cab">{cena.nome.toUpperCase()}</span></span>
              <span className="luta-regra-txt" data-testid="poc-regra">{aviso ? aviso.txt : cena.desc}</span></div>
          </section>
        </div>
      </div>
      <div className="luta-contexto hud-caixa">
        <h1 className="luta-modo" id="poc-tit">{p.contexto}{p.rotulo ? ` · ${p.rotulo}` : ""}</h1>
      </div>
      <div className="luta-dock hud-caixa" role="group" aria-label="Controles da luta" data-testid="poc-dock">
        {luta.lutando && <>
          <button type="button" className="luta-ctl" aria-label={luta.pausado ? "Continuar a animação" : "Pausar a animação"} aria-pressed={luta.pausado} onClick={alternarPausaPoc}>
            {luta.pausado ? <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3l9 5-9 5z" /></svg> : <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z" /></svg>}</button>
          <button type="button" className="luta-ctl luta-ctl--x2" aria-label="Velocidade dobrada" aria-pressed={luta.rapido} onClick={alternarRapidoPoc}>×2</button>
          <span className="luta-dock-sep" aria-hidden="true" /></>}
        {luta.replay
          ? <BotaoHx className="luta-desistir" onClick={() => { pularAnimacaoPoc(); continuar(); }}>Sair do replay</BotaoHx>
          : <BotaoHx tom="perigo" className="luta-desistir" disabled={!luta.lutando} onClick={() => setDesistindo(true)}>Desistir</BotaoHx>}
      </div>
      {p.fim && !luta.lutando && <Resultado key={luta.replay ? "r" : "l"} p={p} replay={luta.replay} continuar={continuar} />}
      {desistindo && luta.lutando && <ConfirmarDesistir ficar={() => setDesistindo(false)} desistir={() => { setDesistindo(false); pularAnimacaoPoc(); continuar(); }} />}
    </section>
  );
}
