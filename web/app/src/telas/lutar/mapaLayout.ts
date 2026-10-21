/* A disposicao do mapa da Exploracao (docs/TAREFA_V2_EXPLORACAO.md): onde fica cada ilha, o cartao dela e o marcador, em px de CSS da
   caixa do mapa. Pura, sem DOM: a tela poe os cartoes e o marcador por cima, e a vista 3D (mapa3d.ts) poe cada ilha com o centro do tampo
   no mesmo ponto. A ordem e a do motor (m.lugares, e a Fronteira no fim): a primeira ilha embaixo, a ultima no alto.
   - celular: duas colunas em zigue-zague, o cartao do lado oposto da ilha, como na referencia; a altura sai da largura (a pagina rola);
   - desktop: em fileiras (2 a 4 colunas, a que der a maior ilha), indo e voltando, com o cartao embaixo da ilha; cabe na caixa.
   As fracoes da ilha (o que o desenho ocupa acima e abaixo do centro do tampo) vem da forma das ilhas de mapa3d.ts; PROPOSTAS, sem fonte. */

/** o desenho da ilha acima do centro do tampo (as decoracoes mais altas) e abaixo dele (a rocha), em fracoes da largura da ilha */
export const ACIMA = 0.62, ABAIXO = 0.70;
/** a altura reservada para um cartao (o nome e ate duas linhas de situacao) e para o marcador (o rotulo, o retrato e a seta) */
export const ALT_CARTAO = 64, ALT_MARCADOR = 76;
/** a ponta do marcador fica um pouco atras do centro do tampo */
export const PE_MARCADOR = 0.12;
/** no desktop o cartao comeca embaixo do centro do tampo, sobre a rocha que afina */
const CARTAO_DESK = 0.45;

export interface PontoIlha { cx: number; cy: number }
export interface CartaoMapa { x: number; y: number; w: number; lado: "esq" | "dir" | "baixo" }
export interface LayoutMapa { larg: number; alt: number; tam: number; ilhas: PontoIlha[]; cartoes: CartaoMapa[] }
/** a caixa de cada coisa do mapa, para os testes de sobreposicao */
export interface Caixa { x0: number; y0: number; x1: number; y1: number }

export function caixaIlha(L: LayoutMapa, i: number): Caixa {
  const { cx, cy } = L.ilhas[i], t = L.tam;
  return { x0: cx - t / 2, y0: cy - ACIMA * t, x1: cx + t / 2, y1: cy + ABAIXO * t };
}
export function caixaCartao(L: LayoutMapa, i: number): Caixa {
  const c = L.cartoes[i];
  const y0 = c.lado === "baixo" ? c.y : c.y - ALT_CARTAO / 2;
  return { x0: c.x, y0, x1: c.x + c.w, y1: y0 + ALT_CARTAO };
}
/** o marcador sobre a ilha i: o rotulo de 120 px e o retrato embaixo dele, com a ponta no tampo */
export function caixaMarcador(L: LayoutMapa, i: number): Caixa {
  const { cx, cy } = L.ilhas[i], pe = cy - PE_MARCADOR * L.tam;
  return { x0: cx - 60, y0: pe - ALT_MARCADOR, x1: cx + 60, y1: pe };
}

/** celular: a largura da caixa da a ilha (37%) e o passo vertical (o mesmo); o cartao fica do outro lado, centrado na altura da ilha */
export function layoutCelular(n: number, larg: number): LayoutMapa {
  if (!Number.isInteger(n) || n < 1) throw new Error("mapa sem ilha: " + n);
  if (!(larg >= 280)) throw new Error("mapa estreito demais: " + larg);
  const W = larg, tam = Math.round(0.37 * W), passo = 0.37 * W;
  const topo = Math.max(ACIMA * tam, PE_MARCADOR * tam + ALT_MARCADOR) + 12, pe = ABAIXO * tam + 12;
  const alt = Math.round(topo + (n - 1) * passo + pe);
  const ilhas: PontoIlha[] = [], cartoes: CartaoMapa[] = [];
  for (let i = 0; i < n; i++) {
    const dir = i % 2 === 1, cx = Math.round((dir ? 0.73 : 0.27) * W), cy = Math.round(alt - pe - i * passo);
    ilhas.push({ cx, cy });
    /* o cartao encosta na ponta do tampo (a referencia sobrepoe um pouco a ilha) e vai ate 10 px da borda */
    const w = Math.round(0.53 * W - 12);
    cartoes.push({ x: dir ? 10 : Math.round(0.47 * W + 2), y: cy, w, lado: dir ? "esq" : "dir" });
  }
  return { larg: W, alt, tam, ilhas, cartoes };
}

