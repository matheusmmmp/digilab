/* A telegrafia e o chao da luta em tempo real (LUTA_EFEITOS, etapa E3; docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 3.5). So apresentacao e
   puro (sem DOM): tudo sai do estado da luta (a acao, o preparo e o empurrao de cada lado), dos eventos `dano` e `empurrao` e do `passo`, nunca
   do relogio do navegador; a mesma luta desenha o mesmo chao. Nada aqui toca o motor, o log, o replay nem o ResultadoLutaTR. O desenho em
   canvas fica em desenhoTR.ts.
   - A elipse no chao: no `preparar_pesado` e no `carregar`, sob o lutador, abre larga e se fecha ate o fim da acao. O pesado preparado fica
     com a elipse fechada, piscando, ate o golpe (ou a finta) sair.
   - A onda de choque: no acerto do pesado, aneis no chao que abrem a partir dos pes do alvo.
   - A marca no piso: a cratera no ponto do acerto do pesado e o arrasto dos pes no deslize do empurrao (a v18). Ficam presas ao chao (no x
     da luta, nao no lutador) e somem em ~2 s.
   - A poeira nos pes: na corrida, na arrancada, no deslize do empurrao, no pouso da queda e no acerto do pesado.
   Portado do palcoTR/ (o palco 1D do combate por turnos) na LUTA_POC, LP4: ficaram so os geradores de pixel que o palco 2D usa
   (desenhoPoc.ts, visualPoc.ts); o que lia o estado da luta 1D saiu com ela. */
import { ELEMENTO, type ElementoTR } from "./elementos.ts";
import { VOO, type PixelTR } from "./projeteis.ts";
/** O chao da E3. PROPOSTO, SEM FONTE: ajustar nas capturas.
    - pixel: quantos pixels do sprite tem cada pixel de chao (inteiro: a grade e a do sprite).
    - elipseAberta, elipseFechada: o raio da elipse (fracao da meia-largura do sprite) no comeco e no fim do preparo; achatado: a altura
      sobre a largura (a perspectiva do chao); piscaPronta: o ciclo (passos) do pisca do pesado pronto.
    - durOnda, ondaDe, ondaAte: os passos da onda de choque e o raio dela (fracao da meia-largura do alvo) do comeco ao fim; ondaAtraso: o
      segundo anel sai tantos passos depois.
    - durMarca: os passos em que a marca fica (125 = 2 s); someMarca: os ultimos passos, em que ela se apaga; brilhoCratera: os passos da
      borda da cratera na cor do elemento.
    - cratera: o raio da cratera (fracao da meia-largura do alvo).
    - durPouso: os passos da nuvem de poeira no pouso da queda e no acerto do pesado. */
export const CHAO = {
  pixel: 2, elipseAberta: 1.7, elipseFechada: .9, achatado: .28, piscaPronta: 6,
  durOnda: 18, ondaDe: .6, ondaAte: 3.2, ondaAtraso: 5,
  durMarca: 125, someMarca: 40, brilhoCratera: 20, cratera: .85,
  durPouso: 14,
} as const;

/** a telegrafia de um lado neste passo: o tipo, quanto ja fechou (0 aberta, 1 fechada) e se o pesado esta pronto (fechada, a espera do golpe) */
export interface TelegrafiaTR { tipo: "pesado" | "carregar"; f: number; pronto: boolean }
/** os pixels (inteiros) de um anel de elipse de raios rx e ry, em pixels de chao, sem repetir: a ordem e a do angulo (sem acaso) */
export function anelDaElipse(rx: number, ry: number): [number, number][] {
  const out: [number, number][] = [], vistos = new Set<string>(), n = Math.max(16, Math.ceil(2 * Math.PI * Math.max(rx, ry) * 1.5));
  for (let k = 0; k < n; k++) {
    const ang = 2 * Math.PI * k / n, p: [number, number] = [Math.round(rx * Math.cos(ang)), Math.round(ry * Math.sin(ang))], ch = p.join(",");
    if (!vistos.has(ch)) { vistos.add(ch); out.push(p); }
  }
  return out;
}
const ry = (rx: number): number => Math.max(1, Math.round(rx * CHAO.achatado));

