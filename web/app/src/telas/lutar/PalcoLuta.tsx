/* Palco da luta (desenhos ArenaAoVivo, BatAcao, UpLuta e UpResultado; porte do HTML): vida e guts dos dois,
   turno no hexagono, arena do UP (PVP_Bg_Octagon) com os dois em escala inteira comum, distancia em etiqueta,
   intencao do rival, regra que o pet usou (travar/vetar ali mesmo), linha do turno, resultado e registro. */
import { useEffect, useRef, useState } from "preact/hooks";
import {
  CAT, DIST, NOME_V2, NPC, chaveRegra, expressar, regraDe, rotuloRegra, type EstadoLuta, type MotivoCombate, type Turno,
} from "../../../motor/index.ts";
import { atlasAtual, desenharSprite, dimSprite, escalaSprite, imagemAtlas, quadroAgora, useAtlas } from "../../atlas.ts";
import { dec } from "../../componentes/Barras.tsx";
import { Peca } from "../../componentes/Imagens.tsx";
import { falaLLM, motivoParaApi, useFalaLLM } from "../../fala.ts";
import { S, desenharGrade, paleta } from "../../grades.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { LUTA, useLuta, type LutadorTela, type Palco } from "../../luta.ts";

const XS = [[27, 69], [18, 78], [10, 86]];   /* centro do seu pet e do rival por distancia (em 96 avos da largura) */
/* geometria da prancha UpLuta, em px de CSS: arena de 420, pes em 344, sombras 120 x 18 em 334 */
const ARENA_H = 420, PES_Y = 344, ALT_MAX = 170;
function ajustarTela(cv: HTMLCanvasElement): { K: number; W: number } {
  const pai = cv.parentElement, W = pai && pai.clientWidth > 0 ? pai.clientWidth : 390, K = devicePixelRatio || 1;
  const bw = Math.round(W * K), bh = Math.round(ARENA_H * K);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; cv.style.width = W + "px"; cv.style.height = ARENA_H + "px"; }
  return { K, W };
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
  const { K, W } = ajustarTela(cv), a = atlasAtual(), ok = a.tipo === "ok";
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, cv.width, cv.height);
  const alt = ok ? [p.A, p.B].map(L => dimSprite(a.dados, L.sprite)[1]) : [];
  const escLuta = alt.length ? Math.max(1, Math.min(3, Math.floor(ALT_MAX / Math.max(...alt)))) : 3;
  if (ok) {
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
      const [w, h] = dimSprite(a.dados, L.sprite), e = escalaSprite() * escLuta;
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
    <div class={`hud-lado${rival ? " hud-lado--rival" : ""}`} title={L.estiloTela ? `${L.nomeTela} (${L.estiloTela})` : L.nomeTela}>
      <span class="hud-ret">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
      <span class="hud-txt">
        <span class="hud-nome">{L.nomeTela}<span class="sr-only"> {Math.max(0, s.hp).toFixed(0)} de vida, guts {Math.round(s.guts)}</span></span>
        <span class="hud-vida" role="img" aria-label={`vida ${rot}`}><i style={{ width: `${Math.max(0, s.hp / s.hpMax * 100)}%` }} /></span>
        <span class="hud-guts" role="img" aria-label={`guts ${rot}`}><i style={{ width: `${s.guts / s.gutsMax * 100}%` }} /></span>
      </span>
    </div>
  );
}
function Cena({ p }: { p: Palco }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const cv = ref.current; if (!cv) return;
    desenharArena(cv, p);
    /* a arena anima o idle entre os turnos (so redesenha o ultimo estado; nada do motor muda) */
    const t = setInterval(() => { if (LUTA.palco) desenharArena(cv, LUTA.palco); }, 120);
    return () => clearInterval(t);
  }, [p, p.E, p.tr]);
  return (
    <section class="luta-arena" aria-label="Palco da luta">
      <canvas ref={ref} class="arena-cv" width={96} height={48} role="img" aria-label={`Arena: ${p.A.nomeTela} contra ${p.B.nomeTela}`} />
      <div class="luta-hud">
        <Lado L={p.A} s={p.E.L[0]} rot="do seu pet" />
        <div class="hud-meio">
          <div class="turno-hex" aria-label="turno"><small>TURNO</small><b class="dl-num">{p.turno ?? "–"}</b></div>
          <span class="luta-dist">{DIST[p.E.dist]}</span>
        </div>
        <Lado L={p.B} s={p.E.L[1]} rot="do rival" rival />
      </div>
      {p.E.L[1].prep && <span class="luta-intencao-balao"><b class="luta-exclam">!</b>golpe pesado</span>}
      {p.callout && <span class="luta-callout dl-num dl-num--amarelo">{p.callout}</span>}
    </section>
  );
}
/** regra que o pet usou neste turno; travar e vetar direto daqui (so regras do proprio pet) */
function RegraUsada({ ma, A }: { ma: MotivoCombate; A: LutadorTela }) {
  const { motor: m } = useJogo(), [msg, setMsg] = useState("");
  if (ma.exploracao) return <div class="dl-card luta-regra-card"><span class="dl-causa dl-causa--sem">? {A.nomeTela} decidiu ao acaso (exploração)</span></div>;
  if (ma.regra === "pesado_automatico") return <div class="dl-card luta-regra-card"><span class="dl-apoio">{A.nomeTela} soltou o pesado que tinha preparado.</span></div>;
  const g = A.estilo.gambits;
  if (!g || typeof ma.regra !== "number") return null;
  const final = ma.regra >= g.regras.length, r = final ? null : g.regras[ma.regra], k = r ? chaveRegra(r) : null;
  const gp = m.gp, doPet = !!(gp && k && k in gp.notas), trav = doPet && k! in gp!.travas, vetada = doPet && gp!.vetos.includes(k!);
  const intervir = (op: "travar" | "destravar" | "vetar") => {
    try { mudarMotor(mm => mm.intervirGambit(op, k!)); setMsg(op === "vetar" ? "vetada: o pet não usa mais" : op === "travar" ? "travada nesta posição" : "destravada"); }
    catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  return (
    <div class="luta-regra-card dl-malha">
      <span class="luta-regra-topo"><span class="luta-regra-cab">REGRA QUE {A.nomeTela.toUpperCase()} USOU</span><span class="luta-regra-sub">aprendida</span></span>
      <span class="luta-regra-txt">{final ? `sempre → ${NOME_V2[g.final]}` : rotuloRegra(r!)}</span>
      {doPet && !vetada && !msg && <span class="luta-regra-bts">
        <button type="button" class="regra-travar" onClick={() => intervir(trav ? "destravar" : "travar")}><Peca nome="icone_cadeado" />{trav ? "Destravar" : "Travar"}</button>
        <button type="button" class="regra-vetar" onClick={() => intervir("vetar")}>Vetar</button></span>}
      {msg && <span class="dl-apoio">{msg}</span>}
    </div>
  );
}
function Resultado({ p, voltarPet }: { p: Palco; voltarPet: () => void }) {
  const { motor: m } = useJogo(), a = useAtlas(), r = p.resultado!, res = r.res, venceu = res.pontosA === 1, empate = res.pontosA !== 1 && res.pontosA !== 0;
  const onde = r.npc ? NPC[r.npc]!.lugar : "Arena", fintas = res.turnos.filter(tr => tr.a === "fintar").length;
  let reforcada: [string, number] | null = null;
  if (!r.cenario && r.notasAntes && m.gp) {
    const gp = m.gp, ganhos = gp.ativas.filter(k => k in r.notasAntes!).map(k => [k, gp.notas[k] - r.notasAntes![k]] as [string, number]).filter(([, d]) => d > 1e-9).sort((x, y) => y[1] - x[1]);
    if (ganhos.length) reforcada = ganhos[0];
  }
  const img = a.tipo === "ok" ? imagemAtlas(a, p.B.sprite) : null;
  return (
    <div class="dl-card luta-res">
      <span class="dl-placa dl-placa--inclinada">{onde} · {venceu ? "vitória" : empate ? "empate" : "derrota"}</span>
      <span class="luta-res-rival">{img && <img class="dl-pix" src={img.url} alt="" style={venceu ? { filter: "grayscale(1)", opacity: .6 } : {}} />}
        <span><b>{p.B.nomeTela}</b> {venceu ? "derrotado" : empate ? "empatou" : "venceu"}<br />
          <span class="dl-apoio">{res.turnos.length} turnos · {res.fim === "ko" ? "nocaute" : "limite de turnos"}{fintas ? ` · ${fintas} finta${fintas > 1 ? "s" : ""}` : ""}</span></span></span>
      {reforcada && <div class="luta-regra-card dl-malha"><span class="luta-regra-cab">REGRA REFORÇADA NESTA LUTA</span>
        <span class="luta-regra-txt">{rotuloRegra(regraDe(reforcada[0]))}</span><span class="dl-apoio" style={{ color: "#BDEFFF" }}>nota +{dec(reforcada[1], 2)}</span></div>}
      {m.estagioAtual === "adolescente" && !r.cenario && <span class="dl-apoio">lutas de treino para evoluir: {Math.min(m.sparring, CAT.sparring)} de {CAT.sparring}</span>}
      {r.cenario && <span class="dl-apoio">Contra pet de cenário o seu não aprende.</span>}
      <button type="button" class="dl-btn dl-btn--sec" onClick={voltarPet}>Voltar ao pet</button>
    </div>
  );
}
function Log({ p }: { p: Palco }) {
  useFalaLLM();
  return (
    <ol class="luta-log" aria-label="Registro da luta">
      {p.log.map(l => {
        /* o tom da fala do seu pet na luta segue o humor dele na vida */
        const resp = falaLLM(motivoParaApi(l.ma, []), l.estPet, l.humor), pet = resp && resp.fonte === "llm" ? "✦ " + resp.texto : expressar(l.ma, l.estPet, l.ma.refs);
        return <li key={l.t}><span class="luta-t">T{l.t}</span> <b>{l.pet}</b>: {pet} · <b>{l.rival}</b>: {expressar(l.mb, l.estRival, l.mb.refs)}</li>;
      })}
    </ol>
  );
}
export function PalcoLuta({ voltarPet }: { voltarPet: () => void }) {
  const luta = useLuta(), p = luta.palco;
  if (!p) return null;
  return (
    <div class="palco-luta dl">
      <Cena p={p} />
      <div class="palco-luta-baixo">
        <div aria-live="polite">{p.intencao && <div class="luta-intencao"><b class="luta-exclam">!</b><span>{p.intencao}</span></div>}</div>
        {p.regra && <RegraUsada key={p.turno} ma={p.regra.ma} A={p.regra.A} />}
        <p class="dl-apoio luta-turno">{p.texto}</p>
        {p.resultado && <Resultado p={p} voltarPet={voltarPet} />}
        <Log p={p} />
      </div>
    </div>
  );
}
