/* Palco do Pet (prancha UpPet; porte do desenharLCD do HTML). Canvas do tamanho da cena (318 px de altura), em
   pixels do aparelho; o sprite entra em escala inteira (ate 3x) sem esticar pelo CSS. Noite, sujeira, sono e o que o pet
   faz vem do motor; o anel de plataforma e o fundo hexagonal do card sao do UP. Sem atlas: placeholders. */
import { useEffect, useRef } from "preact/hooks";
import { OVO, TPD, chaveSprite, corDominante, eNoite } from "../../../motor/index.ts";
import { zoomAtual } from "../../escala.ts";
import { atlasAtual, desenharSprite, dimSprite, escalaSprite, quadroAgora, type AtlasOk } from "../../atlas.ts";
import { S, desenharGrade, gradeDe, paleta } from "../../grades.ts";
import { flashAtual } from "../../flash.ts";
import { jogoAtual, passarQuadroOvo } from "../../jogo.ts";

const W0 = 80, H = 56, CHAO = 46;       /* LCD dos placeholders (sem atlas) */
const ESTRELAS = [[8, 6], [22, 12], [40, 5], [57, 10], [70, 4], [14, 20], [64, 22]];
const ICONE_ACAO: Record<string, string> = { dormir: "zz", chamar_atencao: "exclam", emburrar: "raiva", brincar: "nota", explorar: "pergunta", comer: "carne" };
const EMOTE_ICONE: Record<string, string> = { carne: "emoji_carne", nota: "emoji_nota", exclam: "emoji_exclam", coracao: "emoji_coracao" };

/* icone rapido depois de uma acao do dono (1,4 s): src/flash.ts (o caminho compartilhado das acoes, src/acoes.ts, o dispara) */
export { mostrarFlash } from "../../flash.ts";

/* geometria das pranchas PetTela (cena de 318: anel 212 x 60 com o topo em 226, pes do pet em 242, ate 3x e 150 px) e
   PetTelaDesktop (cena de 468: anel 280 x 79 em 376, pes em 392, ate 4x e 200 px), em px de CSS; titulo translucido ate 36 */
const TOPO_LIVRE = 44;
let ANEL_Y = 226, ANEL_W = 212, ANEL_H = 60, PES_Y = 242, ESC_MAX = 3, ALT_MAX = 150;

/* o canvas cobre a cena inteira; backing store em pixels do aparelho (K = devicePixelRatio x zoom do desktop) */
function ajustarTela(cv: HTMLCanvasElement): { K: number; W: number } {
  const pai = cv.parentElement, W = pai && pai.clientWidth > 0 ? pai.clientWidth : 382, H = pai && pai.clientHeight > 0 ? pai.clientHeight : 318, K = (devicePixelRatio || 1) * zoomAtual();
  const grande = H >= 400;
  [ANEL_Y, ANEL_W, ANEL_H, PES_Y, ESC_MAX, ALT_MAX] = grande ? [376, 280, 79, 392, 4, 200] : [226, 212, 60, 242, 3, 150];
  const bw = Math.round(W * K), bh = Math.round(H * K);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; cv.style.width = W + "px"; cv.style.height = H + "px"; }
  return { K, W };
}

