/* Os lugares da ilha: a tabela da experiencia (L3 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md, "Lugares da ilha: menus (L2/L3)") e os
   modelos 3D na cena (docs/TAREFA_V3_LUGARES_3D.md, secao 12; P-11 de docs/PLANO_V3_PROGRESSAO_TUTORIAL.md). So vista: o motor nao sabe deles, e nada
   daqui entra no registro, no save nem no replay. Os numeros sao do desenho: PROPOSTO, SEM FONTE (numero de interface, nao de jogo).

   A TABELA (LUGARES, da frente UX_TELA_PET): o saco de pancada (Crescer), o portao da arena (Lutar) e a barraca do Tamer (Diario). Cada lugar tem o nome,
   o destino, o ponto na cena, a altura alvo, o raio da base, o estado e o caminho do modelo 3D.
   - o ponto e o centro da base, em celulas do mundo (x leste, z sul): o saco perto da praca, no ponto da planta A (PLANTA_ILHA; ate a planta, a
     [3, -4] do ninho, desde a L2); o portao e a barraca onde a grade os
     poe (grade.ts, porLugares, PLANTA_ILHA: o portao ao norte, a barraca a leste da praca, em grama plana, com a clareira), que chegam em `BaseDoMundo.grade`. Na mescla
     da UX_TELA_PET com a LUGARES_3D (2026-11-07) os pontos provisorios da L3 (o portao a leste do comedouro, a barraca a oeste do ninho) e o giro
     deles sairam: a posicao, o giro e o estilo sao os da LUGARES_3D;
   - o modelo e a luz vem de LUGARES_MODELOS e LUGARES_LUZ (modelos.ts), a mesma tabela que a cena carrega abaixo; a altura alvo e a do modelo;
   - enquanto o modelo nao carrega (e nos estilos sem lugares, como o Voxel), a vista desenha o marcador provisorio (marcadoresLugar.ts) no mesmo ponto;
     a falha do glTF e ALTA (a ilha cai na reserva, como sem os kits);
   - o estado vem do nivel do Tamer (nivel.ts, via trancas.ts): `estado` abaixo e o de partida ("aberto") e `estadoDoLugar` o de agora; trancado, a
     vista apaga o lugar (o modelo ou o marcador: marcadoresLugar.ts, Apagador; o saco em itens.ts), apaga a luz dele (`abrir`) e a tela poe o cadeado
     com o "Nv N" (CadeadosDaIlha.tsx).
   Sem three e sem DOM (o teste le este modulo sozinho). A CENA (`lugares`, da frente LUGARES_3D) mora em lugaresCena.ts: cada modelo de LUGARES_MODELOS (public/lugares/<nome>/) entra pelo carregarVariante, como os enfeites
   (enfeites.ts), com a sombra redonda quando o modelo tem. Aberto e trancado sao o mesmo modelo: aberto, as partes da mascara (LUGARES_LUZ, o
   emissiveMap) acendem na cor do lugar; trancado, apagam. O cais (o multiplayer e futuro) fica trancado por LUGAR_ABERTO (lugaresIlha.ts) e sem menu. */
import { PLANTA_ILHA, TREINO_MS, TREINO_VEL } from "./constantes.ts";
import { LUGARES_LUZ, LUGARES_MODELOS, type NomeLugar } from "./modelos.ts";
import { lugarTrancado } from "../../../trancas.ts";

export type IdLugar = "saco" | "portao" | "barraca";
export type EstadoLugar = "aberto" | "trancado";
export type Ponto = readonly [number, number];

/** onde a grade poe um lugar grande (grade.ts, Lugar): o centro da base (celulas), o giro (a frente, +z do glTF, para a area andavel) e a altura do
    chao ali (celulas; a area andavel e o 0) */
export interface PosicaoNaGrade { x: number; z: number; giro: number; y: number }
/** o que o ponto de cada lugar pede do layout do motor (celulas continuas, o centro da celula) e, para o portao e a barraca, da grade da ilha
    (Ilha.lugares; o saco nao precisa dela) */
