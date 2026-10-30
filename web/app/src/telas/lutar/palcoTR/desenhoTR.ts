/* O desenho da luta em tempo real no canvas (COMBATE-TR, etapa R3; docs/ESPEC_COMBATE_TR.md, item 7). So apresentacao: le o estado da
   luta (motor/combate_tr, a simulacao refeita da entrada do resultado) e nunca o altera.
   - O cenario e o mapa do UP do lugar (cenasTR.ts); sem a imagem, o chao liso (o palco mostra o aviso).
   - Os lutadores sao os sprites do atlas do jogo (src/atlas.ts) em escala inteira de pixel. Com os clipes carregados (a chave CLIPES_UP ou
     ?clipes_up=1), o clipe segue a acao: Run no avanco, no recuo e na arrancada; Attack_1 nos golpes; Stun no atordoamento; Die no
     nocaute; Idle no resto. Sem os clipes, o Idle de sempre. Clipe que falta num sprite com clipes falha alto (atlas.desenharSprite).
   - O tempo do clipe e o da luta (os passos de 16 ms), nao o do relogio: a mesma luta desenha os mesmos quadros. */
import { CTR_TR, NOME_V2, PASSO_TR_MS, type EventoTR, type LadoTR, type LutaTR } from "../../../../motor/index.ts";
import { chaveUp, desenharSprite, dimSprite, quadroDoClipe, type AtlasOk, type Clipe } from "../../../atlas.ts";
import { zoomAtual } from "../../../escala.ts";
import { VISUAL_CENA, prontas, type IdCenaTR } from "./cenasTR.ts";

/** cores do chao liso (o recuo quando o mapa nao carrega) */
const COR = { ceuA: "#cfe6f5", ceuB: "#eaf5fb", chaoA: "#9fcf7a", chaoB: "#8cc068", tinta: "#1d2433", azul: "#2c73e0", vermelho: "#d6336c", cura: "#2f9e44" };
/** o chao do motor (combate_tr: 240 +- 190 px) ocupa esta fracao da largura do palco, centrado */
const FRACAO_CHAO = .84;
const ESQ = CTR_TR.centro - CTR_TR.meiaLargura, LARG = 2 * CTR_TR.meiaLargura;
/** os golpes (Attack_1), os movimentos (Run) e as posturas (a etiqueta sobre a cabeca) */
const GOLPES = ["golpe_rapido", "fintar", "pesado", "disparo", "investida"];
const MOVIMENTOS = ["avancar", "recuar"];
const POSTURAS = ["defender", "esquivar", "carregar", "contra_golpe", "preparar_pesado", "marcar", "pele_dura"];

/** os numeros que sobem (dano, cura, erro) e somem: o tempo de cada um em passos da luta */
export interface NumeroTR { txt: string; cor: string; t0: number; lado: number }
export interface VisualTR { numeros: NumeroTR[] }
export const visualNovoTR = (): VisualTR => ({ numeros: [] });
const VIDA_NUMERO = 45;   /* passos (~0,7 s) */

/** os eventos de um passo viram numeros sobre quem levou */
export function aplicarEventosTR(v: VisualTR, sim: LutaTR, ev: readonly EventoTR[]): void {
  for (const e of ev) {
    if (e.tipo === "dano") v.numeros.push({ txt: "-" + Math.round(e.valor * 10) / 10, cor: e.lado === 0 ? COR.vermelho : COR.azul, t0: e.t, lado: e.lado });
    else if (e.tipo === "cura") v.numeros.push({ txt: "+" + Math.round(e.valor), cor: COR.cura, t0: e.t, lado: e.lado });
    else if (e.tipo === "erro") v.numeros.push({ txt: "errou", cor: COR.tinta, t0: e.t, lado: e.lado });
    else if (e.tipo === "interrompe") v.numeros.push({ txt: "interrompido!", cor: COR.tinta, t0: e.t, lado: e.lado });
  }
  v.numeros = v.numeros.filter(n => sim.S.passo - n.t0 < VIDA_NUMERO);
}