function desenharPalco(cv: HTMLCanvasElement, cx: CanvasRenderingContext2D, quadro: number): void {
  const { motor: m, nascendo } = jogoAtual(), e = m.e, noite = eNoite(e.tick % TPD);
  const { K, W } = ajustarTela(cv), a = atlasAtual(), pal = paleta(corDominante(m.tracos));
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, cv.width, cv.height); cx.imageSmoothingEnabled = false;
  if (a.tipo === "ok") {
    /* o fundo hexagonal e do card (CSS); a noite escurece a cena e acende estrelas */
    if (noite) {
      cx.fillStyle = "rgba(11,22,54,.55)"; cx.fillRect(0, 0, cv.width, cv.height);
      cx.fillStyle = "#E8ECFF";
      for (const [x, y] of ESTRELAS) if ((quadro + x) % 23 !== 0) cx.fillRect(Math.round(x / W0 * W * K), Math.round((40 + y * 5) * K), Math.round(3 * K), Math.round(3 * K));
    }
    /* anel de plataforma (peca pintada do UP, nao pixel art): no tamanho da prancha, com suavizacao */
    const r = a.dados.pecas.anel_plataforma;
    if (!r) throw new Error("peça do atlas ausente: anel_plataforma");
    cx.imageSmoothingEnabled = true;
    cx.drawImage(a.img, r[0], r[1], r[2], r[3], Math.round((W - ANEL_W) / 2 * K), Math.round(ANEL_Y * K), Math.round(ANEL_W * K), Math.round(ANEL_H * K));
    cx.imageSmoothingEnabled = false;
    /* sujeira (motor): a grade do coco em 3x, dos dois lados do anel */
    cx.setTransform(3 * K, 0, 0, 3 * K, 0, 0);
    for (let i = 0; i < e.sujeira; i++) {
      const xc = i < 3 ? (W - ANEL_W) / 2 - 20 - i * 26 : (W + ANEL_W) / 2 + 4 + (i - 3) * 26;
      desenharGrade(cx, S.coco, Math.round(xc / 3), Math.round((PES_Y - 4) / 3), { ...pal, d: "#8A5A2B" });
    }
    cx.setTransform(1, 0, 0, 1, 0, 0);
    if (nascendo > 0) {
      const oscil = nascendo % 2 ? 3 : -3, [ow, oh] = dimSprite(a.dados, OVO[m.especie]), eo = escalaSprite();
      desenharSprite(cx, a, OVO[m.especie], (W / 2 + oscil) * K - ow * eo / 2, PES_Y * K - oh * eo, eo, 0);
      passarQuadroOvo(); return;
    }
    desenharPetUp(cx, a, K, W, quadro);
    return;
  }
  /* sem atlas: a cena original em placeholders, no LCD de 80 x 56 unidades centrado na cena */
  const u = W / W0, y0 = (cv.height / K - H * u) / 2;
  cx.setTransform(u * K, 0, 0, u * K, 0, y0 * K);
  cx.fillStyle = noite ? "#1F2A4A" : "#BFE3D6"; cx.fillRect(0, 0, W0, H);
  if (noite) {
    cx.fillStyle = "#E8ECFF"; for (const [x, y] of ESTRELAS) if ((quadro + x) % 23 !== 0) cx.fillRect(x, y, 1, 1);
    cx.fillStyle = "#F5E7A8"; cx.fillRect(66, 8, 5, 5); cx.fillStyle = "#1F2A4A"; cx.fillRect(68, 7, 4, 4);
  } else { cx.fillStyle = "#FFFFFF"; cx.fillRect(10, 9, 10, 2); cx.fillRect(12, 8, 6, 1); cx.fillRect(52, 14, 12, 2); cx.fillRect(55, 13, 6, 1); }
  cx.fillStyle = noite ? "#2E3B5E" : "#8FC49A"; cx.fillRect(0, CHAO, W0, H - CHAO);
  cx.fillStyle = noite ? "#26324F" : "#7BB388"; for (let x = (quadro % 2); x < W0; x += 4) cx.fillRect(x, CHAO + 3, 2, 1);
  for (let i = 0; i < e.sujeira; i++) desenharGrade(cx, S.coco, 4 + i * 8 + (i > 2 ? 34 : 0), CHAO - 4, { ...pal, d: "#8A5A2B" });
  if (nascendo > 0) { desenharGrade(cx, S.ovo, 34 + (nascendo % 2 ? 1 : -1), CHAO - 14 + 2, pal); passarQuadroOvo(); return; }
  const g = S[gradeDe(m.estagioAtual)], larg = Math.max(...g.map(l => l.length)), alt = g.length;
  let x = Math.round(W0 / 2 - larg / 2), y = CHAO - alt + 2;
  const acao = m.acao;
  if (acao === "explorar") x += Math.round(Math.sin(quadro / 3) * 14);
  else if (acao === "brincar") { x += Math.round(Math.sin(quadro / 2) * 6); y -= (quadro % 4 < 2) ? 3 : 0; }
  else if (acao !== "dormir") y -= (quadro % 4 < 2) ? 1 : 0;
  desenharGrade(cx, g, x, y, pal, { olhosFechados: acao === "dormir" || (quadro % 17 === 0), espelho: acao === "explorar" && Math.cos(quadro / 3) < 0 });
  desenharIconeGrade(cx, x, y, larg, noite);
  if (e.saude < .3) { cx.fillStyle = "#C8443A"; cx.fillRect(2, 2, 3, 3); }
}

