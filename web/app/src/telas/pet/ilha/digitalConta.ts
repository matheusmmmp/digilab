/* As contas do toque digital do estilo Digital (docs/TAREFA_V3_MAPA_DIGITAL.md, D3), sem three e sem DOM, para o teste rodar em node
   (test/mapa_digital.test.ts); a vista (digital.ts) monta as malhas a partir delas.
     - lugaresDasParticulas: onde fica cada particula (x, y, z), sorteado pela rng com o sal de DIGITAL.particulas, sobre a area e a
       moldura perto dela, entre as alturas de DIGITAL.particulas.altura acima do chao;
     - segmentosDosFios: os segmentos dos fios entre os postes (x0, y0, z0, x1, y1, z1 por segmento): cada poste ligado aos vizinhos mais
       perto (ate DIGITAL.fios.porPoste, ate DIGITAL.fios.alcance celulas), sem repetir um par, cada fio uma parabola do alto de um poste ao
       do outro, com a queda proporcional ao vao. */
import { DIGITAL } from "./constantes.ts";
import { rng, type Ilha } from "./grade.ts";
import { ENFEITES_MODELOS } from "./modelos.ts";

export function lugaresDasParticulas(ilha: Ilha): [number, number, number][] {
  const P = DIGITAL.particulas, r = rng(P.sal), lugares: [number, number, number][] = [];
  for (let i = 0; i < P.quantas; i++) {
    const x = -P.margem + r() * (ilha.area.w + 2 * P.margem), z = -P.margem + r() * (ilha.area.h + 2 * P.margem);
    lugares.push([x, ilha.altura(x, z) + P.altura[0] + r() * (P.altura[1] - P.altura[0]), z]);
  }
  return lugares;
}

/** os pares de postes com fio (os indices na ordem de ilha.enfeites filtrada pelos postes) e o vao de cada um */
export function paresDosFios(ilha: Ilha): { a: number; b: number; vao: number }[] {
  const F = DIGITAL.fios, postes = ilha.enfeites.filter(e => e.nome === "poste"), ligados = new Set<string>(), pares: { a: number; b: number; vao: number }[] = [];
  postes.forEach((p, i) => {
    const viz = postes.map((q, j) => ({ j, d: Math.hypot(p.x - q.x, p.z - q.z) })).filter(v => v.j !== i && v.d <= F.alcance)
      .sort((u, v) => u.d - v.d);
    for (const v of viz.slice(0, F.porPoste)) {
      const a = Math.min(i, v.j), b = Math.max(i, v.j), chave = `${a}-${b}`;
      if (ligados.has(chave)) continue;
      ligados.add(chave);
      pares.push({ a, b, vao: v.d });
    }
  });
  return pares;
}

export function segmentosDosFios(ilha: Ilha): number[] {
  const F = DIGITAL.fios, postes = ilha.enfeites.filter(e => e.nome === "poste"), pos: number[] = [];
  const topo = (e: { x: number; z: number }): [number, number, number] => [e.x, ilha.altura(e.x, e.z) + ENFEITES_MODELOS.poste.altura * F.alto, e.z];
  for (const { a, b, vao } of paresDosFios(ilha)) {
    const p0 = topo(postes[a]), p1 = topo(postes[b]), queda = vao * F.queda;
    let ant = p0;
    for (let s = 1; s <= F.segmentos; s++) {
      const u = s / F.segmentos;
      const p: [number, number, number] = [p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u - 4 * queda * u * (1 - u), p0[2] + (p1[2] - p0[2]) * u];
      pos.push(...ant, ...p);
      ant = p;
    }
  }
  return pos;
}

/** os desenhos de um anel do portal do ceu (DIGITAL.portal): a linha cheia, os tracos, as marcas (riscos para fora), os blocos (quadradinhos
    de dados) e a linha dupla */
export const DESENHOS_DE_ANEL = ["linha", "tracos", "marcas", "blocos", "dupla"] as const;
export type DesenhoDeAnel = (typeof DESENHOS_DE_ANEL)[number];
export interface AnelDoPortal { raio: number; desenho: DesenhoDeAnel; partes: number; volta: number; fase: number }

/** os aneis concentricos do portal, de dentro para fora: o raio cresce por igual, o desenho alterna (o de fora e sempre a linha cheia, o
    arco grande das referencias), `partes` e quantos tracos, marcas ou blocos cabem na volta (mais nos de fora), `volta` sao os segundos por
    volta com o sinal do lado (um para cada lado, o de dentro mais depressa) e `fase` o giro de partida, da rng com o sal do portal */
export function aneisDoPortal(): AnelDoPortal[] {
  const P = DIGITAL.portal, r = rng(P.sal), aneis: AnelDoPortal[] = [];
  for (let k = 0; k < P.aneis; k++) {
    const u = k / Math.max(1, P.aneis - 1), raio = P.raio[0] + (P.raio[1] - P.raio[0]) * u;
    const desenho = k === P.aneis - 1 ? "linha" : DESENHOS_DE_ANEL[1 + (k % (DESENHOS_DE_ANEL.length - 1))];
    aneis.push({ raio, desenho, partes: 8 * Math.max(1, Math.round(raio / 3)), volta: (k % 2 ? -1 : 1) * (P.volta[0] + (P.volta[1] - P.volta[0]) * u), fase: r() * Math.PI * 2 });
  }
  return aneis;
}
