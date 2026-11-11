/* O estado visual da luta da POC (LUTA_POC, LP3; docs/TAREFA_V3_LUTA_POC.md, secao 3.3a): os efeitos da LUTA_EFEITOS (E1 a E5) ligados aos
   eventos da simulacao de motor/arena/. So apresentacao e puro (sem DOM): tudo sai dos eventos de cada passo e do estado da luta (a Luta da
   simulacao, refeita da mesma entrada), nunca do relogio do navegador; a mesma luta desenha os mesmos efeitos. Nada aqui muda a luta, o
   log nem o replay. O desenho em canvas fica em desenhoPoc.ts.

   Os efeitos e o evento que dispara cada um (secao 3.3a):
   - E1: a pausa curta, o clarao branco, a tremida, a faisca e os numeros de dano (o maior e amarelo e o critico e a habilidade): cada `dano`,
     corpo a corpo ou projetil; o empurrao e o da propria simulacao (ACAO.empurrao), que ja move o alvo: o desenho do recuo (a poeira, o
     arrasto e, no empurrao grande do Ringue, o pulo) vem por cima dele;
   - E2: os projeteis em voo (L.projeteis), com o rastro e o brilho do elemento por baixo do desenho do jogo; o projetil nosso (LP-8, que a LP3b pos no nucleo) voa do mesmo jeito e so fica marcado;
   - E3: a elipse que se fecha na preparacao da habilidade, a onda de choque e a marca no acerto dela, a poeira na corrida;
   - E4: a imagem fantasma no desvio (o dash da POC) e a aura com a habilidade pronta e na runa do Castelo;
   - E5: a barra com o dano atrasado, a camera lenta e o "K.O." no nocaute, a camera que acompanha os dois no chao 2D. */
import { EQ_POC, GOLPES_DA_POC, PASSO_POC_MS, type DadosFormaPoc, type EventoPoc, type LutaPoc, type LutadorPoc } from "../../../../motor/index.ts";
import { IMPACTO, COR_AZUL, COR_CURA, COR_TINTA, COR_VERMELHO } from "./efeitos.ts";
import { anotarVidaTR, vidasNovasTR, type VidaTR } from "./nocaute.ts";
import { VOO } from "./projeteis.ts";
import { CHAO, type MarcaTR } from "./chao.ts";

export type LadoN = 0 | 1;
export const passoDe = (L: LutaPoc): number => Math.round(L.relogio / PASSO_POC_MS);
export const ladoN = (l: "a" | "b"): LadoN => (l === "a" ? 0 : 1);
export const lutadorN = (L: LutaPoc, i: LadoN): LutadorPoc => (i === 0 ? L.a : L.b);

/** um acerto: quem levou, quando, quanto (fracao da vida maxima), se foi forte (o critico, a habilidade ou um golpe grande), onde (o mundo da
    luta, os pes do alvo) e de que lado veio (dir 1: o golpe veio da esquerda e empurra para a direita) */
export interface ImpactoPoc { lado: LadoN; t0: number; frac: number; forte: boolean; crit: boolean; hab: boolean; x: number; y: number; dir: 1 | -1; de: LadoN }
/** um numero que sobe: no mundo da luta (os pes de quem levou), em fonte de pixel (dano) ou em texto (esquiva, runa, fora do ringue) */
export interface NumeroPoc { txt: string; cor: string; t0: number; lado: LadoN; x: number; y: number; forte: boolean; pixel: boolean }
/** um efeito de acerto do jogo (o prefab do `hits`, dos dados do Digimon UP), no ponto do alvo; t0 ja com o atraso dele */
export interface EfeitoJogoPoc { prefab: string; t0: number; lado: LadoN; x: number; y: number; espelho: boolean }
/** um voo: o projetil da simulacao (nosso: o tiro da LP-8), com a cabeca a cada passo desde t0 (no mundo, ja na altura
    do peito), o prefab que voa e o fim (o passo em que acertou, foi bloqueado ou saiu do alcance).
    LP3c, so desenho: a cada ponto tambem os pes do alvo naquele passo (alvos) e a fracao do caminho ate o acerto (f: 0 na boca do motor,
    1 no acerto; nunca desce), e o atirador no disparo (tiro: os pes, o lado e o tempo do ataque, para achar a frente do sprite no quadro
    do disparo). O desenho leva a cabeca da frente do sprite (f 0) a borda do alvo (f 1); os pontos do motor nao mudam. No voo que nasce e
    acerta no mesmo passo (a simulacao nunca o pos em L.projeteis), o voo e montado do dano (sintetico) */
