/* O que a cena 3D da tela Pet (cena3d.ts, carregada por import dinamico) conta ao resto da tela: se esta ligada, onde o pet esta na
   tela (em px de CSS, para o PalcoPet desenhar por cima a sujeira, o icone rapido e a marca de saude) e a medida M3.
   Nos pets v12 (o mundo fisico; docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2), a vista do mundo (a cena 3D ou a reserva, MundoReserva.tsx)
   conta tambem como passar da tela ao mapa e do mapa a tela (em px do cliente, os de um evento de ponteiro) e onde ela desenha o pet
   (subunidades do mapa, interpolado). `modoMundo`: a reserva do mundo desenha o pet, e o PalcoPet so os extras, como com a cena 3D.
   `coberto`: um painel ou modal esta aberto por cima do habitat (o veu ligado; Habitat.tsx); a ilha desenha mais devagar por tras dele.
   `bolaNaMao`: o dono esta arrastando a bola (PorBola.tsx); a vista a esconde ate ela cair.
   `treino`: o ultimo treino pedido na tela Treinar (performance.now()); a ilha mostra o pet indo ao saco de pancada, batendo e voltando
   (so vista: o ganho e o do motor, na hora; docs/TAREFA_V3_HABITAT_OBJETOS.md). */
export interface VistaDoMundo {
  /** o ponto do cliente (px) no chao, em subunidades inteiras do mapa; null fora do mapa ou fora do chao */
  paraMundo: (clientX: number, clientY: number) => [number, number] | null;
  /** o ponto do mapa (subunidades) no cliente (px) */
  paraTela: (x: number, y: number) => [number, number];
  /** onde a vista desenha o pet agora (subunidades, interpolado) */
  pet: [number, number];
  /** onde a vista desenha a bola agora (subunidades, interpolado); sem ele, onde o motor diz */
  bola?: [number, number];
}
export const CENA: {
  modo3d: boolean;
  modoMundo: boolean;
  ret: { x: number; y: number; w: number; h: number } | null;
  medir: null | (() => Promise<Record<string, unknown>>);
  mundo: VistaDoMundo | null;
  coberto: boolean;
  bolaNaMao: boolean;
  treino: number | null;
} = { modo3d: false, modoMundo: false, ret: null, medir: null, mundo: null, coberto: false, bolaNaMao: false, treino: null };