export interface BaseDoMundo {
  ninho: Ponto; comedouro: Ponto; area: { w: number; h: number }; grade?: Partial<Record<"portao" | "barraca", PosicaoNaGrade>>;
  /** o ponto do saco na planta que vale nesta ilha (Ilha.planta.lugares.saco: a A, a da ilha com agua ou a da ilha grande). Sem ele, o da
      planta A. Quem monta a base de uma ilha de verdade o passa sempre: o ponto da planta A cai na agua da ilha grande (2026-11-11) */
  saco?: Ponto;
}
/** a posicao do portao e da barraca na grade da ilha (Ilha.lugares), para a BaseDoMundo; falha alto se faltar um */
export function gradeDosLugares(ilha: { readonly lugares: readonly { nome: NomeLugar; x: number; z: number; giro: number; y: number }[] }): Record<"portao" | "barraca", PosicaoNaGrade> {
  const achar = (n: "portao" | "barraca"): PosicaoNaGrade => {
    const l = ilha.lugares.find(g => g.nome === n);
    if (!l) throw new Error(`a grade da ilha nao tem o lugar ${n}`);
    return { x: l.x, z: l.z, giro: l.giro, y: l.y };
  };
  return { portao: achar("portao"), barraca: achar("barraca") };
}
/** o ponto de um lugar grande na grade; falha alto sem ela */
function daGrade(b: BaseDoMundo, id: "portao" | "barraca"): Ponto {
  const g = b.grade?.[id];
  if (!g) throw new Error(`o ponto do lugar ${id} vem da grade da ilha (BaseDoMundo.grade), que nao veio`);
  return [g.x, g.z];
}

export interface LugarIlha {
  id: IdLugar;
  /** o nome a vista (a placa do lugar) */
  nome: string;
  /** o menu do jogo que o lugar abre (a rota) */
  destino: "crescer" | "lutar" | "diario";
  /** o ponto do centro da base, a partir do layout */
  ponto: (b: BaseDoMundo) => Ponto;
  /** a altura alvo do modelo, em celulas (o do saco e o desenho procedural de itens.ts) */
  altura: number;
  /** o raio da base (a meia-profundidade a frente do centro, em celulas): o pet fica alem dele, do lado da camera (`pontoDoPet`) */
  raio: number;
  estado: EstadoLugar;
  /** o caminho do glTF em public/ ("lugares/<portao|barraca>/<nome>.gltf", de LUGARES_MODELOS), ou null (o saco: o desenho dele e o de itens.ts) */
  modelo: string | null;
  /** a mascara emissiva opcional do modelo ("lugares/portao/<nome>_luz.png"; apagada quando trancado), ou null */
  luz: string | null;
  /** a peca separada do cadeado ("lugares/cadeado/<nome>.gltf"), mostrada so quando trancado, ou null. Sem logica de trava na L3 */
  cadeado: string | null;
}

const arquivo = (n: NomeLugar): string => "lugares/" + LUGARES_MODELOS[n].arquivos[0];
const luzDe = (n: NomeLugar): string | null => (LUGARES_LUZ[n] ? "lugares/" + LUGARES_LUZ[n] : null);

export const LUGARES: Readonly<Record<IdLugar, LugarIlha>> = {
  saco: {
    id: "saco", nome: "Saco de pancada", destino: "crescer", altura: 2.5, raio: 0.5, estado: "aberto", modelo: null, luz: null, cadeado: null,
    ponto: b => { const p = b.saco ?? PLANTA_ILHA.lugares.saco; return [p[0], p[1]]; },
  },
  portao: {
    id: "portao", nome: "Portão da arena", destino: "lutar", altura: LUGARES_MODELOS.portao.altura, raio: 0.5, estado: "aberto",
    modelo: arquivo("portao"), luz: luzDe("portao"), cadeado: null, ponto: b => daGrade(b, "portao"),
  },
  barraca: {
    id: "barraca", nome: "Barraca do Tamer", destino: "diario", altura: LUGARES_MODELOS.barraca.altura, raio: 2.4, estado: "aberto",
    modelo: arquivo("barraca"), luz: luzDe("barraca"), cadeado: null, ponto: b => daGrade(b, "barraca"),
  },
};
/** o estado de agora: o nivel do Tamer tranca o lugar (trancas.ts); fora isso, o `estado` da tabela */
export const estadoDoLugar = (id: IdLugar): EstadoLugar => lugarTrancado(id) ? "trancado" : LUGARES[id].estado;
export const ORDEM_LUGARES: readonly IdLugar[] = ["saco", "portao", "barraca"];

/** o ponto do lugar no mundo de `base` */
export const pontoDoLugar = (id: IdLugar, base: BaseDoMundo): Ponto => LUGARES[id].ponto(base);
/** a altura do chao no pe do lugar (celulas): 0 no saco (na area andavel), a da grade no portao e na barraca */
export const chaoDoLugar = (id: IdLugar, base: BaseDoMundo): number => (id === "saco" ? 0 : base.grade?.[id]?.y ?? 0);
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

/** quanto dura a ida do pet ate o saco no treino (e a volta), em ms, para `dist` celulas (a PA-3, aprovada em 2026-11-08: com o saco perto da
    praca, a ida fixa de 0,9 s fazia o pet cruzar ~19 celulas): TREINO_VEL celulas por segundo, nunca menos que TREINO_MS.ida */
export const idaDoTreino = (dist: number): number => Math.max(TREINO_MS.ida, (Math.max(0, dist) / TREINO_VEL) * 1000);
