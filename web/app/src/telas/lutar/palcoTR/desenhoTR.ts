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
import { IMPACTO, COR_FORTE, COR_TINTA, MOVIMENTO, VIDA_NUMERO, clarao, empurraoDoPasso, faiscaDoPasso, pixelsDoTexto, poeiraDoPasso, puloDaQueda, textoDeDano, tremidaDoPasso, type VisualTR } from "./efeitosTR.ts";

/** os efeitos de impacto (so vista) ficam em efeitosTR.ts; estes nomes continuam saindo daqui */
export { aplicarEventosTR, visualNovoTR, type NumeroTR, type VisualTR } from "./efeitosTR.ts";

/** cores do chao liso (o recuo quando o mapa nao carrega) */
const COR = { ceuA: "#cfe6f5", ceuB: "#eaf5fb", chaoA: "#9fcf7a", chaoB: "#8cc068", tinta: "#1d2433", azul: "#2c73e0", vermelho: "#d6336c", cura: "#2f9e44" };
/** o chao do motor (combate_tr: 240 +- 190 px) ocupa esta fracao da largura do palco, centrado */
const FRACAO_CHAO = .84;
const ESQ = CTR_TR.centro - CTR_TR.meiaLargura, LARG = 2 * CTR_TR.meiaLargura;
/** os golpes (Attack_1), os movimentos (Run) e as posturas (a etiqueta sobre a cabeca) */
const GOLPES = ["golpe_rapido", "fintar", "pesado", "disparo", "investida"];
const MOVIMENTOS = ["avancar", "recuar"];
const POSTURAS = ["defender", "esquivar", "carregar", "contra_golpe", "preparar_pesado", "marcar", "pele_dura"];

/** o usuario pediu menos movimento: sem tremida, clarao, empurrao nem pausa (os numeros e a faisca ficam) */
export const movimentoReduzido = (): boolean => typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;

