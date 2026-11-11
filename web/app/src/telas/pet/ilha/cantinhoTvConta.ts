/* Os numeros e as contas do cantinho da TV (cantinhoTv.ts; o prototipo P0 do gosto visual, docs/futuro/gosto_visual_pet.md, secao 14),
   sem three e sem DOM, para o teste ler no node (como rotaConta.ts e ponteConta.ts): o ponto e os tamanhos, o modelo esperado da TV do
   Matheus, a chave, o chao do cantinho, a pose do pet sentado e a ida dele ate a almofada. So vista: nada daqui entra no motor, no log
   nem no save. Todos os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import { TEXEL_ALVO, duracaoPetViagem } from "./constantes.ts";
import type { Ilha } from "./grade.ts";
import type { Modelo } from "./modelos.ts";
import { comprimento, naRota, type Ponto } from "./rotaConta.ts";
import { gostoVisualLigado } from "../../../gostoVisual/chave.ts";
import type { Reacao } from "../../../gostoVisual/gosto.ts";

/** o cantinho, em celulas do mundo (x leste, z sul). O centro e o do tapete: a sudeste do comedouro do layout (10,5; 15,5), longe do ninho,
    do saco, dos caminhos e dos postes da praca, ao norte do lago do sudoeste da ilha com agua (que comeca na linha 22). Os deslocamentos
    (da TV, da almofada do pet e da do dono) sao a partir do centro; a TV fica a leste (a direita na tela, longe do cartao do P0, que fica a
    esquerda) e o pet a oeste, olhando para ela. PROPOSTO, SEM FONTE */
export const CANTINHO_TV = {
  centro: [14, 19] as const,
  /** o tapete oval: a largura (x), a profundidade (z) e a espessura; a borda e a faixa mais larga embaixo */
  tapete: { larg: 5, prof: 3.3, alto: 0.05, borda: 0.2 },
  /** a TV: o deslocamento do pe do movel, e o giro (a frente, +z, para o meio entre a almofada do pet e a camera, que olha do sul) */
  tv: { desloc: [1.75, -0.45] as const, giro: Math.atan2(-0.75, 1) },
  /** a almofada do pet e a do dono (vazia: o lugar de quem assiste junto) */
  assento: [-1.45, 0.35] as const,
  dono: [-0.55, 1.2] as const,
  almofada: { raio: 0.42, alto: 0.24, raioDono: 0.55 },
  /** o raio em que a decoracao baixa some e em que o chao tem de ser terra plana da area */
  clareira: 3,
} as const;

/** o modelo da TV do Matheus (em public/), a altura dele (celulas, so a TV, sem o movel) e a do movel do cantinho. PROPOSTO, SEM FONTE */
export const MODELO_TV = "enfeites/tv/tv.gltf";
export const ALTURA_TV = 2.2, ALTURA_MOVEL = 0.5;
export const MODELO_TV_TABELA: Modelo = { arquivos: ["tv/tv.gltf"], altura: ALTURA_TV, vento: 0, sombra: 0, baixo: false };

/** quanto o pet sobe sentado na almofada (texels do sprite: a altura da almofada, um pouco afundada), o pulinho do "adorando" (texels) e o
    periodo dele (ms), e a inclinacao do "curioso" (rad). PROPOSTO, SEM FONTE */
export const SENTADO_TEXELS = Math.round((CANTINHO_TV.almofada.alto * 0.8) / TEXEL_ALVO);
export const PULO_ADORANDO = 2, PULO_ADORANDO_MS = 170, INCLINA_CURIOSO = 0.2;
/** a tela da TV do jogo: o tamanho do desenho (px) e de quanto em quanto tempo ele e refeito (ms). PROPOSTO, SEM FONTE */
export const TELA_PX = [160, 120] as const, TELA_PASSO_MS = 50;

/** o cantinho entra na vista? So com a chave do P0 (`?gosto_visual=1`) */
export const cantinhoNaVista = (busca?: string): boolean => gostoVisualLigado(busca);

/** os pontos do cantinho no mundo (celulas) */
export function pontosDoCantinho(): { centro: Ponto; tv: Ponto; assento: Ponto; dono: Ponto } {
  const [cx, cz] = CANTINHO_TV.centro, mais = (d: readonly [number, number]): Ponto => [cx + d[0], cz + d[1]];
  return { centro: [cx, cz], tv: mais(CANTINHO_TV.tv.desloc), assento: mais(CANTINHO_TV.assento), dono: mais(CANTINHO_TV.dono) };
}