export interface VooPoc {
  de: LadoN; t0: number; pts: { x: number; y: number }[]; prefab: string | null; esq: boolean; tFim: number | null; nosso: boolean; acertou: boolean;
  alvos: { x: number; y: number }[]; f: number[]; tiro: { x: number; y: number; esq: boolean; t: number }; sintetico: boolean;
}
/** uma marca no piso (E3): a cratera da habilidade e o arrasto do empurrao grande, no mundo; o MarcaTR (lado, t0, ate) da a opacidade */
export interface MarcaPoc { m: MarcaTR; x: number; y: number; x1: number; y1: number }
/** a camera (E5): o centro (no mundo) e o nivel de zoom, com a passagem de um nivel para o outro */
export interface CameraPoc { cx: number; cy: number; nivel: number; nivelDe: number; trocaEm: number }
/** um aviso da regra do mapa (a arena fecha, a tempestade, a runa, a queda do ringue): sai no palco por alguns segundos */
export interface AvisoPoc { txt: string; t0: number }

export interface VisualPoc {
  numeros: NumeroPoc[]; impactos: ImpactoPoc[]; efeitos: EfeitoJogoPoc[]; voos: VooPoc[]; marcas: MarcaPoc[];
  /** as posicoes recentes de cada lado (os pes, no mundo), para a imagem fantasma do desvio e o rastro da investida */
  hist: { x: number; y: number }[][];
  /** o passo em que cada lado comecou a correr (null parado) e em que foi empurrado pela ultima vez */
  correndoDe: (number | null)[]; empurradoEm: number[];
  /** a pausa pedida pelos acertos e ainda nao consumida pelo agendador do quadro (ms) */
  pausaMs: number;
  /** passos de efeito depois do fim (a espera do fim conta quadros): os efeitos usam passo + extra e acabam de sumir */
  extra: number;
  vidas: VidaTR[]; cam: CameraPoc | null; koEm: (number | null)[]; avisos: AvisoPoc[];
}
export const visualNovoPoc = (): VisualPoc => ({
  numeros: [], impactos: [], efeitos: [], voos: [], marcas: [], hist: [[], []], correndoDe: [null, null], empurradoEm: [-1e9, -1e9], pausaMs: 0, extra: 0,
  vidas: vidasNovasTR(), cam: null, koEm: [null, null], avisos: [],
});

/** Os numeros desta tela. PROPOSTOS, SEM FONTE: ajustar nas capturas.
    - vidaNumero: os passos de um numero na tela; vidaAviso: os de um aviso da regra do mapa;
    - hist: quantos passos de posicao cada lado guarda; dashMin: a distancia (mundo) por passo a partir da qual o rastro da investida aparece;
    - empurraoGrande: o empurrao (mundo) a partir do qual o desenho poe o arrasto e o pulo (o Ringue empurra o dobro, e 7 vezes na habilidade);
    - durDeslize: os passos da poeira do empurrao; durEfeitoMax: o teto de passos de um efeito do jogo (o prefab) guardado. */
export const TELA_POC = { vidaNumero: 45, vidaAviso: 150, hist: 12, dashMin: 2.2, empurraoGrande: 11, durDeslize: 12, durEfeitoMax: 60 } as const;

/** A camera (E5). PROPOSTO, SEM FONTE: os limiares de distancia (mundo) para o nivel 1 e o 2 de zoom, a histerese, a suavidade do centro por
    passo e os passos da passagem de um nivel para o outro */
export const CAMERA_POC = { limiares: [210, 120], histerese: 18, suave: .08, troca: 18 } as const;

/** a boca (o peito, na frente do corpo) de um lutador, no mundo */
export const bocaDe = (u: LutadorPoc): { x: number; y: number } => ({ x: u.x + (u.viraEsq ? -1 : 1) * EQ_POC.raio, y: u.y - EQ_POC.peito });

