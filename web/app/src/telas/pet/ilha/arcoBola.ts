/* O arco da bola no lance do dono (docs/TAREFA_V3_BOLA_BRINCAR.md, BB-9; a etapa BB3). SO VISTA: o motor ja pos a bola parada no ponto do
   lance (o `lances` do Mundo, BB-1); aqui ela so voa ate la, do lado da camera (de onde o dono joga), num arco no ar, em vez de aparecer
   no lugar. Nada daqui vai ao motor, ao log nem ao save. Sem DOM nem three: as contas sao testadas em node (test/bola_brincar_vista.test.ts).
   Os numeros sao da vista: PROPOSTO, SEM FONTE. */

/** o arco: quanto dura (ms), de quantas celulas do ponto do lance a bola sai (para o lado da camera), de que altura (a mao do dono) e quanto
    sobe acima da reta (celulas) */
export const ARCO_BOLA = { ms: 650, recuo: 5, alturaMao: 1.2, altura: 1.6 } as const;

export type Par = readonly [number, number];
/** um arco em curso: quando comecou (ms da vista), de onde sai e onde cai (celulas no chao), e quanto dura */
export interface ArcoBola { desde: number; de: Par; para: Par; ms: number }

/** de onde a bola sai: `recuo` celulas a partir do ponto do lance, na direcao do chao sob a camera (`camChao`, celulas); com a camera em cima
    do ponto (ou mais perto que o recuo), sai do chao sob a camera */
export function origemDoArco(para: Par, camChao: Par, recuo: number = ARCO_BOLA.recuo): [number, number] {
  if (!(recuo >= 0) || !Number.isFinite(recuo)) throw new Error(`origemDoArco: recuo invalido ${recuo}`);
  for (const v of [...para, ...camChao]) if (!Number.isFinite(v)) throw new Error("origemDoArco: ponto nao finito");
  const dx = camChao[0] - para[0], dz = camChao[1] - para[1], d = Math.hypot(dx, dz);
  if (d <= recuo) return [camChao[0], camChao[1]];
  return [para[0] + (dx / d) * recuo, para[1] + (dz / d) * recuo];
}

/** um arco novo, a partir de `agora`, do lado da camera ate `para` */
export function novoArco(agora: number, para: Par, camChao: Par, ms: number = ARCO_BOLA.ms): ArcoBola {
  if (!(ms > 0) || !Number.isFinite(ms)) throw new Error(`novoArco: duracao invalida ${ms}`);
  return { desde: agora, de: origemDoArco(para, camChao), para: [para[0], para[1]], ms };
}

/** onde a bola esta no arco em `agora`: x e z no chao (celulas) e a altura acima dele (celulas): sai da mao (`alturaMao`), sobe ate `altura`
    acima da reta e cai no chao em `para`. `acabou` quando o tempo passou (a bola no ponto do lance, no chao). Antes de `desde`, na mao */
export function pontoDoArco(a: ArcoBola, agora: number): { x: number; z: number; y: number; acabou: boolean } {
  const f = Math.min(1, Math.max(0, (agora - a.desde) / a.ms));
  const x = a.de[0] + (a.para[0] - a.de[0]) * f, z = a.de[1] + (a.para[1] - a.de[1]) * f;
  const y = ARCO_BOLA.alturaMao * (1 - f) + 4 * ARCO_BOLA.altura * f * (1 - f);
  return { x, z, y, acabou: f >= 1 };
}