/** confere o chao do cantinho (terra plana da area, sem objeto do motor) e tira da vista a decoracao baixa dentro da clareira; falha alto */
export function prepararChao(ilha: Ilha): void {
  const [cx, cz] = CANTINHO_TV.centro, R = CANTINHO_TV.clareira;
  for (let z = Math.floor(cz - R); z <= Math.ceil(cz + R); z++) for (let x = Math.floor(cx - R); x <= Math.ceil(cx + R); x++) {
    if (Math.hypot(x + 0.5 - cx, z + 0.5 - cz) > R) continue;
    const c = ilha.cel(x, z);
    if (!c || !ilha.naArea(x, z) || c.tipo === "agua" || c.nivel !== 0)
      throw new Error(`o cantinho da TV cai fora da terra plana da area na celula ${x},${z} (${c ? c.tipo + ", nivel " + c.nivel : "fora da grade"}) na ilha ${ilha.cm.layout.nome}`);
  }
  ilha.objetos.forEach((o, i) => {
    const perto = Math.hypot(o.x - cx, o.z - cz) < R;
    if (perto && o.doMotor !== null) throw new Error(`um objeto do motor (${o.doMotor}) dentro do cantinho da TV na ilha ${ilha.cm.layout.nome}`);
    if (perto) ilha.escondidos.add(i);
  });
}

/** a pose do pet sentado para a reacao do P0: a altura (texels), a inclinacao (rad) e para onde olha ("tv", "fora" ou o lado que ja tinha) */
export function poseNoCantinho(reacao: Reacao | null, agora: number, reduzido: boolean): { altura: number; angulo: number; olhar: "tv" | "fora" | null } {
  const pulo = reacao === "adorando" && !reduzido ? Math.round(Math.abs(Math.sin(agora / PULO_ADORANDO_MS)) * PULO_ADORANDO) : 0;
  const olhar = reacao === "nao_gosta" || reacao === "enjoou" ? "fora" : reacao === "distraido" ? null : "tv";
  return { altura: SENTADO_TEXELS + pulo, angulo: reacao === "curioso" ? INCLINA_CURIOSO : 0, olhar };
}

/** a ida do pet desenhado ate a almofada com a TV ligada, e a volta para onde o motor diz com ela desligada, na velocidade da viagem aos
    lugares (constantes.ts, duracaoPetViagem); `rota` da o caminho em terra (rotaConta.ts) ou null para a reta. So vista */
export class IdaAoCantinho {
  private anda: { ligada: boolean; de: Ponto; desde: number; dur: number; rota: Ponto[] | null } | null = null;
  private readonly assento: Ponto;
  private readonly rota: (de: Ponto, para: Ponto) => Ponto[] | null;
  constructor(assento: Ponto, rota: (de: Ponto, para: Ponto) => Ponto[] | null) { this.assento = assento; this.rota = rota; }
  /** o pet foi pego ou sumiu da vista: a proxima ida parte de onde ele estiver */
  reiniciar(): void { this.anda = null; }
  /** onde o pet fica agora; `ativo`: o cantinho manda nele (indo, sentado ou voltando); `sentado`: chegou com a TV ligada */
  passo(agora: number, petAgora: Ponto, motorCel: Ponto, ligada: boolean, reduzido: boolean): { cel: Ponto; andando: boolean; sentado: boolean; ativo: boolean } {
    if (ligada !== (this.anda?.ligada ?? false)) {
      const de: Ponto = [petAgora[0], petAgora[1]], para = ligada ? this.assento : motorCel, rota = this.rota(de, para);
      this.anda = { ligada, de, desde: agora, dur: duracaoPetViagem(rota ? comprimento(rota) : Math.hypot(para[0] - de[0], para[1] - de[1]), reduzido), rota };
    }
    const a = this.anda;
    if (!a) return { cel: motorCel, andando: false, sentado: false, ativo: false };
    const para = a.ligada ? this.assento : motorCel, f = a.dur > 0 ? Math.min(1, (agora - a.desde) / a.dur) : 1;
    if (f >= 1 && !a.ligada) { this.anda = null; return { cel: motorCel, andando: false, sentado: false, ativo: false }; }
    if (f >= 1) return { cel: [para[0], para[1]], andando: false, sentado: true, ativo: true };
    if (a.rota) {
      /* a volta segue o pet do motor, que pode ter andado: o desvio do fim da rota entra aos poucos (como em vista.ts, petNaViagem) */
      const [x, z] = naRota(a.rota, f), u = a.rota[a.rota.length - 1];
      return { cel: [x + (para[0] - u[0]) * f, z + (para[1] - u[1]) * f], andando: true, sentado: false, ativo: true };
    }
    return { cel: [a.de[0] + (para[0] - a.de[0]) * f, a.de[1] + (para[1] - a.de[1]) * f], andando: true, sentado: false, ativo: true };
  }
}