/** o nivel de zoom para a distancia d (no mundo) entre os dois, com histerese em volta do nivel atual */
export function nivelDaDistanciaPoc(d: number, atual: number): number {
  const [l1, l2] = CAMERA_POC.limiares, h = CAMERA_POC.histerese;
  const alvo = d < l2 ? 2 : d < l1 ? 1 : 0;
  if (alvo === atual) return atual;
  /* so troca quando passa do limiar com folga */
  if (alvo > atual) return d < (atual === 0 ? l1 : l2) - h ? Math.min(alvo, atual + 1) : atual;
  return d > (atual === 2 ? l2 : l1) + h ? Math.max(alvo, atual - 1) : atual;
}

/** os eventos de um passo (ja aplicados na Luta: o estado e o do fim do passo) viram os efeitos; chamado uma vez por passo, na ordem */
export function aplicarEventosPoc(v: VisualPoc, L: LutaPoc, ev: readonly EventoPoc[], formas: readonly [DadosFormaPoc, DadosFormaPoc]): void {
  const t = passoDe(L);
  for (const e of ev) {
    if (e.tipo === "dano") {
      const i = ladoN(e.alvo.lado), alvo = lutadorN(L, i), frac = e.valor / alvo.st.hp, forte = e.crit || e.hab || frac >= IMPACTO.fracaoPesado;
      const dir: 1 | -1 = e.espelho ? -1 : 1;
      v.impactos.push({ lado: i, t0: t, frac, forte, crit: e.crit, hab: e.hab, x: e.x, y: e.y, dir, de: ladoN(e.at.lado) });
      v.pausaMs = Math.max(v.pausaMs, forte ? IMPACTO.pausaMs : Math.round(IMPACTO.pausaMs / 2));
      v.numeros.push({ txt: "-" + e.valor, cor: i === 0 ? COR_VERMELHO : COR_AZUL, t0: t, lado: i, x: e.x + e.dx / 4, y: e.y, forte, pixel: true });
      if (e.mult > 1) v.numeros.push({ txt: "eficaz!", cor: COR_CURA, t0: t, lado: i, x: e.x, y: e.y - 12, forte: false, pixel: false });
      anotarVidaTR(v.vidas[i], t, e.resta + e.perda, e.resta, alvo.st.hp, true);
      for (const h of e.hits) v.efeitos.push({ prefab: h.prefab, t0: t + Math.round(h.atraso * 1000 / PASSO_POC_MS), lado: i, x: e.x, y: e.y, espelho: e.espelho });
      /* o empurrao da simulacao ja moveu o alvo (o x do evento e o de antes): o grande ganha o arrasto e o pulo; todo empurrao, a poeira */
      v.empurradoEm[i] = t;
      const dx = alvo.x - e.x, dy = alvo.y - e.y, d = Math.sqrt(dx * dx + dy * dy);
      if (!alvo.morto && d >= TELA_POC.empurraoGrande)
        v.marcas.push({ m: { tipo: "arrasto", lado: i, t0: t, x0: e.x, x1: alvo.x, ate: t + TELA_POC.durDeslize }, x: e.x, y: e.y, x1: alvo.x, y1: alvo.y });
      /* a habilidade que acerta: a cratera e a onda de choque (E3) */
      if (e.hab) v.marcas.push({ m: { tipo: "cratera", lado: i, t0: t, x0: e.x, x1: e.x, ate: t }, x: e.x, y: e.y, x1: e.x, y1: e.y });
    } else if (e.tipo === "esquiva") {
      const i = ladoN(e.alvo.lado);
      v.numeros.push({ txt: "esquivou", cor: COR_TINTA, t0: t, lado: i, x: e.x, y: e.y, forte: false, pixel: false });
    } else if (e.tipo === "ambiente") {
      const i = ladoN(e.u.lado), u = lutadorN(L, i);
      anotarVidaTR(v.vidas[i], t, u.hp + e.perda, u.hp, u.st.hp, true);
      if (e.mostrar) v.numeros.push({ txt: "-" + e.mostrar.valor, cor: "#ff8a4c", t0: t, lado: i, x: e.mostrar.x, y: e.mostrar.y, forte: false, pixel: true });
    } else if (e.tipo === "runa") {
      const i = ladoN(e.u.lado);
      v.numeros.push({ txt: "poder da runa!", cor: "#c9a6ff", t0: t, lado: i, x: e.x, y: e.y - 10, forte: false, pixel: false });
      v.avisos.push({ txt: "Runa: +30% de dano por 8 s", t0: t });
    } else if (e.tipo === "queda_ringue") {
      const i = ladoN(e.u.lado), u = lutadorN(L, i);
      v.numeros.push({ txt: "fora do ringue!", cor: "#ff8a4c", t0: t, lado: i, x: u.x, y: u.y - 10, forte: false, pixel: false });
    } else if (e.tipo === "arena_fecha") v.avisos.push({ txt: "A arena fecha: fora da área segura, a vida cai", t0: t });
    else if (e.tipo === "tempestade") v.avisos.push({ txt: "Tempestade: os tiros ficam lentos e a mira piora", t0: t });
    else if (e.tipo === "pilar" && e.quebrou) v.avisos.push({ txt: "Um pilar quebrou", t0: t });
    else if (e.tipo === "queda") {
      const i = ladoN(e.u.lado); if (v.koEm[i] === null) v.koEm[i] = t;
    }
  }
  seguirProjeteis(v, L, t);
  for (const i of [0, 1] as const) {
    const u = lutadorN(L, i), h = v.hist[i];
    h.unshift({ x: u.x, y: u.y }); if (h.length > TELA_POC.hist) h.pop();
    v.correndoDe[i] = u.estado === "run" ? v.correndoDe[i] ?? t : null;
  }
  seguirCamera(v, L);
  v.numeros = v.numeros.filter(n => t - n.t0 < TELA_POC.vidaNumero);
  v.impactos = v.impactos.filter(i => t - i.t0 < Math.max(IMPACTO.durMax, VOO.durImpacto, CHAO.durOnda + CHAO.ondaAtraso));
  v.efeitos = v.efeitos.filter(x => t - x.t0 < TELA_POC.durEfeitoMax);
  v.marcas = v.marcas.filter(x => t - x.m.ate < CHAO.durMarca);
  v.voos = v.voos.filter(o => o.tFim === null || t - o.tFim < VOO.rastroFica);
  v.avisos = v.avisos.filter(a => t - a.t0 < TELA_POC.vidaAviso);
}

