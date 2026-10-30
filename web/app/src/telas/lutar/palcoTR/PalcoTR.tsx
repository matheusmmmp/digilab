/* O palco da luta em tempo real (COMBATE-TR, etapa R3; docs/ESPEC_COMBATE_TR.md, item 7; pranchas UpLuta e BatDesktop): o mapa do UP do
   lugar como cenario, os dois lutadores com os clipes do atlas, a vida e o Guts, o relogio e a morte subita. Nenhum controle sobre a luta:
   o pet luta sozinho; pausar, x2 e pular so mudam como a luta ja decidida e mostrada. A regra em uso e so leitura (travar e vetar ficam
   no Treinador, fora da luta). */
import { useEffect, useReducer, useRef } from "react";
import { CTR_TR, NOME_V2, PASSO_TR_MS, rotuloRegra } from "../../../../motor/index.ts";
import { atlasAtual, imagemAtlas, useAtlas } from "../../../atlas.ts";
import { AvisoSom } from "../../../componentes/AvisoSom.tsx";
import { LUTA, alternarPausa, alternarRapido, useLuta, type HudLado, type LutadorTela, type Palco, type RegraTR } from "../../../luta.ts";
import { arquivosCena, falhasMapa, ouvirMapas } from "./cenasTR.ts";
import { desenharLutaTR } from "./desenhoTR.ts";
import "../../../estilo/abertas.css";