/** a ilha do desktop quando nenhuma cabe na altura da caixa: o mapa fica mais alto que ela, e a caixa rola. Abaixo das ilhas que cabem
    numa janela normal (cerca de 100 px em 1280 x 800), para a janela baixa nao ter ilhas maiores. PROPOSTO */
const TAM_ROLANDO = 90;
/** desktop: fileiras que vao e voltam (a primeira embaixo, da esquerda para a direita), com o cartao embaixo de cada ilha. Prova 2, 3 e 4
    colunas e fica com a que der a maior ilha que cabe na caixa (de 80 a 220 px); o bloco fica no meio da caixa. Se nenhuma couber na
    altura (uma janela baixa), a ilha fica com TAM_ROLANDO, nas colunas que pedirem menos altura, e o mapa passa da altura da caixa */
export function layoutDesktop(n: number, larg: number, alt: number): LayoutMapa {
  if (!Number.isInteger(n) || n < 1) throw new Error("mapa sem ilha: " + n);
  type Opcao = { c: number; tam: number; cartao: number; passo: number; total: number; topo: number; pe: number };
  /* a disposicao com c colunas e a ilha tam, ou null se ela nao cabe na largura */
  const opcao = (c: number, tam: number): Opcao | null => {
    const r = Math.ceil(n / c), col = larg / c;
    /* o cartao tem a largura da coluna (ate 220 px): o nome e a situacao numa linha cada, quase sempre */
    const cartao = Math.min(220, Math.floor(col - 8));
    if (cartao < 150 || tam / 2 + cartao / 2 + 8 > col) return null;
    const passo = Math.max((CARTAO_DESK + ACIMA) * tam + ALT_CARTAO + 6, (CARTAO_DESK + PE_MARCADOR) * tam + ALT_CARTAO + ALT_MARCADOR + 4);
    const topo = Math.max(ACIMA * tam, PE_MARCADOR * tam + ALT_MARCADOR) + 10, pe = CARTAO_DESK * tam + ALT_CARTAO + 10;
    return { c, tam, cartao, passo, total: topo + (r - 1) * passo + pe, topo, pe };
  };
  const colunas = [2, 3, 4].filter(c => c <= Math.max(2, n));
  let melhor: Opcao | null = null;
  for (const c of colunas) for (let tam = 220; tam >= 80; tam -= 2) {
    const o = opcao(c, tam);
    if (!o || o.total > alt) continue;
    if (!melhor || o.tam > melhor.tam) melhor = o;
    break;
  }
  if (!melhor) for (const c of colunas) {
    const o = opcao(c, TAM_ROLANDO);
    if (o && (!melhor || o.total < melhor.total)) melhor = o;
  }
  if (!melhor) throw new Error(`o mapa de ${n} ilhas não cabe em ${larg} px de largura`);
  const { c, tam, cartao, passo, total, pe } = melhor, col = larg / c, altura = Math.max(alt, Math.ceil(total)), sobra = (altura - total) / 2;
  const ilhas: PontoIlha[] = [], cartoes: CartaoMapa[] = [];
  for (let i = 0; i < n; i++) {
    const fila = Math.floor(i / c), k = i % c, coluna = fila % 2 === 0 ? k : c - 1 - k;
    const cx = Math.round(col * (coluna + 0.5)), cy = Math.round(altura - sobra - pe - fila * passo);
    ilhas.push({ cx, cy });
    cartoes.push({ x: Math.round(cx - cartao / 2), y: Math.round(cy + CARTAO_DESK * tam), w: cartao, lado: "baixo" });
  }
  return { larg, alt: altura, tam, ilhas, cartoes };
}
