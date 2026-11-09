/* A tela da luta da POC (LUTA_POC, LP3): a luta em tempo real na tela inteira, com o palco 2D (desenhoPoc.ts), o HUD das peles de hoje (as
   plaquinhas com a vida e o dano atrasado da E5, a carga da habilidade, o relogio) e o cartao do mapa com a regra dele. Nenhum botao durante
   a luta, no desktop e no celular: o pet luta sozinho e o dono assiste. No fim, o resultado e Continuar. */
import { useEffect, useReducer, useRef } from "react";
import { CENAS, LIMITE_POC_MS } from "../../../../motor/index.ts";
import { atlasAtual, imagemAtlas, useAtlas } from "../../../atlas.ts";
import { abrirModal } from "../../../componentes/modal.ts";
import { BotaoContinuar } from "../../../componentes/hx/index.ts";
import { LUTA_POC, fecharPalcoPoc, useLutaPoc, type PalcoPoc } from "../../../lutaPocTela.ts";
import { falhasMapa, ouvirMapas } from "../palcoTR/cenasTR.ts";
import { relogio } from "../palcoTR/PalcoTR.tsx";
import { arquivosPoc, desenharLutaPoc, type LadoDesenhoPoc } from "./desenhoPoc.ts";
import { efeitosAtuais, falhasEfeito, ouvirEfeitos } from "./efeitosJogo.ts";
import { barraDoPasso, passoDe, type LadoN } from "./visualPoc.ts";
import "../../../estilo/abertas.css";
import "../../../estilo/luta_hud.css";

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

/** o resultado: so depois da luta (Continuar fecha a tela) */
function Resultado({ p, continuar }: { p: PalcoPoc; continuar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  if (!p.fim) return null;
  return (
    <dialog className="modal-conf ab-hx dl poc-resultado" ref={ref} aria-labelledby="poc-res-tit" onClose={continuar} data-testid="poc-resultado">
      <h2 id="poc-res-tit">{p.fim.titulo}</h2>
      <p>{p.fim.texto}</p>
      <div className="modal-bts"><BotaoContinuar data-autofocus onClick={() => ref.current?.close()}>Continuar</BotaoContinuar></div>
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
  const luta = useLutaPoc(), p = luta.palco, a = useAtlas();
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
      {p.fim && !luta.lutando && <Resultado p={p} continuar={continuar} />}
    </section>
  );
}