/** os projeteis da simulacao: abre o voo de quem apareceu, anota a cabeca de quem segue e fecha o de quem saiu (acertou, bateu num obstaculo
    ou passou do alcance). Os objetos de projetil da simulacao so servem de chave, num mapa fora do estado visual */
const seguidos = new WeakMap<VisualPoc, Map<{ x: number; y: number }, VooPoc>>();
/** a distancia (mundo) do centro do peito do alvo em que o motor acerta o projetil (motor/arena/sim.ts: o.raio + 6) */
export const ACERTO_MOTOR = 6;
/** a fracao do caminho ate o acerto num ponto: o que ja voou sobre o que voou mais o que falta ate o raio de acerto do alvo; nunca desce */
function fracaoDoVoo(o: VooPoc, p: { x: number; y: number }, alvo: LutadorPoc): number {
  const p0 = o.pts[0], voou = Math.hypot(p.x - p0.x, p.y - p0.y);
  const falta = Math.max(0, Math.hypot(alvo.x - p.x, alvo.y - EQ_POC.peito - p.y) - alvo.raio - ACERTO_MOTOR);
  const f = voou + falta > 0 ? voou / (voou + falta) : 1;
  return Math.max(o.f.length ? o.f[o.f.length - 1] : 0, Math.min(1, f));
}
/** o projetil nosso (LP-8, a LP3b no nucleo): o tiro das formas que atiram o proprio efeito de acerto. Voa como os outros, pela simulacao;
    so fica marcado (o data-nossos do canvas) */
