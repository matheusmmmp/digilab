/* As posturas como efeito na luta em tempo real (LUTA_EFEITOS, etapa E4; docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 3.5). So apresentacao e
   puro (sem DOM): tudo sai do estado da luta (a acao, o preparo e a pele de cada lado), dos eventos `dano` e do `passo`, nunca do relogio do
   navegador; a mesma luta desenha as mesmas posturas. Nada aqui toca o motor, o log, o replay nem o ResultadoLutaTR, e nada empurra
   (D-EMP-9/11: o empurrao e so do motor). O desenho em canvas fica em desenhoTR.ts.
   - O escudo no `defender`: um arco de pixels na frente do corpo (do lado do rival), que acende quando um golpe bate nele.
   - A imagem fantasma na `esquiva`: copias apagadas do sprite, para tras, que se abrem no comeco da esquiva.
   - A aura no `carregar`: faiscas na cor do elemento que sobem dos dois lados do corpo. A elipse tracejada no chao continua a da E3
     (chaoTR.ts, telegrafiaDoPasso): a aura nao desenha nada no chao, para nao repetir o anel.
   - O clarao no `contra_golpe`: em guarda, um brilho pequeno na frente; no golpe que ele devolve, uma cruz de luz na frente do corpo.
   - O brilho na `pele_dura`: enquanto a pele dura vale (S.passo < peleAte, que passa do fim da acao), o sprite fica com a cor do metal e
     uma faixa de luz que corre por ele.
   - A etiqueta de texto de antes vira um icone pequeno em grade de pixel (7 x 7) sobre a cabeca; o nome vai no title e no leitor de tela
     (PalcoTR.tsx).
   Portado do palcoTR/ (o palco 1D do combate por turnos) na LUTA_POC, LP4: ficaram so os geradores de pixel que o palco 2D usa
   (desenhoPoc.ts, visualPoc.ts); o que lia o estado da luta 1D saiu com ela. */
import { ELEMENTO, type ElementoTR } from "./elementos.ts";
import { VOO, type PixelTR } from "./projeteis.ts";
/** As posturas da E4. PROPOSTO, SEM FONTE: ajustar nas capturas.
    - escudoAlto: a altura do arco do escudo (fracao da altura do sprite); escudoFrente: onde ele fica (fracao da meia-largura, na frente);
      acende: os passos em que o escudo (e o contra-golpe) ficam acesos depois de um golpe.
    - fantasmas: as copias da esquiva (opacidade de cada); fantasmaPx: o passo entre elas em pixels do sprite; abre: os passos em que elas
      se abrem do corpo ate o passo cheio; fantasmaTinta: quanto da cor do elemento cobre a copia.
    - aura: as faiscas de cada lado do corpo; auraCiclo: os passos em que uma faisca sobe do pe ao topo; auraMeia: a distancia do centro
      (fracao da largura do sprite).
    - claraoContra: os passos da cruz de luz do contra-golpe; brilhoGuarda: o ciclo (passos) do brilho pequeno em guarda.
    - peleAlfa: a opacidade da cor do metal sobre o sprite; peleFaixa: a largura da faixa de luz (pixels do sprite); peleCiclo: os passos
      em que a faixa atravessa o sprite.
    - icone: o lado da grade do icone (pixels de icone); iconePx: quantos pixels do sprite tem cada pixel do icone; iconeAcima: o vao entre
      o icone e o topo do sprite (px de CSS); pixelMinCss: o pixel do icone e dos efeitos tem pelo menos isto em px de CSS (arredondado
      para cima em pixels do sprite: a grade continua a do sprite). */
export const POSTURA = {
  escudoAlto: .62, escudoFrente: .62, acende: 8,
  fantasmas: [.55, .3], fantasmaPx: 9, abre: 6, fantasmaTinta: .55,
  aura: 4, auraCiclo: 20, auraMeia: .3,
  claraoContra: 9, brilhoGuarda: 8,
  peleAlfa: .45, peleFaixa: 5, peleCiclo: 36,
  icone: 7, iconePx: 1, iconeAcima: 8, pixelMinCss: 2,
} as const;


/** as faiscas da aura do carregar, relativas aos pes no centro, para uma meia-largura `meia` e uma altura `alto` (pixels do sprite): de cada
    lado, POSTURA.aura faiscas que sobem do pe ao topo e se apagam, na cor do elemento, com luz. Sem acaso: o mesmo passo da a mesma aura.
    Com o movimento reduzido, as faiscas param (o mesmo desenho em todo passo) */
export function pixelsDaAura(el: ElementoTR, meia: number, alto: number, passo: number, reduzido: boolean): PixelTR[] {
  const c = ELEMENTO[el], out: PixelTR[] = [], p = reduzido ? 0 : passo;
  for (const s of [1, -1]) for (let k = 0; k < POSTURA.aura; k++) {
    const fase = (p + k * Math.round(POSTURA.auraCiclo / POSTURA.aura) + (s > 0 ? 0 : Math.round(POSTURA.auraCiclo / (2 * POSTURA.aura)))) % POSTURA.auraCiclo;
    const f = fase / POSTURA.auraCiclo, dy = -7 - Math.round(f * alto), dx = s * (meia + (k % 2) - Math.round(f * 2));
    out.push({ dx: dx - 2, dy: dy - 2, cor: c.halo, alfa: .45 * (1 - f), tam: 5, luz: true });
    /* a faisca: 2 x 2 na cor do meio (a borda, saturada, no fim), com o risco de 2 pixels abaixo (o rastro da subida) */
    /* a faisca 2 x 2 com o contorno na cor saturada (a borda) e o miolo claro; o risco de 2 pixels abaixo e o rastro da subida */
    const alfa = 1 - f * .5;
    out.push({ dx: dx - 1, dy: dy - 1, cor: c.borda, alfa, tam: 4, luz: false });
    out.push({ dx, dy, cor: f < .55 ? c.nucleo : c.meio, alfa: 1, tam: 2, luz: false });
    out.push({ dx, dy: dy + 3, cor: c.borda, alfa: alfa * .8, tam: 2, luz: false });
    out.push({ dx, dy: dy + 5, cor: c.borda, alfa: alfa * .45, tam: 1, luz: false });
  }
  return out;
}

