/* O corte do pet em papel (papel.ts), as contas sem DOM (testadas em node). O corte de cada sprite e a caixa do que e opaco no Idle e no Run;
   um clipe fora da locomocao (o Attack_1, o Comer com o Comer_objeto: docs/TAREFA_V3_SPRITES_ACOES.md, 3.4 e M3) usa o corte alargado, que
   cabe todos os quadros dele com o MESMO centro e o MESMO pe do corte do sprite: o papel cresce para os dois lados, e o Digimon nao pula
   ao trocar de clipe. So desenho. */

/** o corte do sprite: as colunas x0 a x1 (inclusive) e as linhas acima de `pe`, onde ha pixel opaco em algum quadro. Um corte alargado pode
    passar das bordas do quadro (x0 < 0 ou x1 alem da largura): o que fica fora e transparente */
export interface Corte { x0: number; x1: number; pe: number }

/** a uniao das caixas (null onde o quadro nao tem nada opaco); null se nenhuma tem */
export function unirCaixas(caixas: readonly (Corte | null)[]): Corte | null {
  let u: Corte | null = null;
  for (const k of caixas) if (k) u = u ? { x0: Math.min(u.x0, k.x0), x1: Math.max(u.x1, k.x1), pe: Math.max(u.pe, k.pe) } : { ...k };
  return u;
}

/** o corte alargado: o `base` crescido para os dois lados ate caber as colunas de todas as `caixas`, com o mesmo centro (x0 + x1 igual, em
    meios texels, sem arredondar) e o mesmo pe (abaixo dele, so a sombra do export, que sai) */
export function alargarCorte(base: Corte, caixas: readonly (Corte | null)[]): Corte {
  const u = unirCaixas([base, ...caixas])!;
  const c2 = base.x0 + base.x1, meia = Math.max(c2 - 2 * u.x0, 2 * u.x1 - c2);
  /* c2 - meia e c2 + meia tem a mesma paridade: o piso de uma metade mais o teto da outra da c2 de novo */
  return { x0: Math.floor((c2 - meia) / 2), x1: Math.ceil((c2 + meia) / 2), pe: base.pe };
}
