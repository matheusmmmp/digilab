/* O genoma da visao (GOSTO_VISUAL; o espelho de digilab/genoma_visao.py, P1d do Python, porte da P1f): por canal da tela, o ponto otimo
   uniforme em [0, C] e a largura do pico uniforme em [largura_min, largura_max], sorteados pela rng propria `visao-ovo` (derivada da semente do
   ovo; canal a canal, o otimo e depois a largura). Fixo na vida. O genoma vazio (o otimo no meio, a largura do meio) e o controle. */
import { RandomPy, derivarSemente } from "../mundo.ts";
import { CANAIS_TELA } from "../tv.ts";
import { divArred } from "./_comum.ts";
import { CONFIG_OLHAR, type ConfigOlhar } from "./constantes.ts";

export const FLUXO_VISAO = "visao-ovo";
export interface GenomaVisao { readonly otimo: Readonly<Record<string, number>>; readonly largura: Readonly<Record<string, number>> }

export function conferirGenomaVisao(g: GenomaVisao): GenomaVisao {
  for (const [nome, d] of [["otimo", g.otimo], ["largura", g.largura]] as const) {
    if (Object.keys(d).join() !== CANAIS_TELA.join() || Object.values(d).some(v => !Number.isInteger(v))) {
      throw new Error(`o genoma da visao tem ${nome} por canal, na ordem ${CANAIS_TELA}: ${JSON.stringify(d)}`);
    }
  }
  if (Object.values(g.otimo).some(v => v < 0) || Object.values(g.largura).some(v => v <= 0)) throw new Error("o genoma da visao: otimo >= 0 e largura > 0");
  return g;
}

/** (o otimo, a largura) na escala S do cerebro: div_arred(v S, C); a largura no minimo 1 */
export function genomaNaEscala(g: GenomaVisao, S: number, C: number): [Record<string, number>, Record<string, number>] {
  if ([...Object.values(g.otimo), ...Object.values(g.largura)].some(v => v > C)) throw new Error(`o genoma da visao passa da escala C = ${C}`);
  return [Object.fromEntries(CANAIS_TELA.map(c => [c, divArred(g.otimo[c]! * S, C)])),
          Object.fromEntries(CANAIS_TELA.map(c => [c, Math.max(1, divArred(g.largura[c]! * S, C))]))];
}

export function genomaVisao(semente: number, co: ConfigOlhar = CONFIG_OLHAR): GenomaVisao {
  if (!Number.isSafeInteger(semente)) throw new Error(`a semente do ovo e inteira: ${semente}`);
  const rng = new RandomPy(derivarSemente(FLUXO_VISAO, semente));
  const otimo: Record<string, number> = {}, largura: Record<string, number> = {};
  for (const c of CANAIS_TELA) {
    otimo[c] = rng.randint(0, co.escala);
    largura[c] = rng.randint(co.largura_min, co.largura_max);
  }
  return conferirGenomaVisao({ otimo, largura });
}

export function genomaVisaoVazio(co: ConfigOlhar = CONFIG_OLHAR): GenomaVisao {
  return { otimo: Object.fromEntries(CANAIS_TELA.map(c => [c, Math.floor(co.escala / 2)])),
           largura: Object.fromEntries(CANAIS_TELA.map(c => [c, Math.floor((co.largura_min + co.largura_max) / 2)])) };
}
