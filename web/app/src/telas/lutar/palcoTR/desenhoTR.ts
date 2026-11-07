/* O desenho da luta em tempo real no canvas (COMBATE-TR, etapa R3; docs/ESPEC_COMBATE_TR.md, item 7). So apresentacao: le o estado da
   luta (motor/combate_tr, a simulacao refeita da entrada do resultado) e nunca o altera.
   - O cenario e o mapa do UP do lugar (cenasTR.ts); sem a imagem, o chao liso (o palco mostra o aviso).
   - Os lutadores sao os sprites do atlas do jogo (src/atlas.ts) em escala inteira de pixel. Com os clipes carregados (a chave CLIPES_UP ou
     ?clipes_up=1), o clipe segue a acao: Run no avanco, no recuo e na arrancada; Attack_1 nos golpes; Stun no atordoamento; Die no
     nocaute; Idle no resto. Sem os clipes, o Idle de sempre. Clipe que falta num sprite com clipes falha alto (atlas.desenharSprite).
   - O tempo do clipe e o da luta (os passos de 16 ms), nao o do relogio: a mesma luta desenha os mesmos quadros. */
import { CTR_TR, PASSO_TR_MS, type EventoTR, type LadoTR, type LutaTR } from "../../../../motor/index.ts";
import { chaveUp, desenharSprite, dimSprite, quadroDoClipe, type AtlasOk, type Clipe } from "../../../atlas.ts";
import { zoomAtual } from "../../../escala.ts";
import { VISUAL_CENA, prontas, type IdCenaTR } from "./cenasTR.ts";
import { ELEMENTO, elementoDoSprite } from "./elementosTR.ts";
import { GOLPES_RAJADA, VOO, cabecaVisivel, fracaoDaRajada, fracaoDoVoo, pixelsDaCabeca, pixelsDoEstouro, pixelsDoRastro, pontoDoVoo, type GeometriaTR, type PixelTR } from "./projeteisTR.ts";
import { cameraDoQuadro } from "./cameraTR.ts";
import { escuroDoPasso, koDoPasso, pixelsDoKO } from "./nocauteTR.ts";
import { CHAO, alfaDaMarca, pixelsDaCratera, pixelsDaOnda, pixelsDaTelegrafia, pixelsDoArrasto, poeiraDaNuvem, poeiraDoPassoTR, telegrafiaDoPasso } from "./chaoTR.ts";
import { COR_PELE, NOME_POSTURA, POSTURA, efeitoDaPostura, pixelsDaAura, pixelsDoContra, pixelsDoEscudo, pixelsDoIcone, posturaDoLado, type PosturaTR } from "./posturasTR.ts";
import { IMPACTO, COR_FORTE, COR_TINTA, MOVIMENTO, VIDA_NUMERO, clarao, empurraoDoPasso, faiscaDoPasso, pixelsDoTexto, poeiraDoPasso, puloDaQueda, textoDeDano, tremidaDoPasso, type VisualTR } from "./efeitosTR.ts";

/** os efeitos de impacto (so vista) ficam em efeitosTR.ts; estes nomes continuam saindo daqui */
export { aplicarEventosTR, visualNovoTR, type NumeroTR, type VisualTR } from "./efeitosTR.ts";

/** cores do chao liso (o recuo quando o mapa nao carrega) */
const COR = { ceuA: "#cfe6f5", ceuB: "#eaf5fb", chaoA: "#9fcf7a", chaoB: "#8cc068", tinta: "#1d2433", azul: "#2c73e0", vermelho: "#d6336c", cura: "#2f9e44" };
/** os golpes (Attack_1) e os movimentos (Run); as posturas (o icone sobre a cabeca) ficam em posturasTR.ts */
const GOLPES = ["golpe_rapido", "fintar", "pesado", "disparo", "investida"];
const MOVIMENTOS = ["avancar", "recuar"];

/** o icone de postura desenhado no ultimo quadro de cada canvas (px de CSS, o retangulo do icone com a placa): o PalcoTR poe por cima um
    elemento transparente com o nome no title e no leitor de tela */
export interface RotuloTR { lado: number; postura: PosturaTR; nome: string; x: number; y: number; w: number; h: number }
const rotulos = new WeakMap<HTMLCanvasElement, RotuloTR[]>();
export const rotulosDoCanvas = (cv: HTMLCanvasElement): readonly RotuloTR[] => rotulos.get(cv) ?? [];

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

