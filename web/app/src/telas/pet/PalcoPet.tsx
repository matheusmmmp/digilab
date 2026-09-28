/* Palco do Pet (desenho UpPet; porte do desenharLCD do HTML). Unidades do LCD (80 x 56) com K pixels do aparelho
   por unidade; o sprite entra em escala inteira (ate 3x) sem esticar pelo CSS. Noite, sujeira, sono e o que o pet
   faz vem do motor; o anel de plataforma e o fundo hexagonal do card sao do UP. Sem atlas: placeholders. */
import { useEffect, useRef } from "preact/hooks";
import { OVO, TPD, chaveSprite, corDominante, eNoite } from "../../../motor/index.ts";
import { atlasAtual, desenharSprite, dimSprite, escalaSprite, quadroAgora, type AtlasOk } from "../../atlas.ts";
import { S, desenharGrade, gradeDe, paleta } from "../../grades.ts";
import { Deco, fundoDeco } from "../../componentes/Deco.tsx";
import { jogoAtual, passarQuadroOvo, useJogo } from "../../jogo.ts";

const W = 80, H = 56, CHAO = 46;
const ESTRELAS = [[8, 6], [22, 12], [40, 5], [57, 10], [70, 4], [14, 20], [64, 22]];
const ICONE_ACAO: Record<string, string> = { dormir: "zz", chamar_atencao: "exclam", emburrar: "raiva", brincar: "nota", explorar: "pergunta", comer: "carne" };
const EMOTE_ICONE: Record<string, string> = { carne: "emoji_carne", nota: "emoji_nota", exclam: "emoji_exclam", coracao: "emoji_coracao" };

/* icone rapido depois de uma acao do dono (1,4 s); so apresentacao */
let flash: { icone: string; ate: number } | null = null;
export function mostrarFlash(icone: string): void { flash = { icone, ate: performance.now() + 1400 }; }

/* canvas em unidades uw x uh; a largura toda em pixels do aparelho, K pode ser fracionario */
const escalas = new WeakMap<HTMLCanvasElement, number>();
function ajustarTela(cv: HTMLCanvasElement, uw: number, uh: number): number {
  const pai = cv.parentElement, K0 = escalas.get(cv);
  if (!pai) return K0 ?? 4;
  const cs = getComputedStyle(pai), livre = pai.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  if (!(livre > 0)) { if (!K0) { escalas.set(cv, 4); cv.width = uw * 4; cv.height = uh * 4; } return escalas.get(cv)!; }
  const dpr = devicePixelRatio || 1, px = Math.max(uw, Math.floor(livre * dpr)), K = px / uw, larg = (px / dpr) + "px";
  if (K0 === K && cv.width === px && cv.style.width === larg) return K;
  escalas.set(cv, K); cv.width = px; cv.height = Math.round(uh * K);
  cv.style.width = larg; cv.style.height = (cv.height / dpr) + "px";
  return K;
}

function desenharPalco(cv: HTMLCanvasElement, cx: CanvasRenderingContext2D, quadro: number): void {
  const { motor: m, nascendo } = jogoAtual(), e = m.e, noite = eNoite(e.tick % TPD);
  const K = ajustarTela(cv, W, H), a = atlasAtual(), pal = paleta(corDominante(m.tracos));
  cx.setTransform(K, 0, 0, K, 0, 0); cx.imageSmoothingEnabled = false;
  if (a.tipo === "ok") {
    /* fundo do card (hexagonos) aparece por tras; anel de plataforma no chao */
    cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, cv.width, cv.height);
    if (noite) {
      cx.fillStyle = "rgba(11,22,54,.55)"; cx.fillRect(0, 0, cv.width, cv.height);
      cx.fillStyle = "#E8ECFF"; for (const [x, y] of ESTRELAS) if ((quadro + x) % 23 !== 0) cx.fillRect(x * K, y * K, K, K);
    }
    /* anel de plataforma (peca pintada do UP, nao pixel art): reduzido para caber, com suavizacao */
    const r = a.dados.pecas.anel_plataforma;
    if (!r) throw new Error("peça do atlas ausente: anel_plataforma");
    const aw = Math.round(W * K * .8), ah = Math.round(aw * r[3] / r[2]);
    cx.imageSmoothingEnabled = true; cx.drawImage(a.img, r[0], r[1], r[2], r[3], Math.round((W * K - aw) / 2), Math.round(CHAO * K - ah * .55), aw, ah); cx.imageSmoothingEnabled = false;
    cx.setTransform(K, 0, 0, K, 0, 0);
    for (let i = 0; i < e.sujeira; i++) desenharGrade(cx, S.coco, 4 + i * 8 + (i > 2 ? 34 : 0), CHAO - 4, { ...pal, d: "#8A5A2B" });
    if (nascendo > 0) {
      const oscil = nascendo % 2 ? 1 : -1, [ow, oh] = dimSprite(a.dados, OVO[m.especie]), eo = escalaSprite();
      desenharSprite(cx, a, OVO[m.especie], (W * K - ow * eo) / 2 + oscil * K, (CHAO + 2) * K - oh * eo, eo, 0);
      passarQuadroOvo(); return;
    }
    desenharPetUp(cx, a, K, noite, quadro);
    return;
  }
  /* sem atlas: a cena original em placeholders */
  cx.fillStyle = noite ? "#1F2A4A" : "#BFE3D6"; cx.fillRect(0, 0, W, H);
  if (noite) {
    cx.fillStyle = "#E8ECFF"; for (const [x, y] of ESTRELAS) if ((quadro + x) % 23 !== 0) cx.fillRect(x, y, 1, 1);
    cx.fillStyle = "#F5E7A8"; cx.fillRect(66, 8, 5, 5); cx.fillStyle = "#1F2A4A"; cx.fillRect(68, 7, 4, 4);
  } else { cx.fillStyle = "#FFFFFF"; cx.fillRect(10, 9, 10, 2); cx.fillRect(12, 8, 6, 1); cx.fillRect(52, 14, 12, 2); cx.fillRect(55, 13, 6, 1); }
  cx.fillStyle = noite ? "#2E3B5E" : "#8FC49A"; cx.fillRect(0, CHAO, W, H - CHAO);
  cx.fillStyle = noite ? "#26324F" : "#7BB388"; for (let x = (quadro % 2); x < W; x += 4) cx.fillRect(x, CHAO + 3, 2, 1);
  for (let i = 0; i < e.sujeira; i++) desenharGrade(cx, S.coco, 4 + i * 8 + (i > 2 ? 34 : 0), CHAO - 4, { ...pal, d: "#8A5A2B" });
  if (nascendo > 0) { desenharGrade(cx, S.ovo, 34 + (nascendo % 2 ? 1 : -1), CHAO - 14 + 2, pal); passarQuadroOvo(); return; }
  const g = S[gradeDe(m.estagioAtual)], larg = Math.max(...g.map(l => l.length)), alt = g.length;
  let x = Math.round(W / 2 - larg / 2), y = CHAO - alt + 2;
  const acao = m.acao;
  if (acao === "explorar") x += Math.round(Math.sin(quadro / 3) * 14);
  else if (acao === "brincar") { x += Math.round(Math.sin(quadro / 2) * 6); y -= (quadro % 4 < 2) ? 3 : 0; }
  else if (acao !== "dormir") y -= (quadro % 4 < 2) ? 1 : 0;
  desenharGrade(cx, g, x, y, pal, { olhosFechados: acao === "dormir" || (quadro % 17 === 0), espelho: acao === "explorar" && Math.cos(quadro / 3) < 0 });
  desenharIcone(cx, null, K, noite, x, y, larg);
  if (e.saude < .3) { cx.fillStyle = "#C8443A"; cx.fillRect(2, 2, 3, 3); }
}