/** o clipe do lado agora e o tempo dentro dele (ms da luta) */
export function clipeDoLado(l: LadoTR, passo: number, koEm: number | null): { clipe: Clipe; t: number } {
  if (l.hp <= 0) return { clipe: "Die", t: (passo - (koEm ?? passo)) * PASSO_TR_MS };
  if (passo < l.atordoadoAte) return { clipe: "Stun", t: (passo - (l.atordoadoAte - CTR_TR.atordoaInterrupcao)) * PASSO_TR_MS };
  const a = l.acao;
  if (a && a.nome === "investida" && !a.feito) return { clipe: "Run", t: (passo - a.inicio) * PASSO_TR_MS };
  if (a && GOLPES.includes(a.nome)) return { clipe: "Attack_1", t: (passo - a.inicio) * PASSO_TR_MS };
  if (a && MOVIMENTOS.includes(a.nome)) return { clipe: "Run", t: (passo - a.inicio) * PASSO_TR_MS };
  return { clipe: "Idle", t: passo * PASSO_TR_MS };
}

export interface LutadorDesenho { sprite: string; sombra?: boolean; nomeTela: string }
export interface CenaDesenho { cena: IdCenaTR; A: LutadorDesenho; B: LutadorDesenho; sim: LutaTR | null; visual: VisualTR; koEm: (number | null)[] }

function ajustar(cv: HTMLCanvasElement): { K: number; W: number; H: number } {
  const pai = cv.parentElement, W = pai && pai.clientWidth > 0 ? pai.clientWidth : 390, H = pai && pai.clientHeight > 0 ? pai.clientHeight : 300;
  const K = (devicePixelRatio || 1) * zoomAtual(), bw = Math.round(W * K), bh = Math.round(H * K);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; cv.style.width = W + "px"; cv.style.height = H + "px"; }
  return { K, W, H };
}
const xTela = (x: number, W: number): number => W * (1 - FRACAO_CHAO) / 2 + (x - ESQ) / LARG * W * FRACAO_CHAO;

/** o cenario: o ceu (degrade), o fundo do mapa e o piso; devolve se faltou alguma imagem do mapa */
function desenharCenario(cx: CanvasRenderingContext2D, id: IdCenaTR, Wp: number, Hp: number, chao: number): boolean {
  const v = VISUAL_CENA[id], [c1, c2] = v.ceu ?? [COR.ceuA, COR.ceuB];
  const g = cx.createLinearGradient(0, 0, 0, chao); g.addColorStop(0, c1); g.addColorStop(1, c2);
  cx.fillStyle = g; cx.fillRect(0, 0, Wp, chao);
  const fundo = v.fundo ? prontas.get(v.fundo) : undefined, piso = v.piso ? prontas.get(v.piso) : undefined;
  cx.imageSmoothingEnabled = true;
  if (fundo && v.fundoCobre) { const s = Math.max(Wp / fundo.width, chao / fundo.height); cx.drawImage(fundo, (Wp - fundo.width * s) / 2, chao - fundo.height * s, fundo.width * s, fundo.height * s); }
  else if (fundo && v.fundoAlt) { const alt = chao * .55, larg = fundo.width * alt / fundo.height; for (let x = 0; x < Wp; x += larg) cx.drawImage(fundo, x, chao - alt, larg, alt); }
  if (piso) { const s = Math.max(Wp / piso.width, (Hp - chao) / piso.height); cx.drawImage(piso, (Wp - piso.width * s) / 2, chao, piso.width * s, piso.height * s); }
  else {
    cx.fillStyle = COR.chaoA; cx.fillRect(0, chao, Wp, Hp - chao);
    cx.fillStyle = COR.chaoB; for (let x = 0; x < Wp; x += Wp / 12) cx.fillRect(x, chao, Wp / 24, Hp - chao);
  }
  return (!!v.fundo && fundo === null) || (!!v.piso && piso === null);
}

