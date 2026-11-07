/* Os efeitos de impacto da luta em tempo real (LUTA_EFEITOS, etapa E1; docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 3.5). So apresentacao:
   tudo sai dos eventos `dano` e `acao` e do `passo` da luta, nunca do relogio do navegador; a mesma luta desenha os mesmos efeitos. Nada
   aqui toca o motor, o log, o replay nem o ResultadoLutaTR. Este arquivo e puro (sem DOM): o desenho fica em desenhoTR.ts. */
import type { EventoTR, LutaTR } from "../../../../motor/index.ts";
import { VOO, seguirProjeteisTR, type VooTR } from "./projeteisTR.ts";
import { seguirChaoTR, type MarcaTR } from "./chaoTR.ts";

/** A forca do impacto (D-LE-2 da tarefa). PROPOSTO, SEM FONTE: ajustar nas capturas da E1.
    - pausaMs: a pausa do desenho no acerto (a luta nao para; so o proximo quadro demora); o pesado pausa o dobro do leve.
    - tremidaMaxPx: a tremida do palco no maximo, em px inteiros de CSS.
    - clarao: quantos passos da luta o alvo fica branco (2 quadros da tela de 48 ms = 6 passos de 16 ms).
    - empurraoPx: o quanto o alvo e empurrado (volta no fim), em px inteiros de CSS, no leve e no pesado.
    - duracoes (em passos): da tremida, do empurrao e da faisca; durMax e o maior deles.
    - fracaoPesado: fracao da vida maxima do alvo a partir da qual o acerto conta como forte mesmo sem ser o pesado. */
export const IMPACTO = {
  pausaMs: 70, tremidaMaxPx: 4, clarao: 6, empurraoPx: [2, 5], durTremida: 8, durEmpurrao: 10, durFaisca: 10, durMax: 12, fracaoPesado: .12,
  /** o dano (fracao da vida maxima do alvo) que chega ao tremor maximo */
  fracaoTremidaMax: .15,
} as const;

/** um acerto desenhavel: quem levou, quando (passo da luta), quanto (fracao da vida maxima do alvo) e se foi forte; motor: o motor empurrou
    o alvo neste acerto (o empurrao de verdade da v18, LUTA_EMPURRAO): o empurrao so visual acima nao entra, para nao somar dois */
export interface ImpactoTR { lado: number; t0: number; frac: number; forte: boolean; motor?: boolean; golpe?: string }

/** os numeros que sobem (dano, cura, erro) e somem: o tempo de cada um em passos da luta */
export interface NumeroTR { txt: string; cor: string; t0: number; lado: number; forte?: boolean }
export interface VisualTR {
  numeros: NumeroTR[]; impactos: ImpactoTR[];
  /** o ultimo golpe que cada lado comecou (para saber se o acerto veio do pesado) */
  ultimoGolpe: string[];
  /** a pausa pedida pelos acertos ainda nao consumida pelo agendador do quadro (ms) */
  pausaMs: number;
  /** passos de efeito depois do fim da luta (a espera do fim conta quadros, nao o relogio): os efeitos usam passo + extra e acabam de sumir */
  extra: number;
  /** os voos dos projeteis (E2, projeteisTR.ts): lidos do estado da luta a cada passo */
  voos: VooTR[];
  /** as marcas no piso (E3, chaoTR.ts): a cratera do pesado e o arrasto do empurrao, presas ao chao */
  marcas: MarcaTR[];
}
export const visualNovoTR = (): VisualTR => ({ numeros: [], impactos: [], ultimoGolpe: ["", ""], pausaMs: 0, extra: 0, voos: [], marcas: [] });
export const VIDA_NUMERO = 45;   /* passos (~0,7 s) */

export const COR_CURA = "#2f9e44", COR_TINTA = "#1d2433", COR_AZUL = "#2c73e0", COR_VERMELHO = "#d6336c", COR_FORTE = "#ffd23f";

