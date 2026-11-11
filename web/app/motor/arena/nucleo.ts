/* Funcoes de apoio da simulacao (porte de web/app/arena/nucleo.ts do efb2ded): quem esta em campo, geometria da elipse, obstaculos e
   dano do ambiente. Mudancas da LP1: Math.hypot -> dist (a D-7), x ** 2 -> x * x, 1 contra 1 (sem equipe nem entrada em campo).
   LP6-1: a geometria le a elipse da luta (L.el: a ELIPSE, ou ela escalada pelo estagio dos dois, a secao 4a do plano da LP6). */
import { dist } from "./aritmetica.ts";
import type { EstadoLutador, Evento, Lado, Luta, Lutador, Obstaculo, Ref, Zona } from "./tipos.ts";

export const lutador = (L: Luta, l: Lado): Lutador => (l === "a" ? L.a : L.b);
export const outro = (l: Lado): Lado => (l === "a" ? "b" : "a");
export const emCampo = (L: Luta): Lutador[] => [L.a, L.b].filter(u => !u.morto && !u.foraAte);
export const ref = (u: Lutador): Ref => ({ lado: u.lado, n: u.n });
export const evento = (L: Luta, e: Evento): void => { L.eventos.push(e); };
export function mudar(u: Lutador, e: EstadoLutador): void { if (u.estado !== e) { u.estado = e; u.t = 0; } }

export const noElipse = (x: number, y: number, z: Zona): boolean => {
  const a = (x - z.x) / z.rx, b = (y - z.y) / z.ry; return a * a + b * b <= 1;
};
export const normArena = (L: Luta, x: number, y: number): number => dist((x - L.el.cx) / L.el.rx, (y - L.el.cy) / L.el.ry);
export function dentroArena(L: Luta, x: number, y: number): boolean {
  const a = (x - L.el.cx) / L.el.rx, b = (y - L.el.cy) / L.el.ry; return a * a + b * b <= 1;
}
export function paraCentro(L: Luta, u: Lutador, f: number): [number, number] {
  const dx = L.el.cx - u.x, dy = L.el.cy - u.y, d = dist(dx, dy) || 1; return [dx / d * f, dy / d * f];
}
export function fugirZona(u: Lutador, z: Zona, margem: number, f: number): [number, number] {
  const n = dist((u.x - z.x) / (z.rx * margem), (u.y - z.y) / (z.ry * margem));
  if (n > 1) return [0, 0];
  const dx = u.x - z.x, dy = u.y - z.y, d = dist(dx, dy) || 1;
  return [dx / d * f, dy / d * f];
}

/** dano do ambiente: fracao da vida maxima; acumula fracoes pequenas; o numero na tela sai no maximo a cada 500 ms */
export function ferir(L: Luta, u: Lutador, frac: number, motivo: string, mostrar = false): void {
  if (u.morto) return;
  u.acDano = u.acDano + frac * u.st.hp;
  const d = Math.floor(u.acDano); if (d < 1) return;
  const antes = u.hp;
  u.acDano -= d; u.hp = Math.max(0, u.hp - d);
  u.ultAmb = u.ultAmb + d;
  let mostra: { valor: number; x: number; y: number } | null = null;
  if (mostrar || L.relogio - u.ultNum > 500) { mostra = { valor: u.ultAmb, x: u.x, y: u.y }; u.ultNum = L.relogio; u.ultAmb = 0; }
  evento(L, { tipo: "ambiente", u: ref(u), perda: antes - u.hp, motivo, mostrar: mostra });
  if (u.hp <= 0) { u.morto = true; mudar(u, "die"); u.caiuEm = L.relogio; evento(L, { tipo: "queda", u: ref(u), motivo }); }
}

/** a cerca: ninguem sai da elipse (menos no ringue, onde sair e a regra da arena) */
export function prender(L: Luta, u: Lutador): void {
  if (L.cena.id === "ringue") return;
  const E = L.el, dx = (u.x - E.cx) / (E.rx - 20), dy = (u.y - E.cy) / (E.ry - 10), d = dist(dx, dy);
  if (d > 1) { u.x = E.cx + dx / d * (E.rx - 20); u.y = E.cy + dy / d * (E.ry - 10); }
}
const inteiro = (o: Obstaculo): boolean => !(o.hp !== undefined && o.hp <= 0);
/** obstaculos: pegada eliptica (r x 0,6r); empurram corpos */
export function colidir(L: Luta, u: Lutador): void {
  for (const o of L.cena.obst) {
    if (!inteiro(o)) continue;
    const r = o.r + u.raio * 0.5, dx = u.x - o.x, dy = (u.y - o.y) / 0.6, d = dist(dx, dy);
    if (d < r) { const k = (r - d) / (d || 1); u.x += dx * k; u.y += dy * k * 0.6; }
  }
}
export function obstaculoEm(L: Luta, x: number, y: number): Obstaculo | undefined {
  return L.cena.obst.find(o => inteiro(o) && dist(x - o.x, (y - o.y) / 0.6) < o.r);
}
/** primeiro obstaculo entre os dois, ou null */
export function bloqueio(L: Luta, a: Lutador, b: Lutador): Obstaculo | null {
  for (let i = 1; i < 12; i++) { const t = i / 12, o = obstaculoEm(L, a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t); if (o) return o; }
  return null;
}
