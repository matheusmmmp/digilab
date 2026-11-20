/* O cérebro de teste do WORLD-POC-01a: um decisor de regras que prova o contrato (docs/futuro/mundo_3d.md, seção 4). NÃO é o cérebro A
   e não aprende nada. Lê só a Observação, devolve só a Intenção e importa só os tipos do contrato (a G-CONTRATO confere pelo fonte):
     - com fome e comida à vista: consumir a mais perto;
     - com tédio e a bola à vista: empurrar a bola;
     - com fome ou tédio e nada à vista: aproximar-se de um setor livre sorteado pela rng da política (explorar);
     - senão: descansar. */
import { ESCALA_RECEPTOR, type Cerebro, type Intencao, type Observacao, type RngPolitica } from "./tipos.ts";

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

/* O cérebro de teste do POC-02 (docs/TAREFA_V2_WORLD_POC_02.md): as mesmas regras, sobre os receptores do corpo químico. A falta é
   S - leitura na fome e na energia (os drives de hoje) e a própria leitura no tédio (um drive novo). Os limiares são PROPOSTOS, sem fonte:
     - exausto (a falta de energia alta): descansar, que é dormir (CP-2);
     - com fome e comida à vista: consumir; com tédio e a bola à vista: empurrar;
     - com fome ou tédio e nada à vista: aproximar-se de um setor livre sorteado (explorar);
     - senão: descansar. */
const S = ESCALA_RECEPTOR;
export const LIMIARES_CORPO = { exausto: 700, fome: 350, tedio: 300 } as const;

export const cerebroDeTesteCorpo: Cerebro = {
  decidir(obs: Observacao, rng: RngPolitica): Intencao {
    const r = obs.corpo;
    for (const k of ["fome", "energia", "tedio"]) if (!Number.isInteger(r[k])) throw new Error(`a Observacao sem o receptor ${k}`);
    const fome = S - r.fome, energia = S - r.energia, tedio = r.tedio;
    if (energia >= LIMIARES_CORPO.exausto) return { tipo: "descansar" };
    const comida = obs.vistos.find(v => v.categoria === "comida");
    const bola = obs.vistos.find(v => v.categoria === "bola");
    if (fome >= LIMIARES_CORPO.fome && comida) return { tipo: "consumir", ref: comida.ref };
    if (tedio >= LIMIARES_CORPO.tedio && bola) return { tipo: "empurrar", ref: bola.ref };
    if (fome >= LIMIARES_CORPO.fome || tedio >= LIMIARES_CORPO.tedio) {
      const livres = obs.obstaculos.map((d, k) => [d, 2 * k] as const).filter(([d]) => d >= LIVRE_MINIMO).map(([, s]) => s);
      if (livres.length) return { tipo: "aproximar", setor: livres[rng.inteiro(livres.length)] };
    }
    return { tipo: "descansar" };
  },
};
