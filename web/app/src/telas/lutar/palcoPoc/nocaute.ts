/* O nocaute e a barra de vida da luta em tempo real (LUTA_EFEITOS, etapa E5; docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 3.5). So vista e puro
   (sem DOM): tudo sai dos eventos `dano` e `cura` e do `passo` da luta (mais os passos de espera do fim, visual.extra), nunca do relogio do
   navegador. Nada aqui toca o motor, o log, o replay nem o ResultadoLutaTR.
   - A barra com o dano atrasado: a vida que acabou de sair fica na barra, branca por BARRA.branco passos, depois vermelha, e esvazia ate a
     vida de verdade a partir de BARRA.segura passos depois do ultimo golpe.
   - A camera lenta do nocaute e so do desenho: nos ultimos NOCAUTE.lentaAntes passos de uma luta que acaba em nocaute (o resultado ja esta
     decidido e guardado), a tela mostra menos passos por quadro; os passos e o fim sao os mesmos. Sem ela com o movimento reduzido.
   - Depois do nocaute: o fundo escurece (o cenario, nao os lutadores) e o "K.O." grande sobe no meio do palco, em fonte de pixel.
   Portado do palcoTR/ (o palco 1D do combate por turnos) na LUTA_POC, LP4: ficaram so os geradores de pixel que o palco 2D usa
   (desenhoPoc.ts, visualPoc.ts); o que lia o estado da luta 1D saiu com ela. */
/** A barra com o dano atrasado (E5). PROPOSTO, SEM FONTE: ajustar nas capturas.
    - branco: os passos em que o pedaco que saiu fica branco (16 ms cada: ~0,2 s);
    - segura: os passos parado antes de esvaziar (~0,5 s);
    - taxa: quanto do maximo da vida o pedaco esvazia por passo (0,006: um golpe de 12 % esvazia em 20 passos, ~0,3 s). */
export const BARRA = { branco: 12, segura: 30, taxa: .006 } as const;

/** O nocaute (E5). PROPOSTO, SEM FONTE: ajustar nas capturas.
    - lentaAntes: os ultimos passos da luta mostrados em camera lenta; lentaPassos: os passos por quadro nela (sem ela, 3; x2, 6);
    - lentaDepois: os quadros da espera do fim que tambem andam devagar (o Die e os ultimos efeitos);
    - escuro: a opacidade maxima do escuro sobre o cenario; escurecer: os passos ate chegar nela;
    - koAtraso: os passos entre o nocaute e o "K.O."; koPop: os passos em que ele encolhe ate o tamanho final (sai grande, em escala inteira);
    - koLargura: a largura do "K.O." em fracao da largura do palco; koAltura: o maximo da altura dele em fracao da altura do palco;
    - koAltura0: a altura do meio do "K.O." na tela (fracao da altura do palco). */
export const NOCAUTE = { lentaAntes: 36, lentaPassos: 1, lentaDepois: 10, escuro: .6, escurecer: 10, koAtraso: 6, koPop: 6, koLargura: .3, koAltura: .2, koAltura0: .3 } as const;

/** a linha da vida de um lado, so do que a luta mostrou: a vida antes do primeiro evento e a vida depois de cada dano ou cura */
export interface VidaTR { ini: number | null; hpMax: number; ev: { t: number; hp: number; dano: boolean }[] }
export const vidasNovasTR = (): VidaTR[] => [{ ini: null, hpMax: 1, ev: [] }, { ini: null, hpMax: 1, ev: [] }];

/** anota um dano (resta: a vida depois dele) ou uma cura (a vida depois dela, do estado) na linha da vida */
export function anotarVidaTR(vida: VidaTR, t: number, hpAntes: number, hpDepois: number, hpMax: number, dano: boolean): void {
  if (vida.ini === null) { vida.ini = hpAntes; vida.hpMax = hpMax; }
  vida.ev.push({ t, hp: hpDepois, dano });
}

/** a barra de um lado no passo: a vida (hp) e o fim do pedaco atrasado (rastro >= hp), as duas na mesma unidade da vida; branco: o pedaco
    ainda esta branco. Sem evento, sem pedaco */