/** os eventos de um passo viram numeros e impactos sobre quem levou */
export function aplicarEventosTR(v: VisualTR, sim: LutaTR, ev: readonly EventoTR[]): void {
  for (const e of ev) {
    if (e.tipo === "acao") v.ultimoGolpe[e.lado] = e.nome;
    else if (e.tipo === "dano") {
      const frac = e.valor / sim.S.L[e.lado].hpMax, forte = v.ultimoGolpe[1 - e.lado] === "pesado" || frac >= IMPACTO.fracaoPesado;
      v.impactos.push({ lado: e.lado, t0: e.t, frac, forte, golpe: v.ultimoGolpe[1 - e.lado] });
      v.pausaMs = Math.max(v.pausaMs, forte ? IMPACTO.pausaMs : Math.round(IMPACTO.pausaMs / 2));
      v.numeros.push({ txt: "-" + Math.round(e.valor * 10) / 10, cor: e.lado === 0 ? COR_VERMELHO : COR_AZUL, t0: e.t, lado: e.lado, forte });
    } else if (e.tipo === "cura") v.numeros.push({ txt: "+" + Math.round(e.valor), cor: COR_CURA, t0: e.t, lado: e.lado });
    else if (e.tipo === "erro") v.numeros.push({ txt: "errou", cor: COR_TINTA, t0: e.t, lado: e.lado });
    else if (e.tipo === "interrompe") v.numeros.push({ txt: "interrompido!", cor: COR_TINTA, t0: e.t, lado: e.lado });
    /* o empurrao do motor (a v18) sai no mesmo passo do dano: o acerto desse lado passa a ser do motor */
    else if (e.tipo === "empurrao" && e.px > 0) for (const i of v.impactos) if (i.lado === e.lado && i.t0 === e.t) i.motor = true;
  }
  v.numeros = v.numeros.filter(n => sim.S.passo - n.t0 < VIDA_NUMERO);
  /* os impactos ficam ate o fim do estouro por elemento da E2 (VOO.durImpacto), que e mais longo que a faisca */
  v.impactos = v.impactos.filter(i => sim.S.passo - i.t0 < Math.max(IMPACTO.durMax, VOO.durImpacto));
  seguirProjeteisTR(v, sim);
  seguirChaoTR(v, sim, ev);
}

/** a pausa pedida desde a ultima chamada (ms), zerando o pedido; 0 com o movimento reduzido */
export function consumirPausa(v: VisualTR, reduzido: boolean): number { const p = reduzido ? 0 : v.pausaMs; v.pausaMs = 0; return p; }

const vivos = (v: VisualTR, passo: number): ImpactoTR[] => v.impactos.filter(i => passo >= i.t0 && passo - i.t0 < IMPACTO.durMax);

