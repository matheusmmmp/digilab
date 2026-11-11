/* Os numeros e as contas do cantinho da TV (cantinhoTv.ts; o prototipo P0 do gosto visual, docs/futuro/gosto_visual_pet.md, secao 14),
   sem three e sem DOM, para o teste ler no node (como rotaConta.ts e ponteConta.ts): o cantinho em volta da TV de tubo da ilha (o marco do
   #814, MUNDO_ENFEITES: o enfeite "tv" que a grade poe, grade.ts, porMarcos), a chave, o chao do cantinho, a tela no modelo, a pose do pet
   sentado e a ida dele ate a almofada. So vista: nada daqui entra no motor, no log nem no save, e a TV e a do #814 (nenhuma TV nova). Todos
   os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import { TEXEL_ALVO, duracaoPetViagem } from "./constantes.ts";
import type { Ilha } from "./grade.ts";
import { comprimento, naRota, type Ponto } from "./rotaConta.ts";
import { gostoVisualLigado } from "../../../gostoVisual/chave.ts";
import type { Reacao } from "../../../gostoVisual/gosto.ts";

/** o cantinho no referencial da TV: `frente` ao longo da frente dela (+z do glTF, que a grade poe em tres quartos para a camera: constantes.ts, TV_TRES_QUARTOS) e `lado` a direita de quem
    olha a tela, em celulas. A almofada do pet fica a `assento.frente` da TV ou mais longe, ate `assento.ate`, no primeiro ponto em que o tapete
    inteiro cai em terra plana da area (na planta A a TV fica no plato, e o cantinho desce para o pe do barranco); a do dono (vazia: o lugar de
    quem assiste junto) e o tapete oval vem a partir da almofada do pet. PROPOSTO, SEM FONTE */
export const CANTINHO_TV = {
  assento: { frente: 2.4, ate: 7, passo: 0.25, lado: -0.45 },
  dono: { frente: 0.35, lado: 1.0 },
  tapete: { frente: 0.3, lado: 0.3, larg: 3.8, prof: 2.6, alto: 0.05, borda: 0.2 },
  almofada: { raio: 0.42, alto: 0.24, raioDono: 0.55 },
  /** a folga em volta do tapete em que a decoracao baixa some da vista */
  folga: 0.3,
} as const;

/** a caixa do toque na TV: o raio em volta do ponto dela (celulas; a altura e a do modelo, modelos.ts) e o lado minimo da area de toque na
    tela (px de CSS: o alvo de 44 px). PROPOSTO, SEM FONTE */
export const CAIXA_TV = { raio: 0.95, minPx: 44 } as const;
/** a camera com o painel da TV aberto: onde o meio do cantinho fica na tela, em fracao da largura de 900 px em diante (a esquerda do painel)
    e em fracao da altura abaixo disso (a partir do alto: acima da folha baixa), e quanto dura a ida e a volta (ms; com "reduzir movimento",
    nenhuma). PROPOSTO, SEM FONTE */
export const CAMERA_CANTINHO = { largo: 0.32, movel: 0.36, ms: 600 } as const;

/** o avanco da ida da camera ao cantinho: `f` (0 a 1) anda para 1 com o painel aberto e para 0 fechado, em `CAMERA_CANTINHO.ms` */
export function passoDaCamera(f: number, aberto: boolean, dtMs: number, reduzido: boolean): number {
  if (!Number.isFinite(f) || !Number.isFinite(dtMs)) throw new Error("passoDaCamera: entrada nao finita");
  if (reduzido) return aberto ? 1 : 0;
  const d = Math.max(0, dtMs) / CAMERA_CANTINHO.ms;
  return Math.min(1, Math.max(0, f + (aberto ? d : -d)));
}
/** a suavizacao da ida (entra e sai devagar) */
export const suave = (f: number): number => f * f * (3 - 2 * f);

/** a tela no modelo da TV (as unidades do glTF, antes da normalizacao do carregarVariante): o centro, os raios e a face da frente da peca
    "tela" de docs/objetos3d/cartoon/tv.py (TX, TY, TRX, TRY x 0,95 e Z1 + 0,034). A textura dinamica vai num plano um fio a frente dela,
    com os cantos arredondados. PROPOSTO, SEM FONTE */
export const TELA_DO_MODELO = { x: -0.105, y: 0.545, rx: 0.315, ry: 0.265 * 0.95, z: 0.394, folga: 0.004 } as const;

