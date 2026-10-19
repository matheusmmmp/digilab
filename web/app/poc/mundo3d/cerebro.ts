/* O cérebro de teste do WORLD-POC-01a: um decisor de regras que prova o contrato (docs/futuro/mundo_3d.md, seção 4). NÃO é o cérebro A
   e não aprende nada. Lê só a Observação, devolve só a Intenção e importa só os tipos do contrato (a G-CONTRATO confere pelo fonte):
     - com fome e comida à vista: consumir a mais perto;
     - com tédio e a bola à vista: empurrar a bola;
     - com fome ou tédio e nada à vista: aproximar-se de um setor livre sorteado pela rng da política (explorar);
     - senão: descansar. */
import type { Cerebro, Intencao, Observacao, RngPolitica } from "./tipos.ts";

const LIMIAR_FOME = 500, LIMIAR_TEDIO = 400, LIVRE_MINIMO = 16;

export const cerebroDeTeste: Cerebro = {
  decidir(obs: Observacao, rng: RngPolitica): Intencao {
    const { fome, tedio } = obs.corpo;
    const comida = obs.vistos.find(v => v.categoria === "comida");
    const bola = obs.vistos.find(v => v.categoria === "bola");
    if (fome >= LIMIAR_FOME && comida) return { tipo: "consumir", ref: comida.ref };
    if (tedio >= LIMIAR_TEDIO && bola) return { tipo: "empurrar", ref: bola.ref };
    if (fome >= LIMIAR_FOME || tedio >= LIMIAR_TEDIO) {
      const livres = obs.obstaculos.map((d, k) => [d, 2 * k] as const).filter(([d]) => d >= LIVRE_MINIMO).map(([, s]) => s);
      if (livres.length) return { tipo: "aproximar", setor: livres[rng.inteiro(livres.length)] };
    }
    return { tipo: "descansar" };
  },
};
