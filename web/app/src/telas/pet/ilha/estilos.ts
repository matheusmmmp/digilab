/* Os estilos do habitat (src/habitat.ts, caminho A de 2026-10-31): cada mapa e uma vista da MESMA grade do motor (grade.ts), so com outro
   terreno, outros modelos e outra dobra. A area andavel, a moldura, os objetos e o lugar do pet nao mudam; a vista (vista.ts) e a mesma.
     - ilha: a da L4 (cena.ts), com o mundo curvo (DOBRA_K) e os kits CC0 de public/kits3d;
     - voxel: a ilha em cubos (voxel.ts), sem asset;
     - floresta: o kit Tiny Fantasy Forest (floresta.ts), so no dev;
     - cassette: as texturas e as arvores do Cassette Beasts (cassette.ts), so no dev.
   Os tres novos sao planos, como os POCs do #480 (a dobra e do estilo Animal Crossing). */
import type { Mapa } from "../../../habitat.ts";
import { montarCena, objetos, terreno, type CenaIlha, type Objetos } from "./cena.ts";
import { arquivosCassette, carregadorCassette, terrenoCassette } from "./cassette.ts";
import { DOBRA_K } from "./constantes.ts";
import { PALETA_FLORESTA, arquivosFloresta, carregadorFloresta } from "./floresta.ts";
import type { Ilha } from "./grade.ts";
import { objetosVoxel, terrenoVoxel } from "./voxel.ts";

export interface Estilo {
  readonly id: Mapa;
  /** a dobra do mundo curvo, por celula (0: plano) */
  readonly dobra: number;
  /** a cena estatica: o ceu, as luzes, o terreno e a agua */
  montar(ilha: Ilha): CenaIlha;
  /** os objetos da grade (podem baixar arquivos; falham alto se faltar um) */
  objetos(ilha: Ilha): Promise<Objetos>;
}

/** o estilo de um mapa; `base` e a URL da pagina (document.baseURI), de onde saem os caminhos dos kits */
export function estiloDe(mapa: Mapa, base: string): Estilo {
  switch (mapa) {
    case "ilha": return { id: mapa, dobra: DOBRA_K, montar: i => montarCena(i), objetos: i => objetos(i, base) };
    case "voxel": return { id: mapa, dobra: 0, montar: i => montarCena(i, terrenoVoxel(i)), objetos: async i => objetosVoxel(i) };
    case "floresta": return {
      id: mapa, dobra: 0, montar: i => montarCena(i, terreno(i, PALETA_FLORESTA)),
      objetos: async i => objetos(i, base, await carregadorFloresta(base), arquivosFloresta),
    };
    case "cassette": return {
      id: mapa, dobra: 0, montar: i => montarCena(i, terrenoCassette(i, base)),
      objetos: async i => objetos(i, base, await carregadorCassette(base), arquivosCassette, false),
    };
  }
}
