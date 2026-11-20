/* LUTA_POC, LP5-2 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, a D-LP5-17): o criterio do P1 a P3, PROPOSTO, SEM FONTE.
   O lider fica no meio do caminho entre o pet sem treino e o tipico, na escala logistica do T1 do lp5_1_esq (0,832, 0,902, 0,942 e 0,959,
   do Rookie ao Mega), com 0,10 de folga: sem treino <= sigma(-d/2) + 0,10 e tipico >= sigma(d/2) - 0,10, com d = logit(T1). O desafiante
   mantem a folga de antes sobre o lider (+0,15 no sem treino, +0,05 no tipico). A pior especie sai do criterio e vai ao lado */
export const T1_DO_CRITERIO: Readonly<Record<string, number>> = { crianca: .832, adolescente: .902, adulto: .942, mega: .959 };
export const FOLGA_LIDER = .10, DESAFIANTE_SEM = .15, DESAFIANTE_TIP = .05;

/** os limites do NPC no estagio dele, arredondados a 0,01 */
export function limitesNpc(estagio: string, desafiante: boolean): { sem: number; tip: number } {
  const t1 = T1_DO_CRITERIO[estagio];
  if (t1 === undefined) throw new Error(`criterio: o estagio ${estagio} nao tem T1`);
  const meio = 1 / (1 + Math.exp(Math.log(t1 / (1 - t1)) / 2)), r = (x: number) => Math.round(x * 100) / 100;
  return { sem: r(meio + FOLGA_LIDER + (desafiante ? DESAFIANTE_SEM : 0)), tip: r(1 - meio - FOLGA_LIDER + (desafiante ? DESAFIANTE_TIP : 0)) };
}
/** o NPC passa: o pet sem treino ate o limite e o tipico a partir dele */
export const passaNpc = (estagio: string, desafiante: boolean, sem: number, tip: number): boolean => {
  const l = limitesNpc(estagio, desafiante);
  return sem <= l.sem && tip >= l.tip;
};