export function barraDoPasso(vida: VidaTR, passo: number): { hp: number; rastro: number; branco: boolean } | null {
  if (vida.ini === null) return null;
  let hp = vida.ini, r = vida.ini, tDano = -Infinity, tAte = -Infinity;
  const drenar = (ate: number) => { const desde = Math.max(tAte, tDano + BARRA.segura); if (ate > desde) r = Math.max(hp, r - BARRA.taxa * vida.hpMax * (ate - desde)); tAte = Math.max(tAte, ate); };
  for (const e of vida.ev) {
    if (e.t > passo) break;
    drenar(e.t);
    hp = e.hp;
    if (e.dano) tDano = e.t; else r = Math.max(r, hp);
    r = Math.max(r, hp);
  }
  drenar(passo);
  return { hp, rastro: r, branco: r > hp && passo - tDano < BARRA.branco };
}

/** os passos da luta neste quadro da tela: os de sempre, ou NOCAUTE.lentaPassos nos ultimos NOCAUTE.lentaAntes de uma luta que acaba em
    nocaute (passos: os do resultado). Com o movimento reduzido, sempre os de sempre. Nunca passa do fim (quem chama para nele) */
export function passosDoQuadro(passo: number, base: number, fim: { passos: number; fim: "ko" | "limite" }, reduzido: boolean): number {
  if (reduzido || fim.fim !== "ko" || passo < fim.passos - NOCAUTE.lentaAntes) return base;
  return Math.min(base, NOCAUTE.lentaPassos);
}
/** os passos de efeito de um quadro da espera do fim (visual.extra): devagar nos primeiros NOCAUTE.lentaDepois quadros depois do nocaute */
export const passosDaEspera = (quadro: number, base: number, ko: boolean, reduzido: boolean): number =>
  !reduzido && ko && quadro < NOCAUTE.lentaDepois ? Math.min(base, NOCAUTE.lentaPassos) : base;

/** a opacidade do escuro sobre o cenario idade passos depois do nocaute (0 antes) */
export const escuroDoPasso = (idade: number): number => idade < 0 ? 0 : NOCAUTE.escuro * Math.min(1, (idade + 1) / NOCAUTE.escurecer);

/** a fonte do "K.O." (5 x 5; o ponto e um pixel no pe) */
const LETRAS: Record<string, readonly string[]> = {
  K: ["10001", "10010", "11100", "10010", "10001"], O: ["01110", "10001", "10001", "10001", "01110"], ".": ["0", "0", "0", "0", "1"],
};
/** os pixels do "K.O." (x, y em unidades de pixel) e o tamanho */
export function pixelsDoKO(): { px: [number, number][]; w: number; h: number } {
  const px: [number, number][] = []; let x = 0;
  for (const ch of "K.O.") { const g = LETRAS[ch]; g.forEach((lin, y) => { for (let k = 0; k < lin.length; k++) if (lin[k] === "1") px.push([x + k, y]); }); x += g[0].length + 1; }
  return { px, w: x - 1, h: 5 };
}
/** o "K.O." idade passos depois do nocaute, numa tela de Wp x Hp px do canvas: null antes de ele sair; senao o tamanho do pixel (inteiro, em
    px do canvas), o centro e se ja esta no tamanho final. Sai uma vez e meia maior e encolhe em NOCAUTE.koPop passos, em pixels inteiros, ate
    o final; com o movimento reduzido, ja no final */
export function koDoPasso(idade: number, Wp: number, Hp: number, reduzido: boolean): { p: number; cx: number; cy: number; pronto: boolean } | null {
  const i = idade - NOCAUTE.koAtraso; if (i < 0) return null;
  const { w, h } = pixelsDoKO(), fim = Math.max(2, Math.floor(Math.min(Wp * NOCAUTE.koLargura / w, Hp * NOCAUTE.koAltura / h)));
  const pronto = reduzido || i >= NOCAUTE.koPop, p = pronto ? fim : fim + Math.ceil(fim * (NOCAUTE.koPop - i) / (2 * NOCAUTE.koPop));
  return { p, cx: Math.round(Wp / 2), cy: Math.round(Hp * NOCAUTE.koAltura0), pronto };
}