/** quanto o pet sobe sentado na almofada (texels do sprite: a altura da almofada, um pouco afundada), o pulinho do "adorando" (texels) e o
    periodo dele (ms), e a inclinacao do "curioso" (rad). PROPOSTO, SEM FONTE */
export const SENTADO_TEXELS = Math.round((CANTINHO_TV.almofada.alto * 0.8) / TEXEL_ALVO);
export const PULO_ADORANDO = 2, PULO_ADORANDO_MS = 170, INCLINA_CURIOSO = 0.2;
/** a tela da TV do jogo: o tamanho do desenho (px) e de quanto em quanto tempo ele e refeito (ms). PROPOSTO, SEM FONTE */
export const TELA_PX = [160, 120] as const, TELA_PASSO_MS = 50;

/** o cantinho entra na vista? So com a chave do P0 (`?gosto_visual=1`) */
export const cantinhoNaVista = (busca?: string): boolean => gostoVisualLigado(busca);

/** o cantinho no mundo (celulas): a TV (o ponto e o giro do enfeite da grade), a almofada do pet, a do dono e o tapete (o centro e o giro) */
export interface PontosCantinho { tv: Ponto; giro: number; assento: Ponto; dono: Ponto; tapete: Ponto }

/** a TV da ilha (o enfeite "tv" da grade); falha alto se a grade nao a pos */
export function tvDaIlha(ilha: Ilha): { x: number; z: number; giro: number } {
  const t = ilha.enfeites.find(e => e.nome === "tv");
  if (!t) throw new Error(`a ilha ${ilha.cm.layout.nome} nao tem a TV (o enfeite "tv" da grade) para o cantinho`);
  return t;
}

/** as celulas sob o tapete (amostras no oval, de meia em meia celula) */
function sobOTapete(centro: Ponto, giro: number): Ponto[] {
  const T = CANTINHO_TV.tapete, a = T.larg / 2 + T.borda, b = T.prof / 2 + T.borda, f: Ponto = [Math.sin(giro), Math.cos(giro)], r: Ponto = [-f[1], f[0]];
  const pts: Ponto[] = [];
  for (let u = -a; u <= a + 1e-9; u += 0.5) for (let v = -b; v <= b + 1e-9; v += 0.5)
    if ((u / a) ** 2 + (v / b) ** 2 <= 1) pts.push([centro[0] + r[0] * u + f[0] * v, centro[1] + r[1] * u + f[1] * v]);
  return pts;
}
const terraPlana = (ilha: Ilha, p: Ponto): boolean => {
  const c = ilha.cel(Math.floor(p[0]), Math.floor(p[1]));
  return !!c && ilha.naArea(p[0], p[1]) && c.tipo !== "agua" && c.nivel === 0;
};

/** os pontos do cantinho em volta da TV da ilha; falha alto se nenhum ponto ate `assento.ate` cabe o tapete em terra plana da area */
export function pontosDoCantinho(ilha: Ilha): PontosCantinho {
  const t = tvDaIlha(ilha), C = CANTINHO_TV, f: Ponto = [Math.sin(t.giro), Math.cos(t.giro)], r: Ponto = [-f[1], f[0]];
  const em = (frente: number, lado: number): Ponto => [t.x + f[0] * frente + r[0] * lado, t.z + f[1] * frente + r[1] * lado];
  for (let d = C.assento.frente; d <= C.assento.ate + 1e-9; d += C.assento.passo) {
    const tapete = em(d + C.tapete.frente, C.assento.lado + C.tapete.lado);
    if (!sobOTapete(tapete, t.giro).every(p => terraPlana(ilha, p))) continue;
    return { tv: [t.x, t.z], giro: t.giro, assento: em(d, C.assento.lado), dono: em(d + C.dono.frente, C.assento.lado + C.dono.lado), tapete };
  }
  throw new Error(`o cantinho da TV nao cabe em terra plana da area na frente da TV (${t.x}, ${t.z}) da ilha ${ilha.cm.layout.nome}`);
}

/** tira da vista a decoracao baixa sob o tapete (Ilha.escondidos, como as clareiras dos lugares); falha alto com um objeto do motor ali */
export function prepararChao(ilha: Ilha, p: PontosCantinho): void {
  const T = CANTINHO_TV.tapete, R = Math.max(T.larg, T.prof) / 2 + T.borda + CANTINHO_TV.folga;
  ilha.objetos.forEach((o, i) => {
    const perto = Math.hypot(o.x - p.tapete[0], o.z - p.tapete[1]) < R;
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
