/* A camera de desenvolvimento (pedido do Matheus, 2026-11-08: "movimentar a camera para algum lugar do mapa para ver e facilitar o
   desenvolvimento de ferramentas"). So com ?cameradev=1 no endereco (o ?camera= ja escolhe o angulo, habitat.ts); o jogador nao ve.
   - a camera solta (cameraLivre.ts: WASD, o arrasto direito, o minimapa, F volta ao pet) vale em qualquer largura e com qualquer controle,
     nao so a partir de 900 px com o "Livre";
   - as ferramentas (as capturas do Playwright, as sessoes dos objetos) dirigem a camera pela pagina, em `window.__camera`:
       __camera.alvos()                  os nomes que se pode visitar e onde ficam (celulas): os lugares, os enfeites, o ninho, o saco...
       __camera.ir("portao", { zoom: 0.6, giro: 0.4, inclina: -0.1 })   ou   __camera.ir([x, z])
       __camera.pet()                    volta a seguir o pet
       __camera.onde()                   o ponto olhado e a orbita de agora
     `ir` vai na hora (sem transicao), para a captura do quadro seguinte ja sair no lugar.
   So vista: fora do save, do registro e do replay, como a camera solta. */
import { LIVRE, VISTA, irPara, seguirPet, type Par } from "./cameraLivre.ts";
import { ORBITA } from "./orbita.ts";

/** a camera de desenvolvimento esta ligada nesta pagina (?cameradev=1) */
export const CAMERA_DEV = typeof location !== "undefined" && new URLSearchParams(location.search).get("cameradev") === "1";

/** a orbita pedida junto do lugar: o zoom (fator da distancia, < 1 aproxima), o giro em volta do ponto (rad) e a inclinacao somada (rad) */
export interface OrbitaDev { zoom?: number; giro?: number; inclina?: number }
export interface ApiCameraDev {
  alvos(): Record<string, Par>;
  ir(alvo: string | Par, orbita?: OrbitaDev): Par;
  pet(): void;
  onde(): { foco: Par | null; solta: boolean; zoom: number; giro: number; inclina: number };
}

/** a API da pagina, sobre os alvos que a vista conhece; falha alto com um nome que nao existe */
export function apiCameraDev(alvos: () => Record<string, Par>): ApiCameraDev {
  return {
    alvos,
    ir(alvo, orbita = {}) {
      const todos = alvos();
      const p: Par | undefined = typeof alvo === "string" ? todos[alvo] : alvo;
      if (!p) throw new Error(`__camera.ir: alvo desconhecido "${String(alvo)}"; os alvos: ${Object.keys(todos).join(", ")}`);
      irPara(p[0], p[1], performance.now(), false);
      if (orbita.zoom !== undefined) ORBITA.zoom = orbita.zoom;
      if (orbita.giro !== undefined) ORBITA.giro = orbita.giro;
      if (orbita.inclina !== undefined) ORBITA.inclina = orbita.inclina;
      ORBITA.versao++;
      return [p[0], p[1]];
    },
    pet() { ORBITA.zoom = 1; ORBITA.giro = 0; ORBITA.inclina = 0; ORBITA.versao++; seguirPet(performance.now()); },
    onde() { return { foco: VISTA.atual ? [...VISTA.atual.foco] as Par : null, solta: LIVRE.solta, zoom: ORBITA.zoom, giro: ORBITA.giro, inclina: ORBITA.inclina }; },
  };
}

/** poe a API em `window.__camera` enquanto a cena existe; devolve o que a tira */
export function ligarCameraDev(alvos: () => Record<string, Par>): () => void {
  if (!CAMERA_DEV) return () => {};
  const g = globalThis as { __camera?: ApiCameraDev };
  g.__camera = apiCameraDev(alvos);
  return () => { delete g.__camera; };
}