/* o pet do UP: posicoes em unidades do LCD, sprite no tamanho nativo (escala inteira ate 3x); a caixa do idle e
   fixa, entao o pet nao pula entre quadros. Fora da luta, sem espelhar (guia, secao 5). */
function desenharPetUp(cx: CanvasRenderingContext2D, a: AtlasOk, K: number, noite: boolean, quadro: number): void {
  const m = jogoAtual().motor, acao = m.acao, nome = chaveSprite(m.forma), [rw, rh] = dimSprite(a.dados, nome), e0 = escalaSprite();
  const esc = e0 * Math.max(1, Math.min(3, Math.floor(40 * K / (rh * e0)))), w = rw * esc / K, h = rh * esc / K;
  let x = W / 2 - w / 2, y = CHAO - h + 2;
  if (acao === "explorar") x += Math.round(Math.sin(quadro / 3) * 14);
  else if (acao === "brincar") { x += Math.round(Math.sin(quadro / 2) * 6); y -= (quadro % 4 < 2) ? 3 : 0; }
  desenharSprite(cx, a, nome, x * K, y * K, esc, quadroAgora(a, nome, acao === "dormir"), { sombria: m.sombria });
  desenharIcone(cx, a, K, noite, x, y, w);
  if (m.e.saude < .3) { cx.fillStyle = "#C8443A"; cx.fillRect(2, 2, 3, 3); }
}
/* icone sobre o pet: o da acao do dono (flash) ou o do que ele faz; emote do UP onde existe */
function desenharIcone(cx: CanvasRenderingContext2D, a: AtlasOk | null, K: number, noite: boolean, x: number, y: number, w: number): void {
  const m = jogoAtual().motor, pal = paleta(corDominante(m.tracos));
  let icone: string | null = flash && flash.ate > performance.now() ? flash.icone : ICONE_ACAO[m.acao] ?? null;
  if (a && icone && EMOTE_ICONE[icone]) {
    const [pw0, ph0] = dimSprite(a.dados, EMOTE_ICONE[icone]), es = escalaSprite() * 2, pw = pw0 * es / K, ph = ph0 * es / K;
    desenharSprite(cx, a, EMOTE_ICONE[icone], Math.min(W - pw - 1, x + w - 2) * K, Math.max(1, y - ph - 1) * K, es, 0);
    icone = null;
  }
  if (icone) {
    const ic = S[icone]; if (!ic) throw new Error("icone desconhecido: " + icone);
    const bx = Math.round(Math.min(W - 9, x + w - 1)), by = Math.round(Math.max(1, y - 9));
    cx.fillStyle = noite ? "#E8ECFF" : "#FFFFFF"; cx.fillRect(bx - 1, by - 1, 9, ic.length + 2);
    desenharGrade(cx, ic, bx, by, pal);
  }
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
  const { motor: m, nascendo } = useJogo(), ovo = nascendo > 0;
  const nome = ovo ? "ovo" : chaveSprite(m.forma), padrao = ovo ? fundoDeco("Icon_Pattern_2") : undefined;
  /* ovo chocando: padrao de ovos do UP bem claro e o anel de Digivice girando atras (parado com movimento reduzido) */
  return (
    <div class={`lcd-caixa${ovo ? " lcd-caixa--ovo" : ""}`}>
      {padrao && <span class="ovo-padrao" style={{ "--padrao": padrao }} aria-hidden="true" />}
      {ovo && <Deco nome="Digivice_Circle_01" class="ovo-anel gira" />}
      <canvas ref={ref} class="lcd" width={W} height={H} role="img" aria-label={`Tela do pet: ${nome}${ovo ? ", chocando" : ""}`} />
    </div>
  );
}
