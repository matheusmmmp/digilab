/* Motivo (espelho de digilab/motivo.py). Somente leitura: nao muda decisao.
   Fator so se a contribuicao e positiva, >= limiar e o termo aprendido MUDOU a escolha (sem ele,
   log-prior + Gumbel daria outra acao). */
import { FATORES_MEMORIA } from "./constantes.ts";
import { CATALOGO_V2, DIST, type Cond } from "./combate.ts";

export const FATOR_BASE = ["habito", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "hora", "tempo_sem_cuidado"];
export const FATOR_DA_FEATURE = [...FATOR_BASE, ...FATORES_MEMORIA];

export function nomeCond(c: Cond): string {
  const tipos = CATALOGO_V2[c.n];
  return c.p.length ? `${c.n}(${c.p.map((x, i) => tipos[i] === "d" ? DIST[x as number] : x).join(",")})` : c.n;
}
