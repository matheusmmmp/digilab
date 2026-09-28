/* Rotas: 4 destinos, cada um com suas sub-abas (mesma organizacao do HTML, TAREFA_INTERFACE_UP Etapa 3).
   O endereco e #/destino/aba; a aba lembrada fica em CHAVE-aba como "destino/aba" (formato do HTML: um valor
   antigo so com a aba vira o destino dela). */
import { CHAVE_ABA, type Armazenamento } from "./save.ts";

export type Destino = "pet" | "crescer" | "lutar" | "diario" | "conversar";
export type Aba = "estado" | "treinar" | "aprend" | "evolucao" | "arena" | "campanha" | "registro" | "catalogo" | "cenarios" | "chat";
export const DESTINOS: Record<Destino, readonly Aba[]> = {
  pet: ["estado"], crescer: ["treinar", "aprend", "evolucao"], lutar: ["arena", "campanha"], diario: ["registro", "catalogo", "cenarios"], conversar: ["chat"],
};
export const ORDEM_DESTINOS: readonly Destino[] = ["pet", "crescer", "lutar", "diario", "conversar"];
export const NOME_DESTINO: Record<Destino, string> = { pet: "Pet", crescer: "Crescer", lutar: "Lutar", diario: "Diário", conversar: "Conversar" };
export const NOME_ABA: Record<Aba, string> = {
  estado: "Estado", treinar: "Treinar", aprend: "Aprendizado", evolucao: "Evolução", arena: "Arena", campanha: "Campanha",
  registro: "Registro", catalogo: "Catálogo", cenarios: "Cenários", chat: "Conversa",
};
export const DESTINO_DA_ABA = Object.fromEntries(Object.entries(DESTINOS).flatMap(([d, abas]) => abas.map(a => [a, d]))) as Record<Aba, Destino>;

export interface Rota { destino: Destino; aba: Aba }
export const ROTA_INICIAL: Rota = { destino: "pet", aba: "estado" };

const ehAba = (x: string): x is Aba => x in DESTINO_DA_ABA;
const ehDestino = (x: string): x is Destino => x in DESTINOS;

/** "#/crescer/treinar" -> rota; "#/lutar" -> primeira aba do destino; outra coisa -> null */
export function rotaDoEndereco(hash: string): Rota | null {
  const [d, a] = hash.replace(/^#\/?/, "").split("/");
  if (!d || !ehDestino(d)) return null;
  if (a === undefined || a === "") return { destino: d, aba: DESTINOS[d][0] };
  return ehAba(a) && DESTINO_DA_ABA[a] === d ? { destino: d, aba: a } : null;
}
export const enderecoDaRota = (r: Rota): string => `#/${r.destino}/${r.aba}`;

/** aba lembrada: "destino/aba" ou, de uma versao antiga do HTML, so a aba */
export function lerAbaLembrada(armaz: Armazenamento): Rota | null {
  let v: string | null;
  try { v = armaz.getItem(CHAVE_ABA); } catch { return null; }
  if (!v) return null;
  const aba = v.includes("/") ? v.split("/")[1] : v;
  return ehAba(aba) ? { destino: DESTINO_DA_ABA[aba], aba } : null;
}
export function gravarAbaLembrada(armaz: Armazenamento, r: Rota): void {
  try { armaz.setItem(CHAVE_ABA, r.destino + "/" + r.aba); } catch { /* preferencia de tela: sem armazenamento, so nao lembra */ }
}

/* Configuracoes (desenhos Cfg*): tela fora dos 4 destinos, aberta pela engrenagem do Diario; #/config/<parte> */
export type ParteConfig = "principal" | "aparencia" | "dados" | "fala" | "sobre";
const PARTES_CONFIG: readonly ParteConfig[] = ["principal", "aparencia", "dados", "fala", "sobre"];
/** "#/config" -> principal; "#/config/dados" -> dados; outra coisa -> null */
export function configDoEndereco(hash: string): ParteConfig | null {
  const [c, p] = hash.replace(/^#\/?/, "").split("/");
  if (c !== "config") return null;
  return !p ? "principal" : (PARTES_CONFIG as readonly string[]).includes(p) ? p as ParteConfig : null;
}
/* luta em andamento: tela cheia com rota propria (secao 7); a aba de origem vem do palco */
export const ENDERECO_LUTA = "#/lutar/luta";
export const ehLuta = (hash: string): boolean => hash.replace(/^#\/?/, "") === "lutar/luta";
export const enderecoDaConfig = (p: ParteConfig): string => p === "principal" ? "#/config" : `#/config/${p}`;
