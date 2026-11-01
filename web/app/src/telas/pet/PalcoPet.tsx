/* Palco do Pet (docs/TAREFA_V2_TELA_PET.md; antes, porte do desenharLCD do HTML). O canvas cobre a cena inteira, transparente,
   por cima do cenario (CenarioPet); desenha so o que e do pet: a plataforma, a sujeira, o pet (ou o ovo) e o icone rapido de
   depois de uma acao do dono. Backing store em pixels do aparelho; o sprite entra em escala inteira, nitido, sem esticar pelo CSS.
   Sujeira, sono, o que o pet faz e a saude critica vem do motor. Sem atlas: o sprite de reserva (grade), tambem em escala inteira. */
import { useEffect, useRef } from "react";
import { OVO, chaveSprite, corDominante } from "../../../motor/index.ts";
import { zoomAtual } from "../../escala.ts";
import { atlasAtual, desenharSprite, dimSprite, escalaSprite, quadroAgora, type AtlasOk } from "../../atlas.ts";
import { S, desenharGrade, gradeDe, paleta } from "../../grades.ts";
import { flashAtual } from "../../flash.ts";
import { balancoOvo, jogoAtual, passarQuadroOvo } from "../../jogo.ts";
import { CENA } from "./cenaEstado.ts";
import { alturaSono, desenharZz } from "./sono.ts";

const ICONE_ACAO: Record<string, string> = { dormir: "zz", chamar_atencao: "exclam", emburrar: "raiva", brincar: "nota", explorar: "pergunta", comer: "carne" };
const EMOTE_ICONE: Record<string, string> = { carne: "emoji_carne", nota: "emoji_nota", exclam: "emoji_exclam", coracao: "emoji_coracao" };

/* icone rapido depois de uma acao do dono (1,4 s): src/flash.ts (o caminho compartilhado das acoes, src/acoes.ts, o dispara) */
export { mostrarFlash } from "../../flash.ts";

/* geometria da cena, em px de CSS, recalculada a cada quadro pelo tamanho do canvas: os pes do pet a 86% da altura, sobre a
   plataforma; o pet ocupa no maximo 42% da altura e 60% da largura, na maior escala inteira que cabe (ate 6x) */
interface Geo { K: number; W: number; H: number; pes: number; anelW: number; anelH: number; altMax: number; largMax: number }
const TOPO_LIVRE = 56;

function ajustarTela(cv: HTMLCanvasElement): Geo {
  const pai = cv.parentElement, W = pai && pai.clientWidth > 0 ? pai.clientWidth : 366, H = pai && pai.clientHeight > 0 ? pai.clientHeight : 460;
  const K = (devicePixelRatio || 1) * zoomAtual();
  const bw = Math.round(W * K), bh = Math.round(H * K);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; cv.style.width = W + "px"; cv.style.height = H + "px"; }
  const pes = Math.round(H * .86), anelW = Math.round(Math.min(W * .66, Math.max(220, H * .6))), anelH = Math.round(anelW * .28);
  return { K, W, H, pes, anelW, anelH, altMax: Math.min(H * .42, pes - TOPO_LIVRE), largMax: W * .6 };
}
/** a maior escala inteira (em px de CSS) que cabe na caixa do pet */
const escalaQueCabe = (g: Geo, w: number, h: number): number => Math.max(1, Math.min(6, Math.floor(Math.min(g.altMax / h, g.largMax / w))));