export const PREFABS_LP8: ReadonlySet<string> = new Set(Object.values(GOLPES_DA_POC).flatMap(g => g.hits.map(h => h.prefab)));
function seguirProjeteis(v: VisualPoc, L: LutaPoc, t: number): void {
  let m = seguidos.get(v); if (!m) { m = new Map(); seguidos.set(v, m); }
  const vivos = new Set<{ x: number; y: number }>(L.projeteis);
  for (const pr of L.projeteis) {
    let o = m.get(pr);
    if (!o) {
      /* a simulacao ja moveu o projetil no passo em que nasceu: o voo comeca na boca de quem atirou */
      const de = ladoN(pr.de.lado), b = bocaDe(pr.de), alvo = lutadorN(L, de === 0 ? 1 : 0);
      const prefab = pr.dados.proj?.prefab ?? null;
      o = { de, t0: t - 1, pts: [b], prefab, esq: pr.esq, tFim: null, nosso: prefab !== null && PREFABS_LP8.has(prefab), acertou: false,
        alvos: [{ x: alvo.x, y: alvo.y }], f: [0], tiro: { x: pr.de.x, y: pr.de.y, esq: pr.de.viraEsq, t: pr.de.t }, sintetico: false };
      m.set(pr, o); v.voos.push(o);
    }
    const alvo = lutadorN(L, o.de === 0 ? 1 : 0), p = { x: pr.x, y: pr.y };
    o.f.push(fracaoDoVoo(o, p, alvo)); o.alvos.push({ x: alvo.x, y: alvo.y }); o.pts.push(p);
  }
  for (const [pr, o] of m) if (!vivos.has(pr)) {
    /* saiu no passo de agora: acertou se o alvo levou dano neste passo (o impacto acabou de entrar) */
    o.tFim = t;
    const im = v.impactos.find(i => i.t0 === t && i.de === o.de);
    o.acertou = !!im;
    /* o acerto e o ultimo ponto do voo (o desenho o leva a borda do alvo, onde ele estava antes do empurrao) */
    if (im) { o.pts.push({ x: pr.x, y: pr.y }); o.alvos.push({ x: im.x, y: im.y }); o.f.push(1); }
    m.delete(pr);
  }
  /* o tiro que nasce e acerta no mesmo passo: a simulacao nunca o pos em L.projeteis; o voo sai do dano (da boca ao acerto) */
  for (const im of v.impactos) if (im.t0 === t && !v.voos.some(o => o.de === im.de && o.tFim === t)) {
    const at = lutadorN(L, im.de), dados = im.hab ? at.sk : at.g; if (!dados.proj) continue;
    const prefab = dados.proj.prefab ?? null, b = bocaDe(at);
    v.voos.push({ de: im.de, t0: t - 1, pts: [b, { x: im.x - im.dir * (EQ_POC.raio + ACERTO_MOTOR), y: im.y - EQ_POC.peito }], prefab, esq: im.dir < 0, tFim: t,
      nosso: prefab !== null && PREFABS_LP8.has(prefab), acertou: true, alvos: [{ x: im.x, y: im.y }, { x: im.x, y: im.y }], f: [0, 1],
      tiro: { x: at.x, y: at.y, esq: at.viraEsq, t: at.t }, sintetico: true });
  }
}

/** O ritmo dos tiros (LP3c, so desenho). PROPOSTO, SEM FONTE: ajustar nas capturas.
    - janela: os passos antes do disparo e antes do acerto em que a tela anda devagar (lentos passos por quadro), para o voo curto (1 a 3
      passos) aparecer em quadros desenhados; a luta, os passos e o fim sao os mesmos. */
export const RITMO_TIRO = { janela: 3, lentos: 1 } as const;
/** os passos deste quadro da tela com um tiro perto de sair ou de acertar: no maximo RITMO_TIRO.lentos; senao, base. Le so o estado da luta */
export function passosDoTiro(L: LutaPoc, base: number): number {
  const lim = RITMO_TIRO.janela * PASSO_POC_MS;
  for (const u of [L.a, L.b]) {
    if (u.morto || u.estado !== "attack" || u.golpeDado) continue;
    const g = u.usandoHab ? u.sk : u.g;
    if (g.proj && g.t * 1000 - u.t <= lim) return Math.min(base, RITMO_TIRO.lentos);
  }
  for (const pr of L.projeteis) {
    const o = pr.de.lado === "a" ? L.b : L.a, vel = Math.hypot(pr.vx, pr.vy) * PASSO_POC_MS / 1000;
    const falta = Math.max(0, Math.hypot(o.x - pr.x, o.y - EQ_POC.peito - pr.y) - o.raio - ACERTO_MOTOR);
    if (vel > 0 && falta / vel <= RITMO_TIRO.janela) return Math.min(base, RITMO_TIRO.lentos);
  }
  return base;
}