/** os pixels da elipse da telegrafia, em volta dos pes, para uma meia-largura de `meia` pixels de chao. O pesado: o anel fechando na cor do
    elemento, o alvo (o anel fechado) apagado por baixo, e o pronto piscando em branco. O carregar: tracejado, na cor do meio. Com o movimento
    reduzido, o pronto nao pisca */
export function pixelsDaTelegrafia(tg: TelegrafiaTR, el: ElementoTR, meia: number, passo: number, reduzido: boolean): PixelTR[] {
  const c = ELEMENTO[el], out: PixelTR[] = [];
  const rFech = Math.max(3, Math.round(meia * CHAO.elipseFechada)), rAb = Math.max(rFech + 2, Math.round(meia * CHAO.elipseAberta));
  const rx = Math.round(rAb + (rFech - rAb) * tg.f);
  if (tg.tipo === "pesado") {
    /* o alvo: onde o anel vai fechar */
    if (!tg.pronto) for (const [dx, dy] of anelDaElipse(rFech, ry(rFech))) out.push({ dx, dy, cor: c.borda, alfa: .5, tam: 1, luz: false });
    const branco = tg.pronto && !reduzido && Math.floor(passo / (CHAO.piscaPronta / 2)) % 2 === 0;
    /* o anel solido na cor do meio (a clara), com a borda (a saturada) por fora, e o brilho somado por baixo */
    for (const [dx, dy] of anelDaElipse(rx, ry(rx))) out.push({ dx: dx - 1, dy: dy - 1, cor: c.halo, alfa: .4, tam: 3, luz: true });
    for (const [dx, dy] of anelDaElipse(rx + 1, ry(rx + 1))) out.push({ dx, dy, cor: c.borda, alfa: 1, tam: 1, luz: false });
    for (const [dx, dy] of anelDaElipse(rx, ry(rx))) out.push({ dx, dy, cor: branco ? "#ffffff" : c.meio, alfa: 1, tam: 1, luz: false });
  } else {
    anelDaElipse(rx, ry(rx)).forEach(([dx, dy], k) => {
      if (k % 4 >= 2) return;   /* tracejado: 2 de 4 */
      out.push({ dx: dx - 1, dy: dy - 1, cor: c.halo, alfa: .4, tam: 3, luz: true });
      out.push({ dx, dy, cor: c.meio, alfa: 1, tam: 1, luz: false });
    });
  }
  return out;
}

/** uma marca no piso, presa ao chao: x0 e x1 no x da luta (a cratera tem x1 = x0); de 'ate' em diante ela para de mudar e conta o sumico */
export interface MarcaTR { tipo: "cratera" | "arrasto"; lado: number; t0: number; x0: number; x1: number; ate: number }

/** a opacidade da marca no passo (1 ate comecar a sumir; 0 depois de durMarca passos do fim) */
export function alfaDaMarca(m: MarcaTR, passo: number): number {
  const idade = passo - m.ate;
  if (passo < m.t0 || idade >= CHAO.durMarca) return 0;
  return Math.min(1, (CHAO.durMarca - idade) / CHAO.someMarca);
}

/** os pixels da cratera de uma meia-largura de `meia` pixels de chao (relativos ao ponto do acerto, nos pes): o fundo escuro achatado, as
    rachaduras para os lados e, nos primeiros passos, a borda na cor do elemento de quem bateu. Sem acaso */