function desenharPalco(cv: HTMLCanvasElement, cx: CanvasRenderingContext2D, quadro: number): void {
  const { motor: m, nascendo } = jogoAtual(), e = m.e;
  const g = ajustarTela(cv), { K, W } = g, a = atlasAtual(), pal = paleta(corDominante(m.tracos));
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, cv.width, cv.height); cx.imageSmoothingEnabled = false;
  /* a cena 3D, ou a reserva do mundo dos v12 (MundoReserva), desenha o pet: aqui ficam os extras */
  if (CENA.modo3d || CENA.modoMundo) { desenharExtras3D(cx, g); return; }
  const anelX = (W - g.anelW) / 2, anelY = g.pes - g.anelH / 2;
  if (a.tipo === "ok") {
    /* plataforma (peca pintada do UP, nao pixel art): com suavizacao */
    const r = a.dados.pecas.anel_plataforma;
    if (!r) throw new Error("peça do atlas ausente: anel_plataforma");
    cx.imageSmoothingEnabled = true;
    cx.drawImage(a.img, r[0], r[1], r[2], r[3], Math.round(anelX * K), Math.round(anelY * K), Math.round(g.anelW * K), Math.round(g.anelH * K));
    cx.imageSmoothingEnabled = false;
  } else {
    /* sem atlas: a plataforma desenhada, um aro claro sobre o chao */
    cx.fillStyle = "rgba(127,180,240,.35)"; cx.strokeStyle = "#9CC8F5"; cx.lineWidth = 6 * K;
    cx.beginPath(); cx.ellipse(W / 2 * K, g.pes * K, g.anelW / 2 * K, g.anelH / 2 * K, 0, 0, Math.PI * 2); cx.fill(); cx.stroke();
  }
  /* sujeira (motor): a grade do coco em escala inteira, dos dois lados da plataforma */
  const ec = Math.max(2, Math.round(g.anelH / 18));
  cx.setTransform(ec * K, 0, 0, ec * K, 0, 0);
  for (let i = 0; i < e.sujeira; i++) {
    const xc = i < 3 ? anelX - 10 * ec - i * 9 * ec : anelX + g.anelW + 2 * ec + (i - 3) * 9 * ec;
    desenharGrade(cx, S.coco, Math.round(xc / ec), Math.round((g.pes - 4 * ec) / ec), { ...pal, d: "#8A5A2B" });
  }
  cx.setTransform(1, 0, 0, 1, 0, 0);
  if (a.tipo === "ok") {
    if (nascendo > 0) {
      const oscil = balancoOvo(nascendo) * 3, [ow, oh] = dimSprite(a.dados, OVO[m.especie]), eo = escalaQueCabe(g, ow, oh) * Math.max(1, Math.round(K));
      desenharSprite(cx, a, OVO[m.especie], (W / 2 + oscil) * K - ow * eo / 2, g.pes * K - oh * eo, eo, 0);
      if (!CENA.coberto) passarQuadroOvo();
      return;
    }
    desenharPetUp(cx, a, g, quadro);
    return;
  }
  /* sem atlas: o sprite de reserva (grade do estagio, ou o ovo), em escala inteira, com o mesmo movimento */
  const grade = nascendo > 0 ? S.ovo : S[gradeDe(m.estagioAtual)], larg = Math.max(...grade.map(l => l.length)), alt = grade.length;
  const u = escalaQueCabe(g, larg, alt), uk = u * K, acao = m.acao;
  let x = W / 2 - larg * u / 2, y = g.pes - alt * u;
  if (nascendo > 0) x += balancoOvo(nascendo) * 3;
  else if (acao === "explorar") x += Math.round(Math.sin(quadro / 3) * u * 10);
  else if (acao === "brincar") { x += Math.round(Math.sin(quadro / 2) * u * 4); y -= (quadro % 4 < 2) ? u * 2 : 0; }
  else if (acao !== "dormir") y -= (quadro % 4 < 2) ? u : 0;
  cx.setTransform(uk, 0, 0, uk, Math.round(x * K), Math.round(y * K));
  desenharGrade(cx, grade, 0, 0, pal, nascendo > 0 ? {} : { olhosFechados: acao === "dormir" || (quadro % 17 === 0), espelho: acao === "explorar" && Math.cos(quadro / 3) < 0 });
  cx.setTransform(1, 0, 0, 1, 0, 0);
  if (nascendo > 0) { if (!CENA.coberto) passarQuadroOvo(); return; }
  desenharIconeGrade(cx, g, x, y, larg * u);
  if (e.saude < .3) marcaSaude(cx, K);
}

