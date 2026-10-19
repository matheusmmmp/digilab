/* Palco da luta (desenhos ArenaAoVivo, BatAcao, UpLuta e UpResultado; porte do HTML): vida e guts dos dois,
   turno no hexagono, arena do UP (PVP_Bg_Octagon) com os dois em escala inteira comum, distancia em etiqueta,
   intencao do rival, regra que o pet usou (travar/vetar ali mesmo), linha do turno, resultado e registro. */
import { useEffect, useRef, useState } from "react";
import {
  CAT, DIST, NOME_V2, NPC, chaveRegra, expressar, regraDe, rotuloRegra, type EstadoLuta, type MotivoCombate, type Turno,
} from "../../../motor/index.ts";
import { zoomAtual } from "../../escala.ts";
import { atlasAtual, desenharSprite, dimSprite, escalaSprite, imagemAtlas, quadroAgora, useAtlas } from "../../atlas.ts";
import { dec } from "../../componentes/Barras.tsx";
import { FUNDO_NPC, imagemDeco, ouvirDecoracao } from "../../decoracao.ts";
import { Peca } from "../../componentes/Imagens.tsx";
import { falaLLM, motivoParaApi, useFalaLLM } from "../../fala.ts";
import { S, desenharGrade, paleta } from "../../grades.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { LUTA, alternarPausa, alternarRapido, useLuta, type LutadorTela, type Palco } from "../../luta.ts";
import { abrirModal } from "../../componentes/modal.ts";

const XS = [[27, 69], [18, 78], [10, 86]];   /* centro do seu pet e do rival por distancia (em 96 avos da largura) */
/* geometria da prancha UpLuta, em px de CSS: arena de 420 (no desktop, a altura do palco), pes a 344/420 da altura,
   sombras 120 x 18, sprite ate 170/420 da altura */
function ajustarTela(cv: HTMLCanvasElement): { K: number; W: number; H: number } {
  const pai = cv.parentElement, W = pai && pai.clientWidth > 0 ? pai.clientWidth : 390, H = pai && pai.clientHeight > 0 ? pai.clientHeight : 420, K = (devicePixelRatio || 1) * zoomAtual();
  const bw = Math.round(W * K), bh = Math.round(H * K);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; cv.style.width = W + "px"; cv.style.height = H + "px"; }
  return { K, W, H };
}
function quadroLutador(tr: Turno | null, lado: 0 | 1): number {
  if (!tr) return 0;
  if (tr.depois.L[lado].hp <= 0) return 3;
  const a = lado === 0 ? tr.a : tr.b;
  return ["golpe_rapido", "disparo", "pesado", "preparar_pesado"].includes(a) ? 2 : 0;
}
/** desenha a arena: fundo do UP (PVP_Bg_Octagon, largura inteira, centro a 38%), sombras, os dois lutadores em escala
    inteira comum (ate 3x) e o "!" de quem prepara o pesado */
