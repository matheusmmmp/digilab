/* A geometria do minimapa (L1 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md): so contas, sem DOM nem React, para o teste conferir.
   Coordenadas em celulas (x para o leste, z para o sul); a imagem do mapa tem um pixel por celula e o ponto (x, z) cai no pixel
   (x - x0, z - z0) dela. Os numeros sao PROPOSTO, SEM FONTE (L1-7): so vista, nenhum numero de jogo. */
import type { Par } from "./cameraLivre.ts";

/** o diametro do circulo (px de CSS); PROPOSTO, SEM FONTE (L1-7) */
export const MINIMAPA_PX = 176;
/** px por celula na escala "B" (a janela em volta do ponto olhado; L1-1) */
export const ESCALA_B = 9;
/** o quanto de zoom cada toque da roda anda (0 = escala A, 1 = escala B); PROPOSTO, SEM FONTE */
export const ZOOM_PASSO = 0.2;
/** celulas que cada toque das setas anda a camera (com o foco no minimapa); PROPOSTO, SEM FONTE */
export const PASSO_SETA = 2;
/** um clique que nao andou mais que isto (px) e clique; alem, e arrasto */
export const LIMIAR_ARRASTO = 4;
/** o comprimento do cone da vista (celulas) */
export const CONE_CELULAS = 13;

export interface Area { w: number; h: number }
export interface Janela { centro: Par; ppc: number }

/** o zoom fica entre a escala A (0) e a B (1) */
export const limitarZoom = (z: number): number => Math.min(1, Math.max(0, Number.isFinite(z) ? z : 0));
/** a escala A: a area andavel inteira dentro do circulo (a diagonal cabe no diametro) */
export const escalaA = (a: Area): number => MINIMAPA_PX / Math.hypot(a.w, a.h);
/** px por celula num nivel de zoom: interpolacao geometrica, para o zoom parecer uniforme a cada toque */
export const pxPorCelula = (a: Area, z: number): number => {
  const A = escalaA(a);
  return A * Math.pow(ESCALA_B / A, limitarZoom(z));
};
/** o centro da janela: do meio da area (zoom 0) ao ponto olhado `foco` (zoom 1) */
export const centroDaJanela = (a: Area, foco: Par, z: number): Par => {
  const k = limitarZoom(z), mx = a.w / 2, mz = a.h / 2;
  return [mx + (foco[0] - mx) * k, mz + (foco[1] - mz) * k];
};
export const janelaDe = (a: Area, foco: Par, z: number): Janela => ({ centro: centroDaJanela(a, foco, z), ppc: pxPorCelula(a, z) });

/** celula -> px dentro do circulo (o canto de cima a esquerda e 0, 0) */
export const celulaParaPx = (c: Par, j: Janela, tam = MINIMAPA_PX): Par =>
  [tam / 2 + (c[0] - j.centro[0]) * j.ppc, tam / 2 + (c[1] - j.centro[1]) * j.ppc];
/** px dentro do circulo -> celula */
export const pxParaCelula = (p: Par, j: Janela, tam = MINIMAPA_PX): Par =>
  [j.centro[0] + (p[0] - tam / 2) / j.ppc, j.centro[1] + (p[1] - tam / 2) / j.ppc];
/** o px esta dentro do circulo (com uma folga em px) */
export const dentroDoCirculo = (p: Par, folga = 0, tam = MINIMAPA_PX): boolean =>
  Math.hypot(p[0] - tam / 2, p[1] - tam / 2) <= tam / 2 - folga;

/** a seta e o passo no plano da vista: [frente, lado] em celulas (cima = frente, direita = lado); null se a tecla nao e seta */
export function passoDaSeta(code: string, passo = PASSO_SETA): Par | null {
  switch (code) {
    case "ArrowUp": return [passo, 0];
    case "ArrowDown": return [-passo, 0];
    case "ArrowLeft": return [0, -passo];
    case "ArrowRight": return [0, passo];
    default: return null;
  }
}
/** o mesmo passo no chao (celulas, x leste e z sul), dado a frente da camera no chao `f` (a mesma conta de andar() em cameraLivre.ts) */
export const passoNoChao = (frente: number, lado: number, f: Par): Par => [f[0] * frente - f[1] * lado, f[1] * frente + f[0] * lado];

/** os dois pontos da base do cone da vista (celulas): do `foco`, `comp` celulas para a frente, abrindo `meia` rad para cada lado */
export function pontasDoCone(foco: Par, frente: Par, meia: number, comp = CONE_CELULAS): [Par, Par] {
  const gira = (a: number): Par => [
    foco[0] + comp * (frente[0] * Math.cos(a) - frente[1] * Math.sin(a)),
    foco[1] + comp * (frente[0] * Math.sin(a) + frente[1] * Math.cos(a))];
  return [gira(-meia), gira(meia)];
}

/** uma cor CSS ("#rgb", "#rrggbb" ou "rgb(a)(r, g, b[, a])") com outra opacidade, para o degrade do cone; falha alto se nao entender */
export function corComAlfa(cor: string, alfa: number): string {
  const c = cor.trim();
  let r: number, g: number, b: number;
  const h = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(c);
  if (h) {
    const x = h[1].length === 3 ? [...h[1]].map(d => d + d).join("") : h[1];
    r = parseInt(x.slice(0, 2), 16); g = parseInt(x.slice(2, 4), 16); b = parseInt(x.slice(4, 6), 16);
  } else {
    const m = /^rgba?\(\s*(\d+(?:\.\d+)?)[\s,]+(\d+(?:\.\d+)?)[\s,]+(\d+(?:\.\d+)?)/i.exec(c);
    if (!m) throw new Error("minimapa: cor que nao entendo: " + cor);
    r = +m[1]; g = +m[2]; b = +m[3];
  }
  return `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)}, ${alfa})`;
}
/** a cena guarda a cor como numero 0xRRGGBB: vira "rgb(r, g, b)" */
export const corDoNumero = (n: number): string => `rgb(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255})`;
