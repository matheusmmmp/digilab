/* LUTA_POC, LP5 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 5; D-LP5-6): as faixas de sementes da rodada, reservadas na FAIXAS_RESERVADAS
   (experiments/bancada/faixas.py). A calibracao (LP5-0 a LP5-3) e a conferencia (LP5-4, uma vez) nao se misturam. A prova de reproducao
   da LP5-0 usa as sementes de teste da LP4 (medir_lp4_gazimon.ts), fora deste mapa. */
/* a investigacao: a investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, D-N-2), as lutas fixas da N2 e os contrafactuais da N4 */
export const FAIXAS = { calibracao: 86101, conferencia: 87101, investigacao: 92101 } as const; // tambem a LP6-3 (docs/PLANO_LP6_SEGUNDO_GOLPE.md, secao 8)
export type NomeFaixa = keyof typeof FAIXAS;
/** as 5 bases de uma faixa (x101, x202, x303, x404, x505) */
export function basesDa(nome: string): number[] {
  if (!Object.hasOwn(FAIXAS, nome)) throw new Error(`faixa desconhecida: ${JSON.stringify(nome)} (so ${Object.keys(FAIXAS).join(", ")})`);
  const b = FAIXAS[nome as NomeFaixa];
  return [0, 101, 202, 303, 404].map(d => b + d);
}
