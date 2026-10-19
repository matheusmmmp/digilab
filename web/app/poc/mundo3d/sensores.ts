/* Os sensores do WORLD-POC-01a (docs/futuro/mundo_3d.md, seção 4.2): do mundo (a verdade) para a Observação (o que o pet sente).
   - a visão: um cone de 120 graus e raio RAIO_VISAO em torno da orientação; o que um sólido alto tapa (uma linha inteira do centro do
     pet ao centro do objeto) não aparece, e um obstáculo baixo não tapa;
   - os bigodes: em 8 setores, a distância livre até o círculo do pet bater num sólido, até RAIO_BIGODE;
   - o contato: o que encostou desde a última leitura, no setor relativo à orientação.
   Toda distância e direção sai relativa ao pet; nenhuma posição absoluta entra na Observação. O `ref` de cada objeto visto é um rótulo
   desta leitura; o mapa ref -> objeto fica com o simulador (`Leitura.refs`), fora do cérebro. */
import { COS_MEIO_CONE, MAX_VISTOS, RAIO_BIGODE, RAIO_VISAO } from "./config.ts";
import { bloqueioEm, pontoNoRetangulo } from "./fisica.ts";
import { DIRECOES_16, distancia, divArred, noSetor, setorDe } from "./inteiros.ts";
import type { Mundo } from "./mundo.ts";
import type { Categoria, Contato, CorpoPoc, Observacao, ResultadoPercebido, Visto } from "./tipos.ts";

/** o objeto do motor por trás de um `ref` (só o simulador vê isto) */
export type AlvoMundo = { tipo: "bola" } | { tipo: "comida"; id: number };
export interface Leitura { obs: Observacao; refs: Map<number, AlvoMundo> }

/** o setor relativo (0 a 15) de um setor absoluto, dada a orientação */
export const relativo = (setor: number, orientacao: number): number => (((setor - orientacao) % 16) + 16) % 16;

/** o objeto em (ox, oy) está dentro do cone da orientação? (dx, dy) = 0 conta como dentro */
export function noCone(dx: number, dy: number, orientacao: number): boolean {
  const d = distancia(dx, dy);
  if (d === 0) return true;
  const [ux, uy] = DIRECOES_16[orientacao];
  return dx * ux + dy * uy >= COS_MEIO_CONE * d;
}

/** a linha de (x0, y0) a (x1, y1) passa por um sólido alto? Os pontos p0 + (p1 - p0) k / n, k = 1 .. n - 1, n = max(|dx|, |dy|) */
export function tapado(m: Mundo, x0: number, y0: number, x1: number, y1: number): boolean {
  const dx = x1 - x0, dy = y1 - y0, n = Math.max(Math.abs(dx), Math.abs(dy));
  const altos = m.solidos.filter(s => s.alto);
  for (let k = 1; k < n; k++) {
    const x = x0 + divArred(dx * k, n), y = y0 + divArred(dy * k, n);
    if (altos.some(s => pontoNoRetangulo(x, y, s.ret))) return true;
  }
  return false;
}

/** a leitura dos sensores; `resultado` é o que o controlador devolveu da Intenção anterior (já filtrado). Com `consumir` (o padrão), os
 *  contatos lidos saem do mundo; sem ele (o fechamento do registro), ficam para a próxima Observação */
export function ler(m: Mundo, resultado: ResultadoPercebido | null, consumir = true): Leitura {
  const p = m.pet;
  const candidatos: { categoria: Categoria; distancia: number; setor: number; alvo: AlvoMundo; ordem: number }[] = [];
  const objetos: [Categoria, number, number, AlvoMundo, number][] = [["bola", m.bola.x, m.bola.y, { tipo: "bola" }, 0]];
  for (const c of m.comidas) if (c.ativa) objetos.push(["comida", c.x, c.y, { tipo: "comida", id: c.id }, c.id]);
  for (const [categoria, ox, oy, alvo, ordem] of objetos) {
    const dx = ox - p.x, dy = oy - p.y, d = distancia(dx, dy);
    if (d > RAIO_VISAO || !noCone(dx, dy, p.orientacao) || tapado(m, p.x, p.y, ox, oy)) continue;
    candidatos.push({ categoria, distancia: d, setor: relativo(setorDe(dx, dy), p.orientacao), alvo, ordem });
  }
  candidatos.sort((a, b) => a.distancia - b.distancia || a.categoria.localeCompare(b.categoria) || a.ordem - b.ordem);
  const refs = new Map<number, AlvoMundo>();
  const vistos: Visto[] = candidatos.slice(0, MAX_VISTOS).map((c, i) => {
    refs.set(i + 1, c.alvo);
    return { ref: i + 1, categoria: c.categoria, distancia: c.distancia, setor: c.setor };
  });
  const obstaculos: number[] = [];
  for (let k = 0; k < 8; k++) {
    const s = (p.orientacao + 2 * k) % 16;
    let livre = RAIO_BIGODE;
    for (let t = 1; t <= RAIO_BIGODE; t++) {
      const [x, y] = noSetor(p.x, p.y, s, t);
      if (bloqueioEm(x, y, p.r, m.solidos, []) !== null) { livre = t - 1; break; }
    }
    obstaculos.push(livre);
  }
  const contato: Contato[] = m.contatos.map(c => ({ categoria: c.categoria, setor: relativo(c.setor, p.orientacao) }))
    .sort((a, b) => a.categoria.localeCompare(b.categoria) || a.setor - b.setor);
  if (consumir) m.contatos = [];
  const corpo: CorpoPoc = { fome: p.fome, tedio: p.tedio };
  return { obs: { vistos, obstaculos, contato, resultado, corpo }, refs };
}

