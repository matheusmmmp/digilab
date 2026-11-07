/* O que a cena 3D da tela Pet (cena3d.ts, carregada por import dinamico) conta ao resto da tela: se esta ligada, onde o pet esta na
   tela (em px de CSS, para o PalcoPet desenhar por cima a sujeira, o icone rapido e a marca de saude) e a medida M3.
   Nos pets v12 (o mundo fisico; docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2), a vista do mundo (a cena 3D ou a reserva, MundoReserva.tsx)
   conta tambem como passar da tela ao mapa e do mapa a tela (em px do cliente, os de um evento de ponteiro) e onde ela desenha o pet
   (subunidades do mapa, interpolado). `modoMundo`: a reserva do mundo desenha o pet, e o PalcoPet so os extras, como com a cena 3D.
   `coberto`: um painel ou modal esta aberto por cima do habitat (o veu ligado; Habitat.tsx); a ilha desenha mais devagar por tras dele.
   `bolaNaMao`: o dono esta arrastando a bola (PorBola.tsx); a vista a esconde ate ela cair.
   `treino`: o ultimo treino pedido na tela Treinar (performance.now()); a ilha mostra o pet indo ao saco de pancada, batendo e voltando
   (so vista: o ganho e o do motor, na hora; docs/TAREFA_V3_HABITAT_OBJETOS.md).
   `cocoNoChao`: a ilha desenha a sujeira como cocos 3D no chao (ilha/cocos.ts); o PalcoPet deixa de desenhar o coco 2D ao lado do pet.
   `cabeca`: com um clipe de reacao de rosto (reacao.ts), o alto da cabeca [x, y] em px de CSS da cena, de onde sai o emote dela (papel.ts); null fora dele.
   `petNaMao`: o dono esta segurando o pet (PegarPet.tsx; docs/TAREFA_V3_PEGAR_PET.md, P2): a camera livre nao gira, e a camera e o foco da
   dobra param de seguir o pet (o paraMundo nao muda sob o dedo). `maoPet`: com ele na mao, o ponto do cliente (px) onde fica o pe do pet
   (o ponteiro mais a distancia do pe ao ponteiro quando ele foi pego); a vista desenha o pet ali, suspenso, e a sombra onde ele vai cair.
   `zzX`: com o quadro Dormir, o x (px de CSS da cena) do topo da cabeca, de onde sai o "zz" (papel.ts); null fora dele. */
export interface VistaDoMundo {
  /** o ponto do cliente (px) no chao, em subunidades inteiras do mapa; null fora do mapa ou fora do chao */
  paraMundo: (clientX: number, clientY: number) => [number, number] | null;
  /** o ponto do mapa (subunidades) no cliente (px) */
  paraTela: (x: number, y: number) => [number, number];
  /** onde a vista desenha o pet agora (subunidades, interpolado) */
  pet: [number, number];
  /** onde a vista desenha a bola agora (subunidades, interpolado); sem ele, onde o motor diz */
  bola?: [number, number];
  /** o pet na mao (a ilha 3D; a reserva nao tem): o ponto do chao (subunidades inteiras, SEM limitar ao mapa) em que cai o pe do pet
      desenhado no ponto do cliente (px) `pe`, ja descontada a altura em que a mao o segura; null fora do chao (o ceu, fora da cena) */
  pousoEm?: (peX: number, peY: number) => [number, number] | null;
}
export const CENA: {
  modo3d: boolean;
  modoMundo: boolean;
  ret: { x: number; y: number; w: number; h: number } | null;
  medir: null | (() => Promise<Record<string, unknown>>);
  mundo: VistaDoMundo | null;
  coberto: boolean;
  bolaNaMao: boolean;
  petNaMao: boolean;
  maoPet: { x: number; y: number } | null;
  treino: number | null;
  cocoNoChao: boolean;
  zzX: number | null;
  cabeca: [number, number] | null;
} = { modo3d: false, modoMundo: false, ret: null, medir: null, mundo: null, coberto: false, bolaNaMao: false, petNaMao: false, maoPet: null, treino: null, cocoNoChao: false, zzX: null, cabeca: null };
