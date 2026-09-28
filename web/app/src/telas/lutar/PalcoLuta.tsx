/* Palco da luta (desenhos ArenaAoVivo, BatAcao, UpLuta e UpResultado; porte do HTML): vida e guts dos dois,
   turno no hexagono, arena do UP (PVP_Bg_Octagon) com os dois em escala inteira comum, distancia em etiqueta,
   intencao do rival, regra que o pet usou (travar/vetar ali mesmo), linha do turno, resultado e registro. */
import { useEffect, useRef, useState } from "preact/hooks";
import {
  CAT, DIST, NOME_V2, NPC, chaveRegra, expressar, regraDe, rotuloRegra, type EstadoLuta, type MotivoCombate, type Turno,
} from "../../../motor/index.ts";
import { atlasAtual, desenharSprite, dimSprite, escalaSprite, imagemAtlas, quadroAgora, useAtlas } from "../../atlas.ts";
import { dec } from "../../componentes/Barras.tsx";
import { falaLLM, motivoParaApi, useFalaLLM } from "../../fala.ts";
import { S, desenharGrade, paleta } from "../../grades.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { LUTA, useLuta, type LutadorTela, type Palco } from "../../luta.ts";

const XS = [[38, 58], [24, 72], [10, 86]];   /* centro do seu pet e do rival por distancia */
const escalas = new WeakMap<HTMLCanvasElement, number>();
function ajustarTela(cv: HTMLCanvasElement, uw: number, uh: number): number {
  const pai = cv.parentElement, K0 = escalas.get(cv);
  if (!pai) return K0 ?? 4;
  const cs = getComputedStyle(pai), livre = pai.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  if (!(livre > 0)) { if (!K0) { escalas.set(cv, 4); cv.width = uw * 4; cv.height = uh * 4; } return escalas.get(cv)!; }
  const dpr = devicePixelRatio || 1, px = Math.max(uw, Math.floor(Math.min(livre, 640) * dpr)), K = px / uw, larg = (px / dpr) + "px";
  if (K0 === K && cv.width === px && cv.style.width === larg) return K;
  escalas.set(cv, K); cv.width = px; cv.height = Math.round(uh * K);
  cv.style.width = larg; cv.style.height = (cv.height / dpr) + "px";
  return K;
}
function quadroLutador(tr: Turno | null, lado: 0 | 1): number {
  if (!tr) return 0;
  if (tr.depois.L[lado].hp <= 0) return 3;
  const a = lado === 0 ? tr.a : tr.b;
  return ["golpe_rapido", "disparo", "pesado", "preparar_pesado"].includes(a) ? 2 : 0;
}
/** desenha a arena: fundo do UP, os dois lutadores e o "!" de quem prepara o pesado */
function desenharArena(cv: HTMLCanvasElement, p: Palco): void {
  const cx = cv.getContext("2d"); if (!cx) throw new Error("canvas 2d indisponível");
  const K = ajustarTela(cv, 96, 48), a = atlasAtual(), ok = a.tipo === "ok";
  /* escala inteira comum aos dois lutadores (ate 3x, guia secao 5): a maior que cabe na altura do palco */
  const alt = ok ? [p.A, p.B].map(L => dimSprite(a.dados, L.sprite)[1]) : [];
  const escLuta = alt.length ? Math.max(1, Math.min(3, Math.floor(34 * K / (Math.max(...alt) * escalaSprite())))) : 1;
  cx.setTransform(K, 0, 0, K, 0, 0); cx.imageSmoothingEnabled = false;
  if (ok) {
    /* fundo de arena do UP (pintura): faixa central do octogono cobrindo o palco, com suavizacao */
    const r = a.dados.pecas.fundo_arena; if (!r) throw new Error("peça do atlas ausente: fundo_arena");
    const sh = Math.round(r[2] * 48 / 96);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.imageSmoothingEnabled = true;
    cx.drawImage(a.img, r[0], r[1] + Math.round((r[3] - sh) * .55), r[2], sh, 0, 0, cv.width, cv.height); cx.restore();
    cx.fillStyle = "rgba(11,42,94,.35)"; cx.fillRect(0, 38, 96, 10);
  } else {
    cx.fillStyle = "#0F3A86"; cx.fillRect(0, 0, 96, 48);
    cx.fillStyle = "#0B2A5E"; cx.fillRect(0, 38, 96, 10);
  }
  const [xa, xb] = XS[p.E.dist];
  const lutador = (L: LutadorTela, x: number, q: number, esquerda: boolean): number => {
    if (a.tipo === "ok") {
      /* UP: so o idle; nocaute (q 3) para no quadro 0 e fica apagado. Os sprites olham para a direita: o rival
         e espelhado (o espelho vale so na luta, guia secao 5) */
      const [w, h] = dimSprite(a.dados, L.sprite), e = escalaSprite() * escLuta;
      if (q === 3) cx.globalAlpha = .45;
      desenharSprite(cx, a, L.sprite, x * K - w * e / 2, 40 * K - h * e, e, quadroAgora(a, L.sprite, q === 3), { sombria: L.sombra, espelho: !esquerda });
      cx.globalAlpha = 1;
      return h * e / K;
    }
    const g = S[L.grade], w = Math.max(...g.map(l => l.length));
    desenharGrade(cx, g, Math.round(x - w / 2), 40 - g.length, paleta(L.cor), { espelho: !esquerda, olhosFechados: q === 3 });
    return g.length;
  };
  const ha = lutador(p.A, xa, quadroLutador(p.tr, 0), true), hb = lutador(p.B, xb, quadroLutador(p.tr, 1), false);
  const pal = paleta("carga");
  if (p.E.L[0].prep) desenharGrade(cx, S.exclam, xa - 3, 40 - ha - 9, pal);
  if (p.E.L[1].prep) desenharGrade(cx, S.exclam, xb - 3, 40 - hb - 9, pal);
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
    <div class="luta-cena">
      <span class="dl-tag luta-dist">distância: {DIST[p.E.dist]}</span>
      <canvas ref={ref} class="arena-cv" width={96} height={48} role="img" aria-label={`Arena: ${p.A.nomeTela} contra ${p.B.nomeTela}`} />
      {p.callout && <span class="luta-callout dl-num">{p.callout}</span>}
    </div>
  );
}
function NomeTopo({ L }: { L: LutadorTela }) {
  return <span class="luta-nome" title={L.estiloTela ? `${L.nomeTela} (${L.estiloTela})` : L.nomeTela}><b>{L.nomeTela}</b>{L.estiloTela && <small>{L.estiloTela}</small>}</span>;
}
function Vida({ L, s, rot }: { L: LutadorTela; s: EstadoLuta["L"][number]; rot: string }) {
  return (
    <div class="luta-vida">
      <div class="dl-vida-topo"><NomeTopo L={L} /><span class="dl-lcd">{Math.max(0, s.hp).toFixed(0)}<span class="sr-only"> de vida, guts {Math.round(s.guts)}</span></span></div>
      <div class="dl-vida-trilho" role="img" aria-label={`vida ${rot}`}><i style={{ width: `${Math.max(0, s.hp / s.hpMax * 100)}%` }} /></div>
      <div class="luta-guts" role="img" aria-label={`guts ${rot}`}><i style={{ width: `${s.guts / s.gutsMax * 100}%` }} /></div>
    </div>
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
      <span class="luta-regra-cab">REGRA QUE {A.nomeTela.toUpperCase()} USOU</span>
      <span class="luta-regra-txt">{final ? `sempre → ${NOME_V2[g.final]}` : rotuloRegra(r!)}</span>
      {doPet && !vetada && !msg && <span class="dl-linha">
        <button type="button" class="dl-btn dl-btn--sec" onClick={() => intervir(trav ? "destravar" : "travar")}>{trav ? "Destravar" : "Travar"}</button>
        <button type="button" class="dl-btn dl-btn--sec" onClick={() => intervir("vetar")}>Vetar</button></span>}
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
        return <li key={l.t}><span class="dl-lcd">T{l.t}</span> <b>{l.pet}</b>: {pet} · <b>{l.rival}</b>: {expressar(l.mb, l.estRival, l.mb.refs)}</li>;
      })}
    </ol>
  );
}
export function PalcoLuta({ voltarPet }: { voltarPet: () => void }) {
  const luta = useLuta(), p = luta.palco;
  if (!p) return null;
  return (
    <div class="palco-luta dl">
      <div class="luta-topo">
        <Vida L={p.A} s={p.E.L[0]} rot="do seu pet" />
        <div class="turno-hex" aria-label="turno"><span class="dl-lcd">TURNO</span><b class="dl-num">{p.turno ?? "–"}</b></div>
        <Vida L={p.B} s={p.E.L[1]} rot="do rival" />
      </div>
      <Cena p={p} />
      <div aria-live="polite">{p.intencao && <span class="dl-balao luta-intencao"><b class="luta-exclam">!</b> {p.intencao}</span>}</div>
      {p.regra && <RegraUsada key={p.turno} ma={p.regra.ma} A={p.regra.A} />}
      <p class="dl-apoio luta-turno">{p.texto}</p>
      {p.resultado && <Resultado p={p} voltarPet={voltarPet} />}
      <Log p={p} />
    </div>
  );
}
