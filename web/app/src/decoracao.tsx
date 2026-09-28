/* Decoracao do Digimon UP (Bandai; so uso pessoal e local): brasoes, icones do guia de crescimento, globo e engrenagem
   que as pranchas usam (docs/ASSETS_UP.md). Fica FORA do repositorio, como o atlas: Assets/digilab_decoracao_up.json e
   Assets/decoracao_up/*.png, gerados por Assets/gerar_decoracao_up.py. Imagens pintadas (nao pixel art). Sem o arquivo,
   quem usa cai no desenho de reserva e o app avisa no console (e decoracao, nao muda o jogo). */
import type { ComponentChildren } from "preact";
import { useEffect, useState } from "preact/hooks";

export const DECORACAO_URL = "../../../Assets/digilab_decoracao_up.json";
interface Decoracao { pecas: Record<string, { arquivo: string; tamanho: [number, number] }> }
let urls: Record<string, { url: string; w: number; h: number }> | null = null;
const ouvintes = new Set<() => void>();

export function carregarDecoracao(url = DECORACAO_URL): void {
  fetch(url)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status} em ${url}`); return r.json() as Promise<Decoracao>; })
    .then(d => {
      const base = new URL(url, document.baseURI);
      urls = Object.fromEntries(Object.entries(d.pecas).map(([k, p]) => [k, { url: new URL(p.arquivo, base).href, w: p.tamanho[0], h: p.tamanho[1] }]));
      for (const o of ouvintes) o();
    })
    .catch((err: unknown) => console.warn("decoração do UP não carregou (usa o desenho de reserva)", url, err));
}
export function useDecoracao(): typeof urls {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return urls;
}
/** peca da decoracao no tamanho pedido (imagem pintada, com suavizacao); sem a decoracao, a reserva */
export function Deco({ nome, w, h, alt = "", cls = "", reserva = null }: { nome: string; w: number; h: number; alt?: string; cls?: string; reserva?: ComponentChildren }) {
  const d = useDecoracao(), p = d?.[nome];
  if (!p) return <>{reserva}</>;
  return <img class={"dl-deco " + cls} src={p.url} width={w} height={h} alt={alt} />;
}
/* brasao de cada especie (placa inteira): Coragem, Amizade, Conhecimento, Sinceridade */
export const BRASAO_DECO: Record<string, string> = { brasa: "Crest_Combine_1", cirro: "Crest_Combine_2", ferrugem: "Crest_Combine_4", limo: "Crest_Combine_5" };
