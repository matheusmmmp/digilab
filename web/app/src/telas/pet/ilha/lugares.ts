/* Os lugares da ilha (L3 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md, "Lugares da ilha: menus (L2/L3)"): o saco de pancada (Crescer), o
   portao da arena (Lutar) e a barraca do Tamer (Diario). Cada lugar tem o nome, o ponto na cena, o giro, a altura alvo, o estado (aberto ou trancado)
   e o caminho do modelo 3D. So vista: o motor nao sabe deles, e nada daqui entra no registro, no save nem no replay. Sem three e sem DOM (o teste le
   este modulo sozinho); o marcador provisorio mora em marcadoresLugar.ts.
   - o ponto e o centro da base, em celulas do mundo (x leste, z sul), calculado do layout do motor: o saco a [3, -4] do ninho (como desde a L2); o
     portao no fim do caminho de terra da casa, a direita (a leste), atravessado na trilha; a barraca a esquerda (a oeste), encostada no barranco;
   - o giro e a rotacao em y, em radianos, com a frente do modelo em +z do glTF (a camera olha do sul, entao giro 0 mostra a frente);
   - o modelo e o caminho do glTF dentro de public/ ("lugares/<portao|barraca>/<nome>.gltf", 1 no e 1 material so de cor; o ITENS_3D os entrega). Hoje
     vazio (null): a vista desenha o marcador provisorio. A troca sera so apontar o caminho aqui e carregar com o carregarVariante de cena.ts (numa
     tabela a moda do ENFEITES_MODELOS); a escala vem da `altura` alvo (o modelo e redimensionado ate ela), com o pivo no centro da base;
   - o glTF vem com Y para cima, o pe em y=0 e a frente (+z) voltada para a area andavel; o giro e nosso (campo `giro`). A mascara de luz (`luz`) e o
     cadeado (`cadeado`) tambem ficam aqui, vazios hoje;
   - quando o glTF entrar, o marcador provisorio (marcadoresLugar.ts) fica ate o modelo carregar, e a falha do glTF deve ser ALTA (erro visivel, como a
     dos kits em vista.ts), nunca um lugar vazio em silencio; a carga ainda nao esta implementada;
   - o estado e "aberto" para todos na L3. A tarefa dos niveis o troca por "trancado"; a vista entao apaga o modelo e poe o cadeado.
   Todos os numeros sao do desenho: PROPOSTO, SEM FONTE (numero de interface, nao de jogo). */
import { SACO_DESDE_NINHO } from "./constantes.ts";

export type IdLugar = "saco" | "portao" | "barraca";
export type EstadoLugar = "aberto" | "trancado";
export type Ponto = readonly [number, number];

/** o que o ponto de cada lugar pede do layout do motor (celulas continuas, o centro da celula) */
export interface BaseDoMundo { ninho: Ponto; comedouro: Ponto; area: { w: number; h: number } }

export interface LugarIlha {
  id: IdLugar;
  /** o nome a vista (a placa do lugar) */
  nome: string;
  /** o menu do jogo que o lugar abre (a rota) */
  destino: "crescer" | "lutar" | "diario";
  /** o ponto do centro da base, a partir do layout */
  ponto: (b: BaseDoMundo) => Ponto;
  /** a rotacao em y (rad), com a frente do modelo em +z */
  giro: number;
  /** a altura alvo do modelo, em celulas (o do saco e o desenho procedural de itens.ts) */
  altura: number;
  /** o raio da base (a meia-profundidade a frente do centro, em celulas): o pet fica alem dele, do lado da camera (`pontoDoPet`) */
  raio: number;
  estado: EstadoLugar;
  /** o caminho do glTF em public/ ("lugares/<portao|barraca>/<nome>.gltf"), ou null enquanto o modelo nao chegou */
  modelo: string | null;
  /** a mascara emissiva opcional do modelo ("lugares/portao/<nome>_luz.png"; apagada quando trancado), ou null */
  luz: string | null;
  /** a peca separada do cadeado ("lugares/cadeado/<nome>.gltf"), mostrada so quando trancado, ou null. Sem logica de trava na L3 */
  cadeado: string | null;
}

/** o portao: a quantas celulas do comedouro, no fim do caminho de terra da casa (a grade pinta o caminho ate ~5 celulas depois do comedouro) */
export const PORTAO_DESDE_COMEDOURO: Ponto = [5, 1.5];
/** a barraca: a quantas celulas do ninho (a oeste dele, rente ao barranco da borda oeste, um pouco ao sul) */
export const BARRACA_DESDE_NINHO: Ponto = [-2.7, 1];
/** a barraca nunca fica mais perto da borda oeste que isto (celulas) */
const FOLGA_BORDA = 1.2;

export const LUGARES: Readonly<Record<IdLugar, LugarIlha>> = {
  saco: {
    id: "saco", nome: "Saco de pancada", destino: "crescer", giro: 0, altura: 2.5, raio: 0.5, estado: "aberto", modelo: null, luz: null, cadeado: null,
    ponto: b => [b.ninho[0] + SACO_DESDE_NINHO[0], b.ninho[1] + SACO_DESDE_NINHO[1]],
  },
  portao: {
    id: "portao", nome: "Portão da arena", destino: "lutar", giro: -Math.PI / 4, altura: 5, raio: 0.5, estado: "aberto", modelo: null, luz: null, cadeado: null,
    ponto: b => [Math.min(b.area.w - 2, b.comedouro[0] + PORTAO_DESDE_COMEDOURO[0]), Math.min(b.area.h - 2, b.comedouro[1] + PORTAO_DESDE_COMEDOURO[1])],
  },
  barraca: {
    id: "barraca", nome: "Barraca do Tamer", destino: "diario", giro: 0.35, altura: 4, raio: 2.4, estado: "aberto", modelo: null, luz: null, cadeado: null,
    ponto: b => [Math.max(FOLGA_BORDA, b.ninho[0] + BARRACA_DESDE_NINHO[0]), Math.min(b.area.h - 2, b.ninho[1] + BARRACA_DESDE_NINHO[1])],
  },
};
export const ORDEM_LUGARES: readonly IdLugar[] = ["saco", "portao", "barraca"];

/** o ponto do lugar no mundo de `base` */
export const pontoDoLugar = (id: IdLugar, base: BaseDoMundo): Ponto => LUGARES[id].ponto(base);
/** o lugar que cada menu abre (Pet, Conversar e Ajustes nao tem lugar) */
export function lugarDoDestino(destino: string): IdLugar | null {
  return ORDEM_LUGARES.find(i => LUGARES[i].destino === destino) ?? null;
}

/** a margem entre a base do lugar e o pet (celulas) e o quanto o pet fica a esquerda do centro na tela. PROPOSTO, SEM FONTE (numero de interface) */
export const PET_MARGEM = 0.8, PET_LADO = 1.0;
/** onde o pet fica num lugar grande (o portao, a barraca): na frente dele, do lado da camera, a `raio` + PET_MARGEM do centro, e a PET_LADO a esquerda
    (na tela), nunca dentro. `frente` e a direcao em que a camera olha no chao e `direita` a direita dela (unitarios). O saco tem a conta propria, da L2 */
export function pontoDoPet(ponto: Ponto, raio: number, frente: Ponto, direita: Ponto): [number, number] {
  const f = raio + PET_MARGEM;
  return [ponto[0] - frente[0] * f - direita[0] * PET_LADO, ponto[1] - frente[1] * f - direita[1] * PET_LADO];
}