/** desenha a luta (ou a previa, sem simulacao: os dois no comeco, em Idle). Devolve se faltou imagem do mapa (o palco avisa) */
export function desenharLutaTR(cv: HTMLCanvasElement, c: CenaDesenho, a: AtlasOk | null): boolean {
  const cx = cv.getContext("2d"); if (!cx) throw new Error("canvas 2d indisponível");
  const { K, W, H } = ajustar(cv), Wp = cv.width, Hp = cv.height, PES = H * .8, ALT_MAX = H * .45;
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, Wp, Hp);
  const faltou = desenharCenario(cx, c.cena, Wp, Hp, Math.round(H * .62 * K));
  cx.imageSmoothingEnabled = false;
  const passo = c.sim ? c.sim.S.passo : 0;
  const xs = c.sim ? c.sim.S.L.map(l => l.x) : [CTR_TR.centro - CTR_TR.entrada, CTR_TR.centro + CTR_TR.entrada];
  const alturas = a ? [c.A, c.B].map(L => dimSprite(a.dados, L.sprite)[1]) : [48, 48];
  const escLuta = Math.max(1, Math.min(3, Math.floor(ALT_MAX / Math.max(...alturas))));
  /* o centro de cada lutador na tela (px de CSS): o corpo do motor tem o raio CTR_TR.raio e o sprite e mais largo, entao a frente do sprite
     fica na frente do corpo (o excesso vai para tras) e os dois nao se sobrepoem no contato */
  const larguras = a ? [c.A, c.B].map(L => dimSprite(a.dados, L.sprite)[0]) : [28, 28], raioTela = CTR_TR.raio / LARG * W * FRACAO_CHAO;
  const centros = xs.map((x, i) => { const exc = Math.max(0, larguras[i] * Math.max(1, Math.floor(escLuta * K)) / K / 2 - raioTela); return xTela(x, W) + (i ? exc : -exc); });
  /* as sombras */
  cx.fillStyle = "rgba(0,0,0,.35)";
  for (const x of centros) { cx.beginPath(); cx.ellipse(x * K, PES * K, 34 * K, 6 * K, 0, 0, Math.PI * 2); cx.fill(); }
  const topo: number[] = [];
  [c.A, c.B].forEach((L, i) => {
    const x = centros[i], lado = c.sim?.S.L[i] ?? null;
    if (!a) { cx.fillStyle = i ? COR.vermelho : COR.azul; cx.fillRect((x - 14) * K, (PES - 40) * K, 28 * K, 40 * K); topo.push(PES - 44); return; }
    const k = chaveUp(a.dados, L.sprite), s = a.dados.sprites[k], [w, h] = dimSprite(a.dados, L.sprite), e = Math.max(1, Math.floor(escLuta * K));
    const { clipe, t } = lado ? clipeDoLado(lado, passo, c.koEm[i]) : { clipe: "Idle" as Clipe, t: performance.now() };
    let iq = 0;
    if (s?.clipes) { const cl = s.clipes[clipe]; if (!cl) throw new Error(`clipe ${clipe} indisponível para ${L.sprite}`); iq = quadroDoClipe(cl.ms, cl.loop, t); }
    else if (s) iq = lado && lado.hp <= 0 ? 0 : Math.floor(t / a.dados.ms_por_quadro) % s.quadros.length;
    if (!s?.clipes && lado && lado.hp <= 0) cx.globalAlpha = .45;
    desenharSprite(cx, a, L.sprite, x * K - w * e / 2, PES * K - h * e, e, iq, { sombria: L.sombra, espelho: i === 1, ...(s?.clipes ? { clipe } : {}) });
    cx.globalAlpha = 1;
    topo.push(PES - h * e / K);
  });
  /* os projeteis em voo */
  if (c.sim) for (const pr of c.sim.S.projeteis) {
    cx.fillStyle = pr.de === 0 ? COR.azul : COR.vermelho;
    cx.beginPath(); cx.arc(xTela(pr.x, W) * K, (PES - 28) * K, 5 * K, 0, Math.PI * 2); cx.fill();
  }
  /* a postura sobre a cabeca (defende, esquiva, prepara o pesado...) */
  cx.font = `${Math.round(11 * K)}px system-ui, sans-serif`; cx.textAlign = "center";
  if (c.sim) c.sim.S.L.forEach((l, i) => {
    const nome = l.prep ? "pesado!" : l.acao && POSTURAS.includes(l.acao.nome) ? NOME_V2[l.acao.nome] ?? l.acao.nome : null;
    if (!nome || l.hp <= 0) return;
    const x = centros[i] * K, y = (topo[i] - 6) * K;
    cx.fillStyle = "rgba(255,255,255,.85)"; const m = cx.measureText(nome).width; cx.fillRect(x - m / 2 - 4 * K, y - 12 * K, m + 8 * K, 16 * K);
    cx.fillStyle = COR.tinta; cx.fillText(nome, x, y);
  });
  /* os numeros que sobem */
  cx.font = `bold ${Math.round(13 * K)}px system-ui, sans-serif`;
  for (const n of c.visual.numeros) {
    const idade = passo - n.t0, y = (topo[n.lado] - 18 - idade * .6) * K;
    cx.globalAlpha = Math.max(0, 1 - idade / VIDA_NUMERO);
    cx.fillStyle = n.cor; cx.fillText(n.txt, centros[n.lado] * K, y);
  }
  cx.globalAlpha = 1;
  return faltou;
}
