/* A camera da luta em tempo real (LUTA_EFEITOS, etapa E5; docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 3.5). So vista e puro (sem DOM): a
   camera acompanha a distancia entre os dois lutadores e chega mais perto quando eles estao perto, para eles ocuparem mais o palco.
   - O estado (CameraTR, em VisualTR.cam) anda com o passo da luta (seguirCameraTR, chamado pelo aplicarEventosTR uma vez por passo), nunca
     com o relogio do navegador: a mesma luta da a mesma camera. O nivel de zoom e da luta (em px do motor), com histerese, para nao piscar.
   - O quadro (cameraDoQuadro) le o estado e a tela: o zoom vira uma escala INTEIRA dos sprites maior que a de sempre, contada em px do canvas
     (e, como sempre foi: cada pixel do sprite e um numero inteiro de pixels da tela), e o mundo (o cenario, o x da luta, as marcas, os
     projeteis) acompanha na razao s = e / e0. Cada nivel sobe a escala CAMERA.passo da escala de sempre, arredondado para cima em px do
     canvas: num celular (o canvas em 2x ou 3x) o zoom anda em 1/3 e 2/3; com 1 px por px de CSS, em escalas de CSS inteiras. Os sprites nunca
     ficam em escala fracionaria (a licao do Dormir); na troca de nivel o mundo passa de um zoom ao outro em CAMERA.troca passos e o sprite
     pula de uma escala inteira para a outra.
   - Com o movimento reduzido, a troca e seca (sem a passagem); o centro segue igual.
   - O empurrao (a v18) afasta os dois de repente: a distancia da camera e a suavizada, mas o quadro sempre confere os dois lutadores de
     verdade na tela (com margem) e, se nao couberem, afasta o zoom no mesmo quadro. A cerca (o limite da luta, a 8 % da borda na tela sem
     zoom) fica dentro: o centro nunca passa do ponto em que o cenario deixaria de cobrir a tela. */
import { CTR_TR, type LutaTR } from "../../../../motor/index.ts";
import { geometriaTR, xTela, type CameraQuadro, type GeometriaTR } from "./projeteisTR.ts";

/** A camera (E5). PROPOSTO, SEM FONTE: ajustar nas capturas.
    - limiares: a distancia entre os centros (px do motor) abaixo da qual o zoom sobe um nivel (o 1.o: o medio do motor, 150, mais folga; o 2.o:
      o perto, 62, mais folga); histerese: a folga (px do motor) para voltar, para o nivel nao piscar na beira.
    - suave: a fracao do caminho que o centro e a distancia da camera andam por passo (16 ms) atras dos lutadores (0,08: ~90 % em 28 passos).
    - troca: os passos da passagem de um nivel ao outro (o mundo; o sprite pula de escala no meio).
    - passo: quanto cada nivel sobe a escala, em fracao da escala de sempre (arredondado para cima em px do canvas, pelo menos 1);
    - altMax: a altura maxima do sprite no zoom, em fracao da altura do palco (sem zoom e 0,45).
    - margem: o espaco minimo (px de CSS) entre o sprite e a borda da tela. */
export const CAMERA = { limiares: [190, 110], histerese: 18, suave: .08, troca: 18, passo: 1 / 3, altMax: .62, margem: 12 } as const;

/** o estado da camera, so do passo da luta: o centro e a distancia suavizados (px do motor), o nivel de zoom (0 sem zoom) e a ultima troca */
export interface CameraTR { meio: number; d: number; nivel: number; nivelDe: number; trocaEm: number }

/** o nivel para a distancia d, partindo do nivel atual (a histerese: subir exige passar do limiar menos a folga, descer, do limiar mais ela) */
export function nivelDaDistancia(d: number, atual: number): number {
  let n = 0;
  CAMERA.limiares.forEach((lim, k) => { const folga = k < atual ? CAMERA.histerese : -CAMERA.histerese; if (d < lim + folga) n = k + 1; });
  return n;
}