function seguirCamera(v: VisualPoc, L: LutaPoc): void {
  const vivos = [L.a, L.b].filter(u => !u.foraAte);
  const xs = vivos.map(u => u.x), ys = vivos.map(u => u.y - EQ_POC.peito);
  const mx = xs.length ? (Math.min(...xs) + Math.max(...xs)) / 2 : 240, my = ys.length ? (Math.min(...ys) + Math.max(...ys)) / 2 : 150;
  const d = vivos.length === 2 ? Math.sqrt((L.a.x - L.b.x) ** 2 + ((L.a.y - L.b.y) / .6) ** 2) : 0;
  const t = passoDe(L);
  if (!v.cam) { v.cam = { cx: mx, cy: my, nivel: 0, nivelDe: 0, trocaEm: -1e9 }; return; }
  const c = v.cam;
  c.cx += (mx - c.cx) * CAMERA_POC.suave; c.cy += (my - c.cy) * CAMERA_POC.suave;
  const n = nivelDaDistanciaPoc(d, c.nivel);
  if (n !== c.nivel) { c.nivelDe = c.nivel; c.nivel = n; c.trocaEm = t; }
}

/** o zoom do quadro (em niveis, fracionario na passagem); com o movimento reduzido, seco */
export function nivelDoQuadro(c: CameraPoc | null, passo: number, reduzido: boolean): number {
  if (!c) return 0;
  if (reduzido) return c.nivel;
  const f = Math.min(1, (passo - c.trocaEm) / CAMERA_POC.troca);
  return c.nivelDe + (c.nivel - c.nivelDe) * f;
}

/** a pausa pedida desde a ultima chamada (ms), zerando o pedido; 0 com o movimento reduzido */
export function consumirPausaPoc(v: VisualPoc, reduzido: boolean): number { const p = reduzido ? 0 : v.pausaMs; v.pausaMs = 0; return p; }

const vivos = (v: VisualPoc, passo: number): ImpactoPoc[] => v.impactos.filter(i => passo >= i.t0 && passo - i.t0 < IMPACTO.durMax);
/** a tremida do palco neste passo (a mesma conta da E1): em px inteiros de CSS, limitada a IMPACTO.tremidaMaxPx em cada eixo */
export function tremidaPoc(v: VisualPoc, passo: number): { x: number; y: number } {
  let x = 0, y = 0;
  for (const i of vivos(v, passo)) {
    const idade = passo - i.t0; if (idade >= IMPACTO.durTremida) continue;
    const mag = Math.max(1, Math.round(Math.min(1, i.frac / IMPACTO.fracaoTremidaMax) * IMPACTO.tremidaMaxPx)) * (1 - idade / IMPACTO.durTremida);
    const s = Math.floor(idade / 2) % 2 ? -1 : 1;
    x += s * Math.round(mag); y += -s * Math.round(mag / 2);
  }
  const lim = (n: number) => Math.max(-IMPACTO.tremidaMaxPx, Math.min(IMPACTO.tremidaMaxPx, n));
  return { x: lim(x), y: lim(y) };
}
/** o lado esta branco (o clarao da E1) neste passo? */
export const claraoPoc = (v: VisualPoc, passo: number, lado: LadoN): boolean => vivos(v, passo).some(i => i.lado === lado && passo - i.t0 < IMPACTO.clarao);

/** a fracao da preparacao da habilidade (a elipse da E3: 0 aberta, 1 fechada) ou null fora dela */
export function preparoDaHabilidade(u: LutadorPoc): { f: number; pronto: boolean } | null {
  if (u.morto || u.estado !== "attack" || !u.usandoHab || u.golpeDado) return null;
  const f = Math.max(0, Math.min(1, u.t / Math.max(1, u.sk.t * 1000)));
  return { f, pronto: f >= .8 };
}

/** o pulo (para cima, no mundo) de quem foi empurrado forte: um arco que sobe e volta ao chao em TELA_POC.durDeslize passos */
export function puloDoEmpurrao(v: VisualPoc, lado: LadoN, passo: number): number {
  const m = v.marcas.find(x => x.m.tipo === "arrasto" && x.m.lado === lado && passo >= x.m.t0 && passo < x.m.ate);
  if (!m) return 0;
  const f = (passo - m.m.t0) / (m.m.ate - m.m.t0);
  return Math.round(8 * 4 * f * (1 - f));
}

/** os passos da luta neste quadro da tela: os de sempre, ou 1 nos ultimos 36 de uma luta que acaba em nocaute (a camera lenta da E5) */
export { passosDoQuadro, passosDaEspera, barraDoPasso, escuroDoPasso, koDoPasso, pixelsDoKO, NOCAUTE } from "./nocaute.ts";