/** um lado do HUD (prancha UpLuta): retrato, nome, vida e guts */
function Lado({ L, s, rot, rival }: { L: LutadorTela; s: HudLado; rot: string; rival?: boolean }) {
  const a = useAtlas(), img = a.tipo === "ok" ? imagemAtlas(a, L.sprite) : null;
  return (
    <div className={`hud-lado${rival ? " hud-lado--rival" : ""}`} title={L.estiloTela ? `${L.nomeTela} (${L.estiloTela})` : L.nomeTela}>
      <span className="hud-ret">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
      <span className="hud-txt">
        <span className="hud-nome">{L.nomeTela}<span className="sr-only"> {Math.max(0, s.hp).toFixed(0)} de vida, guts {Math.round(s.guts)}</span></span>
        <span className="hud-vida" role="img" aria-label={`vida ${rot}`}><i style={{ width: `${Math.max(0, s.hp / s.hpMax * 100)}%` }} /></span>
        <span className="hud-guts" role="img" aria-label={`guts ${rot}`}><i style={{ width: `${Math.max(0, s.guts / s.gutsMax * 100)}%` }} /></span>
      </span>
    </div>
  );
}
/** o intervalo do desenho com o palco parado (ms; o do palco por turnos de antes) */
const QUADRO_PARADO = 120;
const relogio = (s: number): string => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
/** o palco desenhado (tela cheia da luta e previa parada da Arena); pausar e x2 so quando ha luta animada */
export function Cena({ p, controles = false }: { p: Palco; controles?: boolean }) {
  const luta = useLuta(), a = useAtlas(), ref = useRef<HTMLCanvasElement>(null), [, redesenhar] = useReducer((x: number) => x + 1, 0);
  const arqs = arquivosCena(p.cena), faltam = arqs.filter(x => falhasMapa.has(x));
  useEffect(() => ouvirMapas(redesenhar), []);
  useEffect(() => {
    const cv = ref.current; if (!cv) return;
    /* um quadro por frame do navegador durante a luta (ela anda no relogio do luta.ts; aqui so se desenha o estado de agora); parado (a
       previa, o fim), so o Idle a cada QUADRO_PARADO ms, como o palco de antes */
    let id = 0, ult = -Infinity;
    const desenhar = (agora: number) => {
      if (LUTA.lutando || agora - ult >= QUADRO_PARADO) {
        ult = agora;
        const pp = LUTA.palco ?? p, at = atlasAtual();
        desenharLutaTR(cv, { cena: pp.cena, A: pp.A, B: pp.B, sim: pp.sim, visual: pp.visual, koEm: pp.koEm }, at.tipo === "ok" ? at : null);
      }
      id = requestAnimationFrame(desenhar);
    };
    desenhar(performance.now());
    return () => cancelAnimationFrame(id);
  }, [p, a.tipo]);
  const fimTempo = Math.round(CTR_TR.limite * PASSO_TR_MS / 1000);
  return (
    <section className="luta-arena luta-arena--tr" aria-label="Palco da luta" data-cena={p.cena}>
      <canvas ref={ref} className="arena-cv" width={96} height={48} role="img" aria-label={`Luta: ${p.A.nomeTela} contra ${p.B.nomeTela}`} />
      <div className="luta-hud">
        <Lado L={p.A} s={p.hud[0]} rot="do seu pet" />
        <div className="hud-meio">
          <div className="turno-hex" aria-label="tempo da luta"><small>TEMPO</small><b className="dl-num" data-testid="luta-relogio">{p.segundos === null ? "–" : relogio(p.segundos)}</b></div>
          <span className="luta-dist">{p.morteSubita ? "morte súbita" : `até ${relogio(fimTempo)}`}</span>
        </div>
        <Lado L={p.B} s={p.hud[1]} rot="do rival" rival />
      </div>
      {p.callout && <span className="luta-callout dl-num dl-num--amarelo">{p.callout}</span>}
      {a.tipo === "erro" && <p className="luta-aviso-asset" role="alert">O atlas dos sprites não carregou ({a.erro}): a luta aparece com marcadores no lugar dos Digimon.</p>}
      {faltam.length > 0 && <p className="luta-aviso-asset" role="alert">O mapa do cenário não carregou ({faltam.join(", ")}): a luta aparece no chão liso.</p>}
      {controles && luta.lutando && <div className="luta-controles">
        <button type="button" className="luta-ctl" aria-label={luta.pausado ? "Continuar a animação" : "Pausar a animação"} aria-pressed={luta.pausado} onClick={alternarPausa}>
          {luta.pausado ? <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3l9 5-9 5z" /></svg> : <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z" /></svg>}</button>
        <button type="button" className="luta-ctl luta-ctl--x2" aria-label="Velocidade dobrada" aria-pressed={luta.rapido} onClick={alternarRapido}>×2</button>
      </div>}
      {!controles && <span className="luta-previa-rot">prévia · escolha um rival e aperte Lutar</span>}
    </section>
  );
}
/** o que o pet esta fazendo e por que (so leitura: nada se muda durante a luta) */
export function textoRegra(r: RegraTR, A: LutadorTela): string {
  const acao = NOME_V2[r.nome] ?? r.nome;
  if (r.motivo === "exploracao") return `${acao}: ${A.nomeTela} decidiu ao acaso (exploração)`;
  if (r.motivo === "pesado_automatico") return `${acao}: ${A.nomeTela} soltou o pesado que tinha preparado`;
  const g = A.estilo.gambits;
  if (!g || typeof r.motivo !== "number") return acao;
  return r.motivo >= g.regras.length ? `sempre → ${NOME_V2[g.final]}` : rotuloRegra(g.regras[r.motivo]);
}
/** a luta em tela cheia (#/lutar/luta; pranchas UpLuta e BatDesktop): o palco e a leitura da regra em uso */
export function PalcoTR() {
  const luta = useLuta(), p = luta.palco;
  if (!p) return null;
  return (
    <div className="palco-luta dl">
      <Cena p={p} controles />
      <AvisoSom />
      <div className="palco-luta-baixo">
        <section className="dl-card luta-card" aria-live="polite"><h2>Regra em uso</h2>
          {p.regra ? <div className="luta-regra-card dl-malha">
            <span className="luta-regra-topo"><span className="luta-regra-cab">O QUE {p.A.nomeTela.toUpperCase()} FAZ</span></span>
            <span className="luta-regra-txt" data-testid="luta-regra">{textoRegra(p.regra, p.A)}</span></div>
            : <p className="dl-apoio">A luta ainda não começou.</p>}
          {p.texto && <p className="dl-apoio luta-turno">{p.texto}</p>}</section>
      </div>
    </div>
  );
}
