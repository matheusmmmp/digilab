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
