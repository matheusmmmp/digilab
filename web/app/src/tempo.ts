/* Tempo do jogo (igual ao HTML): anda pelo tempo REAL decorrido, na velocidade escolhida (minutos de jogo por
   segundo). No 1x, 1 min de jogo = 1 min de relogio, mesmo com a aba em segundo plano. Salto maximo de 1 h real
   por passo, para nao travar depois de um sono do PC. O bebe anda minuto a minuto para parar no instante em que
   um chamado abre; com chamado aberto o tempo cai para 1x ate atender (e volta depois). Durante a luta no palco e com o Resultado
   dela aberto o tempo nao anda (luta.lutaSeguraTempo): o que passou ali e descartado, como na Pausa. */
import { useEffect, useState } from "react";
import { jogoAtual, mudarMotor } from "./jogo.ts";
import { lutaSeguraTempo } from "./luta.ts";

export const VEL_1X = 1 / 60;
export const VELOCIDADES: readonly [string, number, string?][] = [
  ["Pausa", 0], ["1x", VEL_1X, "tempo real: 1 minuto do pet = 1 minuto do relógio"], ["10 min/s", 10], ["1 h/s", 60], ["6 h/s", 360],
];
let velocidade = 10, velAntesChamado: number | null = null, acumulado = 0;
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };

export const velocidadeAtual = (): number => velocidade;
/** o tempo esta em 1x por causa de um chamado aberto */
export const freadoPorChamado = (): boolean => velAntesChamado !== null;

/** velocidade escolhida pelo jogador: nao devolve a de antes do chamado */
export function escolherVelocidade(v: number): void { velAntesChamado = null; velocidade = v; avisar(); }

/** chamado do bebe aberto: 1x ate atender ou a janela fechar; sem chamado, volta a velocidade de antes.
    Devolve true se acabou de frear. */
export function ajustarVelocidadeChamado(): boolean {
  const aberto = jogoAtual().motor.chamadosAbertos().length > 0;
  if (aberto && velocidade > VEL_1X && velAntesChamado === null) { velAntesChamado = velocidade; velocidade = VEL_1X; avisar(); return true; }
  if (!aberto && velAntesChamado !== null) { velocidade = velAntesChamado; velAntesChamado = null; avisar(); }
  return false;
}
/** +1 h (ferramenta de teste) */
export function pularUmaHora(): void { mudarMotor(m => m.avancar(60)); ajustarVelocidadeChamado(); }

/** laco do tempo: um passo a cada 100 ms; devolve a funcao que para */
export function iniciarTempo(): () => void {
  let ultimo = performance.now();
  const t = setInterval(() => {
    const agora = performance.now(), dt = Math.min(3600, (agora - ultimo) / 1000);
    ultimo = agora;
    const j = jogoAtual();
    if (j.nascendo > 0 || velocidade === 0 || j.erroSave || lutaSeguraTempo()) return;
    acumulado += velocidade * dt;
    let n = Math.floor(acumulado);
    if (n <= 0) return;
    acumulado -= n;
    mudarMotor(m => {
      if (m.estagioAtual === "bebe") {
        /* bebe: minuto a minuto, para parar no instante em que um chamado abre */
        while (n-- > 0) { m.avancar(1); if (m.chamadosAbertos().length && velocidade > VEL_1X && velAntesChamado === null) { acumulado = 0; break; } }
      } else m.avancar(n);
    }, "adiado");
    ajustarVelocidadeChamado();
  }, 100);
  return () => clearInterval(t);
}
export function useTempo(): { velocidade: number; freado: boolean } {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return { velocidade, freado: velAntesChamado !== null };
}
