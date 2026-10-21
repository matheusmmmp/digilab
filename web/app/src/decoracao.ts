/* Decoracao da interface com os assets do Digimon UP (Bandai; so uso pessoal e local): brasoes, aneis, icones,
   molduras e os fundos das lutas da campanha (docs/ASSETS_UP.md). Fica FORA do repositorio, em
   D:\Trab\digilab\Assets, gerada por Assets\gerar_decoracao_up.py; os nomes permitidos estao em
   decoracao_nomes.json (o vite e o servidor_local.py so servem esses). Cada peca e opcional: o que nao carregar
   entra na lista do aviso visivel e aquele lugar fica com o visual de antes. */
import { useEffect, useState } from "react";
import NOMES from "../decoracao_nomes.json";

export const DECORACAO_URL = "../../../Assets/digilab_decoracao_up.json";
export type NomeDeco = string;
interface PecaDeco { arquivo: string; tamanho: [number, number]; sha256: string }
interface DecoracaoUp { versao: number; pecas: Record<NomeDeco, PecaDeco> }
type Estado = { tipo: "carregando" } | { tipo: "ok"; dados: DecoracaoUp; base: string } | { tipo: "erro"; erro: string };

let estado: Estado = { tipo: "carregando" };
const falhas = new Map<NomeDeco, string>();
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };

export function carregarDecoracao(url = DECORACAO_URL): void {
  fetch(url)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status} em ${url}`); return r.json() as Promise<DecoracaoUp>; })
    .then(dados => {
      if (dados.versao !== 1 || typeof dados.pecas !== "object") throw new Error("formato desconhecido em " + url);
      for (const n of NOMES.pecas) if (!dados.pecas[n]) falhas.set(n, "ausente no JSON");
      estado = { tipo: "ok", dados, base: new URL(url, document.baseURI).href };
      avisar();
    })
    .catch((err: unknown) => {
      console.error("falha ao carregar a decoração", url, err);
      estado = { tipo: "erro", erro: err instanceof Error ? err.message : String(err) };
      avisar();
    });
}
/** o estado e a lista do que falhou (para o aviso); re-renderiza quando algo muda */
export function useDecoracao(): { estado: Estado; falhas: ReadonlyMap<NomeDeco, string> } {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return { estado, falhas };
}
/** endereco da peca, ou null (ainda carregando, sem decoracao ou a peca falhou: fica o visual de antes) */
export function urlDeco(nome: NomeDeco): string | null {
  if (estado.tipo !== "ok" || falhas.has(nome)) return null;
  const p = estado.dados.pecas[nome];
  return p ? new URL(p.arquivo, estado.base).href : null;
}
/** uma peca que nao abriu vai para o aviso (uma vez) e sai de cena */
export function falhouDeco(nome: NomeDeco, url: string): void {
  if (falhas.has(nome)) return;
  console.error("peça de decoração não carregou", nome, url);
  falhas.set(nome, "não carregou");
  avisar();
}

/* imagens para o canvas (fundos das lutas): pedidas uma vez; enquanto carregam, null (o palco desenha o de antes) */
const imagens = new Map<NomeDeco, HTMLImageElement>();
export function imagemDeco(nome: NomeDeco): HTMLImageElement | null {
  const url = urlDeco(nome);
  if (!url) return null;
  let img = imagens.get(nome);
  if (!img) {
    img = new Image();
    img.onload = avisar;
    img.onerror = () => falhouDeco(nome, url);
    img.src = url;
    imagens.set(nome, img);
  }
  return img.complete && img.naturalWidth > 0 ? img : null;
}
/** avisa quando uma imagem do canvas termina de carregar (o palco redesenha) */
export function ouvirDecoracao(f: () => void): () => void { ouvintes.add(f); return () => { ouvintes.delete(f); }; }

/* ------------------------------------------------ o que cada lugar usa (so nomes; nada do motor muda) */
/** brasao da especie (guia: brasa Coragem, cirro Amizade, ferrugem Conhecimento, limo Sinceridade) */
export const BRASAO: Record<string, { peca: NomeDeco; esquerda: NomeDeco; direita: NomeDeco; nome: string }> = {
  brasa: { peca: "Crest_Combine_1", esquerda: "Crest_Left_1", direita: "Crest_Right_1", nome: "Coragem" },
  cirro: { peca: "Crest_Combine_2", esquerda: "Crest_Left_2", direita: "Crest_Right_2", nome: "Amizade" },
  ferrugem: { peca: "Crest_Combine_4", esquerda: "Crest_Left_4", direita: "Crest_Right_4", nome: "Conhecimento" },
  limo: { peca: "Crest_Combine_5", esquerda: "Crest_Left_5", direita: "Crest_Right_5", nome: "Sinceridade" },
};
/** fundo ilustrado da luta de cada NPC da campanha (recortes sem o chefe; a arena fica com o octogono). O Gazimon, da Campina, ficou sem:
    o recorte dele tinha um pergaminho com glifos orientais (docs/TAREFA_V2_EXPLORACAO.md) */
export const FUNDO_NPC: Record<string, NomeDeco> = {
  npc_tier2_sentinela: "torre_tortomon",
  npc_tier2_carcereiro: "torre_guardromon",
  npc_tier2_porteiro: "torre_devidramon",
  npc_tier3_soberano: "cidadela_piedmon",
};
/** faixa propria do lugar no cartao da campanha (pelo nome do lugar: o indice muda com a versao do pet); sem ela, o fundo do
    rival em foco */
export const FAIXA_LUGAR: Partial<Record<string, NomeDeco>> = { Cidadela: "cidadela_faixa" };
/** icones de lista (Growth_Guide) */
export const ICONE = {
  naoVisto: "Growth_Guide_Icon_05", alimentar: "Growth_Guide_Icon_06", treinar: "Growth_Guide_Icon_07",
  registro: "Growth_Guide_Icon_09", pets: "Growth_Guide_Icon_10", tempo: "Growth_Guide_Icon_11",
} as const;
/** moldura do retrato por faixa de vitorias contra aquele rival: 0 → 1, 1 → 2, ... ate 10 */
export const molduraArena = (vitorias: number): NomeDeco => `Profile_Outline_Arena_${Math.max(1, Math.min(10, vitorias + 1))}`;
