/* A camera do primeiro dia (a regra 6 de "guiar o olhar sem texto", docs/pranchas/ux-ilha-planta-a/LEIA.md; a prancha em
   docs/pranchas/ux-ilha-abertura/): na primeira vez que a ilha abre, a camera mostra o lugar devagar e volta ao pet. PROTOTIPO da prancha, so
   atras de ?abertura=a|b|c; sem o parametro nada muda. So vista: fora do save, do registro e do replay.
   Uma abertura e uma lista de quadros-chave (o tempo, o ponto olhado, o zoom e a inclinacao somada); entre dois quadros a camera anda pela
   curva suave (suavizar). O ponto olhado e um nome (o ninho, a praca, o portao, a barraca, o pet ou o meio entre o pet e a praca) e a vista diz onde
   cada um fica.
   Os tempos, os zooms e as inclinacoes sao PROPOSTO, SEM FONTE. */

export type Proposta = "a" | "b" | "c";
export type Ponto = "pet" | "ninho" | "praca" | "portao" | "barraca" | "meio";
export type Par = [number, number];
export interface QuadroChave { t: number; em: Ponto; zoom: number; inclina: number }
export interface QuadroAbertura { foco: Par; zoom: number; inclina: number; acabou: boolean }

/** as tres propostas (ms; zoom < 1 aproxima; inclina em rad, > 0 sobe) */
export const ABERTURAS: Record<Proposta, readonly QuadroChave[]> = {
  /* A, o passeio: perto do ninho, a praca, um olhar para o portao, a volta ao pet (7 s) */
  a: [
    { t: 0, em: "ninho", zoom: 0.6, inclina: 0 },
    { t: 1200, em: "ninho", zoom: 0.6, inclina: 0 },
    { t: 3600, em: "praca", zoom: 1.3, inclina: 0.15 },
    { t: 5000, em: "portao", zoom: 1.5, inclina: 0.2 },
    { t: 7000, em: "pet", zoom: 1, inclina: 0 },
  ],
  /* B, o afastar: perto do pet, a camera recua e sobe ate a praca e o portao caberem com o pet ainda no quadro, e volta (5 s) */
  b: [
    { t: 0, em: "pet", zoom: 0.55, inclina: 0 },
    { t: 700, em: "pet", zoom: 0.55, inclina: 0 },
    { t: 3200, em: "meio", zoom: 1.9, inclina: 0.3 },
    { t: 3900, em: "meio", zoom: 1.9, inclina: 0.3 },
    { t: 5200, em: "pet", zoom: 1, inclina: 0 },
  ],
  /* C, de cima: a ilha inteira vista do alto sobre a praca, descendo ate o pet (4 s) */
  c: [
    { t: 0, em: "praca", zoom: 2.4, inclina: 0.6 },
    { t: 900, em: "praca", zoom: 2.4, inclina: 0.6 },
    { t: 4000, em: "pet", zoom: 1, inclina: 0 },
  ],
};

/** a proposta pedida no endereco: null sem o parametro; um valor que nao existe falha alto */
export function propostaDe(q: string | null): Proposta | null {
  if (q === null) return null;
  if (q === "a" || q === "b" || q === "c") return q;
  throw new Error(`?abertura=${q}: as propostas sao a, b e c`);
}
export const ABERTURA_PROPOSTA: Proposta | null =
  typeof location === "undefined" ? null : propostaDe(new URLSearchParams(location.search).get("abertura"));

/** quanto dura a abertura (ms) */
export const duracao = (p: Proposta): number => ABERTURAS[p][ABERTURAS[p].length - 1].t;

/** a curva suave de 0 a 1 (comeca e chega devagar) */
export const suavizar = (s: number): number => { const x = Math.min(1, Math.max(0, s)); return x * x * (3 - 2 * x); };

/** o quadro da abertura `p` no tempo `t` (ms desde o inicio), com os pontos de agora; depois do fim, o ultimo quadro com `acabou` */
export function quadroDaAbertura(p: Proposta, t: number, pontos: Record<Ponto, Par>): QuadroAbertura {
  const qs = ABERTURAS[p];
  if (!Number.isFinite(t) || t < 0) throw new Error(`quadroDaAbertura: tempo invalido ${t}`);
  const fim = qs[qs.length - 1];
  if (t >= fim.t) return { foco: [...pontos[fim.em]] as Par, zoom: fim.zoom, inclina: fim.inclina, acabou: true };
  let i = 0;
  while (qs[i + 1].t <= t) i++;
  const a = qs[i], b = qs[i + 1], s = suavizar((t - a.t) / (b.t - a.t));
  const pa = pontos[a.em], pb = pontos[b.em];
  return {
    foco: [pa[0] + (pb[0] - pa[0]) * s, pa[1] + (pb[1] - pa[1]) * s],
    zoom: a.zoom + (b.zoom - a.zoom) * s,
    inclina: a.inclina + (b.inclina - a.inclina) * s,
    acabou: false,
  };
}

/** o relogio do prototipo: comeca no primeiro quadro com a ilha a vista; `fixo` para o tempo (as capturas da prancha) */
export const RELOGIO_ABERTURA: { inicio: number | null; fixo: number | null } = { inicio: null, fixo: null };
export function tempoDaAbertura(agora: number): number {
  if (RELOGIO_ABERTURA.fixo !== null) return RELOGIO_ABERTURA.fixo;
  /* o laco da cena e o do veu passam relogios que podem vir um pouco fora de ordem (o do quadro e o performance.now): antes do inicio vale 0 */
  RELOGIO_ABERTURA.inicio ??= agora;
  return Math.max(0, agora - RELOGIO_ABERTURA.inicio);
}
/** window.__abertura para as capturas: em(t) para o tempo em t ms, tocar() recomeca andando, duracao */
export function ligarAberturaDev(): () => void {
  const p = ABERTURA_PROPOSTA;
  if (!p) return () => {};
  const g = globalThis as { __abertura?: unknown };
  g.__abertura = {
    duracao: duracao(p),
    em(t: number) { RELOGIO_ABERTURA.fixo = t; },
    tocar() { RELOGIO_ABERTURA.fixo = null; RELOGIO_ABERTURA.inicio = null; },
  };
  return () => { delete g.__abertura; };
}

/** o deslocamento da camera com a inclinacao `d` somada (rad), mantendo a distancia e o lado */
export function inclinar(desloc: readonly [number, number, number], d: number): [number, number, number] {
  const [dx, dy, dz] = desloc, plano = Math.hypot(dx, dz), r = Math.hypot(plano, dy);
  if (plano < 1e-9) return [dx, dy, dz];
  const e = Math.atan2(dy, plano) + d, k = (r * Math.cos(e)) / plano;
  return [dx * k, r * Math.sin(e), dz * k];
}
