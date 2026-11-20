/* A rota do pet na ida a um lugar aberto, na ilha com agua (docs/TAREFA_V3_ILHA_AGUA.md, IA4), sem three e sem DOM: a ida e a volta sao
   so vista (vista.ts, petNaViagem), e em linha reta cruzariam o rio. Aqui a rota contorna a agua pelo mesmo caminho do motor (o A* do
   contrato, motor/contrato.ts, sobre as celulas de terra do layout): de um ponto a outro, pelos centros das celulas do caminho. Sem agua
   no layout, a rota e a reta de sempre. Em celulas do mundo (x leste, z sul). */
import { caminho, celulasSecas, livreMaisPerto, type ConfigMundo } from "../../../../motor/index.ts";

export type Ponto = [number, number];

/** a rota de `de` a `para`: os dois pontos e, entre eles, os centros das celulas do caminho em terra. O ponto que cai na agua vale o
    centro da celula de terra mais perto. Sem agua no layout, [de, para] */
export function rotaEmTerra(cm: ConfigMundo, de: Ponto, para: Ponto): Ponto[] {
  const secas = celulasSecas(cm);
  if (secas === null) return [de, para];
  const W = cm.celulas_x, H = cm.celulas_y;
  const cel = (p: Ponto): Ponto => [Math.min(W - 1, Math.max(0, Math.floor(p[0]))), Math.min(H - 1, Math.max(0, Math.floor(p[1])))];
  const seca = (c: Ponto) => secas[c[1] * W + c[0]];
  const a0 = cel(de), b0 = cel(para), a = seca(a0) ? a0 : livreMaisPerto(secas, W, a0), b = seca(b0) ? b0 : livreMaisPerto(secas, W, b0);
  const celulas = caminho(secas, W, H, a, b);
  if (celulas === null) throw new Error(`sem caminho em terra de ${a.join(",")} a ${b.join(",")} na ilha ${cm.layout.nome}`);
  const centro = (c: readonly [number, number]): Ponto => [c[0] + 0.5, c[1] + 0.5];
  /* as pontas: o ponto pedido, se esta em terra; senao o centro da celula de terra. O meio: os centros, sem a primeira e a ultima celula
     quando a ponta pedida ja esta nelas */
  const ini: Ponto = seca(a0) ? de : centro(a), fim: Ponto = seca(b0) ? para : centro(b);
  const meio = celulas.slice(1, -1).map(centro);
  return celulas.length <= 1 ? [ini, fim] : [ini, ...meio, fim];
}

/** o comprimento da rota (celulas) */
export function comprimento(rota: readonly Ponto[]): number {
  let d = 0;
  for (let k = 1; k < rota.length; k++) d += Math.hypot(rota[k][0] - rota[k - 1][0], rota[k][1] - rota[k - 1][1]);
  return d;
}

/** o ponto da rota na fracao `f` (0 a 1) do comprimento dela */
export function naRota(rota: readonly Ponto[], f: number): Ponto {
  if (rota.length === 0) throw new Error("rota vazia");
  const total = comprimento(rota);
  if (f <= 0 || total === 0) return [rota[0][0], rota[0][1]];
  if (f >= 1) { const u = rota[rota.length - 1]; return [u[0], u[1]]; }
  let falta = Math.min(1, f) * total;
  for (let k = 1; k < rota.length; k++) {
    const d = Math.hypot(rota[k][0] - rota[k - 1][0], rota[k][1] - rota[k - 1][1]);
    if (falta <= d) { const t = d === 0 ? 0 : falta / d; return [rota[k - 1][0] + (rota[k][0] - rota[k - 1][0]) * t, rota[k - 1][1] + (rota[k][1] - rota[k - 1][1]) * t]; }
    falta -= d;
  }
  const u = rota[rota.length - 1];
  return [u[0], u[1]];
}