/* com a cena 3D ligada (cena3d.ts), o pet, a plataforma e o ovo sao dela; aqui ficam so os extras, em volta do retangulo do sprite que
   ela informa: a sujeira dos dois lados dos pes, o icone rapido e a marca de saude critica */
function desenharExtras3D(cx: CanvasRenderingContext2D, g: Geo): void {
  const { motor: m, nascendo } = jogoAtual();
  /* o ovo e desenhado pela cena 3D, mas a contagem dos quadros chocando continua daqui (sem ela o ovo nao choca nunca); com um painel
     por cima (o veu), o ovo espera: o nascimento e para ser visto */
  if (nascendo > 0 && !CENA.coberto) passarQuadroOvo();
  const r = CENA.ret; if (!r) return;
  const a = atlasAtual(), pal = paleta(corDominante(m.tracos)), K = g.K;
  const ec = Math.max(2, Math.round(r.h / 40)), pes = r.y + r.h;
  cx.setTransform(ec * K, 0, 0, ec * K, 0, 0);
  for (let i = 0; i < m.e.sujeira; i++) {
    const xc = i < 3 ? r.x - 10 * ec - i * 9 * ec : r.x + r.w + 2 * ec + (i - 3) * 9 * ec;
    desenharGrade(cx, S.coco, Math.round(xc / ec), Math.round((pes - 6 * ec) / ec), { ...pal, d: "#8A5A2B" });
  }
  cx.setTransform(1, 0, 0, 1, 0, 0);
  if (nascendo > 0) return;
  if (a.tipo === "ok") desenharIcone(cx, a, g, r.x, r.y, r.w); else desenharIconeGrade(cx, g, r.x, r.y, r.w);
  if (m.e.saude < .3) marcaSaude(cx, K);
}

/* saude critica: um quadrado vermelho no canto (o aviso em texto fica no painel de detalhes) */
function marcaSaude(cx: CanvasRenderingContext2D, K: number): void {
  cx.fillStyle = "#C8443A"; cx.fillRect(Math.round(12 * K), Math.round(TOPO_LIVRE * K), Math.round(10 * K), Math.round(10 * K));
}

/* o pet do UP: a maior escala inteira que cabe, pes sobre a plataforma, centrado; a caixa do idle e fixa, entao o pet nao pula entre
   quadros. Fora da luta, sem espelhar (guia, secao 5). */