/** a tremida do palco neste passo: soma dos impactos vivos, em px inteiros de CSS, limitada a IMPACTO.tremidaMaxPx em cada eixo */
export function tremidaDoPasso(v: VisualTR, passo: number): { x: number; y: number } {
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
/** o alvo esta branco neste passo? */
export const clarao = (v: VisualTR, passo: number, lado: number): boolean => vivos(v, passo).some(i => i.lado === lado && passo - i.t0 < IMPACTO.clarao);
/** o empurrao do alvo neste passo, em px de CSS na direcao de fugir do rival (o sinal e do desenho): sobe e volta a zero */
export function empurraoDoPasso(v: VisualTR, passo: number, lado: number): number {
  let m = 0;
  for (const i of vivos(v, passo)) {
    const idade = passo - i.t0; if (i.lado !== lado || i.motor || idade >= IMPACTO.durEmpurrao) continue;
    const meio = IMPACTO.durEmpurrao / 2, f = idade < meio ? (idade + 1) / meio : (IMPACTO.durEmpurrao - idade) / meio;
    m = Math.max(m, Math.round(IMPACTO.empurraoPx[i.forte ? 1 : 0] * Math.min(1, f)));
  }
  return m;
}

/** O movimento da luta de verdade (LUTA_EMPURRAO, etapa 5; so vista, a partir do estado do motor). PROPOSTO, SEM FONTE: ajustar nas
    capturas. pulo: quanto o caido sobe (px de CSS) enquanto e jogado para tras; rastro: as copias da investida, a cada quantos passos de
    arrancada e com que opacidade; poeira: o ciclo das nuvens nos pes (passos) e o tamanho delas (pixels de poeira) */
export const MOVIMENTO = { pulo: 10, rastroPassos: 3, rastroAlfa: [.4, .25, .12], poeiraCiclo: 8, poeiraTam: 3 } as const;

/** a altura (px de CSS, para cima) de quem cai enquanto o motor ainda o desliza para tras: um arco que sobe e volta ao chao no fim do deslize;
    0 fora da queda */
export function puloDaQueda(passo: number, quedaDe: number, deslizeAte: number): number {
  if (quedaDe < 0 || passo < quedaDe || passo >= deslizeAte) return 0;
  const dur = deslizeAte - quedaDe, f = (passo - quedaDe) / dur;
  return Math.round(MOVIMENTO.pulo * 4 * f * (1 - f));
}

/** as nuvens de poeira nos pes neste passo (na arrancada e no deslize): deslocamentos em pixels de poeira para tras (dx >= 0, o desenho poe o
    sinal) e para cima, e o tamanho. idade: os passos desde que o movimento comecou. Sem acaso: a mesma idade da a mesma poeira */
export function poeiraDoPasso(idade: number): { dx: number; dy: number; tam: number }[] {
  if (idade < 0) return [];
  const out: { dx: number; dy: number; tam: number }[] = [];
  for (let k = 0; k < 3; k++) {
    const fase = (idade + k * 3) % MOVIMENTO.poeiraCiclo, f = fase / MOVIMENTO.poeiraCiclo;
    out.push({ dx: Math.round(2 + f * 6 + k * 2), dy: Math.round(f * 3 + (k % 2)), tam: Math.max(1, MOVIMENTO.poeiraTam - Math.floor(f * 3)) });
  }
  return out;
}

/** os pixels da faisca de um impacto: deslocamentos (em unidades de pixel de faisca) e a cor, no passo dado. Os raios sao fixos (sem acaso) */
const RAIOS: readonly (readonly [number, number])[] = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1], [2, 1], [-2, 1], [2, -1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]];
export function faiscaDoPasso(i: ImpactoTR, passo: number): { dx: number; dy: number; cor: string }[] {
  const idade = passo - i.t0; if (idade < 0 || idade >= IMPACTO.durFaisca) return [];
  const raios = i.forte ? RAIOS : RAIOS.slice(0, 8), r = 1 + idade * (i.forte ? 1.1 : .8);
  const cor = idade < 3 ? "#ffffff" : idade < 6 ? COR_FORTE : "#ff8a2b";
  const out = raios.map(([a, b]) => ({ dx: Math.round(a * r), dy: Math.round(b * r), cor }));
  if (idade < 2) out.push({ dx: 0, dy: 0, cor: "#ffffff" });
  return out;
}

/** a fonte de pixel dos numeros: 3 x 5, so o que o dano usa */
const GLIFOS: Record<string, readonly string[]> = {
  "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"],
  "3": ["111", "001", "111", "001", "111"], "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
  "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"], "8": ["111", "101", "111", "101", "111"],
  "9": ["111", "101", "111", "001", "111"], "-": ["000", "000", "111", "000", "000"], ".": ["000", "000", "000", "000", "010"],
};
/** os pixels de um texto (so os glifos acima), em unidades de pixel: x, y; largura e altura. Caractere sem glifo falha alto */
export function pixelsDoTexto(txt: string): { px: [number, number][]; w: number; h: number } {
  const px: [number, number][] = []; let x = 0;
  for (const ch of txt) {
    const g = GLIFOS[ch]; if (!g) throw new Error(`sem glifo de pixel para "${ch}"`);
    g.forEach((lin, y) => { for (let k = 0; k < 3; k++) if (lin[k] === "1") px.push([x + k, y]); });
    x += 4;
  }
  return { px, w: Math.max(0, x - 1), h: 5 };
}
export const textoDeDano = (n: NumeroTR): boolean => /^-[0-9.]+$/.test(n.txt);
