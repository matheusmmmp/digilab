/* Os cenarios da luta em tempo real (docs/ESPEC_COMBATE_TR.md, item 7; E7, decisao do Matheus de 2026-10-29): os mapas da arena do
   Digimon UP viram o cenario de cada lugar, so o desenho. As regras de ambiente (mare, lava, ringue, area que fecha) ficam desligadas: o
   motor nao as tem. Os recortes dos mapas ficam fora do repositorio, em D:\Trab\digilab\Assets\arena_up\mapas (Assets\gerar_arena_up.py;
   DIGIMON UP, Bandai, com o credito: docs/UI_GUIDELINES.md, secao 5.1). Mapa que nao carrega: o palco desenha o chao liso e mostra o
   aviso (falhar alto, nunca calado).
   Portado do palcoTR/ (o palco 1D do combate por turnos) na LUTA_POC, LP4: ficaram so os geradores de pixel que o palco 2D usa
   (desenhoPoc.ts, visualPoc.ts); o que lia o estado da luta 1D saiu com ela. */
export const MAPAS_URL = "../../../Assets/arena_up/mapas/";

/** as imagens dos mapas: uma promessa por arquivo; a falha fica guardada para o aviso */
const imagens = new Map<string, Promise<HTMLImageElement | null>>();
export const prontas = new Map<string, HTMLImageElement | null>();
export const falhasMapa = new Set<string>();
const ouvintes = new Set<() => void>();
export function ouvirMapas(f: () => void): () => void { ouvintes.add(f); return () => { ouvintes.delete(f); }; }
export function imagemMapa(arq: string): Promise<HTMLImageElement | null> {
  let p = imagens.get(arq);
  if (!p) {
    p = new Promise(ok => {
      const i = new Image();
      i.onload = () => { prontas.set(arq, i); ok(i); for (const o of ouvintes) o(); };
      i.onerror = () => { falhasMapa.add(arq); prontas.set(arq, null); ok(null); for (const o of ouvintes) o(); };
      i.src = MAPAS_URL + encodeURIComponent(arq);
    });
    imagens.set(arq, p);
  }
  return p;
}
