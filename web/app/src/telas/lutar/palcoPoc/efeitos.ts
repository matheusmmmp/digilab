/* Os efeitos de impacto da luta em tempo real (LUTA_EFEITOS, etapa E1; docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 3.5). So apresentacao:
   tudo sai dos eventos `dano` e `acao` e do `passo` da luta, nunca do relogio do navegador; a mesma luta desenha os mesmos efeitos. Nada
   aqui toca o motor, o log, o replay nem o ResultadoLutaTR. Este arquivo e puro (sem DOM): o desenho fica em desenhoTR.ts.
   Portado do palcoTR/ (o palco 1D do combate por turnos) na LUTA_POC, LP4: ficaram so os geradores de pixel que o palco 2D usa
   (desenhoPoc.ts, visualPoc.ts); o que lia o estado da luta 1D saiu com ela. */
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

export const COR_CURA = "#2f9e44", COR_TINTA = "#1d2433", COR_AZUL = "#2c73e0", COR_VERMELHO = "#d6336c", COR_FORTE = "#ffd23f";

/** O movimento da luta de verdade (LUTA_EMPURRAO, etapa 5; so vista, a partir do estado do motor). PROPOSTO, SEM FONTE: ajustar nas
    capturas. pulo: quanto o caido sobe (px de CSS) enquanto e jogado para tras; rastro: as copias da investida, a cada quantos passos de
    arrancada e com que opacidade; poeira: o ciclo das nuvens nos pes (passos) e o tamanho delas (pixels de poeira) */
export const MOVIMENTO = { pulo: 10, rastroPassos: 3, rastroAlfa: [.4, .25, .12], poeiraCiclo: 8, poeiraTam: 3 } as const;

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
