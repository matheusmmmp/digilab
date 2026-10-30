/* Os cenarios da luta em tempo real (docs/ESPEC_COMBATE_TR.md, item 7; E7, decisao do Matheus de 2026-10-29): os mapas da arena do
   Digimon UP viram o cenario de cada lugar, so o desenho. As regras de ambiente (mare, lava, ringue, area que fecha) ficam desligadas: o
   motor nao as tem. Os recortes dos mapas ficam fora do repositorio, em D:\Trab\digilab\Assets\arena_up\mapas (Assets\gerar_arena_up.py;
   DIGIMON UP, Bandai, com o credito: docs/UI_GUIDELINES.md, secao 5.1). Mapa que nao carrega: o palco desenha o chao liso e mostra o
   aviso (falhar alto, nunca calado). */
import { LUGARES_V6, NPC, type Instalacao } from "../../../../motor/index.ts";

export type IdCenaTR = "coliseu" | "floresta" | "praia" | "deserto" | "castelo" | "caverna" | "ringue";
export const MAPAS_URL = "../../../Assets/arena_up/mapas/";

/** a arte de cada cenario: o piso (o chao), o fundo (a parede, a cobrir ou repetida na altura dada) e o ceu (o degrade sem fundo) */
export const VISUAL_CENA: Record<IdCenaTR, { piso?: string; fundo?: string; fundoCobre?: boolean; fundoAlt?: number; ceu?: [string, string] }> = {
  coliseu: { piso: "coliseu_piso.jpg", fundo: "coliseu_fundo.jpg", fundoCobre: true },
  floresta: { piso: "floresta_piso.jpg", fundo: "floresta_fundo.png", fundoAlt: 92 },
  praia: { piso: "praia_piso.jpg", ceu: ["#9fd3ef", "#d9f0f7"] },
  deserto: { piso: "deserto_piso.jpg", ceu: ["#f3c27a", "#fbe3b6"] },
  castelo: { piso: "castelo_piso.jpg", fundo: "castelo_fundo.png", fundoAlt: 96, ceu: ["#2a2346", "#4b3b6e"] },
  caverna: { piso: "caverna_piso.jpg", ceu: ["#0d1016", "#1d2430"] },
  ringue: { piso: "ringue_piso.jpg", fundo: "ringue_fundo.jpg", fundoCobre: true },
};
/** o cenario de cada lugar da campanha (pelo nome; o indice muda com o mapa). PROPOSTO, SEM FONTE (espec, item 7) */
const CENA_DO_LUGAR: Record<string, IdCenaTR> = {
  "Campina": "floresta", "Torre de pedra": "castelo", "Floresta": "floresta", "Cidadela": "castelo", "Lago": "praia", "Montanha Espiral": "caverna",
};
/** o cenario da luta: a Arena e o Lab no ringue; a campanha pelo lugar do NPC; a Liga e o Salao no coliseu; a Torre de Batalha e o
    Palacio no castelo. Todo lugar tem um mapa do UP (nao ha mapa de campo: a Campina usa o da floresta). PROPOSTO, SEM FONTE */
export function cenaDaLuta(o: { npc: string | null; liga?: boolean; instalacao?: Instalacao | null; salao?: boolean }): IdCenaTR {
  if (o.liga || o.salao) return "coliseu";
  if (o.instalacao) return "castelo";
  if (o.npc) {
    const n = NPC[o.npc];
    if (!n) throw new Error("NPC desconhecido no cenario da luta: " + o.npc);
    const lugar = LUGARES_V6.find(L => L.rivais.includes(o.npc!));
    if (!lugar) throw new Error(`${n.nome} sem lugar na campanha (cenario da luta)`);
    const c = CENA_DO_LUGAR[lugar.nome];
    if (!c) throw new Error("lugar sem cenario: " + lugar.nome);
    return c;
  }
  return "ringue";
}

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
/** os arquivos de um cenario (pede o carregamento) */
export function arquivosCena(id: IdCenaTR): string[] {
  const v = VISUAL_CENA[id], arqs = [v.piso, v.fundo].filter((x): x is string => !!x);
  for (const a of arqs) void imagemMapa(a);
  return arqs;
}
