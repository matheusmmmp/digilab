/* Os projeteis e os golpes por elemento da luta em tempo real (LUTA_EFEITOS, etapa E2; docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 3.5).
   So apresentacao e puro (sem DOM): o voo de cada projetil e lido do estado da luta (S.projeteis) passo a passo, e o desenho de cada passo sai
   so do voo guardado e do `passo`, nunca do relogio do navegador. O desenho em canvas fica em desenhoTR.ts.

   O defeito que a E2 conserta (o disparo do Gabumon que nao aparecia, visto pelo Matheus no GIF do empurrao): o projetil era um circulo liso
   de 5 px, azul ou vermelho, na altura dos pes, saindo do centro do corpo do atirador (atras da frente do sprite). No motor ele vive pouco
   (a 4,8 px por passo, de 5 passos no contato a ~20 no medio), e a tela desenha 1 quadro a cada 3 passos (12 com o movimento reduzido):
   saia em 1 ou 2 quadros, ou nenhum, e azul sobre o ringue azul. Aqui o voo vai da boca do atirador a frente do alvo, na altura do peito, com
   o tamanho dos pixels do sprite, cor do elemento, halo e rastro, e fica na tela pelo menos VOO.minVisivel passos.
   Portado do palcoTR/ (o palco 1D do combate por turnos) na LUTA_POC, LP4: ficaram so os geradores de pixel que o palco 2D usa
   (desenhoPoc.ts, visualPoc.ts); o que lia o estado da luta 1D saiu com ela. */
import { ELEMENTO, type ElementoTR } from "./elementos.ts";
/** O voo e o brilho dos golpes (E2). PROPOSTO, SEM FONTE: ajustar nas capturas.
    - minVisivel: passos (desde o disparo) em que o projetil fica na tela mesmo que o motor ja o tenha acertado (o resto do voo e no ponto do
      acerto); 12 passos = 4 quadros normais ou 1 quadro do movimento reduzido.
    - rastro: quantos passos para tras o rastro alcanca (rastroReduzido com o movimento reduzido); o rastro fica rastroFica passos depois do acerto.
    - durImpacto: os passos do estouro na cor do elemento, por cima da faisca da E1.
    - rajada: os passos da rajada de um golpe corpo a corpo que acerta (da boca de quem bate ate a frente do alvo; ver GOLPES_RAJADA).
    - pixel: quantos pixels do sprite tem cada pixel de efeito (inteiro: a grade continua a do sprite); pixelMinCss: o pixel de efeito tem
      pelo menos isto em px de CSS (arredondado para cima em pixels do sprite).
    - boca: a fracao da meia-largura do sprite onde o projetil nasce e acerta (na frente do corpo); altura: a fracao da altura do sprite
      (do chao) na altura do peito. */
export const VOO = { minVisivel: 12, rastro: 8, rastroReduzido: 2, rastroFica: 8, durImpacto: 14, rajada: 4, pixel: 2, pixelMinCss: 6, boca: .45, altura: .55, halo: .38 } as const;

/** um pixel de efeito: deslocamento em pixels do sprite (a escala e) a partir do ponto, a cor, a opacidade e o tamanho (em pixels do sprite);
    luz: somado ao fundo (globalCompositeOperation "lighter") */
export interface PixelTR { dx: number; dy: number; cor: string; alfa: number; tam: number; luz: boolean }

/** as silhuetas viradas para a direita (o desenho espelha o dx de quem atira da direita): [dx, dy, camada] com 0 nucleo, 1 meio, 2 borda */
const SILHUETA: Record<"bola" | "lasca" | "raio" | "gota", readonly (readonly [number, number, number])[]> = {
  bola: [[0, 0, 0], [1, 0, 0], [0, -1, 0], [0, 1, 1], [-1, 0, 1], [1, -1, 1], [1, 1, 1], [-1, -1, 1], [-1, 1, 1], [2, 0, 1],
    [0, -2, 2], [0, 2, 2], [-2, 0, 2], [2, -1, 2], [2, 1, 2], [-2, -1, 2], [-2, 1, 2], [-1, -2, 2], [1, -2, 2], [-1, 2, 2], [1, 2, 2], [3, 0, 2]],
  lasca: [[0, 0, 0], [1, 0, 0], [2, 0, 0], [-1, 0, 1], [3, 0, 1], [0, -1, 1], [1, -1, 1], [0, 1, 1], [1, 1, 1], [-2, 0, 2], [-3, 0, 2], [4, 0, 2],
    [2, -1, 2], [2, 1, 2], [-1, -1, 2], [-1, 1, 2], [1, -2, 2], [1, 2, 2]],
  raio: [[0, 0, 0], [1, -1, 0], [-1, 1, 0], [2, -1, 1], [1, 0, 1], [-1, 0, 1], [-2, 1, 1], [0, -1, 1], [0, 1, 1], [3, -2, 2], [2, -2, 2],
    [-2, 2, 2], [-3, 2, 2], [2, 0, 2], [-2, 0, 2]],
  gota: [[0, 0, 0], [1, 0, 0], [0, -1, 0], [0, 1, 1], [1, -1, 1], [1, 1, 1], [2, 0, 1], [-1, 0, 1], [2, -1, 2], [2, 1, 2], [1, -2, 2], [1, 2, 2],
    [0, -2, 2], [0, 2, 2], [3, 0, 2], [-2, 0, 2], [-3, 0, 2]],
};