/** desenha pixels de efeito (projeteisTR.ts) em volta de (x, y) px de CSS, na grade dos pixels do sprite: cada pixel de efeito tem
    VOO.pixel pixels do sprite (e px do canvas cada, inteiro), e pelo menos VOO.pixelMinCss px de CSS (um sprite grande deixa a escala em 1);
    dir -1 espelha */
function pintar(cx: CanvasRenderingContext2D, px: readonly PixelTR[], x: number, y: number, g: GeometriaTR, dir: number, uFixo?: number): void {
  const x0 = Math.round(x * g.K), y0 = Math.round(y * g.K), u = uFixo ?? g.e * Math.max(VOO.pixel, Math.ceil(VOO.pixelMinCss * g.K / g.e));
  for (const luz of [true, false]) {
    cx.globalCompositeOperation = luz ? "lighter" : "source-over";
    for (const p of px) if (p.luz === luz) {
      const t = p.tam * u; cx.globalAlpha = p.alfa; cx.fillStyle = p.cor;
      cx.fillRect(x0 + dir * p.dx * u - (dir < 0 ? t - u : 0), y0 + p.dy * u, t, t);
    }
  }
  cx.globalCompositeOperation = "source-over"; cx.globalAlpha = 1;
}

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
  const { K, W, H } = ajustar(cv), Wp = cv.width, Hp = cv.height;
  cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, Wp, Hp);
  const reduzido = movimentoReduzido();
  const passoLuta = c.sim ? c.sim.S.passo : 0, passo = passoLuta + c.visual.extra;
  const xs = c.sim ? c.sim.S.L.map(l => l.x) : [CTR_TR.centro - CTR_TR.entrada, CTR_TR.centro + CTR_TR.entrada];
  /* a camera (E5, cameraTR.ts) e, com ela, a escala inteira dos sprites, o centro de cada lutador e o topo (projeteisTR.ts, geometriaTR: a
     mesma conta que os testes usam). Sem simulacao (a previa), a de sempre */
  const dims: [number, number][] = a ? [c.A, c.B].map(L => dimSprite(a.dados, L.sprite)) : [[28, 48], [28, 48]];
  const { geo, e0 } = cameraDoQuadro(c.sim ? c.visual.cam : null, W, H, K, dims, xs, passoLuta, reduzido), { PES, centros } = geo, Z = geo.s;
  /* para os testes e as capturas: a escala do sprite (px de CSS por pixel do sprite), o zoom do mundo e se o zoom esta na passagem */
  cv.dataset.esc = String(geo.esc); cv.dataset.zoom = Z.toFixed(3); cv.dataset.passagem = Math.abs(Z - geo.e / e0) > 1e-9 ? "1" : "0";
  /* o cenario com o zoom do mundo, em volta da linha dos pes (o chao fica no lugar; o centro e o da camera) */
  cx.setTransform(Z, 0, 0, Z, Math.round(K * (W / 2 - geo.cx * Z)), Math.round(K * PES * (1 - Z)));
  const faltou = desenharCenario(cx, c.cena, Wp, Hp, Math.round(H * .62 * K));
  cx.setTransform(1, 0, 0, 1, 0, 0);
  cx.imageSmoothingEnabled = false;
  /* o nocaute (E5): o cenario escurece; os lutadores e os efeitos vem por cima */
  const koVal = c.koEm.filter((k): k is number => k !== null), koEm = koVal.length ? Math.min(...koVal) : null;
  const escuro = c.sim && koEm !== null ? escuroDoPasso(passo - koEm) : 0;
  if (escuro > 0) { cx.fillStyle = `rgba(4,8,20,${escuro.toFixed(3)})`; cx.fillRect(0, 0, Wp, Hp); }
  cv.dataset.escuro = escuro.toFixed(2);
  /* as sombras */
  cx.fillStyle = "rgba(0,0,0,.35)";
  for (const x of centros) { cx.beginPath(); cx.ellipse(x * K, PES * K, 34 * K * Z, 6 * K * Z, 0, 0, Math.PI * 2); cx.fill(); }
  /* o chao (E3, chaoTR.ts), por baixo dos lutadores: as marcas no piso, a elipse da telegrafia e a onda de choque do pesado. Pixels de chao
     na grade do sprite (CHAO.pixel pixels do sprite cada); as marcas ficam no x da luta (presas ao chao, nao ao lutador) */
  const elementos = [elementoDoSprite(c.A.sprite), elementoDoSprite(c.B.sprite)], uChao = geo.e * CHAO.pixel;
  const meiaChao = (i: number): number => Math.max(3, Math.round(geo.meias[i] * K / uChao));
  const xChao = (i: number, x: number): number => centros[i] + geo.x(x) - geo.x(xs[i]);
  let marcas = 0, telegrafias = 0, prontas = 0, ondas = 0, preparosMeio = 0, carregarMeio = 0;
  if (c.sim) {
    for (const m of c.visual.marcas) {
      if (alfaDaMarca(m, passo) <= 0) continue;
      marcas++;
      if (m.tipo === "cratera") pintar(cx, pixelsDaCratera(m, elementos[1 - m.lado], meiaChao(m.lado), passo), xChao(m.lado, m.x0), PES, geo, 1, uChao);
      else {
        const a = xChao(m.lado, m.x0), b = xChao(m.lado, m.x1), comp = Math.round(Math.abs(b - a) * K / uChao);
        pintar(cx, pixelsDoArrasto(m, comp, passo), a, PES, geo, b >= a ? 1 : -1, uChao);
      }
    }
    c.sim.S.L.forEach((l, i) => {
      const tg = telegrafiaDoPasso(l, passoLuta); if (!tg) return;
      telegrafias++; if (tg.pronto) prontas++;
      if (tg.f >= .35 && tg.f <= .65) { if (tg.tipo === "pesado") preparosMeio++; else carregarMeio++; }
      pintar(cx, pixelsDaTelegrafia(tg, elementos[i], meiaChao(i), passo, reduzido), centros[i], PES, geo, 1, uChao);
    });
    for (const m of c.visual.marcas) if (m.tipo === "cratera") {
      const px = pixelsDaOnda(elementos[1 - m.lado], passo - m.t0, meiaChao(m.lado), reduzido);
      if (px.length) { ondas++; pintar(cx, px, xChao(m.lado, m.x0), PES, geo, 1, uChao); }
    }
  }
  cv.dataset.marcas = String(marcas); cv.dataset.telegrafias = String(telegrafias); cv.dataset.telegrafiasProntas = String(prontas); cv.dataset.ondas = String(ondas);
  /* para as capturas: a elipse no meio do fechamento, no preparo do pesado e no carregar */
  cv.dataset.preparosMeio = String(preparosMeio); cv.dataset.carregarMeio = String(carregarMeio);
  const topo: number[] = [], empurros: number[] = [0, 0];
  /* as posturas (E4, posturasTR.ts): os efeitos de cada lado neste passo, do estado e das batidas; nada aqui empurra (D-EMP-9/11) */
  const efs = c.sim ? c.sim.S.L.map((l, i) => efeitoDaPostura(l, i, passoLuta, c.visual.batidas, reduzido)) : [null, null];
  const nPost = { escudos: 0, escudosAcesos: 0, fantasmas: 0, fantasmasAbertos: 0, auras: 0, contras: 0, claroes: 0, peles: 0 };
  const empAlvo = (i: number): number => reduzido || !c.sim ? 0 : (i ? 1 : -1) * Math.round(empurraoDoPasso(c.visual, passo, i) * Z);
  [c.A, c.B].forEach((L, i) => {
    const x = centros[i], lado = c.sim?.S.L[i] ?? null;
    if (!a) { cx.fillStyle = i ? COR.vermelho : COR.azul; cx.fillRect((x - 14) * K, (PES - 40) * K, 28 * K, 40 * K); topo.push(PES - 44); return; }
    const k = chaveUp(a.dados, L.sprite), s = a.dados.sprites[k], [w, h] = dimSprite(a.dados, L.sprite), e = geo.e;
    /* o Die do nocaute (E5) anda tambem na espera do fim (passo com visual.extra): sem isso ele ficava no primeiro quadro, de pe */
    const { clipe, t } = lado ? clipeDoLado(lado, lado.hp <= 0 ? passo : passoLuta, c.koEm[i]) : { clipe: "Idle" as Clipe, t: performance.now() };
    let iq = 0;
    if (s?.clipes) { const cl = s.clipes[clipe]; if (!cl) throw new Error(`clipe ${clipe} indisponível para ${L.sprite}`); iq = quadroDoClipe(cl.ms, cl.loop, t); }
    else if (s) iq = lado && lado.hp <= 0 ? 0 : Math.floor(t / a.dados.ms_por_quadro) % s.quadros.length;
    if (!s?.clipes && lado && lado.hp <= 0) cx.globalAlpha = .45;
    const opc = { sombria: L.sombra, espelho: i === 1, ...(s?.clipes ? { clipe } : {}) }, dx = Math.round(empAlvo(i) * K);
    empurros[i] = dx / K;
    /* a queda (a v18): quem cai sobe num arco enquanto o motor o desliza para tras; o x e sempre o do motor */
    const dy = reduzido || !lado ? 0 : -Math.round(puloDaQueda(passoLuta, lado.quedaDe, lado.deslizeAte) * Z * K);
    const ef = efs[i], atras = i ? 1 : -1;
    /* a imagem fantasma da esquiva (E4): copias apagadas para tras, na cor do elemento, por baixo do sprite; com o movimento reduzido ficam
       paradas */
    if (ef?.fantasmas.length) {
      nPost.fantasmas++; if (ef.fantasmas[ef.fantasmas.length - 1].dx === POSTURA.fantasmas.length * POSTURA.fantasmaPx) nPost.fantasmasAbertos++;
      const m = 2 * e, f = document.createElement("canvas"); f.width = w * e + 2 * m; f.height = h * e + 2 * m;
      const fx = f.getContext("2d"); if (!fx) throw new Error("canvas 2d indisponível");
      desenharSprite(fx, a, L.sprite, m, m, e, iq, opc);
      fx.globalCompositeOperation = "source-atop"; fx.globalAlpha = POSTURA.fantasmaTinta; fx.fillStyle = ELEMENTO[elementos[i]].meio; fx.fillRect(0, 0, f.width, f.height);
      for (const g of [...ef.fantasmas].reverse()) {
        cx.globalAlpha = g.alfa; cx.drawImage(f, Math.round(x * K - w * e / 2) - m + atras * g.dx * e + dx, Math.round(PES * K - h * e) - m + dy); cx.globalAlpha = 1;
      }
    }
    /* o rastro da investida: copias mais apagadas atras de quem arranca, so no caminho ja feito (desde o x0) */
    const inv = lado?.acao?.nome === "investida" && !lado.acao.feito ? lado.acao : null;
    if (!reduzido && inv && c.sim) MOVIMENTO.rastroAlfa.forEach((alfa, k) => {
      const atras = (k + 1) * MOVIMENTO.rastroPassos * c.sim!.S.C.arrancada, rumo = i ? -1 : 1;
      if (rumo * (lado!.x - inv.x0) < atras) return;
      const xr = centros[i] + geo.x(lado!.x - rumo * atras) - geo.x(lado!.x);
      cx.globalAlpha = alfa; desenharSprite(cx, a, L.sprite, xr * K - w * e / 2, PES * K - h * e, e, iq, opc); cx.globalAlpha = 1;
    });
    const branco = !reduzido && !!c.sim && clarao(c.visual, passo, i);
    if (branco || ef?.pele) {
      /* o clarao (E1): o sprite vira branco (so onde ha pixel) numa folha a parte, na mesma escala inteira. A pele dura (E4): na mesma
         folha, a cor do metal por cima do sprite e uma faixa de luz em diagonal que corre por ele (sem a faixa com o movimento reduzido) */
      const m = 4 * e, f = document.createElement("canvas"); f.width = w * e + 2 * m; f.height = h * e + 2 * m;
      const fx = f.getContext("2d"); if (!fx) throw new Error("canvas 2d indisponível");
      desenharSprite(fx, a, L.sprite, m, m, e, iq, opc);
      fx.globalCompositeOperation = "source-atop";
      if (branco) { fx.fillStyle = "#fff"; fx.fillRect(0, 0, f.width, f.height); }
      else {
        const faixa = ef!.pele!.faixa; nPost.peles++;
        fx.globalAlpha = POSTURA.peleAlfa; fx.fillStyle = COR_PELE.metal; fx.fillRect(0, 0, f.width, f.height);
        if (faixa !== null) {
          /* a faixa: em cada linha de pixels do sprite, POSTURA.peleFaixa pixels, um pixel mais para a esquerda a cada linha para baixo */
          fx.globalAlpha = .85; fx.fillStyle = COR_PELE.faixa;
          const x0 = Math.round(faixa * (w + h + POSTURA.peleFaixa)) - POSTURA.peleFaixa;
          for (let ly = 0; ly < h; ly++) fx.fillRect(m + (x0 - ly) * e, m + ly * e, POSTURA.peleFaixa * e, e);
        }
        fx.globalAlpha = 1;
      }
      cx.imageSmoothingEnabled = false; cx.drawImage(f, Math.round(x * K - w * e / 2) - m + dx, Math.round(PES * K - h * e) - m + dy);
    } else desenharSprite(cx, a, L.sprite, x * K - w * e / 2 + dx, PES * K - h * e + dy, e, iq, opc);
    cx.globalAlpha = 1;
    topo.push(PES - h * e / K);
    if (!ef || !lado) return;
    /* na frente do corpo (do lado do rival), em pixels do sprite: o escudo do defender e o brilho e o clarao do contra-golpe */
    /* o pixel de postura: kp pixels do sprite, e pelo menos POSTURA.pixelMinCss px de CSS (o adulto grande deixa a escala em 1 no celular) */
    const frente = -atras, xc = x + dx / K, yMeio = PES + dy / K - h * e / K / 2, kp = Math.max(1, Math.ceil(POSTURA.pixelMinCss * K / e)), up = e * kp;
    if (ef.escudo) {
      nPost.escudos++; if (ef.escudo.aceso > 0) nPost.escudosAcesos++;
      pintar(cx, pixelsDoEscudo(Math.round(h * POSTURA.escudoAlto / kp), ef.escudo.aceso), xc + frente * geo.meias[i] * POSTURA.escudoFrente, yMeio, geo, frente, up);
    }
    if (ef.contra) {
      nPost.contras++; if (ef.contra.clarao > 0) nPost.claroes++;
      pintar(cx, pixelsDoContra(ef.contra.guarda, ef.contra.clarao, passoLuta, reduzido), xc + frente * geo.meias[i] * VOO.boca, PES + dy / K - h * e / K * VOO.altura, geo, frente, up);
    }
    /* a aura do carregar: faiscas que sobem dos lados do corpo; o anel tracejado no chao e o da E3 (a telegrafia), a aura nao repete */
    if (ef.aura) { nPost.auras++; pintar(cx, pixelsDaAura(elementos[i], Math.round(w * POSTURA.auraMeia / kp), Math.round(h * .8 / kp), passoLuta, reduzido), xc, PES + dy / K, geo, 1, up); }
  });
  /* a poeira nos pes (a v18, a investida e a E3, chaoTR.ts): na corrida e na arrancada, atras de quem corre (na frente, no recuo); no deslize
     do empurrao, na frente de quem e empurrado (o lado de onde veio o golpe); no pouso da queda e no acerto do pesado, uma nuvem para os dois
     lados. Pixels inteiros, sem acaso; sem poeira com o movimento reduzido */
  let poeiras = 0;
  if (!reduzido && c.sim) {
    const ps = Math.max(1, Math.round(2 * K * Z));
    cx.fillStyle = "rgba(214,196,160,.8)";
    for (const f of poeiraDoPassoTR(c.sim, c.visual.marcas, passoLuta)) {
      const i = f.lado, base = f.x === null ? centros[i] : xChao(i, f.x), sinal = f.sentido * (i ? 1 : -1);
      poeiras++;
      if (f.sentido === 0) {
        for (const p of poeiraDaNuvem(f.idade, f.tipo === "pesado")) cx.fillRect(Math.round((base + (Math.sign(p.dx) * 10 + p.dx * 2) * Z) * K), Math.round((PES - (2 + p.dy * 2) * Z) * K), ps * p.tam, ps * p.tam);
        continue;
      }
      /* a corrida levanta menos: duas nuvens menores */
      const nuvens = f.tipo === "corrida" ? poeiraDoPasso(f.idade).slice(0, 2).map(p => ({ ...p, tam: Math.max(1, p.tam - 1) })) : poeiraDoPasso(f.idade);
      for (const p of nuvens) cx.fillRect(Math.round((base + sinal * (14 + p.dx * 2) * Z) * K), Math.round((PES - (2 + p.dy * 2) * Z) * K), ps * p.tam, ps * p.tam);
    }
  }
  cv.dataset.poeiras = String(poeiras);
  /* os projeteis em voo (E2): da boca de quem atira a frente do alvo, na cor e na forma do elemento, com rastro e halo de luz; a cabeca fica
     na tela pelo menos VOO.minVisivel passos (o voo no motor pode durar so 5) */
  let cabecas = 0, meioDoVoo = 0;
  if (c.sim) for (const o of c.visual.voos) {
    const dir = o.de === 0 ? 1 : -1, k = reduzido ? VOO.rastroReduzido : VOO.rastro;
    /* o rastro: as posicoes de 1 a k passos atras; depois do acerto ele se recolhe no ponto do acerto e some em VOO.rastroFica passos */
    if (o.tFim === null || passo < o.tFim + VOO.rastroFica) for (let j = k; j >= 1; j--) {
      const f = fracaoDoVoo(o, passo - j); if (f === null) continue;
      const pt = pontoDoVoo(geo, o.de, f); pintar(cx, pixelsDoRastro(elementos[o.de], j, k, passo, reduzido), pt.x, pt.y, geo, dir);
    }
    if (!cabecaVisivel(o, passo)) continue;
    const f = fracaoDoVoo(o, passo)!, pt = pontoDoVoo(geo, o.de, f); cabecas++;
    if (f >= .3 && f <= .7) meioDoVoo++;
    pintar(cx, pixelsDaCabeca(elementos[o.de], passo, reduzido), pt.x, pt.y, geo, dir);
  }
  /* para os testes e as capturas: as cabecas desenhadas neste quadro e as que estao no meio do caminho */
  /* a rajada dos golpes corpo a corpo que acertam (E2): da boca de quem bateu a frente do alvo, na cor do elemento, com o rastro do voo */
  let rajadas = 0;
  if (c.sim) for (const im of c.visual.impactos) {
    if (!im.golpe || !GOLPES_RAJADA.includes(im.golpe)) continue;
    const de = 1 - im.lado, idade = passo - im.t0, f = fracaoDaRajada(idade); if (f === null) continue;
    /* a rajada e um feixe: o dobro dos pontos do rastro e um pixel de efeito mais grosso, da boca ate a cabeca */
    const dir = de === 0 ? 1 : -1, k = 2 * (reduzido ? VOO.rastroReduzido : VOO.rastro);
    for (let j = k; j >= 1; j--) {
      const fr = Math.max(0, f * (1 - j / (k + 1))), pt = pontoDoVoo(geo, de, fr);
      pintar(cx, pixelsDoRastro(elementos[de], j, k, passo, reduzido).map(p => ({ ...p, tam: p.tam + 1 })), pt.x, pt.y, geo, dir);
    }
    const pt = pontoDoVoo(geo, de, f); pintar(cx, pixelsDaCabeca(elementos[de], passo, reduzido), pt.x, pt.y, geo, dir); rajadas++;
  }
  cv.dataset.rajadas = String(rajadas);
  cv.dataset.projeteis = String(cabecas); cv.dataset.projeteisMeio = String(meioDoVoo);
  /* a postura sobre a cabeca (E4): um icone 7 x 7 em grade de pixel, numa placa escura; o nome fica no title e no leitor de tela (PalcoTR) */
  const rots: RotuloTR[] = [];
  if (c.sim) c.sim.S.L.forEach((l, i) => {
    const p = posturaDoLado(l); if (!p) return;
    const u = geo.e * Math.max(POSTURA.iconePx, Math.ceil(POSTURA.pixelMinCss * K / geo.e)), lado = (POSTURA.icone + 2) * u / K;
    const x0 = Math.round((centros[i] + empurros[i] - lado / 2) * K) / K, y0 = Math.round((topo[i] - POSTURA.iconeAcima - lado) * K) / K;
    /* pintar() conta o deslocamento a partir do canto do pixel (0, 0) do icone; a placa comeca em -1 */
    pintar(cx, pixelsDoIcone(p, elementos[i], i), x0 + u / K, y0 + u / K, geo, 1, u);
    rots.push({ lado: i, postura: p, nome: NOME_POSTURA[p], x: x0, y: y0, w: lado, h: lado });
  });
  rotulos.set(cv, rots);
  cv.dataset.posturas = [0, 1].map(i => rots.find(r => r.lado === i)?.postura ?? "").join(",");
  for (const [k, n] of Object.entries(nPost)) cv.dataset[k] = String(n);
  /* a faisca no ponto do golpe: pixels inteiros na frente do alvo (do lado de quem bateu), na altura do peito */
  if (c.sim) for (const im of c.visual.impactos) {
    const ps = Math.max(1, Math.round(3 * K * Z)), dir = im.lado === 0 ? 1 : -1, xc = Math.round((centros[im.lado] + empurros[im.lado] + dir * 14 * Z) * K), yc = Math.round((PES - (topo.length ? (PES - topo[im.lado]) / 2 : 20)) * K);
    for (const p of faiscaDoPasso(im, passo)) { cx.fillStyle = p.cor; cx.fillRect(xc + p.dx * ps * 2, yc + p.dy * ps * 2, ps * (im.forte ? 2 : 1), ps * (im.forte ? 2 : 1)); }
    /* o estouro na cor do elemento de quem bateu (E2), por cima da faisca */
    pintar(cx, pixelsDoEstouro(elementos[1 - im.lado], passo - im.t0, im.forte, reduzido), xc / K, yc / K, geo, dir);
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
  /* os estouros por elemento ja depois do clarao (E2; para as capturas) */
  cv.dataset.estourosMeio = String(c.sim ? c.visual.impactos.filter(i => passo - i.t0 >= IMPACTO.clarao && passo - i.t0 < VOO.durImpacto - 4).length : 0);
  cv.dataset.tremidaMax = String(Math.max(Number(cv.dataset.tremidaMax ?? 0), Math.abs(t.x), Math.abs(t.y)));
  if (t.x || t.y) {
    const f = document.createElement("canvas"); f.width = cv.width; f.height = cv.height;
    const fx = f.getContext("2d"); if (!fx) throw new Error("canvas 2d indisponível");
    fx.drawImage(cv, 0, 0); cx.setTransform(1, 0, 0, 1, 0, 0); cx.clearRect(0, 0, cv.width, cv.height); cx.drawImage(f, Math.round(t.x * K), Math.round(t.y * K));
  }
  /* o "K.O." (E5): grande no meio do palco, em fonte de pixel com contorno e sombra, depois da tremida (ele nao treme) */
  const ko = c.sim && koEm !== null ? koDoPasso(passo - koEm, Wp, Hp, reduzido) : null;
  cv.dataset.ko = ko ? String(ko.p) : ""; cv.dataset.koPronto = ko?.pronto ? "1" : "0";
  if (ko) {
    const { px, w: kw, h: kh } = pixelsDoKO(), p = ko.p, x0 = ko.cx - Math.round(kw * p / 2), y0 = ko.cy - Math.round(kh * p / 2), o = Math.max(1, Math.round(p / 3));
    cx.fillStyle = "#8a1c2b"; for (const [gx, gy] of px) cx.fillRect(x0 + gx * p + o, y0 + gy * p + 2 * o, p, p);
    cx.fillStyle = COR_TINTA;
    for (const [ox, oy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]) for (const [gx, gy] of px) cx.fillRect(x0 + gx * p + ox * o, y0 + gy * p + oy * o, p, p);
    cx.fillStyle = COR_FORTE; for (const [gx, gy] of px) cx.fillRect(x0 + gx * p, y0 + gy * p, p, p);
    /* o brilho em cima de cada coluna (um terco do pixel), para o K.O. nao ficar chapado */
    cx.fillStyle = "#fff6c2"; for (const [gx, gy] of px) if (!px.some(([a, b]) => a === gx && b === gy - 1)) cx.fillRect(x0 + gx * p, y0 + gy * p, p, o);
  }
  return faltou;
}