/** anda a camera um passo atras dos lutadores (a primeira chamada a poe neles, sem suavizar) */
export function seguirCameraTR(v: { cam: CameraTR | null }, sim: LutaTR): void {
  const [a, b] = sim.S.L, meio = (a.x + b.x) / 2, d = Math.abs(b.x - a.x), t = sim.S.passo;
  if (!v.cam) { const n = nivelDaDistancia(d, 0); v.cam = { meio, d, nivel: n, nivelDe: n, trocaEm: -Infinity }; return; }
  const c = v.cam;
  c.meio += (meio - c.meio) * CAMERA.suave; c.d += (d - c.d) * CAMERA.suave;
  const n = nivelDaDistancia(c.d, c.nivel);
  if (n !== c.nivel) { c.nivelDe = c.nivel; c.nivel = n; c.trocaEm = t; }
}

/** a camera que cabe: o centro (px da tela base) no meio dos lutadores, empurrado para os dois caberem com margem e preso onde o cenario ainda
    cobre a tela; null se com este zoom os dois nao cabem */
function caber(W: number, H: number, K: number, dims: readonly (readonly [number, number])[], xs: readonly number[], e: number, s: number, meio: number): { cam: CameraQuadro; geo: GeometriaTR } | null {
  const lim = (cx: number) => Math.max(W / (2 * s), Math.min(W - W / (2 * s), cx));
  const bordas = (g: GeometriaTR) => [Math.min(...g.centros.map((c, i) => c - g.meias[i])), Math.max(...g.centros.map((c, i) => c + g.meias[i]))];
  let cx = lim(xTela(meio, W));
  for (let k = 0; k < 3; k++) {
    const g = geometriaTR(W, H, K, dims, xs, { e, s, cx }), [esq, dir] = bordas(g);
    if (esq >= CAMERA.margem && dir <= W - CAMERA.margem) return { cam: { e, s, cx }, geo: g };
    if (dir - esq > W - 2 * CAMERA.margem || k === 2) return null;
    cx = lim(cx + (esq < CAMERA.margem ? esq - CAMERA.margem : dir - (W - CAMERA.margem)) / s);
  }
  return null;
}

/** a escala do sprite (px do canvas por pixel do sprite) no nivel n: e0 mais n passos de CAMERA.passo de e0 (pelo menos 1 px), limitada pela
    altura do palco */
export function escDoNivel(e0: number, n: number, H: number, K: number, altura: number): number {
  const passo = Math.max(1, Math.ceil(e0 * CAMERA.passo - 1e-9)), max = Math.floor(H * CAMERA.altMax * K / altura);
  return Math.max(e0, Math.min(e0 + n * passo, max));
}

/** a camera do quadro, a geometria com ela e a escala de sempre (e0, px do canvas). Sem estado (a previa), ou sem caber, a de sempre (s = 1,
    centro no meio). passo: o da luta */
export function cameraDoQuadro(cam: CameraTR | null, W: number, H: number, K: number, dims: readonly (readonly [number, number])[], xs: readonly number[], passo: number, reduzido: boolean): { cam: CameraQuadro; geo: GeometriaTR; e0: number } {
  const geo0 = geometriaTR(W, H, K, dims, xs), e0 = geo0.e, base = { cam: { e: e0, s: 1, cx: W / 2 }, geo: geo0, e0 };
  if (!cam) return base;
  const altura = Math.max(...dims.map(d => d[1]));
  /* a escala do nivel atual; na passagem (sem o movimento reduzido), o zoom do mundo vai do nivel anterior ao atual e o sprite fica na escala
     inteira mais perto */
  const para = escDoNivel(e0, cam.nivel, H, K, altura), de = escDoNivel(e0, cam.nivelDe, H, K, altura), idade = passo - cam.trocaEm;
  let s = para / e0;
  if (!reduzido && de !== para && idade >= 0 && idade < CAMERA.troca) { const f = (idade + 1) / CAMERA.troca, ease = f * f * (3 - 2 * f); s = (de + (para - de) * ease) / e0; }
  /* do zoom pedido para baixo, ate caber (os dois de verdade na tela: o empurrao e a cerca); abaixo do pedido, o mundo acompanha o sprite */
  const eS = Math.max(e0, Math.round(e0 * s));
  for (let e = eS; e > e0 || (e === e0 && e === eS && s > 1); e--) {
    const sQ = e === eS ? s : e / e0; if (sQ <= 1) break;
    const r = caber(W, H, K, dims, xs, e, sQ, cam.meio);
    if (r) return { ...r, e0 };
  }
  return base;
}

/** para os testes: o limite da luta (a cerca) em px do motor */
export const CERCA = [CTR_TR.centro - CTR_TR.meiaLargura, CTR_TR.centro + CTR_TR.meiaLargura] as const;
