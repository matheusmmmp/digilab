/* A TV do jogo do protótipo P0 (docs/futuro/gosto_visual_pet.md, seção 2.2; a GV-1 recomenda começar por ela): programas sintéticos,
   cada um com um perfil de vetor e uma variação pequena, trocados a cada PROGRAMA_SEGUNDOS. Não captura nada do computador; serve para
   ver as reações sem compartilhar a tela, e onde o navegador não deixa capturar. Determinística: a mesma semente dá a mesma sequência.
   Os perfis e os tempos são PROPOSTOS, SEM FONTE. */
import { criarRng, hashSemente } from "../../motor/rng.ts";
import type { Sentido } from "./gosto.ts";

export interface Programa { nome: string; perfil: Sentido }
export const PROGRAMAS: readonly Programa[] = [
  { nome: "desenho colorido e agitado", perfil: { visao: { cor: 0.85, brilho: 0.7, movimento: 0.8, complexidade: 0.6 }, som: { volume: 0.7, variacao: 0.7, timbre: 0.6 } } },
  { nome: "documentário calmo", perfil: { visao: { cor: 0.35, brilho: 0.45, movimento: 0.15, complexidade: 0.5 }, som: { volume: 0.3, variacao: 0.2, timbre: 0.3 } } },
  { nome: "planilha", perfil: { visao: { cor: 0.08, brilho: 0.9, movimento: 0.02, complexidade: 0.75 }, som: { volume: 0.02, variacao: 0.05, timbre: 0.1 } } },
  { nome: "show de música", perfil: { visao: { cor: 0.6, brilho: 0.25, movimento: 0.6, complexidade: 0.4 }, som: { volume: 0.9, variacao: 0.8, timbre: 0.8 } } },
];
/** quanto dura cada programa, e o tamanho da variação dentro dele */
export const PROGRAMA_SEGUNDOS = 25, VARIACAO_DENTRO = 0.06;

const limitar = (x: number): number => (x < 0 ? 0 : x > 1 ? 1 : x);

/** liga a TV: um Sentido por segundo, até `parar` */
export function ligarTvDoJogo(semente: number, aoSentir: (s: Sentido, programa: string) => void, periodoMs = 1000): { parar(): void } {
  const rng = criarRng(hashSemente("gosto-visual-tv", semente));
  let seg = 0, atual = rng.int(PROGRAMAS.length);
  const t = setInterval(() => {
    if (seg > 0 && seg % PROGRAMA_SEGUNDOS === 0) atual = (atual + 1 + rng.int(PROGRAMAS.length - 1)) % PROGRAMAS.length;
    seg++;
    const p = PROGRAMAS[atual]!, ruido = (): number => (rng.random() * 2 - 1) * VARIACAO_DENTRO;
    const v = p.perfil.visao, s = p.perfil.som!;
    aoSentir({
      visao: { cor: limitar(v.cor + ruido()), brilho: limitar(v.brilho + ruido()), movimento: limitar(v.movimento + ruido()), complexidade: limitar(v.complexidade + ruido()) },
      som: { volume: limitar(s.volume + ruido()), variacao: limitar(s.variacao + ruido()), timbre: limitar(s.timbre + ruido()) },
    }, p.nome);
  }, periodoMs);
  return { parar: () => clearInterval(t) };
}