function desenharArena(cv: HTMLCanvasElement, p: Palco): void {
  const cx = cv.getContext("2d"); if (!cx) throw new Error("canvas 2d indisponível");
  const { K, W, H: ARENA_H } = ajustarTela(cv), a = atlasAtual(), ok = a.tipo === "ok", PES_Y = ARENA_H * 344 / 420, ALT_MAX = ARENA_H * 170 / 420;
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, cv.width, cv.height);
  const alt = ok ? [p.A, p.B].map(L => dimSprite(a.dados, L.sprite)[1]) : [];
  const escLuta = alt.length ? Math.max(1, Math.min(3, Math.floor(ALT_MAX / Math.max(...alt)))) : 3;
  const nomeFundo = p.modo === "campanha" ? FUNDO_NPC[p.B.sprite] : undefined, ilustra = nomeFundo ? imagemDeco(nomeFundo) : null;
  if (ilustra) {
    /* campanha: fundo ilustrado do lugar do NPC (recorte sem o chefe), cover a partir da esquerda, pelicula de 30% */
    const e = Math.max(cv.width / ilustra.naturalWidth, cv.height / ilustra.naturalHeight);
    cx.imageSmoothingEnabled = true; cx.imageSmoothingQuality = "high";
    cx.drawImage(ilustra, 0, (cv.height - ilustra.naturalHeight * e) / 2, ilustra.naturalWidth * e, ilustra.naturalHeight * e);
    cx.fillStyle = "rgba(8,20,48,.3)"; cx.fillRect(0, 0, cv.width, cv.height);
  } else if (ok) {
    const r = a.dados.pecas.fundo_arena; if (!r) throw new Error("peça do atlas ausente: fundo_arena");
    let esc = W / r[2]; if (r[3] * esc < ARENA_H) esc = ARENA_H / r[3];
    const dw = r[2] * esc, dh = r[3] * esc;
    cx.imageSmoothingEnabled = true;
    cx.drawImage(a.img, r[0], r[1], r[2], r[3], Math.round((W - dw) / 2 * K), Math.round((ARENA_H - dh) * .38 * K), Math.round(dw * K), Math.round(dh * K));
  } else { cx.fillStyle = "#0B1A44"; cx.fillRect(0, 0, cv.width, cv.height); }
  cx.imageSmoothingEnabled = false;
  const [xa, xb] = XS[p.E.dist].map(x => x / 96 * W);
  cx.fillStyle = "rgba(0,0,0,.45)";
  for (const x of [xa, xb]) { cx.beginPath(); cx.ellipse(x * K, (PES_Y - 1) * K, 60 * K, 9 * K, 0, 0, Math.PI * 2); cx.fill(); }
  const lutador = (L: LutadorTela, x: number, q: number, esquerda: boolean): number => {
    if (a.tipo === "ok") {
      /* UP: so o idle; nocaute (q 3) para no quadro 0 e fica apagado. Os sprites olham para a direita: o rival
         e espelhado (o espelho vale so na luta, guia secao 5) */
      const [w, h] = dimSprite(a.dados, L.sprite), e = Math.max(1, Math.floor(escLuta * K));
      if (q === 3) cx.globalAlpha = .45;
      desenharSprite(cx, a, L.sprite, x * K - w * e / 2, PES_Y * K - h * e, e, quadroAgora(a, L.sprite, q === 3), { sombria: L.sombra, espelho: !esquerda });
      cx.globalAlpha = 1;
      return h * e / K;
    }
    const g = S[L.grade], w = Math.max(...g.map(l => l.length));
    cx.setTransform(3 * K, 0, 0, 3 * K, 0, 0);
    desenharGrade(cx, g, Math.round(x / 3 - w / 2), Math.round(PES_Y / 3) - g.length, paleta(L.cor), { espelho: !esquerda, olhosFechados: q === 3 });
    cx.setTransform(1, 0, 0, 1, 0, 0);
    return g.length * 3;
  };
  const ha = lutador(p.A, xa, quadroLutador(p.tr, 0), true), hb = lutador(p.B, xb, quadroLutador(p.tr, 1), false);
  const pal = paleta("carga");
  cx.setTransform(3 * K, 0, 0, 3 * K, 0, 0);
  if (p.E.L[0].prep) desenharGrade(cx, S.exclam, Math.round(xa / 3) - 3, Math.round((PES_Y - ha) / 3) - 9, pal);
  if (p.E.L[1].prep) desenharGrade(cx, S.exclam, Math.round(xb / 3) - 3, Math.round((PES_Y - hb) / 3) - 9, pal);
  cx.setTransform(1, 0, 0, 1, 0, 0);
}
/** um lado do HUD (prancha UpLuta): retrato de 34 px, nome, vida (9 px) e guts (5 px) */
function Lado({ L, s, rot, rival }: { L: LutadorTela; s: EstadoLuta["L"][number]; rot: string; rival?: boolean }) {
  const a = useAtlas(), img = a.tipo === "ok" ? imagemAtlas(a, L.sprite) : null;
  return (
    <div className={`hud-lado${rival ? " hud-lado--rival" : ""}`} title={L.estiloTela ? `${L.nomeTela} (${L.estiloTela})` : L.nomeTela}>
      <span className="hud-ret">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
      <span className="hud-txt">
        <span className="hud-nome">{L.nomeTela}<span className="sr-only"> {Math.max(0, s.hp).toFixed(0)} de vida, guts {Math.round(s.guts)}</span></span>
        <span className="hud-vida" role="img" aria-label={`vida ${rot}`}><i style={{ width: `${Math.max(0, s.hp / s.hpMax * 100)}%` }} /></span>
        <span className="hud-guts" role="img" aria-label={`guts ${rot}`}><i style={{ width: `${s.guts / s.gutsMax * 100}%` }} /></span>
      </span>
    </div>
  );
}
/** a arena desenhada (tela cheia da luta e previa parada da Arena); pausar e x2 so quando ha luta animada */
export function Cena({ p, controles = false }: { p: Palco; controles?: boolean }) {
  const luta = useLuta();
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const cv = ref.current; if (!cv) return;
    desenharArena(cv, p);
    /* a arena anima o idle entre os turnos (so redesenha o ultimo estado; nada do motor muda) */
    const t = setInterval(() => { if (LUTA.palco) desenharArena(cv, LUTA.palco); }, 120);
    const sair = ouvirDecoracao(() => { if (LUTA.palco) desenharArena(cv, LUTA.palco); });
    return () => { clearInterval(t); sair(); };
  }, [p, p.E, p.tr]);
  return (
    <section className="luta-arena" aria-label="Palco da luta">
      <canvas ref={ref} className="arena-cv" width={96} height={48} role="img" aria-label={`Arena: ${p.A.nomeTela} contra ${p.B.nomeTela}`} />
      <div className="luta-hud">
        <Lado L={p.A} s={p.E.L[0]} rot="do seu pet" />
        <div className="hud-meio">
          <div className="turno-hex" aria-label="turno"><small>TURNO</small><b className="dl-num">{p.turno ?? "–"}</b></div>
          <span className="luta-dist">{DIST[p.E.dist]}</span>
        </div>
        <Lado L={p.B} s={p.E.L[1]} rot="do rival" rival />
      </div>
      {p.E.L[1].prep && <span className="luta-intencao-balao"><b className="luta-exclam">!</b>golpe pesado</span>}
      {p.callout && <span className="luta-callout dl-num dl-num--amarelo">{p.callout}</span>}
      {controles && luta.lutando && <div className="luta-controles">
        <button type="button" className="luta-ctl" aria-label={luta.pausado ? "Continuar a animação" : "Pausar a animação"} aria-pressed={luta.pausado} onClick={alternarPausa}>
          {luta.pausado ? <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3l9 5-9 5z" /></svg> : <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z" /></svg>}</button>
        <button type="button" className="luta-ctl luta-ctl--x2" aria-label="Velocidade dobrada" aria-pressed={luta.rapido} onClick={alternarRapido}>×2</button>
      </div>}
      {!controles && <span className="luta-previa-rot">prévia · escolha um rival e aperte Lutar</span>}
    </section>
  );
}
/** regra que o pet usou neste turno; travar e vetar direto daqui (so regras do proprio pet) */
function RegraUsada({ ma, A, semDono }: { ma: MotivoCombate; A: LutadorTela; semDono?: boolean }) {
  const { motor: m } = useJogo(), [msg, setMsg] = useState("");
  if (ma.exploracao) return <div className="dl-card luta-regra-card"><span className="dl-causa dl-causa--sem">? {A.nomeTela} decidiu ao acaso (exploração)</span></div>;
  if (ma.regra === "pesado_automatico") return <div className="dl-card luta-regra-card"><span className="dl-apoio">{A.nomeTela} soltou o pesado que tinha preparado.</span></div>;
  const g = A.estilo.gambits;
  if (!g || typeof ma.regra !== "number") return null;
  const final = ma.regra >= g.regras.length, r = final ? null : g.regras[ma.regra], k = r ? chaveRegra(r) : null;
  /* no Lago (semDono) as travas e os vetos nao valem nesta luta: sem os botoes */
  const gp = m.gp, doPet = !semDono && !!(gp && k && k in gp.notas), trav = doPet && k! in gp!.travas, vetada = doPet && gp!.vetos.includes(k!);
  const intervir = (op: "travar" | "destravar" | "vetar") => {
    try { mudarMotor(mm => mm.intervirGambit(op, k!)); setMsg(op === "vetar" ? "vetada: o pet não usa mais" : op === "travar" ? "travada nesta posição" : "destravada"); }
    catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  return (
    <div className="luta-regra-card dl-malha">
      <span className="luta-regra-topo"><span className="luta-regra-cab">REGRA QUE {A.nomeTela.toUpperCase()} USOU</span><span className="luta-regra-sub">aprendida</span></span>
      <span className="luta-regra-txt">{final ? `sempre → ${NOME_V2[g.final]}` : rotuloRegra(r!)}</span>
      {doPet && !vetada && !msg && <span className="luta-regra-bts">
        <button type="button" className="regra-travar" onClick={() => intervir(trav ? "destravar" : "travar")}><Peca nome="icone_cadeado" />{trav ? "Destravar" : "Travar"}</button>
        <button type="button" className="regra-vetar" onClick={() => intervir("vetar")}>Vetar</button></span>}
      {msg && <span className="dl-apoio">{msg}</span>}
    </div>
  );
}
function Log({ p }: { p: Palco }) {
  useFalaLLM();
  return (
    <ol className="luta-log" aria-label="Registro da luta">
      {p.log.map(l => {
        /* o tom da fala do seu pet na luta segue o humor dele na vida */
        const resp = falaLLM(motivoParaApi(l.ma, []), l.estPet, l.humor), pet = resp && resp.fonte === "llm" ? "✦ " + resp.texto : expressar(l.ma, l.estPet, l.ma.refs);
        return <li key={l.t}><span className="luta-t">T{l.t}</span> <b>{l.pet}</b>: {pet} · <b>{l.rival}</b>: {expressar(l.mb, l.estRival, l.mb.refs)}</li>;
      })}
    </ol>
  );
}
/** a luta em tela cheia (#/lutar/luta; pranchas UpLuta e BatDesktop): arena com pausar e x2 e os cards da leitura */
export function PalcoLuta() {
  const luta = useLuta(), p = luta.palco;
  if (!p) return null;
  return (
    <div className="palco-luta dl">
      <Cena p={p} controles />
      <div className="palco-luta-baixo">
        <section className="dl-card luta-card" aria-live="polite"><h2>Intenção do rival</h2>
          {p.intencao ? <div className="luta-intencao"><b className="luta-exclam">!</b><span>{p.intencao}</span></div>
            : <p className="dl-apoio">{p.B.nomeTela} não anunciou nada neste turno.</p>}</section>
        <section className="dl-card luta-card"><h2>Regra em uso</h2>
          {p.regra ? <RegraUsada key={p.turno} ma={p.regra.ma} A={p.regra.A} semDono={p.arena?.regra === "vinculo"} /> : <p className="dl-apoio">A luta ainda não começou.</p>}
          {p.texto && <p className="dl-apoio luta-turno">{p.texto}</p>}</section>
        <section className="dl-card luta-card luta-card--turnos"><h2>Turnos</h2><Log p={p} /></section>
      </div>
    </div>
  );
}
