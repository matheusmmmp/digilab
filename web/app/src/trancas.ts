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
