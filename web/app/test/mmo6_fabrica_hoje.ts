/* MMO6 (docs/PLANO_V3_MMO.md, secao 6; MMO-10): as tentativas da Fabrica de hoje, para o gabarito gravado ANTES da mudanca no
   motor/fabrica.ts (as sementes vindas de fora, atras de chave). Desligada a chave, cada tentativa daqui sai byte a byte igual.

   Cada tentativa: o numero n, o alugado escolhido e uma regra fixa de troca (trocar depois da vitoria k quando k % ritmo === 0; ritmo 0 =
   nunca troca). Joga ate perder, ou ate LUTAS_MAX. Grava as sementes, os alugados, cada luta (o alugado, o rival, a vitoria, a vida no fim
   e o sha256 do resultado inteiro da luta) e o resumo. Rodar em Node (o V8 do navegador difere no ultimo bit de Math.exp). */
import { createHash } from "node:crypto";
import { TentativaFabrica, VERSAO_FABRICA_POC, alugueisFabrica, chaveSprite, formaRivalFabrica, sementeFabrica, sementeLutaFabrica } from "../motor/index.ts";

/** as tentativas do gabarito: [n, escolha, ritmo da troca], n de 1 a 40, a escolha n % 3 e o ritmo n % 4 */
export const TENTATIVAS_HOJE: readonly (readonly [number, number, number])[] =
  Array.from({ length: 40 }, (_, i) => [i + 1, (i + 1) % 3, (i + 1) % 4] as const);
/** o teto de lutas de uma tentativa do gabarito (a Fabrica nao tem teto; aqui so para o gabarito nao rodar sem fim) */
export const LUTAS_MAX = 24;

const sha = (x: unknown): string => createHash("sha256").update(JSON.stringify(x)).digest("hex");

export interface TentativaHoje {
  n: number; escolha: number; ritmo: number; s: number; alugueis: string[];
  sementesLuta: number[]; rivais: string[];
  lutas: { k: number; s: number; alugado: string; rival: string; venceu: boolean; vidaFim: number; trocou: boolean; poc: string }[];
  vitorias: number; series: number; acabou: boolean; vidaAgora: number;
}

export function jogarHoje(n: number, escolha: number, ritmo: number): TentativaHoje {
  const t = new TentativaFabrica(n, escolha, VERSAO_FABRICA_POC);
  while (t.lutas.length < LUTAS_MAX) {
    const p = t.proxima();
    if (!p) break;
    const l = t.lutar(p.s);
    if (l.venceu && ritmo > 0 && l.k % ritmo === 0) t.trocar();
  }
  const s = sementeFabrica(n), ks = [...Array(LUTAS_MAX).keys()];
  return {
    n, escolha, ritmo, s, alugueis: alugueisFabrica(s).map(chaveSprite),
    sementesLuta: ks.map(k => sementeLutaFabrica(s, k)), rivais: ks.map(k => chaveSprite(formaRivalFabrica(s, k))),
    lutas: t.lutas.map(l => ({ k: l.k, s: l.s, alugado: chaveSprite(l.alugado), rival: chaveSprite(l.rival), venceu: l.venceu, vidaFim: l.vidaFim,
      trocou: l.trocou, poc: sha(l.poc) })),
    vitorias: t.vitorias, series: t.series, acabou: t.acabou, vidaAgora: t.vidaAgora,
  };
}

export const todasHoje = (): TentativaHoje[] => TENTATIVAS_HOJE.map(([n, e, r]) => jogarHoje(n, e, r));
