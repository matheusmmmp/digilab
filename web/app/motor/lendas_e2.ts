/* MITOLOGIA, E2 (docs/TAREFA_V3_MITOLOGIA.md, secao 12): Piedmon e a montanha. O Piedmon encarna o deus da Diversao (D-MM-4), o do macaco;
   vence-lo depois de ter conhecido a hybris fecha a lenda: "o macaco saiu da montanha". Funcao pura do pet refeito do log (o forcaLutas); nada
   muda o motor, a luta ou o cerebro. As falas sao por modelo, sem LLM, sem nomear a obra (o criterio F0). */
import { NPC } from "./bots.ts";
import { hybrisDe, type FontesLenda } from "./lendas.ts";

/** os dois Piedmon da Campanha (o da Cidadela e o da Montanha Espiral), pelo nome */
export const ehPiedmon = (rival: string): boolean => NPC[rival]?.nome === "Piedmon";

export interface Montanha {
  /** a primeira derrota para o Piedmon */
  derrota: number | null;
  /** a primeira vitoria sobre o Piedmon com uma hybris antes: a lenda se fecha */
  fechada: number | null;
  /** a primeira vitoria sobre o Piedmon sem nenhuma hybris antes (a lenda nao se fecha por ela) */
  semQueda: number | null;
}

export function montanhaDe(f: FontesLenda): Montanha {
  const quedas = hybrisDe(f.forcaLutas).map(h => h.tick);
  const out: Montanha = { derrota: null, fechada: null, semQueda: null };
  for (const l of f.forcaLutas) {
    if (!ehPiedmon(l.rival)) continue;
    if (l.resultado === "derrota" && out.derrota === null) out.derrota = l.tick;
    if (l.resultado !== "vitoria") continue;
    if (quedas.some(t => t < l.tick)) { if (out.fechada === null) out.fechada = l.tick; }
    else if (out.semQueda === null) out.semQueda = l.tick;
  }
  return out;
}

export const FALA_PIEDMON_ANTES = "Esse aí ri de tudo, até de quem o vence. Se perderem, riam junto: é o deus dele que está olhando.";
export const FALA_PIEDMON_DERROTA = "Ele riu, não foi? O macaco também ria, debaixo da montanha. O riso não prende ninguém; prende não " +
  "aprender nada com a queda.";
export const FALA_MONTANHA_FECHADA = "Vocês caíram antes e voltaram. Foi assim que o macaco saiu da montanha: não mais forte, mais inteiro. " +
  "O aro dele ficou na pedra; agora é de vocês.";
export const FALA_VITORIA_SEM_QUEDA = "Venceram o palhaço sem nunca terem caído. Bonito. Mas a lenda só se fecha para quem conheceu a " +
  "montanha por dentro.";