const RACHAS: readonly (readonly [number, number])[] = [[1, 0], [2, 0], [3, -1], [4, -1], [5, -1], [2, 1], [3, 1], [4, 2]];
export function pixelsDaCratera(m: MarcaTR, el: ElementoTR, meia: number, passo: number): PixelTR[] {
  const a = alfaDaMarca(m, passo); if (a <= 0) return [];
  const c = ELEMENTO[el], out: PixelTR[] = [], rx = Math.max(3, Math.round(meia * CHAO.cratera)), r2 = ry(rx);
  for (let dy = -r2; dy <= r2; dy++) for (let dx = -rx; dx <= rx; dx++) {
    const d = (dx * dx) / (rx * rx) + (dy * dy) / (r2 * r2); if (d > 1) continue;
    out.push({ dx, dy, cor: d < .45 ? "#1a1410" : "#3a2c20", alfa: .55 * a, tam: 1, luz: false });
  }
  for (const s of [1, -1]) for (const [px, py] of RACHAS) out.push({ dx: s * (rx + px), dy: py, cor: "#2a2018", alfa: .6 * a, tam: 1, luz: false });
  const idade = passo - m.t0;
  if (idade < CHAO.brilhoCratera) {
    const b = 1 - idade / CHAO.brilhoCratera;
    for (const [dx, dy] of anelDaElipse(rx, r2)) out.push({ dx, dy, cor: c.meio, alfa: .8 * b, tam: 1, luz: true });
  }
  return out;
}

/** os pixels do arrasto, de comprimento `comp` pixels de chao para a frente (o desenho poe o sinal): os dois sulcos dos pes, mais fundos no
    comeco (de onde o alvo saiu) */
export function pixelsDoArrasto(m: MarcaTR, comp: number, passo: number): PixelTR[] {
  const a = alfaDaMarca(m, passo); if (a <= 0 || comp < 1) return [];
  const out: PixelTR[] = [];
  for (let k = 0; k <= comp; k++) {
    const f = 1 - .5 * k / comp;
    out.push({ dx: k, dy: -1, cor: "#2a2018", alfa: .5 * a * f, tam: 1, luz: false });
    out.push({ dx: k, dy: 1, cor: "#2a2018", alfa: .5 * a * f, tam: 1, luz: false });
  }
  return out;
}

/** a onda de choque idade passos depois do acerto do pesado, para uma meia-largura de `meia` pixels de chao: dois aneis no chao que abrem e
    se apagam, brancos no comeco e na cor do elemento depois. Com o movimento reduzido, um anel so, sem luz */
export function pixelsDaOnda(el: ElementoTR, idade: number, meia: number, reduzido: boolean): PixelTR[] {
  if (idade < 0 || idade >= CHAO.durOnda + CHAO.ondaAtraso) return [];
  const c = ELEMENTO[el], out: PixelTR[] = [];
  for (const [k, atraso] of (reduzido ? [0] : [0, CHAO.ondaAtraso]).entries()) {
    const i = idade - atraso; if (i < 0 || i >= CHAO.durOnda) continue;
    const f = i / CHAO.durOnda, rx = Math.round(meia * (CHAO.ondaDe + (CHAO.ondaAte - CHAO.ondaDe) * Math.sqrt(f))), alfa = (1 - f) * (k ? .6 : 1);
    for (const [dx, dy] of anelDaElipse(rx, ry(rx))) {
      out.push({ dx, dy, cor: i < 4 ? "#ffffff" : c.borda, alfa, tam: f < .5 ? 2 : 1, luz: false });
      if (!reduzido) out.push({ dx: dx - 1, dy: dy - 1, cor: c.halo, alfa: alfa * .5, tam: 3, luz: true });
    }
  }
  return out;
}

/** as nuvens da poeira que vai para os dois lados (o pouso e o acerto do pesado): deslocamentos em pixels de poeira (dx com sinal) e o
    tamanho, que abrem, sobem e encolhem. Sem acaso */
export function poeiraDaNuvem(idade: number, forte: boolean): { dx: number; dy: number; tam: number }[] {
  if (idade < 0 || idade >= CHAO.durPouso) return [];
  const f = idade / CHAO.durPouso, out: { dx: number; dy: number; tam: number }[] = [], n = forte ? 4 : 3;
  for (const s of [1, -1]) for (let k = 0; k < n; k++)
    out.push({ dx: s * Math.round(2 + k * 2 + f * (5 + k * 2)), dy: Math.round(f * (2 + k) + (k % 2)), tam: Math.max(1, (forte ? 4 : 3) - Math.floor(f * 3) - (k > 2 ? 1 : 0)) });
  return out;
}