/** os pixels da cabeca do projetil no passo (halo de luz, silhueta solida por cima). Com o movimento reduzido, o halo nao pulsa e a chama
    nao tremula */
export function pixelsDaCabeca(el: ElementoTR, passo: number, reduzido: boolean): PixelTR[] {
  const c = ELEMENTO[el], out: PixelTR[] = [], pulsa = reduzido ? 0 : passo % 2;
  /* o halo: um disco de luz em volta, raio 4 (5 no pulso) */
  const r = 4 + pulsa;
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r + 1) out.push({ dx, dy, cor: c.halo, alfa: VOO.halo, tam: 1, luz: true });
  const cores = [c.nucleo, c.meio, c.borda];
  for (const [dx, dy, k] of SILHUETA[c.forma]) out.push({ dx, dy, cor: cores[k], alfa: 1, tam: 1, luz: false });
  /* o detalhe que mexe: a lingua de fogo atras da bola, a ponta do raio que salta (so sem o movimento reduzido) */
  if (!reduzido && c.forma === "bola") out.push({ dx: -3, dy: pulsa ? -1 : 1, cor: c.borda, alfa: 1, tam: 1, luz: false });
  if (!reduzido && c.forma === "raio") out.push({ dx: 4, dy: pulsa ? -3 : -1, cor: c.meio, alfa: 1, tam: 1, luz: true });
  return out;
}

/** as particulas do rastro de uma posicao j passos atras (j >= 1), relativas a essa posicao, num voo de k passos de rastro: cada elemento
    deixa o seu (brasas que sobem, lascas que brilham, raio em zigue-zague, gotas que caem). Sem acaso: o mesmo j e passo dao o mesmo rastro */
export function pixelsDoRastro(el: ElementoTR, j: number, k: number, passo: number, reduzido: boolean): PixelTR[] {
  const c = ELEMENTO[el], f = j / (k + 1), cor = c.rastro[Math.min(c.rastro.length - 1, Math.floor(f * c.rastro.length))];
  const alfa = Math.max(.15, 1 - f), tam = j <= k / 3 ? 2 : 1, base: PixelTR = { dx: 0, dy: 0, cor, alfa, tam, luz: true };
  if (reduzido) return [base];
  const lado = (passo + j) % 2 ? 1 : -1;
  switch (c.forma) {
    case "bola": return [{ ...base, dy: -Math.floor(j / 2) }, { ...base, dy: -Math.floor(j / 3) + 2, tam: 1, alfa: alfa * .7 }];
    case "lasca": return [base, ...(j % 2 ? [{ ...base, dy: 2 * lado, tam: 1, cor: c.nucleo }] : [])];
    case "raio": return [{ ...base, dy: 2 * lado }, { ...base, dx: 1, dy: lado, tam: 1 }];
    case "gota": return [{ ...base, dy: Math.floor(j / 3) }, ...(j % 3 === 0 ? [{ ...base, dy: Math.floor(j / 2) + 2, tam: 1, cor: c.rastro[2] }] : [])];
  }
}

/** o estouro na cor do elemento de quem bateu (por cima da faisca da E1), idade passos depois do acerto: um anel que abre e o detalhe do
    elemento. Com o movimento reduzido, sem o brilho que pisca (o anel fica, sem o clarao do comeco) */
const ANEL: readonly (readonly [number, number])[] = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1], [2, 1], [-2, 1], [2, -1], [-2, -1]];
export function pixelsDoEstouro(el: ElementoTR, idade: number, forte: boolean, reduzido: boolean): PixelTR[] {
  if (idade < 0 || idade >= VOO.durImpacto) return [];
  const c = ELEMENTO[el], out: PixelTR[] = [], f = idade / VOO.durImpacto, r = 2 + idade * (forte ? .9 : .65), alfa = 1 - f;
  if (!reduzido && idade < 3) for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) if (dx * dx + dy * dy <= 9) out.push({ dx, dy, cor: c.halo, alfa: .55, tam: 1, luz: true });
  /* o anel na cor saturada (a borda), opaco ate o fim e encolhendo: o alvo esta branco do clarao nos primeiros passos, e o Zudomon e cinza;
     uma cor clara ou meio transparente some por cima deles. O brilho (luz) fica atras, na cor do meio */
  const tam = f < .6 ? 2 : 1;
  for (const [a, b] of forte ? ANEL : ANEL.slice(0, 8)) {
    let dx = Math.round(a * r), dy = Math.round(b * r);
    if (c.forma === "bola") dy -= Math.floor(idade / 3);                 /* as brasas sobem */
    else if (c.forma === "gota") dy += Math.floor(idade * idade / 40);   /* os respingos caem */
    /* solidos: o alvo fica branco do clarao, e luz somada ao branco nao aparece */
    out.push({ dx: dx - 1, dy: dy - 1, cor: c.meio, alfa: alfa * .6, tam: tam + 2, luz: true });
    out.push({ dx, dy, cor: c.borda, alfa: 1, tam, luz: false });
  }
  if (c.forma === "raio" && idade < 8) for (let k = 0; k < 4; k++) out.push({ dx: k % 2 ? k : -k, dy: -2 - 2 * k, cor: c.borda, alfa, tam: 1, luz: false });
  if (c.forma === "lasca") for (const [a, b] of [[0, -1], [0, 1], [1, 0], [-1, 0]]) out.push({ dx: Math.round(a * (r + 2)), dy: Math.round(b * (r + 2)), cor: c.borda, alfa, tam: 1, luz: false });
  return out;
}
