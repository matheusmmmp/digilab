/* O tempo de tela de uma serie de lutas ja jogadas (a D-R3-6 da rodada 3; docs/PLANO_EQUILIBRIO_COMBATE_TR_R3.md, secao 6): o que o palco
   da luta (src/luta.ts, animar) leva para mostrar a serie na velocidade de sempre (sem x2 e sem o movimento reduzido), sem navegador.
   Refaz cada luta da entrada guardada no resultado, com os eventos, e passa os eventos pelas funcoes puras da vista:
   - aplicarEventosTR e consumirPausa (efeitosTR.ts): a pausa do acerto (E1), que atrasa o proximo quadro;
   - passosDoQuadro (nocauteTR.ts): a camera lenta do nocaute (E5), menos passos por quadro no fim de uma luta que acaba em nocaute;
   - a espera do fim (PAUSA_FIM, ou PAUSA_FIM_KO no nocaute) e entre as lutas da serie (PAUSA_SERIE), em quadros inteiros de QUADRO_MS.
   Os numeros do palco sao lidos do proprio src/luta.ts (que tem DOM e nao se importa no Node): se o texto mudar, isto falha alto, nao
   fica com um numero velho. Os numeros da vista sao PROPOSTOS, SEM FONTE (a D-R3-9): a coluna e uma estimativa com os de hoje. */
import { readFileSync } from "node:fs";
import { criarLutaTR, passoTR, type ResultadoLuta } from "../../motor/index.ts";
import { aplicarEventosTR, consumirPausa, visualNovoTR } from "../../src/telas/lutar/palcoTR/efeitosTR.ts";
import { passosDoQuadro } from "../../src/telas/lutar/palcoTR/nocauteTR.ts";

const FONTE = readFileSync(new URL("../../src/luta.ts", import.meta.url), "utf8");
const numeroDoPalco = (nome: string): number => {
  const m = FONTE.match(new RegExp(`\\b${nome} = (\\d+)\\b`));
  if (!m) throw new Error(`src/luta.ts sem ${nome}: o tempo de tela da bancada precisa ser revisto`);
  return Number(m[1]);
};
/** os numeros do palco (src/luta.ts): o quadro (ms), os passos por quadro e as esperas (ms) */
export const PALCO = {
  quadroMs: numeroDoPalco("QUADRO_MS"), passosQuadro: numeroDoPalco("PASSOS_QUADRO"),
  pausaFim: numeroDoPalco("PAUSA_FIM"), pausaFimKo: numeroDoPalco("PAUSA_FIM_KO"), pausaSerie: numeroDoPalco("PAUSA_SERIE"),
} as const;

/** a espera do palco: quadros inteiros de QUADRO_MS (a funcao esperar de src/luta.ts) */
const espera = (ms: number): number => Math.ceil(ms / PALCO.quadroMs) * PALCO.quadroMs;

/** o tempo de tela da serie (ms), do primeiro quadro ao fim da espera da ultima luta. Falha alto se a luta refeita nao acabar como a do motor */
export function telaDaSerie(serie: readonly ResultadoLuta[]): number {
  let ms = 0;
  serie.forEach((r, j) => {
    const res = r.tr;
    if (!res) throw new Error("luta sem o tempo real: o tempo de tela so conta as lutas TR");
    const en = res.entrada, desafiado = en.o.desafiado ?? null;
    const sim = criarLutaTR(en.A, en.B, en.semente, { ...en.o, eventos: true }), v = visualNovoTR();
    let lidos = 0, fim: ReturnType<typeof passoTR> = null;
    /* o primeiro quadro sai QUADRO_MS depois de abrir a luta (agendar() sem pausa) */
    ms += PALCO.quadroMs;
    for (;;) {
      const n = passosDoQuadro(sim.S.passo, PALCO.passosQuadro, res, false);
      for (let q = 0; q < n && !fim; q++) {
        fim = passoTR(sim, desafiado);
        const ev = sim.eventos!.slice(lidos);
        lidos = sim.eventos!.length;
        aplicarEventosTR(v, sim, ev);
      }
      if (fim) break;
      /* o proximo quadro: QUADRO_MS mais a pausa pedida pelos acertos deste */
      ms += PALCO.quadroMs + consumirPausa(v, false);
    }
    if (sim.S.passo !== res.passos || fim[0] !== res.pontosA || fim[1] !== res.fim)
      throw new Error(`a luta refeita nao bate com a do motor: passo ${sim.S.passo} x ${res.passos}`);
    ms += espera(j < serie.length - 1 ? PALCO.pausaSerie : res.fim === "ko" ? PALCO.pausaFimKo : PALCO.pausaFim);
  });
  return ms;
}