/* o pet do UP: escala inteira ate 3x (a maior que cabe entre o titulo e o anel), pes sobre o anel, centrado; a caixa
   do idle e fixa, entao o pet nao pula entre quadros. Fora da luta, sem espelhar (guia, secao 5). */
function desenharPetUp(cx: CanvasRenderingContext2D, a: AtlasOk, K: number, W: number, quadro: number): void {
  const m = jogoAtual().motor, acao = m.acao, nome = chaveSprite(m.forma), [rw, rh] = dimSprite(a.dados, nome), e0 = escalaSprite();
  const escCss = Math.max(1, Math.min(ESC_MAX, Math.floor(Math.min(PES_Y - TOPO_LIVRE, ALT_MAX) / rh))), esc = Math.max(e0, Math.floor(escCss * K));
  const w = rw * esc / K, h = rh * esc / K;           /* em px de CSS */
  let x = W / 2 - w / 2, y = PES_Y - h;
  if (acao === "explorar") x += Math.round(Math.sin(quadro / 3) * 60);
  else if (acao === "brincar") { x += Math.round(Math.sin(quadro / 2) * 28); y -= (quadro % 4 < 2) ? 12 : 0; }
  desenharSprite(cx, a, nome, x * K, y * K, esc, quadroAgora(a, nome, acao === "dormir"), { sombria: m.sombria });
  desenharIcone(cx, a, K, W, x, y, w);
  if (m.e.saude < .3) { cx.fillStyle = "#C8443A"; cx.fillRect(Math.round(8 * K), Math.round(44 * K), Math.round(8 * K), Math.round(8 * K)); }
}
/* icone sobre o pet: o da acao do dono (flash); emote do UP (2x) acima e a direita do sprite */
function desenharIcone(cx: CanvasRenderingContext2D, a: AtlasOk, K: number, W: number, x: number, y: number, w: number): void {
  const m = jogoAtual().motor, pal = paleta(corDominante(m.tracos));
  /* PetTela: sem icone fixo da acao (o que ele faz fica no porque); so o icone rapido depois de uma acao do dono */
  const icone: string | null = flashAtual();
  if (!icone) return;
  if (EMOTE_ICONE[icone]) {
    const [pw0, ph0] = dimSprite(a.dados, EMOTE_ICONE[icone]), es = escalaSprite() * 2, pw = pw0 * es / K, ph = ph0 * es / K;
    desenharSprite(cx, a, EMOTE_ICONE[icone], Math.min(W - pw - 6, x + w - 6) * K, Math.max(TOPO_LIVRE, y - ph - 4) * K, es, 0);
    return;
  }
  const ic = S[icone]; if (!ic) throw new Error("icone desconhecido: " + icone);
  const bx = Math.min(W - 30, x + w - 4), by = Math.max(TOPO_LIVRE, y - 30);
  cx.setTransform(3 * K, 0, 0, 3 * K, 0, 0);
  cx.fillStyle = "#FFFFFF"; cx.fillRect(Math.round(bx / 3) - 1, Math.round(by / 3) - 1, 9, ic.length + 2);
  desenharGrade(cx, ic, Math.round(bx / 3), Math.round(by / 3), pal);
  cx.setTransform(1, 0, 0, 1, 0, 0);
}
/* sem atlas: icone em grade, nas unidades do LCD */
function desenharIconeGrade(cx: CanvasRenderingContext2D, x: number, y: number, w: number, noite: boolean): void {
  const m = jogoAtual().motor, pal = paleta(corDominante(m.tracos));
  const icone: string | null = flashAtual() ?? ICONE_ACAO[m.acao] ?? null;
  if (!icone) return;
  const ic = S[icone]; if (!ic) throw new Error("icone desconhecido: " + icone);
  const bx = Math.round(Math.min(W0 - 9, x + w - 1)), by = Math.round(Math.max(1, y - 9));
  cx.fillStyle = noite ? "#E8ECFF" : "#FFFFFF"; cx.fillRect(bx - 1, by - 1, 9, ic.length + 2);
  desenharGrade(cx, ic, bx, by, pal);
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
  return <canvas ref={ref} class="lcd" width={W0} height={H} role="img" aria-label={`Tela do pet: ${nome}`} />;
}
