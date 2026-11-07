/* As contas do toque digital do estilo Digital (docs/TAREFA_V3_MAPA_DIGITAL.md, D3), sem three e sem DOM, para o teste rodar em node
   (test/mapa_digital.test.ts); a vista (digital.ts) monta as malhas a partir delas.
     - lugaresDasParticulas: onde fica cada particula (x, y, z), sorteado pela rng com o sal de DIGITAL.particulas, sobre a area e a
       moldura perto dela, entre as alturas de DIGITAL.particulas.altura acima do chao;
     - segmentosDosFios: os segmentos dos fios entre os postes (x0, y0, z0, x1, y1, z1 por segmento): cada poste ligado aos vizinhos mais
       perto (ate DIGITAL.fios.porPoste, ate DIGITAL.fios.alcance celulas), sem repetir um par, cada fio uma parabola do alto de um poste ao
       do outro, com a queda proporcional ao vao. */
import { CAMERA_DESLOC, DIGITAL } from "./constantes.ts";
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

/** onde fica a lata gigante (D4) com o pet (o foco da camera e da dobra) em `foco`: o pe dela (x, y, z) e o giro. Ela fica no horizonte
    ao norte (DIGITAL.lata): x anda com o foco so com a fracao 1 - paralaxe, em volta do meio da area, mais `lado` vezes a meia largura
    visivel la longe (`meiaLargura`: a tangente da metade do campo de visao vezes o aspecto da tela; a distancia e `longe` mais o recuo
    da camera); y desconta a dobra do mundo (curvar: dobra * dz^2, com dz a distancia ao foco na direcao da dobra `dir`), para o pe
    ficar sempre na mesma altura na tela */
export function lugarDaLata(ilha: Ilha, foco: readonly [number, number], dobra: number, dir: readonly [number, number], meiaLargura: number):
    { x: number; y: number; z: number; giro: number } {
  const L = DIGITAL.lata, meio = ilha.area.w / 2;
  const x = meio + (foco[0] - meio) * (1 - L.paralaxe) + L.lado * (L.longe + CAMERA_DESLOC[2]) * meiaLargura, z = foco[1] - L.longe;
  const dz = (x - foco[0]) * dir[0] + (z - foco[1]) * dir[1];
  return { x, y: ilha.altura(foco[0], foco[1]) + L.base + dobra * dz * dz, z, giro: L.giro };
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
