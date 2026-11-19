/* Os lugares da ilha que estao trancados agora (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.4): o saco (Crescer, Nv 3), o portao (Lutar, Nv 4) e a barraca
   (Diario, Nv 2). Uma tabela minima, sem import de runtime, para a vista 3D (ilha/vista.ts, via ilha/lugares.ts `estadoDoLugar`) ler a cada quadro sem
   puxar o React nem o jogo. Quem escreve e o nivelTela.ts, a partir do nivel do Tamer (nivel.ts); `versao` sobe so quando algo muda. So vista. */
import type { Lugar } from "./viagem.ts";

export const TRANCAS: { saco: boolean; portao: boolean; barraca: boolean; versao: number } = { saco: false, portao: false, barraca: false, versao: 0 };

/** poe o estado dos tres lugares (true = trancado); devolve se algo mudou */
export function definirTrancas(t: Readonly<Record<Lugar, boolean>>): boolean {
  if (TRANCAS.saco === t.saco && TRANCAS.portao === t.portao && TRANCAS.barraca === t.barraca) return false;
  TRANCAS.saco = t.saco; TRANCAS.portao = t.portao; TRANCAS.barraca = t.barraca; TRANCAS.versao++;
  return true;
}
export const lugarTrancado = (l: Lugar): boolean => TRANCAS[l];

/* O cais (MMO5; docs/PLANO_UX_CAIS.md): so existe com o servidor no build. `ligado` falso: a vista o deixa como sempre foi (o modelo
   normal, sem cadeado e sem marca no minimapa). Ligado e trancado, a vista o apaga como os outros lugares trancados; ligado e aberto,
   ele volta ao normal. Quem escreve e o nivelTela.ts; `versao` sobe so quando algo muda. So vista. */
export const CAIS: { ligado: boolean; trancado: boolean; versao: number } = { ligado: false, trancado: true, versao: 0 };
export function definirCais(ligado: boolean, trancado: boolean): boolean {
  if (CAIS.ligado === ligado && CAIS.trancado === trancado) return false;
  CAIS.ligado = ligado; CAIS.trancado = trancado; CAIS.versao++;
  return true;
}

/* As tacas da temporada (MMO7; o enfeite do ranking que nao se vende na loja): as temporadas que o servidor diz que a conta ganhou
   (GET /premios, cais/premios.ts). Vazio sem a chave do cais, sem a conta ou antes da resposta: a ilha fica como sempre foi. Quem escreve
   e o cais/premios.ts; `versao` sobe so quando algo muda. So vista. */
export const TACAS_DA_CONTA: { temporadas: readonly number[]; versao: number } = { temporadas: [], versao: 0 };
export function definirTacas(temporadas: readonly number[]): boolean {
  const novas = [...new Set(temporadas)].sort((a, b) => b - a);
  if (novas.length === TACAS_DA_CONTA.temporadas.length && novas.every((t, i) => t === TACAS_DA_CONTA.temporadas[i])) return false;
  TACAS_DA_CONTA.temporadas = novas; TACAS_DA_CONTA.versao++;
  return true;
}