/** o clipe do lado agora e o tempo dentro dele (ms da luta) */
export function clipeDoLado(l: LadoTR, passo: number, koEm: number | null): { clipe: Clipe; t: number } {
  if (l.hp <= 0) return { clipe: "Die", t: (passo - (koEm ?? passo)) * PASSO_TR_MS };
  /* a queda do empurrao (a v18): o Stun desde o passo em que caiu, ate levantar */
  if (l.quedaDe >= 0 && passo >= l.quedaDe && passo < l.atordoadoAte) return { clipe: "Stun", t: (passo - l.quedaDe) * PASSO_TR_MS };
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
  const reduzido = movimentoReduzido(), faltou = desenharCenario(cx, c.cena, Wp, Hp, Math.round(H * .62 * K));
  cx.imageSmoothingEnabled = false;
  const passoLuta = c.sim ? c.sim.S.passo : 0, passo = passoLuta + c.visual.extra;
  const xs = c.sim ? c.sim.S.L.map(l => l.x) : [CTR_TR.centro - CTR_TR.entrada, CTR_TR.centro + CTR_TR.entrada];
  const alturas = a ? [c.A, c.B].map(L => dimSprite(a.dados, L.sprite)[1]) : [48, 48];
  /* a escala inteira dos sprites no chao novo (B3, palco a tela inteira): limitada pela altura e tambem pela largura, para os dois nao
     se cobrirem numa tela estreita (390 px: 2; 1280 e 1920 px: 3) */
  const larguraMax = a ? Math.max(...[c.A, c.B].map(L => dimSprite(a.dados, L.sprite)[0])) : 28;
  const escLuta = Math.max(1, Math.min(3, Math.floor(ALT_MAX / Math.max(...alturas)), Math.floor(W / (larguraMax * 1.6))));
  /* o centro de cada lutador na tela (px de CSS): o corpo do motor tem o raio CTR_TR.raio e o sprite e mais largo, entao a frente do sprite
     fica na frente do corpo (o excesso vai para tras) e os dois nao se sobrepoem no contato */
  const larguras = a ? [c.A, c.B].map(L => dimSprite(a.dados, L.sprite)[0]) : [28, 28], raioTela = CTR_TR.raio / LARG * W * FRACAO_CHAO;
  const centros = xs.map((x, i) => { const exc = Math.max(0, larguras[i] * Math.max(1, Math.floor(escLuta * K)) / K / 2 - raioTela); return xTela(x, W) + (i ? exc : -exc); });
  /* as sombras */
  cx.fillStyle = "rgba(0,0,0,.35)";
  for (const x of centros) { cx.beginPath(); cx.ellipse(x * K, PES * K, 34 * K, 6 * K, 0, 0, Math.PI * 2); cx.fill(); }
  const topo: number[] = [], empurros: number[] = [0, 0];
  const empAlvo = (i: number): number => reduzido || !c.sim ? 0 : (i ? 1 : -1) * empurraoDoPasso(c.visual, passo, i);
  [c.A, c.B].forEach((L, i) => {
    const x = centros[i], lado = c.sim?.S.L[i] ?? null;
    if (!a) { cx.fillStyle = i ? COR.vermelho : COR.azul; cx.fillRect((x - 14) * K, (PES - 40) * K, 28 * K, 40 * K); topo.push(PES - 44); return; }
    const k = chaveUp(a.dados, L.sprite), s = a.dados.sprites[k], [w, h] = dimSprite(a.dados, L.sprite), e = Math.max(1, Math.floor(escLuta * K));
    const { clipe, t } = lado ? clipeDoLado(lado, passoLuta, c.koEm[i]) : { clipe: "Idle" as Clipe, t: performance.now() };
    let iq = 0;
    if (s?.clipes) { const cl = s.clipes[clipe]; if (!cl) throw new Error(`clipe ${clipe} indisponível para ${L.sprite}`); iq = quadroDoClipe(cl.ms, cl.loop, t); }
    else if (s) iq = lado && lado.hp <= 0 ? 0 : Math.floor(t / a.dados.ms_por_quadro) % s.quadros.length;
    if (!s?.clipes && lado && lado.hp <= 0) cx.globalAlpha = .45;
    const opc = { sombria: L.sombra, espelho: i === 1, ...(s?.clipes ? { clipe } : {}) }, dx = Math.round(empAlvo(i) * K);
    empurros[i] = dx / K;
    /* a queda (a v18): quem cai sobe num arco enquanto o motor o desliza para tras; o x e sempre o do motor */
    const dy = reduzido || !lado ? 0 : -Math.round(puloDaQueda(passoLuta, lado.quedaDe, lado.deslizeAte) * K);
    /* o rastro da investida: copias mais apagadas atras de quem arranca, so no caminho ja feito (desde o x0) */
    const inv = lado?.acao?.nome === "investida" && !lado.acao.feito ? lado.acao : null;
    if (!reduzido && inv && c.sim) MOVIMENTO.rastroAlfa.forEach((alfa, k) => {
      const atras = (k + 1) * MOVIMENTO.rastroPassos * c.sim!.S.C.arrancada, rumo = i ? -1 : 1;
      if (rumo * (lado!.x - inv.x0) < atras) return;
      const xr = centros[i] + xTela(lado!.x - rumo * atras, W) - xTela(lado!.x, W);
      cx.globalAlpha = alfa; desenharSprite(cx, a, L.sprite, xr * K - w * e / 2, PES * K - h * e, e, iq, opc); cx.globalAlpha = 1;
    });
    if (!reduzido && c.sim && clarao(c.visual, passo, i)) {
      /* o clarao: o sprite vira branco (so onde ha pixel) numa folha a parte, na mesma escala inteira */
      const m = 4 * e, f = document.createElement("canvas"); f.width = w * e + 2 * m; f.height = h * e + 2 * m;
      const fx = f.getContext("2d"); if (!fx) throw new Error("canvas 2d indisponível");
      desenharSprite(fx, a, L.sprite, m, m, e, iq, opc);
      fx.globalCompositeOperation = "source-atop"; fx.fillStyle = "#fff"; fx.fillRect(0, 0, f.width, f.height);
      cx.imageSmoothingEnabled = false; cx.drawImage(f, Math.round(x * K - w * e / 2) - m + dx, Math.round(PES * K - h * e) - m + dy);
    } else desenharSprite(cx, a, L.sprite, x * K - w * e / 2 + dx, PES * K - h * e + dy, e, iq, opc);
    cx.globalAlpha = 1;
    topo.push(PES - h * e / K);
  });
  /* a poeira nos pes (a v18 e a investida): na arrancada, atras de quem arranca; no deslize do empurrao, na frente de quem e empurrado (o
     lado de onde veio o golpe). Pixels inteiros, sem acaso */
  if (!reduzido && c.sim) c.sim.S.L.forEach((l, i) => {
    const inv = l.acao?.nome === "investida" && !l.acao.feito ? l.acao : null, desliza = passoLuta < l.deslizeAte;
    if (!inv && !desliza) return;
    const idade = inv ? passoLuta - inv.inicio : passoLuta - (l.deslizeAte - c.sim!.S.C.empurraoAlvo!.deslize),
      atras = i ? 1 : -1, sinal = inv ? atras : -atras, ps = Math.max(1, Math.round(2 * K));
    cx.fillStyle = "rgba(214,196,160,.8)";
    for (const p of poeiraDoPasso(idade)) cx.fillRect(Math.round((centros[i] + sinal * (14 + p.dx * 2)) * K), Math.round((PES - 2 - p.dy * 2) * K), ps * p.tam, ps * p.tam);
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
  /* a faisca no ponto do golpe: pixels inteiros na frente do alvo (do lado de quem bateu), na altura do peito */
  if (c.sim) for (const im of c.visual.impactos) {
    const ps = Math.max(1, Math.round(3 * K)), dir = im.lado === 0 ? 1 : -1, xc = Math.round((centros[im.lado] + empurros[im.lado] + dir * 14) * K), yc = Math.round((PES - (topo.length ? (PES - topo[im.lado]) / 2 : 20)) * K);
    for (const p of faiscaDoPasso(im, passo)) { cx.fillStyle = p.cor; cx.fillRect(xc + p.dx * ps * 2, yc + p.dy * ps * 2, ps * (im.forte ? 2 : 1), ps * (im.forte ? 2 : 1)); }
  }
  /* os numeros que sobem: o dano em fonte de pixel com contorno (o forte, maior e amarelo); cura, erro e interrompido em texto */
  cx.font = `bold ${Math.round(13 * K)}px system-ui, sans-serif`;
  for (const n of c.visual.numeros) {
    const idade = passo - n.t0, y = (topo[n.lado] - 18 - idade * .6) * K;
    cx.globalAlpha = Math.max(0, 1 - idade / VIDA_NUMERO);
    if (textoDeDano(n)) {
      const { px, w: tw, h: th } = pixelsDoTexto(n.txt), p = Math.max(1, Math.round(K * (n.forte ? 6 : 4)));
      const x0 = Math.round(centros[n.lado] * K - tw * p / 2), y0 = Math.round(y - th * p);
      cx.fillStyle = COR_TINTA;
      for (const [ox, oy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]) for (const [gx, gy] of px) cx.fillRect(x0 + gx * p + ox * Math.max(1, p >> 1), y0 + gy * p + oy * Math.max(1, p >> 1), p, p);
      cx.fillStyle = n.forte ? COR_FORTE : n.cor; for (const [gx, gy] of px) cx.fillRect(x0 + gx * p, y0 + gy * p, p, p);
    } else { cx.fillStyle = n.cor; cx.fillText(n.txt, centros[n.lado] * K, y); }
  }
  cx.globalAlpha = 1;
  /* a tremida do palco: a imagem inteira deslocada em px inteiros (so o canvas; o HUD fica); sem ela com o movimento reduzido */
  const t = reduzido || !c.sim ? { x: 0, y: 0 } : tremidaDoPasso(c.visual, passo);
  cv.dataset.tremida = `${t.x},${t.y}`;
  cv.dataset.impactos = String(c.sim ? c.visual.impactos.filter(i => passo - i.t0 < IMPACTO.durFaisca).length : 0);
  cv.dataset.tremidaMax = String(Math.max(Number(cv.dataset.tremidaMax ?? 0), Math.abs(t.x), Math.abs(t.y)));
  if (t.x || t.y) {
    const f = document.createElement("canvas"); f.width = cv.width; f.height = cv.height;
    const fx = f.getContext("2d"); if (!fx) throw new Error("canvas 2d indisponível");
    fx.drawImage(cv, 0, 0); cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, cv.width, cv.height); cx.drawImage(f, Math.round(t.x * K), Math.round(t.y * K));
  }
  return faltou;
}
