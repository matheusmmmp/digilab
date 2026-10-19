/* O corpo do WORLD-POC-02 (docs/TAREFA_V2_WORLD_POC_02.md): o Corpo do jogo (web/app/motor/corpo.ts), como ele está, com a CCO_V11
   (fome, digestão, Vida, drives novos, gestos e metabolismo). É o único ponto do POC que importa o motor (CP-6): o corpo.ts e o que ele
   importa (a G-FRONTEIRA confere). O cérebro de teste não o importa; ele só vê os receptores na Observação.

   As consequências do mundo do POC viram os estímulos que o corpo já tem, e cada chamada fica gravada (`ChamadaCorpo`), para a
   G-CORPO-IGUAL refazer o mesmo corpo num Corpo solto:
     passo      um tick, no estado do começo dele (dormindo no `descansar`, CP-2; sujeira 0, CP-4)
     consumo    comer a comida do mundo: estimuloConsumoMundo("racao", "madura")
     bola       o primeiro empurrão de uma decisão (CP-5): estimuloBola(ganho_humor_bola) e atividade("bola")
     andar      o fim da decisão: estimuloAndar(o caminho andado, custo_energia_por_subunidade)
   O contato não chama o corpo (CP-1). Nenhum químico, emissor ou estímulo novo. */
import { CCO_V11, CMU } from "../../motor/constantes.ts";
import { Corpo, configCorpo } from "../../motor/corpo.ts";

/** o estado do nascimento do pet do POC (os drives de hoje), PROPOSTO e sem fonte */
export const ESTADO_INICIAL_POC = { tick: 0, fome: 0.75, higiene: 1, energia: 0.9, humor: 0.7, saude: 1 } as const;

/** os drives da consequência no registro: os do N3 (fome, higiene, energia) e os novos que o corpo do v11 tem, como o `drivesCorpo`
 *  do lobos.ts (o canal do humor só vale com a fruta) */
export const DRIVES_CONSEQUENCIA = ["fome", "higiene", "energia", "tedio", "solidao", "estresse", "dor"] as const;
const RECEPTORES_HOJE = ["fome", "higiene", "energia", "humor", "saude"];

export type ChamadaCorpo =
  | { t: "passo"; tick: number; dormindo: boolean; sujeira: number }
  | { t: "consumo" }
  | { t: "bola" }
  | { t: "andar"; deslocamento: number };

export function criarCorpoPoc(): Corpo {
  return Corpo.deEstado({ ...ESTADO_INICIAL_POC }, { cc: configCorpo(CCO_V11) });
}

/** aplica uma chamada ao corpo (a mesma conta no POC e num Corpo solto) */
export function aplicar(c: Corpo, ch: ChamadaCorpo): void {
  switch (ch.t) {
    case "passo": c.passo({ tick: ch.tick, dormindo: ch.dormindo, sujeira: ch.sujeira }); return;
    case "consumo": c.estimuloConsumoMundo("racao", "madura", CMU); return;
    case "bola": c.estimuloBola(CMU.ganho_humor_bola); c.atividade("bola"); return;
    case "andar": c.estimuloAndar(ch.deslocamento, CMU.custo_energia_por_subunidade); return;
    default: throw new Error(`chamada desconhecida ao corpo: ${JSON.stringify(ch)}`);
  }
}

/** a falta de um drive pelo receptor, na escala S: S - leitura nos drives de hoje, a própria leitura nos novos */
export function falta(receptores: Readonly<Record<string, number>>, nome: string, S: number): number {
  const v = receptores[nome];
  if (!Number.isInteger(v)) throw new Error(`receptor ${nome} ausente ou fora dos inteiros: ${v}`);
  return RECEPTORES_HOJE.includes(nome) ? S - v : v;
}

/** a consequência fisiológica de uma decisão: falta(antes)^2 - falta(depois)^2 por drive (positiva = a falta diminuiu), a conta do
 *  contribuicoesCorpo do lobos.ts com todos os pesos 1 (o teste confere contra ele) */
export function consequencia(antes: Readonly<Record<string, number>>, depois: Readonly<Record<string, number>>, S: number): Record<string, number> {
  const c: Record<string, number> = {};
  for (const d of DRIVES_CONSEQUENCIA) {
    const fa = falta(antes, d, S), fd = falta(depois, d, S);
    c[d] = fa * fa - fd * fd;
  }
  return c;
}