function desenharPetUp(cx: CanvasRenderingContext2D, a: AtlasOk, g: Geo, quadro: number): void {
  const m = jogoAtual().motor, acao = m.acao, nome = chaveSprite(m.forma), [rw, rh] = dimSprite(a.dados, nome), e0 = escalaSprite(), K = g.K;
  const escCss = escalaQueCabe(g, rw, rh), esc = Math.max(e0, Math.floor(escCss * K));
  const w = rw * esc / K, h = rh * esc / K;           /* em px de CSS */
  let x = g.W / 2 - w / 2, y = g.pes - h;
  if (acao === "explorar") x += Math.round(Math.sin(quadro / 3) * w * .6);
  else if (acao === "brincar") { x += Math.round(Math.sin(quadro / 2) * w * .25); y -= (quadro % 4 < 2) ? escCss * 4 : 0; }
  if (acao !== "dormir") desenharSprite(cx, a, nome, x * K, y * K, esc, quadroAgora(a, nome), { sombria: m.sombria });
  else {
    /* dormindo (sono.ts): o quadro parado num canvas a parte, posto achatado e respirando, mais largo, com o pe no chao e o tom apagado */
    const alt = alturaSono(performance.now(), matchMedia("(prefers-reduced-motion: reduce)").matches), larg = 1 + (1 - alt) / 2;
    const tmp = document.createElement("canvas"); tmp.width = rw * esc; tmp.height = rh * esc;
    const gt = tmp.getContext("2d"); if (!gt) throw new Error("canvas 2d indisponível");
    desenharSprite(gt, a, nome, 0, 0, esc, 0, { sombria: m.sombria });
    cx.save(); cx.filter = "brightness(.85) saturate(.85)";
    cx.drawImage(tmp, Math.round((x + w / 2 - w * larg / 2) * K), Math.round((y + h * (1 - alt)) * K), Math.round(w * larg * K), Math.round(h * alt * K));
    cx.restore();
    y += h * (1 - alt);
  }
  desenharIcone(cx, a, g, x, y, w);
  if (m.e.saude < .3) marcaSaude(cx, K);
}
/* icone sobre o pet: o da acao do dono (flash); emote do UP (2x) acima e a direita do sprite */
function desenharIcone(cx: CanvasRenderingContext2D, a: AtlasOk, g: Geo, x: number, y: number, w: number): void {
  const m = jogoAtual().motor, pal = paleta(corDominante(m.tracos)), K = g.K;
  const icone: string | null = flashAtual();
  /* sem acao do dono agora, o pet dormindo solta o "zz" (sono.ts) */
  if (!icone) { if (m.acao === "dormir") desenharZz(cx, K, x, y, w, performance.now(), matchMedia("(prefers-reduced-motion: reduce)").matches, pal); return; }
  if (EMOTE_ICONE[icone]) {
    const [pw0, ph0] = dimSprite(a.dados, EMOTE_ICONE[icone]), es = escalaSprite() * 2, pw = pw0 * es / K, ph = ph0 * es / K;
    desenharSprite(cx, a, EMOTE_ICONE[icone], Math.min(g.W - pw - 6, x + w - 6) * K, Math.max(TOPO_LIVRE, y - ph - 4) * K, es, 0);
    return;
  }
  const ic = S[icone]; if (!ic) throw new Error("icone desconhecido: " + icone);
  const bx = Math.min(g.W - 30, x + w - 4), by = Math.max(TOPO_LIVRE, y - 30);
  cx.setTransform(3 * K, 0, 0, 3 * K, 0, 0);
  cx.fillStyle = "#FFFFFF"; cx.fillRect(Math.round(bx / 3) - 1, Math.round(by / 3) - 1, 9, ic.length + 2);
  desenharGrade(cx, ic, Math.round(bx / 3), Math.round(by / 3), pal);
  cx.setTransform(1, 0, 0, 1, 0, 0);
}
/* sem atlas: icone em grade (o da acao do dono, ou o do que ele faz), acima e a direita do sprite de reserva */
function desenharIconeGrade(cx: CanvasRenderingContext2D, g: Geo, x: number, y: number, w: number): void {
  const m = jogoAtual().motor, pal = paleta(corDominante(m.tracos)), K = g.K;
  const icone: string | null = flashAtual() ?? ICONE_ACAO[m.acao] ?? null;
  if (!icone) return;
  const ic = S[icone]; if (!ic) throw new Error("icone desconhecido: " + icone);
  const bx = Math.min(g.W - 30, x + w - 4), by = Math.max(TOPO_LIVRE, y - 30);
  cx.setTransform(3 * K, 0, 0, 3 * K, 0, 0);
  cx.fillStyle = "#FFFFFF"; cx.fillRect(Math.round(bx / 3) - 1, Math.round(by / 3) - 1, 9, ic.length + 2);
  desenharGrade(cx, ic, Math.round(bx / 3), Math.round(by / 3), pal);
  cx.setTransform(1, 0, 0, 1, 0, 0);
}

export function PalcoPet() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const cv = ref.current; if (!cv) return;
    const cx = cv.getContext("2d"); if (!cx) throw new Error("canvas 2d indisponível");
    let quadro = 0;
    const desenha = () => { desenharPalco(cv, cx, quadro); quadro++; };
    desenha();
    const t = setInterval(desenha, 120);
    return () => clearInterval(t);
  }, []);
  const { motor: m, nascendo } = jogoAtual();
  const nome = nascendo > 0 ? "ovo" : chaveSprite(m.forma);
  return <canvas ref={ref} className="lcd" role="img" aria-label={`Tela do pet: ${nome}`} />;
}
